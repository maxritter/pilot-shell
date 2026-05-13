# Task & Workflow

## Plan Mode

`/spec` replaces CC's built-in plan mode — it adds TDD, verification, and code review. Guide users to `/spec` for planned work. If they're already in plan mode, respect it.

**⛔ NEVER auto-invoke `/spec` or `Skill('spec')`.** The user MUST explicitly type it. Suggest, don't invoke.

## Task Complexity Triage

Default is quick mode (direct execution).

| Complexity | Action |
|------------|--------|
| Trivial (single file, no active tasks) | Execute directly |
| Any request while tasks exist | TaskCreate FIRST |
| Moderate (2–5 files) | TaskCreate, then execute |
| High (architectural, 10+ files) | **Ask** if user wants `/spec` or quick mode |

## Task Management

**⛔ ALWAYS use task management in quick mode.** Tasks are working memory — without them, requests get lost during compaction. Skip only for a truly trivial one-shot with empty `TaskList`.

### ⛔ Quick Mode: Task-First

Every user request gets a task BEFORE any code/research/substantive response: TaskCreate → in_progress → work → completed.

### ⛔ On-Demand Interrupts

When the user sends a new request mid-work: STOP, TaskCreate for the new request as your FIRST tool call, then assess priority. If it's not in the task list, it will be forgotten.

### Other Rules

- **Session start:** `TaskList` first, delete stale tasks, create new ones for current request.
- **Cross-session isolation:** Tasks are scoped per session via `CLAUDE_CODE_TASK_LIST_ID`. Memory is shared across sessions; references in memory that aren't in your `TaskList` belong elsewhere. **`TaskList` is the sole source of truth.**
- **Continuations** (same `CLAUDE_CODE_TASK_LIST_ID`): `TaskList` first, don't recreate, resume first uncompleted.
- **Deferring a request:** TaskCreate immediately — never just say "noted."

## Tool Usage

### ⛔ Tool Parameter Names — Use EXACT names

| Tool | Correct | Wrong |
|------|---------|-------|
| `Bash` | `command` | `cmd`, `bash_command`, `shell` |
| `Write`/`Edit`/`Read` | `file_path` | `path`, `filepath`, `file` |
| `Write` | `content` | `contents`, `text`, `body` |
| `Edit` | `old_string`, `new_string` | `old`, `new`, `search`, `replace` |
| `Grep` | `pattern` | `query`, `search`, `regex` |

### ⛔ Agent Tool — Explore / Plan / Research blocked

Hook blocks `subagent_type` of `Explore`/`Plan`, AND any description starting with "Research" or containing "Explore" (regardless of subagent_type — `general-purpose` with `"Explore codebase"` description is the same violation).

Use direct tools instead — see `development-practices.md` and `mcp-servers.md` for CodeGraph + Semble workflow.

**Whitelisted (pass through silently):** `web-search-agent`, `pilot:web-search-agent`, `pilot:changes-review`, `pilot:spec-review`.

### ⛔ Web Search/Fetch

Built-in `WebFetch` / `WebSearch` are hook-blocked. Use ToolSearch:

| Need | Query |
|------|-------|
| Web search | `+web-search search` |
| GitHub README | `+web-search fetch` |
| Fetch page | `+web-fetch fetch` |

### Sub-agents

- Launch with `run_in_background=true`
- ⛔ NEVER use `TaskOutput` — agents write JSON files; poll with bash file-existence loop, then Read once.
- Sub-agents do NOT inherit rules; they can read `~/.claude/rules/*.md` and `.claude/rules/*.md`.

### Background Bash

Use `run_in_background=true` only for long-running processes (dev servers, watchers). Synchronous for tests, lint, git, installs.

---

## /spec Workflow

```
/spec → Dispatcher → Feature: spec-plan        → spec-implement → spec-verify
                   → Bugfix:  spec-bugfix-plan → spec-implement → spec-bugfix-verify
/fix  → fix skill (always quick lane). Stops and tells user to use /spec if scope exceeds quick lane.
```

### ⛔ Dispatcher Integrity

