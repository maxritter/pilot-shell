---
sidebar_position: 8
title: Pilot Console
description: Local Pilot Console at localhost:41777 - monitor sessions, browse memories, manage extensions, view diffs, track usage, and control Pilot from the browser.
---

# Pilot Console

Local 11-view dashboard at `localhost:41777` - monitor and manage Claude Code and Codex sessions.

The Console runs locally as a Bun/Express server with a React web UI. It starts when you launch Pilot and stops when all sessions close. All data - memories, sessions, usage - lives in a local SQLite database, and Pilot never transmits it anywhere. Team plans can additionally share a project's memories with teammates by storing them in the project repository, where git carries them - see [Team Memories](./team-memories.md).

```bash
$ open http://localhost:41777
```

:::tip Custom port
The default port `41777` is configurable. Open the **Settings** tab and edit the **Console -> Worker Port** field, then click **Save Port** (or edit `CLAUDE_PILOT_WORKER_PORT` in `~/.pilot/memory/settings.json` directly). Restart your `claude` or `codex` session for the change to take effect.
:::

## Views

Each view that supports project filtering has an inline **Project Filter** dropdown next to the title. The **Dashboard** shows stats across all projects with clickable tiles that navigate to the relevant view. Its recent cards give equal space to session/memory activity and Pilot's durable workflow artifacts.

