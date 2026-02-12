---
slug: "claude-code-session-context"
title: "Claude Code: Load Different Starting Context by Session"
description: "Use --init with slash commands to load different context per session type. A simpler alternative to setup hooks for context loading."
date: "2026-01-27"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 4
keywords: "by, claude, code, context, different, load, session, starting"
---

Mechanics

# Load Different Context Based on Session Type in Claude Code

Use --init with slash commands to load different context per session type. A simpler alternative to setup hooks for context loading.

Different work needs different context. Writing blog posts requires brand guidelines and SEO workflows. Building features requires architecture docs and coding patterns. Debugging needs system diagrams and error handling conventions.

You could put everything in CLAUDE.md and hope Claude figures out what's relevant. Or you could load the right context for each session type.

## [The Simple Solution](#the-simple-solution)

Claude Code accepts a prompt after the `--init` flag:

```p-4
claude --init "/blog"
```

This starts Claude and immediately executes the `/blog` slash command. That command can load whatever context you need: writing guidelines, content workflows, example posts, linking strategies.

No setup hooks. No environment variables. No file copying. Just a command file that contains your context.

## [When Setup Hooks Are Overkill](#when-setup-hooks-are-overkill)

[Setup hooks](/blog/tools/hooks/claude-code-setup-hooks) (released January 25th, 2026) combine deterministic scripts with agentic oversight. They install dependencies, initialize databases, and run maintenance tasks.

But if you only need to **load context** for a session type, setup hooks add complexity you don't need. A slash command does the job with less moving parts.

| Need | Solution |
| --- | --- |
| Install dependencies, run migrations | Setup hooks |
| Load context for different work types | Slash commands |
| CI/CD automation with deterministic behavior | `claude --init-only` |
| Interactive onboarding with questions | Setup hooks + `/install true` |

## [Our Implementation](#our-implementation)

We use this pattern for blog writing sessions. The file structure:

```p-4
.claude/
  commands/
    blog.md     # Context embedded in command
justfile        # Launcher shortcuts
```

The `blog.md` command contains everything needed for a blog session: brand voice guidelines, content workflow documentation, loading tier instructions, SEO checklists, internal linking rules.

The justfile provides a shortcut:

```p-4
blog:
    claude --init "/blog"
```

Running `just blog` starts a Claude session with all blog context loaded. The session knows the brand voice, understands the linking strategy, and follows the content workflow without being told.

## [What Goes in a Context Command](#what-goes-in-a-context-command)

A good session context command includes:

**Startup message**: Tell Claude what kind of session this is and report that context is loaded.

**Workflow documentation**: The steps and processes for this type of work.

**Reference material**: Guidelines, examples, checklists that apply to every task in this session.

**Quality gates**: What to check before considering work complete.

Here's the structure:

```p-4
---
description: Start a blog writing session with pre-loaded context
---
 
# Blog Session
 
You are starting a blog/content writing session. Report: "Blog session started."
 
---
 
## Content Workflow
 
[Workflow steps and process documentation]
 
## Brand Voice
 
[Guidelines and patterns]
 
## Quality Checklist
 
[Verification steps before publishing]
```

The context lives directly in the command file. When the command runs, Claude has everything it needs.

## [Multiple Session Types](#multiple-session-types)

You can create commands for each type of work:

```p-4
.claude/commands/
  blog.md       # Blog writing context
  feature.md    # Feature development context
  debug.md      # Debugging context
  review.md     # Code review context
```

Each command loads the specific guidelines, workflows, and reference material for that session type. Starting the right kind of session is one command:

```p-4
just blog     # Blog writing
just feature  # Feature development
just debug    # Debugging session
```

## [Why This Works](#why-this-works)

The `--init` flag runs your command before any user interaction. By the time you type your first message, Claude already has the context loaded. You skip the "load these files first" dance and get straight to work.

For [skills](/blog/guide/mechanics/claude-skills-guide), this pattern means loading the right skill configuration automatically. For [CLAUDE.md](/blog/guide/mechanics/claude-md-mastery) overrides, it means session-specific instructions without cluttering your base configuration.

Start simple. If you find yourself needing deterministic scripts, installation automation, or agent oversight during setup, move to [setup hooks](/blog/tools/hooks/claude-code-setup-hooks). But for context loading, a slash command is often all you need.

Last updated on

[Previous

Claude Skills Guide](/blog/guide/mechanics/claude-skills-guide)[Next

CLAUDE.md Mastery](/blog/guide/mechanics/claude-md-mastery)
