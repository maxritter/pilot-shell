<div align="center">

<img src="docs/img/logo.png" alt="Pilot Shell" width="400">

**The professional development environment for [Claude Code](https://docs.anthropic.com/en/docs/claude-code)**

### Claude Code is powerful. Pilot Shell makes it reliable.

Start a task, grab a coffee, check progress from your phone.</br>
**Tests enforced. Context preserved. Quality automated. Controllable from anywhere.**

[![Stars](https://img.shields.io/github/stars/maxritter/pilot-shell?style=flat&color=F59E0B)](https://github.com/maxritter/pilot-shell/stargazers)
[![Star History](https://img.shields.io/badge/Star_History-chart-8B5CF6)](https://star-history.com/#maxritter/pilot-shell&Date)
[![Downloads](https://img.shields.io/github/downloads/maxritter/pilot-shell/total?color=3B82F6)](https://github.com/maxritter/pilot-shell/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-10B981.svg)](https://github.com/maxritter/pilot-shell/pulls)

⭐ [Star this repo](https://github.com/maxritter/pilot-shell) · 🌐 [Website](https://pilot-shell.com) · 📖 [Documentation](https://pilot-shell.com/docs) · 🆕 [Updates](https://www.linkedin.com/in/rittermax/) · 📋 [Changelog](https://pilot.openchangelog.com/)

<br>

```bash
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash
```

**Works on macOS, Linux, and Windows (WSL2).**

<br>

<img src="docs/img/demo.gif" alt="Pilot Shell Demo" width="700">

</div>

---

## Why I Built This

**Claude Code writes code fast**. But without structure, it skips tests, loses context, and produces inconsistent results — especially on complex, established codebases where there are real conventions to follow and real regressions to catch. I tried other frameworks. Most of them add complexity — dozens of agents, elaborate scaffolding, thousands of lines of instruction files — but the output doesn't get a lot better. You just burn more tokens, wait longer and have to deal with a more complex setup.

**So I built Pilot Shell**. Instead of adding process on top, it bakes quality into every interaction. Linting, formatting, and type checking run as enforced hooks on every edit. TDD is mandatory, not suggested. Context is preserved across sessions. Every rule exists because I hit a real problem: a bug that slipped through, a regression that shouldn't have happened, a session where Claude cut corners.

**This isn't a vibe coding tool**. It's true agentic engineering with many months of effort put into it, but without the added complexity. You install it once, run `pilot` in any project, then `/setup-rules` to generate your project rules. Automate your common workflows by invoking the `/create-skill` command. Start a `/spec` task and let it run — when it's done, the work is tested, verified and ready to ship.

---

## Getting Started

### Prerequisites

**Claude Subscription:** Solo developers should choose [Max 5x](https://claude.com/pricing) for moderate usage or [Max 20x](https://claude.com/pricing) for heavy usage. Teams should use [Team Premium](https://claude.com/pricing) (6.25x usage per member, SSO, admin tools, billing management). Companies with stricter compliance or procurement requirements should use [Enterprise](https://claude.com/pricing) (API based pricing applies per usage).

### Installation

**Works with any existing project.** Pilot Shell is installed on top of Claude Code and uses its built-in concepts like commands, rules, hooks, skills, subagents, MCP, LSP and optimized settings to improve your experience:

```bash
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash
```

Installs globally on macOS, Linux, and Windows (WSL2). All tools and rules go to `~/.pilot/` and `~/.claude/`. After installation, `cd` into any project and run `pilot` or `ccp` to start.

<details>
<summary><b>What the installer does</b></summary>

7-step installer with progress tracking, rollback on failure, and idempotent re-runs:

1. **Prerequisites** — Checks/installs Homebrew, Node.js, Python 3.12+, uv, git, jq
2. **Claude files** — Sets up `~/.claude/` plugin — rules, commands, hooks, MCP servers
3. **Config files** — Creates `.nvmrc` and project config
4. **Dependencies** — Installs Probe, RTK, codebase-memory-mcp, playwright-cli, language servers
5. **Shell integration** — Auto-configures bash, fish, and zsh with `pilot` alias
6. **VS Code extensions** — Installs recommended extensions for your stack
7. **Finalize** — Success message with next steps

</details>

<details>
<summary><b>Installing a specific version or uninstalling</b></summary>

**Specific version** (see [releases](https://github.com/maxritter/pilot-shell/releases)):

```bash
export VERSION=7.6.5
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash
```

**Uninstall** — removes the Pilot binary, plugin files, managed commands/rules, settings and shell aliases:

```bash
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/uninstall.sh | bash
```

</details>

<details>
<summary><b>Dev Container</b></summary>

Pilot Shell works inside Dev Containers. Copy the [`.devcontainer`](https://github.com/maxritter/pilot-shell/tree/main/.devcontainer) folder from this repository into your project, adapt it to your needs (base image, extensions, dependencies), and run the installer inside the container. The installer auto-detects the container environment and skips system-level dependencies like Homebrew.

</details>

---

## How It Works

### Pilot Shell Console

A local web dashboard with different views and real-time notifications when Claude needs your input:

<img src="docs/img/dashboard.png" alt="Pilot Shell Console — Dashboard" width="700">

<details>
<summary><b>All views</b></summary>

| View              | What it shows                                                                                                                                |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Dashboard**     | Workspace status, active sessions, spec progress, git info, recent activity                                                                  |
| **Specification** | All spec plans with task progress, phase tracking, and iteration history                                                                     |
| **Extensions**    | All extensions — local, plugin, and remote — with team sharing via git, diff view, push/pull, and color-coded categories                     |
| **Changes**       | Git diff viewer with staged/unstaged files, branch info, and worktree context                                                                |
| **Memories**      | Browsable observations — decisions, discoveries, bugfixes — with type filters and search                                                     |
| **Sessions**      | Active and past sessions with observation counts and duration                                                                                |
| **Usage**         | Daily token costs, model routing breakdown, and usage trends                                                                                 |
| **Settings**      | Model selection per command/sub-agent, spec workflow toggles (worktree, questions, approval), reviewer toggles, context window auto-detected |
| **Help**          | Documentation, guides, and quick-start resources                                                                                             |

</details>

### Status Line

A three-line dashboard rendered below every Claude Code response. Replaces the default status line with real-time session metrics, spec progress, and version info — all color-coded.

```
Opus 4.6 [1M] | █████░▓ 60% | +156 -23 | main +2 ~3 | $1.45 | saved 12.5K (65%)
Spec: my-feature feature [implement] ████░░░░ 3/6 [plan-rev spec-rev wt]
Pilot 8.2.1 (Solo) · CC 2.1.79 (Max) · sessions 2 · memories 12
```

<details>
<summary><b>All fields explained</b></summary>

**Line 1 — Session Metrics** (separated by `|`):

| Widget            | Description                                                                     |
| ----------------- | ------------------------------------------------------------------------------- |
| **Model**         | Active model in short form (`Opus 4.6 [1M]`)                                    |
| **Context**       | Effective context usage with progress bar. Green < 80%, Yellow 80–95%, Red 95%+ |
| **Lines changed** | `+added -removed` in session (hidden on Linux when usage data available)        |
| **Git**           | Branch with staged (`+N`) / unstaged (`~N`) counts                              |
| **Cost**          | Session cost in USD. Green < $1, Yellow $1–5, Red $5+                           |
| **5h / 7d usage** | Rate limit usage with reset time (Linux only)                                   |
| **RTK savings**   | Token savings from RTK proxy (shown when no usage data)                         |

**Line 2 — Mode:**

- **Quick Mode:** `Quick Mode · /spec for feature implementation and complex bugfixes`
- **Spec Mode:** Plan name, type (`feature`/`bugfix`), phase (`plan`/`implement`/`verify`), progress bar, task count, iteration count, and config flags (`plan-rev`, `spec-rev`, `wt` — green = on, dim = off)

**Line 3 — Version & Session Info:**

`Pilot <version> (<tier>) · CC <version> (<subscription>) · sessions <N> · memories <N>`

Pilot tier: Solo, Team, or Trial with time remaining. Claude subscription (Pro/Max/Team/Enterprise) detected via `claude auth status` and cached for 24 hours.

</details>

### /spec — Spec-Driven Development

**`/spec` replaces Claude Code's built-in plan mode** (Shift+Tab). It provides a complete planning workflow with TDD, verification, and code review — use `/spec` instead of plan mode for all planned work.

Features, bug fixes, refactoring — describe it and `/spec` handles the rest. Auto-detects whether it's a feature or a bugfix and adapts the workflow.

```bash
pilot
> /spec "Add user authentication with OAuth and JWT tokens"   # → feature mode
> /spec "Fix the crash when deleting nodes with two children"  # → bugfix mode (auto-detected)
```

```
Plan  →  Approve  →  Implement (TDD)  →  Verify  →  Done
                                            ↑         ↓
                                            └── Loop──┘
```

<details>
<summary><b>Feature Mode</b></summary>

Full exploration workflow for new functionality, refactoring, or architectural changes.

**Plan:** Explores codebase with semantic search → asks clarifying questions → writes detailed spec with scope, tasks, and definition of done → **plan-reviewer sub-agent** validates completeness → waits for your approval.

**Implement:** Creates an isolated git worktree → implements each task with strict TDD (RED → GREEN → REFACTOR) → quality hooks auto-lint, format, and type-check every edit → full test suite after each task.

**Verify:** Full test suite + actual program execution → **unified review sub-agent** (compliance + quality + goal) → auto-fixes findings → squash merges to main on success.

</details>

<details>
<summary><b>Bugfix Mode</b></summary>

Investigation-first workflow for targeted fixes. Finds the root cause before touching any code.

**Investigate:** Reproduces the bug → traces backward through the call chain to find the **root cause** at a specific `file:line` → compares against working code patterns → states the fix with confidence level. If 3+ hypotheses fail, escalates as an architectural problem.

**Test-Before-Fix:** Writes a regression test that FAILS on current code → implements the minimal fix at the root cause → verifies all tests pass. Defense-in-depth validation at multiple layers when the bug involves data flowing through shared code paths.

**Verify:** Lightweight verification — regression test confirmation → full test suite → lint + type check → quality checks. No review sub-agents — the regression test proves the fix works, the full suite proves nothing else broke.

**Why this matters:** Root cause investigation prevents "fix one thing, break another." The regression test locks in the fix. No formal notation overhead — just trace, test, fix, verify.

</details>

### Quick Mode

Just chat — no plan, no approval gate. Quality hooks and TDD enforcement still apply. Best for small tasks and exploration. For anything that needs a plan, use `/spec` — not Claude Code's built-in plan mode.

### /setup-rules — Generate Modular Rules

Explores your codebase, discovers conventions, generates modular rules and documents MCP servers. Run once initially, then anytime your project changes significantly.

```bash
pilot
> /setup-rules
```

<details>
<summary><b>What /setup-rules Does</b></summary>

11 phases that read your codebase and produce comprehensive AI context:

0. **Reference** — load best practices for rule structure, path-scoping, and quality standards
1. **Read existing rules** — inventory all `.claude/rules/` files, detect structure and path-scoping
2. **Migrate unscoped assets** — prefix with project slug for better sharing
3. **Quality audit** — check rules against best practices (size, specificity, stale references, conflicts)
4. **Explore codebase** — semantic search with Probe CLI, structural analysis with codebase-memory-mcp
5. **Compare patterns** — discovered vs documented conventions
6. **Sync project rule** — update `{slug}-project.md` with current tech stack, structure, commands
7. **Sync MCP docs** — smoke-test user MCP servers, document working tools
8. **Discover new rules** — find undocumented patterns worth capturing
9. **Cross-check** — validate all references, ensure consistency across generated files
10. **Summary** — report all changes made

**For monorepos:** Organizes rules in nested subdirectories by product and team, with `paths` frontmatter to scope rules to specific file types. Generates a `README.md` documenting the structure.

</details>

### /create-skill — Reusable Skill Creator

Builds a reusable skill from any topic — explores the codebase and creates it interactively with you. If no topic is given, evaluates the current session for extractable knowledge.

```bash
pilot
> /create-skill "Automate the review and triaging of our PR Bot comments"
```

<details>
<summary><b>What /create-skill Does</b></summary>

6 phases that turn domain knowledge into a reusable skill:

1. **Reference** — load use case categories, complexity spectrum, file structure template, description formula, security restrictions
2. **Understand** — explore the codebase for relevant patterns, ask clarifying questions, or evaluate the current session for extractable knowledge
3. **Check existing** — search project and global skills to avoid duplicates
4. **Create** — write to `.claude/skills/` (project) or `~/.claude/skills/` (global), apply portability and determinism checklists
5. **Quality gates** — structure checklist (SKILL.md naming, frontmatter fields), content checklist (error handling, examples, exclusions), triggering test (should/shouldn't trigger), iteration signals
6. **Test & iterate** — run test prompts with sub-agents, evaluate results, optimize description triggering

**Use case categories:**

| Category                      | Best For                                                                   |
| ----------------------------- | -------------------------------------------------------------------------- |
| **Document & Asset Creation** | Consistent reports, designs, code with embedded style guides and templates |
| **Workflow Automation**       | Multi-step processes with validation gates and iterative refinement        |
| **MCP Enhancement**           | Workflow guidance on top of MCP tool access, multi-MCP coordination        |

**Skill structure:** Each skill is a folder with a `SKILL.md` file (case-sensitive), optional `scripts/`, `references/`, and `assets/` directories. The YAML frontmatter description determines when Claude loads the skill — it must include what the skill does, when to use it, and specific trigger phrases. Progressive disclosure keeps context lean: frontmatter loads always (~100 tokens), SKILL.md loads on activation, linked files load on demand.

</details>

### Extensions

Create your own rules, commands, skills, and agents — all plain markdown files in `.claude/`. Extensions live either in your project's `.claude/` directory or globally in `~/.claude/`.

<details>
<summary><b>Extension types</b></summary>

**Create extensions in your project:**

| Extension    | Location            | When it loads                               |
| ------------ | ------------------- | ------------------------------------------- |
| **Skills**   | `.claude/skills/`   | Automatically when relevant                 |
| **Rules**    | `.claude/rules/`    | Every session, or by file type              |
| **Commands** | `.claude/commands/` | On demand via `/command-name`               |
| **Agents**   | `.claude/agents/`   | Spawned as sub-agents for specialized tasks |

Use `/setup-rules` to auto-generate rules from your codebase. Use `/create-skill` to capture workflows as reusable skills. For monorepos, organize rules in subdirectories by team with `paths` frontmatter to scope by file type.

**Global vs Project scope:** Extensions in `.claude/` are project-specific (commit them so teammates get them on `git clone`). Extensions in `~/.claude/` are personal and available across all your projects.

**Team sharing (Team tier):** Connect a git repository to share extensions across your team. Push local extensions to the remote, pull remote ones to your machine, and compare versions with a built-in diff view. Supports subfolder paths for organized team repos.

**Plugin extensions:** Installed Claude Code plugins and their extensions (commands, skills, agents) are automatically discovered and shown in the Extensions page as read-only items.

Manage all extensions from the **Console Extensions page** — view, edit, rename, delete, move between scopes, compare diffs, and push/pull from a connected team remote.

</details>

### Remote Control

Control your Pilot Shell sessions from anywhere — your phone, tablet, or any browser. Start a `/spec` task at your desk, then monitor and steer it from the couch.

<details>
<summary><b>Setup and usage</b></summary>

**Prerequisite:** [Remote Control](https://youtu.be/Ko7_tC1fMMM?si=kWDzYiQvxlkZTrRK) requires the native install of Claude Code (not the npm version). If you have the npm version installed, uninstall it first:

```bash
npm uninstall -g @anthropic-ai/claude-code   # Remove npm version if installed
curl -fsSL https://claude.ai/install.sh | bash  # Install native version
```

**Activate Remote Control:**

| Method             | How                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------- |
| **Single session** | Type `/remote-control` inside any Pilot Shell session                                 |
| **All sessions**   | Run `/config` in Claude Code → set "Enable Remote Control for all sessions" to `true` |

Once active, open the **Claude Mobile App** (iOS/Android) → **Code** tab. Your Pilot Shell session appears there with all rules, hooks, and MCP servers — the full Pilot Shell experience, from your phone. Your computer must stay awake for the connection to remain active — on macOS, use [Amphetamine](https://apps.apple.com/de/app/amphetamine/id937984704) to keep your Mac awake with the display off.

**Start sessions via SSH from your phone:**

The above assumes you start sessions via `pilot` on your computer first. To also **start new sessions from your phone**:

1. Install [Termius](https://termius.com/) on your **mobile phone** (not your computer)
2. Connect via SSH to your computer and run `pilot` in any project directory

**macOS sleep support:** Turn on **Remote Login** in macOS Settings → General → Sharing → Advanced → Remote Login. This lets you SSH into your Mac even while it's sleeping.

**Outside your home network:** Install [Tailscale](https://tailscale.com/) on both your computer and phone to create a VPN tunnel. This is only needed for the SSH approach — Remote Control via the Claude App works everywhere without extra setup.

</details>

---

## Demo

A full-stack project — created from **scratch with a single prompt**, then extended with **3 features built in parallel** using `/spec` and Git worktrees. Every line of code tested and verified by Pilot, zero manual code edits. **[Check out the Demo Project here →](https://github.com/maxritter/pilot-shell-demo)**

---

## Under the Hood

### The Hooks Pipeline

Hooks fire automatically across the entire lifecycle — formatting, linting, type checking, TDD enforcement, context preservation, and memory capture. Every file edit triggers quality checks. Every session start restores state. Every session end persists context.

<details>
<summary><b>All hooks by lifecycle event</b></summary>

#### SessionStart (on startup, clear, or compact)

| Hook                      | Type     | What it does                                                                          |
| ------------------------- | -------- | ------------------------------------------------------------------------------------- |
| Memory loader             | Blocking | Loads persistent context from Pilot Shell Console memory                              |
| `post_compact_restore.py` | Blocking | After auto-compaction: re-injects active plan, task state, and context                |
| `session_clear.py`        | Blocking | On /clear: resets session state (spec artifacts, task list, caches) for a clean start |
| Session tracker           | Async    | Initializes user message tracking for the session                                     |

#### UserPromptSubmit (when the user sends a message)

| Hook                 | Type     | What it does                                                          |
| -------------------- | -------- | --------------------------------------------------------------------- |
| `spec_mode_guard.py` | Blocking | Blocks `/spec` in plan mode, warns when not in bypassPermissions mode |
| Session initializer  | Async    | Registers the session with the Console worker daemon on first message |

#### PreToolUse (before Bash, search, web, or agent tools)

| Hook                  | Type     | What it does                                                                                                                                      |
| --------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tool_redirect.py`    | Blocking | Blocks WebSearch/WebFetch (MCP alternatives exist), Explore agent (use Probe + codebase-memory-mcp), EnterPlanMode/ExitPlanMode (/spec conflict). |
| `tool_token_saver.py` | Blocking | Rewrites Bash commands via RTK for token savings (60–90% reduction on dev operations).                                                            |

#### PostToolUse (after file edits, searches, and other tool calls)

| Hook                 | Type         | What it does                                                                                                                                                   |
| -------------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `file_checker.py`    | Blocking     | Quality checks: Python (ruff), TypeScript (ESLint), Go (go vet + golangci-lint). Also warns when implementation files are edited without a failing test (TDD). |
| `context_monitor.py` | Non-blocking | Tracks context usage 0-100% with warnings as compaction approaches.                                                                                            |
| Memory observer      | Async        | Captures development observations to persistent memory.                                                                                                        |

#### PreCompact (before auto-compaction)

| Hook             | Type     | What it does                                                                                                   |
| ---------------- | -------- | -------------------------------------------------------------------------------------------------------------- |
| `pre_compact.py` | Blocking | Captures Pilot Shell state (active plan, task list, key context) to persistent memory before compaction fires. |

#### Stop (when Claude tries to finish)

| Hook                 | Type     | What it does                                                                                                                               |
| -------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `spec_stop_guard.py` | Blocking | If an active spec exists with PENDING or COMPLETE status, **blocks stopping**. Forces verification to complete before the session can end. |
| Session summarizer   | Async    | Saves session observations to persistent memory for future sessions.                                                                       |

Additionally, `spec_plan_validator.py` and `spec_verify_validator.py` run as command-scoped Stop hooks during `/spec` phases — they verify plan creation and VERIFIED status respectively.

#### SessionEnd (when the session closes)

| Hook             | Type     | What it does                                                                                                   |
| ---------------- | -------- | -------------------------------------------------------------------------------------------------------------- |
| `session_end.py` | Blocking | Stops the worker daemon when no other Pilot Shell sessions are active. Sends real-time dashboard notification. |

</details>

### Context Preservation

Pilot Shell preserves context automatically across compaction boundaries. Before compaction fires, hooks capture the active plan, task list, and key decisions to persistent memory. After compaction, hooks restore everything — work continues exactly where it left off. Multiple sessions can run in parallel on the same project without interference.

<details>
<summary><b>How the effective context display works</b></summary>

Claude Code reserves ~16.5% of the context window as a compaction buffer, triggering auto-compaction at ~83.5% raw usage. Pilot Shell rescales this to an **effective 0–100% range** so the status bar fills naturally to 100% right before compaction fires. A `▓` buffer indicator at the end of the bar shows the reserved zone. The context monitor warns at ~80% effective (informational) and ~90%+ effective (caution) — no confusing raw percentages.

</details>

### Smart Model Routing

Opus for planning — where reasoning quality matters most. Sonnet for implementation and verification — where a clear spec makes fast execution predictable. All model assignments are configurable per-component via the Pilot Shell Console settings.

<details>
<summary><b>Phase-by-phase breakdown</b></summary>

| Phase                 | Default | Why                                                                                                                                                                                                                 |
| --------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Planning**          | Opus    | Exploring your codebase, designing architecture, and writing the spec requires deep reasoning. A good plan is the foundation of everything.                                                                         |
| **Plan Verification** | Sonnet  | The plan-reviewer sub-agent validates completeness and challenges assumptions on every feature spec. _(enabled by default — disable in Console Settings → Reviewers)_                                               |
| **Implementation**    | Sonnet  | With a solid plan, writing code is straightforward. Sonnet is fast, cost-effective, and produces high-quality code when guided by a clear spec.                                                                     |
| **Code Verification** | Sonnet  | The unified spec-reviewer agent handles deep code review (compliance + quality + goal). The orchestrator runs mechanical checks and applies fixes. _(enabled by default — disable in Console Settings → Reviewers)_ |

Choose between Sonnet 4.6 and Opus 4.6 for the main session, each command, and sub-agents. Context window size (200K or 1M) is **auto-detected from Claude Code** based on your subscription plan — no manual configuration needed. 1M context requires a Max (20x) or Enterprise subscription.

</details>

### Built-in Rules & Standards

Production-tested best practices loaded into every session. Core rules cover workflow, testing, verification, debugging, and tools. Coding standards activate conditionally by file type. These aren't suggestions, they're enforced.

<details>
<summary><b>Core Workflow</b></summary>

- `task-and-workflow.md` — Task management, /spec orchestration, deviation handling
- `testing.md` — TDD workflow, test strategy, coverage requirements
- `verification.md` — Execution verification, completion requirements

</details>

<details>
<summary><b>Development Practices</b></summary>

- `development-practices.md` — Project policies, debugging methodology, git rules
- `context-management.md` — Auto-compaction and context preservation

</details>

<details>
<summary><b>Tools</b></summary>

- `cli-tools.md` — Pilot CLI, Probe CLI semantic search, RTK token optimization
- `playwright-cli.md` — Browser automation for E2E UI testing

</details>

<details>
<summary><b>Coding Standards (activated by file type)</b></summary>

| Standard   | Activates On                                      | Coverage                                                |
| ---------- | ------------------------------------------------- | ------------------------------------------------------- |
| Python     | `*.py`                                            | uv, pytest, ruff, basedpyright, type hints              |
| TypeScript | `*.ts`, `*.tsx`, `*.js`, `*.jsx`                  | npm/pnpm, Jest, ESLint, Prettier, React patterns        |
| Go         | `*.go`                                            | Modules, testing, formatting, error handling            |
| Frontend   | `*.tsx`, `*.jsx`, `*.html`, `*.vue`, `*.css`      | Components, CSS, accessibility, responsive design       |
| Backend    | `**/models/**`, `**/routes/**`, `**/api/**`, etc. | API design, data models, query optimization, migrations |

</details>

### MCP Servers

MCP servers provide external context in every session — library docs, persistent memory, web search, GitHub code search, web page fetching, and code intelligence.

<details>
<summary><b>All servers</b></summary>

| Server              | Purpose                                                                   |
| ------------------- | ------------------------------------------------------------------------- |
| **context7**        | Library documentation lookup — get API docs for any dependency            |
| **mem-search**      | Persistent memory search — recall context from past sessions              |
| **web-search**      | Web search via DuckDuckGo, Bing, and Exa                                  |
| **grep-mcp**        | GitHub code search — find real-world usage patterns across repos          |
| **web-fetch**       | Web page fetching — read documentation, APIs, references                  |
| **codebase-memory** | Code knowledge graph — call tracing, impact analysis, dead code detection |

</details>

### Language Servers (LSP)

Real-time diagnostics and go-to-definition for Python (basedpyright), TypeScript (vtsls), and Go (gopls). Auto-installed, auto-configured via `.lsp.json`, and auto-restart on crash.

### Pilot Shell CLI

The `pilot` binary (`~/.pilot/bin/pilot`) manages sessions, worktrees, licensing, and context. Run `pilot` or `ccp` to start Claude with Pilot Shell enhancements. Most commands support `--json` for structured output.

<details>
<summary><b>Session & Context</b></summary>

| Command                               | Purpose                                                                    |
| ------------------------------------- | -------------------------------------------------------------------------- |
| `pilot`                               | Start Claude with Pilot Shell enhancements, auto-update, and license check |
| `pilot run [args...]`                 | Same as above, with optional flags (e.g., `--skip-update-check`)           |
| `pilot check-context --json`          | Get current context usage percentage                                       |
| `pilot register-plan <path> <status>` | Associate a plan file with the current session                             |
| `pilot sessions [--json]`             | Show count of active Pilot Shell sessions                                  |

</details>

<details>
<summary><b>Worktree Isolation</b></summary>

| Command                                | Purpose                                               |
| -------------------------------------- | ----------------------------------------------------- |
| `pilot worktree create --json <slug>`  | Create isolated git worktree for safe experimentation |
| `pilot worktree detect --json <slug>`  | Check if a worktree already exists                    |
| `pilot worktree diff --json <slug>`    | List changed files in the worktree                    |
| `pilot worktree sync --json <slug>`    | Squash merge worktree changes back to base branch     |
| `pilot worktree cleanup --json <slug>` | Remove worktree and branch when done                  |
| `pilot worktree status --json`         | Show active worktree info for current session         |

</details>

<details>
<summary><b>License & Auth</b></summary>

| Command                        | Purpose                                |
| ------------------------------ | -------------------------------------- |
| `pilot activate <key>`         | Activate a license key on this machine |
| `pilot deactivate`             | Deactivate license on this machine     |
| `pilot status [--json]`        | Show current license status            |
| `pilot verify [--json]`        | Verify license (used by hooks)         |
| `pilot trial --check [--json]` | Check trial eligibility                |
| `pilot trial --start [--json]` | Start a trial                          |

</details>

---

## What Users Say

<!-- Replace with real testimonials from GitHub issues, discussions, or direct feedback as they come in -->

> "I stopped reviewing every line Claude writes. The hooks catch formatting and type errors automatically, TDD catches logic errors, and the spec verifier catches everything else. I review the plan, approve it, and the output is production-grade."

> "Other frameworks I tried added so much overhead that half my tokens went to the system itself. Pilot Shell is lean — quick mode has zero scaffolding, and even /spec only adds structure where it matters. More of my context goes to actual work."

> "The persistent memory changed everything. I can pick up a project after a week and Claude already knows my architecture decisions, the bugs we fixed, and why we chose certain patterns. No more re-explaining the same context every session."

---

## License

Pilot Shell is source-available under a commercial license. See the [LICENSE](LICENSE) file for full terms.

| Tier     | Seats | Includes                                                                           |
| :------- | :---- | :--------------------------------------------------------------------------------- |
| **Solo** | 1     | All features, continuous updates, community support via [GitHub Issues][gh-issues] |
| **Team** | Multi | Solo + extension sharing, seat management, priority support, team onboarding       |

All plans work across multiple personal machines — one subscription, all your devices.

[gh-issues]: https://github.com/maxritter/pilot-shell/issues

Details and licensing at [pilot-shell.com](https://pilot-shell.com).

---

## Rolling Out for Your Team?

Let's figure out if Pilot Shell is the right fit for your team and get everyone set up.

**[Book a Call](https://calendly.com/rittermax/pilot-shell)** · **[Send an Email](mailto:mail@maxritter.net)** · **[Connect on LinkedIn](https://www.linkedin.com/in/rittermax/)**

---

## FAQ

<details>
<summary><b>Does Pilot Shell send my code or data to external services?</b></summary>

**No code, files, prompts, project data, or personal information ever leaves your machine through Pilot Shell.** All development tools — code search (Probe), code intelligence (codebase-memory-mcp), persistent memory (Pilot Shell Console), session state, and quality hooks — run entirely locally.

Pilot Shell makes external calls **only for licensing**. Here is the complete list:

| When                              | Where             | What is sent                     |
| --------------------------------- | ----------------- | -------------------------------- |
| License validation (once per 24h) | `api.polar.sh`    | License key, organization ID     |
| License activation (once)         | `api.polar.sh`    | License key, machine fingerprint |
| Trial start (once)                | `pilot-shell.com` | Hashed hardware fingerprint      |

That's it — three calls total, each sent at most once (validation re-checks daily). No OS, no architecture, no Python version, no locale, no analytics, no heartbeats. The validation result is cached locally, and Pilot Shell works fully offline for up to 7 days between checks. Beyond these licensing calls, the only external communication is between Claude Code and Anthropic's API — using your own subscription or API key.

</details>

<details>
<summary><b>Is Pilot Shell enterprise-compliant for data privacy?</b></summary>

Yes. Your source code, project files, and development context never leave your machine through Pilot Shell. The only external calls are license validation (daily, license key only) and one-time activation/trial start (machine fingerprint only). No OS info, no version strings, no analytics, no telemetry. Enterprises using Claude Code with their own API key or Anthropic Enterprise subscription can add Pilot Shell without changing their data compliance posture.

</details>

<details>
<summary><b>What are the licenses of Pilot Shell's dependencies?</b></summary>

All external tools and dependencies that Pilot Shell installs and uses are open source with permissive licenses (MIT, Apache 2.0, BSD). This includes ruff, basedpyright, Prettier, ESLint, gofmt, uv, Probe, RTK, codebase-memory-mcp, playwright-cli, and all MCP servers. No copyleft or restrictive-licensed dependencies are introduced into your environment.

</details>

<details>
<summary><b>Do I need a separate Anthropic subscription?</b></summary>

Yes. Pilot Shell enhances Claude Code — it doesn't replace it. You need an active Claude subscription — [Max 5x or 20x](https://claude.com/pricing) for solo developers, [Team Premium](https://claude.com/pricing) for teams, or [Enterprise](https://claude.com/pricing) for organizations with compliance or procurement requirements. Pilot Shell adds quality automation on top of whatever Claude Code access you already have.

</details>

<details>
<summary><b>Does Pilot Shell work with Codex, Gemini CLI, OpenCode, or other AI coding tools?</b></summary>

No. Pilot Shell is built exclusively for Claude Code. Every hook, rule, command, and workflow is engineered specifically for Claude's tool-use protocol, prompt format, and session lifecycle. Pilot Shell also only supports Claude Sonnet 4.6 and Claude Opus 4.6 — these are the models that produce the best results, and every rule and prompt is optimized for their behavior. Supporting other tools or models would mean compromising on quality, which is the opposite of what Pilot Shell is designed to do.

</details>

<details>
<summary><b>Does Pilot Shell work with existing projects?</b></summary>

Yes — that's the primary use case. Pilot Shell doesn't scaffold or restructure your code. You install it, run `/setup-rules`, and it explores your codebase to discover your tech stack, conventions, and patterns. From there, every session has full context about your project. The more complex and established your codebase, the more value Pilot Shell adds — quality hooks catch regressions, persistent memory preserves decisions across sessions, and `/spec` plans features against your real architecture.

</details>

<details>
<summary><b>Does Pilot Shell work with any programming language?</b></summary>

Pilot Shell's quality hooks (auto-formatting, linting, type checking) currently support Python, TypeScript/JavaScript, and Go out of the box. TDD enforcement, spec-driven development, persistent memory, context preservation hooks, and all rules and standards work with any language that Claude Code supports. You can add custom hooks for additional languages.

</details>

<details>
<summary><b>Can I use Pilot Shell on multiple projects?</b></summary>

Yes. Pilot Shell installs once globally and works across all your projects — you don't need to reinstall per project. All tools, rules, commands, and hooks live in `~/.pilot/` and `~/.claude/`, available everywhere. Just `cd` into any project and run `pilot`. Each project can optionally have its own `.claude/` rules, custom skills, and MCP servers for project-specific behavior. Run `/setup-rules` in each project to generate project-specific documentation and standards.

</details>

<details>
<summary><b>Do I need to run the installer from inside a project directory?</b></summary>

No. You can run the installer from any directory — your home folder, a parent folder containing multiple repos, anywhere. Everything installs globally to `~/.pilot/` and `~/.claude/`. The only file written to the current directory is `.nvmrc` (a Node.js version hint).

</details>

<details>
<summary><b>Should I still use Claude Code's built-in plan mode (Shift+Tab)?</b></summary>

No — use `/spec` instead. Claude Code's built-in plan mode (Shift+Tab → "plan") is unstructured: plans live only in the conversation, have no consistent format, aren't saved as files, and disappear when the session ends. There's no verification, no TDD enforcement, and no way to resume or review a plan later.

`/spec` is a drop-in replacement that fixes all of this. Plans are written as structured markdown files in `docs/plans/` with a consistent format — scope, tasks, definition of done, and approval status. They persist across sessions, can be edited before approval, and drive a complete workflow: plan → implement with TDD → verify with code review. The plan file becomes the single source of truth for the entire task.

**Use `/spec` for all planned work.** Use Quick Mode (regular chat) for small tasks and exploration. There's no reason to use Claude Code's built-in plan mode when Pilot Shell is installed.

</details>

<details>
<summary><b>Why does Pilot Shell use bypass permissions mode?</b></summary>

Pilot Shell sets Claude Code to `bypassPermissions` mode by default so the `/spec` workflow can run autonomously — planning, implementing, and verifying without pausing for permission prompts at every tool call. This is what enables the end-to-end spec-driven development experience.

**In Quick Mode (regular chat), you have full control.** Press `Shift+Tab` at any time to cycle through Claude Code's permission modes:

| Mode             | Behavior                                              |
| ---------------- | ----------------------------------------------------- |
| **Plan**         | Claude proposes changes, you approve before execution |
| **Accept Edits** | File edits auto-approved, other actions still prompt  |
| **Normal**       | Fine-grained permission prompts for each tool call    |

You can also set a persistent default in `~/.claude/settings.json` by changing the `defaultMode` field to `acceptEdits`, `default`, `plan`, or `dontAsk`. Pilot Shell preserves your choice across updates — the installer merges permissions additively and never overwrites user customizations.

</details>

<details>
<summary><b>Can I add my own rules, commands, skills, and agents?</b></summary>

Yes. Create your own in your project's `.claude/` folder — rules, commands, skills, and agents are all plain markdown files. Your project-level assets load alongside Pilot Shell's built-in defaults and take precedence when they overlap. `/setup-rules` auto-discovers your codebase patterns and generates project-specific rules. `/create-skill` builds reusable skills from any topic interactively. View and manage all extensions on the Console Extensions page.

For monorepos, organize rules in nested subdirectories by product and team (e.g. `.claude/rules/my-product/team-x/`). Team-level rules must use `paths` frontmatter so they only load when working on relevant files. `/setup-rules` validates this structure, enforces path-scoping, and generates a `README.md` to document the organization.

</details>

<details>
<summary><b>Can I control Pilot Shell from my phone?</b></summary>

Yes — using Claude Code's [Remote Control](https://youtu.be/Ko7_tC1fMMM?si=kWDzYiQvxlkZTrRK) feature. Start a session via `pilot` on your computer, then type `/remote-control` to make it accessible from the Claude Mobile App (iOS/Android) under the **Code** tab. You can also enable it globally via `/config` → "Enable Remote Control for all sessions". Remote Control requires the native install of Claude Code (`curl -fsSL https://claude.ai/install.sh | bash`), not the npm version. Your computer must stay awake — on macOS, use [Amphetamine](https://apps.apple.com/de/app/amphetamine/id937984704) to keep your Mac awake with the display off. To start sessions directly from your phone, install [Termius](https://termius.com/) on your mobile device, SSH into your computer, and run `pilot`. For SSH access outside your home network, install [Tailscale](https://tailscale.com/) on both devices — the Claude App approach works everywhere without extra setup. **Troubleshooting:** If Remote Control doesn't connect, run `/logout` followed by `/login` inside Claude Code to re-authenticate.

</details>

<details>
<summary><b>Can I use Pilot Shell inside a Dev Container?</b></summary>

Yes. Copy the `.devcontainer` folder from this repository into your project, adapt it to your needs (base image, extensions, dependencies), and install Pilot Shell inside the container. Everything works the same — hooks, rules, MCP servers, persistent memory, and the Console dashboard all run inside the container. This is a great option for teams that want a consistent, reproducible development environment.

</details>

---

## Changelog

See the full changelog at [pilot.openchangelog.com](https://pilot.openchangelog.com/).

---

## Contributing

**Pull Requests** — New features, improvements, and bug fixes are welcome. You can improve Pilot Shell with Pilot Shell — a self-improving loop where your contributions make the tool that makes contributions better.

**Bug Reports** — Found a bug? [Open an issue](https://github.com/maxritter/pilot-shell/issues) on GitHub.

---

<div align="center">

**Claude Code is powerful. Pilot Shell makes it reliable.**

</div>
