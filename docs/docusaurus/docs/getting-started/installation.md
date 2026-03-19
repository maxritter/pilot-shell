---
sidebar_position: 2
title: Installation
description: One-command installation — works with any existing project
---

# Installation

Works with any existing project — no scaffolding required.

## One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash
```

Run from any directory — it installs globally to `~/.pilot/` and `~/.claude/`. After installation, `cd` into any project and run `pilot` or `ccp` to start.

## What the Installer Does

7 steps with progress tracking and rollback on failure:

| Step | Title | Description |
|------|-------|-------------|
| 1 | Prerequisites | Checks/installs Homebrew, Node.js, Python 3.12+, uv, git, jq |
| 2 | Claude files | Sets up `~/.claude/` plugin — rules, commands, hooks, MCP servers |
| 3 | Config files | Creates `.nvmrc` and project config |
| 4 | Dependencies | Installs Probe, RTK, codebase-memory-mcp, playwright-cli, language servers |
| 5 | Shell integration | Auto-configures bash, fish, and zsh with the `pilot` alias |
| 6 | VS Code extensions | Installs recommended extensions for your language stack |
| 7 | Finalize | Success message with next steps |

## Permissions Mode

Pilot Shell sets Claude Code to `bypassPermissions` mode by default. This enables the `/spec` workflow to run autonomously — planning, implementing, and verifying without pausing for permission prompts.

**In Quick Mode (regular chat), you control the permission level.** Press `Shift+Tab` to cycle through modes:

| Mode | Behavior |
|------|----------|
| **Plan** | Claude proposes changes, you approve before execution |
| **Accept Edits** | File edits auto-approved, other actions still prompt |
| **Normal** | Fine-grained permission prompts for each tool call |

To set a persistent default, change `defaultMode` in `~/.claude/settings.json`:

```json
{
  "permissions": {
    "defaultMode": "acceptEdits"
  }
}
```

The installer uses three-way merge — your customizations to `defaultMode` and other permission settings are preserved across updates.

:::tip Use /spec instead of plan mode
Claude Code's built-in plan mode (`Shift+Tab` → "plan") is unstructured — plans aren't saved as files, have no consistent format, and disappear when the session ends. Use `/spec` as a drop-in replacement: plans are saved as structured markdown in `docs/plans/`, persist across sessions, and drive a complete workflow with TDD and verification. See the [spec workflow guide](/docs/workflows/spec).
:::

## Dev Container

Pilot Shell works inside Dev Containers. Copy the `.devcontainer` folder from the [Pilot Shell repository](https://github.com/maxritter/pilot-shell/tree/main/.devcontainer) into your project, adapt it to your needs (base image, extensions, dependencies), and run the installer inside the container. The installer auto-detects the container environment and skips system-level dependencies like Homebrew.

## Install Specific Version

```bash
export VERSION=7.5.7
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash
```

See [releases](https://github.com/maxritter/pilot-shell/releases) for all available versions. Useful when a specific version is known stable.

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/uninstall.sh | bash
```

Removes binary, plugin files, managed commands/rules, settings, and shell aliases. Your project's custom `.claude/` files are preserved.
