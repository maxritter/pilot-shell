## Step 8: Worktree Sync & Post-Merge Verification (if worktree active)

### 8.1 Worktree Sync

1. Extract plan slug from path (strip date prefix and `.md`)

2. Check: `~/.pilot/bin/pilot worktree detect --json <plan_slug>`

3. **If no worktree:** Skip to Step 10.

4. **Save plan to project root** (only if gitignored):
   ```bash
   git -C <project_root> check-ignore -q docs/plans/<plan_filename>
   ```
   If exit 0 (ignored): `cp <worktree_plan_path> <project_root>/docs/plans/<plan_filename>`
   If exit 1 (tracked): skip — the squash merge will bring the updated plan.

5. **Show diff:** `~/.pilot/bin/pilot worktree diff --json <plan_slug>`

6. **Notify and ask:**
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Worktree Sync" "<plan_name> — approve merge" --plan-path "<plan_path>" 2>/dev/null || true
   ```
   AskUserQuestion: "Yes, squash merge" (Recommended) | "No, keep worktree" | "Discard all changes"

7. **Handle choice:**

   **Squash merge:**
   ```bash
   # ⛔ ALL THREE operations MUST be in ONE Bash call chained with &&
   # If sync fails, cleanup MUST NOT run — otherwise work is lost.
   ~/.pilot/bin/pilot worktree sync --json <plan_slug> && PROJECT_ROOT=$(~/.pilot/bin/pilot worktree cleanup --force --json <plan_slug> | jq -r '.project_root') && cd "$PROJECT_ROOT"
   ```
   ⛔ NEVER split sync, cleanup, or cd into separate Bash calls — compaction between them can cause work loss.
   ⛔ The `&&` chain ensures cleanup only runs after a successful sync.

   **Keep worktree:** Report path, user can sync later. Skip 8.2 below.
   **Discard:** `cleanup --discard` + `cd` in same bash call (no sync needed — `--discard` explicitly allows deleting unmerged work). Skip 8.2 below.

### 8.2 Post-Merge Verification (after squash merge only)

**Mandatory after successful squash merge.** The squash merge can introduce breakage from base branch divergence.

1. Run full test suite
2. Run type checker / linter
3. Build verification
4. Program launch smoke test

If any fails: fix on base branch, re-run, commit fix separately (e.g., `fix: resolve post-merge regression from spec/<slug>`).

**⛔ Do NOT proceed to Step 10 until all post-merge checks pass.**
