---
slug: "rules-directory"
title: "Claude Code Rules Directory: Modular Instructions That Scale"
description: "Organize Claude Code instructions into modular files with path-specific targeting. Rules activate only where they matter, saving context tokens."
date: "2025-12-10"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 9
keywords: "claude, code, directory, instructions, modular, rules, scale, that"
---

Mechanics

# Claude Code Rules Directory: Modular Instructions That Scale

Organize Claude Code instructions into modular files with path-specific targeting. Rules activate only where they matter, saving context tokens.

**Problem**: Your CLAUDE.md file has grown unwieldy. React patterns mixed with API guidelines mixed with testing rules. Everything loads every session, even when you're only working on database migrations.

**Quick Win**: Create your first modular rule:

```p-4
mkdir -p .claude/rules
echo "# Testing Rules
- Run tests before committing
- Mock external services in unit tests" > .claude/rules/testing.md
```

That rule now loads automatically alongside your CLAUDE.md, keeping concerns separated.

## [What Is the Rules Directory?](#what-is-the-rules-directory)

The `.claude/rules/` directory is a **modular alternative to monolithic CLAUDE.md files**. Instead of cramming everything into one file, you organize instructions into multiple markdown files that Claude loads as project memory.

**Critical detail from Anthropic**: Rules files load with the **same high priority as CLAUDE.md**. This matters because Claude's context window has a priority hierarchy - not all tokens are weighted equally.

Every `.md` file in `.claude/rules/` automatically becomes part of your project context. No configuration needed.

```p-4
.claude/rules/
├── code-style.md      # Formatting and conventions
├── testing.md         # Test requirements
├── security.md        # Security checklist
└── frontend/
    ├── react.md       # React-specific patterns
    └── styles.md      # CSS conventions
```

This structure gives you **separation of concerns** at the instruction level. Update your security rules without touching your styling guidelines.

## [Path-Specific Rules: The Power Feature](#path-specific-rules-the-power-feature)

Here's where rules get interesting. You can target rules to specific file patterns using YAML frontmatter:

```p-4
---
paths: src/api/**/*.ts
---
 
# API Development Rules
 
- All endpoints must validate input with Zod
- Return consistent error shapes: { error: string, code: number }
- Log all requests with correlation IDs
```

This rule \*\*only activates when Claude works on files matching `src/api/**/\*.ts`\*\*. Your API guidelines stay out of the way when you're editing React components.

### [Multiple Path Patterns](#multiple-path-patterns)

Target multiple patterns in a single rule:

```p-4
---
paths:
  - src/components/**/*.tsx
  - src/hooks/**/*.ts
---
 
# React Development Rules
 
- Use functional components exclusively
- Extract logic into custom hooks
- Memoize expensive computations
```

### [Common Path Patterns](#common-path-patterns)

| Pattern | Matches |
| --- | --- |
| `src/api/**/*.ts` | All TypeScript files in src/api and subdirectories |
| `*.test.ts` | All test files in any directory |
| `src/components/*.tsx` | Only direct children of components (not nested) |
| `**/*.css` | All CSS files anywhere in the project |

## [Why Priority Matters: The Monolithic CLAUDE.md Problem](#why-priority-matters-the-monolithic-claudemd-problem)

Claude's context window isn't flat. Different sources of information receive different priority levels in how the model weighs them during generation. Anthropic confirms that **CLAUDE.md and rules files receive high priority** - Claude treats these instructions as authoritative.

This created a problem with the old approach: stuffing everything into one massive CLAUDE.md meant *all* of that content received high priority. Your React patterns competed for attention with your API guidelines, even when you were working on database migrations.

**High priority everywhere = priority nowhere.**

When everything is marked important, Claude struggles to determine what's actually relevant to the current task. The result: instructions get ignored, context becomes noisy, and Claude's behavior becomes unpredictable.

### [The Context Priority Hierarchy](#the-context-priority-hierarchy)

Understanding how Claude weighs different context sources:

