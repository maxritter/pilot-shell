---
sidebar_position: 3
title: Context Optimization
description: Strategies for maximizing effective context usage across the 200K and 1M context windows
---

# Context Optimization

Strategies for maximizing effective context usage.

With 1M context windows (API subscribers on Team and Enterprise get this with all models; Max plan users must set all models to Opus), compaction is rare — most sessions complete well within the available context. Pilot Shell's optimization strategies focus on **keeping context lean** so Claude spends tokens on your code, not on overhead.

## Token Reduction

Pilot Shell reduces context consumption at multiple levels:

| Strategy | Savings | How |
|----------|---------|-----|
| **context-mode sandbox** | Up to 98% | Routes large-output commands to a sandboxed executor — only your printed summary enters context. An FTS5 knowledge base indexes content for on-demand search. Blocks curl/wget/WebFetch entirely. |
| **RTK proxy** | 60–90% | Rewrites dev tool output (`git status`, `npm test`, etc.) to remove noise before it enters the context window |
| **Conditional rule loading** | Variable | Coding standards load only for matching file types — Python rules don't load when editing TypeScript |
| **Progressive skill disclosure** | ~90% | Skill frontmatter (~100 tokens) loads always; full SKILL.md loads only on activation; linked files load on demand |
| **Scoped MCP tools** | Variable | MCP tool schemas are lazy-loaded via `ToolSearch` — only fetched when needed, not preloaded |

### context-mode

The biggest single source of context savings. When a command would dump 50KB+ of output into your context window, context-mode intercepts it and runs it in a sandbox instead. The tool hierarchy:

1. **`ctx_batch_execute`** — Run multiple commands + search in one call. Replaces 30+ individual tool calls.
2. **`ctx_search`** — Query indexed content. Pass all questions as an array in one call.
3. **`ctx_execute` / `ctx_execute_file`** — Run code in sandbox (JS, Python, shell). Only stdout enters context.

PreToolUse hooks automatically guide Claude toward these tools when it attempts commands that would produce large output. Session continuity hooks (PostToolUse, PreCompact, SessionStart) track 13 event categories across compactions so context-mode can restore session awareness after auto-compaction.

## Context Display

The status line shows context usage as a visual progress bar:

```
Opus 4.6 [1M] | █████░▓ 60% | ...
```

Claude Code reserves ~16.5% of the context window as a compaction buffer, triggering auto-compaction at ~83.5% raw usage. Pilot Shell rescales this to an **effective 0–100% range** so the bar fills naturally to 100% right before compaction fires. A `▓` buffer indicator shows the reserved zone. The context monitor warns at ~80% effective (informational) and ~90%+ effective (caution).

## Compaction Resilience

When compaction does fire (more common on 200K windows), Pilot Shell preserves state automatically:

```
PreCompact → Compact → SessionStart(compact)
```

1. **PreCompact** — `pre_compact.py` captures active plan, task list, recent decisions, and key context to Pilot Shell Console memory.
2. **Compact** — Claude Code summarizes conversation history. Preserves recent tool calls and conversation flow.
3. **SessionStart(compact)** — `post_compact_restore.py` re-injects Pilot context: active plan path, task state, key decisions. Work resumes seamlessly.

Memory observations (decisions, discoveries, bugfixes) persist independently in SQLite — they survive compaction regardless of hooks.

## Parallel Sessions

Multiple Pilot Shell sessions can run on the same project without interference. Each session has its own context window, task list, and plan state. The Console dashboard tracks all active sessions.

:::tip Never rush due to context warnings
Context limits are not an emergency — auto-compaction preserves everything and resumes seamlessly. Finish the current task with full quality. The only thing that matters is the output, not the context percentage.
:::
