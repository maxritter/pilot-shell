# Task & Workflow

<!-- CC-ONLY -->
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

Each writes a file to its own directory — `/spec` plans to `docs/plans/` (`Type: Feature|Bugfix`), `/build` Buildouts to `docs/builds/` (`Type: Build`) — just as requirements documents get a directory of their own. The `Type:` header, not the directory, is what identifies a file, so a Buildout still in `docs/plans/` from before the split keeps working. Both register with `pilot register-plan`, drive the statusline, appear in the Console, and are held open by the same stop guard. Both count **tasks** as the unit of progress; `/build` adds a small set of acceptance criteria that a judge rules at the end of each round, and counts rounds where `/spec` counts iterations.

**⛔ NEVER auto-invoke `/spec`, `/build`, `Skill('spec')`, or `Skill('build')`.** The user MUST explicitly type it. Suggest, don't invoke.
<!-- /CC-ONLY -->
<!-- CODEX-START
## Pilot workflow skills are opt-in

`$spec`, `$build`, `$fix`, and `$prd` run only when the user explicitly invokes them. A normal request stays in direct execution even when it is large or cross-cutting. Mention these skills only when the user asks about workflows or process.
CODEX-END -->

<!-- CC-ONLY -->
## Plan Mode

`/spec` is the structured alternative to CC's built-in plan mode — it adds TDD, verification, and code review. Users should NOT manually enter plan mode (Shift+Tab) before `/spec`: the `spec_mode_guard` hook blocks that, because `/spec` manages plan mode itself when needed. `/build` never enters plan mode at all.

**Model Switching** (Automated / Manual / Off, set in Console → Settings) is `/spec`'s own business, and its whole lifecycle lives at point-of-use in the spec skills — which mode is active, the `opusplan` gates, `EnterPlanMode`/`ExitPlanMode` as the model lever, and what to do when the harness emits a plan-mode reminder. Read the step, don't reason about it from here. Two things carry outside the skill: **never try to work out which model is serving you** — the hooks read the statusline and tell you — and Pilot never remaps model aliases behind the scenes.
<!-- /CC-ONLY -->

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
Default is direct execution. A clear user request is authorization to execute it in quick mode, including investigation, implementation, verification, and affected documentation.

Size, file count, architectural breadth, and cross-cutting scope change how the work is organized; they do not trigger a workflow question. Descriptions and mentions like "make it good", "build the whole thing", or "do not stop early" likewise strengthen the requested outcome rather than selecting `$build`.

`$spec`, `$build`, `$fix`, and `$prd` are explicit opt-ins. Enter one only when the user invokes that skill by name. If the user asks which process would fit, explain the choices without starting one. Otherwise do not mention Pilot workflows and do not trigger a workflow question.

## Task Management

Use the native `/goal` state as the persistent outcome when one is active. Keep working until that goal is achieved or genuinely blocked.

Use `update_plan` as optional working memory when several dependent steps would otherwise be easy to lose. A plan is an internal coordination aid, not a user gate, and direct work may begin without one when the request is already clear.

### Quick Mode

Organize complex work into bounded steps, execute them, and keep the current state accurate. Do not pause to ask the user to choose a process merely because the work spans several surfaces.

### On-Demand Interrupts

When the user sends a new request mid-work, decide whether it replaces the active request or adds to it. If it adds work and an `update_plan` plan is in use, record it before returning to the current step.

### Other Rules

- **Session start / continuation:** inspect current state and resume the active request or native goal.
- **Cross-session isolation:** the current conversation or native goal is authoritative; memory may describe unrelated sessions.
- **Deferring a request:** record the concrete deferred work in the active plan when one exists.
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

Do not assume Claude Code's sub-agent tools exist in Codex. The current Codex tool schema is authoritative for names and parameters.

Proactively delegate bounded, independent work when agent tools are listed and parallel execution materially improves speed or quality: separate product surfaces, independent codebase questions, isolated implementation ownership, or a test run that can proceed beside other work. Use the main thread for integrated decisions and work whose files or state overlap.

Give each agent explicit ownership, success evidence, and the warning that other agents share the codebase. Launch independent agents together, keep their returned ids, wait with the mechanism exposed by the current schema, and inspect the resulting files or diff before accepting completion. Do not redo a completed agent's exploration; integrate its evidence and continue.

If no agent tools are listed, work directly with CodeGraph, Semble, shell commands, and file reads. Tool absence changes execution mechanics, not the scope of the user's request.
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

Use the agent tools actually exposed in the current Codex schema. Prefer one agent per concrete, non-overlapping responsibility; several independent responsibilities may run in parallel. Agents may further delegate when the same bounded-ownership rule holds.

When a task changes Codex skills, hooks, rules, or custom agents, verify the generated artifacts directly; the current running session may not expose newly generated agent types until the next install or SessionStart sync.

For long-running Codex subagent or companion tasks, persist returned agent/job ids to a session file before running tests or builds. Do not rely only on conversation memory across compaction.
CODEX-END -->

