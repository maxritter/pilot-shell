---
name: bot-heartbeat
description: Pilot Bot heartbeat — keeps the bot's health under watch between jobs and speaks up only when something is wrong. Runs on its own half-hourly schedule, not on user request.
model: sonnet
effort: medium
---

# Bot Heartbeat Skill

Runs periodic checks directly in the scheduled heartbeat turn. Spawning another
model agent for this bounded check doubles token use without adding isolation.

## Steps

1. Run: `bash "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/bot-heartbeat/scripts/check.sh"`
2. If the script outputs `SKIP`, stop immediately (dedup — heartbeat already ran recently).
3. Evaluate whether any issues exist (dead processes, failed jobs, etc.).
4. Check whether Telegram MCP tools (`reply`, `react`) are available.
5. If there are no issues, stay silent. If issues exist, send a brief Telegram reply when available; otherwise output the alert to the console.

Keep the turn brief. Do not ask questions or wait for responses.

## Lock File Dedup

The check.sh script implements lock file deduplication:
- Lock file: `$PILOT_BOT_DIR/.heartbeat-lock`
- Threshold: 1350s (75% of the 30-minute interval)
- If the last check ran within the threshold, check.sh outputs "SKIP" and the subagent exits

## Usage

Registered automatically at boot by `/bot-boot`.
Default schedule: `*/30 * * * *` (every 30 minutes).
