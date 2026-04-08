---
name: bot-defaults
description: Pilot Bot default behaviors — always applied during bot sessions
model: sonnet
effort: medium
---

# Bot Default Behaviors

These rules are always applied during Pilot Bot sessions. They override general defaults.

## HTTP Requests

Use sandbox/MCP tools for HTTP requests, not raw curl. This ensures proper error handling and avoids context pollution from large responses.

## Cron Deduplication

**Always wrap bash commands in cron prompts with a lock file check.**

Cron triggers can fire 2-3x in the same interval due to scheduler jitter. Without deduplication, this causes duplicate operations.

**Pattern:**

```bash
LOCK=$PILOT_BOT_DIR/.<job-id>-lock; NOW=$(date +%s); if [ -f "$LOCK" ] && [ $((NOW - $(cat "$LOCK"))) -lt <threshold> ]; then echo "SKIP"; else echo $NOW > "$LOCK"; <your command>; fi
```

**Threshold = ~75% of the cron interval in seconds:**

| Interval | Threshold |
|----------|-----------|
| `*/5 * * * *` (5 min) | 225s |
| `*/10 * * * *` (10 min) | 450s |
| `*/30 * * * *` (30 min) | 1350s |
| `0 * * * *` (hourly) | 2700s |

**In the cron prompt, add:** "If output is `SKIP`, stop here and do nothing."

## Channel Reporting (when Telegram or other channels are available)

- Acknowledge every channel message before starting work (via `/bot-channel-task`)
- Run long tasks as background agents
- Report progress and completion via channel reply tool
- Keep messages brief and actionable — no spam, no chatty "alive" messages

## Job Management

Use `/bot-jobs` to manage scheduled tasks programmatically. Users should not need to edit JOBS.yaml directly — the skill handles reading, writing, and cron sync.

## Error Handling

- If a channel is available: report errors immediately with context
- If no channel: log errors to console
- Do not retry failed tasks automatically unless explicitly asked
- Include enough detail to understand what went wrong
