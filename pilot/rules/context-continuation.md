# Context Management — Auto-Compaction

**Context management is fully automatic.** Auto-compaction fires at ~83% context, preserves Pilot state via hooks, and restores context seamlessly. **No context is ever lost.**

## How Auto-Compaction Works

When context reaches ~83%, Claude Code's auto-compaction automatically:
1. **PreCompact hook** captures Pilot state (active plan, task progress, key context) to Memory
2. **Compaction** summarizes the conversation, preserving recent work and context
3. **SessionStart(compact) hook** re-injects Pilot-specific context after compaction
4. **You continue working** — no interruption, no manual action needed

## Context Levels

| Level | What Happens |
|-------|--------------|
| < 65% | Work normally |
| 65%   | Informational notice: "Auto-compact will handle context management automatically" |
| 75%+  | Caution: "Auto-compact approaching. Complete current work — do NOT start new complex tasks" |
| ~83%  | Auto-compaction fires automatically — state preserved, context restored |

## ⛔ NEVER Rush — Quality Is Always Priority #1

**Context limits are not the enemy. No context is ever lost.** Auto-compaction preserves everything: your task list, plan state, recent files, key decisions, and conversation flow. After compaction, you continue exactly where you left off.

**When you see context warnings:**
- Do NOT cut corners or skip steps
- Do NOT reduce test coverage or skip verification
- Do NOT compress your output or skip explanations
- Do NOT try to "finish quickly before context runs out"
- Simply complete the current task with full quality — compaction handles the rest

Work spans compaction cycles seamlessly via:
- Automatic compaction preserving critical state
- Pilot Memory capturing decisions and progress
- Plan files and task lists surviving across compaction
- Recent files automatically rehydrated after compaction

## What You Don't Need to Do

- ❌ Worrying about when to `/compact` (auto-compact handles this)
- ❌ Writing continuation files (PreCompact hook captures state)
- ❌ Stopping work at 75% (complete current task, then auto-compact fires)
- ❌ Worrying about context percentage (informational only)
- ❌ Rushing to finish before compaction (quality over speed, always)

## What Gets Preserved

Auto-compaction preserves:
- **Recent work** (last 5 files read, recent tool calls)
- **Task list** (Claude Code's built-in task management)
- **Pilot state** (active plan, current task, key decisions via hooks)
- **Conversation flow** (summarized, not lost)

## Working Across Compaction Cycles

When auto-compact completes, you'll see:
```
[Pilot Context Restored After Compaction]
Active Plan: docs/plans/2026-02-16-feature.md (Status: PENDING, Task 3 in progress)
```

This context injection happens automatically. Just continue working as if nothing happened.

## Pilot Commands

```bash
~/.pilot/bin/pilot check-context --json    # Check context % (informational only)
```

No other context-related commands needed — auto-compaction handles everything.
