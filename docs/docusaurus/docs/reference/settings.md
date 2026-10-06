---
title: Settings
description: The four Settings tabs, Workflow, Licence, Team and About, and the changes you can ask for on one task.
---

![Settings, Workflow: Planning defaults and Build defaults, each with a tab per agent, the independent review, the second opinion and Notifications, beside the tabs Licence, Team and About; and the overrides for one task, said in words](pathname:///img/diagrams/settings-light.svg)
![Settings, Workflow: Planning defaults and Build defaults, each with a tab per agent, the independent review, the second opinion and Notifications, beside the tabs Licence, Team and About; and the overrides for one task, said in words](pathname:///img/diagrams/settings-dark.svg)

Open **Settings** with the gear at the bottom of the App's sidebar. Changes save at once and apply to every project on this computer.

## Workflow

### Planning and Build defaults {#defaults}

Two cards, one agent at a time: a tab each for **Claude Code**, **Codex** and **Another agent**. The tab marked **Default** is the one **+ New** and Implement Start open on; **Make default** moves the mark, so you can plan with Claude Code and build with Codex.

- **Planning defaults** are what **+ New** opens with: the model, the effort and where the session starts. Discuss and Plan run on them. Recommended: the most capable model you can afford, Opus 5.5 or Fable 5.1, at High effort or more.
- **Build defaults** are what [Implement Start](../steps/implement.md#start-implement) opens with: the orchestrator's model (Opus 5.5 by default, Fable 5.1 if it fits your budget), the workers' model (Sonnet 5.5), one effort for both (High), and where the build starts (the session that planned the task). Anything you change at Implement Start applies to that build only.
- **Another agent** runs on its own models and effort, set in that agent, so there is nothing to pick; it gets one prompt to paste.

**Use recommended** brings a tab back to the recommended setup.

### Independent review {#independent-review}

On every task, an agent that never wrote the code decides whether the finished change passes in [Verify](../steps/verify.md). Pick its model for Claude Code (Opus 5.5) and for Codex (GPT-6.1 Sol).

### Second opinion {#second-opinion}

With Claude Code and Codex both installed, the other agent reviews a risky Plan and the built change. Each finding becomes an item for you. Pick the model for each direction here, or turn it off; a task that asks for one still gets it.

### Notifications {#notifications}

One switch: tell me when something needs me, or a task ships or stops. A second switch opens the right sidebar by itself when a teammate comments or asks.

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
