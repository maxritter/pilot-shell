---
title: "Claude Code Routines: AI Automation Replacing No-Code Tools"
description: "Set up Claude Code routines that run on schedule, API call, or webhook. Replace no-code automation workflows with natural language prompts."
slug: routines-guide
date: 2026-04-14
authors:
  - max-ritter
tags:
  - guide
  - development
---

Set up Claude Code routines that run on schedule, API call, or webhook. Replace no-code automation workflows with natural language prompts.

<!-- truncate -->

Running Claude Code locally means your AI agent only works when your laptop is open. You close the lid, the agent stops. You forget to run the morning prompt, the review doesn't happen. [Scheduled tasks](/blog/scheduled-tasks) solved part of this by letting you automate recurring prompts on your machine, but the dependency on a running local process remained. Routines eliminate that constraint entirely.

**Claude Code routines** are saved configurations (a prompt, one or more repositories, and your connectors) that run on Anthropic's cloud infrastructure. No terminal window. No local machine. Define the work once, attach a trigger, and Claude handles the rest whether you're asleep, on a flight, or just closed your laptop for the weekend.

Routines ship today (April 14, 2026) in research preview across all paid plans: Pro, Max, Team, and Enterprise. Create them at [claude.ai/code/routines](https://claude.ai/code/routines) or with `/schedule` in the CLI.

## Three Trigger Types

Every routine supports one or more triggers. You can combine them freely on a single routine, so the same prompt can fire on a schedule, respond to an API call, and react to GitHub events simultaneously.

### Scheduled Routines

Set a cadence and walk away. Scheduled routines run hourly, daily, on weekdays, or weekly. Times are entered in your local timezone and converted automatically.

```
/schedule daily PR review at 9am
```

The `/schedule` command in the CLI creates scheduled routines conversationally. If you were already using `/schedule` for [local scheduled tasks](/blog/scheduled-tasks), the same command now creates cloud routines instead. Nothing to migrate.

For custom intervals like "every two hours" or "first Monday of the month," pick the closest preset in the web UI, then run `/schedule update` in the CLI to set a specific cron expression. The minimum interval is one hour.

Runs may start a few minutes after the scheduled time due to stagger. The offset is consistent per routine, so a 9am daily routine always fires at the same offset.

### API Routines

Each routine can expose its own HTTP endpoint with a dedicated bearer token. POST to the endpoint and Claude spins up a session, runs your prompt, and returns a session URL you can open in real time.

The killer detail: you can pass context with every trigger. The request body accepts a `text` field that gets appended to the routine's configured prompt as a one-shot user turn. Point your alerting system, deploy pipeline, or internal tools directly at Claude.

```
curl -X POST https://api.anthropic.com/v1/claude_code/routines/trig_01ABC.../fire \
  -H "Authorization: Bearer sk-ant-oat01-xxxxx" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sentry alert SEN-4521 fired in prod. Stack trace attached."}'
```

A successful response returns the session ID and URL:

```
{
  "type": "routine_fire",
  "claude_code_session_id": "session_01HJKLMNOPQRSTUVWXYZ",
  "claude_code_session_url": "https://claude.ai/code/session_01HJKLMNOPQRSTUVWXYZ"
}
```

Each routine gets its own token, scoped to triggering that routine only. The token is shown once when generated and cannot be retrieved later, so store it immediately in your alerting tool's secret store or a password manager. Rotate or revoke tokens from the routine's edit page on the web.

The `/fire` endpoint ships under the `experimental-cc-routine-2026-04-01` beta header. The two most recent previous header versions continue to work so callers have time to migrate when breaking changes ship.

### Webhook Routines (GitHub)

Subscribe a routine to GitHub repository events and Claude reacts automatically. Each matching event starts its own session. Session reuse across events is not available, so two pushes or two PR updates produce two independent sessions. The supported event list is extensive:

| Event Category | Triggers When |
| --- | --- |
| **Pull request** | Opened, closed, assigned, labeled, synchronized, or updated |
| **Pull request review** | Submitted, edited, dismissed |
| **Pull request review comment** | Created, edited, deleted on a diff |
| **Push** | Commits pushed to a branch |
| **Release** | Created, published, edited, deleted |
| **Issues** | Opened, edited, closed, labeled, or updated |
| **Issue comment** | Created, edited, deleted |
| **Sub issues** | Sub-issue or parent issue added or removed |
| **Commit comment** | Comment on a commit or diff |
| **Discussion** | Created, edited, answered, or updated |
| **Discussion comment** | Created, edited, deleted |
| **Check run** | Created, requested, rerequested, completed |
| **Check suite** | Completed or requested |
| **Merge queue entry** | PR enters or leaves the merge queue |
| **Workflow run** | GitHub Actions workflow starts or completes |
| **Workflow job** | GitHub Actions job queued or completes |
| **Workflow dispatch** | Workflow manually triggered |
| **Repository dispatch** | Custom repository_dispatch event |

You can filter pull request events by author, title, body text, base branch, head branch, labels, draft state, merge state, and whether the PR comes from a fork. All filter conditions must match for the routine to fire.

Webhook triggers require installing the Claude GitHub App on the target repository. The trigger setup prompts you through this. Note that running `/web-setup` in the CLI grants clone access but does not install the GitHub App, so webhook delivery requires the separate installation step.

During the research preview, GitHub webhook events are subject to per-routine and per-account hourly caps. Events beyond the limit are dropped until the window resets.

## Routines vs. Scheduled Tasks vs. GitHub Actions

If you're coming from [scheduled tasks](/blog/scheduled-tasks) or [GitHub Actions](https://code.claude.com/docs/en/github-actions), here's how routines compare:

| Aspect | Routines | Desktop Scheduled Tasks | CLI /loop | GitHub Actions |
| --- | --- | --- | --- | --- |
| **Runs on** | Anthropic cloud | Your machine (Desktop app) | Your machine (CLI session) | GitHub runners |
| **Persistence** | Survives laptop shutdown | Survives app restart | Dies when session exits | CI-managed |
| **Trigger types** | Schedule + API + GitHub webhooks | Schedule only | Interval polling only | GitHub events + cron |
| **Setup** | Web UI, CLI `/schedule`, or Desktop | Desktop sidebar form | `/loop 5m prompt` | YAML workflow files |
| **Connectors** | Full MCP connector access | Full local MCP access | Session MCP access | Limited to Actions marketplace |
| **Daily limits** | 5-25 per plan | Unlimited | 50 per session | Minutes-based billing |
| **Best for** | Unattended automation, event-driven workflows | Local recurring tasks | Quick polling | CI/CD pipelines |

The mental model: scheduled tasks are for work that needs your local filesystem and tools. Routines are for work that should happen regardless of whether your machine is on. GitHub Actions are for CI/CD pipelines already embedded in your repository workflow.

## Routines vs. No-Code Automation (N8N, Make.com)

Traditional automation platforms like N8N and Make.com follow a three-part pattern: an event triggers the workflow, a chain of drag-and-drop logic nodes processes the data, and the output lands in some destination like Slack, a CRM, or a database. Building that middle layer is where the real work lives. You wire up nodes, map variables between steps, configure authentication for each service, and debug data format mismatches across the chain.

Routines collapse that middle layer into a natural language prompt. The same three-part pattern still applies (event, logic, output), but instead of building the logic visually with nodes, you describe what you want in plain text. Claude handles the API calls, data extraction, conditional logic, and formatting internally.

What this changes in practice:

- **No node configuration.** Describe the logic instead of dragging connectors between boxes.
- **No variable mapping.** Claude reads the input and figures out which fields matter.
- **No per-service authentication setup.** Connectors handle OAuth centrally.
- **Faster iteration.** Changing a workflow means editing text, not rewiring a visual pipeline.
- **Workflow conversion.** You can export an existing N8N workflow as JSON, paste it into a Claude Code session, and ask Claude to convert it into a routine prompt. The same works with Make.com blueprints or any SOP document that describes a step-by-step process.

The tradeoff is cost. Automation platforms run on compute with fixed pricing regardless of complexity. Routines run on tokens, so a workflow that processes large documents or generates lengthy outputs costs more per execution. For high-frequency, simple transformations (reformatting a webhook payload, routing a message based on a keyword), a traditional platform is still cheaper. Routines are strongest when the task requires reasoning: summarizing, drafting, analyzing context, or making judgment calls that would require dozens of conditional branches in a visual builder.

## Setting Up Your First Routine

### From the Web (Recommended)

1. Visit [claude.ai/code/routines](https://claude.ai/code/routines) and click **New routine**
2. Name the routine and write the prompt. This is the most important step: routines run autonomously with no permission prompts, so the prompt must be self-contained and explicit about what success looks like
3. Select one or more GitHub repositories. Each gets cloned at the start of every run, starting from the default branch. Claude creates `claude/`-prefixed branches for its changes
4. Choose a cloud environment (controls network access, environment variables, and setup scripts)
5. Add one or more triggers (schedule, API, GitHub event, or any combination)
6. Review connectors. All your connected MCP connectors are included by default. Remove any the routine doesn't need
7. Click **Create**. Use **Run now** to test immediately. Switch to the **Calendar** tab on the routines page to see a visual timeline of all scheduled runs across your routines

### From the CLI

```
/schedule daily PR review at 9am
```

Claude walks through the same information the web form collects, then saves the routine to your account. The routine appears at [claude.ai/code/routines](https://claude.ai/code/routines) immediately.

CLI management commands:

| Command | Purpose |
| --- | --- |
| `/schedule` | Create a new scheduled routine conversationally |
| `/schedule list` | View all routines |
| `/schedule update` | Modify an existing routine |
| `/schedule run` | Trigger a routine immediately |

Note: `/schedule` in the CLI creates scheduled routines only. To add API or GitHub triggers, edit the routine on the web.

### From the Desktop App

Open **Schedule** in the Desktop sidebar, click **New task**, and choose **New remote task**. Choosing **New local task** instead creates a [local scheduled task](/blog/scheduled-tasks) that runs on your machine. Both types appear in the same grid.

## How Routines Execute

Routines run as full Claude Code cloud sessions on Anthropic-managed infrastructure. Each run gets:

- A fresh clone of your selected repositories (starting from the default branch)
- Access to all included connectors (Slack, Linear, Google Drive, etc.)
- Access to skills committed to the cloned repository
- Network access as configured in the cloud environment
- Environment variables from the selected environment
- A setup script that runs before the session starts (install dependencies, configure tools)

By default, Claude can only push to branches prefixed with `claude/`. This prevents routines from accidentally modifying protected branches. Enable **Allow unrestricted branch pushes** per repository if you need Claude to push elsewhere.

Routines belong to your individual claude.ai account. They are not shared with teammates. Anything a routine does through your connected GitHub identity or connectors appears as you: commits carry your GitHub user, Slack messages use your linked account, and Linear tickets are created under your identity.

## Use Cases That Actually Matter

### Alert Triage (API Trigger)

Your monitoring tool (Datadog, Sentry, PagerDuty) calls the routine's API endpoint when an error threshold is crossed, passing the alert body as the `text` field. The routine pulls the stack trace, correlates it with recent commits in the repository, and opens a draft pull request with a proposed fix and a link back to the alert. On-call reviews the PR instead of starting from a blank terminal.

### Bespoke Code Review (GitHub Trigger)

A GitHub trigger fires on `pull_request.opened`. The routine applies your team's custom review checklist, leaving inline comments for security, performance, and style issues. It adds a summary comment so human reviewers can focus on design decisions instead of mechanical checks. Filter by base branch, labels, or author to scope which PRs get the automated review.

### Nightly Backlog Grooming (Schedule Trigger)

A schedule trigger runs every weeknight against your issue tracker via a connector. The routine reads issues opened since the last run, applies labels, assigns owners based on the area of code referenced, and posts a summary to Slack or [Telegram via Channels](/blog/claude-code-channels). The team starts each morning with a groomed queue instead of spending 30 minutes triaging.

### Deploy Verification (API Trigger)

Your CD pipeline calls the routine's endpoint after each production deploy. The routine runs smoke checks against the new build, scans error logs for regressions, and posts a go/no-go to the release channel before the deploy window closes. No human staring at dashboards waiting for errors to surface.

### Library Porting (GitHub Trigger)

A GitHub trigger fires on `pull_request.closed` filtered to merged PRs in your Python SDK repository. The routine ports the change to the Go SDK in a separate repository and opens a matching PR. Two libraries stay in sync without a human re-implementing each change by hand.

### Weekly Docs Drift (Schedule Trigger)

A weekly schedule trigger scans merged PRs since the last run, flags documentation that references changed APIs, and opens update PRs against the docs repository. Documentation stays current without relying on developers remembering to update it during feature work.

### Daily Email Triage (Schedule Trigger)

A morning schedule trigger checks your inbox via the Gmail connector, pulls unread messages, and reviews prior conversation history with each sender for context. The routine drafts contextual replies, stages them as drafts in your email, and sends a Slack summary with highlights and draft links. You wake up to a pre-sorted inbox with replies ready to review and send.

### Proposal Generation (API Trigger)

Your call recording tool (Fireflies, Otter, Fathom) sends a transcript to the routine's API endpoint after a sales call. The routine extracts deal terms, client requirements, and pricing discussed during the conversation, then generates a formatted proposal using your template. The finished document posts to Slack or gets committed to a repository, ready to review and send while the conversation is still fresh.

### Post-Call Follow-Up Chain (API Trigger)

After a sales call, a webhook fires the routine with the call transcript. The routine drafts an immediate follow-up email referencing specific discussion points, generates a summary of the proposed engagement, and triggers a second routine (via API chaining) to monitor for a signed contract. When the signature lands, another routine sends the onboarding package with calendar invites and welcome materials. The entire post-call pipeline runs without manual steps.

## Writing Effective Routine Prompts

Since routines run autonomously with no interactive approval, the prompt quality determines the outcome quality. If you're familiar with Claude Code skills, think of a routine prompt as a skill that runs without a human in the loop. The same principles apply (structured steps, clear success criteria, explicit tool usage) but with less room for error since nobody is there to course-correct mid-run. Be more precise than you would in a skill. A few principles from writing prompts for [autonomous agent workflows](/blog/autonomous-agent-loops):

**Be explicit about success criteria.** Don't say "review PRs." Say "review open PRs against the /auth module, check for SQL injection vulnerabilities and missing input validation, leave inline comments with severity labels, and add a summary comment with pass/fail status."

**Define boundaries.** Specify what the routine should and should not do. "Create draft PRs only. Never merge. Never push to main. If unsure about a fix, leave a comment instead of committing code."

**Handle edge cases.** "If no new issues were opened since the last run, post a 'nothing to triage' message to #dev-standup and exit."

**Include output instructions.** Tell Claude where to post results: "Post the summary to #releases in Slack" or "Open a PR against the docs repo" or "Comment on the triggering issue."

## Plan Limits

Routines draw from the same subscription usage as interactive sessions. On top of that, each plan has a daily cap on routine runs:

| Plan | Daily Routine Runs |
| --- | --- |
| **Pro** | 5 |
| **Max** | 15 |
| **Team** | 25 |
| **Enterprise** | 25 |

Organizations with extra usage enabled can exceed these caps on metered overage. Without extra usage, additional runs are rejected until the daily window resets. Check your current consumption at [claude.ai/settings/usage](https://claude.ai/settings/usage).

## When Routines Aren't the Right Fit

Not every automation should be a routine. High-frequency workflows that fire dozens of times per hour (webhook-per-message Slack bots, real-time data pipelines) will burn through daily run limits and token budgets quickly. Simple transformations that don't require reasoning, like reformatting a payload, routing based on a keyword match, or updating a spreadsheet row, run cheaper and faster on traditional automation platforms like N8N or Make.com. If your workflow is already working well on one of those platforms and doesn't need AI judgment, there's no reason to migrate it.

Routines make sense when the task requires reading context, drafting original content, analyzing code, or making decisions that would take dozens of conditional branches to express in a visual builder. The question to ask: does this workflow need to think, or just move data? If it just moves data, keep it where it is.

## The Evolution from Local to Cloud

If you've been following Claude Code's trajectory, routines are the natural next step in a clear progression:

1. **CLI `/loop`**: Session-scoped polling that dies when you exit. Good for "watch this deploy for the next hour." Still available, still useful for [quick in-session monitoring](/blog/scheduled-tasks)
2. **Desktop scheduled tasks**: Persistent, survive restarts, run as long as the app is open. The first real automation layer for Claude Code
3. **[Remote Control](/blog/remote-control-guide)**: Monitor and steer sessions from your phone. Freed you from the desk but still required a running machine
4. **Routines**: Fully cloud-hosted. Your laptop can be off. The agent runs anyway

Each step removed a dependency. `/loop` removed the need to type the prompt repeatedly. Scheduled tasks removed the need to remember timing. Remote Control removed the need to be at your desk. Routines remove the need for your machine to be running at all.

For teams already using async workflows and multi-agent patterns, routines are the missing orchestration layer. You can now chain automated triggers (a deploy fires an API routine, which runs smoke checks, which posts results to Slack) without any human in the loop until something needs attention.

## Frequently Asked Questions

**What happens to my existing `/schedule` tasks?**
Nothing breaks. The `/schedule` command in the CLI now creates cloud routines instead of local tasks. Your existing Desktop scheduled tasks remain untouched and continue running locally. Routines and local scheduled tasks are separate systems that coexist.

**Do routines have access to my local files?**
No. Routines run on Anthropic's cloud infrastructure and clone the repositories you configure. They do not access your local filesystem. For work that needs local files, use [Desktop scheduled tasks](/blog/scheduled-tasks) instead.

**Can a routine trigger another routine?**
Not directly through the UI, but yes through the API. One routine can call another routine's API endpoint using a `curl` command in its prompt, creating chains of automated workflows.

**Can routines use MCP servers?**
Routines use connectors (Anthropic's cloud-hosted MCP integrations) rather than locally-running MCP servers. All your connected connectors are available by default when creating a routine. This includes integrations like Slack, Linear, Google Drive, and others.

**Are routine runs visible to teammates?**
Routines belong to your individual account and are not shared with teammates. However, the actions a routine takes through your connected accounts (GitHub commits, Slack messages, Linear tickets) are visible to anyone with access to those services, since they appear under your identity.

**What model do routines use?**
The routine creation form includes a model selector. The selected model runs on every execution. You can change it at any time by editing the routine.

**Can routines push to any branch?**
By default, routines can only push to `claude/`-prefixed branches. Enable **Allow unrestricted branch pushes** per repository in the routine settings if you need to push elsewhere. This default prevents accidental modifications to protected branches.

**Is there a way to test a routine without waiting for the trigger?**
Yes. Click **Run now** on the routine's detail page at [claude.ai/code/routines](https://claude.ai/code/routines) to start a run immediately. From the CLI, use `/schedule run`.

**What happens when a GitHub webhook exceeds the hourly cap?**
Events beyond the per-routine or per-account hourly cap are dropped until the window resets. The caps exist during the research preview and may change.

## Getting Started

Pick one piece of work you do repeatedly that doesn't need your local machine. A nightly issue triage. A post-deploy smoke check. A PR review checklist. Create a routine for it at [claude.ai/code/routines](https://claude.ai/code/routines), run it once manually to verify the output, then let it run on its own.

If you're already using [scheduled tasks](/blog/scheduled-tasks) for recurring local work, consider which of those could move to routines. Anything that doesn't depend on your local filesystem is a candidate. Anything that should run even when your laptop is closed is a strong candidate.

### Migrating Existing Workflows

If you have workflows on N8N, Make.com, or similar platforms that would benefit from AI reasoning, you don't have to rebuild them from scratch. Export the workflow (N8N exports as JSON, Make exports as a blueprint), paste it into a Claude Code session, and ask Claude to convert it into a routine. Claude reads the node logic, understands what each step does, and produces natural language instructions that replicate the flow. You can also just describe the workflow in plain text. Any SOP document or step-by-step process description works as input.

For developers building with Claude Code's agent capabilities, routines unlock a new pattern: persistent, event-driven agents that respond to production signals in real time. Combined with skills committed to your repository, connectors for external services, and the ability to chain routines through API triggers, you have the building blocks for autonomous development workflows that operate continuously without human intervention.

The research preview is live today. Behavior, limits, and the API surface may change, but the core concept is stable: define the work once, let Claude handle the when.

[Scheduled Tasks](/blog/scheduled-tasks)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