<!-- CC-ONLY -->
### Background Bash

Use `run_in_background=true` only for long-running processes (dev servers, watchers). Synchronous for tests, lint, git, installs.
<!-- /CC-ONLY -->
<!-- CODEX-START
### Long-running commands

Use the execution tool's current session or background-process capability for dev servers and watchers. Run tests, lint, git reads, and installs synchronously unless their observed duration makes a resumable session necessary.
CODEX-END -->

---

<!-- CC-ONLY -->
## Workflows

```
/spec  → Feature: spec-plan        → spec-implement → spec-verify
       → Bugfix:  spec-bugfix-plan → spec-implement → spec-bugfix-verify
/build → goal (grill it) → tasks + criteria → round (build every task → judge) → verify → hand back
         all questions up front; autonomous after — no approval gate, no check-ins
/fix   → quick lane; stops and asks for /spec when scope exceeds it
```

The phase skills carry their own contracts — dispatch rules, toggles, plan registration, worktree handling, per-task tracking. Don't restate them here; read the skill. What follows applies whether or not a skill is loaded.

**`Status:` is a closed set** — exactly one of `PENDING` → `COMPLETE` → `VERIFIED`, written as the bare keyword with no trailing prose. Never invent another value (`RESOLVED`, `DONE`, `CLOSED`); the Console treats anything outside the set as terminal. Resolution notes belong in the plan body. This applies to `/build` Buildouts identically.

**`/spec` — four user interaction points, and no more:** branch/type confirmation (new plans), plan approval, worktree sync approval (`Worktree: Yes` only), and the final code-review gate. Everything else is automatic — **never ask "should I fix these findings?"**, since verification fixes are part of the approved plan.

**`/build` — all of it before any work, none after:** Step 1.5 grills the goal until it can name the oracle, every intended criterion's settling evidence, and the misfire — up to three rounds on a weak goal, none at all on a sharp one. After that the run is autonomous to the hand-back: no approval of the tasks and criteria, no round-budget check-in, no sign-off before `VERIFIED`, and no merge-back question on `Worktree: Yes` (the flag already asked for the squash). A failing criterion is never an interaction point — it becomes the next round's tasks, and at the four-round ceiling a line in the report. **Never ask "should I keep going?"** `PILOT_PLAN_APPROVAL_ENABLED` is not read by `/build`; it governs `/spec`'s plan gate only.

⛔ **Autonomy is not a lower bar.** `/build` writes `VERIFIED` itself, so it is earned by evidence in the Buildout — every criterion ticked against evidence, every verification layer either evidenced or disclosed. Switching the verification pass off means the run ends `COMPLETE` and unverified, not verified anyway.

**`/fix` — one, and only when approval is enabled:** the confirmation at 6.2. On `Worktree: Yes` the merge-back choice rides along with it — the gate sits **before** the commit and squash-merge at 6.3, so approving it is what authorises the merge. The branch question, when Branch Isolation is on and no flag was given, is asked once before Step 1 and is part of invoking the command, not the flow.

⛔ **A gate placed after the step it guards is not a gate.** `/fix` and `/spec` both put their one irreversible action — the squash merge onto the base branch — behind a question, and both must ask it *first*: once the merge has landed, the only answers left are "approve what already happened" and "revert". This is also why an agent that cannot emit `AskUserQuestion` must yield instead of proceeding (`agent-gate-protocol.md`); under orchestration the gate is the coordinator's only chance to see the diff before it lands.

**Worktree isolation is available in all three**, via the shared `spec-branch-setup.md` runbook: `--worktree=yes` for an isolated checkout squash-merged back at the end, `--new-branch` for a fresh branch off the default. Each workflow owns its own merge-back.

⛔ **An auto-continued question is not an answer.** An `AskUserQuestion` result reading "No response after Ns — continued without an answer" means the user has not responded. Treat it as silence at any interaction point: don't act on the recommended option, don't infer approval, re-ask when they return. **The one exception is `/build`'s Step 1.5 clarification**, which is a scoping question and not a gate: there, take the recommended option, say which, and build — an autonomous run must not stall on an absent user. Nothing else in `/build` can auto-continue, because nothing else asks.

**Deviations:** auto-fix bugs, missing validation, and broken imports inline and document them. **Stop and ask** for architectural changes — a new table, a library swap, a breaking API.

**Stop guard:** when it blocks a stop during `/spec` or `/build`, don't acknowledge it, output resume instructions, or say goodbye. Your very next action is a tool call. Same after any user interruption — re-read the plan or Buildout and resume. In `/build` this hook *is* the loop's goal condition; there is nothing extra for the user to type.
<!-- /CC-ONLY -->
<!-- CODEX-START
## Explicit workflow runs

When the user explicitly invokes a Pilot workflow, its loaded skill is authoritative for its lifecycle, gates, and completion conditions. Until then, none of those workflow mechanics apply to ordinary direct execution.
CODEX-END -->
