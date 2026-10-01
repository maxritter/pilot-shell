---
title: Install
description: What you need, the one install command, and how to update or remove QualityLayer.
---

![Install with one command, start a task with /ql, and review it in the Cockpit](pathname:///img/diagrams/install-light.svg)
![Install with one command, start a task with /ql, and review it in the Cockpit](pathname:///img/diagrams/install-dark.svg)

## What you need

- **A coding agent.** Any agent that supports skills and can run shell commands, in the terminal, its desktop app or its IDE extension. The installer sets up Claude Code and Codex. Sign in to your agent and start it once before you install. The terminal shows you the most: in Claude Code, a status line follows the task.
- **macOS, Linux, or Windows with WSL2**, plus Git and a repository. Nothing else: no Node.js, Python or Bun.

## What it costs your machine

QualityLayer is held to these limits, measured on a Mac with a repository of 20,000 files:

- **The Cockpit page** uses about 20 MB of browser memory, and the amount stays the same through half an hour of constant use. Switching pages never freezes it for more than 60 ms, even with the processor slowed to a quarter of its speed.
- **The Cockpit itself** runs only while you use it, and quits by itself 30 minutes after you close the page, unless a decision is waiting for you. Idle, it uses under 0.2 % of one processor core and about 50 MB. With the page open while your agent works, it uses about 1 % of a core and 100 to 160 MB.
- **Waiting for your approval** costs your agent's session under 0.5 % of one core.
- **Linking Claude Code and Codex sessions** costs under 1 % of one core, for as long as the link is on.
- **The status line** takes about 30 ms each time Claude Code runs it.
- **When you stop**, nothing keeps running: the Cockpit, the wait for your approval and the session link all end with it.

## Install

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash
```

It adds the `qualitylayer` command, the `/ql` skill (`$ql` in Codex) and [session messaging](reference/commands.md#session-messaging). It asks you nothing. It lists every agent setting it adds and keeps any value you set. Your own Claude Code status line stays; `qualitylayer install --refresh --status-line` swaps in QualityLayer's, and uninstalling puts yours back.

QualityLayer runs only when you call it. Everything else works as before.

## Other agents

Copy `~/.qualitylayer/skill/qualitylayer` into your agent's skills folder. At handoff, pick **Other agent** to get its build prompt. The [second opinion](reference/settings.md#second-opinion) and [session messaging](reference/commands.md#session-messaging) need Claude Code and Codex; everything else works with any agent.

## Update, remove and licence {#uninstall}

```bash
qualitylayer update
qualitylayer uninstall
qualitylayer licence activate <key>
```

Uninstalling puts back what the installer changed; your plans stay. The trial lasts seven days. Coming from Pilot Shell 11? Run the installer. It shows one screen about the upgrade, once, then removes Pilot Shell's tools and installs QualityLayer without asking anything. Your licence and plans carry over, and your own agent settings keep working.

Next: [your first task](first-task.md).
