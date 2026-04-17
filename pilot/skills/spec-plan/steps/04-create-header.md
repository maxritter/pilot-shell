---

## Step 4: Create Plan File Header (FIRST)

1. **Parse flags** from arguments: `--worktree=yes|no` or `--new-branch` (default: `Yes`). Strip the flag from task description.

2a. **Create new branch (if `--new-branch`):**

   **Step 1 — Stash any uncommitted work** (prevents checkout conflicts):
   ```bash
   STASH_MSG="pilot-spec-$(date +%s)"
   git stash push -m "$STASH_MSG" --include-untracked 2>/dev/null
   STASHED=$?  # 0 = stashed something, 1 = nothing to stash
   ```

   **Step 2 — Detect default branch** (local-only, no network dependency):
   ```bash
   git fetch origin 2>/dev/null
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
   DEFAULT_BRANCH=${DEFAULT_BRANCH:-main}
   ```

   **Step 3 — Create and checkout the branch** (handle name collisions):
   ```bash
   BRANCH_NAME="feat/<plan_slug>"
   # If branch already exists, append short timestamp
   if git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1; then
     BRANCH_NAME="feat/<plan_slug>-$(date +%m%d-%H%M)"
   fi
   git checkout -b "$BRANCH_NAME" "origin/$DEFAULT_BRANCH"
   ```

   **Step 4 — Restore stash on failure:**
   ```bash
   # If checkout failed and we stashed, restore the stash
   if [ $? -ne 0 ] && [ "$STASHED" -eq 0 ]; then
     git stash pop 2>/dev/null
   fi
   ```

   `<plan_slug>` is derived from the task description (same slug used for the plan filename). If checkout fails even after stashing (e.g. no origin remote), warn the user and fall back to current branch — the stash is restored automatically. After branch creation, continue with `Worktree: No` semantics (work directly on the new branch). Note: the stash remains in `git stash list` and can be recovered with `git stash pop` if needed.

2b. **Create worktree early (if `--worktree=yes`):**

   ```bash
   ~/.pilot/bin/pilot worktree detect --json <plan_slug>
   # If not found:
   ~/.pilot/bin/pilot worktree create --json <plan_slug>
   # Returns: {"path": "...", "branch": "spec/<slug>", "base_branch": "main"}
   ```

   All file writes use the worktree path as base. If creation fails (old git): continue without worktree, set to `No`.

3. **Generate filename:** (for both worktree and new-branch paths) `docs/plans/YYYY-MM-DD-<feature-slug>.md` — slug from first 3-4 words (lowercase, hyphens). If worktree active, use worktree path as base directory.

4. **Fetch author email** (best-effort, do not fail if unavailable):

   ```bash
   ~/.pilot/bin/pilot status --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('email',''))" 2>/dev/null
   ```

   If the command returns a non-empty email, include `Author: <email>` in the header. If empty or fails, omit the Author line entirely.

5. **Write initial header:**

   ```markdown
   # [Feature Name] Implementation Plan

   Created: [Date]
   Author: [email if available]
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

6. **Register plan:** `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`

**Do this FIRST** — before any exploration or questions. Status bar shows progress immediately.