---
sidebar_position: 3
title: Context Preservation
description: Seamless continuation across auto-compaction cycles
---

# Context Preservation

Seamless continuation across auto-compaction cycles.

Claude Code reserves ~16.5% of the context window as a compaction buffer, triggering auto-compaction at ~83.5% raw usage. Pilot hooks intercept this cycle to preserve state — you never lose progress mid-task. Multiple Pilot sessions can run in parallel on the same project without interference.

## The Compaction Cycle

```
PreCompact → Compact → SessionStart(compact)
```

1. **PreCompact** — `pre_compact.py` captures active plan, task list, recent decisions, and key context to Pilot Shell Console memory.
2. **Compact** — Claude Code auto-compaction summarizes conversation history. Preserves recent tool calls and conversation flow.
3. **SessionStart(compact)** — `post_compact_restore.py` re-injects Pilot context: active plan path, task state, key decisions. Work resumes seamlessly.

## Effective Context Display

Pilot rescales the raw context usage to an **effective 0–100% range** so the status bar fills naturally to 100% right before compaction fires. A `▓` buffer indicator at the end of the bar shows the reserved zone. The context monitor warns at ~80% effective (informational) and ~90%+ effective (caution) — no confusing raw percentages.

## What Gets Preserved

The PreCompact hook captures:

- Active plan file path and current status (PENDING/COMPLETE/VERIFIED)
- Task count and directory reference
- Custom instructions from the session

Memory observations (decisions, discoveries, bugfixes) persist independently in SQLite — they survive compaction regardless of hooks.

:::tip Never rush due to context warnings
Context limits are not an emergency — auto-compaction preserves everything and resumes seamlessly. Finish the current task with full quality. The only thing that matters is the output, not the context percentage.
:::
