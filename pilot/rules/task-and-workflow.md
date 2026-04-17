# Task and Workflow Rules

## Plan Mode

**`/spec` replaces CC's built-in plan mode.** When a user wants planned work, guide them to `/spec` instead of Shift+Tab plan mode. `/spec` provides planning with TDD, verification, and code review — plan mode does not.

If a user has already switched to plan mode, respect it — present proposed changes and wait for approval. But proactively suggest `/spec` as the better alternative for structured work.

---

## Task Complexity Triage

**Default mode is quick mode (direct execution).** `/spec` is ONLY used when the user explicitly types `/spec`.

| Complexity | Action |
|------------|--------|
| **Trivial** (single file, obvious fix, no active tasks) | Execute directly |
| **Any request while tasks exist** | **TaskCreate FIRST** — then execute or queue |
| **Moderate** (2-5 files, clear scope) | TaskCreate, then execute |
| **High** (architectural, 10+ files) | **Ask user** if they want `/spec` or quick mode |

**⛔ NEVER auto-invoke `/spec` or `Skill('spec')`.** The user MUST explicitly type `/spec`. If you think it would help, ask — never invoke.

---

## Task Management

**⛔ ALWAYS use task management in quick mode.** Tasks are your working memory — without them, requests get lost during context switches and compaction. The only exception is a truly trivial one-shot with no other active work.

### ⛔ Quick Mode: Task-First Rule

**Every user request gets a task.** Before writing code, researching, or responding substantively:

1. **TaskCreate** with clear subject and description
2. **TaskUpdate** → `in_progress`
3. Do the work
4. **TaskUpdate** → `completed`

Skip only when: single trivial request AND `TaskList` is empty (no active work).

### ⛔ On-Demand Interrupts — Capture Before Anything Else

**When the user sends a new request while you're working:**

1. **STOP** current work immediately
2. **TaskCreate** for the new request — this is your FIRST tool call, before any research or code
3. Assess priority: new request urgent? → switch to it. Otherwise → resume current task

The task list is your memory — if it's not in the task list, it will be forgotten. Never rely on "I'll get to it after this" without a task.

### When to Create Tasks

| Situation | Action |
|-----------|--------|
| **Any user request** (quick mode default) | **TaskCreate FIRST** |
| User asks for 2+ things | Create a task for each |
| Work has multiple steps | Create tasks with dependencies |
| **Deferring a user request** | **TaskCreate IMMEDIATELY — never just say "noted"** |
| **User sends new request mid-task** | **TaskCreate for the new request BEFORE continuing current work** |
| `/spec` implementation phase | Create tasks from plan |

### Session Start: Clean Up Stale Tasks

Run `TaskList`, delete irrelevant leftover tasks, then create new tasks for current request.

### ⛔ Cross-Session Task Isolation

Tasks are scoped per session via `CLAUDE_CODE_TASK_LIST_ID`. Pilot Memory is shared across sessions — task references from memory that don't appear in your `TaskList` belong to another session. **`TaskList` is the sole source of truth.**

### Session Continuations

When resuming same session (same `CLAUDE_CODE_TASK_LIST_ID`): run `TaskList` first, don't recreate existing tasks, resume first uncompleted task.

---

## Tool Usage

### ⛔ Tool Parameter Names

Use EXACT parameter names — abbreviated names cause `InputValidationError`:

| Tool | Correct | Wrong (causes error) |
|------|---------|---------------------|
| `Bash` | `command` | `cmd`, `bash_command`, `shell` |
| `Write`/`Edit`/`Read` | `file_path` | `path`, `filepath`, `file` |
| `Write` | `content` | `contents`, `text`, `body` |
| `Edit` | `old_string`, `new_string` | `old`, `new`, `search`, `replace` |
| `Grep` | `pattern` | `query`, `search`, `regex` |

### ⛔ Agent Tool — NEVER Use Explore, Plan, or Research Agents

**NEVER call Agent with `subagent_type` "Explore" or "Plan".** These are prohibited — not as a suggestion, but as a hard rule. Use direct tools instead.

**Description-based blocking (ANY `subagent_type`, including `general-purpose`):**
- Description starting with "Research" → **BLOCKED**
- Description containing "Explore" (anywhere) → **BLOCKED**

The hook enforces BOTH `subagent_type` and description patterns. Using `general-purpose` with an "Explore codebase" description is the same violation as using `subagent_type="Explore"`.

**Use direct tools instead:**
- **Orient:** `codegraph_context(task="...")` — ALWAYS start here for any new task
- **Deep dive:** `codegraph_search` → `codegraph_explore(query="SymbolA SymbolB")` — full source code in one call
- **Trace:** `codegraph_callers`/`codegraph_callees` (call graphs), `codegraph_impact` (blast radius), `codegraph_files` (file tree)
- **Intent search:** Probe CLI `probe search` → Grep/Glob (exact text only, last resort)
- See `development-practices.md` for mandatory checkpoints.

