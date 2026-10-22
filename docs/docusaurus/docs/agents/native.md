---
title: Supported agents
sidebar_label: Supported agents
description: Set up the seven coding agents QualityLayer runs, choose their models, permission modes and reviewers, and control their sessions in the App.
---

# Supported agents {#supported-agents}

QualityLayer connects seven coding agents to the same workflow: **Claude Code**, **Codex**, **Cursor**, **Grok**, **Antigravity**, **Pi** and **OpenCode**. Install your agent, sign in through its own login and start it once, then run QualityLayer setup. The App and CLI installers add the integration for each agent they find.

In the App or browser, choose **+ New**, pick your agent and describe the change. The task stays on the left and its agent opens in the right sidebar, running as its own program in its own terminal.

In your own terminal, VS Code or another IDE, say “Using QualityLayer, plan a CSV export”. The same wording works with **QL** and requests to implement, verify or continue an existing task.

| Agent | Checked with | What QualityLayer adds |
| --- | --- | --- |
| [Claude Code](https://code.claude.com/docs/en/setup) | 2.1.306 | Skills, lifecycle hooks and its existing prompt integration |
| [Codex](https://developers.openai.com/codex/cli) | 0.163.0 | Skills, implicit invocation policies and lifecycle hooks |
| [Cursor](https://cursor.com/docs/cli/installation) | 2026.10.19 | Skills and turn-end hooks in its own hooks file |
| [Grok](https://docs.x.ai/build/overview) | 1.0.62 | Skills and hooks, in its own hooks folder |
| [Antigravity](https://antigravity.google/docs/getting-started/) | 1.4.4 | Skills, a workflow command and turn-end hooks |
| [Pi](https://pi.dev/docs/latest/quickstart) | 1.2.0 | Skills, a lifecycle extension and fresh helper sessions |
| [OpenCode](https://opencode.ai/docs/) | 2.0.29 | Skills, a command and a lifecycle plugin |

Cursor, Grok and Antigravity are set up only after you have started them once from a terminal. An ordinary coding request stays an ordinary request. Ask QualityLayer or QL to carry the work; merely discussing the product or quoting an example does not start a workflow. Natural wording, clear spelling variants and requests in other languages are supported.

## The five skills

QualityLayer installs these skills for the supported agents. Ask in plain language; your agent chooses the right one.
| Skill | What it does |
| --- | --- |
| `ql-workflow` | Plan, build, verify and review a change |
| `ql-artifact` | Create and revise mockups, diagrams and clickable pages |
| `ql-manage` | Find tasks and manage memory, sharing, settings and setup |
| `ql-peer` | Coordinate other agent sessions on your computer |
| `ql-quality` | Review code complexity, structure and duplication |

Only workflow requests start a planning/build task. The other skills can work on their own. See [Artifacts](../artifacts.md), [Project memory](../memory.md) and [Code health](../reference/code-health.md).

## Models and reviews

Choose the agent, model and effort when starting a task or build. Settings › Workflow keeps the review models and general run controls. Pi and OpenCode use provider-qualified model IDs, such as `openai-codex/gpt-6.1-sol` in Pi and `openai/gpt-6.1-sol` in OpenCode. Cursor puts the effort inside the model name, such as Opus 5.5 (High), so it has no separate effort control. Workflow defaults use High effort; your native login and provider settings stay in your agent.

**Second opinion by** selects who reviews. **Other model family** chooses an installed agent that is not signed out and did not build the change, preferring one whose model comes from a different maker than the building session's (GPT reviews Claude, Claude reviews GPT). Among those, an agent whose read-only mode it enforces itself (Claude Code, Codex, Pi, OpenCode, Grok) comes before Cursor and Antigravity, which are chosen only when nothing better qualifies or when you name them. You can also choose a particular agent for a fresh review. The reviewer inspects files in a separate context and does not edit them. Cursor and Antigravity cannot be made read-only, so they review a disposable copy of exactly what is under review, made in QualityLayer's folder and deleted afterwards, and QualityLayer stops them the moment they start a tool that is not read-only. Your agent's project hooks may run during a review, as they do for Claude Code in print mode.

Pi and OpenCode can run the same model as your working agent. **Other model family** looks at the model each reviewer would use (Settings › Workflow › Reviewer models), so a Pi and an OpenCode that both run GPT count as one family. Give one of them a model from another maker when you want a second family as well as a fresh context.

## Sessions in the App or browser

With **In the App**, choose the agent, model, effort, project and branch when you start a task or build. The task’s **Agent** tab holds its conversation in QualityLayer. Closing the sidebar keeps the run; **Stop** ends it. If the local runtime cannot start a session, use **In my terminal**.

Every agent keeps running as its own program in its own terminal. The **Conversation** view reads what it writes to its session record and shows messages, tool calls and files; **Terminal** shows the program itself. Switch per session, or choose the default in Settings › Agents. Some records hold less than others:

| Agent | What its Conversation lacks |
| --- | --- |
| Claude Code, Codex, Pi, OpenCode | Nothing |
| Grok | How full the context is, and permission questions |
| Antigravity | Permission questions |
| Cursor | Thinking, tool output, token counts, how full the context is, and permission questions |

A permission question that the Conversation cannot show appears in the Terminal view. Cursor, Grok and Antigravity cannot show a choice list for workflow questions, so each one arrives as a numbered list in the chat.

Codex shows its choice list outside Plan mode because the installer adds `[features] default_mode_request_user_input = true` to `~/.codex/config.toml`. A value you set yourself stays. Codex closes an untouched list after two minutes; press any key in the list and it stays open until you answer. A list that closed without an answer comes back as a numbered list in the chat.

To continue after a crash or in another agent, stop the previous run if it is still active, then name the same task and intended stage: “Using QL, continue verification of task retry-webhooks.” Keep the task's recorded approvals, changes and evidence; the CLI resolves ownership before work resumes.

The App records the native conversation, accepts one typing controller and offers Interrupt, Stop, Resume, Move and settings changes at a completed turn. Resume requires saved native state and verified process cleanup. If the conversation is still open in another terminal, the App refuses to resume it there.

### Permission modes {#permission-modes}

A run starts in your agent's own permission setting, and the footer row under the message box shows it with its source, such as “Claude Code’s settings”. Switch to another mode from that row. QualityLayer lists the modes the agent really has:

| Agent | Modes |
| --- | --- |
| Claude Code | Auto, Ask first, Accept edits, Bypass |
| Codex | On request, Ask first, Auto review, Full access |
| Cursor | Ask first, Auto-review, Run everything |
| Grok | Auto, Ask first, Accept edits, Bypass |
| Antigravity | Ask first, Accept edits, Auto, Bypass |
| OpenCode | Agent settings, Auto-approve |
| Pi | None; its own tool permissions apply |

A mode that skips every check (Bypass, Full access or Run everything) asks you to confirm each time you choose it, and cannot be set as a default. Set the default mode per agent in Settings › Agents. Stopping a run in QualityLayer leaves your other sessions alone.

### Plan limits {#plan-limits}

For **Claude Code** and **Codex**, QualityLayer shows how much of each plan window is left and when it resets. The sidebar shows the window with the least left for each agent. The footer under the message box shows the agent's tightest window as a chip, such as **Week · 42 % left**, which turns amber only when you use the plan faster than an even pace. For an agent billed by use, on an API key or through a gateway, the chip shows what the session has cost so far as an estimate at list prices; a plan never shows dollars. Choose the chip for the usage details; **Settings › Usage** lists every window. Claude Code's numbers come from its own `/usage` report on your existing login, and Codex's from its session records. QualityLayer never changes your agent's settings or status line to read them. The other agents report no limits, and the App says so.

With **Resume when a limit resets** on, a build that stopped on a plan limit continues by itself when the window resets. It only does so if nobody has typed in the session since. You can cancel it on the task.

## Peer sessions

Ask one agent session to review another's work, hand over a task or discuss a problem. Claude Code, Codex, Pi and OpenCode can coordinate on this computer. [Session messaging commands](../reference/commands.md#session-messaging).

## How QualityLayer finds your agents {#finding-agents}

An App opened from the Dock or Finder does not get your terminal's PATH, so QualityLayer looks in this order and uses the first match:

1. A command you chose in Settings › Agents › **Edit launch…** › **Command**. It is never searched past: if that file cannot run, the agent counts as missing.
2. The PATH of the App, then the PATH your login shell prints.
3. The folders agents install to: `~/.local/bin`, Codex's standalone folder `~/.codex/packages/standalone/current/bin`, Homebrew, `~/.npm-global/bin`, Bun, Volta, pnpm, and the folders of nvm and fnm.
4. npm's global folder, asked the way your login shell would.
5. For Codex, the command inside the ChatGPT or Codex desktop app in `/Applications` or `~/Applications`.

The agent's version comes from `--version`, which must name the agent: `codex-cli 0.163.0` for Codex, `… (Claude Code)` for Claude Code. An install that starts with `#!/usr/bin/env node` is asked with its own folder first on the PATH, because its `node` sits beside it.

The Version column in Settings › Agents shows the file it found when you point at it. An agent QualityLayer does not find shows **Not installed**; **Check again** repeats the search. If it is installed somewhere else, open **⋯ › Edit launch…** and enter the full path in **Command**, for example `/opt/tools/bin/codex`. The New task agent list and the other pickers show every agent found this way, whether or not it is signed in; a sign-in problem appears in Settings › Agents instead of hiding the agent.

## Setup and removal

Settings › Agents lists all seven agents with their version, sign-in and plan where the agent reports one, and the state of QualityLayer's integration. A **Use** switch lets you turn an agent off for QualityLayer. An agent that is not installed offers **Install…**, which opens the vendor's install page or shows the command for you to run; QualityLayer never runs an installer. **Check again** runs a fresh check. The **⋯** menu offers **Edit launch…** (the command, extra arguments, config folder and default permission mode) and **Repair skill and hooks**. A responding version does not prove account access, which is checked when a session starts. The same results are available through `qualitylayer agents list` and `qualitylayer agents check`.

Both QualityLayer installers add skills and lifecycle files to the initialized agents they discover. Pi uses `~/.pi/agent`; OpenCode uses `~/.config/opencode`. Their configured root overrides are respected. QualityLayer does not replace their authentication or personal model settings.

An update replaces unchanged integration files it owns and retires its legacy skill names. Edited legacy files are backed up outside skill discovery, so they do not activate alongside the new names. Unrelated custom skills stay. Uninstall preserves your native settings, login and session history, along with files you edited.

Other coding agents can still [follow the same workflow](other.md) through the CLI.
