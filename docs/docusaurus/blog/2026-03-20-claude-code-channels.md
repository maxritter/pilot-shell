---
title: "Claude Code Channels: Telegram, Discord & iMessage (2026)"
description: "Message Claude Code from Telegram, Discord, or iMessage. Setup guides for all three platforms with practical use cases."
slug: claude-code-channels
date: 2026-03-20
authors:
  - max-ritter
tags:
  - guide
  - development
---

Message Claude Code from Telegram, Discord, or iMessage. Setup guides for all three platforms with practical use cases.

<!-- truncate -->

**Problem**: You're on the train, your laptop is at home running a 40-minute build, and you realize the test suite needs a config flag you forgot to set. Your options? Wait until you get home, or SSH into your machine from your phone and fumble through a terminal on a 6-inch screen.

Or maybe you're not a developer at all. You run a business and you've set up Claude Code as a general-purpose assistant: managing your calendar, drafting marketing emails, triaging tasks, updating spreadsheets, pulling reports. Right now, every interaction requires sitting at the terminal. You can't message your assistant from your phone between meetings the way you'd text an actual EA.

**Quick Win**: Connect your Claude Code session to Telegram (or iMessage on macOS), then message it from your phone like you'd text a colleague:

```
claude --channels plugin:telegram@claude-plugins-official
```

Send "add the --coverage flag to the test script in package.json" from Telegram. Claude reads the message, makes the change, and replies in your chat. Your session keeps running locally with full access to your filesystem, MCP servers, and project configuration.

## What Are Claude Code Channels?

**Claude Code Channels are a plugin-based feature that lets you send messages from Telegram, Discord, or iMessage directly into a running Claude Code session on your local machine.** Your session processes requests with full filesystem, MCP, and git access, then replies through the same messaging app. Announced March 20, 2026 as a research preview, Channels launched with Telegram and Discord, then added iMessage support a week later. The plugin architecture means more platforms can follow.

The concept is straightforward: an MCP server connects your Claude Code session to a messaging platform. When you send a message to your bot on Telegram or Discord, the MCP server forwards it to Claude. Claude processes the request using your local environment (files, tools, git, everything), then replies back through the same channel.

This is not a cloud-hosted coding environment. Your session stays on your machine. The messaging app is just a window into it, similar to how [Remote Control](/blog/remote-control-guide) uses claude.ai and the mobile app as a window into your local session. Different interface, same principle.

