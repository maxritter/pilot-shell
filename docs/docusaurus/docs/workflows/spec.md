---
sidebar_position: 4
title: /spec
description: Plan, implement, and verify complex features with full automation — Spec-Driven Development with TDD, plan approval gates, code review, and worktree isolation.
---

# /spec

Plan, implement, and verify complex features with full automation using Spec-Driven Development.

Best for new features, refactoring, and architectural changes — work where a plan and discussion add value before writing code. On Claude Code, `/spec` replaces the built-in plan mode (Shift+Tab). The structured workflow prevents scope creep and ensures every task is tested and verified before being marked complete.

For bugfixes, use [`/fix`](/docs/workflows/fix). For vague ideas, use [`/prd`](/docs/workflows/prd) first to produce a PRD, then hand off to `/spec`.

```bash
# Claude Code
claude
> /spec "Add user authentication with OAuth and JWT tokens"
> /spec "Migrate the REST API to GraphQL"

# Codex CLI
codex
> $spec "Add user authentication with OAuth and JWT tokens"
> $spec "Migrate the REST API to GraphQL"
```

## Workflow

```
Discuss → Plan → Approve → Implement → Verify → Done
```

Manual steps are **Approve** (required) and **Code Review** (optional, via Console). Everything else runs automatically. The Verify → Implement feedback loop repeats until all checks pass, then prompts for squash merge.

## Spec Types

### Feature Spec

Full exploration workflow for new functionality, refactoring, or any work where architecture decisions matter.

- Codebase exploration with Semble hybrid search and CodeGraph structural analysis
- Architecture design decisions via Q&A
- Concise plan: Goal, Approach, per-task Definition of Done — boundary, risks, and verification sections appear only when there's something concrete to say
- Unified verification agent (optional, configurable in Console Settings)

### Bugfixes

For a bugfix workflow without a plan file, use [`/fix`](/docs/workflows/fix). When the user types `/spec` with a bug description, the full bugfix workflow runs — root-cause investigation, three-task structure (RED test → fix → quality gate), Behavior Contract audit, revert-test proof in verify, iteration cap at 3.

## Three Phases

### Plan Phase

- Explores codebase with semantic search, asks clarifying questions
- Writes detailed spec with scope, tasks, and definition of done
- For UI/user-facing features: writes structured **E2E test scenarios** (TS-001, TS-002…) with step-by-step actions and expected results — these become the verification contract for the Verify phase
- Spec-review agent validates completeness in Claude Code or Codex (optional, enabled by default)
- Waits for your approval — edit the plan directly, or **annotate it visually** in the Console's Specifications tab (select any text, write a note — annotations save automatically). The agent reads your annotations at the approval checkpoint, revises the plan, and re-asks for approval

:::note Approval gates wait for you
Claude Code auto-continues an unanswered question after 60 seconds of keyboard idle ("No response after 60s — continued without an answer"). Pilot disables that by setting `CLAUDE_AFK_TIMEOUT_MS` in `~/.claude/settings.json`, so `/spec` and `/fix` approval gates stay open until you answer — even when you work in another window for an hour. Takes effect for sessions started after the update (or after a Console settings save); the workflow rules additionally treat an auto-continued question as "not answered" and re-ask. Prefer the auto-continue? Set your own `CLAUDE_AFK_TIMEOUT_MS` value under `env` in `settings.json`; Pilot never overwrites an existing value.
:::

### Implement Phase

- Isolated git worktree, new branch from default, or current branch (your choice)
- Strict TDD for each task: RED → GREEN → REFACTOR
- Quality hooks auto-lint, format, and type-check every edit
- Full test suite runs at the **Quality Gate** task (end), not after every task — running it per-fix-task is the single biggest token sink in bundled bugfix plans, so the targeted test module is used between fixes and the authoritative full-suite run happens once

### Verify Phase

