---
title: Settings
description: The four Settings tabs, Workflow, Licence, Team and About, and the changes you can ask for on one task.
---

![Settings, Workflow: the Subagents grid, the Second opinion pickers and Notifications, beside the tabs Licence, Team and About; and the overrides for one task, said in words](pathname:///img/diagrams/settings-light.svg)
![Settings, Workflow: the Subagents grid, the Second opinion pickers and Notifications, beside the tabs Licence, Team and About; and the overrides for one task, said in words](pathname:///img/diagrams/settings-dark.svg)

Open **Settings** with the gear at the bottom of the App's sidebar. Changes save at once and apply to every project on this computer.

## Workflow

### Subagents {#subagents}

Fresh agents your agent starts for parts of the work, from the Plan, never from your chat.

- **Workers** research, build the slices and fix what checks find. Default: Sonnet 5.5 in Claude Code, GPT-6.1 Sol in Codex. **No subagents** makes your agent do everything itself: cheaper, with less independent checking.
- **Checking** sets the agents that check the finished change in [Verify](../steps/verify.md). Default: Opus 5.5, GPT-6.1 Sol in Codex.

Your own session's model is yours to pick in your agent; Opus 5.5 is recommended for Discuss and Plan.

### Second opinion {#second-opinion}

With Claude Code and Codex both installed, the other agent reviews a risky Plan and the built change. Each finding becomes an item for you. Pick the model for each direction here.

### Notifications {#notifications}

One switch: tell me when something needs me, or a task ships or stops.

## For one task {#for-one-task}

Say it to your agent in words, such as "skip security", "run a checkpoint after every slice" or "no second opinion". No setting turns an approval off.

## Licence

Your plan or the days left of your trial, and a link to the customer portal for invoices, seats and payment. **On another computer** shows the command that moves your licence.

## Team

- **Your name**, shown to your team.
- **People and groups:** seats, members and their computers, and the groups.
- **Slack:** your team owner connects it once; each member can turn Slack messages off. See [Plan reviews](../team/plans.md#slack).
- **Shared links:** each link with **Copy** and **Revoke**.

## About

The version, **Check now**, and what's new. See [Updates](../install.md#updates).
