---
slug: "session-memory"
title: "Claude Code Session Memory: Automatic Cross-Session Context"
description: "Claude Code Session Memory auto-recalls past work and writes summaries in the background. Learn how it works and where files live."
date: "2026-02-04"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 6
keywords: "automatic, claude, code, context, crosssession, memory, session"
---

Mechanics

# Claude Code Session Memory: How Your AI Remembers Across Sessions

Claude Code Session Memory auto-recalls past work and writes summaries in the background. Learn how it works and where files live.

**Problem**: You start a new Claude Code session and spend the first five minutes re-explaining what you built yesterday. Claude has no idea you already solved the auth flow, picked a database schema, or decided on the API structure.

**Quick Win**: Check if Session Memory is already working for you. Open your terminal and look for these messages when you start Claude Code:

```p-4
Recalled 3 memories (ctrl+o to expand)
```

If you see that, Claude already loaded summaries from your past sessions. Press `ctrl+o` to see exactly what it remembered. If you don't see it yet, keep reading to understand when and how it activates.

## [What Session Memory Actually Is](#what-session-memory-actually-is)

Session Memory is Claude Code's automatic background system for remembering what you did across sessions. Unlike [CLAUDE.md](/blog/guide/mechanics/memory-optimization), which you write and maintain manually, Session Memory runs without any input from you. It watches your conversation, extracts the important parts, and saves structured summaries to disk.

You'll notice two types of terminal messages:

- **"Recalled X memories"** appears at session start. Claude loaded summaries from previous sessions in this project.
- **"Wrote X memories"** appears periodically during your session. Claude just saved a snapshot of your current work.

Both messages include `(ctrl+o to expand)` so you can inspect exactly what was recalled or written.

## [How It Works Under the Hood](#how-it-works-under-the-hood)

Session Memory runs as a background process during every session. Here's the mechanics.

### [Storage Location](#storage-location)

Claude stores session summaries as structured markdown files at:

```p-4
~/.claude/projects/<project-hash>/<session-id>/session-memory/summary.md
```

Each session gets its own directory with its own summary file. These accumulate over time, building a history of your work on each project.

### [Extraction Cadence](#extraction-cadence)

Session Memory doesn't save on every message. It follows a specific rhythm:

- **First extraction**: Triggers after roughly 10,000 tokens of conversation
- **Subsequent updates**: Every ~5,000 tokens or after every 3 tool calls, whichever comes first

This cadence keeps the summaries useful without burning compute on trivial exchanges. Short "fix this typo" sessions produce minimal summaries. Deep architecture discussions produce detailed ones.

### [Cross-Session Recall](#cross-session-recall)

When you start a new session, Claude injects relevant past session summaries into its context. These summaries carry a note: *"from PAST sessions that might not be related to the current task."* Claude uses them as background knowledge, not as active instructions.

This means Claude won't blindly follow decisions from three weeks ago. It treats past sessions as reference material, giving you the continuity of context without the rigidity of hard-coded instructions.

## [What Gets Remembered](#what-gets-remembered)

Each session summary follows a consistent structure:

- **Session title**: An auto-generated description of what you worked on (e.g., "Implement user dashboard with role-based access")
- **Current status**: Completed items, discussion points, open questions
- **Key results**: Important outcomes, decisions made, patterns chosen
- **Work log**: A chronological record of actions taken during the session

The summary captures *what* you did and *why*, not a transcript of every message. This compression is what makes it useful. A two-hour session becomes a focused summary that Claude can load in seconds.

## [The /remember Command](#the-remember-command)

Session Memory stores raw history. The `/remember` command turns that history into permanent project knowledge.

When you run `/remember`, Claude reviews your session memories stored at the summary path, identifies recurring patterns across sessions, and proposes updates to `CLAUDE.local.md`. You confirm each proposed addition before it's written.

For example, if Claude notices you've corrected the same coding pattern across three sessions ("always use server actions instead of API routes"), `/remember` surfaces that as a candidate for [permanent memory](/blog/guide/mechanics/memory-optimization). Once added to your CLAUDE.local.md, Claude follows the pattern from session start instead of needing a reminder.

