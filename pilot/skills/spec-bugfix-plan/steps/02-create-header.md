---

## Step 2: Create Plan File Header (FIRST)

1. **Parse flags** from arguments: `--worktree=yes|no` or `--new-branch` (default: `No`). Strip the flag.
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
   BRANCH_NAME="fix/<plan_slug>"
   # If branch already exists, append short timestamp
   if git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1; then
     BRANCH_NAME="fix/<plan_slug>-$(date +%m%d-%H%M)"
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

   `<plan_slug>` is derived from the bug description (same slug used for the plan filename). If checkout fails even after stashing, warn the user and fall back to current branch — the stash is restored automatically. After branch creation, continue with `Worktree: No` semantics. The stash remains in `git stash list` for manual recovery if needed.
2b. **Create worktree early (if `--worktree=yes`):** Same pattern as spec-plan Step 2.
3. **Generate filename:** `docs/plans/YYYY-MM-DD-<bug-slug>.md`
4. **Fetch author email** (best-effort): same as spec-plan Step 2 step 4. If non-empty, include `Author: <email>` in header. If empty/fails, omit.
5. **Write header:**

   ```markdown
   # [Bug Description] Fix Plan

   Created: [Date]
   Author: [email if available]
   Status: PENDING
   Approved: No
   Iterations: 0
   Worktree: [Yes|No]
   Type: Bugfix

   > Investigating bug...

   ## Summary

   **Symptom:** [Bug description from user]

   ---

   _Tracing root cause..._
   ```

6. **Register:** `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`
