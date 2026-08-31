---
slug: /
sidebar_position: 0
title: Introduction
description: Complete technical reference for Pilot Shell — professional context and harness engineering for Claude Code and Codex CLI.
---

# Pilot Shell Documentation

**Pilot Shell** is how real engineers run Claude Code and Codex CLI. It keeps persistent knowledge, enforced quality, professional tools, and runtime proof around the way you already use either agent.

Work directly, use the native Plan/Goal tools your agent provides, or invoke a Pilot workflow. These are peer paths through the same harness; Pilot does not prescribe one over another.

## Why Pilot Shell

- **Automatic quality** — linting, formatting, type checking, and test enforcement happen as hooks, not suggestions
- **Persistent context** — architectural decisions, patterns, project knowledge, and working state survive across sessions
- **Professional tools** — Semble, CodeGraph, RTK, browser automation, language servers, and MCP integrations support the complete engineering loop
- **Runtime proof** — tests, builds, real execution, and browser or device verification replace “looks done” handoffs
- **Full visibility** — a local dashboard shows what's running, what changed, and what it cost
- **Structured workflows when useful** — `/spec`, `/build`, `/fix`, and `/prd` add durable artifacts and explicit lifecycle contracts

## Quick start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash

# Start with Claude Code or Codex CLI — Pilot loads automatically
cd your-project
claude   # Claude Code — full feature set
codex    # Codex CLI — supported through CLI or ChatGPT desktop

# Or restart ChatGPT desktop after installation and open this project there
```

From there, use whichever path fits the work: a direct request, the agent's native Plan/Goal tools, or a Pilot workflow.

```bash
# Add repository-specific shared guidance when wanted
> /setup-rules       # Codex: $setup-rules

# Pilot workflows add explicit artifact and lifecycle contracts
> /prd "Add real-time notifications for team updates"   # Codex: $prd
> /spec "Add user authentication with OAuth"            # Codex: $spec
> /build "onboarding flow as smooth as Linear's"        # Codex: $build
> /fix "OAuth callback drops the redirect path"          # Codex: $fix
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
- **Pilot Console** — local web dashboard at `localhost:41777` for sessions, memories, workflow artifacts, changes, usage, and configuration
- **Codex compatibility** — adapted skills, `AGENTS.md` guidance, hooks, and support in Codex CLI and the ChatGPT desktop app

Explore the sidebar for [getting started](/docs/getting-started/prerequisites), the [engineering harness](/docs/features/hooks), [Pilot workflows](/docs/workflows/spec), and the [Console](/docs/features/console).
