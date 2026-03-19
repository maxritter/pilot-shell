---
slug: /
sidebar_position: 0
title: Introduction
description: Complete technical reference for Pilot Shell
---

# Pilot Shell Documentation

**Pilot Shell** is the professional development environment for Claude Code. It provides spec-driven development, persistent memory, quality hooks, reusable skills, and a modular rules system.

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash

# Start
cd your-project && pilot

# Generate project rules
> /setup-rules

# Create a reusable skill
> /create-skill

# Plan and build a feature
> /spec "Add user authentication with OAuth"
```

## What's Inside

| Category | Highlights |
|----------|-----------|
| **[Getting Started](/docs/getting-started/prerequisites)** | Prerequisites, one-command installation |
| **[Workflows](/docs/workflows/setup-rules)** | `/setup-rules`, `/spec`, Quick Mode, `/create-skill` |
| **[Features](/docs/features/console)** | Pilot Console, statusline, model routing, rules, context preservation, remote control, hooks, extensions, Pilot CLI, MCP servers, language servers, open-source tools |

## Key Commands

| Command | Purpose |
|---------|---------|
| `pilot` or `ccp` | Start Claude with Pilot enhancements |
| `/setup-rules` | Generate project rules and MCP docs |
| `/spec "task"` | Plan → Implement → Verify with TDD |
| `/create-skill` | Build a reusable skill from any topic |

## Architecture

Pilot enhances Claude Code with:

- **15 hooks** across 7 lifecycle events for automatic quality enforcement
- **6 MCP servers** for library docs, memory, web search, code search, page fetching, and code intelligence
- **3 language servers** (Python, TypeScript, Go) for real-time diagnostics
- **Intelligent model routing** — Opus for planning, Sonnet for implementation
- **Persistent memory** via local SQLite — decisions and context survive across sessions
- **Pilot Console** — local web dashboard for monitoring, configuration, and skill sharing
