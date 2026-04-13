---
sidebar_position: 2
title: Hooks Pipeline
description: 15 hooks across 7 lifecycle events — fire automatically at every stage
---

# Hooks Pipeline

15 hooks across 7 lifecycle events — quality enforcement on autopilot.

Blocking hooks reject actions or force fixes. Non-blocking hooks warn without interrupting. Async hooks run in the background. Two additional command-scoped Stop hooks run during `/spec` phases.

## SessionStart

*On startup, clear, or after compaction*

| Hook | Type | Description |
|------|------|-------------|
| Worker context bootstrap | Blocking | Restores session context through the worker service on startup, `/clear`, and after compaction |
| `post_compact_restore.py` | Blocking | Re-injects the active plan and task state after compaction |
| `session_clear.py` | Blocking | Resets Pilot session state on `/clear` |
| Session tracker | Async | Starts background session activity tracking |

## UserPromptSubmit

*When the user sends a message*

| Hook | Type | Description |
|------|------|-------------|
| `spec_mode_guard.py` | Blocking | Blocks `/spec` in plan mode, warns when not in bypassPermissions mode |
| Session initializer | Async | Registers the session with the Console worker daemon |

## PreToolUse

*Before Bash, search, web, or agent tools run*

| Hook | Type | Description |
|------|------|-------------|
| `tool_redirect.py` | Blocking | Redirects to MCP alternatives, blocks unsupported web fetch paths, and enforces `/spec`-compatible tool usage |
| `tool_token_saver.py` | Blocking | Rewrites Bash commands via RTK for token savings (60-90% reduction) |

## PostToolUse

*After file edits, reads, searches, and task tools*

| Hook | Type | Description |
|------|------|-------------|
| `file_checker.py` | Blocking | Quality checks: Python (ruff), TypeScript (ESLint), Go (go vet + golangci-lint). Also warns when implementation files are edited without a failing test (TDD) |
| `context_monitor.py` | Non-blocking | Tracks context usage 0-100% with warnings as compaction approaches |
| Memory observer | Async | Captures decisions, discoveries, and bugfixes to persistent memory |

## PreCompact

*Before auto-compaction fires*

| Hook | Type | Description |
|------|------|-------------|
| `pre_compact.py` | Blocking | Snapshots active plan and task list to memory |

## Stop

*When Claude tries to finish*

| Hook | Type | Description |
|------|------|-------------|
| `spec_stop_guard.py` | Blocking | Blocks stopping if an active spec hasn't completed verification |
| Session summarizer | Async | Saves session observations to memory |

Additionally, `spec_plan_validator.py` and `spec_verify_validator.py` run as command-scoped Stop hooks during `/spec` phases — they verify plan creation and VERIFIED status respectively.

## SessionEnd

*When the session closes*

| Hook | Type | Description |
|------|------|-------------|
| `session_end.py` | Blocking | Stops worker daemon if no other sessions active, sends dashboard notification |

:::info Closed loop
When compaction fires, **PreCompact** snapshots your active plan and task list to persistent memory. **SessionStart** restores the working state afterward through the worker service and `post_compact_restore.py` so progress survives compaction.
:::
