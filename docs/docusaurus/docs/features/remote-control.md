---
sidebar_position: 6
title: Remote Control
description: Control Pilot Shell sessions from your phone, tablet, or any browser
---

# [Remote Control](https://youtu.be/Ko7_tC1fMMM?si=kWDzYiQvxlkZTrRK)

Control Pilot Shell sessions from your phone, tablet, or any browser.

Start a `/spec` task at your desk, then monitor and steer it from the couch. Your full local environment stays available — filesystem, MCP servers, hooks, rules, and project configuration. Nothing moves to the cloud.

## Prerequisites

Remote Control requires the **native install** of Claude Code, not the npm version. If you have the npm version installed, uninstall it first:

```bash
npm uninstall -g @anthropic-ai/claude-code   # Remove npm version if installed
curl -fsSL https://claude.ai/install.sh | bash  # Install native version
```

You also need a **Pro, Max, Team, or Enterprise** Claude subscription. API keys won't work with Remote Control.

## Setup

### 1. Start Pilot Shell

```bash
pilot
```

Loads all hooks, rules, MCP servers, and project configuration.

### 2. Activate Remote Control

| Method | How |
| ------ | --- |
| **Single session** | Type `/remote-control` inside the Pilot Shell session |
| **All sessions** | Run `/config` in Claude Code and set "Enable Remote Control for all sessions" to `true` |

### 3. Connect from your phone

Open the **Claude Mobile App** ([iOS](https://apps.apple.com/app/claude-by-anthropic/id6473753684) / [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude)) and go to the **Code** tab. Your session appears there with a green status dot when online.

You can also connect from any browser at [claude.ai/code](https://claude.ai/code).

## How it works

Sessions started via `pilot` carry over all rules, hooks, MCP servers, and project configuration. The Claude App and web interface are just a window into your local session — your machine does all the work.

- **Full Pilot Shell experience** — hooks, rules, skills, MCP servers all stay active
- **Outbound-only** — no ports open on your machine, all traffic over TLS
- **Multi-device sync** — send messages from terminal, browser, and phone interchangeably
- **Auto-reconnect** — reconnects automatically when your laptop wakes from sleep

## Starting sessions from your phone via SSH

The setup above assumes you start sessions via `pilot` on your computer first. To start new sessions from your phone instead:

1. Install [Termius](https://termius.com/) on your phone (not your computer)
2. SSH into your computer
3. Run `pilot` in any project directory

## Keeping your computer reachable

For the Claude App or browser to stay connected, and for SSH to work when you're away from the keyboard, your computer needs to stay awake and — in the SSH case — accept connections while sleeping.

| Scenario | What you need |
|----------|---------------|
| App / browser approach | Keep the Mac awake — [Amphetamine](https://apps.apple.com/de/app/amphetamine/id937984704) keeps it awake with the display off |
| SSH approach | **System Settings → General → Sharing → Advanced → Remote Login** lets you SSH into your Mac while it's sleeping |
| Away from home network (either approach) | Install [Tailscale](https://tailscale.com/) on both devices for a VPN tunnel that works anywhere — the Claude App works everywhere out of the box, so Tailscale is only needed for SSH |

## Channels — Telegram, Discord & iMessage

[Channels](https://code.claude.com/docs/en/channels) push messages from external platforms directly into your running Pilot session. Claude reads the message, acts on it with your full local environment, and replies through the same platform.

```bash
pilot --channels plugin:telegram@claude-plugins-official
pilot --channels plugin:discord@claude-plugins-official
pilot --channels plugin:imessage@claude-plugins-official
```

Channels require [Bun](https://bun.sh/) and a one-time bot setup (Telegram/Discord) or macOS (iMessage). Each channel maintains a sender allowlist — only paired users can push messages.

| Channel | Setup | Pairing |
| ------- | ----- | ------- |
| **Telegram** | [Create a bot](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram), pass token during install | Send any message to the bot → approve pairing code in terminal |
| **Discord** | [Create a bot](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/discord), pass token during install | Send any message to the bot → approve pairing code in terminal |
| **iMessage** | [macOS only](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage), no token needed | Texting yourself works automatically |

**Channels vs Remote Control:** Remote Control gives you a window *into* your session from the Claude App or browser. Channels let external platforms push events *into* your session — they're complementary. Use both: channels for incoming messages, Remote Control for monitoring and steering.

**Team/Enterprise:** Channels are off by default. Admins enable them via [claude.ai Admin settings](https://claude.ai/admin-settings/claude-code). See the full [Channels documentation](https://code.claude.com/docs/en/channels) and [Channels reference](https://code.claude.com/docs/en/channels-reference) for building custom channels.

## Use cases

| Pattern | Description |
| ------- | ----------- |
| **Walk away** | Start a `/spec` task at your desk, monitor progress from your phone |
| **Couch review** | Queue up code reviews at your workstation, approve from the couch |
| **Quick check** | Glance at a running session from your phone without going back to your desk |
| **Multi-device** | Heavy coding from terminal, lighter interactions from browser, quick approvals from phone |

## Troubleshooting

If Remote Control doesn't connect or shows authentication errors, run `/logout` followed by `/login` inside Claude Code. This re-authenticates your session and resolves most connection issues.

## Limitations

- Your computer must stay awake (see above)
- One remote connection per Claude Code instance
- Terminal must stay open (close it and the session ends)
