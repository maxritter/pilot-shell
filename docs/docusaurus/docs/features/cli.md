---
sidebar_position: 4
title: Pilot CLI
description: Command reference for the pilot binary at ~/.pilot/bin/pilot
---

# Pilot CLI

Command reference for the `pilot` binary at `~/.pilot/bin/pilot`.

Run `pilot` or `ccp` with no arguments to start Claude with Pilot enhancements. Most commands support `--json` for structured output. Multiple sessions can run in parallel on the same project.

## Session & context

| Command | Description |
|---------|-------------|
| `pilot` | Start Claude with Pilot enhancements, auto-update, and license check |
| `pilot [claude-flags...]` | Start Claude with any Claude CLI flags passed through |
| `pilot -p "prompt" [flags...]` | Headless mode — non-interactive for CI/CD, scripts |
| `pilot run [flags...]` | Explicit alias for starting Claude |
| `ccp` | Alias for `pilot` |
| `pilot check-context --json` | Get current context usage percentage |
| `pilot register-plan <path> <status>` | Associate a plan file with the current session |
| `pilot sessions [--json]` | Show count of active Pilot sessions |
| `pilot statusline` | Run the status line formatter (called by Claude Code) |
| `pilot notify <type> <title> <message> [--plan-path PATH] [--json]` | Send a notification to the Console dashboard (type: `info`, `plan_approval`, `attention_needed`, `verification_complete`) |
| `pilot skill-build <skill-dir> [--output <path>] [--dry-run] [--json]` | Build `SKILL.md` and `hashes.json` from a skill's manifest + fragments |
| `pilot --version` | Show Pilot Shell version |

## Bot mode

| Command | Description |
|---------|-------------|
| `pilot bot` | Launch Pilot Bot — persistent automation session with scheduled tasks, background jobs, and optional Telegram |

## Worktree isolation

| Command | Description |
|---------|-------------|
| `pilot worktree create --json <slug>` | Create isolated git worktree |
| `pilot worktree detect --json <slug>` | Check if a worktree already exists |
| `pilot worktree diff --json <slug>` | List changed files in the worktree |
| `pilot worktree sync --json <slug>` | Squash merge worktree changes back to base branch |
| `pilot worktree cleanup --json <slug>` | Remove worktree and branch (`--force` to skip checks, `--discard` to drop changes) |
| `pilot worktree status --json` | Show active worktree info for current session |

:::info Slug format
The `<slug>` for worktree commands is the plan filename without the date prefix and `.md` extension. Example: `docs/plans/2026-02-22-add-auth.md` → `add-auth`.
:::

## License & auth

| Command | Description |
|---------|-------------|
| `pilot activate <key>` | Activate a license key on this machine |
| `pilot deactivate` | Deactivate license on this machine |
| `pilot status [--json]` | Show current license status and tier |
| `pilot verify [--json]` | Verify license validity (used by hooks) |
| `pilot trial --check [--json]` | Check trial eligibility for this machine |
| `pilot trial --start [--json]` | Start a trial (one-time per machine) |

## Customization (Team / Enterprise)

Compose custom steps into core workflow skills and ship team rules, hooks, and agents. Source is either a git URL (team-wide) or a local directory (personal). See [Customization](/docs/features/customization) for the full overlay schema.

| Command | Description |
|---------|-------------|
| `pilot customize install <source> [--branch <b>] [--subfolder <p>] [--json]` | Install and apply. `<source>` = git URL or local directory path. `--branch` applies to git sources only. |
| `pilot customize update [--json]` | Re-apply — pulls git sources, reads local sources in place |
| `pilot customize status [--json]` | Show active source, file counts, and drift warnings |
| `pilot customize diff <skill>/<step-id> [--json]` | Unified diff between pinned replacement and current upstream |
| `pilot customize remove [--json]` | Delete pack files and regenerate pristine `SKILL.md` |

## Claude CLI flag passthrough

Pilot forwards any unrecognized flags directly to the Claude CLI — all current and future Claude Code flags work out of the box, no Pilot update required.

```bash
# Any Claude CLI flag works directly
pilot --channels plugin:telegram@claude-plugins-official
pilot --model opus --verbose
pilot --resume
pilot --continue

# 'run' is an explicit alias — same behavior
pilot run --channels plugin:telegram@claude-plugins-official
```

Pilot only intercepts its own subcommands (`activate`, `status`, `worktree`, etc.) and flags (`--version`, `--skip-update-check`). Everything else passes through to `claude`.

## Headless mode

Run Pilot non-interactively with `-p` (or `--print`). Wraps `claude -p` with license validation and the Pilot plugin — use it in CI/CD pipelines, scripts, or automated workflows.

```bash
# Basic usage
pilot -p "What does the auth module do?"

# Structured JSON output
pilot -p "Summarize this project" --output-format json

# Auto-approve specific tools
pilot -p "Run tests and fix failures" --allowedTools "Bash,Read,Edit"

# With channels
pilot --channels plugin:telegram@claude-plugins-official -p "Check messages"

# Continue a previous conversation
pilot -p "Now focus on the database queries" --continue

# Minimal startup (skip hooks, plugins, MCP auto-discovery)
pilot -p "Summarize this file" --bare --allowedTools "Read"
```

All [Claude Code CLI flags](https://code.claude.com/docs/en/cli-reference) work with `-p`, including `--output-format`, `--allowedTools`, `--continue`, `--resume`, `--channels`, `--append-system-prompt`, `--json-schema`, and `--bare`. Pilot-specific flags like `--skip-update-check` are stripped automatically.
