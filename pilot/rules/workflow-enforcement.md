# Workflow Enforcement Rules

## Task Complexity Triage

**Default mode is quick mode (direct execution).** `/spec` is ONLY used when the user explicitly types `/spec`.

| Complexity | Action |
|------------|--------|
| **Trivial** (single file, obvious fix) | Execute directly |
| **Moderate** (2-5 files, clear scope) | Use TaskCreate/TaskUpdate to track, then execute |
| **High** (architectural, 10+ files) | **Ask user** if they want `/spec` or quick mode |

**⛔ NEVER auto-invoke `/spec` or `Skill('spec')`.** The user MUST explicitly type `/spec`. If you think it would help, ask — never invoke.

---

## ⭐ MANDATORY: Task Management

**ALWAYS use task management tools for non-trivial work.**

### When to Create Tasks

| Situation | Action |
|-----------|--------|
| User asks for 2+ things | Create a task for each |
| Work has multiple steps | Create tasks with dependencies |
| **Deferring a user request** | **TaskCreate IMMEDIATELY — never just say "noted"** |
| `/spec` implementation phase | Create tasks from plan |

### ⛔ Never "Note" Without a Task

Call `TaskCreate` immediately with the request, then continue current work. The task list is your memory.

### Session Start: Clean Up Stale Tasks

Run `TaskList`, delete irrelevant leftover tasks, then create new tasks for current request.

### ⛔ Cross-Session Task Isolation

Tasks are scoped per session via `CLAUDE_CODE_TASK_LIST_ID`. Pilot Memory is shared across sessions — task references from memory that don't appear in your `TaskList` belong to another session. **`TaskList` is the sole source of truth.**

### Session Continuations

When resuming same session (same `CLAUDE_CODE_TASK_LIST_ID`): run `TaskList` first, don't recreate existing tasks, resume first uncompleted task.

---

## Sub-Agent and Tool Usage

**Prefer direct tools (vexor, Grep, Glob, Read) over sub-agents.** Sub-agents (Task/Explore) are acceptable for complex multi-file exploration when direct tools are insufficient.

### /spec Verification Agents (MANDATORY)

The Task tool spawns verification sub-agents at two points:

| Phase | Agents (parallel, both `run_in_background=true`) | `subagent_type` |
|-------|--------------------------------------------------|-----------------|
| `spec-plan` Step 1.7 | plan-verifier + plan-challenger | `pilot:plan-verifier` + `pilot:plan-challenger` |
| `spec-verify` Step 3.0, 3.5 | spec-reviewer-compliance + spec-reviewer-quality | `pilot:spec-reviewer-compliance` + `pilot:spec-reviewer-quality` |

**Launch with TWO `Task()` calls in a SINGLE message, both with `run_in_background=true`.** Without it, they run sequentially.

**⛔ NEVER skip verification. ⛔ NEVER use `TaskOutput` to retrieve results** (dumps full transcript, wastes tokens). Agents write findings to JSON files — poll with Read tool, `sleep 10` between attempts.

**Sub-agents do NOT inherit rules.** Verifier agents have key rules embedded and can read from `~/.claude/rules/*.md` and `.claude/rules/*.md`.

### Background Bash

Use `run_in_background=true` only for long-running processes (dev servers, watchers). Prefer synchronous for tests, linting, git, installs.

### No Built-in Plan Mode

**NEVER use `EnterPlanMode` or `ExitPlanMode`.** Use `/spec` instead.

---

## Deviation Handling During Implementation

| Type | Trigger | Action | User Input? |
|------|---------|--------|-------------|
| **Bug / Missing Critical / Blocking** | Code errors, missing validation, broken imports | Auto-fix inline, document as deviation | No |
| **Architectural** | Structural change (new DB table, switching libraries, breaking API) | **STOP** — `AskUserQuestion` with options | **Yes** |

Auto-fix rules: fix inline, add/update tests if applicable, do NOT expand scope. For architectural: stop, present options, wait for decision.

---

## Plan Registration (MANDATORY for /spec)

```bash
~/.pilot/bin/pilot register-plan "<plan_path>" "<status>" 2>/dev/null || true
```

Call after creating plan header, reading existing plan, and after status changes (PENDING → COMPLETE → VERIFIED).

---

## /spec Workflow

**⛔ When `/spec` is invoked, the structured workflow is MANDATORY.** Everything after `/spec` is the task description.

```
/spec → Dispatcher
          ├→ Skill('spec-plan')      → Plan, verify, approve
          ├→ Skill('spec-implement') → TDD loop for each task
          └→ Skill('spec-verify')    → Tests, execution, code review
```

### Phase Dispatch

| Status | Approved | Skill Invoked |
|--------|----------|---------------|
| PENDING | No | `Skill(skill='spec-plan', args='<plan-path>')` |
| PENDING | Yes | `Skill(skill='spec-implement', args='<plan-path>')` |
| COMPLETE | * | `Skill(skill='spec-verify', args='<plan-path>')` |
| VERIFIED | * | Report completion, done |

### Feedback Loop

```
spec-verify finds issues → Status: PENDING → spec-implement fixes → COMPLETE → spec-verify → ... → VERIFIED
```

### ⛔ Only THREE User Interaction Points

1. **Worktree Choice** (new plans only, in dispatcher)
2. **Plan Approval** (in spec-plan)
3. **Worktree Sync Approval** (in spec-verify, only when `Worktree: Yes`)

Everything else is automatic. **NEVER ask "Should I fix these findings?"** — verification fixes are part of the approved plan.

**Status values:** `PENDING` (awaiting implementation), `COMPLETE` (ready for verification), `VERIFIED` (done)

### Worktree Isolation (Optional)

Controlled by `Worktree:` field in plan header (default: `No`). User chooses at START of `/spec`.

**When `Worktree: Yes`:** Worktree created at `.worktrees/spec-<slug>-<hash>/`, all implementation there, squash merged after verification.

**When `Worktree: No`:** Direct implementation on current branch.

**Worktree CLI:** `pilot worktree detect|create|diff|sync|cleanup|status --json <slug>` (see `cli-tools.md`)

---

## Task Completion Tracking

Update plan file after EACH task: `[ ]` → `[x]`, increment Done, decrement Left. Do this immediately.

## No Stopping — Automatic Continuation

The ONLY user interaction points are worktree choice, plan approval, and worktree sync approval.
