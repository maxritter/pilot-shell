---
slug: /
sidebar_position: 0
title: Introduction
description: Complete technical reference for Pilot Shell — how real engineers run Claude Code and Codex CLI, with spec-driven plans, enforced TDD, persistent memory, and quality hooks.
---

# Pilot Shell Documentation

**Pilot Shell** is how real engineers run Claude Code and Codex CLI. You get plans you can review before a single line is written, tests that are enforced — not optional, knowledge that persists across sessions, and quality gates that run automatically on every edit.

No more re-explaining decisions, chasing skipped tests, or reviewing 15-file changes that were never scoped. Pilot adds the structure that turns fast AI output into reliable production code.

## Why Pilot Shell

- **Reliable output** — every feature goes through plan → implement → verify, with TDD at each step
- **Persistent context** — architectural decisions, patterns, and project knowledge survive across sessions
- **Automatic quality** — linting, formatting, type checking, and test enforcement happen as hooks, not suggestions
- **Full visibility** — a local dashboard shows what's running, what changed, and what it cost

## Quick start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash

# Start with Claude Code or Codex CLI (Pilot loads automatically)
cd your-project
claude   # Claude Code — full feature set
codex    # Codex CLI — all core workflows

# Generate project rules
> /setup-rules       # Codex: $setup-rules

# Create a reusable skill
> /create-skill      # Codex: $create-skill

# Brainstorm a vague idea into a PRD (with optional research)
> /prd "Add real-time notifications for team updates"   # Codex: $prd

# Plan and build a feature
> /spec "Add user authentication with OAuth"            # Codex: $spec

# Ask Codex for a second opinion or a steerable side-task (Claude Code only)
> /ask-codex "Review the auth flow for race conditions"
```

## Architecture

Pilot enhances Claude Code and Codex CLI with:

- **Quality hooks** — auto-format, lint, type-check, and TDD enforcement on every file edit
- **7 MCP servers** — library docs, persistent memory, web search, code search, page fetching, code intelligence
- **3 language servers** *(Claude Code only)* — Python (basedpyright), TypeScript (vtsls), Go (gopls)
- **Persistent memory** — decisions and context survive across sessions in a local SQLite database, and can be shared with your team through the project repository
- **Pilot Console** — local web dashboard at `localhost:41777` for monitoring, configuration, and skill sharing

Explore the sidebar for [getting started](/docs/getting-started/prerequisites), [workflows](/docs/workflows/prd), and [features](/docs/features/console).
