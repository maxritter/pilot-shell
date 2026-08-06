---
sidebar_position: 2
title: Hooks Pipeline
description: Quality hooks across lifecycle events — auto-format, lint, type-check, and TDD enforcement that fire automatically at every stage of work.
---

# Hooks Pipeline

Lifecycle hooks enforce quality automatically on every file edit, prompt, and session event. Hooks run on both **Claude Code** and **Codex CLI** — registered in `~/.claude/settings.json` for Claude Code and `~/.codex/hooks.json` for Codex.

Blocking hooks reject actions or force fixes before they land. Non-blocking hooks warn without interrupting. Async hooks run in the background.

## SessionStart

*On startup, after `/clear`, or after compaction*

| Hook | Description |
|------|-------------|
| `license_check.py` | Verifies Pilot Shell license — blocks session if invalid |
| `session_announcements.py` | Delivers one-time announcements; re-injects until acknowledged *(Claude Code only)* |
| `session_startup_maintenance.py` | Cleans stale Claude task files and dead-PID session dirs (async) *(Claude Code only)* |
| `codegraph_init.py` | Initializes CodeGraph for the current project (async) |
| `post_compact_restore.py` | Re-injects active plan and task state after compaction *(Claude Code only)* |
| `session_clear.py` | Resets Pilot session state on `/clear` *(Claude Code only)* |
| Worker context bootstrap | Restores session context through the Console worker *(Claude Code only)* |

## UserPromptSubmit

*When you send a message*

| Hook | Description |
|------|-------------|
| `spec_mode_guard.py` | Warns outside bypassPermissions; blocks manual plan mode; in Automated Model Switching it requires `opusplan` (shows as Sonnet before planning) and pre-flight-warns when the conversation likely exceeds the Opus plan leg's window; Manual/Off have no model gate |
| Session initializer | Registers session with the Console worker (async) |

## PreToolUse

*Before Bash, search, or web tools run*

| Hook | Description |
|------|-------------|
| `tool_redirect.py` | Redirects to MCP alternatives; blocks unsupported web paths *(Claude Code only)* |
| `tool_token_saver.py` | Rewrites Bash commands via RTK for 60–90% token savings |
| `plan_mode_tracker.py` | Tracks the `/spec` plan-mode levers via a session sentinel; verifies the observed planning-leg model against the expected Opus leg and reports it once per leg — confirming when the `opusplan` switch took effect, warning when it did not (e.g. Opus usage-limit fallback). Claude Code announces nothing either way, so both outcomes are surfaced *(Claude Code only)* |

## PermissionRequest *(Claude Code only)*

*When a tool call would show a permission dialog*

| Hook | Description |
|------|-------------|
| `auto_approve_plan.py` | Allows `ExitPlanMode` as the `/spec` model-switch lever (denies it while a registered spec plan awaits approval), and restores `bypassPermissions` after a plan-mode exit: current Claude Code builds drop the session to `acceptEdits` or manual mode on exit, so when the session was observed in bypass before the planning leg, the hook re-applies bypass on the first permission request that follows — no prompt is shown |

## PostToolUse

*After file edits, reads, and searches*

| Hook | Description |
|------|-------------|
| `file_checker.py` | Linting (ruff/ESLint/go vet) plus a C# `dotnet format` whitespace check, and TDD enforcement — warns when editing without a failing test |
| `context_monitor.py` | Tracks context usage 0–100%, warns as compaction approaches |
| Memory observer | Saves decisions, discoveries, and bugfixes to persistent memory (async) |

## PreCompact *(Claude Code only)*

| Hook | Description |
|------|-------------|
| `pre_compact.py` | Snapshots active plan and task list before compaction |

## Stop

*When the agent finishes*

| Hook | Description |
|------|-------------|
| `spec_stop_guard.py` | Blocks stopping if an active spec hasn't completed verification |
| Session summarizer | Saves session observations to memory (async) |
| Team memory auto-export *(Codex only)* | Writes the project's new shared memories to `.pilot/memories/`. Codex has no SessionEnd event, so this stands in for it; it writes nothing when the turn produced no new shareable memory |

`spec_plan_validator.py` runs as a command-scoped Stop hook during the `/spec` planning phases.

## SessionEnd *(Claude Code only)*

| Hook | Description |
|------|-------------|
| `session_end.py` | Stops the Console worker when no sessions remain; marks the session complete, which is what exports its team memories. Invoked with `--session-end` here — Codex registers the same script on `Stop` without that flag, so an end-of-turn run stops the worker but never completes the session |

:::info Compaction resilience
When compaction fires (Claude Code): **PreCompact** captures plan state → compaction runs → **SessionStart** restores it via `post_compact_restore.py`. Work continues without data loss.
:::
