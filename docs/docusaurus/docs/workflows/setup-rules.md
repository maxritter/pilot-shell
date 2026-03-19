---
sidebar_position: 1
title: /setup-rules
description: Generate project rules, audit your codebase, and document MCP servers
---

# /setup-rules

Generate project rules and document your development environment.

Run `/setup-rules` to explore your project structure, discover your conventions and undocumented patterns, update project documentation, and document your MCP servers. This is how Pilot adapts to your project — not the other way around. Run it once initially, then any time your codebase changes significantly.

```bash
$ pilot
> /setup-rules
```

## What /setup-rules Does

10 phases:

| Phase | Action |
|-------|--------|
| 0 | Load reference guidelines, recommended directory structure, error handling |
| 1 | Read existing rules (including nested subdirectories), detect structure and path-scoping |
| 2 | Migrate unscoped assets to `{slug}`-prefixed names |
| 3 | Quality audit against best practices (size, specificity, path-scoping enforcement) |
| 4 | Explore codebase with Probe CLI, codebase-memory-mcp, and Grep to find patterns |
| 5 | Compare discovered vs documented patterns |
| 6 | Sync project rule, nested directories, and generate rules README |
| 7 | Sync MCP server documentation |
| 8 | Discover new rules, place in correct directory by scope |
| 9 | Cross-check: validate references, README, path-scoping |
| 10 | Report summary of all changes made |

## When to Run /setup-rules

- After installing Pilot in a new project
- After making significant architectural changes
- When adding new MCP servers to `.mcp.json`
- Before starting a complex `/spec` task on an unfamiliar codebase
- After onboarding to a project you didn't write

:::tip Creating skills
Use `/create-skill` to create workflow skills — `/setup-rules` focuses exclusively on rules and MCP documentation.
:::
