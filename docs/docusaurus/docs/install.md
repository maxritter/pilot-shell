---
title: Install
description: What you need, the one install command, and how to update or remove QualityLayer.
---

![Install with one command, start a task with /ql, and review it in the Cockpit](pathname:///img/diagrams/install-light.svg)
![Install with one command, start a task with /ql, and review it in the Cockpit](pathname:///img/diagrams/install-dark.svg)

## What you need

- **A coding agent.** Any agent that supports skills and can run shell commands, in the terminal, its desktop app or its IDE extension. The installer sets up Claude Code and Codex. Sign in to your agent and start it once before you install. The terminal shows you the most: in Claude Code, a status line follows the task.
- **macOS, Linux, or Windows with WSL2**, plus Git and a repository. Nothing else: no Node.js, Python or Bun.

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
