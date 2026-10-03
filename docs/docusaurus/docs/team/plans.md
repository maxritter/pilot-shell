---
title: Review plans as a team
description: With a Team plan, your team helps shape the Plan before any code, each in their own App, and people outside it comment through a link.
---

With a Team plan, your team comes in at two moments: once **before any code**, covered here, and once [after the build](changes.md), to review the finished change.

![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-light.svg)
![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-dark.svg)

Your team sees the decisions and the slices while they are still a plan. A wrong scope or a weak decision is caught before anything is built, while a comment still costs minutes.

## Ask a teammate

![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-light.svg)
![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-dark.svg)

Choose **Ask…** on any passage, diagram, table, section or document, on the approval itself, on a build item or on a comment thread. Or mention someone with **@**. They answer with **Looks right**, **Suggest a change** or **Reply**, and the answer goes straight to your agent. Mark a question as required, and the approval waits for the answer. At any approval, **Ask for review** names the people whose review is required or optional.

A teammate can also hand your question to their own Claude Code, Codex or Grok Bot. See [Teammates' agents](agents.md).

## How it works on both sides

| | Your side | Your teammates' side |
| --- | --- | --- |
| **Start** | In **Share**, switch on **Your team** | The task appears under **Team** in their App |
| **Read** | You review as usual | They read the same Plan in their own App |
| **Comment** | Their comments arrive as **From your team**, marked once they reach your agent | They comment on any passage, and approve or ask for changes |
| **Decide** | Your agent answers every comment and updates the Plan where it agrees. Only your approval moves the task on | Their approval shows as advice in your review bar |

## The Team space

The **Team** space lists every shared task by person and step, with the questions waiting for you on top. Each task shows who it waits for.

## Slack messages

Your team owner connects your Slack workspace once: in **Settings › Team**, **Slack** › **Add to Slack**, then approve the QualityLayer app in Slack. The card shows the connected workspace, and **Disconnect** removes it. Members see the connection; only the owner changes it.

From then on, teammates get a direct message in Slack when something waits for them or for you:

- **You're asked.** A teammate asks you, or hands an ask on to you.
- **A reminder.** The person who asked presses **Remind**.
- **Your turn.** The last answer your approval waits for is in.
- **Build finished.** The build of your task is done and now in Verify.
- **Build stopped.** The build stopped and needs your decision.

Each message links to a page on qualitylayer.dev that opens the question in the reader's App. Without the App, the page offers the browser page on their computer or the download. On a phone it offers to copy the link for later. An ask message also says how to answer with your own agent: `/ql answer <ask>`. No key ever passes through Slack.

Only people with a seat on your team get messages, matched by e-mail address to their Slack account. Someone with no account in the connected workspace still gets the ask in their App. Slack only nudges: the answers go in the App.

## People outside your team {#outside-links}

Under **People outside your team**, **Create link** shares the Plan as it is now. Anyone with the link can read it and comment under a name they type, without an account, and needs no seat. The link expires after 14 days; **Renew** shares the current Plan for another 14, and **Revoke** ends it at once. Their comments reach your agent like your team's, as advice.

The link carries a key after the `#`, and your browser never sends that part to a server. The page opens the Plan with it, and a guest's comment is encrypted in the guest's browser before it is sent. A link without its key shows only the message "This link is missing its key".

## Groups

Groups split a team, so a shared task reaches only the people it concerns. Your team owner manages them in **Settings › Team › Groups**: **New group**, a name, and the members to pick from the seats. A person can be in more than one group. Members see the groups read-only, with their own marked.

A task shared into a group is seen by that group, your team owner, the task's owner, and anyone asked on it. Everyone else sees neither the task nor its Plan; an old link to it says "This task isn't shared with you". In **Share**, **Share with** picks the group:

- With no groups set up, the whole team sees the task.
- In one group, that group is already picked.
- In several, you choose a group or **Whole team**. An ask on a task you haven't shared yet asks the same, and keeps what you wrote.

Asking someone outside the group lets them open that one task, and the ask says so before you send it. Deleting a group leaves its tasks hidden from everyone but their owners, your team owner and the people already asked, until you share a task again.

## What is shared, and who can read it

Sharing sends the Plan and its progress: the documents a reviewer reads with their mockups, the task's title and step, and the comments. It never sends your code, the diff or your logs.

Everything shared is encrypted on your machine before it leaves, so we can't read it. Only your team's computers, and people with a guest link, can open it. What stays readable to us is who shared a task, who was asked on it, an ID that tells tasks apart (never its title), when, and its step. The page behind a guest link loads its code from us; the Plan itself is opened in the guest's browser with the key in the link.

If you connect Slack, a message's task title and question pass through our server to Slack. When Slack is busy, they wait on our server for a retry, a day at most, and are deleted after that.

A new teammate needs no code, key or setup step: they install QualityLayer. One of your team's computers hands over the key the next time it checks in, normally within a minute. Until then, a shared task reads **Joining the team** and names who can let the computer in. Every new computer shows in **Settings › Team**, with your seats and members; seats are managed in the customer portal. When someone leaves the team, what you share from then on can't be read by their computer.

See [Files and privacy](../reference/files.md).
