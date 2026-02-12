---
slug: "native-installer"
title: "Claude Code Native Installer: Skip Node.js Entirely"
description: "One command to install Claude Code on Windows, Mac, or Linux. No Node.js, no npm, no PATH configuration. Automatic updates included."
date: "2026-01-17"
author: "Max Ritter"
tags: [Guide]
readingTime: 3
keywords: "claude, code, entirely, installer, native, nodejs, skip"
---

# Claude Code Native Installer: Skip Node.js Entirely

One command to install Claude Code on Windows, Mac, or Linux. No Node.js, no npm, no PATH configuration. Automatic updates included.

**Problem**: Installing Claude Code through npm required Node.js 18+, caused PATH issues, and broke on certain platforms. The native installer fixes all of this with a single command that works everywhere.

## [Quick Start: One Command Install](#quick-start-one-command-install)

**Windows PowerShell:**

```p-4
irm https://claude.ai/install.ps1 | iex
```

**macOS / Linux / WSL:**

```p-4
curl -fsSL https://claude.ai/install.sh | bash
```

**Homebrew (macOS/Linux):**

```p-4
brew install --cask claude-code
```

That's it. No Node.js. No npm. No PATH configuration. Run `claude --version` to verify.

## [Why the Native Installer Is Better](#why-the-native-installer-is-better)

Anthropic released the native installer as the **recommended installation method** for all Claude Code users. Here's why:

| Feature | Native Installer | npm Install |
| --- | --- | --- |
| Requires Node.js | No | Yes (v18+) |
| Auto-updates | Yes (background) | No (manual) |
| PATH setup | Automatic | Often broken |
| Platform support | Windows, macOS, Linux, WSL | Varies |
| Stability | Production-tested | Platform-dependent |

The native installer handles everything automatically: downloads the right binary for your system, sets up PATH, and keeps Claude Code updated in the background.

## [Windows: `irm https://claude.ai/install.ps1 | iex`](#windows-irm-httpsclaudeaiinstallps1--iex)

The PowerShell command `irm https://claude.ai/install.ps1 | iex` does three things:

1. **irm** (Invoke-RestMethod) downloads the install script from Anthropic
2. **|** pipes the script content to the next command
3. **iex** (Invoke-Expression) executes the downloaded script

**Run as Administrator** for cleanest install:

```p-4
# Open PowerShell as Administrator, then:
irm https://claude.ai/install.ps1 | iex
 
# Verify installation
claude --version
```

**Alternative for CMD users:**

```p-4
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

**WinGet option:**

```p-4
winget install Anthropic.ClaudeCode
```

Note: WinGet doesn't auto-update. The native installer is preferred.

## [macOS and Linux: `curl https://claude.ai/install.sh | bash`](#macos-and-linux-curl-httpsclaudeaiinstallsh--bash)

The bash installer works identically across macOS, Linux, and WSL:

```p-4
curl -fsSL https://claude.ai/install.sh | bash
```

The `-fsSL` flags mean:

- **f**: Fail silently on HTTP errors
- **s**: Silent mode (no progress bar)
- **S**: Show errors if they occur
- **L**: Follow redirects

**Verify and start:**

```p-4
claude --version
cd your-project
claude
```

## [Troubleshooting](#troubleshooting)

### ["irm is not recognized" (Windows)](#irm-is-not-recognized-windows)

You're in CMD, not PowerShell. Open PowerShell and run the command there.

### ["Execution policy" error (Windows)](#execution-policy-error-windows)

PowerShell may block scripts by default:

```p-4
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm https://claude.ai/install.ps1 | iex
```

### ["command not found" after install](#command-not-found-after-install)

Close and reopen your terminal to reload PATH, then try `claude --version` again.

### [Already have npm version installed?](#already-have-npm-version-installed)

Uninstall the npm version first:

```p-4
npm uninstall -g @anthropic-ai/claude-code
```

Then run the native installer.

## [What Happens After Install](#what-happens-after-install)

Once Claude Code is installed:

1. Run `claude` in any project directory
2. Complete one-time authentication with your [Anthropic account](https://console.anthropic.com)
3. Start coding with AI

**New to Claude Code?** Follow the [first project tutorial](/blog/guide/first-project) to see it in action. Need more installation options? See the [complete installation guide](/blog/guide/installation-guide).

The native installer was announced in October 2025 as Anthropic's recommended method. It's simpler, more stable, and keeps you updated automatically. No Node.js required.

Last updated on

[Previous

Installation Guide](/blog/guide/installation-guide)[Next

First Project](/blog/guide/first-project)