| Source | Priority Level | Implication |
| --- | --- | --- |
| **CLAUDE.md** | High | Treated as authoritative instructions |
| **Rules Directory** | High | Same weight as CLAUDE.md |
| **Skills** | Medium (on-demand) | Loaded only when triggered |
| **Conversation history** | Variable | Decays over long sessions |
| **File contents (Read tool)** | Standard | Normal context, no special weight |

The rules directory solves the monolithic problem by letting you **distribute high-priority instructions across targeted files**. Your API rules still get high priority - but only when you're working on API files.

### [Path Targeting = Priority Scoping](#path-targeting--priority-scoping)

When a rule has `paths` frontmatter, it only loads (and receives high priority) when Claude is working on matching files:

```p-4
---
paths: src/api/**/*.ts
---
 
# These instructions get high priority ONLY during API work
```

This is the key insight: **you're not just organizing files, you're scoping when instructions receive elevated attention**.

## [Rules vs CLAUDE.md vs Skills](#rules-vs-claudemd-vs-skills)

When do you use each?

| Feature | Priority | Best For | Loads When |
| --- | --- | --- | --- |
| **CLAUDE.md** | High | Universal operational workflows | Every session |
| **Rules Directory** | High | Domain-specific instructions | Every session (filtered by path) |
| **[Skills](/blog/guide/mechanics/claude-skills-guide)** | Medium | Reusable cross-project expertise | On-demand when triggered |

**Use CLAUDE.md** for what applies everywhere: routing logic, quality standards, coordination protocols. Keep it lean - everything here competes for high-priority attention.

**Use rules** for what applies to specific areas: API patterns for API files, test requirements for test files. Path targeting ensures high priority only when relevant.

**Use skills** for what applies across projects: deployment procedures, code review checklists, brand guidelines. Lower priority until explicitly triggered.

## [Practical Examples](#practical-examples)

### [Security Rules for Sensitive Directories](#security-rules-for-sensitive-directories)

```p-4
---
paths:
  - src/auth/**/*
  - src/payments/**/*
---
 
# Security-Critical Code Rules
 
- Never log sensitive data (passwords, tokens, card numbers)
- Validate all inputs at function boundaries
- Use parameterized queries exclusively
- Require explicit authorization checks before data access
```

### [Test File Standards](#test-file-standards)

```p-4
---
paths: **/*.test.ts
---
 
# Test Writing Standards
 
- Use descriptive test names: "should [action] when [condition]"
- One assertion per test when possible
- Mock external dependencies, never real APIs
- Include edge cases: empty inputs, null values, boundaries
```

### [Database Migration Rules](#database-migration-rules)

```p-4
---
paths: prisma/migrations/**/*
---
 
# Migration Safety Rules
 
- Always include rollback instructions
- Test migrations on a copy of production data first
- Never delete columns in the same migration that removes code using them
- Add columns as nullable first, populate, then add constraints
```

## [Migration from Monolithic CLAUDE.md](#migration-from-monolithic-claudemd)

If your CLAUDE.md has grown large, you're likely experiencing the priority saturation problem: too much high-priority content competing for attention. Extract domain sections into path-targeted rules:

**Before** (single 400-line CLAUDE.md):

```p-4
# Project Context
 
...
 
## API Guidelines
 
- Validate inputs with Zod
- Return consistent errors
  ...
 
## React Patterns
 
- Use functional components
- Extract hooks
  ...
 
## Testing Rules
 
- Mock external services
  ...
```

**After** (lean CLAUDE.md + modular rules):

```p-4
# CLAUDE.md - Operational Core Only
 
## Routing Logic
 
- Simple tasks: execute directly
- Complex tasks: delegate to sub-agents
 
## Quality Standards
 
- Correctness > Maintainability > Performance
```

```p-4
.claude/rules/
├── api-guidelines.md      # API section with paths: src/api/**/*
├── react-patterns.md      # React section with paths: src/components/**/*
└── testing-rules.md       # Testing section with paths: **/*.test.*
```

Your CLAUDE.md stays focused on universal behavior. Domain knowledge lives in targeted rules that only receive high priority when relevant.