**Exceptions (pass through silently regardless of description):** `web-search-agent`, `pilot:web-search-agent`, `pilot:changes-review`, `pilot:spec-review`. These are in `SILENT_AGENT_TYPES` and bypass all description checks.

### ⛔ Web Search/Fetch

**NEVER use built-in `WebFetch` or `WebSearch` — blocked by hook.** Use MCP alternatives via `ToolSearch`:

| Need | ToolSearch query |
|------|-----------------|
| Web search | `+web-search search` |
| GitHub README | `+web-search fetch` |
| Fetch page | `+web-fetch fetch` |

### Spec Workflow Toggles

Three toggles in **Console Settings → Spec Workflow** control user interaction points. When all three are disabled, `/spec` runs end-to-end without any user interaction.

| Toggle | Env Var | Default | When Disabled |
|--------|---------|---------|---------------|
| Worktree Support | `$PILOT_WORKTREE_ENABLED` | `false` | `/spec` never asks about worktree; always passes `--worktree=no` |
| Ask Questions During Planning | `$PILOT_PLAN_QUESTIONS_ENABLED` | `true` | `spec-plan` and `spec-bugfix-plan` skip all `AskUserQuestion` calls; make autonomous default choices |
| Plan Approval | `$PILOT_PLAN_APPROVAL_ENABLED` | `true` | Plan is auto-approved (`Approved: Yes`); implementation starts immediately |

These env vars are set by the Pilot wrapper from `~/.pilot/config.json → specWorkflow`. When unset (non-Pilot invocations), all three default to enabled.

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
                   → Feature: Skill('spec-verify')        → Tests, code review, structured E2E scenarios (TS-NNN)
                   → Bugfix:  Skill('spec-bugfix-verify') → Tests, quality checks, verification scenario
```

### ⛔ Dispatcher Integrity

**The `/spec` dispatcher is a thin router.** Only permitted tool calls: `Bash` (env var reads only), `Read` (plan files only), `AskUserQuestion`, and `Skill()`.

**Any other tool use (Grep, Glob, Task, Edit, Write, etc.) is a workflow violation.** If the dispatcher does substantive work, no plan file is created and the spec workflow silently disappears.

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

**`spec-implement` works identically for both plan types** — the plan file is the interface. **Verification dispatches by type:** features → `spec-verify` (1 review agent + optional Codex adversarial review, automated checks, structured E2E via TS-NNN scenarios from the plan), bugfixes → `spec-bugfix-verify` (tests, quality checks, verification scenario — no sub-agents). Codex reviewers are opt-in via Console Settings and run in parallel with Claude reviewers when enabled.

### Feedback Loop

```
spec-verify (or spec-bugfix-verify) finds issues → Status: PENDING → spec-implement fixes → COMPLETE → verify → ... → VERIFIED
```

### ⛔ Only FOUR User Interaction Points

1. **Worktree Choice + Type Confirmation** (new plans only, in dispatcher — type only asked when ambiguous; worktree skipped when `$PILOT_WORKTREE_ENABLED=false`; Codex controlled entirely by Console Settings)
2. **Plan Approval** (in spec-plan or spec-bugfix-plan; skipped when `$PILOT_PLAN_APPROVAL_ENABLED=false`)
3. **Worktree Sync Approval** (in spec-verify/spec-bugfix-verify, only when `Worktree: Yes`)
4. **Code Review Gate** (in spec-verify Step 18 / spec-bugfix-verify Step 10 — uses `AskUserQuestion` so the stop guard allows session exit while waiting)

Everything else is automatic. **NEVER ask "Should I fix these findings?"** — verification fixes are part of the approved plan.

**Zero-interaction mode:** When `$PILOT_WORKTREE_ENABLED=false`, `$PILOT_PLAN_QUESTIONS_ENABLED=false`, and `$PILOT_PLAN_APPROVAL_ENABLED=false`, `/spec` runs completely autonomously from invocation to verified completion (Code Review Gate remains active as the final quality gate). Configure via Console Settings → Spec Workflow.

**Stop Guard:** When the stop guard blocks a stop during `/spec`, do NOT acknowledge it, output resume instructions, or say goodbye. Your **very next action** must be a tool call (TaskList, Read plan file, or code change). Never produce a text-only response after a stop block — immediately resume the current task or invoke the next phase. This also applies after user interruptions ("Continue", new messages mid-task) — re-read the plan and resume from where you left off.

**Status values:** `PENDING` (awaiting implementation), `COMPLETE` (ready for verification), `VERIFIED` (done)

### Worktree Isolation (Optional)

Controlled by `Worktree:` field in plan header (default: `No`). User chooses at START of `/spec`.

**When `Worktree: Yes`:** Worktree created during planning phase at `.worktrees/spec-<slug>-<hash>/`. All implementation happens there, squash merged after verification.

**When `Worktree: No`:** Direct implementation on current branch.

---

## Task Completion Tracking

Update plan file after EACH task: `[ ]` → `[x]`, increment Done, decrement Left. Do this immediately.