Think of it as the bridge between automatic memory and deliberate configuration.

## [Instant Compaction](#instant-compaction)

Before Session Memory existed, running `/compact` meant waiting up to two minutes while Claude re-analyzed your entire conversation to produce a summary. Now `/compact` is instant.

Because Session Memory writes summaries continuously in the background, compaction just loads the pre-written summary into a fresh context window. No re-analysis needed. Your [context management](/blog/guide/mechanics/context-management) workflow gets faster and more reliable.

This matters most during long sessions. Instead of dreading the compaction pause when you hit 80% context usage, you can compact freely. The summary is always ready.

## [Availability and Requirements](#availability-and-requirements)

Session Memory is available on the first-party Anthropic API. If you're using Claude Code through a Claude Pro or Max subscription, it works automatically.

A few things to know about availability:

- **API providers**: Bedrock, Vertex, and Foundry users don't have access to Session Memory. The feature requires Anthropic's native API infrastructure.
- **Feature gating**: Session Memory is gated behind the `tengu_session_memory` Statsig feature flag. A related flag, `tengu_sm_compact`, enables the instant compaction behavior.
- **Timeline**: The underlying system has existed since roughly v2.0.64 in late 2025. The visible terminal messages ("Recalled/Wrote memories") became prominent around v2.1.30 and v2.1.31 in early February 2026.

If you're on a supported plan and don't see the messages, your account may not have the feature flag enabled yet. This is a gradual rollout.

## [Working With Session Memory](#working-with-session-memory)

### [Inspect Your Stored Memories](#inspect-your-stored-memories)

Browse your session memories directly:

```p-4
# Find your project's memory directory
ls ~/.claude/projects/
 
# List all sessions for a specific project
ls ~/.claude/projects/<project-hash>/
 
# Read a specific session's summary
cat ~/.claude/projects/<project-hash>/<session-id>/session-memory/summary.md
```

### [Maximize What Gets Captured](#maximize-what-gets-captured)

Session Memory extracts more useful summaries when your sessions have clear structure:

- **State your intent early**: "I'm building the payment integration using Stripe" gives Claude a clear session title
- **Summarize decisions explicitly**: "We decided on webhook-based sync instead of polling" becomes a key result
- **Ask Claude to document**: "Document the architecture decisions we just made" triggers a richer extraction

### [Understand the Relationship With CLAUDE.md](#understand-the-relationship-with-claudemd)

Session Memory and [CLAUDE.md](/blog/guide/mechanics/claude-md-mastery) serve different purposes and work together:

| Aspect | Session Memory | CLAUDE.md |
| --- | --- | --- |
| **Created by** | Claude (automatic) | You (manual) |
| **Scope** | Per-session snapshots | Persistent project rules |
| **Priority** | Background reference | High-priority instructions |
| **Best for** | Continuity, context recall | Standards, architecture, commands |

The strongest setup uses both. Session Memory provides continuity between work sessions. CLAUDE.md provides the authoritative rules Claude follows. The `/remember` command bridges the two by promoting recurring patterns from session memory into permanent configuration.

## [Next Steps](#next-steps)

- Set up your [CLAUDE.md memory system](/blog/guide/mechanics/memory-optimization) for persistent project instructions
- Learn [context management strategies](/blog/guide/mechanics/context-management) to work within token limits
- Explore [context preservation](/blog/guide/performance/context-preservation) for advanced cross-session workflows
- Understand [context engineering](/blog/guide/mechanics/context-engineering) for production AI systems

Session Memory is one of those features that works best when you don't think about it. It runs in the background, saves what matters, and loads it when relevant. The next time you start a session and Claude already knows what you did yesterday, that's Session Memory doing its job.

Last updated on

[Previous

Memory Optimization](/blog/guide/mechanics/memory-optimization)[Next

Output Formatting](/blog/guide/mechanics/output-formatting)
