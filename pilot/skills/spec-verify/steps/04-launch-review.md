## Step 4: Launch Code Review Agent (Early)

**⛔ If `PILOT_CHANGES_REVIEW_ENABLED` is `"false"` (from Step 0),** skip this step entirely and proceed to Step 5. (Automated checks in Step 5 still run; only the agent-based review is skipped.)

**When enabled:** Launch the reviewer IMMEDIATELY — it works in the background while you run automated checks.

#### 4a: Gather Context

```bash
git status --short  # Changed files
echo $PILOT_SESSION_ID
```

**Validate session ID:** If `$PILOT_SESSION_ID` is empty, fall back to `"default"` to avoid writing to `~/.pilot/sessions//`.

Collect: changed files list, test framework constraints, runtime environment info, plan risks section.

**Derive plan slug** from the plan filename: strip the date prefix (`YYYY-MM-DD-`) and `.md` extension. Example: `2026-03-02-sku-builder-modal-cleanup.md` → `sku-builder-modal-cleanup`.

Output path: `~/.pilot/sessions/<session-id>/findings-changes-review-<plan-slug>.json`

#### 4b: Launch

**⛔ Delete stale changes-review findings before launching** (previous run may have left a file):

```bash
rm -f ~/.pilot/sessions/$PILOT_SESSION_ID/findings-changes-review-*.json
```

```
Task(
  subagent_type="pilot:changes-review",
  run_in_background=true,
  prompt="""
  **Plan file:** <plan-path>
  **User request:** <original task description that invoked /spec>
  **Changed files:** [file list]
  **Output path:** <absolute path to findings JSON>
  **Runtime environment:** [how to start, port, deploy path]
  **Test framework constraints:** [what it can/cannot test]

  Review implementation: compliance (plan match + user request match), quality (security, bugs, tests, performance), goal (achievement, artifacts, wiring).
  Performance: check for expensive uncached work on hot paths, heavy dependency imports with lighter alternatives, and repeated invocations that redo work when input hasn't changed.
  Write findings JSON to output_path using Write tool.
  IMPORTANT: Include the plan file path in your output JSON as the "plan_file" field.
  """
)
```

**Do NOT wait.** Proceed to Codex launch (if enabled) or Step 5 immediately.

#### Codex Adversarial Review (Optional — launch immediately after Claude reviewer)

**If `PILOT_CODEX_CHANGES_REVIEW_ENABLED` is `"true"` (from Step 0):**

Launch Codex review NOW — it runs in parallel with the Claude reviewer above.

**⛔ Codex-once rule.** Codex runs at most once per `/spec` invocation. Before launching, check the sentinel file. If it exists, the review already ran in this session — skip the launch and the collection sub-step in Step 7. Verify-phase iterations (re-verify after fixing findings, code-review-gate annotation fixes) do NOT trigger another Codex run.

```bash
SESS_ID="${PILOT_SESSION_ID:-default}"
CODEX_FLAG="$HOME/.pilot/sessions/$SESS_ID/codex-ran-<plan-slug>.flag"
if [ -f "$CODEX_FLAG" ]; then
  echo "Codex already reviewed this plan in this session — skipping (codex-once)."
  # Skip the launch below and the Codex collection sub-step in Step 7.
fi
```

1. Detect companion path and ensure project root:
```bash
CODEX_COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
```

2. Launch adversarial review in background using `--scope working-tree` (reviews all uncommitted changes regardless of staging state — works in both worktree and non-worktree mode). **⛔ Use `Bash(run_in_background=true)`** — the companion's `--background` flag is a no-op for reviews (only works for `task`), so we use Claude Code's background bash instead:
```bash
cd "$PROJECT_ROOT" && node "$CODEX_COMPANION" adversarial-review --scope working-tree "Challenge this implementation: <plan summary/goal>. Plan: <plan-path>. Focus on: wrong approach, missing edge cases, security gaps, untested paths, and design choices that could fail under load."
```
**Do NOT wait** — proceed to Step 5 immediately. You'll be notified when the background bash completes.
