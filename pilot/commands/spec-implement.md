---
description: "Spec implementation phase - TDD loop for each task in the plan"
argument-hint: "<path/to/plan.md>"
user-invocable: false
model: sonnet
---

# /spec-implement - Implementation Phase

**Phase 2 of the /spec workflow.** Reads approved plan, implements each task using TDD (Red → Green → Refactor).

**Input:** Approved plan file (`Approved: Yes`)
**Output:** All tasks completed, status → COMPLETE
**Next:** Verify phase (type-aware: `spec-verify` for features, `spec-bugfix-verify` for bugfixes)

---

## ⛔ Critical Constraints

- **NO sub-agents** — all tasks execute sequentially in main context
- **TDD is MANDATORY** — no production code without failing test first
- **NEVER SKIP TASKS** — every task must be fully implemented, no "MVP scope" exceptions
- **Quality over speed** — never rush due to context pressure. Context warnings are informational. Finish current task with full quality — auto-compaction handles the rest.
- **Plan file is source of truth** — re-read after auto-compaction, don't rely on conversation memory
- **NEVER stop during implementation** — the stop guard blocks premature exits. If blocked: your very next action must be a tool call (TaskList, Read plan, or code change). After user interruptions or "Continue" messages: re-read the plan and resume from the current task. Never produce text-only responses when work remains.

---

## Feedback Loop Awareness

This phase may be called multiple times:
```
spec-implement → spec-verify → issues found → spec-implement → ...
```
When called after verification: read plan, check `Iterations` field, report "Starting Iteration N...", focus on uncompleted `[ ]` tasks (look for `[MISSING]` markers from verification).

---

### Step 2.1: Read Plan & Gather Context

1. **Read the COMPLETE plan** — understand architecture and design
2. **Summarize understanding** — demonstrate comprehension
3. **Check current state:** `git status --short`, `git diff --name-only`, plan progress (`[x]` vs `[ ]`)

**Research tools during implementation:** Context7 (library docs), Vexor (find patterns), grep-mcp (production examples).

---

### Step 2.1b: Detect or Resume Worktree (Conditional)

**Read `Worktree:` header from plan.** If `No` or missing: skip to Step 2.2.

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

---

### Step 2.2: Set Up Task List (MANDATORY)

1. **Check existing:** `TaskList` — if tasks exist from prior session, resume (don't recreate)
2. **If empty:** Create one task per uncompleted `[ ]` plan task:
   ```
   TaskCreate(subject="Task N: <title>", description="<objective>", activeForm="Implementing <desc>")
   ```
   Set dependencies: `TaskUpdate(taskId="...", addBlockedBy=["..."])`
3. Skip `[x]` (already completed) tasks

---

### Step 2.3: TDD Loop

**For EVERY task:**

1. **Read plan's implementation steps** — list files to create/modify/delete
2. **Call chain analysis:** Trace callers (upwards), callees (downwards), side effects
3. **Mark in_progress:** `TaskUpdate(taskId, status="in_progress")`
4. **TDD Flow:**
   - **RED:** Write failing test → verify it fails (feature missing, not syntax error)
   - **GREEN:** Implement minimal code to pass
   - **REFACTOR:** Improve while keeping tests green
   - Skip TDD for: docs, config, IaC, formatting-only changes
5. **Verify tests pass** — run test suite
6. **Run actual program** — use plan's Runtime Environment. Check port: `lsof -i :<port>`. If using playwright-cli: `-s="${PILOT_SESSION_ID:-default}"`
7. **Check diagnostics** — zero errors
8. **Validate Definition of Done** — all criteria from plan
9. **Self-review:** Completeness? Names clear? YAGNI? Tests verify behavior not implementation?
10. **Per-task commit (worktree only):** `git add <files> && git commit -m "{type}(spec): {task-name}"`
11. **Mark completed:** `TaskUpdate(taskId, status="completed")`
12. **Update plan file immediately** (Step 2.4)

---

### Step 2.4: Update Plan After EACH Task

**⛔ NON-NEGOTIABLE.** After each task:
1. Change `[ ]` → `[x]` for that task
2. Update Completed/Remaining counts
3. Do NOT proceed to next task until checkbox updated

---

### Step 2.5: All Tasks Complete → Verification

1. Check diagnostics + run test suite
2. **For migrations:** Feature parity check against old code. If features missing: add tasks, do NOT mark complete.
3. Set `Status: COMPLETE` in plan
4. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "COMPLETE" 2>/dev/null || true`
5. Read `Type:` field → Bugfix: `Skill(skill='spec-bugfix-verify', args='<plan-path>')` | Otherwise: `Skill(skill='spec-verify', args='<plan-path>')`

---

## Migration/Refactoring Additions

**Before starting:** Locate Feature Inventory in plan. If missing: STOP. Verify all features mapped.

**During each migration task:** Read old files, create checklist of functions/behaviors, verify each exists in new code, test with same inputs.

**Red flags (STOP):** Feature Inventory missing, old functions not in any task, "Out of Scope" items that should be migrated, tests pass but functionality missing vs old code.

ARGUMENTS: $ARGUMENTS
