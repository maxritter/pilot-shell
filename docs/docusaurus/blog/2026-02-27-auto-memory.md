---
title: "Claude Code Auto Memory: How Your AI Learns Your Project"
description: "Claude Code auto memory lets Claude write its own project notes. Learn how it works, where files live, and when to use it vs CLAUDE.md."
slug: auto-memory
date: 2026-02-27
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Claude Code auto memory lets Claude write its own project notes. Learn how it works, where files live, and when to use it vs CLAUDE.md.

<!-- truncate -->

**Problem**: You set up CLAUDE.md with your project rules, but Claude still asks the same questions about build commands, test conventions, and debugging quirks. Your instructions cover what you want Claude to do. They don't cover what Claude has already learned about your codebase.

**Quick Win**: Check if auto memory is already working. Run `/memory` inside any Claude Code session. You'll see a selector showing your CLAUDE.md files and an auto-memory toggle. If the toggle is on (it is by default), Claude has been taking notes about your project in the background.

```
# Find your project's auto memory directory
ls ~/.claude/projects/
```

If you see directories there, Claude already has notes. Read on to understand what it stores, how to use it, and how it fits alongside your CLAUDE.md memory system. And if your memory files have grown noisy over many sessions, check out [Auto Dream](/blog/auto-dream), the consolidation feature that periodically cleans and reorganizes everything Auto Memory writes.

## What Auto Memory Actually Is

Auto memory is a persistent directory where Claude records learnings, patterns, and insights as it works. The key distinction: **CLAUDE.md is your instructions to Claude. MEMORY.md is Claude's notebook about your project.**

You write CLAUDE.md to tell Claude things like "use pnpm, not npm" or "always write tests before implementation." Auto memory is where Claude writes notes to itself: "build command is `pnpm build`, tests live in `__tests__/`, API uses Express with middleware in `src/middleware/`."

This is not [Session Memory](/blog/session-memory), which saves conversation-level summaries for cross-session recall. Auto memory operates at a different level. It captures durable project knowledge that persists regardless of which conversation produced it.

## Three Memory Systems Compared

Claude Code now has three distinct memory systems. Understanding when each applies saves you from duplicating effort or missing the right tool for the job.

| Aspect | **CLAUDE.md** | **Auto Memory** | **Session Memory** |
| --- | --- | --- | --- |
| **Who writes it** | You | Claude | Claude |
| **What it contains** | Instructions and rules | Project patterns and learnings | Conversation summaries |
| **Scope** | Per-project or global | Per-project | Per-session |
| **Loaded at startup** | Full file | First 200 lines of MEMORY.md | Relevant past sessions |
| **Priority** | High (treated as instructions) | Background reference | Background reference |
| **Storage** | `./CLAUDE.md` or `~/.claude/CLAUDE.md` | `~/.claude/projects/<project>/memory/` | `~/.claude/projects/<project>/<session>/session-memory/` |
| **Best for** | Standards, architecture decisions, commands | Build patterns, debugging insights, preferences | Continuity between work sessions |
| **Shared with team** | Yes (via git) | No (local only) | No (local only) |

The strongest setup uses all three. [CLAUDE.md](/blog/claude-md-mastery) provides authoritative rules. Auto memory captures what Claude learns while working. [Session Memory](/blog/session-memory) maintains conversation continuity.

## Where Auto Memory Lives

Each project gets its own memory directory based on the git repository root:

```
~/.claude/projects/<project>/memory/
├── MEMORY.md          # Main index, loaded every session
├── debugging.md       # Detailed debugging patterns
├── api-conventions.md # API design decisions
└── ...                # Any topic files Claude creates
```

A few storage details that matter:

- **Git repo root determines the project path.** All subdirectories within the same repo share one auto memory directory. If you `cd` into `src/api/` and start Claude, it uses the same memory as running from the repo root.
- **Git worktrees get separate memory directories.** This is intentional. Different worktrees often represent different branches with different states.
- **Outside a git repo**, the working directory is used instead of the repo root.

## What Gets Remembered

As Claude works on your project, it saves notes across several categories:

**Project patterns**: Build commands, test conventions, code style preferences. After running your test suite once, Claude notes the command and any special flags needed.

**Debugging insights**: Solutions to tricky problems and common error causes. If Claude spends time diagnosing a CORS issue or a webpack config problem, it records the fix.

**Architecture notes**: Key files, module relationships, important abstractions. Claude maps the territory so it doesn't need to rediscover your project structure each session.

**Your preferences**: Communication style, workflow habits, tool choices. If you consistently prefer certain approaches, Claude picks up on that.

The `MEMORY.md` file acts as a concise index. When detailed notes pile up, Claude moves them into dedicated topic files like `debugging.md` or `patterns.md`. This keeps the main file under 200 lines, since that's the cutoff for what loads at startup.

