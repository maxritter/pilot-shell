## Step 2: Create Plan File Header (FIRST)

1. **Parse flags** from arguments: `--worktree=yes|no` or `--new-branch` (default: `No`). Strip the flag from task description.

2. **Branch / worktree setup — only when the flag is `--new-branch` or `--worktree=yes`.** Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/spec-branch-setup.md` and follow it, using branch prefix `feat/` and `<plan_slug>` derived from the task description (the same slug as the plan filename). On the default `--worktree=no` there is nothing to do — work continues on the current branch.

3. **Generate filename:** (for both worktree and new-branch paths) `docs/plans/YYYY-MM-DD-<feature-slug>.md` — slug from first 3-4 words (lowercase, hyphens). If worktree active, use worktree path as base directory.

4. **Fetch author email** (best-effort, do not fail if unavailable):

   ```bash
   ~/.pilot/bin/pilot status --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('email',''))" 2>/dev/null
   ```

   If the command returns a non-empty email, include `Author: <email>` in the header. If empty or fails, omit the Author line entirely.

<!-- CC-ONLY -->
4b. **Detect agent:** If `$CLAUDE_CODE_ENTRYPOINT` is set, agent is `Claude Code`. Otherwise, agent is `Codex`.
<!-- /CC-ONLY -->
<!-- CODEX-START
4b. **Set agent:** Use `Codex`.
CODEX-END -->

5. **Write initial header:**

   ```markdown
   # [Feature Name] Implementation Plan

   Created: [Date]
   Author: [email if available]
   <!-- CC-ONLY -->
   Agent: [Claude Code|Codex]
   <!-- /CC-ONLY -->
   <!-- CODEX-START
   Agent: Codex
   CODEX-END -->
   Status: PENDING
   Approved: No
   Iterations: 0
   Worktree: [Yes|No]
   Type: Feature

   > Planning in progress...

   ## Summary

   **Goal:** [Task description from user]

   ---

   _Exploring codebase and gathering requirements..._
   ```

   **`Status:` is a closed set** — only `PENDING` | `COMPLETE` | `VERIFIED`, written as the bare keyword with no trailing prose or parentheticals (see `task-and-workflow.md` → *Status values*). At creation it is always `PENDING`; never invent a custom status (no `RESOLVED`/`DONE`/`CLOSED`).

6. **Register plan:** `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`

**Do this FIRST** — before any exploration or questions. Status bar shows progress immediately.
