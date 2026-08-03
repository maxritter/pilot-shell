## Step 10: Plan Verification

### 10.0: No-Placeholders Self-Check (always — before launching reviewers)

Read the plan once, fresh-eyed. **Every match below is a plan failure** — fix it inline before any reviewer sees the plan or the user is asked to approve it.

- `TBD`, `TODO`, `FIXME`, "implement later", "fill in details", "details below"
- "add appropriate error handling", "add validation", "handle edge cases" — without naming which cases
- "write tests for the above" — a task must name the actual test cases, not a meta-instruction
- "similar to Task N" — implementers read tasks out of order; repeat the content
- Steps that say *what* without showing *how* (code steps need code blocks)
- References to types, functions, files, or env vars no task defines
- `<your-code-here>` / `<insert-X>` outside the header's literal placeholders
- Goal Verification truths that aren't falsifiable ("works correctly", "is fast enough")

```bash
grep -nEi "TBD|TODO|FIXME|implement later|fill in details|appropriate error handling|similar to Task" "<plan_path>"
```

**Then check cross-task identifier consistency.** Types, function names, property names, and env vars introduced in one task must be spelled identically everywhere later tasks use them — `clearLayers()` in Task 3 and `clearFullLayers()` in Task 7 is a bug the implementer inherits, not a synonym. Tasks are written in sequence and read out of order, so drift here stays invisible until implementation. Sorting the plan's identifiers puts near-misses on adjacent lines:

```bash
grep -oE '`[A-Za-z_][A-Za-z0-9_]*(\(\))?`' "<plan_path>" | sort | uniq -c
```

Scan for two spellings of one thing, then `grep -n` the pair to see which tasks disagree and fix the loser.

---

<!-- CC-ONLY -->
### 10.1: Claude spec-review

**Skip when** `PILOT_SPEC_REVIEW_ENABLED` is `"false"`, or when the plan has **≤ 2 tasks** AND touches none of security, authentication, data integrity, or destructive operations — reviewer overhead exceeds its value on a change the implementer can audit by inspection. For 3+ task plans, or any plan touching those surfaces at any size, run it in full.

⛔ **Skipping the reviewer never skips Step 11 (annotations) or Step 12 (approval).** Those always run.

**Derive the plan slug** from the filename: strip the `YYYY-MM-DD-` prefix and `.md`. Example: `2026-03-02-sku-builder-modal-cleanup.md` → `sku-builder-modal-cleanup`.

Delete stale findings from a previous run of this plan, then launch:

```bash
SESS_ID="${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
OUTPUT_PATH="$HOME/.pilot/sessions/$SESS_ID/findings-spec-review-<plan-slug>.json"
rm -f "$OUTPUT_PATH"
```

```
Agent(
  subagent_type="spec-review",
  run_in_background=true,
  prompt="""
  **Plan file:** <plan-path>
  **User request:** <original task description>
  **Clarifications:** <any Q&A>
  **Output path:** <absolute path to findings JSON>

  Review for alignment with requirements AND adversarial risks.
  Write findings JSON to output_path using Write tool.
  IMPORTANT: Include the plan file path in your output JSON as the "plan_file" field.
  """
)
```

⛔ **Never `TaskOutput`** — it dumps the full agent transcript into context. Collect via the file poll in 10.3.

### 10.2: Codex adversarial review (optional — launch immediately, runs in parallel)

**Only when `PILOT_CODEX_SPEC_REVIEW_ENABLED` is `"true"`** (from Step 0).

**Codex-once:** at most one companion run per `/spec` invocation. Plan iterations — annotation feedback, plan edits, fixing prior findings — never trigger a second run.

```bash
SESS_ID="${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
CODEX_FLAG="$HOME/.pilot/sessions/$SESS_ID/codex-spec-review-ran-<plan-slug>.flag"
[ -f "$CODEX_FLAG" ] && echo "Codex already reviewed this plan in this session — skipping (codex-once)."
```

