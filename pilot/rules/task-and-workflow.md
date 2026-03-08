# Task and Workflow Rules

## Plan Mode

**`/spec` replaces CC's built-in plan mode.** When a user wants planned work, guide them to `/spec` instead of Shift+Tab plan mode. `/spec` provides planning with TDD, verification, and code review — plan mode does not.

If a user has already switched to plan mode, respect it — present proposed changes and wait for approval. But proactively suggest `/spec` as the better alternative for structured work.

---

## Task Complexity Triage

**Default mode is quick mode (direct execution).** `/spec` is ONLY used when the user explicitly types `/spec`.

| Complexity | Action |
|------------|--------|
| **Trivial** (single file, obvious fix) | Execute directly |
| **Moderate** (2-5 files, clear scope) | Use TaskCreate/TaskUpdate to track, then execute |
| **High** (architectural, 10+ files) | **Ask user** if they want `/spec` or quick mode |

**⛔ NEVER auto-invoke `/spec` or `Skill('spec')`.** The user MUST explicitly type `/spec`. If you think it would help, ask — never invoke.

---

## Task Management

**ALWAYS use task management tools for non-trivial work.**

### When to Create Tasks

| Situation | Action |
|-----------|--------|
| User asks for 2+ things | Create a task for each |
| Work has multiple steps | Create tasks with dependencies |
| **Deferring a user request** | **TaskCreate IMMEDIATELY — never just say "noted"** |
| **User sends new request mid-task** | **TaskCreate for the new request BEFORE continuing current work** |
| `/spec` implementation phase | Create tasks from plan |

### ⛔ Never Drop a User Request

**The #1 failure mode is losing user requests during context-switches.** When the user sends a new request while you're working on something else:

1. **STOP** current work momentarily
2. **TaskCreate** for the new request with full details
3. **Resume** current work

The task list is your memory — if it's not in the task list, it will be forgotten. Never rely on "I'll get to it after this" without a task.

### Session Start: Clean Up Stale Tasks

Run `TaskList`, delete irrelevant leftover tasks, then create new tasks for current request.

### ⛔ Cross-Session Task Isolation

Tasks are scoped per session via `CLAUDE_CODE_TASK_LIST_ID`. Pilot Memory is shared across sessions — task references from memory that don't appear in your `TaskList` belong to another session. **`TaskList` is the sole source of truth.**

### Session Continuations

When resuming same session (same `CLAUDE_CODE_TASK_LIST_ID`): run `TaskList` first, don't recreate existing tasks, resume first uncompleted task.

---

## Sub-Agent and Tool Usage

**Search:** See `research-tools.md` for the priority chain (Probe → Grep/Glob → Explore). Task agents are for multi-step *reasoning*, not search.

### /spec Verification Agents

| Phase | Agent (background) | `subagent_type` |
|-------|-------------------|-----------------|
| `spec-plan` 1.7 (all features) | plan-reviewer | `pilot:plan-reviewer` |
| `spec-verify` 3.1, 3.4 (features only) | spec-reviewer | `pilot:spec-reviewer` |

**Plan-reviewer is mandatory** for all feature specs. Spec-reviewer is mandatory during verification.
**Bugfixes skip sub-agents** in both planning and verification — the regression test proves the fix, the full suite proves preservation.

**Rules:**
- Launch with `run_in_background=true`
- ⛔ NEVER use `TaskOutput` (wastes tokens) — agents write to JSON files, poll with bash file-existence loop then Read once
- Sub-agents do NOT inherit rules but can read from `~/.claude/rules/*.md` and `.claude/rules/*.md`

### Background Bash

Use `run_in_background=true` only for long-running processes (dev servers, watchers). Prefer synchronous for tests, linting, git, installs.

---

## Deviation Handling During /spec Implementation

