---
sidebar_position: 8
title: Pilot Console
description: Local web dashboard at localhost:41777 — monitor and manage your sessions
---

# Pilot Console

Local web dashboard at `localhost:41777` — monitor and manage your sessions.

The Console runs locally as a Bun/Express server with a React web UI. It's automatically started when you launch Pilot and stopped when all sessions close. All data — memories, sessions, usage — is stored in a local SQLite database. Nothing leaves your machine.

```bash
$ open http://localhost:41777
```

## 9 Views

| View | Description |
|------|-------------|
| **Dashboard** | Workspace status, active sessions, spec progress, git info, recent activity. Your real-time command center. |
| **Specifications** | All spec plans with task progress (checkboxes), phase tracking (PENDING/COMPLETE/VERIFIED), and iteration history. |
| **Extensions** | All extensions — local, plugin, and remote — with team sharing via git (push, pull, diff), color-coded categories, and scope filtering (All / Global / Project / Plugin / Remote). |
| **Changes** | Git diff viewer with staged/unstaged files, branch info, and worktree context. |
| **Memories** | Browsable observations — decisions, discoveries, bugfixes — with type filters, search, and timeline view. |
| **Sessions** | Active and past sessions with observation counts, duration, and the ability to browse session context. |
| **Usage** | Daily token costs, model routing breakdown (Opus vs Sonnet distribution), and usage trends over time. |
| **Settings** | Model selection per command and sub-agent (Sonnet 4.6 vs Opus 4.6). Spec workflow toggles (worktree support, ask questions, plan approval). Reviewer toggles (plan reviewer, spec reviewer). Context window size auto-detected from Claude Code. |
| **Help** | Embedded documentation from pilot-shell.com — full technical reference without leaving the Console. |

## Plan Annotation & Code Review

The Console provides two live annotation mechanisms that let you shape what gets built and verify what was built — without leaving the browser. Annotations save automatically as you write them; the agent reads them directly at review checkpoints.

### Plan Annotation

When a spec plan is in the planning phase (PENDING, not yet approved), the Specifications tab automatically opens in **Annotate mode**. You can also toggle between View and Annotate modes using the prominent toggle next to the "Specifications" heading.

In Annotate mode, the entire plan is rendered as selectable text. Select any passage and write a free-text note in the popover that appears. That's it — no type selection, no submit button. Your annotation is immediately saved and visible in the sidebar panel.

The sidebar shows all your annotations with the selected text and your note. You can edit or delete any annotation at any time.

When the agent reaches the approval checkpoint, it reads your annotations directly from the Console, incorporates every note into the plan, and asks for approval again. You don't need to do anything — just write your notes and say "ready" when done.

### Code Review

After a spec completes all automated verification checks, the agent prompts you to review the code changes before marking the spec as verified. The **Changes** tab is located right next to Specifications in the sidebar — switch there and enable **Review mode** using the toggle next to the "Changes" heading.

In Review mode, a **+** button appears on hover for every diff line. Click it to open an inline annotation form below that line — write your note and press Save. The annotation appears in the panel at the bottom of the diff viewer.

The agent reads your code review annotations directly from the Console before marking the spec as verified. Say "fix" to have it address your annotations, or "approve" to mark the spec as verified.

Annotations persist across page reloads, so you can review asynchronously while the agent runs verification in the background.

## Smart Notifications via SSE

The Console sends real-time alerts via Server-Sent Events when Claude needs your input or a significant phase completes. You don't need to watch the terminal constantly — the Console notifies you.

- Plan requires your approval — review and respond in the terminal or via notification
- Spec phase completed — implementation done, verification starting
- Clarification needed — Claude is waiting for design decisions before proceeding
- Session ended — completion summary with observation count

## Settings

The Settings tab (`localhost:41777/#/settings`) controls how Pilot Shell behaves. Changes are saved to `~/.pilot/config.json` and take effect after restarting Claude Code.

### Model Preferences

Choose between **Sonnet 4.6** ($3/$15 per MTok) and **Opus 4.6** ($5/$25 per MTok) for each component independently.

#### General

| Setting | Default | Description |
|---------|---------|-------------|
| **Main Session** | Opus | Quick mode and direct chat |

#### Spec Phases

| Phase | Default | Description |
|-------|---------|-------------|
| **Planning** | Opus | Codebase exploration, architecture design, plan writing |
| **Implementation** | Sonnet | TDD loop — write test, write code, verify |
| **Verification** | Sonnet | Test execution, code review orchestration |

#### Extended Context (1M)

Toggle for using the 1M token context window instead of 200K. Included at no additional cost with Max, Team, and Enterprise Claude plans. Disable only if your API plan doesn't support it.

### Spec Workflow

#### Review Agents

Two independent sub-agents that run in separate context windows during `/spec`:

| Agent | Default | Token cost | Description |
|-------|---------|------------|-------------|
| **Plan Review** | On | ~50k tokens | Validates plans before implementation. Checks alignment with requirements and flags risky assumptions. |
| **Spec Review** | On | ~100k tokens | Reviews code after implementation. Checks compliance, quality, and goal achievement. Reads all changed files. |

Each agent has its own model selector (Sonnet or Opus). Disabling an agent skips it entirely — no tokens consumed.

:::tip Non-Max users
During installation, Pilot automatically disables both review agents for Pro, Team, and Enterprise users to reduce token usage. You can re-enable them here if desired.
:::

#### Automation

Three toggles that control user interaction points during `/spec`. Disable all three for fully autonomous operation.

| Toggle | Default | When enabled | When disabled |
|--------|---------|-------------|---------------|
| **Worktree Support** | On | Asks whether to isolate changes in a git worktree at the start of `/spec` | Worktree is always skipped — changes go directly on the current branch |
| **Ask Questions** | On | Asks clarifying questions during planning to resolve ambiguities | Planning runs fully autonomous — makes default choices without asking |
| **Plan Approval** | On | Requires your approval before implementation starts | Implementation begins automatically after planning completes |

#### Fully Autonomous Mode

To make `/spec` run end-to-end without any user interaction:

1. Disable **Worktree Support** — skips the worktree prompt
2. Disable **Ask Questions** — planning makes autonomous decisions
3. Disable **Plan Approval** — implementation starts automatically

With all three off, typing `/spec add user authentication` will plan, implement, and verify the feature completely autonomously. You can review the output when it's done.

:::warning Token usage
Fully autonomous mode means no checkpoints — Claude will execute the entire workflow without asking. Make sure your prompt is specific enough to avoid misinterpretation. You can always interrupt with Escape.
:::

### Config File

All settings are stored in `~/.pilot/config.json`:

```json
{
  "model": "opus",
  "extendedContext": true,
  "commands": {
    "spec-plan": "opus",
    "spec-implement": "sonnet",
    "spec-verify": "sonnet",
    "spec": "sonnet",
    "setup-rules": "opus",
    "create-skill": "opus"
  },
  "agents": {
    "plan-reviewer": "sonnet",
    "spec-reviewer": "sonnet"
  },
  "reviewerAgents": {
    "planReviewer": true,
    "specReviewer": true
  },
  "specWorkflow": {
    "worktreeSupport": true,
    "askQuestionsDuringPlanning": true,
    "planApproval": true
  }
}
```

You can edit this file directly — the Console Settings UI is a convenience wrapper. Changes require a Claude Code restart to take effect.
