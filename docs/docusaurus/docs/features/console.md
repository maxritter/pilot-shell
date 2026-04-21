---
sidebar_position: 8
title: Pilot Console
description: Local web dashboard at localhost:41777 — monitor and manage your sessions
---

# Pilot Console

Local web dashboard at `localhost:41777` — monitor and manage your sessions.

The Console runs locally as a Bun/Express server with a React web UI. It starts when you launch Pilot and stops when all sessions close. All data — memories, sessions, usage — lives in a local SQLite database. Nothing leaves your machine.

```bash
$ open http://localhost:41777
```

## Views

Each view that supports project filtering has an inline **Project Filter** dropdown next to the title. The **Dashboard** shows stats across all projects with clickable tiles that navigate to the relevant view.

| View | Description |
|------|-------------|
| **Dashboard** | Global command center — 8 clickable stat cards (Projects, Sessions, Active, Memories, Extensions, Requirements, Specifications, Changes), 4 recent-item cards with "Show all" links, active specs as pills in the top bar, notification bell in the top right. |
| **Sessions** | Browse past sessions with search. Copy a session ID and run `/resume <session-id>` to jump back in — all context, files, and conversation history restored. |
| **Memories** | Observations (decisions, discoveries, bugfixes) with type filters and search. Each memory links back to the session it came from. |
| **Requirements** | PRD documents with view/annotate modes. Selected opens as a tab, others live in a Previous dropdown. |
| **Specifications** | Spec plans with task progress, phase tracking (PENDING/COMPLETE/VERIFIED), and iteration history. Hosts Plan Annotation and Spec Sharing (below). |
| **Extensions** | All extensions — local, plugin, remote — with team sharing via git (push, pull, diff), color-coded categories, and scope filtering. |
| **Changes** | Git diff viewer with staged/unstaged files, branch info, worktree context. Hosts Code Review and Spec Task Correlation (below). |
| **Usage** | Daily token costs, model routing breakdown (Opus vs Sonnet), and usage trends. |
| **Help** | Embedded pilot-shell.com documentation — full technical reference without leaving the Console. |
| **Settings** | Model selection, spec workflow toggles, reviewer toggles, extended context toggle. See [Settings](#settings) below. |

## Plan Annotation

When a spec plan is in the planning phase (PENDING, not yet approved), the Specifications tab auto-opens in **Annotate mode**. Toggle between View and Annotate using the control next to the "Specifications" heading.

Select any passage and write a free-text note in the popover that appears — no type selection, no submit button. Annotations save immediately and appear in the sidebar panel, where you can edit or delete them.

When the agent reaches the approval checkpoint, it reads your annotations directly from the Console, incorporates every note into the plan, and asks for approval again. Just write your notes and say "ready" when done.

## Code Review

After a spec completes automated verification, the agent prompts you to review the code changes. Switch to the **Changes** tab and enable **Review mode** using the toggle next to the "Changes" heading.

In Review mode, a **+** button appears on hover for every diff line. Click it to open an inline annotation form — write your note and press Save. Annotations appear in a panel at the bottom of the diff viewer.

The agent reads your code-review annotations directly from the Console before marking the spec verified. Say "fix" to have it address them, "approve" to mark the spec as verified. Annotations persist across page reloads, so you can review asynchronously while the agent runs verification in the background.

## Spec Task Correlation

When a `/spec` task is active, the Changes tab correlates each changed file with the spec task that touched it — instant traceability.

- Each file in the file list shows a **T{N}** badge (e.g., `T1`, `T3`) linking it to the matching spec task
- Hover the badge for the full task name
- Click the **Spec** button to switch to **group-by-spec** view — files organized by spec name and task number
- Correlation is parsed from the `**Files:**` section of each task, so any spec following the standard format works automatically

Especially useful for multi-task specs: instead of scrolling a flat file list, review changes task by task.

## Spec Sharing

Share specs with teammates for collaborative review — no cloud service required. Everything works locally with compressed URLs.

**Share:**

1. Open a spec, click **Share with Teammate** in the metadata row
2. A share URL is generated — the spec content and your annotations are compressed into the URL fragment (per the HTTP spec, fragments are never sent to any server)
3. Copy the URL and send it via Slack, email, or any channel
4. The **Receive Feedback** dialog opens automatically so you're ready for their response

**Review a shared spec:**

1. Your colleague opens the URL in their Pilot Console
2. They see your spec and annotations as read-only highlights
3. They add their own feedback via text selection or the **+** button on any block
4. Click **Send Feedback** to generate a feedback URL

**Import feedback:**

1. Click **Receive Feedback** on the original spec
2. Paste the URL — a preview shows the incoming annotations
3. **Accept** or **Reject** each annotation individually, or use **Accept All** / **Reject All**

Importing the same feedback twice is safe — annotations matching existing ones are skipped. For specs larger than ~32KB compressed, an embedded paste service stores the data locally in `~/.pilot/share/` with 3-day auto-expiry.

:::tip Both annotation methods work everywhere
The **+** button and text selection both work on the normal review page and on shared feedback pages. The **+** button is more reliable for quick block-level comments.
:::

## Notifications

The Console sends real-time alerts via Server-Sent Events when Claude needs your input or a significant phase completes — no need to watch the terminal.

- Plan requires your approval — review and respond
- Spec phase completed — implementation done, verification starting
- Clarification needed — Claude is waiting for design decisions
- Session ended — completion summary with observation count

## Settings

The Settings tab (`localhost:41777/#/settings`) controls Pilot Shell behavior. Changes save to `~/.pilot/config.json` and take effect after restarting Claude Code.

### Model preferences

Choose between **Sonnet 4.6** ($3/$15 per MTok) and **Opus 4.7** ($5/$25 per MTok) independently per component.

| Component | Default | Scope |
|-----------|---------|-------|
| **Main Session** | Opus | Quick mode and direct chat |
| **Planning** | Opus | Codebase exploration, architecture design, plan writing |
| **Implementation** | Sonnet | TDD loop — write test, write code, verify |
| **Verification** | Sonnet | Test execution, code review orchestration |

**Custom model IDs** — each dropdown also offers a **Custom…** option. Selecting it reveals a text input where you can pin an explicit Anthropic model ID such as `claude-opus-4-6`, `claude-opus-4-5`, or `claude-sonnet-4-5-20250929`. Useful for reproducibility, team standardization, or falling back to an older model when a newer release mis-triggers content filters on legitimate code. The value is passed through to Claude Code verbatim.

**Extended Context (1M):** toggle for the 1M token context window instead of 200K. API subscribers (Team, Enterprise) get this at no additional cost with all models. Max plan users must set all models to Opus — Sonnet 1M is not included in Max. The toggle only applies to the `sonnet` and `opus` aliases; custom model IDs are sent verbatim, so pick the concrete ID for the context window you want.

### Review agents

Two Claude sub-agents run in separate context windows during `/spec`. Each has its own model selector; disabling an agent skips it entirely.

| Agent | Default | Role |
|-------|---------|------|
| **Spec Review** | On | Validates plans before implementation. Checks alignment with requirements, flags risky assumptions. |
| **Changes Review** | On | Reviews code after implementation. Checks compliance, security, test coverage, goal achievement. |

**Codex adversarial reviewers (optional)** — OpenAI Codex agents that provide an independent second opinion.

| Agent | Default | Role |
|-------|---------|------|
| **Codex Spec Review** | Off | Adversarial plan review — second opinion before implementation. |
| **Codex Changes Review** | Off | Adversarial code review — second opinion after implementation. |

### Automation toggles

Three toggles control user interaction points during `/spec`. Disable all three for fully autonomous end-to-end execution.

| Toggle | Default | Enabled | Disabled |
|--------|---------|---------|----------|
| **Worktree Support** | On | Asks how to handle branching at `/spec` start | Skips the branch question — changes go on the current branch |
| **Ask Questions** | On | Asks clarifying questions during planning | Planning makes autonomous default choices |
| **Plan Approval** | On | Requires your approval before implementation starts | Implementation begins automatically after planning |

With all three off, `/spec add user authentication` plans, implements, and verifies the feature end-to-end without checkpoints.

:::warning Token usage in autonomous mode
No checkpoints means Claude executes the entire workflow without asking. Make sure your prompt is specific enough to avoid misinterpretation. You can always interrupt with Escape.
:::

### Config file

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
    "spec-review": "sonnet",
    "changes-review": "sonnet"
  },
  "reviewerAgents": {
    "specReview": true,
    "changesReview": true
  },
  "codexReviewers": {
    "specReview": false,
    "changesReview": false
  },
  "specWorkflow": {
    "worktreeSupport": true,
    "askQuestionsDuringPlanning": true,
    "planApproval": true
  }
}
```

You can edit this file directly — the Settings UI is a convenience wrapper. Changes require a Claude Code restart.
