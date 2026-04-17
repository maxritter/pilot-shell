---
sidebar_position: 3
title: Context Optimization
description: Keep the context window lean and recover cleanly when it fills up
---

# Context Optimization

Two things matter for a long-running Claude session: keeping the context window lean so tokens go to your code, and handling the moments when it fills up anyway.

With 1M context windows (API subscribers on Team and Enterprise get this on all models; Max plan users must set all models to Opus), compaction is rare — most sessions complete well within the available context. Pilot Shell's strategies focus on **staying lean**, and making **compaction and parallel work** painless when they happen.

## Keeping context lean

| Strategy | Savings | How |
|----------|---------|-----|
| **context-mode sandbox** | Up to 98% | Routes large-output commands to a sandboxed executor — only your printed summary enters context. An FTS5 knowledge base indexes content for on-demand search. Blocks curl/wget/WebFetch entirely. |
| **RTK proxy** | 60–90% | Rewrites dev tool output (`git status`, `npm test`, etc.) to remove noise before it enters the context window |
| **Conditional rule loading** | Variable | Coding standards load only for matching file types — Python rules don't load when editing TypeScript |
| **Progressive skill disclosure** | ~90% | Skill frontmatter (~100 tokens) loads always; full SKILL.md loads only on activation; linked files load on demand |
| **Scoped MCP tools** | Variable | MCP tool schemas are lazy-loaded via `ToolSearch` — only fetched when needed, not preloaded |

### context-mode in detail

The biggest single source of context savings. When a command would dump 50KB+ of output into your context window, context-mode intercepts it and runs it in a sandbox. The tool hierarchy:

1. **`ctx_batch_execute`** — Run multiple commands + search in one call. Replaces 30+ individual tool calls.
2. **`ctx_search`** — Query indexed content. Pass all questions as an array in one call.
3. **`ctx_execute` / `ctx_execute_file`** — Run code in sandbox (JS, Python, shell). Only stdout enters context.

PreToolUse hooks automatically guide Claude toward these tools when it attempts commands that would produce large output. Session continuity hooks (PostToolUse, PreCompact, SessionStart) track 13 event categories across compactions.

## Status line display

The status line shows context usage as a visual progress bar:

```
Opus 4.7 [1M] | █████░▓ 60% | ...
```

Claude Code reserves ~16.5% of the context window as a compaction buffer, triggering auto-compaction at ~83.5% raw usage. Pilot Shell rescales this to an **effective 0–100% range** so the bar fills naturally to 100% right before compaction fires. A `▓` indicator shows the reserved zone. The monitor warns at ~80% effective (informational) and ~90%+ effective (caution).

## When compaction fires

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
