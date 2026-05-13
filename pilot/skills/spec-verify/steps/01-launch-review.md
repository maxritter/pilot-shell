## Phase A — Finalize the Code

## Step 1: Launch Code Review Agent (Early)

### 1a: Clean Up Stale Spec-Review Findings (always run, before any launch)

**⛔ ALWAYS run this first** — regardless of whether changes-review is enabled. Spec-review findings are stale artifacts from the planning phase that were already addressed during implementation.

```bash
rm -f ~/.pilot/sessions/$PILOT_SESSION_ID/findings-spec-review-*.json
```

---

**⛔ If `PILOT_CHANGES_REVIEW_ENABLED` is `"false"` (from Step 0),** skip the rest of this step and proceed to Step 2. (Automated checks in Step 2 still run; only the agent-based review is skipped.)

**When enabled:** Launch the reviewer IMMEDIATELY — it works in the background while you run automated checks.

#### 1b: Gather Context

```bash
git status --short  # Changed files
echo $PILOT_SESSION_ID
```

**Validate session ID:** If `$PILOT_SESSION_ID` is empty, fall back to `"default"` to avoid writing to `~/.pilot/sessions//`.

Collect: changed files list, test framework constraints, runtime environment info, plan risks section.

**Derive plan slug** from the plan filename: strip the date prefix (`YYYY-MM-DD-`) and `.md` extension. Example: `2026-03-02-sku-builder-modal-cleanup.md` → `sku-builder-modal-cleanup`.

Output path: `~/.pilot/sessions/<session-id>/findings-changes-review-<plan-slug>.json`

#### 1c: Launch

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

**Do NOT wait.** Proceed to Codex launch (if enabled) or Step 2 immediately.

#### Codex Adversarial Review (Optional — launch immediately after Claude reviewer)

**If `PILOT_CODEX_CHANGES_REVIEW_ENABLED` is `"true"` (from Step 0):**

Launch Codex review NOW — it runs in parallel with the Claude reviewer above.

**⛔ Codex-once rule.** Codex runs at most once per `/spec` invocation. Before launching, check the sentinel file. If it exists, the review already ran in this session — skip the launch and the collection sub-step in Step 3. Verify-phase iterations (re-verify after fixing findings, code-review-gate annotation fixes) do NOT trigger another Codex run.

```bash
SESS_ID="${PILOT_SESSION_ID:-default}"
CODEX_FLAG="$HOME/.pilot/sessions/$SESS_ID/codex-changes-review-ran-<plan-slug>.flag"
if [ -f "$CODEX_FLAG" ]; then
  echo "Codex already reviewed this plan in this session — skipping (codex-once)."
  # Skip the launch below and the Codex collection sub-step in Step 3.
fi
```

1. Detect companion path and ensure project root:
```bash
CODEX_COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
```

2. Build the review prompt file by rendering the **template at `${CLAUDE_PLUGIN_ROOT}/agents/changes-review-codex.md`**. The template is the single source of truth for code-review semantics — do NOT re-state the prompt inline in this skill. Substitute four placeholders:
   - `{{PLAN_PATH}}` — absolute path to the plan file
   - `{{PLAN_GOAL}}` — the 1–2 sentence Goal sentence from the plan's `## Summary`
   - `{{BASE_REF}}` — `main` (or the worktree base branch detected via `pilot worktree status --json`)
   - `{{CHANGED_FILES}}` — newline-separated paths to the files the plan said it would touch (extracted from each task's `Files:` block)

```bash
PROMPT_TEMPLATE="${CLAUDE_PLUGIN_ROOT}/agents/changes-review-codex.md"
PROMPT_FILE="/tmp/codex-changes-review-${PILOT_SESSION_ID:-default}-<plan-slug>.md"

PLAN_PATH="/absolute/path/to/docs/plans/YYYY-MM-DD-<slug>.md"
PLAN_GOAL="<one or two sentences from the plan Summary>"
BASE_REF="main"
CHANGED_FILES=$(printf -- '- %s\n' \
  path/to/changed/file-1 \
  path/to/changed/file-2)

PLAN_PATH="$PLAN_PATH" PLAN_GOAL="$PLAN_GOAL" BASE_REF="$BASE_REF" CHANGED_FILES="$CHANGED_FILES" \
PROMPT_TEMPLATE="$PROMPT_TEMPLATE" PROMPT_FILE="$PROMPT_FILE" \
uv run --no-project python -c '
import os, pathlib
text = pathlib.Path(os.environ["PROMPT_TEMPLATE"]).read_text()
for key in ("PLAN_PATH", "PLAN_GOAL", "BASE_REF", "CHANGED_FILES"):
    text = text.replace("{{" + key + "}}", os.environ[key])
pathlib.Path(os.environ["PROMPT_FILE"]).write_text(text)
'
```

3. Launch the task in background. **⛔ For `task`, the companion's `--background` flag IS supported** (unlike `review`/`adversarial-review`). Use the companion's own background mode — the launch command returns the job ID immediately on stdout. Capture the job ID for collection in Step 3.

   ```
   Bash(
     command="cd $PROJECT_ROOT && node $CODEX_COMPANION task --background --prompt-file \"$PROMPT_FILE\"",
     run_in_background=false,
     timeout=60000
   )
   ```

   The stdout looks like: `Codex Task started in the background as task-<id>. Check /codex:status task-<id> for progress.` Extract the `task-…` token and store as `JOB_ID`.

**Why `task` instead of `adversarial-review --scope working-tree`?** Two reasons: (1) consistency with `spec-plan`, where plan files are gitignored and only `task` works; (2) single source of truth — the Codex prompt lives in `pilot/agents/changes-review-codex.md` and is shared by all `/spec` and `/fix` Codex calls, instead of being embedded in skill steps. Codex still gets the diff — the template instructs it to run `git diff {{BASE_REF}}..HEAD -- {{CHANGED_FILES}}` itself via Bash.

**Do NOT wait** — proceed to Step 2 immediately. You'll be notified when the polling bash (Step 3) completes.
