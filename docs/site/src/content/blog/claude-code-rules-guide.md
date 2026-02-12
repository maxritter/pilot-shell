---
slug: "claude-code-rules-guide"
title: "The Complete Guide to Claude Code Rules"
description: "Everything you need to know about Claude Code rules: types, locations, frontmatter, writing effective rules, practical examples, and team management."
date: "2026-02-08"
author: "Max Ritter"
tags: [Guide, Configuration]
readingTime: 5
keywords: "Claude Code rules, CLAUDE.md, Claude Code custom instructions, Claude Code configuration, Claude Code rules guide"
---

# The Complete Guide to Claude Code Rules

Rules are markdown files that give Claude persistent instructions — coding standards, project conventions, workflow requirements. Instead of repeating "use pytest, not unittest" every session, you write it once as a rule and Claude follows it automatically.

## Rule Types and Locations

Claude Code supports rules at three levels:

| Level | Location | Scope |
|-------|----------|-------|
| **Global** | `~/.claude/rules/` | All projects on your machine |
| **Project** | `.claude/rules/` | This project only (committed to git) |
| **Conditional** | Frontmatter with `globs:` | Only when matching files are active |

Project rules override global rules when they conflict. Conditional rules activate only for matching file patterns:

```markdown
---
globs: ["**/*.test.ts", "**/*.spec.ts"]
---
# Test File Standards
- Use `describe` blocks grouped by function name
- Prefer `toEqual` over `toBe` for objects
```

## Writing Effective Rules

### Be Specific, Not Vague

```
❌ Write clean, maintainable code following best practices.
✅ Functions must be under 30 lines. No function takes more than 4 parameters.
```

### Use Tables for Decisions

Tables are the most reliable format — Claude parses them consistently:

```markdown
| Task Complexity | Approach |
|----------------|----------|
| Trivial (1 file) | Execute directly |
| Moderate (2-5 files) | Track with tasks |
| High (10+ files) | Plan first |
```

### Include Why

Claude follows rules better when it understands the reasoning:

```markdown
## File Size Limit
Files must stay under 300 lines. Above 500 is a hard limit.
**Why:** Large files indicate poor separation of concerns.
```

### Cover Exceptions

```markdown
## TDD Enforcement
All code changes require a failing test first.
**Exceptions:** Documentation, config files, dependency updates.
**When uncertain, use TDD.**
```

## Practical Examples

### Python Project

```markdown
# Python Standards
| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Run tests | `uv run pytest -q` |
| Lint | `ruff check . --fix` |
| Type check | `basedpyright src` |

- Type hints on all public functions
- Dataclasses over dicts for structured data
- pathlib.Path over os.path
```

### React/TypeScript Project

```markdown
# React Conventions
- Functional components only
- Props interface defined above component
- Local state: useState / useReducer
- Server state: React Query
- Global state: Zustand (no Redux)
```

## Common Mistakes

- **Too long** — Keep each rule file focused on one topic. Split "coding standards" into separate files.
- **Duplicating defaults** — Don't write rules for things Claude already does well. Focus on behaviors you want to change.
- **Stale rules** — Update rules when your stack changes. Treat them like code.

## Automating Rule Management

Pilot provides two tools for rule management:

- **`/sync`** scans your codebase and generates rules matching your actual project structure, dependencies, and patterns
- **Team Vault** (`sx`) shares rules across your team via a private Git repository — push once, everyone gets it

Rules compound. A well-maintained library means Claude starts every session already understanding your project, conventions, and quality bar.