## How to Use Auto Memory

### Let It Work Automatically

The simplest approach: do nothing. Auto memory is enabled by default. As you work, Claude reads and writes memory files in the background. You'll see it happen during sessions when Claude accesses files in the memory directory.

### Save Specific Knowledge

Tell Claude directly what to remember:

```
"remember that we use pnpm, not npm"
"save to memory that the API tests require a local Redis instance"
"note that the staging environment uses port 3001"
```

Claude writes these to the appropriate memory file immediately.

### Browse and Edit

Run `/memory` during any session to open the memory file selector. This shows all your memory files (CLAUDE.md, auto memory, local config) and lets you open any of them in your system editor.

You can also read the files directly:

```
# List all memory files for a project
ls ~/.claude/projects/<project>/memory/
 
# Read the main memory index
cat ~/.claude/projects/<project>/memory/MEMORY.md
 
# Read a specific topic file
cat ~/.claude/projects/<project>/memory/debugging.md
```

These are plain markdown files. Edit them whenever you want. Delete entries that are outdated. Reorganize as your project evolves.

## Configuration and Control

Auto memory ships enabled by default. Here are all the ways to control it:

### Toggle Per Session

Run `/memory` and use the auto-memory toggle. This is the quickest way to flip it on or off for your current workflow.

### Disable for All Projects

Add this to your user settings:

```
// ~/.claude/settings.json
{ "autoMemoryEnabled": false }
```

### Disable for a Single Project

Add this to the project settings:

```
// .claude/settings.json
{ "autoMemoryEnabled": false }
```

### Environment Variable Override

The `CLAUDE_CODE_DISABLE_AUTO_MEMORY` environment variable overrides all other settings. This is the right choice for CI pipelines, automated environments, and managed deployments:

```
export CLAUDE_CODE_DISABLE_AUTO_MEMORY=1  # Force off
export CLAUDE_CODE_DISABLE_AUTO_MEMORY=0  # Force on
```

This takes precedence over both the `/memory` toggle and `settings.json`, making it the definitive kill switch.

## When to Use What

With three memory systems available, here's a practical decision framework:

**Use CLAUDE.md when** you want to enforce rules. Coding standards, architecture decisions, required commands, and team conventions belong here. CLAUDE.md loads in full at startup with high priority. If you want Claude to always follow a pattern, put it in CLAUDE.md.

**Use auto memory when** you want Claude to learn organically. Project patterns that emerge during work, debugging solutions, and implicit preferences are perfect for auto memory. You don't need to anticipate everything upfront.

**Use Session Memory when** you need conversation continuity. Session Memory tracks what you discussed and decided in specific sessions. It's the "what did we do yesterday" system.

**Use the [rules directory](/blog/rules-directory) when** your CLAUDE.md grows too large. Split instructions into focused files under `.claude/rules/` for better organization without losing priority.

The overlap between these systems is intentional. Auto memory catches things you forget to write in CLAUDE.md. Session Memory provides context that auto memory's project-level notes don't capture. Together they create layered memory that covers project rules, project knowledge, and conversation history.

## Best Practices

**Keep MEMORY.md under 200 lines.** Only the first 200 lines load at startup. Claude is instructed to keep it concise by moving detailed notes into separate topic files. If you're editing manually, respect this boundary.

**Review auto memory periodically.** Like any notes, these can become stale. After major refactors or architecture changes, skim your memory files and delete outdated entries.

**Don't duplicate between CLAUDE.md and auto memory.** If something is important enough to be a rule, put it in [CLAUDE.md](/blog/claude-md-mastery). If it's a learned pattern that might change, let auto memory handle it.

**Use explicit saves for critical knowledge.** When you solve a hard debugging problem or make an important architecture decision, tell Claude to remember it. Don't rely on Claude noticing everything on its own.

**Disable auto memory in CI.** Automated pipelines don't need Claude accumulating notes about your build environment. Set `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` in your CI configuration.

**Combine with context engineering.** Auto memory is one layer in a broader [context engineering](/blog/context-engineering) strategy. The more deliberately you structure what Claude knows at startup, the better every session performs.

## Next Steps

- Set up your CLAUDE.md memory system for persistent project instructions
- Understand [Session Memory](/blog/session-memory) for cross-session conversation continuity
- Learn context management strategies to work within token limits
- Explore the [rules directory](/blog/rules-directory) for modular project instructions
- Read about [context engineering](/blog/context-engineering) for production AI memory systems

Auto memory closes the gap between what you tell Claude and what Claude figures out on its own. CLAUDE.md handles the "do it this way" instructions. Auto memory handles the "I noticed this about your project" knowledge. Together, they mean fewer repeated explanations and more time building.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
