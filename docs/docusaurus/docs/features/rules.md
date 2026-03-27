---
sidebar_position: 4
title: Rules & Standards
description: Production-tested best practices loaded into every session
---

# Rules & Standards

Production-tested best practices loaded into every session.

Rules load automatically at session start — they're enforced standards, not suggestions. Coding standards load conditionally by file type to keep context lean. Your project-level rules in `.claude/rules/` take precedence over Pilot's built-ins.

## Built-in Rule Categories

### Core Workflow (3 rules)

- `task-and-workflow.md` — Task management, /spec orchestration, deviation handling
- `testing.md` — TDD workflow, test strategy, coverage requirements (≥80%)
- `verification.md` — Execution verification, completion requirements

### Development Practices (3 rules)

- `development-practices.md` — Project policies, systematic debugging, git rules
- `context-management.md` — Context optimization and compaction resilience
- `code-review-reception.md` — How to receive and act on code review feedback

### Tools (3 rules)

- `cli-tools.md` — Pilot CLI, Probe code search, RTK token optimization
- `agent-browser.md` — Browser automation for E2E UI testing
- `mcp-servers.md` — MCP server reference and tool selection guidance

## Coding Standards — Activated by File Type

| Standard | Activates On | Coverage |
|----------|-------------|----------|
| Python | `*.py` | uv, pytest, ruff, basedpyright, type hints |
| TypeScript | `*.ts, *.tsx, *.js, *.jsx` | npm/pnpm, Jest, ESLint, Prettier, React patterns |
| Go | `*.go` | Modules, testing, formatting, error handling |
| Frontend | `*.tsx, *.jsx, *.html, *.vue, *.css` | Components, CSS, accessibility, responsive design |
| Backend | `**/models/**, **/routes/**, **/api/**` | API design, data models, query optimization, migrations |

:::tip Custom rules
Create `.claude/rules/my-rule.md` in your project. Add `paths: ["*.py"]` frontmatter to activate only for specific file types. Run `/setup-rules` to auto-discover patterns and generate project-specific rules.
:::

:::info Monorepo support
Organize rules in nested subdirectories by product and team (e.g. `.claude/rules/my-product/team-x/`). Team-level rules must use `paths` frontmatter to scope to the right files. `/setup-rules` generates a `README.md` in your rules directory to document the structure.
:::
