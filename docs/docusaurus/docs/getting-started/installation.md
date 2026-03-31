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
| 4 | Dependencies | Installs Probe, RTK, CodeGraph, agent-browser (fallback), language servers |
| 5 | Shell integration | Auto-configures bash, fish, and zsh with the `pilot` alias |
| 6 | VS Code extensions | Installs recommended extensions for your language stack |
| 7 | Finalize | Success message with next steps |

## Chrome Extension (Recommended)

For the best browser automation and E2E testing experience, install the [Claude Code Chrome extension](https://code.claude.com/docs/en/chrome). It provides richer visual context and more reliable interactions than the agent-browser fallback.

Pilot automatically detects the Chrome extension and uses it when available. In environments where the extension can't be installed (e.g., dev containers, headless CI), Pilot falls back to agent-browser automatically.

## Codex Plugin (Optional)

For adversarial code review powered by OpenAI Codex, install the [Codex plugin](https://github.com/openai/codex-plugin-cc):

```bash
claude plugin install @openai/codex
```

After installation, run `/codex:setup` and enable the Codex reviewers in Console Settings → Spec Workflow → Codex Reviewers. Pilot auto-detects the plugin — when enabled, Codex provides an independent second opinion during `/spec` planning and verification phases.

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
