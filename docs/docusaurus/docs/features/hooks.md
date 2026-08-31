---
sidebar_position: 2
title: Hooks Pipeline
description: Quality and lifecycle hooks for Claude Code and Codex, including context recovery, memory, workflow guards, and SessionEnd handling.
---

# Hooks Pipeline

Lifecycle hooks enforce quality automatically throughout **Claude Code** workflows and connect Pilot's context and memory lifecycle to **Codex**. They are registered in `~/.claude/settings.json` for Claude Code and `~/.codex/hooks.json` for Codex CLI and ChatGPT desktop's Codex runtime. The tables below show which hooks apply to each agent.

Blocking hooks reject actions or force fixes before they land. Non-blocking hooks warn without interrupting. Hook output is user-visible in both clients.

Pilot installs and updates its lifecycle integrations as one managed set. The tables below describe the user-relevant behavior of that pipeline.

Codex runs the skill refresh, session registration, memory observer, and turn summarizer as native asynchronous command hooks. Repository synchronization, workflow guards, context injection, compaction, and SessionEnd remain synchronous because their result must be observed before the lifecycle event completes. Pilot does not register an MCP hook merely as a transport substitute; an MCP handler belongs here only when an installed server owns a concrete lifecycle operation and returns the hook contract directly.

## SessionStart

*On startup, after `/clear`, or after compaction*

| Hook | Applies to | Description |
|------|------------|-------------|
| `session_announcements.py` | Claude Code | Delivers one-time announcements and re-injects them until acknowledged. |
| `config_dir_guard.py` | Claude Code | Warns when the active Claude configuration directory differs from the installed profile. |
| `session_startup_maintenance.py` | Claude Code | Cleans stale Claude task files and dead PID-backed session directories. |
| `codegraph_init.py` | Claude Code | Initializes CodeGraph for the current project. |
| Skill sync | Both | Refreshes managed skills for the active agent. |
| Worker context bootstrap | Both | Restores the memory digest and active session context through the Console worker. |
| `post_compact_restore.py` | Both | Re-injects active plan and task state after compaction. |
| `session_clear.py` | Both | Resets Pilot session state after `/clear`. |

## UserPromptSubmit

*When you send a message*

| Hook | Applies to | Description |
|------|------------|-------------|
| `spec_mode_guard.py` | Claude Code | Warns outside bypassPermissions, blocks manual plan mode, and applies the configured `/spec` model-switching checks; Manual/Off modes have no model gate. |
| Session initializer | Both | Registers the session with the Console worker. |

## PreToolUse

*Before Bash, search, or web tools run*

| Hook | Applies to | Description |
|------|------------|-------------|
| `tool_redirect.py` | Claude Code | Nudges recursive Bash and built-in search calls toward the indexed code-search tools; blocks unsupported web paths. |
| `tool_token_saver.py` | Both | Rewrites eligible Bash commands through RTK for 60–90% smaller output. |
| `plan_mode_tracker.py` | Claude Code | Tracks `/spec` plan-mode state, verifies the observed planning-leg model, and reports the result once per leg. |

## PermissionRequest *(Claude Code only)*

*When a tool call would show a permission dialog*

| Hook | Description |
|------|-------------|
| `auto_approve_plan.py` | Allows `ExitPlanMode` as the `/spec` model-switch lever (denies it while a registered spec plan awaits approval), and restores `bypassPermissions` after a plan-mode exit: current Claude Code builds drop the session to `acceptEdits` or manual mode on exit, so when the session was observed in bypass before the planning leg, the hook re-applies bypass on the first permission request that follows — no prompt is shown |

## PostToolUse

*After file edits, reads, and searches*

| Hook | Applies to | Description |
|------|------------|-------------|
| `plan_mode_tracker.py` | Claude Code | Tracks entry to and exit from Claude Code plan mode for `/spec`. |
| `file_checker.py` | Claude Code | Runs the existing edit-time lint/format checks and TDD reminder. |
| `context_monitor.py` | Claude Code | Tracks context use and warns as compaction approaches. |
| Memory observer | Both | Saves decisions, discoveries, and bugfixes. |

## PreCompact

| Hook | Applies to | Description |
|------|------------|-------------|
| `pre_compact.py` | Both | Snapshots active work before compaction so the next SessionStart can restore it. |

## Stop

*When the agent finishes*

| Hook | Applies to | Description |
|------|------------|-------------|
| `spec_stop_guard.py` | Both | Holds a registered `/spec` or `/build` open until its completion rules are met. |
| Session summarizer | Both | Saves the turn's durable observations. |

`spec_plan_validator.py` runs as a command-scoped Stop hook during the `/spec` planning phases, holding the turn open until the run's plan file exists. It is satisfied by **this session's own** registered plan, so a plan another session is working on in the same directory does not release your planning run. Without a registration it falls back to scanning for a plan dated today, skipping any file another session has registered — see [Registering a plan](plan-format#registering-a-plan).

## SessionEnd

| Hook | Applies to | Description |
|------|------------|-------------|
| `session_end.py --session-end` | Both | Completes the real session, waits for the team-memory export attempt, then stops the Console worker only when no other session remains. Codex now uses its native SessionEnd event rather than treating every Stop as a session boundary. |

:::info Compaction resilience
When compaction fires: **PreCompact** captures active state → compaction runs → **SessionStart** restores it via `post_compact_restore.py`. Work continues from the saved state on both agents.
:::
