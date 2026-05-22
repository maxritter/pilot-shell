## Step 6: Finalise

### 6.1 Worktree mode — single commit

If a worktree was created: bundle test + fix into one commit.

```bash
git add <test_file> <fix_file>
git commit -m "fix: <one-line description>"
```

The conventional `fix:` prefix triggers a patch release if/when this branch ships. Do not split into multiple commits in the quick lane.

### 6.2 Approval gate (only when enabled)

⛔ **Before showing the approval question, you MUST have completed Step 4 (Verify End-to-End) with evidence.** "Tests pass" is not enough — the approval summary must include what you actually ran and what you observed. If you cannot fill in `**E2E:**` below with concrete evidence, you have not finished Step 4 — go back, do not ask for approval.

Read `PILOT_PLAN_APPROVAL_ENABLED`. If `"false"` → skip 6.2 entirely, mark done.

Read `PILOT_CODEX_CHANGES_REVIEW_ENABLED` to decide whether to offer the optional Codex review:

```bash
echo "CODEX_REVIEW=$PILOT_CODEX_CHANGES_REVIEW_ENABLED"
```

When approval is enabled, summarise + ask. Build the `options` array in this order:

1. `"Approve — done"`
2. `"Request changes"`
3. `"Explain the fix in more detail"` — always present.
4. `"Run Codex adversarial review for added confidence"` — **only when** `PILOT_CODEX_CHANGES_REVIEW_ENABLED == "true"`. Omit the entry entirely otherwise; do NOT show a disabled / greyed option.

```
AskUserQuestion(
  question="Bugfix complete.\n\nBug: <one line>\nRoot cause: <file>:<line> — <what>\nFix: <one-line description of the change>\nTests: reproducing test added (<test_name>), full suite green.\nE2E: <command/URL you ran and the concrete observation that proves the fix — e.g. 'curl /search -d {} → 200 with [results]', 'opened /tasks page, saved end_date=2026-05-15, list shows 2026-05-15', 'ran pilot register-plan ./foo.md PENDING → exit 0, plan visible in console'>\n\nReview the diff in the Console's Changes tab. Approve when ready.",
  options=[<see list above>]
)
```

Handle:

- **Approve** → done.
- **Request changes** → user describes problem in free-form. Treat as a new investigation: re-run Step 1.3 (re-trace) → Step 2 onward.
- **Explain the fix in more detail** → write a fuller walkthrough (causal chain from trigger → root cause; why the boundary you fixed at is correct; line-by-line meaning of the diff; alternatives considered and rejected). Do NOT modify code. Then re-ask 6.2 — drop the "Explain" option from the new list to avoid loops; keep the Codex option if still applicable.
- **Run Codex adversarial review** (only present when enabled) → run sub-step 6.2.a, then re-ask 6.2 with this option removed (one Codex run per `/fix` invocation).

#### 6.2.a Optional Codex Adversarial Review

Run **only** when the user explicitly picked "Run Codex adversarial review" in 6.2. Opt-in, never automatic — the quick-lane reproducing test plus Step 4 E2E remain the proof of correctness. Codex is for added confidence on user request.

1. **Locate the companion.** If missing, tell the user "Codex companion not found — install the openai-codex plugin or disable Codex in Console Settings" and return to 6.2 with the Codex option removed.

   ```bash
   CODEX_COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
   PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
   [ -z "$CODEX_COMPANION" ] && echo "MISSING"
   ```

2. **Build the review prompt file** by rendering the **template at `${CLAUDE_PLUGIN_ROOT}/agents/changes-review-codex.md`** (the same template `spec-verify` uses — single source of truth for code-review semantics).

   For `/fix`, the "plan" is the conversation, not a file. Inline a one-page plan into a temp file so the template's `{{PLAN_PATH}}` substitution has something to point at:

   ```bash
   PROMPT_TEMPLATE="${CLAUDE_PLUGIN_ROOT}/agents/changes-review-codex.md"
   PROMPT_FILE="/tmp/codex-fix-review-${PILOT_SESSION_ID:-default}-$$.md"
   FIX_PLAN_FILE="/tmp/codex-fix-plan-${PILOT_SESSION_ID:-default}-$$.md"
   cat > "$FIX_PLAN_FILE" <<'PLAN_EOF'
   # /fix Bugfix Summary
   Bug: <one-line bug>
   Root cause: <file>:<line> — <what>
   Fix: <one-line fix description>
   Reproducing test: <test file>::<test name> (added in Step 3.3)
   PLAN_EOF

   PLAN_GOAL="Bugfix for: <one-line bug>. Root cause at <file>:<line>. The reproducing test must reliably fail before the fix and pass after."
   BASE_REF="$(git rev-parse --abbrev-ref HEAD@{upstream} 2>/dev/null | sed 's|^[^/]*/||' || echo main)"
   CHANGED_FILES=$(git status --short --untracked-files=all | awk '{print "- " $2}')

   PLAN_PATH="$FIX_PLAN_FILE" PLAN_GOAL="$PLAN_GOAL" BASE_REF="$BASE_REF" CHANGED_FILES="$CHANGED_FILES" \
   PROMPT_TEMPLATE="$PROMPT_TEMPLATE" PROMPT_FILE="$PROMPT_FILE" \
   uv run --no-project python -c '
   import os, pathlib
   text = pathlib.Path(os.environ["PROMPT_TEMPLATE"]).read_text()
   for key in ("PLAN_PATH", "PLAN_GOAL", "BASE_REF", "CHANGED_FILES"):
       text = text.replace("{{" + key + "}}", os.environ[key])
   pathlib.Path(os.environ["PROMPT_FILE"]).write_text(text)
   '
   ```

