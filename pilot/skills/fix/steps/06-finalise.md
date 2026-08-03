## Step 6: Finalise

### 6.1 Automated changes review (when enabled)

⛔ **Step 4 (Verify End-to-End) must be complete, with concrete evidence, before any reviewer runs.** Reviewers audit the fix; they never substitute for running the program.

The same Console Settings toggles that drive `/spec`'s post-implementation review govern `/fix`. Run whichever are enabled and **apply their findings before** the worktree commit (6.2) and the approval gate (6.3), so review-driven changes land in the single bundled commit.

<!-- CC-ONLY -->
```bash
echo "CHANGES_REVIEW=$PILOT_CHANGES_REVIEW_ENABLED"          # changes-review sub-agent — runs unless explicitly "false"
echo "CODEX_REVIEW=$PILOT_CODEX_CHANGES_REVIEW_ENABLED"      # Codex companion review — runs only when "true"
```

Skip straight to 6.2 **only** when `PILOT_CHANGES_REVIEW_ENABLED` IS `"false"` AND `PILOT_CODEX_CHANGES_REVIEW_ENABLED` is not `"true"`. Otherwise at least one reviewer runs — changes-review is on by default, so an unset value runs it.

⛔ **Never `Skill(skill='code-review', ...)` here.** It carries `disable-model-invocation`, so the call is rejected and the fix ships with no review while the report claims one. A deeper review is the user's to start by typing `/code-review`.
<!-- /CC-ONLY -->
<!-- CODEX-START
```bash
echo "CHANGES_REVIEW=$PILOT_CHANGES_REVIEW_ENABLED"          # native changes-review agent — runs unless explicitly "false"
```

The Codex companion (`PILOT_CODEX_CHANGES_REVIEW_ENABLED`) does NOT apply in Codex. Skip to 6.2 **only** when `PILOT_CHANGES_REVIEW_ENABLED` IS `"false"`; otherwise the native `changes-review` agent runs (an unset value runs it).
CODEX-END -->

#### 6.1.pre Instrumentation gate, then stage the fix (whenever any reviewer runs)

**Scan the unstaged tree before anything is staged or committed.** Step 3.5 was the primary gate; this is the last point at which a `SPEC-DEBUG` or stray `console.log` can still be caught pre-commit.

```bash
git diff | grep -nE "SPEC-DEBUG|^\+.*\b(console\.log|console\.error|print\()" && \
  { echo "Leftover instrumentation — remove before staging/commit"; } || echo "instrumentation clean"
```

Remove any match and re-run.

Then stage the change's own files. The fix and its new test sit unstaged, and a brand-new test file is untracked — which misfires reviewers both ways: one reading `git status --untracked-files=all` flags the new test as a spurious `critical` ("untracked deliverable"), while one reading only `git diff HEAD` silently omits it, leaving the test unreviewed.

```bash
git add <fix_file> <test_file>   # only the bugfix's own files — never unrelated dirty paths
git status --short --untracked-files=all | grep '^??' || true   # should list only files outside this fix
```

A bare `git add -N` is not enough — `git status` still reports the path as untracked. **Staging is not committing**: the commit (6.2) still waits for the review and the approval gate. All reviewers scope to `git diff HEAD`, which now includes the staged additions; a committed ref-range would be empty pre-commit and scan nothing.

<!-- CC-ONLY -->
#### 6.1.0 Bugfix summary artifact

For `/fix` the "plan" is this conversation, not a file. Both reviewers anchor on a plan artifact — the changes-review sub-agent and the Codex companion — so build one:

```bash
SESS_DIR="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"; mkdir -p "$SESS_DIR"
FIX_PLAN_FILE="$SESS_DIR/fix-review-plan.md"
cat > "$FIX_PLAN_FILE" <<'PLAN_EOF'
# /fix Bugfix Summary
Bug: <one-line bug>
Root cause: <file>:<line> — <what>
Fix: <one-line fix description>
Reproducing test: <test file>::<test name> (added in Step 2 RED)
PLAN_EOF
```

