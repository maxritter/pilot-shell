## Step 1: Setup — Read Plan, Detect Worktree, Set Up Task List

### 1.1 Read Plan & Gather Context

1. **Read the COMPLETE plan** — understand architecture and design
2. **Summarize understanding** — demonstrate comprehension
3. **Check current state:** `git status --short`, `git diff --name-only`, plan progress (`[x]` vs `[ ]`)

**Research tools during implementation:** CodeGraph (`codegraph_context` to orient on each task, `codegraph_explore` for deep code understanding in one call, `codegraph_callers`/`codegraph_callees` before modifying any function, `codegraph_impact` for blast radius), Context7 (library docs), Semble `semble search` or `mcp__semble__search` (find patterns by intent), `semble find-related` (discover parallel implementations), grep-mcp (production examples).

**⛔ Before modifying any function:** Run `codegraph_callers` + `codegraph_callees` to understand the call graph. This is not optional — it catches callers you'd otherwise miss.

### 1.2 Detect or Resume Worktree (Conditional)

**Read `Worktree:` header from plan.** If `No` or missing: skip to 1.3.

**If `Worktree: Yes`:**

1. Extract plan slug: `docs/plans/2026-02-09-add-auth.md` → `add-auth`
2. Detect: `~/.pilot/bin/pilot worktree detect --json <plan_slug>`
3. **If found:** `cd` to the worktree `path`
4. **If not found:** Create as fallback:
   ```bash
   ~/.pilot/bin/pilot worktree create --json <plan_slug>
   ```
   Copy plan file into worktree if needed. `cd` to worktree path.
5. If creation fails (old git): continue without worktree.
6. Verify: `git branch --show-current` should show `spec/<plan_slug>`

All subsequent work happens inside the worktree directory.

### 1.3 Set Up Task List (MANDATORY)

1. **Check existing:** `TaskList` — if tasks exist from prior session, resume (don't recreate)
2. **If empty:** Create one task per uncompleted `[ ]` plan task:
   ```
   TaskCreate(subject="Task N: <title>", description="<objective>", activeForm="Implementing <desc>")
   ```
   Set dependencies: `TaskUpdate(taskId="...", addBlockedBy=["..."])`
3. Skip `[x]` (already completed) tasks