The result: **cleaner priority distribution**. Your core operational instructions always get attention. Domain-specific rules get attention only when Claude is working in their target areas.

## [User-Level Rules: Personal Defaults Across All Projects](#user-level-rules-personal-defaults-across-all-projects)

Beyond project-specific rules, you can create personal rules that apply to every project you work on. Place them in `~/.claude/rules/`:

```p-4
~/.claude/rules/
├── preferences.md     # Your personal coding preferences
├── workflows.md       # Your preferred workflows
└── shortcuts.md       # Custom patterns you always want
```

User-level rules load before project rules, giving project rules higher priority. This means your personal defaults apply everywhere, but any project can override them.

This is ideal for preferences that follow you regardless of project: indentation style, commit message format, preferred testing patterns, or anything that reflects how you personally work rather than how a specific project operates.

## [Brace Expansion in Path Patterns](#brace-expansion-in-path-patterns)

Path patterns support brace expansion for matching multiple extensions or directories in a single pattern:

```p-4
---
paths:
  - "src/**/*.{ts,tsx}"
  - "{src,lib}/**/*.ts"
---
 
# TypeScript/React Rules
 
- Use strict TypeScript
- Prefer interfaces over type aliases for public APIs
```

`{ts,tsx}` matches both `.ts` and `.tsx` files. `{src,lib}` matches both the `src/` and `lib/` directories. This keeps your frontmatter compact when a rule applies to related file types or directories.

## [Symlinks: Sharing Rules Across Projects](#symlinks-sharing-rules-across-projects)

The `.claude/rules/` directory supports symlinks, allowing you to maintain a single source of rules shared across multiple projects:

```p-4
# Symlink a shared rules directory
ln -s ~/shared-claude-rules .claude/rules/shared
 
# Symlink individual rule files
ln -s ~/company-standards/security.md .claude/rules/security.md
```

Symlinks are resolved and their contents load normally. Circular symlinks are detected and handled gracefully, so you don't need to worry about infinite loops.

This pattern works well for organizations where teams share common coding standards. Maintain one canonical rules repository and symlink it into each project.

## [Recursive Subdirectory Discovery](#recursive-subdirectory-discovery)

Rules can be organized into subdirectories for better structure. All `.md` files are discovered recursively:

```p-4
.claude/rules/
├── frontend/
│   ├── react.md
│   └── styles.md
├── backend/
│   ├── api.md
│   └── database.md
└── general.md
```

Every `.md` file in the tree loads automatically. Use subdirectories to keep related rules grouped without sacrificing discoverability.

## [Best Practices](#best-practices)

**Keep rules focused**: One concern per file. Security rules separate from styling rules.

**Use descriptive filenames**: `api-validation.md` beats `rules1.md`.

**Leverage path targeting**: Rules without paths load everywhere. Add paths to reduce noise.

**Version control everything**: Rules are code. Review changes, track history, roll back mistakes.

**Document rule purpose**: Start each file with a brief comment explaining when it applies.

## [Next Steps](#next-steps)

1. **Audit your CLAUDE.md**: Identify sections that apply only to specific file types
2. **Extract one rule**: Move your most domain-specific section to `.claude/rules/`
3. **Add path targeting**: Make that rule activate only where it matters
4. **Iterate**: As you work, notice when Claude receives irrelevant context and extract more rules

For the complete memory architecture and why monolithic files cause problems, see [CLAUDE.md Mastery](/blog/guide/mechanics/claude-md-mastery). To understand how priority fits into broader context strategy, explore [context management](/blog/guide/mechanics/context-management) and [memory optimization](/blog/guide/mechanics/memory-optimization).

**The goal**: Claude receives exactly the high-priority instructions it needs for the files it's touching. No more, no less. Priority where it matters, silence everywhere else.

Last updated on

[Previous

CLAUDE.md Mastery](/blog/guide/mechanics/claude-md-mastery)[Next

Terminal Main Thread](/blog/guide/mechanics/terminal-main-thread)
