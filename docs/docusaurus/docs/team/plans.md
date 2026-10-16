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

1. Select a passage, choose **Give feedback**, then **Ask a teammate**. Mark it **needed before approval** or **opinion only**.
2. They answer with **Looks right**, **Suggest a change** or **Reply**, or let [their agent draft it](agents.md).
3. Your agent updates the Plan. Only your approval moves the task on.

On a shared Plan or Review, **Looks right** sends your review to the owner. **Suggest changes** asks what should change before sending. **Give feedback** leaves a thread without requesting a decision. The owner decides when to approve the task.

## Hand over an approved Plan {#hand-over}

**Hand to the team › Hand over** on the Implement card (or `qualitylayer handover --push`) commits the task and pushes its branch. The first teammate to run `qualitylayer next` on that branch builds it; the final approval comes back to you. It is refused on the base branch, or when the Plan changed since you approved it.

## Slack {#slack}

The team owner connects Slack once in **Settings › Team**. Each person controls **Slack messages to you** and an optional **Morning digest**. Digest timing uses the computer's local time automatically; Slack controls do-not-disturb hours. **Follow** subscribes you to a shared task's updates.

Questions and answers always appear in Team. Slack delivery depends on your own notification setting and account match. If your emails differ, link your own Slack account in Settings.

## People outside your team {#outside-links}

**Share › Copy link** gives a qualitylayer.dev link. Anyone with it can read and comment without an account; the task owner decides approval. The open page updates as the task changes and keeps your unsent answers and comments. A link lasts 14 days; **Revoke** ends it at once. **Include designs** adds previews ([Designs](../designs.md#never-shared)).

If an update cannot be published, Share shows the problem and keeps the last complete copy. Reduce oversized content, then use **Retry sharing** for the team or **Renew** for an external link.

A coding agent can fetch the shared documents as Markdown, no licence needed:

```sh
qualitylayer share fetch --link-file /path/to/private-link.txt --out ./shared-copies --json
```

The file holds the whole link, including the part after `#`; keep it private ([details](../reference/commands.md#read-a-public-share)).

## What is shared {#privacy}

Shared documents, designs and comment bodies are encrypted with your team's key before publication. The server stores their ciphertext. Slack notifications can include task titles and short question or answer excerpts, which pass through the notification service. Your code, the diff and your logs are not included in the shared task. More in [Files and privacy](../reference/files.md#privacy).
