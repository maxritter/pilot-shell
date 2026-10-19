---
title: Install
description: Use QualityLayer in the desktop App or your browser, with your task and coding agent side by side.
---

![One rule: a machine with a screen gets the App, which updates itself; WSL2, dev containers and servers get the command line and open the App in a browser](pathname:///img/diagrams/install-light.svg)
![One rule: a machine with a screen gets the App, which updates itself; WSL2, dev containers and servers get the command line and open the App in a browser](pathname:///img/diagrams/install-dark.svg)

**You need** macOS, Windows or Linux, Git, a repository, and Claude Code, Codex, Pi, OpenCode or [another agent](agents/other.md) that you have signed in to and started once. See [native agent setup](agents/native.md) for supported versions and commands.

## On your computer

**[Download the App](https://qualitylayer.dev/download)** and open it. Setup asks for:

1. **Licence:** activate yours, or start the 7-day trial.
2. **Command line:** the App installs the `qualitylayer` command, skills and hooks.
3. **Your agents:** Claude Code, Codex, Pi and OpenCode are connected when found on this computer.
4. **Your level:** Engineering (default) or Product. [What each changes](intro.md#two-levels).

On Windows you can also run `irm https://qualitylayer.dev/install.ps1 | iex` in PowerShell. This installs the App and the command line.

## In your browser {#browser}

The browser shows the same workspace: task content on the left, your agent on the right. After installation, run `qualitylayer app` to open it. Your agents run on the computer where QualityLayer is installed.

### WSL2, dev containers and servers {#without-a-screen}

Install QualityLayer where your agent runs. Its pages open in your computer's browser, so you don't need the App there.

![Install QualityLayer where your agent runs, in a dev container, WSL2 or on a server. Its pages open in the browser on your computer through one forwarded port](pathname:///img/diagrams/remote-light.svg)
![Install QualityLayer where your agent runs, in a dev container, WSL2 or on a server. Its pages open in the browser on your computer through one forwarded port](pathname:///img/diagrams/remote-dark.svg)

Install your agent first, then run this where it runs:

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash
```

| Your agent runs in | The App's pages open |
| --- | --- |
| **WSL2** | In your Windows browser |
| **A VS Code dev container** (on macOS, Windows or Linux) | In your browser. VS Code forwards the port |
| **A server over SSH** | In VS Code Remote-SSH, by themselves. With plain `ssh`, forward the port that `qualitylayer app pair` prints |

`qualitylayer app` opens the pages again at any time. An App installed on your computer shows only that computer's tasks.

To keep your licence, Claude Code login and QualityLayer setup when the container is rebuilt, add this to `devcontainer.json`:

```json
"mounts": [
  "source=qualitylayer-${devcontainerId},target=/home/vscode/.qualitylayer,type=volume",
  "source=claude-${devcontainerId},target=/home/vscode/.claude,type=volume"
],
"postCreateCommand": "sudo chown vscode ~/.qualitylayer ~/.claude && curl -fsSL https://claude.ai/install.sh | bash && curl -fsSL https://qualitylayer.dev/install.sh | bash"
```

## Updates {#updates}

Click **Update ready** in the App's sidebar, then **Restart and update**. Without the App, run `qualitylayer update`. See the [changelog](reference/changelog.md).

Setup installs `ql-workflow`, `ql-artifact`, `ql-peer` and `ql-manage` into each supported agent it finds. Ask naturally to plan, implement, draw an artifact or continue using QualityLayer or QL; the agent loads the matching instructions. Updates retire QualityLayer's old skill names and preserve edited legacy files as inactive backups, keeping unrelated custom skills.

## Remove it {#uninstall}

`qualitylayer uninstall` undoes what the installer changed; your plans stay. To move your licence, run `qualitylayer licence activate <key>` on the other computer.

### On Windows {#uninstall-windows}

Works even when the App or CLI is blocked or gone:

```powershell
& ([scriptblock]::Create((irm https://qualitylayer.dev/install.ps1))) -Uninstall
```

It removes QualityLayer's integrations from Claude Code, Codex, Pi and OpenCode (keeping a backup of changed files), plus the skills, App and shortcuts. Your native logins, settings and session history stay. Your licence and tasks stay; add `-Purge` to remove QualityLayer's data too.

## Windows with Intune or Defender Exploit Guard {#managed-windows}

If setup fails with "Microsoft Defender Exploit Guard blocked an operation that was not allowed by your IT administrator", or files vanish after install: QualityLayer is not code-signed yet, and Defender blocks new unsigned programs.

| Fix | How |
| --- | --- |
| **Exclusion** (IT) | Exclude `%LOCALAPPDATA%\QualityLayer` and `%USERPROFILE%\.qualitylayer\bin`. Intune: Endpoint security › Attack surface reduction › *Attack Surface Reduction Only Exclusions* |
| **File indicator** (IT) | Allow the setup file by its SHA-256 from `SHA256SUMS` on the release page |
| **WSL** (no IT) | Install [in WSL2](#without-a-screen); the App opens in your Windows browser |

Then run `qualitylayer doctor` and open the App once to repair the install.

Next: [your first task](first-task.md).