| View | Description |
|------|-------------|
| **Dashboard** | Global command center - 8 stat cards (Projects, Sessions, Memories, Cost Today, Requirements, Specifications, Buildouts, In Progress) and 4 recent-item cards (Sessions, Memories, Specifications, Buildouts), plus active-work pills and notifications in the top bar. |
| **Sessions** | Browse past sessions with search. Copy a session ID and run `/resume <session-id>` in Claude Code to jump back in (Claude Code only). |
| **Memories** | Observations (decisions, discoveries, bugfixes) with type filters and search. Each memory links back to the session it came from. Hosts the **Team Sharing** card - see [Team Memories](./team-memories.md). |
| **Requirements** | PRD documents with view/annotate modes. Selected opens as a tab, others live in a Previous dropdown. |
| **Buildouts** | [`/build`](../workflows/build.md) goal-and-loop runs, in their own section: the goal and its oracle, the acceptance criteria the judge rules each round, the task list as it evolved, and the round log. Phase tracking reads `goal` -> `build` -> `judge`, and the repeat counter counts rounds rather than iterations. Same annotation and sharing surfaces as Specifications - and because a `/build` run never stops to ask, annotating a Buildout is how you steer one in flight: it folds them in at the top of every round. |
| **Specifications** | Spec plans with task progress, phase tracking (PENDING/COMPLETE/VERIFIED), and iteration history. Hosts Plan Annotation and Spec Sharing (below). |
| **Extensions** | All extensions - local, plugin, remote - with team sharing via git (push, pull, diff), color-coded categories, and scope filtering. |
| **Changes** | Git diff viewer with staged/unstaged files, branch info, worktree context. Hosts Code Review and Spec Task Correlation (below). |
| **Usage** | Daily token costs, model routing breakdown (Opus vs Sonnet), and usage trends. |
| **Settings** | Workflow toggles for `/spec`, `/fix` and `/build` (branch isolation, ask questions, plan approval, verification pass), the Model Switching mode, and the review agents. See [Settings](#settings) below. |
| **Documentation** | Embedded pilot-shell.com documentation - full technical reference without leaving the Console. |

## Plan Annotation

When a spec plan is in the planning phase (PENDING, not yet approved), the Specifications tab auto-opens in **Annotate mode**. Toggle between View and Annotate using the control next to the "Specifications" heading.

Select any passage and write a free-text note in the popover that appears - no type selection, no submit button. Annotations save immediately and appear in the sidebar panel, where you can edit or delete them.

When the agent reaches the approval checkpoint, it reads your annotations directly from the Console, incorporates every note into the plan, and asks for approval again. Just write your notes and say "ready" when done.

## Code Review

After a spec completes automated verification, the agent prompts you to review the code changes. Switch to the **Changes** tab and enable **Review mode** using the toggle next to the "Changes" heading.

In Review mode, a **+** button appears on hover for every diff line. Click it to open an inline annotation form - write your note and press Save. Annotations appear in a panel at the bottom of the diff viewer.

The agent reads your code-review annotations directly from the Console before marking the spec verified. Say "fix" to have it address them, "approve" to mark the spec as verified. Annotations persist across page reloads, so you can review asynchronously while the agent runs verification in the background.

## Spec Task Correlation

When a `/spec` task is active, the Changes tab correlates each changed file with the spec task that touched it - instant traceability.

- Each file in the file list shows a **T{N}** badge (e.g., `T1`, `T3`) linking it to the matching spec task
- Hover the badge for the full task name
- Click the **Spec** button to switch to **group-by-spec** view - files organized by spec name and task number
- Correlation is parsed from the `**Files:**` section of each task, so any spec following the standard format works automatically

Especially useful for multi-task specs: instead of scrolling a flat file list, review changes task by task.

## Spec Sharing

Share specs with teammates for collaborative review - no cloud service required. Everything works locally with compressed URLs.

**Share:**

1. Open a spec, click **Share with Teammate** in the metadata row
2. A share URL is generated - the spec content and your annotations are compressed into the URL fragment (per the HTTP spec, fragments are never sent to any server)
3. Copy the URL and send it via Slack, email, or any channel
4. The **Receive Feedback** dialog opens automatically so you're ready for their response

**Review a shared spec:**

1. Your colleague opens the URL in their Pilot Console
2. They see your spec and annotations as read-only highlights
3. They add their own feedback via text selection or the **+** button on any block
4. Click **Send Feedback** to generate a feedback URL

**Import feedback:**

1. Click **Receive Feedback** on the original spec
2. Paste the URL - a preview shows the incoming annotations
3. **Accept** or **Reject** each annotation individually, or use **Accept All** / **Reject All**

Importing the same feedback twice is safe - annotations matching existing ones are skipped. For specs larger than ~32KB compressed, an embedded paste service stores the data locally in `~/.pilot/share/` with 3-day auto-expiry.

:::tip Both annotation methods work everywhere
The **+** button and text selection both work on the normal review page and on shared feedback pages. The **+** button is more reliable for quick block-level comments.
:::

## Notifications

The Console sends real-time alerts via Server-Sent Events when your agent needs input or a significant phase completes - no need to watch the terminal.

- Plan requires your approval - review and respond
- Spec phase completed - implementation done, verification starting
- Clarification needed - the agent is waiting for design decisions
- Session ended - completion summary with observation count

## Settings

The Settings tab (`localhost:41777/#/settings`, or your custom port) is a single scrollable page with two stacked sections: **Workflows** and **Console**. Workflows holds three groups - Model Switching, Automation, and Reviews - and a collapsed Worktrees block. A scope chip on each control says which workflows it affects, so there is no per-workflow split. Toggle preferences save to `~/.pilot/config.json`. The **Console -> Worker Port** field saves to `~/.pilot/memory/settings.json` and lets you move the Console off `41777` if it conflicts with another service. Both changes take effect after restarting your session.

:::info Model selection lives in the agent
Pilot doesn't manage model preferences. Set the model with Claude Code's `/model` command or Codex's `codex --model <name>` / `~/.codex/config.toml`. See [Model Routing](./model-routing.md).
:::

### Workflows -> Review Agents

Three named review passes are available across the workflows on Claude Code and Codex: **Spec Review** during `/spec`, **Build Review** during `/build`, and **Changes Review** at the end of `/spec`, `/fix` and a code `/build`. Toggle each on or off. Each configured pass launches one named reviewer - a sub-agent on Claude Code, a managed custom agent under `~/.codex/agents/` on Codex. That describes the cost of the configured pass only; it does not limit the active workflow from spawning, resuming, or nesting additional agents autonomously.

| Agent | Group | Default | Role |
|-------|-------|---------|------|
| **Spec Review** | Reviews | On | Validates plans before implementation. Checks alignment with requirements, flags risky assumptions. |
| **Build Review** | Reviews | On | Audits a `/build`'s drafted tasks and acceptance criteria before the loop starts, catching criteria a judge could not decide from the finished artifact. |
| **Changes Review** | Reviews | On | Reviews the diff after `/spec` implementation, after `/fix`, and at a code `/build`'s hand-back - one toggle covers all three. Hunts bugs, security issues, and cleanups; plan compliance and goal achievement stay covered on both agents (inline workflow audit on Claude Code, the native agent's own pass on Codex). |

:::info Want a deeper review? Run `/code-review` yourself
Claude Code's built-in `/code-review` skill is a much larger multi-agent sweep, and it is **user-invocable only** - the flag `disable-model-invocation` means no workflow can launch it on your behalf. Pilot used to offer it as a Changes Review "mode"; that option is gone, because the call was rejected at runtime and the workflow silently ended up with no review at all. Type `/code-review` in your session whenever a change warrants the deeper pass.
:::

**Codex second opinion (optional, Claude Code only).** Each reviewer card carries an **Also review with Codex** switch. It is independent of the native reviewer - you can run either, both, or neither - and needs the Claude Code Codex plugin, so it is disabled until that is installed. All three default to off.

