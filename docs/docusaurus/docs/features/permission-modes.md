---
sidebar_position: 10
title: Permission Modes
description: How Pilot Shell configures Claude Code permission modes — controlling when Claude asks before reading or writing.
---

# Permission Modes

:::warning Claude Code only
Permission modes are a Claude Code concept. Codex configures tool approval through `approval_policy` in `~/.codex/config.toml`.
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

## Cross-Session Messages

Claude Code sessions on the same machine can message each other over a socket at `/tmp/cc-socks/<pid>.sock`. The `crossSessionInbound` setting decides what happens to an inbound message:

| Value | Behavior |
|-------|----------|
| `accept` | **Pilot's default** — delivered straight into the session, no prompt |
| `hold` | Claude Code's default — prompts for approval when the sender's permission mode class differs from yours |
| `refuse` | Dropped silently, no prompt |

Pilot ships `"crossSessionInbound": "accept"` because it is the only value under which
two sessions can actually align without you in the loop. Both alternatives break that:
`refuse` drops the message, and `hold` raises a modal approval prompt that takes over the
terminal — which stalls an unattended `/spec` or `/build` run until you answer it.

The case this exists for is real. Two sessions working the same repository will edit the
same files, and the one that finds out second wastes its work. A session that can say
"I moved the comparison row, rebase your assumptions" is worth the exposure below.

```json
{
  "crossSessionInbound": "hold"
}
```

Set it to `hold` in `~/.claude/settings.json` if you want peer messages reviewed before
Claude sees them, or `refuse` to opt out entirely. Your choice is preserved across updates.

:::caution What `accept` costs you
`accept` delivers peer instructions into a session that executes without prompting, so any
other local session can steer your run. It is not only Claude Code that can reach the
inbox: the socket accepts anything running as your operating-system user, so treat a peer
message as input from your own machine rather than as a trusted instruction.

Pilot takes that trade deliberately, because every session on your machine is already
yours and already runs under `bypassPermissions`. On a shared or multi-tenant machine,
set `hold` instead — that is what the mode-mismatch check was built for.
:::

## Auto Mode

Auto Mode runs a classifier on each action before it executes, blocking anything outside the task scope. Available on **Max, Team, or Enterprise** plans (not Pro). Requires Claude Sonnet 4.6+ or Opus 4.7+.

Blocked by default: downloading and executing scripts, production deploys, mass deletion, IAM changes, force-push to main. Allowed: local file operations, installing from lock files, read-only HTTP.

If the classifier blocks 3 consecutive or 20 total actions, Auto Mode pauses and standard prompts resume.

See [Claude Code permission modes](https://code.claude.com/docs/en/permission-modes) for the full reference.
