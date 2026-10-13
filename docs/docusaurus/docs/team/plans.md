---
title: Plan reviews
description: With a Team plan, your team helps shape the Plan before any code, each in their own App, and people outside the team comment through a link.
---

With a Team plan, your team comes in twice: on the Plan before any code (this page) and on the [finished change](changes.md). A wrong scope caught in the Plan costs one comment.

![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-light.svg)
![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-dark.svg)

## Ask a teammate

![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-light.svg)
![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-dark.svg)

1. Select a passage or diagram and choose **Ask…**, or mention someone with **@**. Mark it **needed before approval** or **opinion only**.
2. They get a message that opens their App at that passage.
3. They answer with **Looks right**, **Suggest a change** or **Reply**, or let [their own agent draft it](agents.md).
4. The answer goes straight to your agent, which updates the Plan. Only your approval moves the task on.

**Remind** nudges a late answer. While a needed answer holds the approval, the task header says who it waits on.

## Hand over an approved Plan {#hand-over}

A teammate can build a Plan you approved. On the Implement card, **Hand to the team › Hand over** commits the task's files with an approval record and pushes your task's branch; `qualitylayer handover --push` does the same from a terminal. The final approval comes back to you.

| | What happens |
| --- | --- |
| **With a Team plan** | The task appears in your teammates' list with the command to check it out. The first to run `qualitylayer next` on that branch claims it |
| **Without one** | The teammate's agent asks them to confirm they build from your approval |
| **Refused** | The base branch, a Plan that is not approved, or one changed since you approved it |

## Slack {#slack}

Your team owner connects Slack once, in **Settings › Team**. Teammates then get a direct message only when they can act: a question, an answer, a finished build. Messages within five minutes of each other arrive as one, and each link opens the exact step in the App.

**Follow**, in the header of a teammate's shared task, tells you when its Plan is ready, its checks pass, it is in review and it ships. Each member sets their own **Morning digest**, **Quiet hours** (optionally weekends too) and time zone in **Settings › Team**.

## People outside your team {#outside-links}

**Share › Copy link** gives a qualitylayer.dev link. Anyone with it reads the task step by step and comments, without an account; approving stays with your team. Each time you open the link, you read the latest shared copy. The open page updates as the task changes, through all seven steps, and keeps your unsent answers and comments. **Include designs** adds script-free artboard previews that readers can comment on ([Designs](../designs.md#never-shared)). A link lasts 14 days, and **Revoke** ends it at once.

Each shared document offers **Copy as Markdown** and **Download Markdown**. A coding agent can fetch them too, with no licence needed:

```sh
qualitylayer share fetch --link-file /path/to/private-link.txt --out ./shared-copies --json
```

The file holds the whole link, including the part after `#`; keep it private. Fetching changes nothing ([details](../reference/commands.md#read-a-public-share)).

**Groups**, set up by your team owner in **Settings › Team**, make a shared task reach only the people it concerns.

## What is shared {#privacy}

Nothing leaves your computer until you share. Shared plans and comments are encrypted on your computer with your team's key, so the server sees who is involved and the step, never the content. A link carries its own key, which never reaches the server. Your code, the diff and your logs are never sent. A new teammate only installs QualityLayer; the key reaches their computer by itself. More in [Files and privacy](../reference/files.md#privacy).
