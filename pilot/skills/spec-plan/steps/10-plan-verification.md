## Step 10: Plan Verification

### 10.0: No-Placeholders Self-Check (always — before launching reviewers)

⛔ Walk the plan file once, fresh-eyed, and grep for the patterns below. **Every match is a plan failure** — fix inline before sending the plan to a reviewer or asking for approval.

**Forbidden placeholder patterns:**

- `TBD`, `TODO`, `FIXME`, "implement later", "fill in details", "details below"
- "add appropriate error handling", "add validation", "handle edge cases" — without specifying which cases
- "write tests for the above" — tasks must specify the actual test cases, not a meta-instruction
- "similar to Task N" — implementers may read tasks out of order; repeat the relevant content
- Steps that describe *what* to do without showing *how* (code blocks required for code steps)
- References to types, functions, methods, files, or env vars not defined in any task
- Bracketed angle-brackets like `<your-code-here>`, `<insert-X>` outside of header literal placeholders
- Goal Verification truths that are not falsifiable ("works correctly", "is fast enough")

```bash
# Quick grep (run in worktree or repo root):
grep -nEi "TBD|TODO|FIXME|implement later|fill in details|appropriate error handling|similar to Task" "<plan_path>"
```

If anything matches, fix it inline (no new round-trip needed). Then proceed to spec-review launch below.

---

**⛔ If `PILOT_SPEC_REVIEW_ENABLED` is `"false"` (from Step 0),** skip the Claude reviewer launch below and proceed straight to the Codex section.

**⛔ Auto-skip the Claude reviewer for small plans.** If the plan has **task count ≤ 2** AND it does NOT touch security, authentication, data integrity, or destructive operations, skip the Claude reviewer launch — reviewer overhead exceeds value for a change the implementer can audit by inspection. Continue to the Codex section below; Codex still runs **only** when the user has explicitly opted in via `PILOT_CODEX_SPEC_REVIEW_ENABLED`.

For 3+ task plans, OR any plan touching sensitive surfaces regardless of task count, run the Claude reviewer below in full.

**When running:** Run spec-review for every applicable feature spec. Missing edge cases and unclear DoD criteria are size-independent once the plan crosses the size gate.

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

**⛔ NEVER use `TaskOutput`** to retrieve results — it dumps the full agent transcript into context, wasting thousands of tokens.

#### Codex Adversarial Review (Optional — launch immediately after Claude reviewer)

**If `PILOT_CODEX_SPEC_REVIEW_ENABLED` is `"true"` (from Step 0):**

Launch Codex review NOW — it runs in parallel with the Claude reviewer above.

**⛔ Codex-once rule.** Codex runs at most once per `/spec` invocation. Before launching, check the sentinel file. If it exists, the review already ran in this session — skip the launch and the collection sub-step below. Plan iterations (annotation feedback, plan edits, fixing prior findings) do NOT trigger another Codex run.

```bash
SESS_ID="${PILOT_SESSION_ID:-default}"
CODEX_FLAG="$HOME/.pilot/sessions/$SESS_ID/codex-spec-review-ran-<plan-slug>.flag"
if [ -f "$CODEX_FLAG" ]; then
  echo "Codex already reviewed this plan in this session — skipping (codex-once)."
  # Skip the launch and the Codex collection sub-step. Continue with Claude reviewer results only.
fi
```

**⛔ DO NOT use `adversarial-review --base` or `adversarial-review --scope branch` for plans.** Those subcommands bundle a git diff and feed it to Codex as the review target. Plan files in `pilot-shell` are gitignored (see `.gitignore` line ~271 — `docs/plans` is excluded), so the bundled diff is empty, and Codex returns a meta-finding ("no implementation diff was provided") with zero substantive findings on the actual plan content. Use the `task` subcommand with `--prompt-file` instead — it lets Codex Read the plan file directly via its own tools, with no diff dependency. (The `adversarial-review` path remains correct for `spec-verify`, where there is real working-tree code to scan.)

1. Detect companion path and project root:
```bash
CODEX_COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
```

2. Build the review prompt file by rendering the **template at `${CLAUDE_PLUGIN_ROOT}/agents/spec-review-codex.md`**. The template is the single source of truth for plan-review semantics — do NOT re-state the prompt inline in this skill. Substitute three placeholders:
   - `{{PLAN_PATH}}` — absolute path to the plan file
   - `{{PLAN_GOAL}}` — the 1–2 sentence Goal sentence from the plan's `## Summary`
   - `{{CONTEXT_FILES}}` — newline-separated absolute paths to source/reference files the plan ports from or extends (use the files referenced in `## Context for Implementer`)

```bash
PROMPT_TEMPLATE="${CLAUDE_PLUGIN_ROOT}/agents/spec-review-codex.md"
PROMPT_FILE="/tmp/codex-spec-review-${PILOT_SESSION_ID:-default}-<plan-slug>.md"

# Set these before rendering:
PLAN_PATH="/absolute/path/to/docs/plans/YYYY-MM-DD-<slug>.md"
PLAN_GOAL="<one or two sentences from the plan Summary>"
# CONTEXT_FILES is a newline-separated list — use printf to build it:
CONTEXT_FILES=$(printf -- '- %s\n' \
  /absolute/path/to/source-or-pattern-file-1 \
  /absolute/path/to/source-or-pattern-file-2)

PLAN_PATH="$PLAN_PATH" PLAN_GOAL="$PLAN_GOAL" CONTEXT_FILES="$CONTEXT_FILES" \
PROMPT_TEMPLATE="$PROMPT_TEMPLATE" PROMPT_FILE="$PROMPT_FILE" \
uv run --no-project python -c '
import os, pathlib
text = pathlib.Path(os.environ["PROMPT_TEMPLATE"]).read_text()
for key in ("PLAN_PATH", "PLAN_GOAL", "CONTEXT_FILES"):
    text = text.replace("{{" + key + "}}", os.environ[key])
pathlib.Path(os.environ["PROMPT_FILE"]).write_text(text)
'
```

