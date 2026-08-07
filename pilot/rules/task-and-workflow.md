# Task & Workflow

## The two structured workflows are peers

Pilot has **two** ways to run substantial work, and neither is the escalation path for the other:

| What the work is measured against | Command |
|---|---|
| A defect in behaviour that already worked | `/fix` |
| An ordered list of tasks, approved before any code | `/spec` |
| A clear goal — "make this, and make it good", approach found while building | `/build` |
| Nothing yet; it is still vague who it serves or what done means | `/prd`, then one of the above |

**Size does not decide.** A 30-screen migration can be `/build`; a 40-line change can be `/build`; a modest feature with an unclear execution order can be `/spec`. Ask what the work is *measured against*: an approved task list, or a defined end state.

⛔ **Never route to `/spec` by reflex because the work is large.** `/build` escalates internally (parallel surfaces) and has no size ceiling. Recommending `/spec` for scale alone is the single most common routing error.

Both write a file under `docs/plans/` (`Type: Feature|Bugfix` vs `Type: Build`), register it with `pilot register-plan`, drive the statusline, appear in the Console, and are held open by the same stop guard. Both count **tasks** as the unit of progress; `/build` adds a small set of acceptance criteria that a judge rules at the end of each round, and counts rounds where `/spec` counts iterations.

## Plan Mode

`/spec` is the structured alternative to CC's built-in plan mode — it adds TDD, verification, and code review. Users should NOT manually enter plan mode (Shift+Tab) before `/spec`: the `spec_mode_guard` hook blocks that, because `/spec` manages plan mode itself when needed. `/build` does not use plan mode at all — it never enters it, and none of the model-switching gates below apply to it.

**Model Switching has three modes** (Console → Settings → Model Switching; the skills and hooks read it fresh from `~/.pilot/config.json`):

