---
slug: "context-recovery-hook"
title: "Claude Code Context Backups: Beat Auto-Compaction"
description: "Proactively backup your Claude Code session before compaction hits. StatusLine monitoring and threshold triggers keep your work safe."
date: "2026-01-26"
author: "Max Ritter"
tags: [Guide, Hooks]
readingTime: 8
keywords: "autocompaction, backups, beat, claude, code, context, hook, recovery"
---

Hooks

# Never Lose Work to Compaction: Threshold-Based Context Backups for Claude Code

Proactively backup your Claude Code session before compaction hits. StatusLine monitoring and threshold triggers keep your work safe.

You're 4 hours into a complex implementation. Context hits 83%. Auto-compaction fires. Suddenly Claude doesn't remember the specific error message you debugged, the exact function signatures you discussed, or the architectural decisions that led to your current approach.

The summary captures the gist. The precision is gone.

Here's the alternative: **backup your session at 30%, 15%, and 5% remaining - before compaction destroys your context**. When compaction hits, you have a structured markdown file with every user request, file modification, and key decision preserved.

## [Why StatusLine Is the Only Solution](#why-statusline-is-the-only-solution)

Most Claude Code hooks don't receive context metrics. PreToolUse, PostToolUse, Stop - none of them know how much context you've consumed.

StatusLine is different. It receives a JSON payload on every turn with `context_window.remaining_percentage` - live data showing exactly how much room you have left.

```p-4
{
  "session_id": "abc123...",
  "context_window": {
    "remaining_percentage": 35.5,
    "context_window_size": 200000
  }
}
```

This is the ONLY mechanism in Claude Code that provides real-time context visibility. Without it, you're flying blind until compaction hits.

### [The 16.5% Buffer Calculation](#the-165-buffer-calculation)

Here's what trips people up: that `remaining_percentage` field includes the 16.5% autocompact buffer that you can't actually use. (This was previously 22.5% when the buffer was 45K tokens -- it was [recently reduced to 33K](/blog/guide/mechanics/context-buffer-management).)

When StatusLine reports 25% remaining, you don't have 25% before compaction. You have **8.5%**.

```p-4
const AUTOCOMPACT_BUFFER_PCT = 16.5;
const freeUntilCompact = Math.max(
  0,
  remaining_percentage - AUTOCOMPACT_BUFFER_PCT,
);
```

The threshold-based backup system accounts for this. When we say "backup at 30%", we mean 30% free-until-compaction - which is actually 46.5% remaining in the raw metric.

## [The Threshold Concept](#the-threshold-concept)

Auto-compaction is reactive - it fires when you've already used too much context, then throws away detail in the summarization process.

Threshold-based backup is proactive. Set thresholds at meaningful points:

| Threshold | When It Fires | Purpose |
| --- | --- | --- |
| **30%** | ~60K tokens free until compact | First warning, full backup |
| **15%** | ~30K tokens free until compact | Getting critical, updated backup |
| **5%** | ~10K tokens free until compact | Last chance before compaction |
| **Under 5%** | Every context decrease | Continuous backup mode |

Why these numbers? At 30%, you still have substantial working room but should capture state. At 15%, compaction is approaching. Below 5%, every turn could be your last - so backup continuously.

## [Three-File Architecture](#three-file-architecture)

A production backup system needs clean separation of concerns. We use three files:

```p-4
.claude/hooks/ContextRecoveryHook/
├── backup-core.mjs        # Shared backup logic
├── statusline-monitor.mjs # Threshold detection + display
└── conv-backup.mjs        # PreCompact hook trigger
```

### [backup-core.mjs - The Engine](#backup-coremjs---the-engine)

This file handles everything about creating backups:

- **Transcript parsing**: Reads the JSONL transcript file and extracts user requests, file modifications, tasks, and Claude's key responses
- **Markdown formatting**: Structures the data as a readable markdown file
- **File operations**: Saves numbered backups with timestamps
- **State management**: Tracks which session is active and what the current backup path is

The key insight: backups should be structured, not raw dumps. The markdown format groups information logically so you can quickly find what you need when recovering.

### [statusline-monitor.mjs - The Detector](#statusline-monitormjs---the-detector)

This runs on every turn via StatusLine. Its job:

1. Calculate true "free until compaction" percentage
2. Check if any threshold was crossed (going down)
3. Trigger `backup-core` when thresholds cross
4. Display formatted status with warning indicators

The output format tells you exactly where you stand:

```p-4
[!] 25.0% free (50.0K/200K)
-> .claude/backups/3-backup-26th-Jan-2026-5-45pm.md
```

That second line? It's the file you'll load after compaction. No hunting through directories.

### [conv-backup.mjs - The Safety Net](#conv-backupmjs---the-safety-net)

PreCompact hooks fire right before compaction happens - your last chance to capture state. This file triggers `backup-core` with `precompact_auto` or `precompact_manual` as the trigger reason.

Think of it as the emergency backup. StatusLine-based thresholds are proactive; PreCompact is reactive but still better than losing everything.

## [Configuration](#configuration)

The system requires two settings.json entries:

```p-4
{
  "statusLine": {
    "type": "command",
    "command": "node .claude/hooks/ContextRecoveryHook/statusline-monitor.mjs"
  },
  "hooks": {
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/ContextRecoveryHook/conv-backup.mjs",
            "async": true
          }
        ]
      }
    ]
  }
}
```

