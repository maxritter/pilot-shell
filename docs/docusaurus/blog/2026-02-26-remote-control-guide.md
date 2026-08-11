---
title: "Claude Code Remote Control: Complete Setup Guide (2026)"
description: "Use Claude Code Remote Control to control your local terminal from any device. Setup guide, security model, and how it compares to OpenClaw."
slug: remote-control-guide
date: 2026-02-26
authors:
  - max-ritter
tags:
  - guide
  - development
---

Use Claude Code Remote Control to control your local terminal from any device. Setup guide, security model, and how it compares to OpenClaw.

<!-- truncate -->

**Problem**: You kick off a long-running Claude Code session at your desk, then need to step away. Maybe you're waiting for a build to finish. Maybe you want to check results from the couch. You've got two options: stay chained to your workstation, or lose the session entirely.

**Quick Win**: Start a remote-controllable session from your terminal:

```
claude remote-control
```

This registers your local session with Anthropic's API and gives you a URL and QR code. Open it on your phone, tablet, or any browser. Your full local environment stays available: filesystem, MCP servers, tools, and project configuration. Nothing moves to the cloud.

## What is Remote Control?

Remote Control is a new feature (February 2026, research preview) that bridges your local Claude Code terminal session with [claude.ai/code](https://claude.ai/code), the Claude iOS app, and the Claude Android app. It's a synchronization layer, not a cloud migration. Your session keeps running on your machine the entire time.

The key distinction from [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web): web sessions run on Anthropic-managed cloud infrastructure. Remote Control sessions run on your machine. The web and mobile interfaces are just a window into your local session.

This matters because your local setup is irreplaceable. Your [CLAUDE.md configuration](/blog/claude-md-mastery), custom skills, file access, and MCP integrations all stay available. A cloud session starts fresh. Remote Control keeps everything.

If you prefer messaging apps over the claude.ai interface, check out [Claude Code Channels](/blog/claude-code-channels), which lets you control sessions from Telegram and Discord instead.

## How to Set Up Remote Control

### Requirements

- **Claude Code installed**: If you haven't set up Claude Code yet, follow the installation guide for your platform first.
- **Subscription**: Pro or Max plan required. API keys won't work.
- **Authentication**: Run `claude` and use `/login` to sign in through claude.ai.
- **Workspace trust**: Run `claude` in your project directory at least once to accept the trust dialog.

### Starting a New Session

Navigate to your project directory and run:

```
claude remote-control
```

The process stays running in your terminal. It displays a session URL and you can press spacebar to show a QR code for quick phone access. While active, the terminal shows connection status and tool activity.

Available flags:

- `--verbose` for detailed connection and session logs
- `--sandbox` / `--no-sandbox` to toggle [sandboxing](https://code.claude.com/docs/en/sandboxing) for filesystem and network isolation

### From an Existing Session

Already mid-conversation and want to go mobile? Use the slash command:

```
/remote-control
```

Or the shorthand:

```
/rc
```

This converts your current session to a remote-controllable one, carrying over your full conversation history. Tip: use `/rename` first to give your session a descriptive name so you can find it easily across devices.

### Always-On Remote Control

To enable Remote Control for every session automatically, run `/config` inside Claude Code and set **Enable Remote Control for all sessions** to `true`.

## Connecting from Another Device

Three ways to connect once a session is active:

1. **Open the session URL** directly in any browser at [claude.ai/code](https://claude.ai/code)
2. **Scan the QR code** shown in your terminal (press spacebar to toggle) to open in the Claude mobile app
3. **Browse the session list** in claude.ai/code or the Claude app. Remote Control sessions show a computer icon with a green status dot when online

The conversation stays in sync across all connected devices. You can send messages from your terminal, browser, and phone interchangeably.

Don't have the Claude app yet? Run `/mobile` inside Claude Code to get a download QR code for iOS or Android.

## How It Works Under the Hood

The security model is straightforward. Your local Claude Code session makes **outbound HTTPS requests only**. No inbound ports open on your machine. When you start Remote Control, the process registers with the Anthropic API and polls for work. When you connect from another device, the server routes messages between the client and your local session over a streaming connection.

All traffic flows through the Anthropic API over TLS (the same transport security as any Claude Code session). Multiple short-lived credentials are used, each scoped to a single purpose and expiring independently.

In plain terms: your files and MCP servers never leave your machine. Only chat messages and tool results flow through the encrypted bridge.

## Remote Control vs OpenClaw

If you've been following the [OpenClaw phenomenon](/blog/openclaw-vs-claude-code), you'll recognize the appeal. Controlling your computer from your phone is one of OpenClaw's headline features, and it helped propel the project to 199K GitHub stars.

Remote Control is Anthropic's native answer. Here's how they compare on this specific capability:

| Aspect | Remote Control | OpenClaw |
| --- | --- | --- |
| **Setup** | `claude remote-control` (one command) | Self-hosted, requires port forwarding or tunnel config |
| **Security** | Outbound-only HTTPS, no open ports, TLS encryption, short-lived credentials | WebSocket-based, CVE-2026-25253 RCE vulnerability affected 50K+ instances |
| **Platforms** | claude.ai/code, iOS, Android | WhatsApp, Telegram, Discord, Slack, 15+ platforms |
| **Scope** | Coding-focused (terminal, files, MCP) | General-purpose (calendar, email, smart home, everything) |
| **Cost** | Included with Pro/Max subscription | Free (self-hosted), but you bring your own API keys |
| **Reconnection** | Automatic when laptop wakes from sleep | Manual restart on connection loss |
| **Permissions** | Full Claude Code permission model | Broad system access by default |

The fundamental difference: Remote Control is a secure, purpose-built bridge for development workflows. OpenClaw is a general-purpose life assistant that happens to offer remote device control among many other capabilities. Different tools for different jobs.

For developers who want to continue a coding session from their phone, Remote Control is the cleaner solution. No exposed ports, no WebSocket vulnerabilities, no self-hosting overhead.

## Current Limitations

This is a research preview. Rough edges exist:

- **One session at a time**: Each Claude Code instance supports one remote connection
- **Terminal must stay open**: Close the terminal or stop the `claude` process and the session ends
- **10-minute network timeout**: If your machine can't reach the network for roughly 10 minutes, the session times out. Run `claude remote-control` again to start fresh
- **Permission approval still required**: Even with remote control active, you'll need to approve actions. The `--dangerously-skip-permissions` flag [reportedly doesn't work](https://simonwillison.net/2026/Feb/25/claude-code-remote-control/) with Remote Control yet
- **Availability**: Pro and Max plans only for now. Not available on Team or Enterprise plans

Simon Willison noted some additional rough edges in his initial testing: session crashes can produce "mysterious API errors" instead of clear termination messages, and restarting the process requires starting a new session rather than reconnecting to the old one.

## Practical Workflows

Here are the scenarios where Remote Control shines:

### The "Walk Away" Pattern

Start a complex multi-agent task at your desk, then monitor and steer from your phone while grabbing coffee. Your agents keep running locally with full tool access.

### The "Couch Review" Pattern

Queue up code reviews or test runs at your workstation, then review results and approve actions from the couch. Especially useful with async workflows where tasks run independently and you check in periodically.

### The "Multi-Device" Pattern

Start from your terminal for heavy coding, switch to the browser on your laptop for lighter interactions, then use your phone for quick approvals. The conversation stays perfectly in sync across all three.

### Pair It with Worktrees

For maximum flexibility, combine Remote Control with [git worktrees](/blog/worktree-guide). Start an isolated worktree session, enable remote control, then manage it from anywhere. Your main branch stays untouched while you steer the isolated session remotely.

## What's Next

Remote Control launched alongside Cowork (scheduled tasks), signaling Anthropic's push toward making Claude Code a persistent, always-available development companion. The current limitations, particularly the requirement for the terminal to stay open and the single-session cap, point toward an obvious next step: a fully cloud-hosted Remote Control that doesn't depend on your machine being awake.

For now, Remote Control turns your phone into a window to your terminal. That alone changes how you interact with long-running Claude Code sessions. No more being chained to your desk waiting for a build to finish or an agent to complete its work.

Start with `claude remote-control` and see how it fits your workflow. If you're already running multi-agent setups or long autonomous sessions, the ability to monitor and steer from your phone is a meaningful quality-of-life improvement. Keep an eye on the Claude Code changelog for Remote Control updates as it moves beyond the research preview stage.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
