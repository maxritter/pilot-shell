---
name: bot-channel-task
description: "How a Pilot Bot session handles a channel task, so the sender is never left waiting in silence. Follow this skill whenever a message arrives from a channel — Telegram or any other configured source — whatever it asks for: a question, a status check, a job to run, or work to carry out. Not for sending an outbound message on your own initiative, and not for questions about how channels are set up — this covers work arriving over one."
model: sonnet
effort: medium
---

# Bot Channel Task Skill

Standard processing flow for tasks received via messaging channels (e.g., Telegram). Only active when a channel plugin is installed and connected.

## Overview

```
[Channel message received]
        |
        v
+----------------------+
| 1. Immediate ack     |  <- Required, highest priority
|  "Got it, I'll do X" |
+----------------------+
        |
        v
+------------------------------------------+
| Task classification                       |
|                                          |
|  Bounded work (including multi-step) --> Sync execution |
|  Long-running / unattended --> One background agent     |
+------------------------------------------+
        |
        +-- [Sync]  Execute -> completion notification
        |
        +-- [BG]   Launch Agent (run_in_background=true)
                     |
                     +-- Progress report if applicable
                     +-- Completion notification
```

## Step 1: Immediate acknowledgment (required)

After receiving a channel message, **reply to the channel first**.

**Channel detection:**
```
<channel source="plugin:telegram:telegram"> -> mcp__plugin_telegram_telegram__reply
```

**Reply format:** "Got it, I'll [action]." (one sentence, concise)
**reply_to:** `message_id` from the received message

## Step 2: Task execution

**Bounded tasks, including bounded multi-step work**
- Execute synchronously in the current bot session. Do not classify by raw tool count: a simple task that needs several reads, edits, or checks still stays here.
- Report results to channel after completion

**Genuinely long-running or unattended tasks**
- Use one background agent only when the work will take substantial time, wait on an external system, or otherwise prevent the bot from receiving new messages.
- Launch that one subagent via `Agent` with `run_in_background=true`; do not fan out multiple perspectives unless the sender explicitly asks for parallel research.
- Main session returns to message listening immediately

### Handoff info for background subagent

```
Task: [specific task content]
Channel: [channel source from received message]
chat_id: [chat_id from received message]
reply_to: [original message_id]

Instructions:
- Report via the channel's reply tool when work is complete
- Send intermediate progress updates for long tasks
- Report errors immediately
```

## Step 3: Completion notification

Send results to channel after work is done.
- Briefly describe what was done and the outcome
- Include error details and remediation if applicable

## Job Management via Conversation

Users can manage scheduled jobs through natural conversation:
- "Add a job that checks the server every hour" -> bot calls `/bot-jobs add` internally
- "Show my jobs" -> bot calls `/bot-jobs list`
- "Pause the daily-report job" -> bot calls `/bot-jobs pause daily-report`

The bot interprets the user's intent and invokes the appropriate `/bot-jobs` subcommand.

## Usage

This skill triggers automatically when the bot receives a channel message via Claude Code Channels routing. It is not invoked manually. Only active when a Channels plugin (e.g., Telegram) is installed.
