## Step 8: Worktree Sync & Post-Merge Verification (if worktree active)

### 8.1 Worktree Sync

1. Extract plan slug from path (strip date prefix and `.md`)

2. Check: `~/.pilot/bin/pilot worktree detect --json <plan_slug> $LANE_FLAG`

3. **If no worktree:** Skip to Step 9 (the annotation check — it runs BEFORE the review gate regardless of worktree mode; never collapse Step 9 → Step 10).

4. **Save plan to project root** (only if gitignored):
   ```bash
   git -C <project_root> check-ignore -q docs/plans/<plan_filename>
   ```
   If exit 0 (ignored): `cp <worktree_plan_path> <project_root>/docs/plans/<plan_filename>`
   If exit 1 (tracked): skip — the squash merge will bring the updated plan.

5. **Show diff:** `~/.pilot/bin/pilot worktree diff --json <plan_slug> $LANE_FLAG`

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
   ~/.pilot/bin/pilot worktree sync --json <plan_slug> $LANE_FLAG && PROJECT_ROOT=$(~/.pilot/bin/pilot worktree cleanup --force --json <plan_slug> $LANE_FLAG | jq -r '.project_root') && cd "$PROJECT_ROOT"
   ```
   ⛔ NEVER split sync, cleanup, or cd into separate Bash calls — compaction between them can cause work loss.
   ⛔ The `&&` chain ensures cleanup only runs after a successful sync.

   **Exit codes.** `0` clean · `1` nothing landed · **`2` the squash landed but the base checkout's own uncommitted work could not be restored** and is sitting in `git stash list`. The chain stops on 2 by itself, deliberately leaving the worktree in place. Do NOT re-run cleanup to "finish the job": surface the JSON's `stash_warning` and the `git stash pop` recovery to the user first. `success: true` is still correct — the merge landed; only the unrelated local work is stranded.

   **Lane contention.** Sync serializes on a repo-wide lock, so a concurrent lane's sync waits instead of interleaving its merge into the shared base checkout. A failure naming lane contention means another lane held the lock past the timeout and **nothing was changed** — retry once it finishes.

   **Keep worktree:** Report path, user can sync later. Skip 8.2 below.
   **Discard:** `~/.pilot/bin/pilot worktree cleanup --discard --json <plan_slug> $LANE_FLAG` + `cd` in same bash call (no sync needed — `--discard` explicitly allows deleting unmerged work). Skip 8.2 below. ⛔ `$LANE_FLAG` here too: an unflagged discard resolves a different worktree identity and silently no-ops, leaving the lane's checkout behind.

### 8.2 Post-Merge Verification (after squash merge only)

**Mandatory after successful squash merge.** The squash merge can introduce breakage from base branch divergence.

1. Run full test suite
2. Run type checker / linter
3. Build verification
4. Program launch smoke test

If any fails: fix on base branch, re-run, commit fix separately (e.g., `fix: resolve post-merge regression from spec/<slug>`).

**⛔ Do NOT proceed to Step 10 until all post-merge checks pass.**
