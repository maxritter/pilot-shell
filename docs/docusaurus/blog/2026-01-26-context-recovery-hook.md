---
title: "Claude Code Context Backups: Beat Auto-Compaction"
description: "Proactively backup your Claude Code session before compaction hits. StatusLine monitoring and threshold triggers keep your work safe."
slug: context-recovery-hook
date: 2026-01-26
authors:
  - max-ritter
tags:
  - tools
  - hooks
---

Proactively backup your Claude Code session before compaction hits. StatusLine monitoring and threshold triggers keep your work safe.

<!-- truncate -->

You're 4 hours into a complex implementation. Context hits 83%. Auto-compaction fires. Suddenly Claude doesn't remember the specific error message you debugged, the exact function signatures you discussed, or the architectural decisions that led to your current approach.

The summary captures the gist. The precision is gone.

Here's the alternative: **backup your session automatically starting at 50K tokens used, updating every 10K tokens after that**. When compaction hits, you have a structured markdown file with every user request, file modification, and key decision preserved. Percentage-based thresholds (30%, 15%, 5% free) serve as a safety net, especially on smaller context windows.

## Why StatusLine Is the Only Solution

Most Claude Code hooks don't receive context metrics. PreToolUse, PostToolUse, Stop - none of them know how much context you've consumed.

StatusLine is different. It receives a JSON payload on every turn with `context_window.remaining_percentage` - live data showing exactly how much room you have left.

```
{
  "session_id": "abc123...",
  "context_window": {
    "remaining_percentage": 35.5,
    "context_window_size": 200000
  }
}
```

This is the ONLY mechanism in Claude Code that provides real-time context visibility. Without it, you're flying blind until compaction hits.

### The Buffer Calculation

Here's what trips people up: that `remaining_percentage` field includes a fixed 33K-token autocompact buffer that you can't actually use. The implementation accounts for this with a token-based calculation rather than a percentage:

```
const AUTOCOMPACT_BUFFER_TOKENS = 33000;
const autocompactBufferPct = (AUTOCOMPACT_BUFFER_TOKENS / windowSize) * 100;
const freeUntilCompact = Math.max(0, pctRemainTotal - autocompactBufferPct);
```

On a 200K window, that 33K buffer is 16.5%. On a 1M window, it's only 3.3%. Using a fixed token count instead of a percentage keeps the calculation accurate across all context window sizes.

## The Dual Trigger System

Auto-compaction is reactive. It fires when you've already used too much context, then throws away detail in the summarization process.

The backup system is proactive, using two trigger systems that run simultaneously:

### Token-Based Triggers (Primary)

| Trigger | When It Fires | Purpose |
| --- | --- | --- |
| **50K tokens** | After 50K total tokens used | First backup, early capture |
| **Every 10K** | 60K, 70K, 80K, 90K, 100K, ... | Regular updates |

This system works identically regardless of context window size. On a 1M window, your first backup fires at just 5% usage. On a 200K window, it fires at 25% usage. Either way, you get early coverage.

### Percentage-Based Triggers (Safety Net)

| Threshold | When It Fires | Purpose |
| --- | --- | --- |
| **30%** | ~60K tokens free until compact | Additional checkpoint |
| **15%** | ~30K tokens free until compact | Getting critical |
| **5%** | ~10K tokens free until compact | Last chance before compaction |
| **Under 5%** | Every context decrease | Continuous backup mode |

The percentage system is a safety net that catches cases the token system might miss (e.g., sessions that start with a large prompt injection). On 200K windows, both systems provide overlapping coverage. On 1M windows, the token system dominates since 30% remaining means you've already used 670K+ tokens.

## Three-File Architecture

A production backup system needs clean separation of concerns. We use three files:

```
.claude/hooks/ContextRecoveryHook/
├── backup-core.mjs        # Shared backup logic
├── statusline-monitor.mjs # Threshold detection + display
└── conv-backup.mjs        # PreCompact hook trigger
```

### backup-core.mjs - The Engine

This file handles everything about creating backups:

- **Transcript parsing**: Reads the JSONL transcript file and extracts user requests, file modifications, tasks, and Claude's key responses
- **Markdown formatting**: Structures the data as a readable markdown file
- **File operations**: Saves numbered backups with timestamps
- **State management**: Tracks which session is active and what the current backup path is

The key insight: backups should be structured, not raw dumps. The markdown format groups information logically so you can quickly find what you need when recovering.

### statusline-monitor.mjs - The Detector

This runs on every turn via StatusLine. Its job:

1. Calculate total tokens used and true "free until compaction" percentage
2. Check token-based triggers (50K first, then every 10K)
3. Check percentage thresholds as safety net (30%, 15%, 5%)
4. Trigger `backup-core` when any trigger fires
5. Display formatted status with backup path

The backup path shows whenever a backup exists for the current session:

```
[!] Opus 4.6 | 65k / 1m | 6% used 65,000 | 90% free 900,000 | thinking: On
-> .claude/backups/3-backup-18th-Feb-2026-2-15pm.md
```

