## Step 3: Code Review & Re-Verify

<!-- CC-ONLY -->
**If `PILOT_CHANGES_REVIEW_ENABLED` is `"false"` (from Step 0),** skip the review collection below. If the Codex companion was launched in Step 1, still collect it — then proceed to Step 4 (Phase B). If neither reviewer is enabled, skip this step entirely.

**When enabled — mandatory. Never skip**, however confident you are, however high the context, however green the tests.

#### Collect the findings from the sub-agent launched in Step 1

**Stale-snapshot guard first:** the Step 1 launch reviewed the tree as it stood BEFORE the Step 2 automated checks. If Step 2's fixes modified any file after that launch, the findings describe stale code — relaunch now (same Step 1 prompt, current diff) and collect the relaunch instead. ⛔ The original agent may still be running and will eventually write to its own path, so every launch MUST get a FRESH `output_path` (`-r2`, `-r3`, …); a late write from a superseded agent must never be collected as the fresh run. If Step 2 changed nothing, collect the Step 1 run as-is.

**Poll for the findings file** — not a Read loop, and ⛔ never `TaskOutput`:

```bash
# Poll the path of the launch you are collecting (Step 1's path, or the -rN relaunch path)
SESS_DIR="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
RUN_DIR="$SESS_DIR"            # on a lane run: "$SESS_DIR/lanes/<lane>"
OUTPUT_PATH="$RUN_DIR/findings-changes-review-<plan-slug>.json"
# $LAUNCHED_AT is the epoch stamped in Step 1a. A file older than the launch is a
# stale artifact, not this review's result - reading it would let a previous run's
# (or a sibling lane's) clean report stand in as evidence for THIS diff.
for i in $(seq 1 150); do
  [ -f "$OUTPUT_PATH" ] && [ "$(date -r "$OUTPUT_PATH" +%s)" -ge "$LAUNCHED_AT" ] && echo "READY" && break
  sleep 2
done
```

Run as `Bash(run_in_background=true, timeout=330000)` — the loop can wait 5 min, beyond the foreground timeout, and `sleep` is allowed in background; you are notified on exit. Then Read the file once. **A findings file whose mtime predates `$LAUNCHED_AT` is absent, not a result.** Not READY afterwards usually means slow, not dead: relaunch ONCE with a fresh `-rN` path and poll that.

**Validate findings:** the JSON's `plan_file` must match the current plan path. A mismatch means findings from another plan — delete, relaunch, wait again.

**Apply agent findings — lineage first** (same rule as the table below; out-of-lineage findings are mention-only regardless of severity): `must_fix` → fix now; `should_fix` → fix now; `suggestion` → implement if quick, else mention in the report. The agent's `truths` array feeds the report's Goal Achievement line. Then continue at "Collect Codex results".

⛔ **Resolve every cannot-verify item yourself — silence from the reviewer is not a pass.** A reviewer scoped to a diff cannot check a requirement living in unchanged code or spanning tasks, so it hands the question back: `category: cannot_verify` from the changes-review agent, a `cannot verify from diff:` info-severity finding from Codex, and any truth returned with `status: uncertain`. Each one is yours to settle before this step's report — you hold the plan and the cross-task context the reviewer lacks. Confirm the requirement is met (say so in the report) or find it genuinely missing, in which case it becomes a **must_fix** and runs the fix loop like any other. Neither fixing them blind nor listing them as mentions counts as resolving them.

⛔ **Do not substitute `Skill(skill='code-review', ...)` for a sub-agent that came back empty or failed.** The skill carries `disable-model-invocation`; the call is rejected and the iteration ends up with no review while the report claims one. If the sub-agent produced nothing after its one relaunch, record the gap in this step's report and the Step 6.3 Not-Verified table, and rely on the Step 2.2 audit for this iteration.

#### Apply findings (severity → action)

**Fix automatically — no user permission needed.** **Lineage is evaluated FIRST:** a finding outside the spec's lineage — the plan's `Files:` blocks plus files legitimately touched as documented deviations — is mention-only regardless of severity. Out-of-lineage crashes get reported, never auto-fixed. Only in-lineage findings run through the rows below.

