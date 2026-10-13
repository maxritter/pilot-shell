---
title: Install
description: Download the App, or run one command on a machine without a screen. Updates come through the App.
---

![One rule: a machine with a screen gets the App, which updates itself; WSL2, dev containers and servers get the command line and open the App in a browser](pathname:///img/diagrams/install-light.svg)
![One rule: a machine with a screen gets the App, which updates itself; WSL2, dev containers and servers get the command line and open the App in a browser](pathname:///img/diagrams/install-dark.svg)

**You need** macOS, Windows or Linux, Git, a repository, and Claude Code, Codex or [another agent](agents/other.md) that you have signed in to and started once.

## On your computer

**[Download the App](https://qualitylayer.dev/download)** and open it. Setup asks for:

1. **Licence:** activate yours, or start the 7-day trial.
2. **Command line:** the App installs the `qualitylayer` command, skills and hooks.
3. **Your agents:** Claude Code and Codex are set up for you.
4. **Your level:** Engineering (default) or Product. [What each changes](intro.md#two-levels).

On Windows you can also run `irm https://qualitylayer.dev/install.ps1 | iex` in PowerShell. This installs the App and the command line.

## Without a screen {#without-a-screen}

For WSL2, dev containers and servers:

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash
```

In WSL, run it inside your Linux distribution. The installer prints how to open the App in your browser; over SSH, forward the port it names.

## Updates {#updates}

Click **Update ready** in the App's sidebar, then **Restart and update**. Without the App, run `qualitylayer update`. See the [changelog](reference/changelog.md).

## Remove it {#uninstall}

`qualitylayer uninstall` undoes what the installer changed; your plans stay. To move your licence, run `qualitylayer licence activate <key>` on the other computer.

### On Windows {#uninstall-windows}

Works even when the App or CLI is blocked or gone:

```powershell
& ([scriptblock]::Create((irm https://qualitylayer.dev/install.ps1))) -Uninstall
```

It removes QualityLayer from Claude Code and Codex (keeping a backup of each changed file), plus the skills, App and shortcuts. Your licence and tasks stay; add `-Purge` to remove them too.

## Windows with Intune or Defender Exploit Guard {#managed-windows}

If setup fails with "Microsoft Defender Exploit Guard blocked an operation that was not allowed by your IT administrator", or files vanish after install: QualityLayer is not code-signed yet, and Defender blocks new unsigned programs.

| Fix | How |
| --- | --- |
| **Exclusion** (IT) | Exclude `%LOCALAPPDATA%\QualityLayer` and `%USERPROFILE%\.qualitylayer\bin`. Intune: Endpoint security › Attack surface reduction › *Attack Surface Reduction Only Exclusions* |
| **File indicator** (IT) | Allow the setup file by its SHA-256 from `SHA256SUMS` on the release page |
| **WSL** (no IT) | Install [without a screen](#without-a-screen); the App opens in your Windows browser |

Then run `qualitylayer doctor` and open the App once to repair the install.

Next: [your first task](first-task.md).