That second line appears as soon as you hit 50K tokens. No waiting until context gets critical.

### conv-backup.mjs - The Safety Net

PreCompact hooks fire right before compaction happens - your last chance to capture state. This file triggers `backup-core` with `precompact_auto` or `precompact_manual` as the trigger reason.

Think of it as the emergency backup. StatusLine-based thresholds are proactive; PreCompact is reactive but still better than losing everything.

## Configuration

The system requires two settings.json entries:

```
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

## Backup File Format

Backups use numbered filenames with human-readable timestamps:

```
.claude/backups/1-backup-26th-Jan-2026-4-30pm.md
.claude/backups/2-backup-26th-Jan-2026-5-15pm.md
.claude/backups/3-backup-26th-Jan-2026-5-45pm.md
```

Inside, you get a structured summary:

```
# Session Backup
 
**Session ID:** abc123...
**Trigger:** tokens_60k_update
**Context Remaining:** 94.0%
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

## The Recovery Workflow

When compaction happens:

1. **StatusLine shows backup path**: You see exactly which file has your latest backup
2. **Run /clear**: Start a fresh session (cleaner than continuing with compacted context)
3. **Load the backup**: Read the markdown file to restore context
4. **Continue work**: Claude now has structured context about what you were doing

The alternative - working with compacted context - means Claude has a summary of your session but has lost the specifics. Loading a structured backup gives you those specifics back.

### Why /clear Instead of Continuing?

After compaction, you have two types of context:

1. **Compaction summary**: Auto-generated, lossy, captures the gist
2. **Loaded backup**: Structured, detailed, captures specifics

Having both can confuse things. The summary might contradict details in the backup. Starting fresh with `/clear` and loading only the backup gives you cleaner, more reliable context.

## State Tracking

Both StatusLine and PreCompact hooks update a shared state file:

This lets the StatusLine monitor know:

- Which session it's tracking (to reset state when sessions change)
- What the last context percentage was (to detect percentage threshold crossings)
- How many tokens were used at the last backup (to calculate the next 10K interval)
- Where the current backup lives (to display in the statusline)

## Transcript Parsing Details

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

## Why This Beats Manual Tracking

You could manually copy important context into a file as you work. But you won't. You're focused on the implementation, not on documentation.

The token-based system runs automatically. Starting at 50K tokens used, you get a backup every 10K tokens without thinking about it. The cognitive load is zero.

And the backups are structured. Not a raw paste of conversation, but organized sections you can scan quickly.

## Comparison: Auto-Compaction vs Threshold Backup

| Aspect | Auto-Compaction | Threshold Backup + /clear |
| --- | --- | --- |
| **When it happens** | At ~83.5% usage | At 50K tokens, then every 10K |
| **What's preserved** | Lossy summary | Structured markdown with full detail |
| **Control** | None (hardcoded) | Configurable token + pct thresholds |
| **Recovery** | Continue with summary | Load specific backup file |
| **Specifics retained** | Only what fits summary | Everything in backup |

Auto-compaction is the default because most users don't set up backup systems. But if you're working on complex, multi-hour sessions where precision matters, token-based backup gives you much better recovery options. On a 1M context window, you'll have dozens of backup snapshots captured throughout the session instead of losing everything to a single compaction event.

## Key Takeaways

1. **StatusLine is the only live context monitor** - Other hooks don't get token counts
2. **Token-based triggers fire early** - First backup at 50K used, then every 10K, regardless of window size
3. **Percentage thresholds are a safety net** - 30%, 15%, 5% free catch edge cases on smaller windows
4. **Raw percentage includes a 33K buffer** - Calculate true "free until compact" using token counts
5. **Structured backups beat raw dumps** - Parse transcripts into organized markdown
6. **Three-file architecture** - Clean separation between detection, backup logic, and triggers
7. **Recovery workflow: /clear + load** - Cleaner than mixing compacted context with backup

## Get the Full Implementation

- Complete `backup-core.mjs` with transcript parsing and markdown formatting
- StatusLine monitor with dual trigger system (token-based + percentage) and visual indicators
- PreCompact hook for emergency backups
- State management across sessions

The full implementation handles edge cases - session changes, transcript discovery, numbered backup sequences, and the critical buffer calculation. All hooks use [cross-platform patterns](/blog/cross-platform-hooks) so they work on Windows, Linux, and macOS without modification.

## Related Resources

- [Context Buffer Management](/blog/context-buffer-management) - Why the 33K-45K buffer exists
- [Claude Code Hooks Guide](/blog/hooks-guide) - All 12 hook types explained
- [Context Engineering](/blog/context-engineering) - Strategic context usage
- [Session Lifecycle Hooks](/blog/session-lifecycle-hooks) - Setup and cleanup automation

[Session Lifecycle](/blog/session-lifecycle-hooks)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** ships a configured hook pipeline for Claude Code — formatter and linter on `PostToolUse`, type-check before stop, context capture on session events. Installed once, applied across every project.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
