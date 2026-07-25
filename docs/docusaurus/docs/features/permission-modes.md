---
sidebar_position: 10
title: Permission Modes
description: How Pilot Shell configures Claude Code permission modes — controlling when Claude asks before reading or writing.
---

# Permission Modes

:::warning Claude Code only
Permission modes are a Claude Code concept. For Codex CLI, the equivalent is `approval_policy` in `~/.codex/config.toml` — Pilot sets it to `"never"` by default.
:::

Permission modes control whether Claude asks before acting.

## Default: Bypass Permissions

Pilot Shell sets Claude Code to `bypassPermissions` by default so `/spec` can run autonomously without permission prompts. Quality hooks (linting, TDD, type checking) act as the safety layer.

:::caution Trusted environments only
Use `bypassPermissions` in local dev, containers, or VMs — not on production infrastructure.
:::

## Modes

| Mode | Claude can do without asking | Best for |
|------|------------------------------|----------|
| **Normal** | Read files | Sensitive or unfamiliar work |
| **Accept Edits** | Read and edit files | Daily coding |
| **Plan** | Read files (proposes changes, you approve) | Reviewing before `/spec` |
| **Auto** | Everything — classifier reviews each action | Long autonomous tasks |
| **Bypass Permissions** | Everything, no checks | `/spec` workflow, containers |

Press `Shift+Tab` in Quick Mode to cycle through modes.

:::tip Use /spec instead of plan mode
Claude Code's built-in plan mode has no persistent format. `/spec` saves plans as markdown in `docs/plans/`, drives TDD, and runs full verification. Use `/spec`.
:::

## Set a Persistent Default

Edit `defaultMode` in `~/.claude/settings.json`:

```json
{
  "permissions": {
    "defaultMode": "acceptEdits"
  }
}
```

Pilot preserves your `defaultMode` across updates.

## Auto Mode

Auto Mode runs a classifier on each action before it executes, blocking anything outside the task scope. Available on **Max, Team, or Enterprise** plans (not Pro). Requires Claude Sonnet 4.6+ or Opus 4.7+.

Blocked by default: downloading and executing scripts, production deploys, mass deletion, IAM changes, force-push to main. Allowed: local file operations, installing from lock files, read-only HTTP.

If the classifier blocks 3 consecutive or 20 total actions, Auto Mode pauses and standard prompts resume.

See [Claude Code permission modes](https://code.claude.com/docs/en/permission-modes) for the full reference.
