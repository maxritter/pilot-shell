---
name: bot-jobs
description: Manage Pilot Bot scheduled jobs — add, remove, pause, resume, edit, list. Live-syncs JOBS.yaml with CronCreate/CronDelete.
model: sonnet
effort: medium
---

# Bot Jobs Skill

Manage scheduled jobs defined in `JOBS.yaml` at `$PILOT_BOT_DIR`. All changes are written to YAML **and** live-synced with CronCreate/CronDelete immediately.

**Before using cron tools:** Load them first with `ToolSearch(query="select:CronList,CronCreate,CronDelete")`. CronCreate uses `cron` (not `schedule`) as the parameter name for the cron expression.

Users interact with this skill via conversation (e.g., "add a job that checks X every morning") — either through Telegram (if available) or directly in the Claude Code session. The bot calls this skill internally.

## Commands

| Command | Action |
|---------|--------|
| `/bot-jobs list` | Show all jobs with status |
| `/bot-jobs add` | Add a new job interactively |
| `/bot-jobs remove <id>` | Delete a job permanently |
| `/bot-jobs pause <id>` | Set `active: false` and unregister from cron |
| `/bot-jobs resume <id>` | Set `active: true` and register with cron |
| `/bot-jobs edit <id>` | Modify a job interactively |

Args are passed via the Skill tool's `args` parameter (e.g., `skill: "bot-jobs", args: "pause daily-report"`).

## Steps

### Parse command

Extract the subcommand and optional job ID from args:
- No args or `list` → **list**
- `add` → **add**
- `remove <id>` → **remove**
- `pause <id>` → **pause**
- `resume <id>` → **resume**
- `edit <id>` → **edit**

### Read JOBS.yaml

Read `JOBS.yaml` from `$PILOT_BOT_DIR`. Parse the YAML structure. Each job has:

```yaml
jobs:
  <id>:
    schedule: "<cron expression>"
    description: <short description>
    active: true|false
    prompt: |
      <prompt text>
```

### Execute subcommand

#### list

Display all jobs in a table format:

```
| ID | Schedule | Active | Description |
|----|----------|--------|-------------|
| daily-report | 0 9 * * * | yes | Morning status report |
```

Also run CronList to show which jobs are currently registered in the session.

#### add

Ask the user for each field:
1. **ID** — short kebab-case identifier (e.g., `daily-report`)
2. **Schedule** — cron expression (e.g., `0 9 * * *`)
3. **Description** — one-line summary
4. **Prompt** — the prompt text (can be multi-line)

Then:
1. Write the new job entry to `JOBS.yaml` using the Edit tool
2. Run `CronCreate` with `cron='<cron expression>'` and `prompt='<prompt text>'`
3. Confirm to the user

#### remove

1. Verify the job ID exists in `JOBS.yaml`
2. Run `CronList` to find the matching cron job, then `CronDelete` it
3. Remove the entry from `JOBS.yaml` using the Edit tool
4. Confirm to the user

#### pause

1. Verify the job ID exists and is currently `active: true`
2. Change `active: true` to `active: false` in `JOBS.yaml`
3. Run `CronList` to find the matching cron job, then `CronDelete` it
4. Confirm to the user

#### resume

1. Verify the job ID exists and is currently `active: false`
2. Change `active: false` to `active: true` in `JOBS.yaml`
3. Run `CronCreate` with `cron='<schedule>'` and `prompt='<prompt>'`
4. Confirm to the user

#### edit

1. Verify the job ID exists
2. Show the current values and ask what to change
3. Update `JOBS.yaml` with the new values
4. If the job is active: `CronDelete` the old cron, then `CronCreate` with updated values
5. Confirm to the user

### Matching JOBS.yaml entries to CronList

CronCreate returns a session-internal ID that differs from the JOBS.yaml job ID. To match them:
- Use CronList to list all cron jobs
- Match by the prompt text (the prompt field is unique per job)
- If no match is found, the job is not currently registered (e.g., after a session restart)

## Notes

- JOBS.yaml is the source of truth for persistent job definitions
- CronCreate/CronDelete are session-scoped (lost on session end)
- Boot skill registers all `active: true` jobs on every session start
- Heartbeat is NOT managed here — it's registered separately by boot skill

## Usage

```
/bot-jobs
/bot-jobs list
/bot-jobs add
/bot-jobs remove daily-report
/bot-jobs pause daily-report
/bot-jobs resume daily-report
/bot-jobs edit daily-report
```
