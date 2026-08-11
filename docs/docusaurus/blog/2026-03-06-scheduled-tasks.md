---
title: "Claude Code Scheduled Tasks: Complete Setup Guide (2026)"
description: "Set up scheduled tasks in Claude Code Desktop and CLI. Automate code reviews, error monitoring, and daily briefings step by step."
slug: scheduled-tasks
date: 2026-03-06
authors:
  - max-ritter
tags:
  - guide
  - development
---

Set up scheduled tasks in Claude Code Desktop and CLI. Automate code reviews, error monitoring, and daily briefings step by step.

<!-- truncate -->

Claude Code scheduled tasks let you save a prompt and have it run automatically on a recurring cadence. No more opening a new session every morning to type the same "check error logs" prompt. No more forgetting to run your daily code review. You define the work once, Claude handles the timing. Pair scheduled tasks with [Channels](/blog/claude-code-channels) to get results delivered straight to Telegram or Discord.

There are two flavors. **Desktop scheduled tasks** are persistent: they survive restarts, run on a visual schedule, and fire as long as the app is open. **CLI session-scoped tasks** use `/loop` and cron tools for quick, in-session polling that dies when you exit. This guide covers both.

## Desktop Scheduled Tasks

Desktop scheduled tasks are the primary way to automate recurring work in Claude Code. They run locally on your machine, each firing a fresh session at the time and frequency you choose. Every run has full access to your files, MCP servers, skills, connectors, and plugins.

### Creating a Task

Click **Schedule** in the Desktop sidebar, then **+ New task**. Fill in these fields:

| Field | Description |
| --- | --- |
| **Name** | Identifier for the task (converted to lowercase kebab-case, used as folder name on disk, must be unique) |
| **Description** | Short summary shown in the task list |
| **Prompt** | The instructions sent to Claude each run. Same as any message you'd type in the prompt box |
| **Frequency** | How often the task runs (see cadence options below) |

The prompt input also includes controls for model selection, permission mode, working folder, and worktree isolation. Enable the worktree toggle to give each run its own isolated Git worktree, preventing scheduled runs from interfering with your manual work.

You can also create a task conversationally. In any Desktop session, just say: "set up a daily code review that runs every morning at 9am." Claude handles the rest.

### Frequency Options

| Frequency | Behavior |
| --- | --- |
| **Manual** | No schedule. Only runs when you click **Run now** |
| **Hourly** | Every hour, with a fixed offset of up to 10 minutes to stagger traffic |
| **Daily** | Time picker, defaults to 9:00 AM local time |
| **Weekdays** | Same as Daily but skips Saturday and Sunday |
| **Weekly** | Time picker plus day picker |

For intervals the picker doesn't offer (every 15 minutes, first of each month), ask Claude in any Desktop session using plain language. For example: "schedule a task to run all the tests every 6 hours."

### How Desktop Tasks Run

Desktop checks the schedule every minute while the app is open. When a task is due, it starts a fresh session independent of whatever you're working on. Each task gets a deterministic delay of up to 10 minutes after the scheduled time to stagger API traffic. The same task always fires at the same offset.

When a task fires, you get a desktop notification and a new session appears under the **Scheduled** section in the sidebar. Open it to see what Claude did, review diffs, or respond to permission prompts. The session works like any other: Claude can edit files, run commands, create commits, and open pull requests.

### Missed Runs and Catch-Up

When the app starts or your computer wakes, Desktop checks whether each task missed any runs in the last seven days. If it did, it starts exactly one catch-up run for the most recently missed time and discards anything older. A daily task that missed six days runs once on wake. Desktop shows a notification when a catch-up run starts.

Keep this in mind when writing prompts. A task scheduled for 9am might run at 11pm if your computer was asleep all day. If timing matters, add guardrails to the prompt: "Only review today's commits. If it's after 5pm, skip the review and post a summary of what was missed."

### Permissions for Scheduled Tasks

Each task has its own permission mode, set when creating or editing it. Allow rules from `~/.claude/settings.json` also apply. If a task runs in Ask mode and hits a tool it doesn't have permission for, the run stalls until you approve it. The session stays open in the sidebar so you can answer later.

To avoid stalls, click **Run now** after creating a task, watch for permission prompts, and select "always allow" for each one. Future runs auto-approve the same tools without prompting. You can review and revoke these approvals from the task's detail page under the **Always allowed** panel.

### Managing Tasks

Click a task in the **Schedule** list to open its detail page:

- **Run now**: start the task immediately without waiting for the next scheduled time
- **Toggle repeats**: pause or resume scheduled runs without deleting the task
- **Edit**: change the prompt, frequency, folder, model, or permission mode
- **Review history**: see every past run, including skipped ones
- **Review allowed permissions**: see and revoke saved tool approvals
- **Delete**: remove the task and archive all sessions it created

