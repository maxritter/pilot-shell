---
title: Plan reviews
description: With a Team plan, your team helps shape the Plan before any code, each in their own App, and people outside the team comment through a link.
---

With a Team plan, your team reviews the Plan before any code (this page) and the [finished change](changes.md).

![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-light.svg)
![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-dark.svg)

## Ask a teammate

![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-light.svg)
![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-dark.svg)

1. Select a passage and choose **Ask…**, or type **@**. Mark it **needed before approval** or **opinion only**.
2. They answer with **Looks right**, **Suggest a change** or **Reply**, or let [their agent draft it](agents.md).
3. Your agent updates the Plan. Only your approval moves the task on.

## Hand over an approved Plan {#hand-over}

**Hand to the team › Hand over** on the Implement card (or `qualitylayer handover --push`) commits the task and pushes its branch. The first teammate to run `qualitylayer next` on that branch builds it; the final approval comes back to you. It is refused on the base branch, or when the Plan changed since you approved it.

## Slack {#slack}

The team owner connects Slack once in **Settings › Team**. Teammates get a message only when they can act, linking to the exact step. **Follow** on a shared task tells you when it moves on. Each member sets **Morning digest** and **Quiet hours**.

## People outside your team {#outside-links}

**Share › Copy link** gives a qualitylayer.dev link. Anyone with it can read and comment without an account; only your team approves. The open page updates as the task changes and keeps your unsent answers and comments. A link lasts 14 days; **Revoke** ends it at once. **Include designs** adds previews ([Designs](../designs.md#never-shared)).

A coding agent can fetch the shared documents as Markdown, no licence needed:

```sh
qualitylayer share fetch --link-file /path/to/private-link.txt --out ./shared-copies --json
```

The file holds the whole link, including the part after `#`; keep it private ([details](../reference/commands.md#read-a-public-share)).

## What is shared {#privacy}

Nothing leaves your computer until you share. Shared plans and comments are encrypted with your team's key, so the server never sees the content. Your code, the diff and your logs are never sent. More in [Files and privacy](../reference/files.md#privacy).