**These rules apply only during `/spec` workflows.** Outside of `/spec`, always respect the user's current mode.

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
/spec → Dispatcher → Detect type (LLM intent) → Feature: Skill('spec-plan') → Plan, verify, approve
                                                → Bugfix:  Skill('spec-bugfix-plan') → Root cause investigation, plan, approve
                   → Skill('spec-implement')   → TDD loop for each task (both types)
                   → Feature: Skill('spec-verify')        → Tests, execution, code review, 1 review agent
                   → Bugfix:  Skill('spec-bugfix-verify') → Tests, quality checks, fix confirmation
```

### ⛔ Dispatcher Integrity

**The `/spec` dispatcher is a thin router.** Only permitted tool calls: `AskUserQuestion` and `Skill()`.

**Any other tool use (Read except plan files, Bash, Grep, Glob, Task, etc.) is a workflow violation.** If the dispatcher does substantive work, no plan file is created and the spec workflow silently disappears.

### Phase Dispatch

**For new tasks (no `.md` path):** Dispatcher infers spec type from the task description using LLM judgment. Clearly a bugfix → `spec-bugfix-plan`. Clearly a feature → `spec-plan`. Ambiguous → ask user (bundled with worktree question in a single AskUserQuestion).

**For existing plans (`.md` path):** Dispatcher reads `Type:` header for PENDING+unapproved routing.

| Status | Approved | Type | Skill Invoked |
|--------|----------|------|---------------|
| PENDING | No | Feature (or absent) | `Skill(skill='spec-plan', args='<plan-path>')` |
| PENDING | No | Bugfix | `Skill(skill='spec-bugfix-plan', args='<plan-path>')` |
| PENDING | Yes | * | `Skill(skill='spec-implement', args='<plan-path>')` |
| COMPLETE | * | Feature (or absent) | `Skill(skill='spec-verify', args='<plan-path>')` |
| COMPLETE | * | Bugfix | `Skill(skill='spec-bugfix-verify', args='<plan-path>')` |
| VERIFIED | * | * | Report completion, done |

**`spec-implement` works identically for both plan types** — the plan file is the interface. **Verification dispatches by type:** features → `spec-verify` (1 review agent, automated checks, runtime profile-based E2E), bugfixes → `spec-bugfix-verify` (tests, quality checks, fix confirmation — no sub-agents).

### Feedback Loop

```
spec-verify (or spec-bugfix-verify) finds issues → Status: PENDING → spec-implement fixes → COMPLETE → verify → ... → VERIFIED
```

### ⛔ Only THREE User Interaction Points

1. **Worktree Choice + Type Confirmation** (new plans only, in dispatcher — type only asked when ambiguous)
2. **Plan Approval** (in spec-plan or spec-bugfix-plan)
3. **Worktree Sync Approval** (in spec-verify/spec-bugfix-verify, only when `Worktree: Yes`)

Everything else is automatic. **NEVER ask "Should I fix these findings?"** — verification fixes are part of the approved plan.

**Stop Guard:** When the stop guard blocks a stop during `/spec`, do NOT acknowledge it, output resume instructions, or say goodbye. Your **very next action** must be a tool call (TaskList, Read plan file, or code change). Never produce a text-only response after a stop block — immediately resume the current task or invoke the next phase. This also applies after user interruptions ("Continue", new messages mid-task) — re-read the plan and resume from where you left off.

**Status values:** `PENDING` (awaiting implementation), `COMPLETE` (ready for verification), `VERIFIED` (done)

### Worktree Isolation (Optional)

Controlled by `Worktree:` field in plan header (default: `No`). User chooses at START of `/spec`.

**When `Worktree: Yes`:** Worktree created during planning phase at `.worktrees/spec-<slug>-<hash>/`. All implementation happens there, squash merged after verification.

**When `Worktree: No`:** Direct implementation on current branch.

---

## Task Completion Tracking

Update plan file after EACH task: `[ ]` → `[x]`, increment Done, decrement Left. Do this immediately.