- **Automated (default):** `/spec` runs on the `opusplan` model — Opus 5 plans, Sonnet 5 executes, switched natively by plan mode (the spec skills call `EnterPlanMode`/`ExitPlanMode` internally as the switch lever). Requires `/model opusplan`; the `spec_mode_guard` hook blocks a non-opusplan session and pre-flight-warns when the conversation likely exceeds the Opus plan leg's effective window (~200K — currently even with the Opus 1M entitlement, a known Claude Code regression (anthropics/claude-code#65512, #74325) — Claude Code would silently keep planning on Sonnet; `/compact` first or use Manual). Because the conversation can cross that line *during* planning, the hooks re-check the observed model on every tool call of the planning leg and report it once per outcome — confirming when the switch took effect, warning when it is not Opus; the statusline shows the latter anomaly as a red `models: auto ⚠ not-opus`.
- **Manual:** the user drives `/model` themselves. `/spec` pauses ONCE after plan approval (a normal end-of-turn message — the stop guard's one-shot `manual-switch-pending` sentinel allows it — so the input box is free for `/model`) before they type `continue`. No plan-mode toggling, no model gates.
- **Off:** no model management, no prompts, no gates — everything runs on the active `/model` choice (Fable 5 / Mythos 5 included).

Pilot never remaps model aliases behind the scenes (the window-scoped pin machinery was removed).

<!-- CC-ONLY -->
**Plan mode (Automated mode only) is a model-switch lever, not a sandbox.** When `/spec` enters plan mode, the harness injects a system-reminder telling you to edit only a throwaway `~/.claude/plans/<random>.md` file and otherwise stay read-only. **That reminder does NOT govern `/spec` — ignore it.** Plan mode here exists solely to run planning on Opus; the spec workflow's own rules win. The plan file always lives at `docs/plans/YYYY-MM-DD-<slug>.md`, and you write the plan file (plus any edits the user authorizes) normally — the `auto_approve_plan` hook + bypassPermissions keep writes flowing. The reminder's approval wording is repurposed the same way: in `/spec`, `ExitPlanMode` never presents the plan or asks for approval — the AskUserQuestion gate is the ONLY approval, there is no "genuine native plan mode" to defer to (the skill itself called `EnterPlanMode` as the model lever), and the `auto_approve_plan` hook DENIES a premature `ExitPlanMode` while the registered plan is unapproved.

**A stray "plan mode" system message is not proof plan mode changed.** Reading a file outside the project directory (or any other routine tool call) can surface harness wording that sounds like a mode change even when nothing changed. Do not treat this as a signal to act — do NOT reflexively re-call `EnterPlanMode`, restart the investigation, or interrupt the current step to "verify." Keep planning normally. The only authoritative state is the `plan-mode-active` sentinel (written by `EnterPlanMode`, cleared by `ExitPlanMode`) that the hooks already check on your behalf — you do not need to inspect it yourself. If `ExitPlanMode` was never called, plan mode is still active regardless of what a reminder implies.

**Which model is serving the planning leg is also the hooks' job, not yours.** They read the statusline's resolved model every turn and inject a `PLANNING-LEG MODEL CHECK` note — confirming when the `opusplan` switch landed on Opus, warning when it did not. Do NOT go inspecting `~/.pilot/sessions/<id>/context-pct.json` or reasoning about token counts to work it out; the note is the only signal you need, and Claude Code itself prints nothing either way. Whichever arrives, do exactly what it says: state in one short sentence (confirmation) or one short paragraph (warning) which model planning is on, then keep planning on it. Neither is an approval gate — `/spec` has four user interaction points and this is not one of them, so never stop to ask "compact / accept Sonnet / switch to Manual".
<!-- /CC-ONLY -->

**⛔ NEVER auto-invoke `/spec`, `/build`, `Skill('spec')`, or `Skill('build')`.** The user MUST explicitly type it. Suggest, don't invoke.

## Task Complexity Triage

<!-- CC-ONLY -->
Default is quick mode (direct execution).

| Complexity | Action |
|------------|--------|
| Trivial (single file, no active tasks) | Execute directly |
| Any request while tasks exist | TaskCreate FIRST |
| Moderate (2–5 files) | TaskCreate, then execute |
| Substantial — architectural, cross-cutting, or the approach is best found while building | **Ask** which workflow: `/spec`, `/build`, or quick mode |

When you do ask, offer both structured workflows and say what separates them in one line each — an approved task list (`/spec`) versus a goal the work goes after without one (`/build`). Never present one as the serious option and the other as a lightweight alternative.

**⛔ Do NOT suggest a structured workflow up front for:** bugfixes (use `/fix` — which escalates to `/spec` itself when scope exceeds its quick lane, so relaying that escalation is fine), single-feature additions, refactors inside one module, CLI flag changes, config tweaks, dependency updates, test additions, or anything already scoped to a clear outcome with no standard attached. When in doubt, execute in quick mode.

**Two signals that outrank the size heuristic**, because they point at a specific workflow rather than at "this is big":

- The user names an end state, says "make it good", or wants the approach discovered while building rather than agreed first → suggest `/build`, whatever the size.
- The user wants the approach written down and approved before any code exists → suggest `/spec`, whatever the size.

## Task Management

**Use task management in quick mode.** Tasks are working memory — without them, requests get lost during compaction. Skip only for a truly trivial one-shot with empty `TaskList`.

### Quick Mode: Task-First

Every user request gets a task BEFORE any code/research/substantive response: TaskCreate → in_progress → work → completed.

### On-Demand Interrupts

When the user sends a new request mid-work: STOP, TaskCreate for the new request as your FIRST tool call, then assess priority. If it's not in the task list, it will be forgotten.

### Other Rules

- **Session start:** `TaskList` first, delete stale tasks, create new ones for current request.
- **Cross-session isolation:** Tasks are scoped per session via `CLAUDE_CODE_TASK_LIST_ID`. Memory is shared across sessions; references in memory that aren't in your `TaskList` belong elsewhere. **`TaskList` is the sole source of truth.**
- **Continuations** (same `CLAUDE_CODE_TASK_LIST_ID`): `TaskList` first, don't recreate, resume first uncompleted.
- **Deferring a request:** TaskCreate immediately — never just say "noted."
<!-- /CC-ONLY -->
<!-- CODEX-START
Default is quick mode (direct execution).

| Complexity | Action |
|------------|--------|
| Trivial (single file, no active tasks) | Execute directly |
| Any request while tasks exist | Update the current `update_plan` plan first |
| Moderate (2–5 files) | Create or refresh an `update_plan` plan, then execute |
| Substantial — architectural, cross-cutting, or the approach is best found while building | **Ask** which workflow: `$spec`, `$build`, or quick mode |

When you do ask, offer both structured workflows and say what separates them in one line each — an approved task list (`$spec`) versus a goal the work goes after without one (`$build`). Never present one as the serious option and the other as a lightweight alternative.

**⛔ Do NOT suggest a structured workflow up front for:** bugfixes (use `$fix` — which escalates to `$spec` itself when scope demands it), single-feature additions, refactors inside one module, CLI flag changes, config tweaks, dependency updates, test additions, or anything already scoped to a clear outcome with no standard attached. When in doubt, execute in quick mode.

**Two signals that outrank the size heuristic**, because they point at a specific workflow rather than at "this is big":

- The user names an end state, says "make it good", or wants the approach discovered while building rather than agreed first → suggest `$build`, whatever the size.
- The user wants the approach written down and approved before any code exists → suggest `$spec`, whatever the size.

## Task Management

**Use `update_plan` in quick mode for non-trivial work.** Plans are working memory — without them, requests get lost during compaction. Skip only for a truly trivial one-shot.

### Quick Mode: Plan-First

For every non-trivial user request, create or update a concise `update_plan` plan before substantive code/research work: in_progress → work → completed.

### On-Demand Interrupts

When the user sends a new request mid-work: update the plan as your first tool call, then assess priority. If it is not tracked in the plan, it can be forgotten.

### Other Rules

- **Session start / continuation:** inspect current state, then create or refresh the `update_plan` plan for the active request.
- **Cross-session isolation:** use the current conversation's plan as the source of truth; memory may contain other sessions and must not be treated as this session's task list.
- **Deferring a request:** add it to the plan immediately — never just say "noted."
CODEX-END -->

## Tool Usage

<!-- CODEX-START
### Tool Parameters — Use the Current Tool Schema

Codex tools may not share Claude Code's parameter names. Use the schema shown for the currently available tool. For repository edits, prefer `apply_patch`; for shell commands, use the available command-execution tool's schema exactly.
CODEX-END -->

<!-- CC-ONLY -->
### Agent Tool — fan-out subagents allowed; Plan routes to /spec

Read-only fan-out subagents are **allowed**: the built-in `Explore` agent, `general-purpose` agents, and any description containing "Explore" or "Research". Reach for them when a search means sweeping many files, directories, or naming conventions and you only need the conclusion.

#### Delegate rarely — subagents multiply cost and latency

Every subagent re-establishes context, re-explores, and reports back, and then you re-read its report. Current models reach for them far more readily than the payoff justifies, so the bar is high.

**Do delegate** for genuinely independent, sizeable tracks: unrelated modules, a wide multi-file investigation, a fan-out where each item is its own search.

**Do NOT delegate** work you could finish in a handful of tool calls, and never for review, verification, or double-checking — that belongs in your own loop. Prefer one subagent over several; don't split one modest job into parallel pieces. Brief each one precisely the first time, then commit to the result: don't redo its work or re-derive its findings. Launch parallel agents in a single message so they actually run concurrently.

**Pass `model` explicitly on every ad-hoc dispatch** — omit it and the subagent inherits the session model, often the most capable and most expensive one. Shipped reviewer agents already pin theirs in frontmatter; this is about `Explore` / `general-purpose`. Pick by turn count, not token price: the cheapest tier routinely takes 2-3× the turns on multi-step work and costs more overall, so a mid tier is the floor for anything past a single-file mechanical read.

**Still blocked:** `subagent_type` of `Plan` — use `/spec` for structured planning. Built-in `WebSearch`/`WebFetch` stay blocked too (see Web Search/Fetch below).

**Reviewer agents pass through silently:** `changes-review`, `spec-review`. Launch `changes-review` only where the `/spec` and `/fix` steps say to.
<!-- /CC-ONLY -->
<!-- CODEX-START
### Agent Tools

Do not assume Claude Code's agent tool or subagent names exist in Codex. Use only agent tools that are actually listed in the current Codex tool schema; otherwise work directly with CodeGraph, Semble, shell commands, and file reads.
CODEX-END -->

### Web Search/Fetch

<!-- CC-ONLY -->
Built-in `WebFetch` / `WebSearch` are hook-blocked. Discover the replacements via `ToolSearch(query="+web-search search")` and `ToolSearch(query="+web-fetch fetch")`; the servers and their tools are documented in `mcp-servers.md` (§web-search, §web-fetch).
<!-- /CC-ONLY -->
<!-- CODEX-START
Use the current Codex tool schema for web access. If the Pilot web MCP tools are lazy-loaded, discover them via `tool_search(query="+web-search search")` / `tool_search(query="+web-fetch fetch")`; details in `mcp-servers.md` (§web-search, §web-fetch).
CODEX-END -->

<!-- CC-ONLY -->
### Sub-agents

- Launch with `run_in_background=true`
- ⛔ NEVER use `TaskOutput` to retrieve results.
- **Pilot reviewer agents** (`spec-review`, `changes-review`) write findings JSON files — poll with a bash file-existence loop, then Read once. Other agent types do NOT write files; their only output is the final message of a foreground call. Never plan on `SendMessage` to follow up — it may not exist in the running Claude Code version. The changes review in `/spec` and `/fix` is this sub-agent, on both agents; whether it runs at all is Console Settings → Spec Workflow → Review Agents → Changes Review.
- ⛔ **`/code-review` is not model-invocable.** It carries `disable-model-invocation`, so `Skill(skill='code-review', ...)` is rejected outright. Never wire it into a workflow as an automated review step, and never treat a rejected call as "reviewed" — a deeper multi-agent pass is the user's to start by typing `/code-review`.
- ⛔ **Never pre-judge a reviewer's findings in its dispatch prompt.** If the prompt you are writing contains "do not flag", "don't treat X as a defect", "at most Minor", or "the plan chose" — stop. You are ruling on a finding before it exists, usually to spare yourself a review loop. Let the reviewer raise it and adjudicate afterwards, when you can see what it actually found.
- Sub-agents do NOT inherit rules; they can read `~/.claude/rules/*.md` and `.claude/rules/*.md`.

### Codex Companion (Reviews & Tasks)

- ⛔ NEVER delegate a Codex companion run to a subagent (`codex:codex-rescue` included) when you need its output — the subagent backgrounds the broker job, writes no findings file, and there is no recovery path (`TaskOutput` banned, `SendMessage` unavailable). The rescue agent exists for user-typed `/codex:rescue` handoffs only.
- Run the companion directly via Bash in the main conversation, exactly as the /spec and /fix steps specify:
  `CODEX_COMPANION=$(ls ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)`
- A background job is never lost while you hold its `task-…` ID: `node "$CODEX_COMPANION" status <job-id> --json` polls it, `node "$CODEX_COMPANION" result <job-id> --json` fetches the finished result. Do NOT abandon a launched job and redo the review yourself.
- If the job ID is unrecoverable (it was launched inside a subagent), re-launch once directly via Bash and continue.
- **Stage before any pre-commit diff review.** `/spec` and `/fix` review the WORKING TREE before committing, so every file the change ADDS is untracked. Before launching ANY pre-commit review (companion `task`/`review`/`adversarial-review`, or the `changes-review` sub-agent), run a real `git add` of the change's own files (the plan's `Files:` paths, or the fix + its test — never unrelated dirty files). A bare `git add -N` is NOT enough: Codex's `git status --untracked-files=all` still flags the path as untracked, producing a spurious `critical` ("deliverable depends on untracked files"), while a `git diff HEAD` reviewer silently OMITS it. Review against `git diff HEAD`; never pass a committed ref-range (`--base HEAD`, `--scope branch`, `main...HEAD`, `HEAD~1`) — pre-commit those diffs are empty and the review scans nothing. Staging is not committing; the push still waits for approval.
- **Broker `status` is not a liveness signal — watch the log mtime.** A companion job can go silent mid-`verifying` while `status` keeps reporting `running`/`verifying` with a climbing `elapsed`. A poll that waits only on `status` then burns its full timeout before noticing. Resolve `job.logFile` from `status --json` and poll its mtime alongside `job.status`: if status is still running but the log has not advanced for ≥90s (stall) or total elapsed exceeds ~8min (ceiling), the job is dead — `cancel` it, re-launch once under the same monitor, and if it stalls again proceed WITHOUT the Codex pass and record the gap (do NOT spin the full poll timeout, do NOT silently skip). The `/spec` and `/fix` skill steps carry the exact monitor — a single-process `node -e` watcher (5s poll, no per-poll `uv`/`python` spawns, no zsh/`stat` portability traps).
- **Review effort: `medium` by default, model untouched.** Companion review `task` launches pass `--effort "${PILOT_CODEX_REVIEW_EFFORT:-medium}"` (fail-closed to `medium`): a review is a bounded read-only audit, and the user's interactive default (often `xhigh`) runs ~2× slower for equivalent material findings (verified live 2026-07-13: same prompt/diff — medium 109s vs xhigh 221–223s, same finding tier). ⛔ Never pass `--model` — fast-model aliases (e.g. `spark`) 400 on ChatGPT-plan auth. Any re-launch after a stall or failure drops the `--effort` override and inherits the user's Codex default.
<!-- /CC-ONLY -->
<!-- CODEX-START
### Sub-agents

