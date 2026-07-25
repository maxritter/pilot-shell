---
sidebar_position: 4
title: Pilot CLI
description: Command reference for the pilot admin binary — license activation, updates, worktrees, bot mode, and customization.
---

# Pilot CLI

Admin command reference for the `pilot` binary at `~/.pilot/bin/pilot`.

:::note Pilot does not launch your agent
Pilot Shell loads automatically when you run `claude` or `codex` — there is no wrapper command. The `pilot` CLI is for admin tasks only: license management, updates, worktrees, bot mode, customization, and diagnostics. Most commands support `--json` for structured output.
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

## Updates

| Command | Description |
|---------|-------------|
| `pilot update [--yes] [--json]` | Update Pilot Shell. `pilot upgrade` is an alias. Pass `--yes` to skip the confirmation prompt. |
| `pilot --version` | Show Pilot Shell version |

Update Claude Code and Codex CLI through their own installers independently — `pilot update` only updates Pilot Shell itself.

## Worktree isolation

Used by the `/spec` workflow to keep work isolated until verification passes. All commands work with both Claude Code and Codex sessions.

| Command | Description |
|---------|-------------|
| `pilot worktree create --json <slug>` | Create isolated git worktree |
| `pilot worktree detect --json <slug>` | Check if a worktree already exists |
| `pilot worktree diff --json <slug>` | List changed files in the worktree |
| `pilot worktree sync --json <slug>` | Squash merge worktree changes back to base branch |
| `pilot worktree cleanup --json <slug>` | Remove worktree and branch (`--force` after a sync — still verifies the work reached the base branch; `--discard` to delete unmerged work) |
| `pilot worktree status --json` | Show active worktree info for current session |

:::info Slug format
The `<slug>` is the plan filename without the date prefix and `.md` extension. Example: `docs/plans/2026-02-22-add-auth.md` → `add-auth`.
:::

## Bot mode *(Claude Code only)*

| Command | Description |
|---------|-------------|
| `pilot bot` | Launch [Pilot Bot](/docs/features/bot) — persistent automation session with scheduled tasks, background jobs, and optional Telegram |

## Customization (Team / Enterprise)

Compose custom steps into core workflow skills and ship team rules, hooks, and agents. Source is either a git URL (team-wide) or a local directory (personal). See [Customization](/docs/features/customization) for the full overlay schema.

| Command | Description |
|---------|-------------|
| `pilot customize install <source> [--branch <b>] [--subfolder <p>] [--json]` | Install and apply. `<source>` = git URL or local directory path. |
| `pilot customize update [--json]` | Re-apply — pulls git sources, reads local sources in place |
| `pilot customize status [--json]` | Show active source, file counts, and drift warnings |
| `pilot customize diff <skill>/<step-id> [--json]` | Unified diff between pinned replacement and current upstream |
| `pilot customize remove [--json]` | Delete pack files and regenerate pristine `SKILL.md` |

## Internal commands

Called by hooks and the Console — you rarely need to run these directly.

| Command | Description |
|---------|-------------|
| `pilot check-context --json` | Get current context usage percentage |
| `pilot register-plan <path> <status>` | Associate a plan file with the current session. Prints a warning when `<path>` is outside `docs/plans/` — the Console only displays plans in `<project>/docs/plans/` or `<project>/.worktrees/<slug>/docs/plans/` |
| `pilot review-scope [--slug <slug>] [--json]` | Resolve the `git diff` scope a code review should read — the single source of truth for review diff scope. Prints a range you splice directly (`git diff $(pilot review-scope) -- <files>`); `--json` adds `mode` (`working-tree` or `worktree`), `base_ref`, and a `warning` when the scope degraded. In worktree mode it returns the fork-point range `<base_branch>...HEAD` against the branch's *detected* base — never a hardcoded `main`, and never a two-dot range against the base branch's live tip |
| `pilot sessions [--json]` | Show count of active Pilot sessions |
| `pilot statusline` | Status line formatter *(Claude Code only — called by Claude Code's statusLine hook)* |
| `pilot notify <type> <title> <message> [--plan-path PATH] [--json]` | Send a notification to the Console dashboard (type: `info`, `plan_approval`, `attention_needed`, `verification_complete`) |
| `pilot skill-build <skill-dir> [--output <path>] [--dry-run] [--json]` | Build `SKILL.md` and `hashes.json` from a skill's manifest + fragments |
