---

## Step 5: Worktree Sync (if worktree active)

1. Detect: `~/.pilot/bin/pilot worktree detect --json <plan_slug>`
2. If no worktree: skip to Step 7.
3. Save plan to project root (only if gitignored):
   `git -C <project_root> check-ignore -q docs/plans/<plan_filename>` — if exit 0: `cp <worktree_plan> <project_root>/docs/plans/`; if exit 1 (tracked): skip — squash merge brings the updated plan.
5. Show diff: `~/.pilot/bin/pilot worktree diff --json <plan_slug>`
6. Notify + AskUserQuestion: "Yes, squash merge" | "No, keep" | "Discard"
7. Handle:
   - **Squash:** `worktree sync && cleanup --force + cd` — ALL in ONE Bash call chained with `&&`. Cleanup MUST NOT run if sync fails.
   - **Keep:** Report path
   - **Discard:** `cleanup --discard` + `cd` in SAME bash call (no sync needed — `--discard` explicitly allows deleting unmerged work)

   ⛔ NEVER split sync, cleanup, or cd into separate Bash calls — compaction between them can cause work loss.