### Workflows -> Automation (build)

| Toggle | Default | Enabled | Disabled |
|--------|---------|---------|----------|
| **Verification Pass** | On | Before hand-back, `/build` runs the full test suite, type checker, linter, build, a live-target E2E pass, the changes review, documentation sync, and a final regression - scaled to the artifact, so a prose build pays almost nothing. It is what `VERIFIED` is measured against on a run nobody supervised | The run **cannot reach `VERIFIED`**. It is judged on its acceptance criteria alone, ends `COMPLETE`, and the hand-back report leads with the fact that nothing checked the code behind them |

### Workflows -> Automation

Three toggles control user interaction points, plus the Model Switching mode during `/spec`. **Ask Questions** and **Branch Isolation** apply to `/spec`, `/fix` and `/build` alike; **Plan Approval** covers `/spec`'s plan gate and `/fix`'s end-of-flow confirmation, and is not read by `/build` — a Buildout has no approval gate to switch off, because [`/build` runs autonomously](../workflows/build.md#it-runs-on-its-own) once its goal is clear. Disable them for fully autonomous execution.

| Toggle | Default | Enabled | Disabled |
|--------|---------|---------|----------|
| **Branch Isolation** | On | Asks how to isolate `/spec` changes (new branch or worktree) | Always works on the current branch |
| **Ask Questions** | On | Asks clarifying questions during planning | Planning makes autonomous default choices |
| **Plan Approval** | On | Requires your approval before implementation starts | Implementation begins automatically after planning |
| **Model Switching** *(Claude Code only; own Settings block with three mode cards)* | Manual | **Manual** (default for new installs): you drive `/model` yourself -- `/spec` runs start to finish on whatever model is active, and never pauses to ask you to switch. **Automated**: `/spec` runs on `opusplan` (Opus 5 plans, Sonnet 5 executes, switched natively; requires `/model opusplan`). **Off**: no model management at all. Upgrading from an older Pilot keeps the mode your old ON/OFF toggle mapped to. See [Model Routing](model-routing). | n/a -- pick one of the three modes |

With all three workflow toggles off, `/spec add user authentication` plans, implements, and verifies the feature end-to-end without checkpoints, entirely on your active model.

### Workflows -> Worktrees

Two fields control where `/spec` creates its isolated worktrees and how long it waits for git. Leave either blank to use the default. Both are global (they apply to every project) and can be overridden per shell with `PILOT_WORKTREE_DIR` / `PILOT_WORKTREE_TIMEOUT`.

| Field | Default | What it does |
|-------|---------|--------------|
| **Location** | `.worktrees` | Directory worktrees are created in. A relative value resolves against the project root (`../worktrees` puts them beside the repo); an absolute value (`~/pilot-worktrees`) keeps them off the repo entirely, which stops IDE indexers and file watchers from walking a second full checkout. Only a location *inside* the repo is added to `.gitignore` - anywhere else is not the repo's to ignore. |
| **Git Timeout** | `300` seconds | How long a single git call during a worktree operation may run before Pilot treats it as wedged. `git worktree add` materialises a full checkout, so large monorepos need more than a short budget. Raise it if worktree creation reports a timeout. |

The Console keeps up with a relocated location: specs living in the configured directory still appear in the Specifications view.

:::warning Token usage in autonomous mode
No checkpoints means your agent executes the entire workflow without asking. Make sure your prompt is specific enough to avoid misinterpretation. You can always interrupt with Escape.
:::

### Config file

All settings are stored in `~/.pilot/config.json`:

```json
{
  "reviewerAgents": {
    "specReview": true,
    "changesReview": true,
    "buildReview": true
  },
  "codexReviewers": {
    "specReview": false,
    "changesReview": false,
    "buildReview": false
  },
  "specWorkflow": {
    "branchIsolation": true,
    "askQuestionsDuringPlanning": true,
    "planApproval": true,
    "modelSwitchMode": "manual",
    "worktreeDir": "../worktrees",
    "worktreeTimeout": 900
  },
  "buildWorkflow": {
    "verification": true
  }
}
```

`worktreeDir` and `worktreeTimeout` are optional - omit them (the Settings UI removes the key when you clear the field) to get `.worktrees` and 300 seconds.

A `codeReview` section from an older Pilot is obsolete - it selected a Changes Review mechanism that no longer exists. It is removed automatically on upgrade, and ignored in the meantime.

You can edit `~/.pilot/config.json` directly - the Settings UI is a convenience wrapper. Changes take effect after restarting your session.
