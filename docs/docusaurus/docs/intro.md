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
- **Two ways to run substantial work** — `/spec` when the work is measured against an approved task list, `/build` when it is measured against a goal you name
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

# Or restart ChatGPT desktop after installation and open this project there

# Generate project rules
> /setup-rules       # Codex: $setup-rules

# Brainstorm a vague idea into a PRD (with optional research)
> /prd "Add real-time notifications for team updates"   # Codex: $prd

# Plan and build a feature against an approved task list
> /spec "Add user authentication with OAuth"            # Codex: $spec

# Build toward a goal without a spec, judged in rounds
> /build "onboarding flow as smooth as Linear's"        # Codex: $build

# Fix a focused bug with TDD
> /fix "OAuth callback drops the redirect path"          # Codex: $fix

# Additional workflows, used on demand
> /investigate "How does a CLI flag become persisted config?"   # Codex: $investigate
> /cleanup "src/auth"                                   # Codex: $cleanup
> /create-skill                                          # Codex: $create-skill
```

## Architecture

Pilot enhances Claude Code and Codex CLI with:

- **Quality hooks** — Claude Code auto-formats, lints, type-checks, and enforces TDD on edits; both agents enforce the checks required by an active workflow
- **7 MCP servers** — library docs, persistent memory, web search, code search, page fetching, code intelligence
- **3 language servers** *(Claude Code only)* — Python (basedpyright), TypeScript (vtsls), Go (gopls)
- **Persistent memory** — decisions and context survive across sessions in a local SQLite database, and can be shared with your team through the project repository
- **Pilot Console** — local web dashboard at `localhost:41777` for monitoring, configuration, and skill sharing
- **Codex compatibility** — adapted skills, `AGENTS.md` guidance, hooks, and support in Codex CLI and the ChatGPT desktop app

Explore the sidebar for [getting started](/docs/getting-started/prerequisites), [workflows](/docs/workflows/prd), and [features](/docs/features/console).
