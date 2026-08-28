---
sidebar_position: 3
title: Context Optimization
description: Keep the context window lean and recover cleanly when it fills up — strategies and memory persistence for Claude Code and Codex.
---

# Context Optimization

Two things matter for a long-running session: keeping the context window lean so tokens go to your code, and handling the moments when it fills up anyway.

These strategies apply to both **Claude Code** and **Codex CLI**. Compaction (automatic context summarization) applies to Claude Code; on Codex, context is managed per the model's native window.

## Keeping context lean

| Strategy | Savings | How |
|----------|---------|-----|
| **RTK proxy** | 60–90% | Rewrites dev tool output (`git status`, `npm test`, etc.) to remove noise before it enters the context window |
| **Semble code search** | ~98% | Returns only the matched chunks instead of dumping whole files — Semble's own benchmark shows ~98% fewer tokens than `grep + read` at 94% recall |
| **Conditional rule loading** | Variable | Coding standards load only for matching file types — Python rules don't load when editing TypeScript |
| **Progressive skill disclosure** | ~90% | Skill frontmatter (~100 tokens) loads always; full SKILL.md loads only on activation; linked files load on demand |
| **Scoped MCP tools** | Variable | MCP tool schemas are lazy-loaded via `ToolSearch` — only fetched when needed, not preloaded |
| **Routing hooks** | Variable | PreToolUse hooks block `curl`/`wget`/ordinary built-in `WebFetch` requests and redirect to the dedicated web-fetch MCP, while authenticated Claude artifact URLs pass through to the session-aware built-in tool |

## Status line display *(Claude Code only)*

The status line shows context usage as a visual progress bar:

```
Opus 5 [1M] | █████░▓ 60% | ...
```

Claude Code reserves ~16.5% of the context window as a compaction buffer, triggering auto-compaction at ~83.5% raw usage. Pilot Shell rescales this to an **effective 0–100% range** so the bar fills naturally to 100% right before compaction fires. A `▓` indicator shows the reserved zone. The monitor warns at ~80% effective (informational) and ~90%+ effective (caution).

## When compaction fires *(Claude Code only)*

On 200K windows, compaction happens more often. Pilot Shell preserves state automatically across the three lifecycle events:

```
PreCompact → Compact → SessionStart(compact)
```

1. **PreCompact** — `pre_compact.py` captures active plan, task list, recent decisions, and key context to Pilot Shell Console memory.
2. **Compact** — Claude Code summarizes conversation history while preserving recent tool calls and flow.
3. **SessionStart(compact)** — `post_compact_restore.py` re-injects the active plan path, task state, and key decisions. Work resumes seamlessly.

Memory observations (decisions, discoveries, bugfixes) persist independently in SQLite — they survive compaction regardless of hooks.

:::tip Don't rush the current task
Context limits are not an emergency — auto-compaction preserves everything and resumes cleanly. Finish the current task with full quality. The only thing that matters is the output, not the context percentage.
:::

## Running parallel sessions

Multiple Pilot Shell sessions can run on the same project without interference. Each session has its own context window, task list, and plan state. The Console dashboard tracks every active session so you can jump between them.
