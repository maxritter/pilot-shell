---
sidebar_position: 3
title: Context Optimization
description: Keep the context window lean and recover cleanly when it fills up — strategies and memory persistence for Claude Code and Codex.
---

# Context Optimization

Two things matter for a long-running session: keeping the context window lean so tokens go to your code, and handling the moments when it fills up anyway.

These strategies apply to both **Claude Code** and **Codex CLI**. Claude Code uses automatic compaction. For Codex, Pilot enables the native experimental context manager unless `experimental_mode` is already set explicitly in `config.toml`.

## Native Codex context management

Pilot adds this default during installation:

```toml
[features]
context_management.experimental_mode = true
```

For eligible ChatGPT-backed Codex sessions, this keeps notes across context windows, makes earlier thread history searchable, and exposes Codex's `new_context` tool. Codex ignores the feature for unsupported plans, custom providers, provider credentials, non-Codex endpoints, and temporary structured threads.

Pilot also requests `model_context_window = 1050000` and
`model_auto_compact_token_limit = 922000`, matching Astra's published total
window and maximum input. These remain safe global defaults for GPT-5.6 Sol and
its Terra/Luna siblings as well as older models: Pilot lifts the four published
full-window models (Astra, Sol, Terra, Luna) to 1,050,000 in its provider-derived
catalog. Codex clamps every other selected model to its own catalog ceiling, then
caps auto-compaction at 90% of that resolved window. A genuinely smaller model
therefore keeps its smaller boundary instead of inheriting Astra's limits.

Pilot memory remains the cross-session layer. Its observer and summarizer continue to save durable project knowledge locally, but Codex does not receive an automatic Pilot memory digest. Before non-trivial work on existing behavior, Codex searches the local `mem-search` MCP with the current task, uses `timeline` for surrounding context, and fetches only selected observations. This produces smaller, more relevant context than loading a recency-based digest before the task is known.

API-key, custom-provider, and otherwise ineligible Codex sessions ignore the native experimental mode. They still have on-demand Pilot memory for cross-session recall, while their current thread follows Codex's ordinary context behavior.

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

## Session-start memory digest *(Claude Code only)*

At `startup`, `clear`, and `compact`, Pilot injects a digest of recent memory for the project: a table of recent observations by day and file, the last session summary, and the previous assistant message. Claude Code caps a SessionStart hook's `additionalContext` at 10,000 characters and hands the model only a short preview of anything longer, so the digest is rendered to a budget: `CLAUDE_PILOT_CONTEXT_MAX_CHARS` in `~/.pilot/memory/settings.json` (default `9000`, `0` for no cap). When the budget is exceeded, whole days are dropped from the old end first and a line says how many older entries were left out; they remain searchable through the `mem-search` MCP server or `bun ~/.pilot/scripts/worker-service.cjs search "<query>" --json`. `CLAUDE_PILOT_CONTEXT_OBSERVATIONS` (default `50`) and `CLAUDE_PILOT_CONTEXT_FULL_COUNT` (default `10`) still bound how much is fetched before the budget applies.

:::tip Don't rush the current task
Context limits are not an emergency — auto-compaction preserves everything and resumes cleanly. Finish the current task with full quality. The only thing that matters is the output, not the context percentage.
:::

## Running parallel sessions

Multiple Pilot Shell sessions can run on the same project without interference. Each session has its own context window, task list, and plan state. The Console dashboard tracks every active session so you can jump between them.
