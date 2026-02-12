---
slug: "memory-optimization"
title: "Claude Code Memory: End Repetitive Context Setup"
description: "CLAUDE.md loads at startup with high priority. Structure it correctly and Claude Code remembers your tech stack and preferences every session."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 8
keywords: "claude, code, context, end, memory, optimization, repetitive, setup"
---

Mechanics

# Claude Code Memory: Never Re-Explain Your Project Again

CLAUDE.md loads at startup with high priority. Structure it correctly and Claude Code remembers your tech stack and preferences every session.

**Problem**: Claude Code loses track of your project context between sessions, forcing you to repeat instructions every time you start working.

**Quick Win**: Create your memory system in 30 seconds:

```p-4
cd your-project
claude
/init
```

Claude analyzes your codebase and generates a starter `CLAUDE.md` file. This becomes your project's persistent memory - loaded automatically every session.

## [CLAUDE.md is Your Memory System](#claudemd-is-your-memory-system)

Claude Code's memory lives in the `CLAUDE.md` file. Unlike conversation history that disappears, this file persists across sessions. Claude reads it at startup and treats its contents as authoritative instructions.

Here's what makes this powerful: **CLAUDE.md content receives high priority in Claude's context window**. It's followed more strictly than your chat messages or file contents you read during a session. Think of it as configuration, not documentation.

