---
title: Supported agents
sidebar_label: Supported agents
description: Set up the seven coding agents QualityLayer runs, choose their models, permission modes and reviewers, and control their sessions in the App.
---

# Supported agents {#supported-agents}

QualityLayer runs seven coding agents in the same workflow: **Claude Code**, **Codex**, **Cursor**, **Grok**, **Antigravity**, **Pi** and **OpenCode**. Install your agent, sign in through its own login and start it once. Then run QualityLayer setup. The App and CLI installers add the integration for each agent they find.

Start a task in either place:

- **In the App or browser:** choose **+ New**, pick your agent and describe the change. The task stays on the left; the agent opens in the right sidebar, running as its own program in its own terminal.
- **In your terminal or IDE:** say “Using QualityLayer, plan a CSV export”. **QL** works too, as do requests to implement, verify or continue an existing task.

| Agent | Checked with | What QualityLayer adds |
| --- | --- | --- |
| [Claude Code](https://code.claude.com/docs/en/setup) | 2.1.306 | Skills, lifecycle hooks and its existing prompt integration |
| [Codex](https://developers.openai.com/codex/cli) | 0.163.0 | Skills, implicit invocation policies and lifecycle hooks |
| [Cursor](https://cursor.com/docs/cli/installation) | 2026.10.19 | Skills and turn-end hooks in its own hooks file |
| [Grok](https://docs.x.ai/build/overview) | 1.0.62 | Skills and hooks, in its own hooks folder |
| [Antigravity](https://antigravity.google/docs/getting-started/) | 1.4.4 | Skills, a workflow command and turn-end hooks |
| [Pi](https://pi.dev/docs/latest/quickstart) | 1.2.0 | Skills, a lifecycle extension and fresh helper sessions |
| [OpenCode](https://opencode.ai/docs/) | 2.0.29 | Skills, a command and a lifecycle plugin |

Cursor, Grok and Antigravity are set up only after you have started them once from a terminal.

An ordinary coding request stays an ordinary request. Ask QualityLayer or QL to carry the work; discussing the product or quoting an example does not start a workflow. Other spellings and other languages work.

## The five skills

QualityLayer installs these skills for the supported agents. Ask in plain language; your agent chooses the right one.

| Skill | What it does |
| --- | --- |
| `ql-workflow` | Plan, build, verify and review a change |
| `ql-artifact` | Create and revise mockups, diagrams and clickable pages |
| `ql-manage` | Find tasks and manage memory, sharing, settings and setup |
| `ql-peer` | Coordinate other agent sessions on your computer |
| `ql-quality` | Review code complexity, structure and duplication |

Only workflow requests start a planning and build task. The other skills work on their own. See [Artifacts](../artifacts.md), [Project memory](../memory.md) and [Code health](../reference/code-health.md).

## Models and reviews

Choose the agent, model and effort when you start a task or build. Settings › Workflow keeps the review models and general run controls. Workflow defaults use High effort. Your login and provider settings stay in your agent.

- Pi and OpenCode use provider-qualified model IDs, such as `openai-codex/gpt-6.1-sol` in Pi and `openai/gpt-6.1-sol` in OpenCode.
- Cursor puts effort in the model name, such as Opus 5.5 (High), so it has no separate effort control.

**Second opinion by** selects who reviews. **Other model family** picks an installed, signed-in agent that did not build the change. It prefers a model from a different maker than the builder's: GPT reviews Claude, Claude reviews GPT. You can also name a particular agent for a fresh review.

The reviewer reads files in a separate context and does not edit them. Agents that enforce read-only mode themselves (Claude Code, Codex, Pi, OpenCode, Grok) come first. Cursor and Antigravity are chosen only when nothing better qualifies or when you name them. They cannot be made read-only, so they review a disposable copy of the code under review, deleted afterwards. QualityLayer stops them as soon as they start a tool that is not read-only. Your agent's project hooks may run during a review.

Pi and OpenCode can run the same model as your working agent. **Other model family** compares the model each reviewer would use (Settings › Workflow › Reviewer models). A Pi and an OpenCode that both run GPT count as one family. To get a second family as well as a fresh context, give one of them a model from another maker.

## Sessions in the App or browser

With **In the App**, choose the agent, model, effort, project and branch when you start a task or build. The task’s **Agent** tab holds its conversation. Closing the sidebar keeps the run; **Stop** ends it. If the local runtime cannot start a session, use **In my terminal**.

Every agent runs as its own program in its own terminal. The **Conversation** view reads its session record and shows messages, tool calls and files. **Terminal** shows the program itself. Switch per session, or set the default in Settings › Agents. Some records hold less than others:

| Agent | What its Conversation lacks |
| --- | --- |
| Claude Code, Codex, Pi, OpenCode | Nothing |
| Grok | How full the context is, and permission questions |
| Antigravity | Permission questions |
| Cursor | Thinking, tool output, token counts, how full the context is, and permission questions |

A permission question the Conversation cannot show appears in the Terminal view. Cursor, Grok and Antigravity cannot show a choice list for workflow questions, so each arrives as a numbered list in the chat.

Codex shows QualityLayer's questions in its own choice list outside Plan mode too. The installer turns that on in Codex's settings and keeps a value you set yourself. Codex closes an untouched list after two minutes; pressing any key keeps it open. A closed list comes back as numbered choices in the conversation.

To continue after a crash or in another agent, stop the previous run if it is still active. Then name the same task and stage: “Using QL, continue verification of task retry-webhooks.” The task's approvals, changes and evidence are kept.

In the App you can **Interrupt**, **Stop**, **Resume**, **Move to my terminal** and change settings at a completed turn. One window types at a time. Resume needs the agent's saved state and a cleanly stopped old process. If the conversation is still open in another terminal, the App will not resume it there.

### Permission modes {#permission-modes}

A run starts in your agent's own permission setting. The row under the message box shows it with its source, such as “Claude Code’s settings”, and switches modes. QualityLayer lists the modes the agent really has:

| Agent | Modes |
| --- | --- |
| Claude Code | Auto, Ask first, Accept edits, Bypass |
| Codex | On request, Ask first, Auto review, Full access |
| Cursor | Ask first, Auto-review, Run everything |
| Grok | Auto, Ask first, Accept edits, Bypass |
| Antigravity | Ask first, Accept edits, Auto, Bypass |
| OpenCode | Agent settings, Auto-approve |
| Pi | None; its own tool permissions apply |

A mode that skips every check (Bypass, Full access or Run everything) asks you to confirm each time and cannot be a default. Set the default mode per agent in Settings › Agents. Stopping a run leaves your other sessions alone.

### Plan limits {#plan-limits}

For **Claude Code** and **Codex**, QualityLayer shows how much of each plan window is left and when it resets.

- The sidebar shows each agent's tightest window.
- The row under the message box shows it as a chip, such as **Week · 42 % left**. The chip turns amber only when you use the plan faster than an even pace.
- An agent billed by use (an API key or a gateway) shows the session's cost so far, estimated at list prices. A plan never shows dollars.
- Choose the chip for details. **Settings › Usage** lists every window.

Claude Code's numbers come from its own `/usage` report on your existing login, and Codex's from its session records. QualityLayer never changes your agent's settings or status line to read them. The other agents report no limits, and the App says so.

With **Resume when a limit resets** on, a build that stopped on a plan limit continues when the window resets. It does not resume if someone has typed in the session since. You can cancel it on the task.

## Peer sessions

Ask one agent session to review another's work, hand over a task or discuss a problem. Claude Code, Codex, Pi and OpenCode can coordinate on this computer. [Session messaging commands](../reference/commands.md#session-messaging).

## How QualityLayer finds your agents {#finding-agents}

An agent that shows **Not installed** was not found. Settings › Agents › **Check again** repeats the search. If the agent lives elsewhere, open **⋯ › Edit launch…** and enter the full path in **Command**, for example `/opt/tools/bin/codex`.

<details>
<summary>Search order</summary>

An App opened from the Dock or Finder does not get your terminal's PATH. QualityLayer uses the first match in this order:

1. A command you set in Settings › Agents › **Edit launch…** › **Command**. It is never searched past: if that file cannot run, the agent counts as missing.
2. The App's PATH, then the PATH your login shell prints.
3. The folders agents install to: `~/.local/bin`, `~/.codex/packages/standalone/current/bin`, Homebrew, `~/.npm-global/bin`, Bun, Volta, pnpm, nvm and fnm.
4. npm's global folder.
5. For Codex, the command inside the ChatGPT or Codex desktop app in `/Applications` or `~/Applications`.

The version comes from `--version`, which must name the agent, such as `codex-cli 0.163.0` for Codex. Point at the Version column in Settings › Agents to see the file it found. The New task list and the other pickers show every agent found, signed in or not. A sign-in problem appears in Settings › Agents.

</details>

## Setup and removal

Settings › Agents lists all seven agents with version, sign-in, plan (where the agent reports one) and the state of QualityLayer's integration.

- **Use** turns an agent off for QualityLayer.
- **Install…** appears for an agent that is not installed. It opens the vendor's install page or shows the command for you to run. QualityLayer never runs an installer.
- **Check again** runs a fresh check. A responding version does not prove account access; that is checked when a session starts.
- **⋯** offers **Edit launch…** (command, extra arguments, config folder and default permission mode) and **Repair skill and hooks**.

`qualitylayer agents list` and `qualitylayer agents check` give the same results.

Both installers add skills and lifecycle files to the initialized agents they find. Pi uses `~/.pi/agent`; OpenCode uses `~/.config/opencode`. Configured root overrides are respected. QualityLayer does not replace your authentication or personal model settings.

An update replaces unchanged integration files it owns and retires legacy skill names. Edited legacy files are backed up outside skill discovery, and unrelated custom skills stay. Uninstall keeps your native settings, login, session history and files you edited.

Other coding agents can still [follow the same workflow](other.md) through the CLI.
