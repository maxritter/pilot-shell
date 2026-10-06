---
title: Install
description: Download the App, or run one command on a machine without a screen. Updates come through the App.
---

A computer with a screen gets the **QualityLayer App**. A machine without one (WSL2, a dev container, a server) gets the **QualityLayer CLI** and opens the App in a browser.

![One rule: a machine with a screen gets the App, which updates itself; WSL2, dev containers and servers get the command line and open the App in a browser](pathname:///img/diagrams/install-light.svg)
![One rule: a machine with a screen gets the App, which updates itself; WSL2, dev containers and servers get the command line and open the App in a browser](pathname:///img/diagrams/install-dark.svg)

## You need

- **A coding agent:** Claude Code, Codex, or [another agent](agents/other.md) that runs shell commands. Sign in and start it once.
- **macOS, Windows or Linux**, Git and a repository.

## On your computer

**[Download the App](https://qualitylayer.dev/download)** and open it. The first start is one checklist: your licence (or a 7-day trial), the CLI, and your agents. **Open QualityLayer** turns on once one agent is ready.

## Without a screen

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash
```

On Windows, in PowerShell: `irm https://qualitylayer.dev/install.ps1 | iex`. The installer prints a link that opens the App in your browser; over SSH, forward the port it names.

## Updates {#updates}

The App updates itself and the CLI together. When **Update ready** shows in the sidebar, click it and **Restart and update**; you land back on the same page. Without the App, run `qualitylayer update`. What changed is in the [changelog](reference/changelog.md).

## Remove it {#uninstall}

`qualitylayer uninstall` puts back what the installer changed. Your plans stay. `qualitylayer licence activate <key>` moves your licence to another computer.

Coming from Pilot Shell 11? Its updater moves you over by itself; see [From Pilot Shell 11](moving-from-pilot-shell.md).

Next: [your first task](first-task.md).