The `async: true` on PreCompact matters - backups shouldn't slow down the compaction process.

## [Backup File Format](#backup-file-format)

Backups use numbered filenames with human-readable timestamps:

```p-4
.claude/backups/1-backup-26th-Jan-2026-4-30pm.md
.claude/backups/2-backup-26th-Jan-2026-5-15pm.md
.claude/backups/3-backup-26th-Jan-2026-5-45pm.md
```

Inside, you get a structured summary:

```p-4
# Session Backup

**Session ID:** abc123...
**Trigger:** crossed_30pct_free
**Context Remaining:** 27.5%
**Generated:** 2026-01-26T17:45:00.000Z

## User Requests

- Create two blog posts about context management
- Add the new post to blog-structure.ts
- Fix the internal linking

## Files Modified

- apps/web/src/content/blog/guide/mechanics/context-buffer-management.mdx
- apps/web/src/content/blog/tools/hooks/context-recovery-hook.mdx
- apps/web/src/content/blog/blog-structure.ts

## Tasks

### Created

- **Write Post 1: Context Buffer Management**
- **Write Post 2: Context Recovery Hook**

### Completed

- 2 tasks completed

## Skills Loaded

- content-writer
```

This isn't a raw transcript. It's a structured summary that tells you what happened, what changed, and what's still pending.

## [The Recovery Workflow](#the-recovery-workflow)

When compaction happens:

1. **StatusLine shows backup path**: You see exactly which file has your latest backup
2. **Run /clear**: Start a fresh session (cleaner than continuing with compacted context)
3. **Load the backup**: Read the markdown file to restore context
4. **Continue work**: Claude now has structured context about what you were doing

The alternative - working with compacted context - means Claude has a summary of your session but has lost the specifics. Loading a structured backup gives you those specifics back.

### [Why /clear Instead of Continuing?](#why-clear-instead-of-continuing)

After compaction, you have two types of context:

1. **Compaction summary**: Auto-generated, lossy, captures the gist
2. **Loaded backup**: Structured, detailed, captures specifics

Having both can confuse things. The summary might contradict details in the backup. Starting fresh with `/clear` and loading only the backup gives you cleaner, more reliable context.

## [Transcript Parsing Details](#transcript-parsing-details)

The backup system parses Claude Code's JSONL transcript files to extract meaningful data. Here's what it captures:

| Data Type | How It's Extracted |
| --- | --- |
| **User Requests** | Messages where `type === "user"` |
| **Files Modified** | Write/Edit tool calls with `file_path` |
| **Tasks Created** | TaskCreate tool calls |
| **Tasks Completed** | TaskUpdate with `status === "completed"` |
| **Sub-Agent Calls** | Task tool invocations |
| **Skills Loaded** | Skill tool calls |
| **MCP Tool Usage** | Tool names starting with `mcp__` |
| **Build/Test Runs** | Bash commands containing build/test/npm/pnpm |

The parser filters out noise - tool results, system messages, single-character inputs - to focus on what actually matters for session recovery.

## [Why This Beats Manual Tracking](#why-this-beats-manual-tracking)

You could manually copy important context into a file as you work. But you won't. You're focused on the implementation, not on documentation.

The threshold system runs automatically. Every time context drops through a threshold, you get an updated backup without thinking about it. The cognitive load is zero.

And the backups are structured. Not a raw paste of conversation, but organized sections you can scan quickly.

## [Comparison: Auto-Compaction vs Threshold Backup](#comparison-auto-compaction-vs-threshold-backup)

| Aspect | Auto-Compaction | Threshold Backup + /clear |
| --- | --- | --- |
| **When it happens** | At ~83.5% usage | At configurable thresholds |
| **What's preserved** | Lossy summary | Structured markdown with full detail |
| **Control** | None (hardcoded) | You choose thresholds |
| **Recovery** | Continue with summary | Load specific backup file |
| **Specifics retained** | Only what fits summary | Everything in backup |

Auto-compaction is the default because most users don't set up backup systems. But if you're working on complex, multi-hour sessions where precision matters, threshold-based backup gives you much better recovery options.

## [Key Takeaways](#key-takeaways)

1. **StatusLine is the only live context monitor** - Other hooks don't get token counts
2. **Raw percentage includes 16.5% buffer** - Calculate true "free until compact"
3. **Threshold backups are proactive** - Capture state before compaction, not during
4. **Structured backups beat raw dumps** - Parse transcripts into organized markdown
5. **Three-file architecture** - Clean separation between detection, backup logic, and triggers
6. **Recovery workflow: /clear + load** - Cleaner than mixing compacted context with backup

## [Related Resources](#related-resources)

- [Context Buffer Management](/blog/guide/mechanics/context-buffer-management) - Why the 33K-45K buffer exists
- [Claude Code Hooks Guide](/blog/tools/hooks/hooks-guide) - All 12 hook types explained
- [Context Engineering](/blog/guide/mechanics/context-engineering) - Strategic context usage
- [Session Lifecycle Hooks](/blog/tools/hooks/session-lifecycle-hooks) - Setup and cleanup automation

Last updated on

[Previous

Session Lifecycle](/blog/tools/hooks/session-lifecycle-hooks)[Next

Skill Activation Hook](/blog/tools/hooks/skill-activation-hook)