| Finding class | Action |
|---------------|--------|
| Outside the spec's lineage (CHECK FIRST — overrides every row below) | **Mention-only — do NOT fix** (mirrors the pre-existing-issue rule) |
| `category: cannot_verify`, a `cannot verify from diff:` Codex finding, or a truth with `status: uncertain` | **Resolve it yourself** — confirm the requirement is met, or find it missing and treat as **must_fix** |
| `failure_scenario` names a concrete crash, wrong output, security, or data-integrity problem | **must_fix** — fix immediately |
| Cleanup / efficiency / altitude finding (duplication, wasted work, maintainability), single-site | **should_fix** — fix immediately |
| Cleanup that would expand scope (3+ files, architectural) | **suggestion** — implement if quick, else mention in the report |

Rank order is the tiebreaker within a class. For each fix: implement → run relevant tests → log "Fixed: [title]".

#### Collect Codex results (if launched in Step 1)

**Never skip or defer it.** Follow `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/codex-companion-protocol.md` §4–§6 with the `JOB_ID` and `PROMPT_FILE` from Step 1: run the stall monitor, branch on `READY` / `FAIL` / `STALLED`, then fetch, parse, apply by severity (lineage first), mark the codex-once flag, and clean up.

If the companion produced no result after its one retry, proceed WITHOUT the Codex pass and record the gap explicitly — in this step's report and the Step 6.3 Not-Verified table, noting how long it ran and when its log last advanced. Continue with this iteration's changes-review results.

**Report:**
```
## Code Verification Complete
**Issues Found:** X
### Goal Achievement: N/M truths verified   (from the Step 2.2 Plan Compliance & Goal-Truth Audit)
### Must Fix (N) | Should Fix (N) | Suggestions (N) | Out-of-lineage mentions (N)
```

#### Re-verification (only for structural fixes)

**Skip** when the fixes were localized (terminology, error handling, test updates, minor bugs) — run tests + lint to confirm, then proceed to Phase B.

**Re-verify** when fixes added functionality, changed APIs, or introduced significant new code paths: re-run the Step 2.2 Plan Compliance & Goal-Truth Audit on the post-fix diff (fixes can break mitigations or truths), then relaunch the changes-review sub-agent with a FRESH `-rN` output path and `Changed files:` = the fixed files, so the review is SCOPED to what the fixes touched rather than the whole spec diff. Max 2 iterations before adding remaining issues to the plan.
<!-- /CC-ONLY -->
<!-- CODEX-START
**If `PILOT_CHANGES_REVIEW_ENABLED` is `"false"` (from Step 0 — Step 1 was skipped),** skip this step entirely and proceed to Step 4 (Phase B).

**When enabled — mandatory. Never skip.** Read the `changes-review` agent id captured in Step 1 from working notes or the session file:

```bash
AGENT_ID_FILE="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}/changes-review-agent-id-<plan-slug>.txt"
```

If `CHANGES_REVIEW_AGENT_ID` is missing and the file exists, read the file and use its trimmed contents. If both are missing or empty, re-launch `changes-review` once using the Step 1 prompt, persist the new id to the file, then continue. Do not silently skip review while `PILOT_CHANGES_REVIEW_ENABLED` is enabled.

Wait for the final result:

```python
result = multi_agent_v1.wait_agent(targets=[CHANGES_REVIEW_AGENT_ID], timeout_ms=600000)
```

Parse the agent's final message as JSON. If parsing fails, treat the raw final message as one `suggestion` finding and continue; do not re-launch on parse failure.

Validate `plan_file` matches the current plan. If it does not, discard the stale result and self-review the diff before proceeding.

Lineage first — a finding outside the plan's `Files:` blocks and documented deviations is mention-only regardless of severity. Otherwise: `must_fix` → fix immediately; `should_fix` → fix immediately; `suggestion` → implement if quick.

⛔ **Resolve every cannot-verify item yourself — silence from the reviewer is not a pass.** A reviewer scoped to a diff cannot check a requirement living in unchanged code or spanning tasks, so it hands the question back: `category: cannot_verify`, or a truth returned with `status: uncertain`. Settle each one before the report — you hold the plan and the cross-task context the reviewer lacks. Confirm the requirement is met (say so in the report) or find it genuinely missing, in which case it becomes a **must_fix** and runs the fix loop like any other.

Final-status-only findings are not implementation fixes. If a finding only says the plan still reads `Status: COMPLETE` instead of `Status: VERIFIED`, record it as pending Step 11 finalization and do not loop back to implementation. Step 11 is responsible for writing `VERIFIED` after the user review gate and re-checking final-status truths.

For each fix: implement → run relevant tests → log `Fixed: [title]`.

After all findings are handled, re-run the relevant automated checks from Step 2 before proceeding to Step 4.
CODEX-END -->