3. Launch the task in background. **⛔ For `task`, the companion's `--background` flag IS supported (unlike `review`/`adversarial-review` where only Claude Code's `Bash(run_in_background=true)` detaches).** Use the companion's own background mode here — the launch command returns the job ID immediately on stdout. Capture the job ID for collection.

   ```
   Bash(
     command="cd $PROJECT_ROOT && node $CODEX_COMPANION task --background --prompt-file \"$PROMPT_FILE\"",
     run_in_background=false,
     timeout=60000
   )
   ```

   The stdout looks like: `Codex Task started in the background as task-<id>. Check /codex:status task-<id> for progress.` Extract the `task-…` token and store as `JOB_ID`.

   **Verify registration before polling** — fail-fast guard against synthetic-ID launches:

   ```bash
   node "$CODEX_COMPANION" status "$JOB_ID" --json 2>/dev/null | grep -q '"status":' \
     || { echo "Codex launch did not register with broker — JOB_ID is synthetic. Skipping Codex this run."; JOB_ID=""; }
   ```

   If `$JOB_ID` is empty, skip the Codex polling section and proceed with Claude reviewer only.

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

**⛔ If the notification hasn't arrived yet:** Do NOT proceed to Step 11 or approval. Do NOT read the output file. Do NOT conclude the review failed. Wait for the `<task-notification>` with `<status>completed</status>`. If you are tempted to check the file — that is the exact mistake this rule prevents.

**⛔ "Wait" does NOT mean "end your turn."** Ending the conversation turn lets the user think the workflow is finished and triggers a stop hook that pulls you out. Do not output a closing text message ("Waiting for codex…", "Holding for completion…"), do not call `ScheduleWakeup` as a substitute for staying engaged. Stay in-turn until the `<task-notification>` arrives. While waiting, do something productive in the same turn:
- Re-read the plan file once and pre-emptively spot any gaps you would fix anyway.
- If the user has queued a related request (e.g. a second bug to bundle), investigate / draft plan text for it now so you are ready to act when Codex completes.
- Run sanity-check Bash one-liners that don't fork long-running processes (path checks, file existence, small `git log` queries).
- As an absolute last resort with no other useful work, call `AskUserQuestion` to ask a short clarifying question — `AskUserQuestion` is the only tool whitelisted for a legitimate session-pause while a background task is in flight.

The completion notification arrives automatically as a mid-turn tool-result-style event; you do not need to poll for it.

**Wait for completion via bash polling**, NOT by reading the state file directly while waiting. The polling bash returns when the job's `status` flips to `completed`/`failed`, which triggers the completion notification.

```bash
JOB_ID="<captured-task-id>"
for i in $(seq 1 150); do
  STATE=$(node "$CODEX_COMPANION" status "$JOB_ID" --json 2>/dev/null \
    | uv run --no-project python -c "import json,sys; print((json.load(sys.stdin).get('job') or {}).get('status') or '')")
  case "$STATE" in
    completed) echo "READY"; break ;;
    failed)    echo "FAILED"; break ;;
  esac
  sleep 4
done
```

Run this as `Bash(run_in_background=true, timeout=600000)`. Plan reviews typically take 1–4 minutes (no diff context to load); the 10-minute ceiling is a safety margin.

1. **When (and ONLY when) the completion notification arrives**, fetch the result via the companion's public interface:

   ```bash
   node "$CODEX_COMPANION" result "$JOB_ID" --json > /tmp/codex-task-result-$$.json
   ```

   Read `/tmp/codex-task-result-$$.json` with the `Read` tool. The relevant fields:
   - `storedJob.status` — must be `"completed"`. If not, treat as a re-launch trigger; do not silently proceed.
   - `storedJob.result.rawOutput` — a string containing Codex's response. With our prompt, this is JSON matching the schema above.
   - `storedJob.rendered` — same content rendered for display; useful as a fallback if `rawOutput` is malformed.

2. **Parse `rawOutput` as JSON.** Extract `verdict`, `summary`, `findings`, `next_steps`. If `JSON.parse` fails (Codex deviated from the schema), fall back to `storedJob.rendered` — surface the rendered text to the user as a suggestion-level finding and continue. Do NOT re-launch on a parse failure; one Codex run per `/spec` is the rule.

   Severity → action map for the parsed findings:
   - `critical` / `high` → must_fix
   - `medium` / `low` → should_fix
   - `info` → suggestion

   Fix every must_fix and should_fix inline before requesting plan approval. Codex findings frequently surface architectural gaps (chained-command bypasses, fail-open paths, encoding edge cases) that the Claude reviewer misses — treat them with at least equal weight.

3. **If `storedJob.status` is `"failed"`** (genuine launch failure, not a timeout): re-launch synchronously and wait. If the second attempt also fails, escalate to the user with the captured error — do not silently proceed.

4. **Mark Codex as ran** so re-iterations of this plan within the same session do not re-run it:
```bash
mkdir -p "$(dirname "$CODEX_FLAG")" && touch "$CODEX_FLAG"
```

5. **Cleanup:** delete the temp prompt file:
```bash
rm -f "$PROMPT_FILE"
```

**If Codex was NOT launched**, proceed after all Claude reviewer must_fix/should_fix resolved.
