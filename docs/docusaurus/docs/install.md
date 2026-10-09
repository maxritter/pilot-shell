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

On Windows, you can also install it from PowerShell: `irm https://qualitylayer.dev/install.ps1 | iex`. This installs the App and the command line.

### Remove it on Windows {#uninstall-windows}

One PowerShell command removes QualityLayer without starting any of its programs, which also works when the App, the CLI or the uninstaller is blocked or gone:

```powershell
& ([scriptblock]::Create((irm https://qualitylayer.dev/install.ps1))) -Uninstall
```

It takes QualityLayer's own hooks and settings out of Claude Code and Codex and leaves every other line of those files as it is, keeping a copy of each file it changed. It also removes the skills, the launcher, the App folder and its shortcuts. Your licence and tasks in `.qualitylayer` stay; add `-Purge` to remove them too.

## Without a screen

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash
```

In WSL, run the command above inside your Linux distribution. The installer explains how to open the App in your browser; over SSH, forward the port it names.

## Updates {#updates}

The App updates itself and the CLI together. When **Update ready** shows in the sidebar, click it and **Restart and update**; you land back on the same page. Without the App, run `qualitylayer update`. What changed is in the [changelog](reference/changelog.md).

## Remove it {#uninstall}

`qualitylayer uninstall` puts back what the installer changed. Your plans stay. `qualitylayer licence activate <key>` moves your licence to another computer.

On Windows, one PowerShell command removes it even when the App, the CLI or the uninstaller is blocked or gone: see [Remove it on Windows](#uninstall-windows).

Coming from Pilot Shell 11? Its updater moves you over by itself; see [From Pilot Shell 11](moving-from-pilot-shell.md).

## Windows with Intune or Defender Exploit Guard {#managed-windows}

On a Windows PC that your company manages, setup can be refused with "Microsoft Defender Exploit Guard blocked an operation that was not allowed by your IT administrator", or the App's update can be blocked, or a file of QualityLayer's can disappear after the install.

**Why.** QualityLayer's installer and programs are not signed with a code-signing certificate yet. A Defender rule called *Block executable files from running unless they meet a prevalence, age, or trusted list criterion* stops programs that are new, rarely seen and unsigned. Your IT administrator has turned that rule on, and you cannot switch it off yourself.

**What your IT administrator can allow.** Either of these is enough:

- An exclusion for the rule on the App's folder, `%LOCALAPPDATA%\QualityLayer`, and on the launcher's folder, `%USERPROFILE%\.qualitylayer\bin`. In Intune this is under Endpoint security, Attack surface reduction, *Attack Surface Reduction Only Exclusions*.
- A file indicator for the setup file by its SHA-256. The checksums are in `SHA256SUMS` on the release page.

**Without administrator help.** Use WSL. Inside a Linux distribution, install the command line with the command from [Without a screen](#without-a-screen), and QualityLayer opens its App in your Windows browser. The Windows rule does not apply to Linux programs inside WSL.

**If files were removed.** Your agent's hooks stay silent when the App is gone, so Claude Code and Codex do not show an error on every tool call. `qualitylayer doctor` shows what a hook found, and opening the App once repairs the install. If the App itself is blocked, remove QualityLayer with the [one-line script above](#uninstall-windows).

Next: [your first task](first-task.md).
