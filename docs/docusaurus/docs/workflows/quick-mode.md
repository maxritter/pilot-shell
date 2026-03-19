---
sidebar_position: 4
title: Quick Mode
description: Direct execution — no plan file, no approval gate
---

# Quick Mode

Direct execution — no plan file, no approval gate.

Quick mode is the default interaction model. Just describe your task and Pilot gets it done — no spec file, no approval step, no directory scaffolding. Zero overhead on simple tasks. All quality guardrails still apply — hooks, TDD, type checking — but nothing slows down the interaction. When you need a plan, use `/spec` — not Claude Code's built-in plan mode (Shift+Tab).

```bash
$ pilot
> Add a loading spinner to the submit button
> Write tests for the OrderService class
> Explain how the auth middleware works
> Rename the "products" table to "items" across the codebase
```

## Quality Guardrails Active in Quick Mode

- Quality hooks — auto-format, lint, type-check on every file edit
- TDD enforcement — write failing tests before implementation
- Context preservation across auto-compaction cycles
- Persistent memory for recalling past decisions and context
- MCP servers (context7, mem-search, web-search, grep-mcp, web-fetch, codebase-memory-mcp)
- Language servers — real-time diagnostics and go-to-definition

:::tip When to use /spec instead
Use `/spec` for bug fixes (root cause investigation with test-before-fix), complex features that need a plan before implementation, or refactors with many interdependent changes.
:::
