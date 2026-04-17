## Step 7: Codex Adversarial Review (Optional)

**If `PILOT_CODEX_SPEC_REVIEW_ENABLED` is `"true"` (from Step 0):**

1. Detect companion path, project root, and base branch:
```bash
CODEX_COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
# Use worktree base branch if in worktree, otherwise detect repo default branch
BASE_BRANCH=$(~/.pilot/bin/pilot worktree status --json 2>/dev/null | grep -o '"base_branch":"[^"]*"' | cut -d'"' -f4)
[ -z "$BASE_BRANCH" ] && BASE_BRANCH=$(cd "$PROJECT_ROOT" && git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")
```

2. Launch adversarial review in background. **⛔ Use `Bash(run_in_background=true)`** — the companion's `--background` flag is a no-op for reviews (only works for `task`), so we use Claude Code's background bash instead:
```bash
cd "$PROJECT_ROOT" && node "$CODEX_COMPANION" adversarial-review --base "$BASE_BRANCH" "Challenge this bugfix plan: <plan summary/root cause>. Plan: <plan-path>. Focus on: wrong root cause, incomplete fix, missing edge cases, regression risk, and whether the fix addresses symptoms vs cause."
```

3. **⛔ MANDATORY — NEVER skip or defer.** The completion notification is the ONLY valid signal. Do NOT read the output file to check if the review is done — the file may contain partial output from an in-progress review. Reading it before the notification leads to false conclusions ("no findings" when the review is still running). Wait for the `<task-notification>` with `<status>completed</status>`.

4. **When (and ONLY when) the completion notification arrives**, read the background bash output. **Filter out `[codex]` prefixed log lines** — use `ctx_execute_file` to extract only non-`[codex]` lines. Search for `# Codex Adversarial Review` section via `ctx_search`. Extract `Verdict:` and `Findings:` lines. Map severities: `[high]` / `[critical]` → must_fix, `[medium]` / `[low]` → should_fix. Fix all must_fix/should_fix in the plan.

5. **If the background bash timed out or failed** (exit code non-zero in the notification): Re-launch synchronously and wait. Only skip if the second attempt also fails.