Session-isolated and deterministic (no `/tmp`, no `$$`): later Bash calls, the reviewer prompt, and cleanup all reconstruct this path from outside that shell.

#### 6.1.a Codex companion review — launch FIRST when `PILOT_CODEX_CHANGES_REVIEW_ENABLED == "true"`

An independent second opinion, launched before the inline review so the two run in parallel.

**Codex-once:** at most one companion run per `/fix` invocation. Check the sentinel first; if it exists, a prior approval-gate loop already ran it — skip the launch and the Codex half of 6.1.c.

```bash
CODEX_FLAG="$SESS_DIR/codex-changes-review-ran-fix.flag"
[ -f "$CODEX_FLAG" ] && echo "Codex already reviewed this fix in this session — skipping (codex-once)."
```

Otherwise **read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/codex-companion-protocol.md` and follow it end to end** (locate → render → launch → stall monitor → collect → mark). It is the single source of truth for the companion run loop. Supply:

| Protocol input | Value for `/fix` |
|---|---|
| `PROMPT_TEMPLATE` | `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/changes-review-codex.md` |
| `{{PLAN_PATH}}` | `$FIX_PLAN_FILE` from 6.1.0 |
| `{{PLAN_GOAL}}` | `Bugfix for: <one-line bug>. Root cause at <file>:<line>. The reproducing test must reliably fail before the fix and pass after.` |
| `{{BASE_REF}}` | `HEAD` — the fix is staged, not committed |
| `{{CHANGED_FILES}}` | `git status --short --untracked-files=all` paths for this fix |
| `SLUG` | `fix` |
| `CODEX_FLAG` | the path above |

Launch, then **continue to 6.1.b immediately** — the changes review runs while Codex churns. Collect in 6.1.c. If the companion is missing or its job never registers, continue with the 6.1.b results and note the gap in the 6.6 report.

#### 6.1.b Changes review — when `PILOT_CHANGES_REVIEW_ENABLED` is not `"false"`

Launch the changes-review sub-agent in the background:

```bash
FINDINGS_PATH="$SESS_DIR/findings-changes-review-fix.json"
rm -f "$SESS_DIR"/findings-changes-review-fix*.json   # incl. -rN files from prior runs
```

```
Agent(
  subagent_type="changes-review",
  run_in_background=true,
  prompt="""
  **Plan file:** <$FIX_PLAN_FILE path>
  **Changed files:** <fix file> <test file>
  **Output path:** <$FINDINGS_PATH>

  Review the diff (git diff HEAD -- <fix file> <test file>) against the bugfix summary: root-cause fix quality, test quality, regressions.
  Write findings JSON to output_path using the Write tool.
  IMPORTANT: Include the plan file path in your output JSON as the "plan_file" field.
  """
)
```

Wait by polling the file — ⛔ never `TaskOutput`, which dumps the whole agent transcript into context:

```bash
for i in $(seq 1 150); do [ -f "$FINDINGS_PATH" ] && echo READY && break; sleep 2; done
```

Run that as `Bash(run_in_background=true, timeout=330000)` (the 5-min loop exceeds the foreground timeout; `sleep` is allowed in background and you are notified on exit), then Read the file once. Not READY afterwards usually means slow, not dead — relaunch ONCE with a fresh output path (`findings-changes-review-fix-r2.json`) and poll that. Never reuse an in-flight path: a late write from the superseded agent must not be collected as the fresh run.

If the relaunch also produces nothing, continue with whatever the Codex companion returned and note the gap in the 6.6 report. ⛔ Do NOT fall back to `Skill(skill='code-review', ...)` — the call is rejected, so it produces no review at all.

#### 6.1.c Apply findings

Both reviewers receive the bug summary, so root-cause-vs-symptom judgment is theirs to challenge — but the final call stays here (Step 1.3 trace + the 6.5 checklist).

**Lineage is evaluated FIRST.** A finding on a file outside the bug's lineage — the fix file, its test, and files the fix legitimately touched — is mention-only regardless of severity. Out-of-lineage crashes get reported to the user, never auto-fixed. Only in-lineage findings run through the rows below.

| Finding class | Action |
|---------------|--------|
| Outside the bug's lineage (CHECK FIRST — overrides every row below) | Mention in one line; do not auto-apply |
| `failure_scenario` names a concrete crash, wrong output, security, or data-integrity problem | **must_fix** — fix now, then re-run Step 3.4's targeted tests + Step 5.2's full suite |
| Cleanup / efficiency finding, single-site, in-lineage | **should_fix** — fix |
| Would expand scope (3+ files, architectural) | Summarise; let the user decide between fixing here and a `/spec` follow-up |

Changes-review findings carry explicit severities — map them through the same lineage-first rule (`must_fix` → row 2, `should_fix` → row 3, `suggestion` → mention). Codex findings map by the table in the protocol file's §5.

If a reviewer returns nothing blocking, report "Review: no blocking findings" in one line and move on.
<!-- /CC-ONLY -->
<!-- CODEX-START
When `PILOT_CHANGES_REVIEW_ENABLED` is not `"false"`, run the managed Codex `changes-review` custom agent on the bugfix diff before finalising. (The Codex *companion* review — `PILOT_CODEX_CHANGES_REVIEW_ENABLED` — is a Claude-Code-only plugin path and does not run here.)

1. Build a one-page bugfix summary as the review anchor:

```bash
SESS_DIR="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"; mkdir -p "$SESS_DIR"
FIX_PLAN_FILE="$SESS_DIR/fix-review-plan.md"
cat > "$FIX_PLAN_FILE" <<'PLAN_EOF'
# Bugfix Summary
Bug: <one-line bug>
Root cause: <file>:<line> — <what>
Fix: <one-line fix description>
Reproducing test: <test file>::<test name>
PLAN_EOF
```

2. Spawn the review agent and wait for its final JSON response:

```python
review = multi_agent_v1.spawn_agent(
    agent_type="changes-review",
    message="""
    Plan file: <FIX_PLAN_FILE path>
    User request: Bugfix — <one-line bug>
    Changed files: [git status --short list]

    Review the bugfix diff: quality and goal achievement. The "plan" is a one-page bugfix
    summary, not a multi-task spec — judge compliance against the bug, not absent feature tasks.
    Return ONLY valid JSON matching the changes-review schema. Include the plan file path in `plan_file`.
    """,
)
result = multi_agent_v1.wait_agent(targets=[review.agent_id], timeout_ms=600000)
```

3. Parse the final message as JSON. If parsing fails, treat the raw message as one `suggestion` finding and continue. Validate `plan_file` matches `$FIX_PLAN_FILE`; on mismatch discard the stale result and self-review instead.

4. Lineage first — a finding outside the fix file, its test, and files the fix legitimately touched is mention-only regardless of severity. Otherwise: `must_fix` → fix now; `should_fix` → fix when single-site (else summarise and let the user decide); `suggestion` → mention. After any fix, re-run the targeted test + full suite. Then `rm -f "$FIX_PLAN_FILE"`.
CODEX-END -->

### 6.2 Worktree mode — single commit

Only when this session is already inside a `.worktrees/spec-*` checkout. Bundle test + fix + any review-driven fixes into one commit:

```bash
git add <test_file> <fix_file>
git commit -m "fix: <one-line description>" -m "Root cause: <file>:<line> — <what was wrong and why>"
```

The conventional `fix:` prefix triggers a patch release if this branch ships. Don't split into multiple commits in the quick lane. The body is the Step 1.5 statement with its `Confidence` tail dropped (the template already carries the `Root cause:` prefix — don't repeat it inside the placeholder); it gives the next debugger the confirmed cause straight from `git log`.

### 6.3 Approval gate (when enabled)

⛔ **The approval summary must contain what you actually ran and observed in Step 4.** If you cannot fill in `E2E:` with concrete evidence, Step 4 is not finished — go back rather than asking for approval.

Read `PILOT_PLAN_APPROVAL_ENABLED`. `"false"` → skip 6.3 entirely, mark done.

Otherwise summarise and ask, offering: `"Approve — done"`, `"Request changes"`, and `"Explain the fix in more detail"` (present in the first ask only; drop it from any re-ask to avoid loops).

```
AskUserQuestion(
  question="Bugfix complete.\n\nBug: <one line>\nRoot cause: <file>:<line> — <what>\nFix: <one-line description of the change>\nTests: reproducing test added (<test_name>), full suite green.\nReview: <none | changes-review: N findings, all resolved | Codex: approve | ...>\nE2E: <command/URL you ran and the concrete observation that proves the fix — e.g. 'curl /search -d {} → 200 with [results]', 'opened /tasks page, saved end_date=2026-05-15, list shows 2026-05-15', 'ran pilot register-plan ./foo.md PENDING → exit 0, plan visible in console'>\n\nReview the diff in the Console's Changes tab. Approve when ready.",
  options=[<see list above>]
)
```

- **Approve** → done.
- **Request changes** → the user describes the problem freely. Treat it as a new investigation: Step 1.3 (re-trace) → Step 2 onward. Reviews re-run on the new fix scoped to files changed since the previous review, not the whole diff again.
<!-- CC-ONLY -->
  Re-run mechanics: codex-once keeps the companion to one run per invocation. For the changes review — rebuild `$FIX_PLAN_FILE`, delete the findings file, relaunch with `Changed files:` = files changed since the previous review.
<!-- /CC-ONLY -->
<!-- CODEX-START
  Re-run mechanics: spawn the managed `changes-review` custom agent again on the updated diff (rebuild the one-page summary first so its `Plan file:` anchor exists), listing only the files changed since the previous review.
CODEX-END -->
- **Explain the fix in more detail** → write the fuller walkthrough (causal chain trigger → root cause; why that boundary is the right place to fix; what the diff means line by line; alternatives considered and rejected). Change no code, then re-ask without the Explain option.

### 6.4 Console notification

```bash
~/.pilot/bin/pilot notify plan_approval "Bugfix complete" "<one-line bug>" 2>/dev/null || true
```

Best-effort — don't block on failure.

### 6.5 Pre-report checklist

Every box must hold before you write the report. Any gap → return to the step that owns it.

- [ ] Reproducing test passes — fresh run, this message (Step 3.3).
- [ ] Full anti-regression suite green — fresh run (Step 5.2).
- [ ] E2E executed against the actual program, concrete evidence captured (Step 4).
- [ ] Enabled reviewers ran; every `must_fix` / `should_fix` resolved or escalated (6.1).
- [ ] Instrumentation clean — confirmed at 6.1.pre before staging. In worktree mode, where 6.2 already committed, re-check the commit: `git show HEAD | grep -nE "SPEC-DEBUG|console\.log|console\.error|print\("` must return nothing; amend if it fires.
- [ ] Diff is small and every changed line traces to the bug.
- [ ] Docs updated if the fix changed documented behaviour, a flag, or a config default — or "no doc impact" stated deliberately.
- [ ] Worktree mode: one bundled `fix:` commit. Otherwise: changes ready, no commit.

### 6.6 Report

```
Bugfix complete — <bug>.
Root cause: <file>:<line>.
Tests: 1 new reproducing test, full suite green.
Review: <none enabled | changes-review sub-agent / native changes-review + Codex, no blocking findings | N findings resolved>.
E2E: <command/URL run> → <observation that proves the symptom is gone>.
Docs: <files updated | no doc impact>.

Run /clear before starting new work — this resets context while keeping project rules loaded.
```

The `E2E:` line is **mandatory** — it is the record that the actual program was exercised, not just the unit tests.

### 6.7 Post-mortem flag (optional, one line)

You know more now than when you started, so ask once: **what would have prevented this bug?** If the answer is architectural — no clean test seam, hidden coupling, validation absent at the boundary the bad data crossed, a repeated near-miss in this area — name it in one line:

```
Follow-up (architectural): <one-line description> — candidate for /spec.
```

Skip when the honest answer is "nothing structural — a typo / off-by-one / wrong default". Don't manufacture follow-ups.

ARGUMENTS: $ARGUMENTS