This priority distinction matters for how you structure your context. See [the priority hierarchy](/blog/guide/mechanics/rules-directory#why-priority-matters-the-monolithic-claudemd-problem) for the full breakdown.

## [Structure Your CLAUDE.md for Maximum Retention](#structure-your-claudemd-for-maximum-retention)

A well-structured file separates what Claude needs to always remember from what changes:

```p-4
# Project Context
 
- Framework: Next.js 14 with App Router
- Database: Supabase with Row Level Security
- Testing: Vitest for unit tests
 
## Key Directories
 
- `src/app/` - Route handlers and pages
- `src/lib/` - Shared utilities
- `src/components/` - React components
 
## Standards
 
- TypeScript strict mode required
- All API routes need error handling
- Run `npm test` before committing
 
## Current Focus
 
- Building user authentication flow
- Priority: Login and password reset
```

The "Current Focus" section gives you a place to update session-specific context without cluttering permanent instructions.

## [Directory Crawling: Hierarchical Memory](#directory-crawling-hierarchical-memory)

Claude reads `CLAUDE.md` files up the directory tree. This creates a memory hierarchy:

```p-4
~/projects/CLAUDE.md          <- Universal defaults
~/projects/my-app/CLAUDE.md   <- Project-specific
~/projects/my-app/api/CLAUDE.md <- Component-specific
```

Use this for monorepos or when different parts of your project need different contexts. Keep parent directories lightweight - everything loads every session.

## [@import Syntax: Composable Memory](#import-syntax-composable-memory)

CLAUDE.md files can import additional files using the `@path/to/import` syntax. This turns your memory system from a single file into a composable network of instructions.

```p-4
See @README for project overview and @package.json for available npm commands.
 
# Additional Instructions
 
- git workflow @docs/git-instructions.md
```

Both relative and absolute paths work. Relative paths resolve from the file containing the import, not from your working directory. You can reference any file in your project or system:

```p-4
# Pull in shared team standards
 
- @docs/coding-standards.md
- @docs/api-conventions.md
 
# Reference external files with absolute paths
 
- @~/.claude/my-preferences.md
```

**First-time approval**: When Claude Code encounters external imports in a project for the first time, it shows an approval dialog listing the specific files. Approve to load them, decline to skip them. This is a one-time decision per project. Once declined, the dialog does not resurface and those imports remain disabled.

**Code block safety**: Imports are not evaluated inside markdown code spans or code blocks. So writing `@path/to/file` in a code example won't trigger an import.

**Recursive imports**: Imported files can themselves import additional files, with a max-depth of 5 hops. This lets you build layered instruction sets without flattening everything into one file.

**Git worktree tip**: If you work across multiple git worktrees, `CLAUDE.local.md` only exists in one. Use a home-directory import so all worktrees share the same personal instructions:

```p-4
# Individual Preferences
 
- @~/.claude/my-project-instructions.md
```

## [CLAUDE.local.md: Private Project Memory](#claudelocalmd-private-project-memory)

For personal project-specific preferences that should not be checked into version control, use `CLAUDE.local.md`. This file is automatically added to `.gitignore`, making it ideal for private context like sandbox URLs, preferred test data, or personal workflow preferences.

```p-4
# CLAUDE.local.md
 
## My Local Setup
 
- Dev server: http://localhost:3001
- Test database: local-dev-db
- Preferred branch naming: feature/[initials]-[description]
```

`CLAUDE.local.md` loads automatically alongside `CLAUDE.md` with the same priority. You get personal context without polluting the team's shared instructions.

## [/memory Command: View and Edit Loaded Files](#memory-command-view-and-edit-loaded-files)

Use the `/memory` command during a session to see what memory files are currently loaded and to open any memory file in your system editor. This is useful for:

- Verifying which CLAUDE.md files, rules, and imports are active
- Quickly editing memory files without leaving your session
- Debugging when instructions seem to be missing or not loading

## [Modular Rules: Path-Targeted High-Priority Memory](#modular-rules-path-targeted-high-priority-memory)

For finer control, the `.claude/rules/` directory lets you split instructions into multiple files with path targeting:

```p-4
.claude/rules/
├── api-guidelines.md     # paths: src/api/**/*
├── react-patterns.md     # paths: src/components/**/*
└── testing-rules.md      # paths: **/*.test.*
```

**Critical**: Rules files receive the **same high priority as CLAUDE.md**. The difference is path targeting lets you scope when that priority applies.

This solves the "monolithic CLAUDE.md problem" - when you cram everything into one file, all instructions compete for high-priority attention even when they're irrelevant to the current task. With rules, your API guidelines get high priority only during API work.

**User-level rules**: You can also create personal rules that apply across all your projects in `~/.claude/rules/`. These load before project rules, giving project rules higher priority when there's a conflict.

**Brace expansion**: Path patterns support brace expansion for matching multiple extensions or directories: `src/**/*.{ts,tsx}` or `{src,lib}/**/*.ts`.

**Symlinks**: The `.claude/rules/` directory supports symlinks, letting you share common rules across multiple projects. Circular symlinks are detected and handled gracefully.

See the [Rules Directory guide](/blog/guide/mechanics/rules-directory) for path patterns, the priority hierarchy, and migration strategies.

## [The Complete Memory Hierarchy](#the-complete-memory-hierarchy)

Claude Code offers five memory locations in a hierarchical structure, each serving a different purpose:

| Memory Type | Location | Purpose | Shared With |
| --- | --- | --- | --- |
| **Managed policy** | System paths (see below) | Organization-wide instructions | All users in organization |
| **Project memory** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared instructions for the project | Team via source control |
| **Project rules** | `./.claude/rules/*.md` | Modular, topic-specific project rules | Team via source control |
| **User memory** | `~/.claude/CLAUDE.md` | Personal preferences for all projects | Just you (all projects) |
| **Project local** | `./CLAUDE.local.md` | Personal project-specific preferences | Just you (current project) |

**Managed policy paths** vary by platform:

- macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`
- Linux: `/etc/claude-code/CLAUDE.md`
- Windows: `C:\Program Files\ClaudeCode\CLAUDE.md`

Files higher in the hierarchy take precedence and load first. This means organization-wide policies set the baseline, and more specific files build on top.

## [Subtree Discovery: Lazy Loading Nested Memory](#subtree-discovery-lazy-loading-nested-memory)

Claude reads CLAUDE.md files by crawling up the directory tree from your working directory. But it also discovers CLAUDE.md files nested in subdirectories below your current directory.

The difference: subtree CLAUDE.md files are not loaded at launch. They only load when Claude reads files in those subdirectories. This keeps startup lean while still honoring localized instructions when they become relevant.

For example, if your project has `packages/auth/CLAUDE.md` with authentication-specific rules, those instructions only load when Claude starts working with files inside `packages/auth/`.

## [Version Control Your Memory](#version-control-your-memory)

Git turns CLAUDE.md into a time-traveling memory system:

```p-4
# Before experimenting with instructions
git add CLAUDE.md && git commit -m "working context state"
 
# Try new instructions, then restore if needed
git checkout CLAUDE.md
```

This gives you instant rollback when instruction changes backfire.

## [Session Memory: Automatic Summarization](#session-memory-automatic-summarization)

Claude Code now maintains a continuous session memory that updates with every message exchange. This structured summary lives at `~/.claude/projects/[project]/[session]/session_memory` and includes:

- **Session title**: Auto-generated description of your work
- **Current status**: Completed items, discussion points, open questions
- **Key results**: Important outcomes and learnings
- **Work log**: Chronological record of actions taken

This automatic summarization powers instant compaction. When you run `/compact`, Claude loads your session memory into a fresh context immediately - no more two-minute waits.

Ask Claude "where is your session memory stored?" to find the exact path for your current session.

## [Fresh Context When You Need It](#fresh-context-when-you-need-it)

Long sessions accumulate irrelevant context. Use `/clear` to reset:

```p-4
/clear
```

This removes conversation history while preserving your CLAUDE.md. Your memory stays intact; the noise disappears.

For completely fresh starts, exit and restart:

```p-4
exit
claude
```

## [Isolated Contexts for Different Work](#isolated-contexts-for-different-work)

Need different memory for different tasks? Use separate directories:

```p-4
mkdir feature-auth && cd feature-auth
cp ../CLAUDE.md CLAUDE.md
echo "## Focus: Authentication only" >> CLAUDE.md
claude
```

Each directory gets its own CLAUDE.md, creating isolated contexts. Perfect for feature branches or experimental work.

## [When Things Go Wrong](#when-things-go-wrong)

**Context feels stale**: Conversation has accumulated irrelevant history.

- **Fix**: Run `/clear` to reset while keeping CLAUDE.md loaded.

**Multiple projects mixing**: Context from one project bleeding into another.

- **Fix**: Each project needs its own CLAUDE.md in its root directory.

**Instructions being ignored**: CLAUDE.md has grown too large or unclear.

- **Fix**: Keep instructions under 400 lines. Move domain-specific details to [path-targeted rules](/blog/guide/mechanics/rules-directory) so they only receive high priority when relevant.

## [Next Steps](#next-steps)

- Master [CLAUDE.md as an operating system](/blog/guide/mechanics/claude-md-mastery) for advanced orchestration patterns
- Learn [context management](/blog/guide/mechanics/context-management) to optimize token usage
- Explore [planning modes](/blog/guide/mechanics/planning-modes) for structured work
- Set up [git integration](/blog/guide/development/git-integration) for seamless memory checkpoints
- See how memory fits into [context engineering](/blog/guide/mechanics/context-engineering) for production AI systems

**Remember**: CLAUDE.md isn't project documentation - it's your AI's operating system. Well-structured memory means Claude picks up exactly where you left off, every session.

Last updated on

[Previous

Context Management](/blog/guide/mechanics/context-management)[Next

Session Memory](/blog/guide/mechanics/session-memory)
