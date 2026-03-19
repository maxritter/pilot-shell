---
sidebar_position: 4
title: Pilot CLI
description: Command reference for the pilot binary at ~/.pilot/bin/pilot
---

# Pilot CLI

Command reference for the `pilot` binary at `~/.pilot/bin/pilot`.

Run `pilot` or `ccp` with no arguments to start Claude with Pilot enhancements. Most commands support `--json` for structured output. Multiple sessions can run in parallel on the same project.

## Session & Context

| Command | Description |
|---------|-------------|
| `pilot` | Start Claude with Pilot enhancements, auto-update, and license check |
| `pilot run [args...]` | Same as above, with optional flags (`--skip-update-check`) |
| `ccp` | Alias for pilot |
| `pilot check-context --json` | Get current context usage percentage |
| `pilot register-plan <path> <status>` | Associate a plan file with the current session |
| `pilot sessions [--json]` | Show count of active Pilot sessions |
| `pilot statusline` | Run the status line formatter (called by Claude Code) |
| `pilot notify <event> [data]` | Send a notification to the Console dashboard |
| `pilot --version` | Show Pilot Shell version |

## Worktree Isolation

| Command | Description |
|---------|-------------|
| `pilot worktree create --json <slug>` | Create isolated git worktree |
| `pilot worktree detect --json <slug>` | Check if a worktree already exists |
| `pilot worktree diff --json <slug>` | List changed files in the worktree |
| `pilot worktree sync --json <slug>` | Squash merge worktree changes back to base branch |
| `pilot worktree cleanup --json <slug>` | Remove worktree and branch (`--force` to skip checks, `--discard` to drop changes) |
| `pilot worktree status --json` | Show active worktree info for current session |

## License & Auth

| Command | Description |
|---------|-------------|
| `pilot activate <key>` | Activate a license key on this machine |
| `pilot deactivate` | Deactivate license on this machine |
| `pilot status [--json]` | Show current license status and tier |
| `pilot verify [--json]` | Verify license validity (used by hooks) |
| `pilot trial --check [--json]` | Check trial eligibility for this machine |
| `pilot trial --start [--json]` | Start a trial (one-time per machine) |

:::info Slug format
The `<slug>` parameter for worktree commands is the plan filename without the date prefix and `.md` extension. For example, `docs/plans/2026-02-22-add-auth.md` → `add-auth`.
:::
