---
slug: /
sidebar_position: 0
title: Introduction
description: Complete technical reference for Pilot Shell
---

# Pilot Shell Documentation

**Pilot Shell** makes Claude Code production-ready. You get plans you can review before a single line is written, tests that are enforced — not optional, knowledge that persists across sessions, and quality gates that run automatically on every edit.

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

# Start
cd your-project && pilot

# Generate project rules
> /setup-rules

# Create a reusable skill
> /create-skill

# Brainstorm a vague idea into a PRD (with optional research)
> /prd "Add real-time notifications for team updates"

# Plan and build a feature
> /spec "Add user authentication with OAuth"
```

## Architecture

Pilot enhances Claude Code with:

- **15 hooks** across 7 lifecycle events for automatic quality enforcement
- **6 MCP servers** for library docs, memory, web search, code search, page fetching, and code intelligence
- **3 language servers** (Python, TypeScript, Go) for real-time diagnostics
- **Intelligent model routing** — Opus for planning, Sonnet for implementation
- **Persistent memory** via local SQLite — decisions and context survive across sessions
- **Pilot Console** — local web dashboard for monitoring, configuration, and skill sharing

Explore the sidebar for [getting started](/docs/getting-started/prerequisites), [workflows](/docs/workflows/setup-rules), and [features](/docs/features/console).
