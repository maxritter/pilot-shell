---
title: Install
description: One rule for every machine, the download and the terminal installer, what first start sets up, and how to remove QualityLayer.
---

One rule decides what you get. A machine with a screen gets the QualityLayer App. A machine without one gets the command line and opens the App in a browser.

![One rule: a machine with a screen gets the App, which updates itself; WSL2, dev containers and servers get the command line and open the App in a browser](pathname:///img/diagrams/install-light.svg)
![One rule: a machine with a screen gets the App, which updates itself; WSL2, dev containers and servers get the command line and open the App in a browser](pathname:///img/diagrams/install-dark.svg)

| Where you work | Install | Update |
| --- | --- | --- |
| macOS (Intel, Apple silicon), Windows, Linux desktop | Download the App from [qualitylayer.dev/download](https://qualitylayer.dev/download) and open it. First start sets up the command line, your agents and your licence. Or run the terminal installer, which does the same and fetches the App | The App updates itself and its command line together. It checks daily, downloads in the background and shows **Update ready** in the sidebar. On Windows it waits for running agent commands. `qualitylayer update` hands over to the App |
| WSL2 | The terminal installer inside WSL: command line only. Links open in your Windows browser | `qualitylayer update` |
| VS Code dev container | The terminal installer in the container: command line only. VS Code forwards the printed link | `qualitylayer update` |
| Linux server | The terminal installer over SSH: command line only. Forward the port and open the printed link. You pair the browser once; links carry no key | `qualitylayer update` |
| Pilot Shell 11, any of the above | Nothing to do. Pilot's updater runs the installer, which moves the machine over by the same rule | As above |

More on [updating](updating.md) and on [moving from Pilot Shell 11](moving-from-pilot-shell.md).

## What you need

- **A coding agent.** Claude Code or Codex, in the terminal, its desktop app or its IDE extension. Sign in and start it once before you install.
- **macOS, Windows or Linux**, plus Git and a repository. Nothing else: no separate Node.js, Python or Bun. Windows runs on x64 and ARM64, without WSL.

## The terminal installer

On macOS, Linux, WSL2, a dev container or a server:

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash
```

On Windows, in PowerShell:

```powershell
irm https://qualitylayer.dev/install.ps1 | iex
```

The first line of its output names what it found, such as "macOS, Apple silicon, with a screen" or "over SSH, no screen". It checks the release's signature and every download's checksum before it installs anything, and needs `ssh-keygen` for the signature, which macOS, Linux and Windows' OpenSSH client include. `--cli-only` installs only the command line on a desktop, and `--with-app` installs the App where the installer found no screen. In PowerShell the first one is `-CliOnly`.

Windows may show a SmartScreen notice when you open the App for the first time. The download page says what to expect.

## First start

The App opens a setup page the first time. It is one checklist and one main button:

- **Licence:** enter your key, or the 7-day trial starts by itself.
- **Command line:** placed where your agents call it, so Claude Code and Codex reach it without a terminal. **Where it lives** shows the path.
- **Your agents:** **Claude Code** and **Codex**, found even when your shell's path does not list them. Codex may need one step: allow QualityLayer once in Codex, with `/hooks` (there is a **Copy** button). You can finish Codex later. **Another coding agent** is one more row: any agent that runs shell commands can use QualityLayer, and **How to connect it** opens [How to connect another coding agent](agents/other.md).

**Check again** finds an agent you installed since. **Open QualityLayer** opens the App. On a computer with no agent found, the page says what to install, and **Open QualityLayer** stays disabled until one agent is ready.

Setup keeps any value you set yourself. QualityLayer sets no Claude Code status line. If an earlier version set one, setup puts yours back.

QualityLayer runs only when you call it. Everything else works as before.

When the trial has ended, the App says so. Your plans and tasks stay where they are, and the workflow goes on once a licence is active.

## Other agents

Any other agent works as well; see [How to connect another coding agent](agents/other.md). The [second opinion](reference/settings.md#second-opinion) needs Claude Code and Codex both. [Session messaging](reference/commands.md#session-messaging) works between any Claude Code and Codex sessions.

## Remove it, or move your licence {#uninstall}

```bash
qualitylayer uninstall
qualitylayer licence activate <key>
```

Uninstalling puts back what the installer changed. Your plans stay. `licence activate` moves your licence to another computer.

Next: [your first task](first-task.md).
