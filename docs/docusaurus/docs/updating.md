---
title: Updating
description: How the App updates itself and its command line, and how a command-line-only machine updates.
---

![Updating the App: it checks daily, asks you in the tray, waits for running agent commands on Windows, and replaces the App and its command line together](pathname:///img/diagrams/update-light.svg)
![Updating the App: it checks daily, asks you in the tray, waits for running agent commands on Windows, and replaces the App and its command line together](pathname:///img/diagrams/update-dark.svg)

## With the App

The App updates itself and its command line in one step. You never update them separately.

- **It checks once a day.** Choose **Check for updates** to look now.
- **It asks you first.** A new version shows in the tray or menu bar: update now, or later.
- **On Windows it waits** while agent commands still run from the App's command line. Nothing is stopped. It installs once they finish, or when you say so.
- **Agents keep working.** They call the same command before and after, with nothing to set up again. Your skills and the Claude Code add-on are refreshed with it.

`qualitylayer update` on a machine with the App hands over to the App's own updater.

## Command line only

On WSL2, a dev container or a server, update from the terminal:

```bash
qualitylayer update
```

## Pilot Shell 11

Pilot Shell 11's own updater moves the machine to QualityLayer by the [install rule](install.md): the App on a machine with a screen, the command line elsewhere. See [Moving from Pilot Shell 11](moving-from-pilot-shell.md).