Do not assume Claude Code's sub-agent tools exist in Codex. Use only agent tools that are actually listed in the current Codex tool schema; otherwise work directly with CodeGraph, Semble, shell commands, and file reads.

When a task changes Codex skills, hooks, rules, or custom agents, verify the generated artifacts directly; the current running session may not expose newly generated agent types until the next install or SessionStart sync.

For long-running Codex subagent or companion tasks, persist returned agent/job ids to a session file before running tests or builds. Do not rely only on conversation memory across compaction.
CODEX-END -->

### Background Bash

Use `run_in_background=true` only for long-running processes (dev servers, watchers). Synchronous for tests, lint, git, installs.

---

## Workflows

```
/spec  → Feature: spec-plan        → spec-implement → spec-verify
       → Bugfix:  spec-bugfix-plan → spec-implement → spec-bugfix-verify
/build → goal → tasks + criteria → approve → round (build every task → judge) → hand back
/fix   → quick lane; stops and asks for /spec when scope exceeds it
```

The phase skills carry their own contracts — dispatch rules, toggles, plan registration, worktree handling, per-task tracking. Don't restate them here; read the skill. What follows applies whether or not a skill is loaded.

**`Status:` is a closed set** — exactly one of `PENDING` → `COMPLETE` → `VERIFIED`, written as the bare keyword with no trailing prose. Never invent another value (`RESOLVED`, `DONE`, `CLOSED`); the Console treats anything outside the set as terminal. Resolution notes belong in the plan body. This applies to `/build` Buildouts identically.

