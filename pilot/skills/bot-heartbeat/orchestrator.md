---
name: bot-heartbeat
description: Pilot Bot heartbeat — spawns background subagent for periodic health check, notifies only when issues are detected
model: sonnet
effort: medium
---

# Bot Heartbeat Skill

Spawns a background subagent to run periodic checks.
The main session is released immediately after the subagent is launched.

## Steps

1. Launch a subagent with `run_in_background=true`
2. Main session exits immediately (does not wait for subagent completion)

## Background Subagent Prompt

Prompt to pass to the subagent:

```
You are a heartbeat agent for Pilot Bot.

Steps:
1. Run: bash $PILOT_BOT_DIR/../../.claude/skills/bot-heartbeat/scripts/check.sh
   If the script outputs "SKIP", exit immediately (dedup — heartbeat already ran recently).
2. Evaluate whether any issues exist (dead processes, failed jobs, etc.)
3. Check if Telegram MCP tools (reply, react) are available. Track telegram_available.
4. Notification rule:
   - NO issues → do NOT send any message. Stay silent.
   - Issues found AND telegram_available → send issue details via Telegram reply (brief, no "alive" prefix)
   - Issues found AND NOT telegram_available → output alert to console only.
5. Exit.

Keep it brief. Do not ask questions. Do not wait for responses.
```

## Lock File Dedup

The check.sh script implements lock file deduplication:
- Lock file: `$PILOT_BOT_DIR/.heartbeat-lock`
- Threshold: 1350s (75% of the 30-minute interval)
- If the last check ran within the threshold, check.sh outputs "SKIP" and the subagent exits

## Usage

Registered automatically at boot by `/bot-boot`.
Default schedule: `*/30 * * * *` (every 30 minutes).

## Note

The subagent inherits MCP tools from the main session.
It does not inherit the main session's conversation context.
