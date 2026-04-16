---
sidebar_position: 3
title: Permission Modes
description: How Pilot Shell configures Claude Code permissions — from full autonomy to manual approval
---

# Permission Modes

Permission modes control whether Claude asks before acting. Different tasks call for different levels of autonomy: full oversight for sensitive work, minimal interruptions for a long refactor, or read-only access while exploring a codebase.

## Default: Bypass Permissions

Pilot Shell sets Claude Code to `bypassPermissions` mode by default. This enables the `/spec` workflow to run autonomously — planning, implementing, and verifying without pausing for permission prompts. All permission checks are disabled and every tool call executes immediately.

This is safe because Pilot Shell adds its own quality layer on top: [hooks](/docs/features/hooks) enforce linting, type checking, TDD, and other guardrails that catch issues before they land.

:::caution Only for trusted environments
`bypassPermissions` disables all safety checks. Use it in environments where Claude cannot cause damage to your host system — local development machines, containers, VMs, or devcontainers. If you work on production infrastructure directly, consider switching to a more restrictive mode.
:::

## Quick Mode Permissions

**In Quick Mode (regular chat), you control the permission level.** Press `Shift+Tab` to cycle through modes. The current mode appears in the status bar.

| Mode | What Claude can do without asking | Best for |
|------|-----------------------------------|----------|
| **Normal** (`default`) | Read files | Getting started, sensitive work |
| **Accept Edits** (`acceptEdits`) | Read and edit files | Iterating on code you're reviewing |
| **Plan** (`plan`) | Read files (proposes changes, you approve) | Exploring a codebase, planning a refactor |
| **Bypass Permissions** (`bypassPermissions`) | All actions, no checks | Isolated containers and VMs, `/spec` workflow |
| **Auto** (`auto`) | All actions, with background safety checks | Long-running tasks, reducing prompt fatigue |

`bypassPermissions` appears in the cycle only if your session started with it (Pilot Shell's default). `auto` appears only when `--enable-auto-mode` is passed at startup — Pilot Shell does this automatically.

## Setting a Persistent Default

Change `defaultMode` in `~/.claude/settings.json`:

```json
{
  "permissions": {
    "defaultMode": "acceptEdits"
  }
}
```

The Pilot Shell installer uses three-way merge — your customizations to `defaultMode` and other permission settings are preserved across updates.

## Plan Mode

Plan mode tells Claude to research and propose changes without making them. Claude reads files, runs shell commands to explore, and writes a plan — but does not edit your source code. Permission prompts work the same as Normal mode: you still approve Bash commands, network requests, and other actions that would normally prompt.

:::tip Use /spec instead of plan mode
Claude Code's built-in plan mode (`Shift+Tab` → "plan") is unstructured — plans aren't saved as files, have no consistent format, and disappear when the session ends. Use `/spec` as a drop-in replacement: plans are saved as structured markdown in `docs/plans/`, persist across sessions, and drive a complete workflow with TDD and verification. See the [spec workflow guide](/docs/workflows/spec).
:::

## Auto Mode

Pilot Shell passes `--enable-auto-mode` to Claude Code at launch, making Auto Mode available in the `Shift+Tab` permission cycle. Auto Mode lets Claude execute actions without showing permission prompts — a separate classifier model reviews each action before it runs and blocks anything that escalates beyond the task scope.

:::warning Availability
Auto Mode is available on **Max, Team, or Enterprise plans**, or with **API access**. It is **not available on the Pro plan**. On Team and Enterprise plans, an admin must enable it in [Claude Code admin settings](https://claude.ai/admin-settings/claude-code) before users can turn it on. It also requires **Claude Sonnet 4.6 or Opus 4.7** — older models and third-party providers (Bedrock, Vertex, Foundry) are not supported.
:::

### How the Classifier Works

The classifier runs on Claude Sonnet 4.6 (even if your main session uses a different model). Each action goes through a fixed decision order — the first matching step wins:

1. Actions matching your allow/deny rules resolve immediately
2. Read-only actions and file edits in your working directory are auto-approved
3. Everything else goes to the classifier
4. If the classifier blocks an action, Claude receives the reason and tries an alternative approach

The classifier receives user messages and tool calls as input, with Claude's own text and tool results stripped out. It also reads your `CLAUDE.md` content, so project instructions factor into allow/block decisions. Because tool results never reach the classifier, hostile content in files or web pages cannot manipulate it.

**Cost:** Classifier calls count toward your token usage. The extra cost comes mainly from shell commands and network operations — read-only actions and file edits don't trigger a classifier call.

### Blocked by Default

- Downloading and executing code (`curl | bash`, scripts from cloned repos)
- Sending sensitive data to external endpoints
- Production deploys and migrations
- Mass deletion on cloud storage
- Granting IAM or repository permissions
- Modifying shared infrastructure
- Irreversibly destroying files that existed before the session started
- Destructive source control operations (force push, pushing directly to `main`)

### Allowed by Default

- Local file operations in your working directory
- Installing dependencies from your lock files or manifests
- Reading `.env` and sending credentials to their matching API
- Read-only HTTP requests
- Pushing to the branch you started on or one Claude created

### Configuring Trusted Infrastructure

The classifier trusts your working directory and your git repo's configured remotes. Everything else is treated as external. If Auto Mode blocks something routine for your team — like pushing to your org's repo or writing to a company bucket — an administrator can add trusted infrastructure via `autoMode.environment` in managed settings. See [Configure the auto mode classifier](https://code.claude.com/docs/en/permissions#configure-the-auto-mode-classifier) for the full guide.

### Subagents in Auto Mode

When Claude spawns a subagent, the classifier evaluates the delegated task before the subagent starts. Inside the subagent, Auto Mode runs with the same block and allow rules as the parent session. When the subagent finishes, the classifier reviews its full action history — if it flags a concern, a security warning is prepended to the results.

### Fallback Behavior

If the classifier blocks 3 consecutive actions or 20 total in one session, Auto Mode pauses and Claude Code resumes standard permission prompts. Approving a prompted action resets the counters so you can continue in Auto Mode.

## Comparison

| | Normal | Accept Edits | Plan | Auto | Bypass Permissions |
|---|---|---|---|---|---|
| **Permission prompts** | File edits and commands | Commands only | File edits and commands | None unless fallback triggers | None |
| **Safety checks** | You review each action | You review commands | You review each action | Classifier reviews commands | None |
| **Token usage** | Standard | Standard | Standard | Higher (classifier calls) | Standard |
| **Best with Pilot** | Exploring unfamiliar code | Quick Mode daily work | Reviewing before `/spec` | Long autonomous tasks | `/spec` workflow (default) |

## Further Reading

- [Claude Code permission modes](https://code.claude.com/docs/en/permission-modes) — full reference for all modes
- [Claude Code permissions](https://code.claude.com/docs/en/permissions) — allow, ask, and deny rules
- [Auto Mode announcement](https://claude.com/blog/auto-mode) — how the classifier is designed
