## Step 1: Setup — Read Plan, Detect Worktree, Set Up Task List

<!-- CC-ONLY -->
### 1.0 Plan Mode Exit Guard (MANDATORY safety net)

**⛔ This is the very first action — before reading the plan or doing any other work.**

The guard is STATE-based, not mode-based: it checks whether plan mode is actually still open (the `plan-mode-active` sentinel the plan_mode_tracker hook maintains), so it works even when the Console mode changed mid-run or the config read fails.

```bash
SPEC_SESS="${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
[ -f "$HOME/.pilot/sessions/$SPEC_SESS/plan-mode-active" ] && echo "PLAN_MODE_STILL_OPEN=true" || echo "PLAN_MODE_STILL_OPEN=false"
MODE=$(python3 -c "import sys,os;sys.path.insert(0,os.path.expanduser('~/.pilot/hooks'));from _lib.util import read_model_switch_mode;print(read_model_switch_mode())" 2>/dev/null || echo "automated")
echo "MODE=$MODE"
```

**If `PLAN_MODE_STILL_OPEN=true` (any mode):** `spec-plan` should have called `ExitPlanMode` before invoking this skill; it didn't (model skip, approval edge case, mid-run mode change). Exit now — implementation must never run in plan mode:

```
ToolSearch(query="select:ExitPlanMode")   # deferred — load schema first
ExitPlanMode(...)                          # safe to call even if already exited
```

- If `ToolSearch` returns no tool: emit one visible line ("ExitPlanMode unavailable — implementation will run on current model") and continue. If `ExitPlanMode` errors with "not in plan mode", plan mode is already closed (e.g. a Shift+Tab exit) — the hook heals the stale sentinel; proceed normally.
- **Do NOT skip this step to save tokens. An extra ExitPlanMode call costs nothing; running the entire implementation leg in plan mode is expensive and wrong.**

**If `PLAN_MODE_STILL_OPEN=false` and `MODE=manual`:** when this skill was invoked directly (resume path — the 12.3/6.3 post-approval pause never ran in this session), print one line: "ℹ️ Manual model switching: implementation runs on your current /model choice (see the status bar)." Then proceed.

**Otherwise:** proceed to 1.1 — nothing to exit.
<!-- /CC-ONLY -->

### 1.1 Read Plan & Gather Context

1. **Read the COMPLETE plan** — understand architecture and design
2. **Summarize understanding** — demonstrate comprehension
3. **Check current state:** `git status --short`, `git diff --name-only`, plan progress (`[x]` vs `[ ]`)

<!-- CC-ONLY -->
**Research tools during implementation:** CodeGraph (`codegraph_explore(query=...)` — one call orients on the task, returns deep source, and gives callers + blast radius before you modify a shared or non-trivial function), Context7 (library docs), Semble `semble search` or `mcp__semble__search` (find patterns by intent), `semble find-related` (discover parallel implementations), grep-mcp (production examples).

**Before modifying a shared or non-trivial function:** run `codegraph_explore(query="<fn> callers and impact")` — its response includes the call path and blast radius, catching callers you'd otherwise miss. A self-contained local function the plan already isolated doesn't need it.
<!-- /CC-ONLY -->
<!-- CODEX-START
**Research tools during implementation:** Use CodeGraph for structural runtime-code questions (`codegraph_explore(query=...)` — one call orients, returns known-symbol source, and gives callers + blast radius before a non-local change), Context7 for library docs, Semble for intent/pattern discovery, and grep-mcp for production examples.

**Codex proportionality:** Skip CodeGraph for docs, rules, markdown, config, UI copy, test-only edits, or named-path local changes unless the call graph itself is the uncertainty. Before modifying a runtime function with non-local effects, run `codegraph_explore(query="<fn> callers")`; for a local function already isolated by the plan and targeted reads, do not add graph calls just to satisfy a checklist.
CODEX-END -->

### 1.2 Detect or Resume Worktree (Conditional)

**Read `Worktree:` header from plan.** If `No` or missing: skip to 1.3.

**If `Worktree: Yes`:**

1. Extract plan slug: `docs/plans/2026-02-09-add-auth.md` → `add-auth`
> **`$LANE_FLAG`** is `--lane <id>` when this run was dispatched as an orchestration lane, and **nothing at all** otherwise — the value the invocation parsed from its arguments. It keeps worktree and plan identity scoped to this lane; an unflagged call resolves a different identity and silently finds nothing (issue #174).

2. Detect: `~/.pilot/bin/pilot worktree detect --json <plan_slug> $LANE_FLAG`
3. **If found:** `cd` to the worktree `path`
4. **If not found:** Create as fallback:
   ```bash
   ~/.pilot/bin/pilot worktree create --json <plan_slug> $LANE_FLAG
   ```
   Copy plan file into worktree if needed. `cd` to worktree path.

   ⛔ `$LANE_FLAG` here too, not just on the `detect` above. Worktree identity is keyed on `(slug, lane)`, so an unflagged create makes a worktree that the lane-flagged `sync`/`cleanup` in the verify phase can never find — the run's work ends up stranded in an orphaned checkout that never reaches the base branch.
5. If creation fails (old git): continue without worktree — **unless this is a lane run**, which aborts instead (`spec-branch-setup.md`): a lane silently sharing the coordinator's checkout races every sibling's edits.
6. Verify: `git branch --show-current` should show `spec/<plan_slug>`

All subsequent work happens inside the worktree directory.

### 1.3 Set Up Task List (MANDATORY)

<!-- CC-ONLY -->
1. **Check existing:** `TaskList` — if tasks exist from prior session, resume (don't recreate)
2. **If empty:** Create one task per uncompleted `[ ]` plan task:
   ```
   TaskCreate(subject="Task N: <title>", description="<objective>", activeForm="Implementing <desc>")
   ```
   Set dependencies: `TaskUpdate(taskId="...", addBlockedBy=["..."])`
3. Skip `[x]` (already completed) tasks
<!-- /CC-ONLY -->
<!-- CODEX-START
1. List uncompleted `[ ]` plan tasks — these are your work items.
2. Track progress by updating plan checkboxes (`[ ]` → `[x]`) after each task.
3. Skip `[x]` (already completed) tasks.
CODEX-END -->