Otherwise **read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/codex-companion-protocol.md` and follow it end to end** (locate → render → launch → stall monitor → collect → mark). Supply:

| Protocol input | Value for plan review |
|---|---|
| `PROMPT_TEMPLATE` | `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/spec-review-codex.md` |
| `{{PLAN_PATH}}` | absolute path to the plan file |
| `{{PLAN_GOAL}}` | the Goal sentence from the plan's `## Summary` |
| `{{CONTEXT_FILES}}` | newline-separated absolute paths the plan ports from or extends (the files named in `## Context for Implementer`) |
| `SLUG` | `<plan-slug>` |
| `CODEX_FLAG` | the path above |

⛔ **Use the protocol's `task --prompt-file` launch — never `adversarial-review --base` or `--scope branch` for a plan.** Those bundle a git diff as the review target, and plan files are gitignored here, so Codex receives an empty diff and returns a meta-finding ("no implementation diff was provided") with nothing substantive about the plan. `task` lets Codex read the plan file directly. (`adversarial-review` stays correct in `spec-verify`, where real working-tree code exists.)

**Do NOT wait** — go collect the Claude reviewer first.

### 10.3: Collect and fix

**Claude reviewer** — poll the file, never a Read loop:

```bash
OUTPUT_PATH="<findings-path>"
for i in $(seq 1 150); do [ -f "$OUTPUT_PATH" ] && echo "READY" && break; sleep 2; done
```

Read it once. Not READY after 5 min → relaunch synchronously. **Validate `plan_file` matches the current plan path**; a mismatch means stale findings from a previous `/spec` — delete, relaunch, wait again.

Fix must_fix → should_fix immediately. Suggestions if reasonable.

**Codex** — collect per the protocol's §5 once its monitor exits, and fix every must_fix and should_fix inline before requesting approval. Codex findings frequently surface architectural gaps the Claude reviewer misses; weigh them at least equally. If the companion never produced a result after its one retry, proceed on the Claude reviewer alone and say so before asking for approval.

Proceed to Step 11 once all must_fix and should_fix from both reviewers are resolved.
<!-- /CC-ONLY -->
<!-- CODEX-START
**If `PILOT_SPEC_REVIEW_ENABLED` is `"false"` (from Step 0),** skip native Codex plan review and proceed to the task-card format check below.

**When enabled:** launch the managed Codex custom agent and wait for its final JSON response before requesting approval.

1. Spawn the review agent:

```python
review = multi_agent_v1.spawn_agent(
    agent_type="spec-review",
    message="""
    Plan file: <plan-path>
    User request: <original task description>
    Clarifications: <any Q&A>

    Review for alignment with requirements and adversarial risks.
    Return ONLY valid JSON matching the spec-review schema.
    Include the plan file path in the `plan_file` field.
    """,
)
```

2. Wait for the result:

```python
result = multi_agent_v1.wait_agent(targets=[review.agent_id], timeout_ms=600000)
```

3. Parse the agent's final message as JSON. If parsing fails, treat the raw final message as one `suggestion` finding and continue; do not launch a second reviewer.

4. Validate `plan_file` matches the current plan. If it does not, discard the stale result and self-review instead of applying mismatched findings.

5. Severity mapping: `must_fix` → fix immediately; `should_fix` → fix immediately; `suggestion` → implement if quick.

Fix every `must_fix` and `should_fix` inline, then re-run the no-placeholders and task-card checks before approval.

Before Step 11, run this task-card format check on the plan:

```bash
grep -nE '^### Task [0-9]+:|^\*\*(Objective|Files|Key Decisions / Notes|Definition of Done):\*\*' "<plan_path>"
```

Every `### Task N:` block under `## Implementation Tasks` must contain all four bold labels: `**Objective:**`, `**Files:**`, `**Key Decisions / Notes:**`, and `**Definition of Done:**`. Fix any plain labels such as `Files:`, `Key Decisions:`, `Definition of Done:`, or `Verification:` before asking for approval.

Self-review the plan for obvious issues before requesting approval: missing edge cases, unclear DoD criteria, placeholder text, wrong task-card label format, and unresolved ambiguities.
CODEX-END -->
