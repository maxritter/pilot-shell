## Step 11: Plan Verification

**⛔ If `PILOT_SPEC_REVIEW_ENABLED` is `"false"` (from Step 0),** skip this step entirely and proceed to Step 13.

**When enabled:** Run spec-review for every feature spec. Small plans benefit from a second pair of eyes just as much as large ones — missing edge cases and unclear DoD criteria are size-independent.

```bash
SESS_ID=$(echo $PILOT_SESSION_ID)
```

**Derive plan slug** from the plan filename: strip the date prefix (`YYYY-MM-DD-`) and `.md` extension. Example: `2026-03-02-sku-builder-modal-cleanup.md` → `sku-builder-modal-cleanup`.

Output path: `~/.pilot/sessions/<SESS_ID>/findings-spec-review-<plan-slug>.json`

**⛔ Delete stale findings before launching** (previous run of the same plan may have left a file):

```bash
rm -f "$OUTPUT_PATH"
```

```
Task(
  subagent_type="pilot:spec-review",
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

**⛔ NEVER use `TaskOutput`** to retrieve results — it dumps the full agent transcript into context, wasting thousands of tokens.

#### Codex Adversarial Review (Optional — launch immediately after Claude reviewer)

**If `PILOT_CODEX_SPEC_REVIEW_ENABLED` is `"true"` (from Step 0):**

Launch Codex review NOW — it runs in parallel with the Claude reviewer above.

1. Detect companion path, project root, and base branch:
```bash
CODEX_COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
# Use worktree base branch if in worktree, otherwise detect repo default branch
BASE_BRANCH=$(~/.pilot/bin/pilot worktree status --json 2>/dev/null | grep -o '"base_branch":"[^"]*"' | cut -d'"' -f4)
[ -z "$BASE_BRANCH" ] && BASE_BRANCH=$(cd "$PROJECT_ROOT" && git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")
```

2. Launch adversarial review in background. **⛔ Use `Bash(run_in_background=true)`** — the companion's `--background` flag is a no-op for reviews (only works for `task`), so we use Claude Code's background bash instead. The review runs synchronously inside the bash, and you'll be notified when it completes:
```bash
cd "$PROJECT_ROOT" && node "$CODEX_COMPANION" adversarial-review --base "$BASE_BRANCH" "Challenge this plan: <plan summary/goal>. Plan file: <plan-path>. Focus on: wrong assumptions, missing edge cases, scope gaps, and design choices that could fail under real-world conditions."
```
**Do NOT wait** — proceed to collect the Claude reviewer results first.

#### Collect Review Results

**Wait for Claude reviewer results (bash polling — NOT Read loop):**

```bash
OUTPUT_PATH="<findings-path>"
for i in $(seq 1 150); do [ -f "$OUTPUT_PATH" ] && echo "READY" && break; sleep 2; done
```

Then Read the file once. If not READY after 5 min, re-launch synchronously.

**⛔ Validate findings:** After reading the JSON, verify that the `plan_file` field matches the current plan path. If it doesn't match, the findings are stale from a previous `/spec` — delete the file, re-launch the reviewer, and wait again.

**Fix Claude reviewer findings immediately** — must_fix → should_fix. Suggestions if reasonable.

#### Collect Codex Results (if launched)

**⛔ MANDATORY — NEVER skip or defer the Codex review.** If Codex was launched above, you MUST collect and act on its results before proceeding. The Codex review runs as `Bash(run_in_background=true)` — you will be automatically notified when it completes.

**⛔ The completion notification is the ONLY valid signal.** Do NOT read the output file to check if the review is done. The file may contain partial output from an in-progress review — reading it before the notification arrives leads to false conclusions ("no findings" when the review is still running). This is the #1 cause of premature Codex skip.

**⛔ If the notification hasn't arrived yet:** STOP. Do NOT proceed to Step 12 or approval. Do NOT read the output file. Do NOT conclude the review failed. Wait for the `<task-notification>` with `<status>completed</status>`. If you are tempted to check the file — that is the exact mistake this rule prevents.

1. **When (and ONLY when) the completion notification arrives**, read the background bash output. **Filter out `[codex]` prefixed log lines** — use `ctx_execute_file` to extract only non-`[codex]` lines. Search for `# Codex Adversarial Review` section via `ctx_search`.

2. **Parse the output:** Extract `Verdict:` and `Findings:` lines. Map severities: `[high]` / `[critical]` → must_fix, `[medium]` / `[low]` → should_fix. Fix all must_fix/should_fix.

3. **If the background bash timed out or failed** (exit code non-zero in the notification): Re-launch synchronously and wait. Only skip if the second attempt also fails.

**If Codex was NOT launched**, proceed after all Claude reviewer must_fix/should_fix resolved.
