---
sidebar_position: 2
title: Installation
description: One-command installation that works with any existing project — no scaffolding, no restructuring. Run the installer once, then use Pilot across all repos.
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
| 4 | Dependencies | Installs Semble, RTK, CodeGraph, Chrome DevTools MCP, playwright-cli, agent-browser, language servers |
| 5 | Shell integration | Auto-configures bash, fish, and zsh with the `pilot` alias. Add `# pilot-shell:managed-elsewhere` to a config file to opt out (for framework-managed shells) |
| 6 | VS Code extensions | Installs recommended extensions for your language stack |
| 7 | Finalize | Success message with next steps |

## Browser Automation

For the best browser automation and E2E testing experience, install the [Claude Code Chrome extension](https://code.claude.com/docs/en/chrome). It provides richer visual context and direct access to your existing browser sessions.

Pilot uses a 4-tier browser tool selection: **Chrome extension** (preferred) → **[Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)** (enterprise fallback via CDP — Lighthouse, performance tracing, device emulation) → **playwright-cli** (thorough E2E with persistent sessions, tracing, network mocking) → **agent-browser** (lightweight, fast startup). The three CLI/MCP tools are installed automatically. The Chrome extension must be installed manually via the browser extension store. In environments where the Chrome extension can't be installed (enterprise restrictions, dev containers), Pilot falls back to Chrome DevTools MCP first, then to CLI tools.

## Codex Plugin (Included)

The [Codex plugin](https://github.com/openai/codex-plugin-cc) is installed automatically by the Pilot installer. To activate it:

1. Run `/codex:setup` in any Pilot session to authenticate with your OpenAI account
2. Enable the Codex reviewers in Console Settings → Reviewers

When enabled, Codex provides an independent adversarial review during `/spec` planning and verification phases. A [ChatGPT Plus](https://chatgpt.com/#pricing) subscription ($20/mo) covers the Codex API usage needed for code reviews.

## Dev Container

Pilot Shell works inside Dev Containers. Copy the `.devcontainer` folder from the [Pilot Shell repository](https://github.com/maxritter/pilot-shell/tree/main/.devcontainer) into your project, adapt it to your needs (base image, extensions, dependencies), and run the installer inside the container. The installer auto-detects the container environment and skips system-level dependencies like Homebrew.

For tighter isolation when working with untrusted code, layer Claude Code's [`/sandbox`](https://code.claude.com/docs/en/sandboxing) on top — `bubblewrap`, `socat`, `iptables`, and `ipset` are pre-installed in the Dockerfile so it works out of the box on Linux.

### Further reading

- [Claude Code · Development containers](https://code.claude.com/docs/en/devcontainer) — Anthropic's reference container, persistent volumes, organization policy, network egress, the `--dangerously-skip-permissions` flag.
- [Claude Code · Sandboxing](https://code.claude.com/docs/en/sandboxing) — Seatbelt (macOS) and bubblewrap (Linux/WSL2), `/sandbox` modes, `allowedDomains`, filesystem allow/deny rules, security limitations.

## Install Specific Version

```bash
export VERSION=8.4.0
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash
```

See [releases](https://github.com/maxritter/pilot-shell/releases) for all available versions. Useful when a specific version is known stable.

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/uninstall.sh | bash
```

Removes binary, plugin files, managed commands/rules, settings, and shell aliases. Your project's custom `.claude/` files are preserved.

## Reset & Refresh

Claude Code's session logs and Pilot's caches grow over time and can degrade performance. A periodic reset every few weeks restores a clean baseline.

```bash
# 1. Inside Claude Code, log out
/logout

# 2. Back up your current config (just in case)
mv ~/.claude.json ~/.claude.json.bak
mv ~/.claude       ~/.claude.bak
mv ~/.pilot        ~/.pilot.bak

# 3. Reinstall Pilot Shell from the official installer
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash

# 4. Start Pilot, sign in to Claude, and re-activate your license
pilot
pilot activate <your-license-key>
```

Once Pilot Shell is running smoothly again, you can delete the `.bak` copies. Forgot your license key? Recover it in the [Polar members area](https://polar.sh/max-ritter/portal).