The [original announcement on X](https://x.com/trq212/status/1902534040898191536) picked up significant traction, with developers noting that this pushes dev workflows toward async and mobile-first. The most common community request at launch was iMessage support, and Anthropic [delivered it within a week](https://x.com/trq212/status/2036959638646866021).

## Channels vs Remote Control vs Web Sessions

If you've been following Claude Code's evolution, you now have three ways to interact with sessions remotely. They solve different problems.

| Aspect | Channels | [Remote Control](/blog/remote-control-guide) | Web Sessions |
| --- | --- | --- | --- |
| **Interface** | Telegram, Discord, iMessage (messaging apps) | claude.ai/code, iOS app, Android app | claude.ai/code browser |
| **Session location** | Your machine (local) | Your machine (local) | Anthropic cloud |
| **Setup** | Install plugin, create bot, pair | `claude remote-control` (one command) | Open claude.ai/code |
| **Best for** | Async messages, mobile-first, team channels | Continuing terminal sessions from phone | Quick tasks without local setup |
| **Local tools** | Full access (filesystem, MCP, git) | Full access (filesystem, MCP, git) | Cloud sandbox only |
| **Hackability** | High (plugin architecture, build your own) | Low (fixed interface) | None |
| **Notification style** | Native app notifications (Telegram/Discord/iMessage) | Must open claude.ai or app | Must open claude.ai |
| **Team collaboration** | Discord guild channels for shared access | Single-user only | Single-user only |

**When to use Channels**: You want native mobile notifications, async workflows where you fire off requests and check back later, or team-based interaction through Discord guild channels. You also want Channels when you prefer a hackable, extensible system you can customize.

**When to use Remote Control**: You want the full claude.ai interface with rich formatting, file previews, and a familiar chat UI. It requires less setup (one command vs bot creation) and works immediately with the Claude mobile app.

As Thariq from the Claude Code team [noted in the announcement thread](https://x.com/trq212/status/1902534040898191536): "We want to give you a lot of different options in how you talk to Claude remotely. Channels is more focused on devs who want something hackable."

## How Channels Work Under the Hood

The architecture follows the MCP pattern that Claude Code already uses for tool extensions. Here's the flow:

1. **You install a channel plugin** (Telegram, Discord, or iMessage) that runs as an MCP server
2. **You launch Claude Code** with the `--channels` flag, which activates the plugin
3. **The MCP server connects** to the messaging platform (polling for Telegram, WebSocket for Discord)
4. **When a message arrives**, the server wraps it as a `<channel>` event and pushes it into your Claude Code session
5. **Claude processes the request** using your full local environment
6. **Claude replies** through tools exposed by the MCP server (`reply`, `react`, `edit_message`)

The security model has two layers. First, every channel plugin maintains a **sender allowlist**. Only user IDs you've explicitly paired and approved can push messages. Everyone else is silently dropped. Second, the `--channels` flag controls which servers are active per session. Being configured in `.mcp.json` is not enough to push messages; a server must also be named in `--channels`.

On Team and Enterprise plans, organization admins control channel availability through a `channelsEnabled` managed setting. It's disabled by default and must be explicitly enabled.

One important detail: if Claude hits a permission prompt while you're away from the terminal, the session pauses until you approve locally. For fully unattended operation, the `--dangerously-skip-permissions` flag bypasses prompts, but only use this in environments you trust.

Keep in mind that Claude's replies flow through the messaging platform's servers. If you're working with proprietary code or sensitive credentials, be deliberate about what you ask Claude to output through a channel. For sensitive work, the `fakechat` localhost option (covered below) keeps everything on your machine.

## Setting Up the Telegram Channel

The Telegram setup takes about 5 minutes. You need [Bun](https://bun.sh) installed (the MCP server runs on it) and a Claude Code session authenticated with a claude.ai account (not an API key).

### Step 1: Create a Telegram Bot

Open [@BotFather](https://t.me/BotFather) on Telegram and send `/newbot`. BotFather asks for two things:

- **Display name**: Anything you want, spaces are fine (e.g., "My Dev Assistant")
- **Username**: A unique handle ending in `bot` (e.g., `my_dev_assistant_bot`)

BotFather replies with a token like `123456789:AAHfiqksKZ8...`. Copy the entire thing including the leading number and colon.

### Step 2: Install the Plugin

Start a Claude Code session and run:

```
/plugin install telegram@claude-plugins-official
```

### Step 3: Configure the Token

```
/telegram:configure 123456789:AAHfiqksKZ8...
```

This writes `TELEGRAM_BOT_TOKEN=...` to `.claude/channels/telegram/.env` in your project. You can also set the variable in your shell environment before launching Claude Code (shell takes precedence).

### Step 4: Relaunch with Channels Enabled

Exit your session and restart with the channel flag:

```
claude --channels plugin:telegram@claude-plugins-official
```

### Step 5: Pair Your Account

DM your bot on Telegram. It replies with a 6-character pairing code. Back in Claude Code:

```
/telegram:access pair <code>
```

### Step 6: Lock Down Access

Switch to allowlist mode so only your account can interact with the bot:

```
/telegram:access policy allowlist
```

That's it. Your next message to the bot reaches Claude directly.

### Telegram-Specific Features

- **Photos**: Inbound photos are downloaded automatically to `~/.claude/channels/telegram/inbox/`. The assistant can read them directly. Send as "File" (long-press in Telegram) if you need the uncompressed original
- **File attachments**: The `reply` tool supports sending files back. Images render inline; other types send as documents. Max 50MB per file
- **Typing indicator**: Telegram shows "botname is typing..." while Claude works on a response. This is surprisingly useful for knowing whether Claude is still processing or has stalled on a permission prompt
- **No message history**: The Telegram Bot API doesn't expose message history or search. The bot only sees messages as they arrive in real-time. If the session was down when you sent a message, it's gone

## Setting Up the Discord Channel

Discord requires a few more steps because you need to create an application in the Developer Portal and invite the bot to a server. Budget about 10 minutes.

### Step 1: Create a Discord Application

Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**. Name it whatever you want.

### Step 2: Create the Bot and Get a Token

Navigate to **Bot** in the sidebar. Give your bot a username. Scroll up to **Token** and press **Reset Token**. Copy the token (it's only shown once).

### Step 3: Enable Message Content Intent

Still in the Bot settings, scroll to **Privileged Gateway Intents** and enable **Message Content Intent**. Without this, the bot receives messages with empty content.

### Step 4: Invite the Bot to Your Server

Navigate to **OAuth2** then **URL Generator**. Select the `bot` scope and enable these permissions:

- View Channels
- Send Messages
- Send Messages in Threads
- Read Message History
- Attach Files
- Add Reactions

Copy the generated URL, open it, and add the bot to your server.

### Step 5: Install and Configure

In Claude Code:

```
/plugin install discord@claude-plugins-official
/discord:configure <your-bot-token>
```

### Step 6: Relaunch and Pair

```
claude --channels plugin:discord@claude-plugins-official
```

DM your bot on Discord. It replies with a pairing code. In Claude Code:

```
/discord:access pair <code>
/discord:access policy allowlist
```

### Discord-Specific Features

- **Message history**: Unlike Telegram, Discord's `fetch_messages` tool can pull recent history from a channel (up to 100 messages per call, oldest-first). This is the key differentiator. If your session restarts, Claude can catch up on what it missed
- **Attachment handling**: Attachments aren't auto-downloaded. The assistant sees metadata (name, type, size) and calls `download_attachment` when it needs the actual file
- **Guild channels**: Discord supports server/guild channels, not just DMs. This opens up team collaboration where multiple people interact with Claude through a shared channel
- **Custom emoji reactions**: The `react` tool supports both Unicode emoji and custom server emoji in `<:name:id>` format
- **Threading**: The `reply` tool supports `reply_to` for native Discord threading, which keeps conversations organized when multiple people are interacting in the same channel

## Setting Up the iMessage Channel

iMessage is the newest channel, added after overwhelming community demand following the initial Telegram and Discord launch. The key difference: no bot token, no external service, no pairing code. The plugin reads your Mac's Messages database directly and sends replies through AppleScript.

**Important: iMessage requires macOS.** The plugin reads `~/Library/Messages/chat.db` and controls Messages.app through AppleScript. There is no Windows or Linux equivalent.

### Step 1: Grant Full Disk Access

The plugin needs to read your Messages database. Open **System Settings > Privacy & Security > Full Disk Access** and enable it for your terminal app (Terminal.app, iTerm2, Warp, or whichever you use to run Claude Code).

### Step 2: Install the Plugin

Start a Claude Code session and run:

```
/plugin install imessage@claude-plugins-official
```

### Step 3: Relaunch with Channels Enabled

Exit your session and restart with the channel flag:

```
claude --channels plugin:imessage@claude-plugins-official
```

### Step 4: Test with Self-Chat

The fastest way to verify the setup: text yourself from any Apple device. Self-chat (messaging your own number) bypasses the access control system entirely, so it works with zero configuration.

### Step 5: Approve the Automation Prompt

The first time Claude sends a reply, macOS shows an Automation prompt asking whether your terminal app can control Messages.app. Click **OK**. This is a one-time approval.

### Step 6: Allow Other Senders

By default, only self-chat works. To let other people message your Claude session, add them by phone number or Apple ID:

```
/imessage:access allow +15551234567
/imessage:access allow AppleID
```

### iMessage-Specific Features

- **macOS native**: No external service, no bot token, no developer portal. The plugin uses your existing Messages infrastructure directly
- **Self-chat works instantly**: Texting yourself is the zero-config test path. No pairing code, no allowlist entry needed
- **Identity detection from Messages database**: Instead of the pairing code flow used by Telegram and Discord, the iMessage plugin identifies senders by reading the Messages database. It knows who sent a message based on the handle stored in `chat.db`
- **Add senders by handle**: Phone numbers (`+15551234567`) or Apple IDs both work with the `/imessage:access allow` command
- **AppleScript-based replies**: Outbound messages go through Messages.app via AppleScript, so replies appear as normal iMessages from your account

## Practical Use Cases

### Monitor Long-Running Tasks from Your Phone

Start a complex build, test suite, or multi-agent workflow at your desk. Walk away. When Claude finishes or hits an issue, you see the notification on your phone through Telegram, Discord, or iMessage. Send follow-up instructions without opening a laptop.

### Quick Fixes on the Go

You're reviewing a PR on your phone and spot a typo in a config file. Instead of noting it down for later, message your bot: "Change the Redis port in docker-compose.yml from 6380 to 6379 and commit it." Claude makes the change, commits, and confirms.

### Team Collaboration Through Discord

Set up a Discord guild channel where your team can interact with a shared Claude Code session. Useful for pair-debugging, where one person describes the issue and Claude investigates with full access to the codebase. Everyone in the channel sees the conversation.

### Async Development Workflows

The combination of Channels and [scheduled tasks](/blog/scheduled-tasks) creates a powerful async pattern. Schedule Claude to run your test suite every hour, report results through Telegram, and wait for your instructions if something fails. You check in when it's convenient.

### Your AI Executive Assistant, on Telegram

Not every Claude Code setup is about writing code. If you've configured Claude as a productivity assistant with MCP connections to your calendar, email, CRM, or project management tools, Channels turns it into something closer to a real EA. Message "what's my priority list for today?" from Telegram while you're grabbing coffee. Ask it to draft a follow-up email to a client between meetings. Tell it to reschedule your afternoon and reprioritize based on that urgent Slack thread. The interaction model stops being "sit at terminal, type command" and becomes "text your assistant whenever you need something."

### CI/CD Notifications and Reactions

Forward CI results into your session through a channel. When a build fails, Claude can inspect the logs, identify the issue, and either fix it automatically or message you with a diagnosis. This goes beyond passive notifications because Claude has your full project context.

## Building Your Own Channel

The plugin architecture isn't limited to the three official channels. Anthropic provides a [Channels reference](https://code.claude.com/docs/en/channels-reference) for building custom channels. Any MCP server that implements the channel protocol can push events into Claude Code.

During the research preview, `--channels` only accepts plugins from an Anthropic-maintained allowlist. To test a channel you're building, use the `--dangerously-load-development-channels` flag. This lets you iterate on custom integrations without waiting for official approval.

The `fakechat` plugin ships as a development demo. It runs a chat UI on localhost with no external dependencies, so you can test the full channel flow before wiring up a real platform:

```
/plugin install fakechat@claude-plugins-official
claude --channels plugin:fakechat@claude-plugins-official
```

Open `http://localhost:8787` and start chatting. Messages flow into your Claude Code session, and replies appear in the browser.

## Requirements and Limitations

### Requirements

- **Claude Code v2.1.80 or later**
- **Bun runtime** installed ([bun.sh](https://bun.sh))
- **claude.ai authentication** (Pro or Max plan). Console and API key authentication is not supported
- **Team/Enterprise plans**: admin must explicitly enable channels in managed settings
- **iMessage channel**: macOS only, with Full Disk Access granted to your terminal app

### Current Limitations

This is a research preview. Expect rough edges:

- **Session must stay running**: Close the terminal or stop the `claude` process and the channel goes offline. Messages sent while the session is down are lost (Telegram) or queued until the bot comes back online (Discord, via `fetch_messages`)
- **Permission prompts block remotely**: If Claude needs permission approval, it pauses until you approve at the terminal. The `--dangerously-skip-permissions` flag works but carries obvious risks
- **Allowlisted plugins only**: During the preview, only plugins from `claude-plugins-official` are accepted by `--channels`. Custom channels require the development flag
- **No persistent background mode**: You need to keep a terminal session open. Combining with `tmux`, `screen`, or a background process is the current workaround
- **Platform-specific gaps**: Telegram has no message history API. Discord requires more setup steps. iMessage only works on macOS and requires Full Disk Access. Each platform has its own constraints

Anthropic has described this as a feature "we'll be expanding more on." The plugin architecture suggests future platforms (Slack and WhatsApp have both been requested) and the channel reference documentation signals that community-built channels are part of the plan.

## Frequently Asked Questions

### What is Claude Code Channels?

Channels is a plugin-based feature that connects Claude Code sessions to messaging apps like Telegram, Discord, and iMessage. You send messages from the app, Claude processes them using your local dev environment, and replies in the same chat. Your code and tools never leave your machine.

### Is Claude Code Channels free?

You need a claude.ai Pro or Max subscription. API key authentication is not supported. The Telegram, Discord, and iMessage plugins themselves are free and open source.

### What's the difference between Channels and Remote Control?

[Remote Control](/blog/remote-control-guide) gives you the full claude.ai web interface as a window into your local session. Channels uses messaging apps (Telegram, Discord, iMessage) as the interface instead. Both keep your session running locally. Remote Control is one command to set up; Channels requires plugin setup but gives you native notifications and more hackability.

### Can I use Claude Code from my phone?

Yes, through three different methods. [Remote Control](/blog/remote-control-guide) lets you use the Claude mobile app. Channels lets you use Telegram, Discord, or iMessage. Web sessions at claude.ai/code run entirely in the cloud. All three work from any device with a browser or the relevant app.

### Which messaging apps work with Claude Code Channels?

Telegram, Discord, and iMessage are the three officially supported platforms as of March 2026. The plugin architecture is designed for expansion, and the community has already requested Slack and WhatsApp. You can also build your own channel using the [Channels reference](https://code.claude.com/docs/en/channels-reference).

## Getting Started

If you're already comfortable with MCP servers and Claude Code plugins, the setup is familiar territory. Pick the platform you use most:

1. **Telegram** if you want the fastest setup (5 minutes, no server invite needed)
2. **Discord** if you want message history, guild channels, or team collaboration
3. **iMessage** if you're on macOS and want zero-config native messaging with no external service
4. **Fakechat** if you want to test the flow locally before committing to a platform

Start with DM-only access and the allowlist policy. Once you're comfortable, explore guild channels on Discord or group chats on Telegram for broader use cases.

Channels represent a shift in how developers interact with their coding environment. Instead of sitting at a terminal, you message it. Instead of waiting for a build to finish, you get notified. Instead of context-switching between your phone and your workstation, you work from wherever you are.

The "code from your phone" promise has been floating around for years. With Channels, [Remote Control](/blog/remote-control-guide), and [scheduled tasks](/blog/scheduled-tasks), Claude Code is making it real, one interface at a time.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
