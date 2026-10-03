---
title: Install
description: What you need, the one install command, and how to update or remove QualityLayer.
---

![Install with one command, start a task with /ql, and review it in the Cockpit](pathname:///img/diagrams/install-light.svg)
![Install with one command, start a task with /ql, and review it in the Cockpit](pathname:///img/diagrams/install-dark.svg)

## What you need

- **A coding agent.** Any agent that supports skills and can run shell commands, in the terminal, its desktop app or its IDE extension. The installer sets up Claude Code and Codex. Sign in to your agent and start it once before you install. The terminal shows you the most: in Claude Code, a status line follows the task.
- **macOS, Linux, or Windows**, plus Git and a repository. Nothing else: no separate Node.js, Python or Bun runtime. Native Windows builds support x64 and ARM64 and use PowerShell 5.1 or newer.

Native Windows support is included in the next release. Until it is published, use WSL2 with the Linux installer and run your agent inside WSL2 too.

## What it costs your machine

QualityLayer is held to these limits, measured on a Mac with a repository of 20,000 files:

- **The Cockpit page** uses about 20 MB of browser memory, and the amount stays the same through half an hour of constant use. Switching pages never freezes it for more than 60 ms, even with the processor slowed to a quarter of its speed.
- **The Cockpit itself** runs only while you use it, and quits by itself 30 minutes after you close the page, unless a decision is waiting for you. Idle, it uses under 0.2 % of one processor core and about 50 MB. With the page open while your agent works, it uses about 1 % of a core and 100 to 160 MB.
- **Waiting for your approval** costs your agent's session under 0.5 % of one core.
- **Linking Claude Code and Codex sessions** costs under 1 % of one core, for as long as the link is on.
- **The status line** takes about 30 ms each time Claude Code runs it.
- **When you stop**, nothing keeps running: the Cockpit, the wait for your approval and the session link all end with it.

## Install

On macOS or Linux:

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash
```

On Windows, in PowerShell (available with the next release):

```powershell
irm https://qualitylayer.dev/install.ps1 | iex
```

WSL2 is optional for the Windows build. Run QualityLayer and your coding agent in the same environment: both native Windows, or both inside WSL2. Local session messaging does not cross that boundary.

The Windows installer checks the download's SHA-256 checksum and installs into `%USERPROFILE%\.qualitylayer\bin`. It adds that directory to the current PowerShell session's `PATH` and prints a line you can put in your PowerShell profile for future sessions; it does not edit the profile. In another terminal, you can also run the binary directly:

```powershell
& "$env:USERPROFILE\.qualitylayer\bin\qualitylayer.exe" status
```

It adds the `qualitylayer` command, the `/ql` skill (`$ql` in Codex) and [session messaging](reference/commands.md#session-messaging). It asks you nothing, apart from the migration questions for Pilot Shell users below. It lists every agent setting it adds and keeps any value you set. Your own Claude Code status line stays; `qualitylayer install --refresh --status-line` swaps in QualityLayer's, and uninstalling puts yours back.

QualityLayer runs only when you call it. Everything else works as before.

## Other agents

Copy `~/.qualitylayer/skill/ql` into your agent's skills folder. At handoff, pick **Other agent** to get its build prompt. The [second opinion](reference/settings.md#second-opinion) and [session messaging](reference/commands.md#session-messaging) need Claude Code and Codex; everything else works with any agent.

## Update, remove and licence {#uninstall}

```bash
qualitylayer update
qualitylayer uninstall
qualitylayer licence activate <key>
```

Uninstalling puts back what the installer changed; your plans stay. The trial lasts seven days.

## Coming from Pilot Shell 11

Run the installer. It shows one screen about the change, once. In a terminal it then asks before anything of Pilot Shell's goes:

1. **What moving over removes.** A list: Pilot's own files in `~/.claude`, its entries in your agent settings (restored from Pilot's own baselines, so your values stay), its block in your shell profile, its Codex parts and its runtime in `~/.pilot`. Your own settings, skills and files stay. You confirm, or nothing is changed.
2. **Which tools Pilot Shell installed should go too.** Only the tools Pilot recorded as its own are listed, and you tick the ones to remove. Our benchmarks show today's models gain nothing from rtk, semble or codegraph, so those start ticked. General tools such as typescript, prettier or ruff, and design tools such as Impeccable, start unticked, because your projects may use them. A tool you leave unticked stays installed and is yours.
3. **Delete your Pilot Shell memories (`~/.pilot/memory`)?** QualityLayer does not use them, and the answer is no unless you say otherwise. To keep what is in them, ask Claude Code or Codex to move them into its own memory first; QualityLayer does not do that for you. Sessions, logs and configuration in `~/.pilot` stay either way.

Your plans carry over. The summary at the end says what happened to your licence: a paid Pilot Shell licence keeps working, and without one (a Pilot Shell trial does not carry over) a 7-day QualityLayer trial starts.

Without a terminal, including Pilot Shell 11's own updater and `--non-interactive`, nothing is asked: Pilot's own parts are removed, no tool and no memory is, and the summary lists each tool that stayed with the command that removes it.

Next: [your first task](first-task.md).
