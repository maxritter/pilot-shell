---
title: "Claude Code: Load Different Starting Context by Session"
description: "Use --init with slash commands to load different context per session type. A simpler alternative to setup hooks for context loading."
slug: claude-code-session-context
date: 2026-01-27
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Use --init with slash commands to load different context per session type. A simpler alternative to setup hooks for context loading.

<!-- truncate -->

Different work needs different context. Writing blog posts requires brand guidelines and SEO workflows. Building features requires architecture docs and coding patterns. Debugging needs system diagrams and error handling conventions.

You could put everything in CLAUDE.md and hope Claude figures out what's relevant. Or you could load the right context for each session type.

## The Simple Solution

Claude Code accepts a prompt after the `--init` flag:

```
claude --init "/blog"
```

This starts Claude and immediately executes the `/blog` slash command. That command can load whatever context you need: writing guidelines, content workflows, example posts, linking strategies.

No setup hooks. No environment variables. No file copying. Just a command file that contains your context.

## When Setup Hooks Are Overkill

[Setup hooks](/blog/claude-code-setup-hooks) (released January 25th, 2026) combine deterministic scripts with agentic oversight. They install dependencies, initialize databases, and run maintenance tasks.

But if you only need to **load context** for a session type, setup hooks add complexity you don't need. A slash command does the job with less moving parts.

| Need | Solution |
| --- | --- |
| Install dependencies, run migrations | Setup hooks |
| Load context for different work types | Slash commands |
| CI/CD automation with deterministic behavior | `claude --init-only` |
| Interactive onboarding with questions | Setup hooks + `/install true` |

## Our Implementation

We use this pattern for blog writing sessions. The file structure:

```
.claude/
  commands/
    blog.md     # Context embedded in command
justfile        # Launcher shortcuts
```

The `blog.md` command contains everything needed for a blog session: brand voice guidelines, content workflow documentation, loading tier instructions, SEO checklists, internal linking rules.

The justfile provides a shortcut:

```
blog:
    claude --init "/blog"
```

Running `just blog` starts a Claude session with all blog context loaded. The session knows the brand voice, understands the linking strategy, and follows the content workflow without being told.

### Launchers Are Mode Selectors Too, and That Cuts Both Ways

A justfile recipe loads context. It also sets environment, and that second job is much easier to forget you gave it.

We ran Claude Code in agent-teams mode for weeks without knowing. A launcher recipe exported `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` on the way into the session, and nothing downstream ever said so. `/config` showed nothing. `settings.json` showed nothing. The session behaved differently from a default session in one specific and consequential way, which is that sub-agent reports stop auto-returning to the caller and have to be sent explicitly, and every symptom of that got attributed to something else for weeks.

An environment variable set inside a launcher script is invisible in exactly the places you would look for it. That is not the launcher's fault, it is what launchers do. The fix is to stop hiding the mode and start naming it:

```
# Classic: sub-agents auto-return their results
cc:
    claude
 
# Teams: peers coordinate, reports must be sent explicitly
team:
    CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude --settings .claude/settings.teams.json
```

Now the mode is a thing you choose by name at the moment you start work, rather than a property your terminal quietly has. Two rules make this hold up:

**One recipe per mode, never a default that differs from bare `claude`.** If `just dev` sets a mode flag, someone will eventually run `claude` directly, get different behaviour, and have no way to see why.

**Pair conditional config with the recipe that needs it.** Teams mode wants a different hook layer than classic mode, and `--settings` is how you attach it to the launcher rather than to the repo. A hook that only makes sense for teammates should not be loading in a solo session.

The general principle is worth more than the specific flag: **anything that changes how a session behaves should be visible at the moment you start the session.** Context loading already follows that rule, which is the whole point of this pattern. Mode selection should follow it too.

## What Goes in a Context Command

A good session context command includes:

**Startup message**: Tell Claude what kind of session this is and report that context is loaded.

**Workflow documentation**: The steps and processes for this type of work.

**Reference material**: Guidelines, examples, checklists that apply to every task in this session.

**Quality gates**: What to check before considering work complete.

Here's the structure:

```
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

## Multiple Session Types

You can create commands for each type of work:

```
.claude/commands/
  blog.md       # Blog writing context
  feature.md    # Feature development context
  debug.md      # Debugging context
  review.md     # Code review context
```

Each command loads the specific guidelines, workflows, and reference material for that session type. Starting the right kind of session is one command:

```
just blog     # Blog writing
just feature  # Feature development
just debug    # Debugging session
```

## Why This Works

The `--init` flag runs your command before any user interaction. By the time you type your first message, Claude already has the context loaded. You skip the "load these files first" dance and get straight to work.

For [skills](/blog/claude-skills-guide), this pattern means loading the right skill configuration automatically. For [CLAUDE.md](/blog/claude-md-mastery) overrides, it means session-specific instructions without cluttering your base configuration.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
