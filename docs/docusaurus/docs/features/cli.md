---
sidebar_position: 4
title: Pilot CLI
description: Command reference for the pilot binary at ~/.pilot/bin/pilot
---

# Pilot CLI

Command reference for the `pilot` binary at `~/.pilot/bin/pilot`.

Run `pilot` or `ccp` with no arguments to start Claude with Pilot enhancements. Most commands support `--json` for structured output. Multiple sessions can run in parallel on the same project.

## Headless Mode

Run Pilot non-interactively with `-p` (or `--print`). Wraps `claude -p` with license validation and the Pilot plugin — use it in CI/CD pipelines, scripts, or automated workflows.

```bash
# Basic usage
pilot -p "What does the auth module do?"

# Structured JSON output
pilot -p "Summarize this project" --output-format json

# Auto-approve specific tools
pilot -p "Run tests and fix failures" --allowedTools "Bash,Read,Edit"

# Streaming output
pilot -p "Explain recursion" --output-format stream-json --verbose

# Continue a previous conversation
pilot -p "Now focus on the database queries" --continue

# Minimal startup (skip hooks, plugins, MCP auto-discovery)
pilot -p "Summarize this file" --bare --allowedTools "Read"
```

All [Claude Code CLI flags](https://code.claude.com/docs/en/cli-reference) work with `-p`, including `--output-format`, `--allowedTools`, `--continue`, `--resume`, `--append-system-prompt`, `--json-schema`, and `--bare`. Pilot-specific flags like `--skip-update-check` are stripped automatically.

## Session & Context

| Command | Description |
|---------|-------------|
| `pilot` | Start Claude with Pilot enhancements, auto-update, and license check |
| `pilot -p "prompt" [flags...]` | Headless mode — run non-interactively with Pilot plugin (CI/CD, scripts) |
| `pilot run [args...]` | Same as interactive, with optional flags (`--skip-update-check`) |
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
