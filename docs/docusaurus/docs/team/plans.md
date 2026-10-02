---
title: Review plans as a team
description: Your team reviews the plan before any code is written, in their own Cockpit, and people outside it comment through a link.
---

With a Team plan, your team comes in at two moments: once **before any code**, covered here, and once [after the build](changes.md), to review the finished change.

![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-light.svg)
![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-dark.svg)

This is shift left: your team sees the design and the slices while they are still documents, so a wrong scope or a weak design is caught before anything is built, while a comment still costs minutes.

## How it works on both sides

![Plan review on both sides: you share the task and see your team's comments; your teammate finds it under Team, comments on a passage and approves or asks for changes](pathname:///img/diagrams/team-plan-light.svg)
![Plan review on both sides: you share the task and see your team's comments; your teammate finds it under Team, comments on a passage and approves or asks for changes](pathname:///img/diagrams/team-plan-dark.svg)

| | Your side | Your teammates' side |
| --- | --- | --- |
| **Start** | In **Share**, switch on **Your team** | The task appears under **Team** in their sidebar |
| **Read** | You review as usual | They read the same plan in their own Cockpit |
| **Comment** | Their comments arrive as **From your team**, marked once they reach your agent | They comment on any passage, and approve or ask for changes |
| **Decide** | Your agent answers every comment and updates the plan where it agrees; only your approval moves the task on, in the Cockpit or typed as `approve` in the task's chat | Their approval shows as advice in your next-step bar |
| **Follow** | | The **Team** workspace shows every shared task, its step, and who it waits for |

![A shared plan: Ben approves, Anna asks for changes, Sam comments through a link; your agent answers every comment and you decide](pathname:///img/diagrams/team-light.svg)
![A shared plan: Ben approves, Anna asks for changes, Sam comments through a link; your agent answers every comment and you decide](pathname:///img/diagrams/team-dark.svg)

## People outside your team

Under **People outside your team**, **Create link** shares the plan as it is now. Anyone with the link can read it and comment under a name they type, without an account, and needs no seat. The link expires after 14 days; **Renew** shares the current plan for another 14, and **Revoke** ends it at once. Their comments reach you like your team's, as advice.

The link carries a key after the `#`, and your browser never sends that part to a server. The page opens the plan with it, and a guest's comment is encrypted in the guest's browser before it is sent. A link without its key shows nothing readable, only the message "This link is missing its key".

## Ask a teammate

Mention someone with **@**, or choose **Ask…** on any passage, diagram, table, document, build item or review thread. They get a notification first, and their answer reaches your agent. Mark the question as required, and the approval waits for the answer. At any approval, **Ask for review** names the people whose review is required or optional.

## Seats and what is shared

**Settings → Team** shows your seats, your members with their computers, and your shared links; seats are managed in the customer portal. Sharing sends the documents a reviewer reads (frame or PRD, research or diagnosis, design or TDD with its mockups, outline overview), the task's title and step, and the comments. It never sends your code, the diff or your logs. See [Files and privacy](../reference/files.md).

## Who can read your plans

Plans, task titles, comments, questions and reviews are encrypted on your machine before they are shared, so we can't read them. Only your team's computers, and people with a guest link, can open them. What stays readable to us is who shared a task, an ID that tells tasks apart (never its title), when, and its stage. The page behind a guest link loads its code from us; the plan itself is opened in the guest's browser with the key in the link.

If you connect Slack, a nudge's task title and question pass through our server to Slack and aren't stored.

A new teammate on your Team plan needs no code, key or setup step: they install QualityLayer. One of your team's computers hands over the key the next time it checks in, normally within a minute. Until then, a shared task reads **Joining the team** and names who can let the computer in. Every new computer shows in **Settings → Team**. When someone leaves the team, what you share from then on can't be read by their computer.
