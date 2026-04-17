---
name: bot-boot
description: Pilot Bot boot sequence — health check, job registration, heartbeat setup
model: sonnet
effort: medium
---

# Bot Boot Skill

Boot orchestrator for Pilot Bot. Runs on every bot session start via `pilot bot`.

The bot is an automation agent — scheduled tasks, background jobs, 24/7 operation. Telegram integration is optional (auto-detected).

Environment variables available:
- `PILOT_BOT_MODE=1` — confirms bot context
- `PILOT_BOT_DIR` — path to `~/.pilot/bot/` (contains JOBS.yaml)

## Execution

**Phase 1** — Single message with parallel tool calls (foreground + background agents):

| # | Type | Action |
|---|------|--------|
| 1 | **Foreground** | Read `$PILOT_BOT_DIR/JOBS.yaml` to understand current job configuration. |
| 2 | **Background Agent** | **MCP health check** — silent check, no greeting (see below) |

**Phase 2** — After Phase 1 completes, register crons in the **main session** (Cron tools are not available to subagents):

| # | Action |
|---|--------|
| 3 | **Heartbeat registration** — First load tools: `ToolSearch(query="select:CronList,CronCreate")`. Then use CronList to check if a heartbeat cron already exists (look for 'bot-heartbeat' in prompt text). If it already exists, do nothing. If not found, use CronCreate with `cron='*/30 * * * *'` and `prompt='Run /bot-heartbeat skill (invoke Skill tool with skill=bot-heartbeat)'`. |
| 4 | **Jobs registration** — Read JOBS.yaml from `$PILOT_BOT_DIR`. If missing or empty (`jobs: {}`), skip. Otherwise use CronList to get existing crons, then for each job with `active: true`, register via CronCreate with `cron='<schedule>'` and `prompt='<prompt>'` if not already registered (match by job ID in prompt content). |

### #2 MCP health check

`description='MCP health check'`, `run_in_background=true`. Prompt:

```
Check MCP health silently. Do NOT send any message to any channel.
1) Check if Telegram MCP tools (reply, react) are available in the tool list. Do NOT call them — just confirm they exist. Track telegram_available.
2) If tools are not available on first check, wait 5s and recheck (up to 3 attempts).
3) Log result to console: 'Telegram: available' or 'Telegram: not available (bot will run without messaging)'.
4) Exit. Do NOT send any message via reply or any other channel tool.
```

**Phase 3** — Boot completion (main session, after Phase 2):

- If Telegram MCP tools are available: send a boot completion message via Telegram `reply` tool.
- If Telegram is not available: log "Pilot Bot online (no Telegram)" to console. This is normal — the bot works as a standalone automation agent.

## Done

Main session is ready once Phase 3 completes. The bot now:
- Runs scheduled jobs via CronCreate registrations
- Performs periodic heartbeat checks via `/bot-heartbeat`
- If Telegram is available: receives and processes messages via `/bot-channel-task`

## Usage

```
/bot-boot
```
