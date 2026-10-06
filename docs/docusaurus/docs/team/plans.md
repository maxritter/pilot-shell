---
title: Plan reviews
description: With a Team plan, your team helps shape the Plan before any code, each in their own App, and people outside the team comment through a link.
---

With a Team plan, your team comes in twice: on the Plan **before any code**, covered here, and on the [finished change](changes.md).

![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-light.svg)
![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-dark.svg)

A wrong scope or a weak decision is caught while it is still a plan, when a comment costs minutes.

## Ask a teammate

![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-light.svg)
![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-dark.svg)

1. **Select** a passage or a diagram and choose **Ask…** to ask the domain expert on your team, or mention someone with **@**.
2. **They get a message** that opens the App at that passage.
3. **They answer** with **Looks right**, **Suggest a change** or **Reply**. Their own agent can [draft the reply](agents.md).
4. **The answer goes straight to your agent,** which updates the Plan. Only your approval moves the task on.

An ask can be **needed before approval** or **opinion only**. **Remind** nudges a late answer.

## Slack {#slack}

Your team owner connects Slack once, in **Settings › Team**. From then on, teammates get a direct message when something waits for them: a question, an answer, or a build that finished. Messages go out only when a person can act.

## People outside your team {#outside-links}

**Copy link** in **Share** gives a qualitylayer.dev link that works like a shared document: anyone with it reads the task, step by step, and comments, without an account. The link always shows the latest state, with the time it was last updated, so you never share it again after a change. In place of a design it shows a still picture, marked as one. The link lasts 14 days; **Revoke** ends it at once. Outside reviewers comment only; approving stays with your team.

## Groups

Groups split a team, so a shared task reaches only the people it concerns. Your team owner sets them up in **Settings › Team**.

## What is shared {#privacy}

Sharing is optional; until you share, everything stays on your computer. Shared plans and comments are encrypted on your computer with your team's key, so the server sees who is involved and the step, not your plans or comments. A link carries its own key, which never reaches the server. Your code, the diff and your logs are never sent. A new teammate only installs QualityLayer; their computer gets the team's key by itself.

See [How it fits together](../intro.md#how-it-fits-together) and [Files and privacy](../reference/files.md).