- Full test suite + type checking + lint + build verification
- Features: changes review — a single `changes-review` sub-agent on Claude Code, the native changes-review agent on Codex, plus an inline plan-compliance & goal-truth audit (optional, enabled by default)
- Bugfixes: regression test + full suite — no sub-agents needed
- For UI features: executes the plan's **E2E test scenarios** step-by-step via browser automation — tracks pass/fail per scenario, auto-fixes failures (up to 2 attempts), escalates persistent failures to known issues; results written back to the plan file. Claude Code prefers its Chrome extension; Codex uses the Chrome DevTools MCP. Both fall back to playwright-cli / agent-browser.
- Auto-fixes findings, loops back until all checks pass
- After automated checks pass, prompts you to **review code changes** in the Console's Changes tab — each file shows a **T{N}** badge linking it to the spec task that changed it, and you can click **Spec** to group files by task for focused review. Enable Review mode to add inline annotations on any diff line (they save automatically), and the agent addresses them before marking the spec as verified

## Configurable Toggles

All interaction points in `/spec` are configurable via **Console Settings → Spec Workflow** and **Console Settings → Reviewers**.

### Spec Workflow Toggles

| Toggle               | Default | Effect when disabled                                                      |
| -------------------- | ------- | ------------------------------------------------------------------------- |
| **Worktree Support** | On      | Worktree and new-branch options are hidden — implementation always runs on the current branch |
| **Ask Questions**    | On      | Planning runs fully autonomous — no clarifying questions                  |
| **Plan Approval**    | On      | Implementation starts immediately after planning — no approval gate       |

When all three are disabled, `/spec` runs end-to-end without any user interaction. Start a task, come back to verified code.

### Reviewer Toggles

| Toggle          | Default | What it does                                                                                  |
| --------------- | ------- | --------------------------------------------------------------------------------------------- |
| **Spec Review** | On      | Validates the plan before implementation — checks alignment and flags risky assumptions       |
| **Changes Review** | On   | Reviews code after implementation — bugs, security, and cleanups; plan compliance and goal achievement stay covered on both agents (inline workflow audit on Claude Code, the native agent's own pass on Codex) |

Both run outside the main session context on both agents: Claude Code uses a sub-agent, Codex a custom agent installed under `~/.codex/agents/`. Optional **Codex Companion Reviewers** (off by default) add a Claude Code plugin second opinion using OpenAI Codex — best reserved for high-risk or security-sensitive specs. The **Changes Review** and **Codex Companion Changes Review** toggles also govern [`/fix`](/docs/workflows/fix), which runs the same reviews at finalise.

For a deeper multi-agent sweep on a particular change, run Claude Code's built-in `/code-review` yourself. It is user-invocable only, so no Pilot workflow can launch it for you — see the [Review Agents](/docs/features/console#spec-workflow---review-agents) note.

**Codex runs at most once per `/spec` invocation.** Plan iterations (annotation feedback, verify re-runs, fixing prior findings) reuse the result of the first Codex review instead of re-launching — a sentinel file in the session directory enforces this. The bugfix planning phase no longer runs Codex at all; adversarial review is most valuable on real code, not on a plan.

## Branch Strategy (Optional)

When starting a `/spec` task, you're asked how you want to work:

| Option | What happens |
| ------ | ------------ |
| **Use worktree** | Creates an isolated git worktree on a dedicated branch. `main` stays clean. Pilot auto-stashes uncommitted changes, restores them after. Squash-merged after verification — or discard with no cleanup. |
| **Current branch** | Works directly on whatever branch you're on. Simplest option when you're already on a clean feature branch. |
| **New branch from default** | Fetches origin, creates `feat/<slug>` (or `fix/<slug>` for bugfixes) from `origin/main`, and checks it out. Best when your current branch isn't clean but you don't want full worktree isolation. |

Disable the **Worktree Support** toggle in Console Settings to skip this question entirely — `/spec` will always use the current branch.

For bugfixes, use [`/fix`](/docs/workflows/fix) — the worktree question is asked here in `/spec` because that's where it applies.