**`/spec` — four user interaction points, and no more:** branch/type confirmation (new plans), plan approval, worktree sync approval (`Worktree: Yes` only), and the final code-review gate. Everything else is automatic — **never ask "should I fix these findings?"**, since verification fixes are part of the approved plan.

**`/build` — three, and no more:** goal/reference confirmation (a reference only when one genuinely exists and the user did not name it), approval of the drafted tasks and criteria, and hand-back. A failing criterion is never an interaction point — it becomes the next round's tasks. **Never ask "should I keep going?"**; the criteria and the three-round budget answer that.

⛔ **An auto-continued question is not an answer.** An `AskUserQuestion` result reading "No response after Ns — continued without an answer" means the user has not responded. Treat it as silence at any interaction point: don't act on the recommended option, don't infer approval, re-ask when they return.

**Deviations:** auto-fix bugs, missing validation, and broken imports inline and document them. **Stop and ask** for architectural changes — a new table, a library swap, a breaking API.

<!-- CC-ONLY -->
**Stop guard:** when it blocks a stop during `/spec` or `/build`, don't acknowledge it, output resume instructions, or say goodbye. Your very next action is a tool call. Same after any user interruption — re-read the plan or Buildout and resume. In `/build` this hook *is* the loop's goal condition; there is nothing extra for the user to type.
<!-- /CC-ONLY -->
<!-- CODEX-START
**Stop guard:** when it blocks a stop during `$spec` or `$build`, don't acknowledge it, output resume instructions, or say goodbye. Your very next action is a tool call — re-read the plan or Buildout, refresh `update_plan`, or make the next change. Same after any user interruption. In `$build` this hook *is* the loop's goal condition.
CODEX-END -->