You can also manage tasks by asking Claude in any session: "pause my dependency-audit task", "delete the standup-prep task", or "show me my scheduled tasks."

Task prompts live on disk at `~/.claude/scheduled-tasks/<task-name>/SKILL.md` with YAML frontmatter for name and description. Edit the file directly and changes take effect on the next run.

## CLI Scheduled Tasks: /loop and Cron Tools

The CLI has its own lighter-weight scheduling system. It's session-scoped: tasks live in the current Claude Code process and are gone when you exit. Use it for quick polling and in-session monitoring, not durable automation.

### The /loop Command

The fastest way to schedule a recurring prompt in the CLI:

```
/loop 5m check if the deployment finished and tell me what happened
```

Claude parses the interval, converts it to a cron expression, schedules the job, and confirms the cadence and job ID.

Interval syntax is flexible:

| Form | Example | Parsed interval |
| --- | --- | --- |
| Leading token | `/loop 30m check the build` | Every 30 minutes |
| Trailing `every` clause | `/loop check the build every 2 hours` | Every 2 hours |
| No interval | `/loop check the build` | Defaults to every 10 minutes |

Supported units: `s` (seconds, rounded up to nearest minute), `m` (minutes), `h` (hours), `d` (days).

You can loop over other commands too:

```
/loop 20m /review-pr 1234
```

Each time the job fires, Claude runs `/review-pr 1234` as if you typed it.

### One-Time Reminders

For one-shot tasks, just use natural language:

```
remind me at 3pm to push the release branch
```

```
in 45 minutes, check whether the integration tests passed
```

Claude pins the fire time to a specific cron expression and confirms when it will run.

### Under the Hood: CronCreate, CronList, CronDelete

The `/loop` command and natural language scheduling use these tools:

| Tool | Purpose |
| --- | --- |
| `CronCreate` | Schedule a new task with a 5-field cron expression and prompt |
| `CronList` | List all scheduled tasks with IDs, schedules, and prompts |
| `CronDelete` | Cancel a task by its 8-character ID |

A session can hold up to 50 scheduled tasks. All times are interpreted in your local timezone.

### CLI Scheduling Constraints

- **Session-scoped**: closing the terminal or exiting Claude Code cancels everything
- **No catch-up**: if Claude is busy when a task is due, it fires once when idle, not once per missed interval
- **Three-day expiry**: recurring tasks auto-delete after 3 days to bound how long a forgotten loop can run
- **No persistence**: restarting Claude Code clears all session-scoped tasks
- Disable entirely with `CLAUDE_CODE_DISABLE_CRON=1`

## Desktop vs CLI: Which to Use

| Aspect | Desktop Scheduled Tasks | CLI /loop + Cron Tools |
| --- | --- | --- |
| **Persistence** | Survives restarts, runs as long as app is open | Dies when you exit the session |
| **Setup** | Visual form in sidebar | `/loop 5m prompt` inline |
| **Missed runs** | Catches up from last 7 days (one run) | No catch-up |
| **Expiry** | None (runs until you delete it) | Auto-deletes after 3 days |
| **Max tasks** | No stated limit | 50 per session |
| **Permissions** | Per-task permission mode with "always allow" approvals | Inherits session permissions |
| **Git isolation** | Optional worktree per run | No isolation |
| **Best for** | Daily reviews, weekly reports, morning briefings | Polling deploys, babysitting PRs, quick checks |

Use Desktop scheduled tasks for anything you want to run tomorrow, next week, or indefinitely. Use CLI `/loop` for "watch this deploy for the next hour."

## Use Cases That Actually Matter

### Error Log Monitoring

Thariq from the Claude Code team shared his favorite: "Ask it to check error logs every few hours and create PRs for any actionable errors."

Set this to hourly in Desktop. Connect your logging service via MCP. The agent reads recent errors, filters noise, and opens pull requests for issues worth fixing. You review PRs instead of scanning logs.

### Morning Briefings

Schedule a weekday task at 8:30am. Connect Slack, email, and calendar via connectors. The agent summarizes overnight messages, flags urgent items, and outlines your day. You open Claude Desktop to a ready-made briefing instead of spending 30 minutes triaging inboxes.

### Weekly Reports

Set a weekly task that pulls data from Google Drive, spreadsheets, or project management tools. The agent compiles metrics, identifies trends, and generates a formatted report. Especially powerful for teams running async workflows where status updates are scattered across multiple tools.

### PR Babysitting (CLI)

Kicked off a PR and want to know when CI finishes? In the CLI:

```
/loop 5m check the CI status on PR #247 and tell me if it passed or failed
```