`/spec` dispatcher is a thin router. **Only allowed tools:** `Bash` (env-var reads), `Read` (plan files), `AskUserQuestion`, `Skill()`. Any Grep/Glob/Task/Edit/Write is a workflow violation.

### Phase Dispatch

New tasks (no `.md`): infer type from description. Ambiguous → ask user (bundled with worktree question).

Existing plans (`.md`): read `Type:` header.

| Status | Approved | Type | Skill |
|--------|----------|------|-------|
| PENDING | No | Feature | `spec-plan` |
| PENDING | No | Bugfix | `spec-bugfix-plan` |
| PENDING | Yes | * | `spec-implement` |
| COMPLETE | * | Feature | `spec-verify` |
| COMPLETE | * | Bugfix | `spec-bugfix-verify` |
| VERIFIED | * | * | Done |

`spec-implement` is identical for both types (the plan file is the interface). Verification differs: features get review agent + optional Codex + structured E2E (TS-NNN); bugfixes get Behavior Contract audit + revert-test proof.

**Status values:** `PENDING` (awaiting impl) → `COMPLETE` (ready to verify) → `VERIFIED` (done).

### Feedback Loop

`spec-verify` finds issues → status flips to PENDING → `spec-implement` fixes → COMPLETE → re-verify → … → VERIFIED.

### ⛔ Only FOUR User Interaction Points

1. **Branch + Type confirmation** — new plans only (in dispatcher; type only when ambiguous; branch question skipped when `$PILOT_BRANCH_ISOLATION_ENABLED=false`).
2. **Plan Approval** — in `spec-plan`/`spec-bugfix-plan`; skipped when `$PILOT_PLAN_APPROVAL_ENABLED=false`.
3. **Worktree Sync Approval** — in verify, only when `Worktree: Yes`.
4. **Code Review Gate** — final quality gate via `AskUserQuestion`.

Everything else is automatic. **NEVER ask "Should I fix these findings?"** — verification fixes are part of the approved plan.

### Spec Workflow Toggles

`~/.pilot/config.json → specWorkflow` sets these env vars (defaults shown when run outside Pilot):

| Toggle | Env Var | Default | When disabled |
|--------|---------|---------|---------------|
| Branch Isolation | `$PILOT_BRANCH_ISOLATION_ENABLED` | `false` | Skip the dispatcher branch question entirely; always pass `--worktree=no` |
| Plan questions | `$PILOT_PLAN_QUESTIONS_ENABLED` | `true` | Skip all `AskUserQuestion` in plan phase |
| Plan approval | `$PILOT_PLAN_APPROVAL_ENABLED` | `true` | Auto-approves; implementation starts immediately |

All three disabled = end-to-end autonomous (Code Review Gate still runs).

### Plan Registration (MANDATORY for /spec)

```bash
~/.pilot/bin/pilot register-plan "<plan_path>" "<status>" 2>/dev/null || true
```

Call after creating the plan header, after reading an existing plan, and after status changes.

### Deviation Handling (during /spec)

| Type | Trigger | Action |
|------|---------|--------|
| Bug / missing critical / blocking | Errors, missing validation, broken imports | Auto-fix inline, document deviation |
| Architectural | New table, library swap, breaking API | **STOP** — `AskUserQuestion` |

Auto-fix: inline + tests if applicable, do NOT expand scope. Outside `/spec`, respect the user's mode.

### Stop Guard

When the stop guard blocks a stop during `/spec`, do NOT acknowledge it, output resume instructions, or say goodbye. Your **very next action** must be a tool call (TaskList, Read plan, code change). No text-only responses after a stop block. Same applies after user interruptions ("Continue", new mid-task messages) — re-read the plan, resume.

### Worktree

`Worktree:` field in plan header (default `No`). User chooses at start of `/spec`.

- **Yes** → worktree at `.worktrees/spec-<slug>-<hash>/`. Implementation isolated; squash-merged after verification.
- **No** → direct on current branch.

### Task Completion Tracking

Update plan after EACH task: `[ ]` → `[x]`, increment Done, decrement Left. Immediately.
