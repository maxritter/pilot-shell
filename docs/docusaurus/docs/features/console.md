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

## 10 Views

Each view that supports project filtering has an inline **Project Filter** dropdown next to the title — switch projects without leaving the page. The **Dashboard** shows stats across all projects with clickable tiles that navigate to the relevant view.

| View | Description |
|------|-------------|
| **Dashboard** | Global command center — 8 clickable stat cards (Projects, Sessions, Active, Memories, Extensions, Requirements, Specifications, Changes), plus 4 recent cards (Specifications, Requirements, Sessions, Memories) with "Show all" links. Active specs shown as pills in the top bar, notification bell in the top right. |
| **Sessions** | Browse past sessions with search. Copy the session ID and use `/resume <session-id>` to jump back in. |
| **Memories** | Browsable observations — decisions, discoveries, bugfixes — with type filters and search. Each memory shows which session it belongs to — click the session label to navigate directly to it. |
| **Requirements** | PRD documents with view/annotate modes. Selected shown as a tab, others in a Previous dropdown. |
| **Specifications** | All spec plans with task progress (checkboxes), phase tracking (PENDING/COMPLETE/VERIFIED), and iteration history. Selected shown as a tab, others in a Previous dropdown. |
| **Extensions** | All extensions — local, plugin, and remote — with team sharing via git (push, pull, diff), color-coded categories, and scope filtering. |
| **Changes** | Git diff viewer with staged/unstaged files, branch info, worktree context, spec task correlation, and inline code review. |
| **Usage** | Daily token costs, model routing breakdown (Opus vs Sonnet distribution), and usage trends over time. |
| **Help** | Embedded documentation from pilot-shell.com — full technical reference without leaving the Console. |
| **Settings** | Model selection per command and sub-agent. Spec workflow toggles. Reviewer toggles and optional Codex adversarial reviewers. Extended context (1M) toggle with pricing info. |

### Session Resume

The Sessions tab shows the Claude Code session ID for each session with a **copy-to-clipboard** button. Use this ID to resume any past session:

```bash
/resume <session-id>
```

This lets you pick up exactly where you left off — all context, files, and conversation history are restored.

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

### Spec Task Correlation

When a `/spec` task is active (PENDING or COMPLETE), the Changes tab automatically correlates each changed file with the spec task that touched it. This gives you instant traceability — if something looks wrong in a diff, you know exactly which task in the spec caused the change.

**How it works:**

- Each file in the file list shows a **T{N}** badge (e.g., `T1`, `T3`) linking it to the corresponding spec task
- Hover over the badge to see the full task name
- Click the **Spec** button in the file list header to switch to **group-by-spec** view — files are organized by spec name and task number, so you can review changes task by task
- Correlation is parsed from the `**Files:**` section in each spec task, so it works automatically with any spec that follows the standard format

This is especially useful when reviewing multi-task specs: instead of scrolling through a flat list of changed files, group by spec to see exactly which files belong to each task and review them in context.

### Spec Sharing

Share specifications with teammates for collaborative review — no cloud service required. Everything works entirely locally with compressed URLs.

**Sharing a spec:**

1. Open a spec in the Specifications tab
2. Click **Share with Teammate** in the metadata row
3. A share URL is generated — the spec content and your annotations are compressed and encoded in the URL fragment (never sent to any server)
4. Copy the URL and send it to your colleague via Slack, email, or any channel
5. The **Receive Feedback** dialog opens automatically so you're ready to import their response

**Reviewing shared specs:**

1. Your colleague opens the URL in their Pilot Console (`localhost:41777`)
2. They see the full spec with your annotations displayed as read-only highlights
3. They can add their own feedback — either by selecting text or clicking the **+** button on any block
4. Click **Send Feedback** to generate a feedback URL and copy it to clipboard

**Importing feedback:**

1. Click **Receive Feedback** on the original spec
2. Paste the feedback URL — a preview shows the incoming annotations
3. Import adds annotations with `pending` status to your annotation panel
4. **Accept** or **Reject** each annotation individually, or use **Accept All** / **Reject All**
5. The view auto-switches to Annotate mode so you see the imported feedback immediately

**Deduplication:** Importing the same feedback twice is safe — annotations matching existing ones (same text and selection) are automatically skipped.

**Privacy:** All shared data lives in the URL fragment, which per the HTTP spec is never sent to any server — no data reaches pilot-shell.com or any third party. For specs larger than ~32KB compressed, an embedded paste service stores the compressed data locally in `~/.pilot/share/` with automatic 3-day expiry.

:::tip Both annotation methods work everywhere
The **+** button on each block and text selection both work on the normal review page and the shared spec feedback page. Use whichever is more convenient — the **+** button is more reliable for quick block-level comments.
:::

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

Toggle for using the 1M token context window instead of 200K. API subscribers (Team, Enterprise) get this at no additional cost with all models. Max plan users must set all models to Opus for 1M to work — Sonnet 1M is not included in Max.

### Spec Workflow

#### Review Agents

Two independent sub-agents that run in separate context windows during `/spec`:

| Agent | Default | Description |
|-------|---------|-------------|
| **Spec Review** | On | Validates plans before implementation. Checks alignment with requirements and flags risky assumptions. |
| **Changes Review** | On | Reviews code after implementation. Checks compliance, security, test coverage, and goal achievement. Reads all changed files. |

Each agent has its own model selector (Sonnet or Opus). Disabling an agent skips it entirely — no tokens consumed.

#### Codex Reviewers (Optional)

Adversarial review agents powered by OpenAI Codex that provide an independent second opinion:

| Agent | Default | Description |
|-------|---------|-------------|
| **Codex Spec Review** | Off | Adversarial plan review — provides an independent second opinion on plans. |
| **Codex Changes Review** | Off | Adversarial code review — provides an independent second opinion on implementations. |

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

You can edit this file directly — the Console Settings UI is a convenience wrapper. Changes require a Claude Code restart to take effect.