Claude polls every 5 minutes and reports back. When CI finishes, cancel the loop and move on.

### Dependency Audits

Schedule a weekly task that runs `npm audit` or `pip audit`, analyzes the results, and creates a PR with fixes for any actionable vulnerabilities. Set it to Monday morning so you start the week with a clean bill of health.

### Recurring Research

Track competitors, industry news, or technology trends on a daily or weekly cadence. The agent browses configured sources, extracts relevant updates, and compiles summaries. Connect it to web search for broad coverage.

## The OpenClaw Effect

If you've been following the [OpenClaw phenomenon](/blog/openclaw-vs-claude-code), this feature should look familiar. OpenClaw's entire pitch was an autonomous AI agent that connects to your apps and runs tasks on your behalf, on a schedule, without you babysitting it. That pitch resonated with 199K GitHub stars and a wave of mainstream attention that proved the demand was real.

Anthropic clearly took notes. [Remote Control](/blog/remote-control-guide) landed in February as a direct answer to OpenClaw's "control your computer from your phone" feature. Now scheduled tasks close another gap: the ability to set an agent loose on a recurring cadence without manual intervention.

The pattern is consistent. OpenClaw shows what users want through sheer viral adoption. Anthropic ships the native, integrated, security-first version weeks later. Remote Control replaced OpenClaw's WebSocket-based remote access with an encrypted, outbound-only bridge. Scheduled tasks replace the "always-on personal assistant" concept with a structured, permission-controlled agent scheduler that inherits your full MCP and plugin setup.

The difference in execution matters. OpenClaw grants broad system access by default and has faced security incidents (CVE-2026-25253 affected 50K+ instances). Claude Code's scheduled tasks run with explicit permission boundaries and per-task approval controls. OpenClaw requires self-hosting, port forwarding, and manual configuration. Claude Code gives you a form and a sidebar.

This isn't a criticism of OpenClaw. It proved the category. But for developers already in the Claude ecosystem, Anthropic building these capabilities natively means you get the same autonomous agent patterns with tighter integration, better security, and zero infrastructure overhead.

## Frequently Asked Questions

**Do scheduled tasks work in Claude Code CLI?**
Yes, but differently. The CLI has `/loop` and cron tools for session-scoped scheduling that dies when you exit. For persistent scheduling, use Desktop scheduled tasks. For always-on cloud scheduling, use [GitHub Actions](https://code.claude.com/docs/en/github-actions) with a schedule trigger.

**What happens if my computer is asleep when a task is scheduled?**
The run is skipped. When your machine wakes or you reopen Claude Desktop, it checks the last seven days for missed runs, starts one catch-up run for the most recently missed time, and shows a notification. To prevent idle-sleep, enable **Keep computer awake** in Desktop Settings under General. Closing the laptop lid still triggers sleep.

**Can I use scheduled tasks on Linux?**
Desktop scheduled tasks are not available on Linux (macOS and Windows only). Linux users can use the CLI's `/loop` command for session-scoped scheduling, or set up cron jobs running `claude -p` in headless mode for persistent scheduling.

**Do scheduled tasks count against my usage limits?**
Yes. Each run starts a full Claude Code session. Factor this in if you're on a Pro plan with tighter limits. Max and Enterprise plans have more headroom.

**Can a scheduled task create pull requests?**
Yes. Each run is a full Claude Code session with access to your local git setup and any configured MCP servers. Connect GitHub via MCP or connectors and the agent can create branches, commit changes, and open PRs.

**Where are task prompts stored?**
Desktop task prompts live at `~/.claude/scheduled-tasks/<task-name>/SKILL.md`. The file uses YAML frontmatter for name and description, with the prompt as the body. Edit it directly and changes take effect on the next run.

## What This Means for Development Workflows

Scheduled tasks turn Claude from a tool you invoke into an agent that works alongside you on a cadence. Instead of remembering to run a prompt, you define the intent once and let the system handle timing.

Combined with [Remote Control](/blog/remote-control-guide) (monitor sessions from your phone) and [autonomous agent loops](/blog/autonomous-agent-loops) (long-running agentic work), scheduled tasks complete the picture of Claude as a persistent development companion. Remote Control lets you steer sessions from anywhere. Autonomous loops let agents work independently for hours. Scheduled tasks automate the trigger itself.

For teams using multi-agent architectures, this opens a practical pattern: schedule a daily task that reviews overnight agent work, summarizes results, and flags items needing human review. The agent becomes both the worker and the shift supervisor.

Pick one recurring task you do manually today. A morning inbox triage, a weekly metrics pull, an error log scan. Set it up as a scheduled task. Run it for a week. See how much time comes back.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