3. **Launch the task in background.** Use `task --background --prompt-file` (the companion's own background mode is supported for `task` — unlike `review`/`adversarial-review`).

   ```
   Bash(
     command="cd $PROJECT_ROOT && node $CODEX_COMPANION task --background --prompt-file \"$PROMPT_FILE\"",
     run_in_background=false,
     timeout=60000
   )
   ```

   Capture the job ID from stdout (`task-…` token). **Verify registration before polling** — fail-fast guard against synthetic-ID launches:

   ```bash
   node "$CODEX_COMPANION" status "$JOB_ID" --json 2>/dev/null | grep -q '"status":' \
     || { echo "Codex launch did not register with broker (synthetic task id?). Aborting Codex; mark this run as no-op."; JOB_ID=""; }
   ```

   If `$JOB_ID` is empty, skip polling, return to 6.2 with the Codex option removed. Otherwise poll for completion:

   ```bash
   JOB_ID="<captured-task-id>"
   for i in $(seq 1 150); do
     STATE=$(node "$CODEX_COMPANION" status "$JOB_ID" --json 2>/dev/null \
       | uv run --no-project python -c "import json,sys
try: print((json.load(sys.stdin).get('job') or {}).get('status') or 'unknown')
except Exception: print('parse_error')" 2>/dev/null)
     case "$STATE" in
       completed)        echo "READY @ iter=$i"; break ;;
       failed|parse_error|unknown) echo "FAIL state=$STATE iter=$i"; break ;;
     esac
     sleep 4
   done
   ```

   Treat `parse_error` / `unknown` as failure — they indicate the job vanished or the broker is unreachable, not normal in-progress state.

   Run this as `Bash(run_in_background=true, timeout=600000)`. ⛔ **Wait for the completion notification** — do NOT read the result file before the `<task-notification>` with `<status>completed</status>` arrives.

4. **On completion notification, retrieve findings via the companion's public interface:**

   ```bash
   node "$CODEX_COMPANION" result "$JOB_ID" --json > /tmp/codex-fix-result-$$.json
   ```

   Read `/tmp/codex-fix-result-$$.json` with the `Read` tool. Verify `storedJob.status === "completed"`, then parse `storedJob.result.rawOutput` as JSON (`{verdict, summary, findings, next_steps}`). If JSON parse fails, fall back to `storedJob.rendered` and surface as a suggestion-level finding.

5. **Act on findings — same severity → action map as `/spec-verify`:**

   | Severity | Action |
   |----------|--------|
   | `critical` / `high` | **must_fix** — fix immediately, re-run the targeted test from Step 3.4 + the full suite from Step 5.2, then re-ask 6.2 |
   | `medium` / `low` | **should_fix** — fix if it's a single-site change consistent with the original bug's lineage; if it would expand scope (3+ files, architectural), summarise to the user and let them decide whether to fix here or open a `/spec` follow-up |
   | `info` | **suggestion** — mention in one line; do not auto-apply |

   If verdict is `approve` and there are no must/should findings: report "Codex: approve — no blocking findings" and re-ask 6.2.

6. **Cleanup.** Delete the temp prompt and bugfix-summary files:
   ```bash
   rm -f "$PROMPT_FILE" "$FIX_PLAN_FILE"
   ```

7. **Launch failure handling.** If `$JOB_ID` is empty after the completion notification, or `storedJob.status` is `"failed"`: surface the captured stderr to the user, do **not** silently mark the bugfix done. Return to 6.2 with the Codex option removed.

### 6.3 Console notification (always, when binary present)

```bash
~/.pilot/bin/pilot notify plan_approval "Bugfix complete" "<one-line bug>" 2>/dev/null || true
```

Best-effort — don't block on failure.

### 6.4 Pre-report verification checklist

⛔ Walk every box before writing the report. Missing any one = not done — return to the relevant step.

- [ ] Reproducing test passes (Step 3.3 fresh run, this message).
- [ ] Full anti-regression suite green (Step 5.2 fresh run).
- [ ] E2E executed against the actual program with concrete evidence captured (Step 4).
- [ ] `git diff | grep -E "SPEC-DEBUG|^\\+.*\\b(console\\.log|print\\()"` returns nothing (no leftover instrumentation).
- [ ] Diff is small and every changed line traces to the bug (lineage rule).
- [ ] Worktree mode: single bundled `fix:` commit. Non-worktree: changes ready, no commit yet.

If any box is unchecked, do not write the report and do not ask for approval — fix the gap first.

### 6.5 Report

```
Bugfix complete — <bug>.
Root cause: <file>:<line>.
Tests: 1 new reproducing test, full suite green.
E2E: <command/URL run> → <observation that proves the symptom is gone>.

Run /clear before starting new work — this resets context while keeping project rules loaded.
```

The `E2E:` line is **mandatory** — it documents that the actual program was exercised, not just the unit tests.

### 6.6 Post-mortem flag (optional, one line)

Ask once, now that you have more information than when you started: **what would have prevented this bug?** If the answer is architectural — no clean test seam, hidden coupling between modules, validation absent at the boundary the bad data crossed, repeated near-miss in the same area — name it as a `/spec` follow-up candidate in one line:

```
Follow-up (architectural): <one-line description> — candidate for /spec.
```

Skip when the answer is "nothing structural, it was a one-line typo / off-by-one / wrong default." Don't manufacture follow-ups.

ARGUMENTS: $ARGUMENTS
