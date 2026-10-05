---
title: Review plans as a team
description: With a Team plan, your team helps shape the Plan before any code, each in their own App. Questions and answers, Slack messages, reminders, and people outside the team who comment through a link.
---

With a Team plan, your team comes in at two moments: once **before any code**, covered here, and once [after the build](changes.md), to review the finished change.

![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-light.svg)
![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-dark.svg)

Your team sees the decisions and the slices while they are still a plan. A wrong scope or a weak decision is caught before anything is built, while a comment still costs minutes.

## Ask a teammate

![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-light.svg)
![Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too](pathname:///img/diagrams/team-dark.svg)

Select a passage, a diagram, a table, a section or a whole document, or point at the approval itself, a build item or a comment thread. Choose **Ask…**, pick the person and write the question. Or mention someone with **@**. Asking about a passage works the same as commenting. The Slack message opens the App at that passage.

An ask is **Needed before approval** or **Opinion only**. A needed ask blocks the approval until it is answered, or until the asker chooses **Approve without Anna** in the App. At any approval, **Ask for review** names the people whose review is required or optional.

The person asked sees it under **Questions for you**, with the passage or diagram in view. They answer **Looks right**, **Suggest a change** or **Reply**, and the answer goes straight to your agent. They can also **Draft with my agent**, **Hand to someone else**, or **Open the Plan at this diagram**.

A teammate can hand your question to their own coding agent. See [Teammates' agents](agents.md).

## How it works on both sides

| | Your side | Your teammates' side |
| --- | --- | --- |
| **Start** | In **Share**, choose your team or a group | The task appears under **Team** in their App |
| **Read** | You review as usual | They read the same Plan in their own App |
| **Ask and answer** | Your question waits under **Your questions to others**. When an answer arrives you get a Slack message and a notification, with the answer quoted | A question for them appears under **Questions for you** |
| **Decide** | Your agent answers every comment and updates the Plan where it agrees. Only your approval moves the task on, given in the terminal when your agent asks "Approve the Plan?" | Their approval shows as advice in your review |

## The Team space

The **Team** space lists the questions waiting for you first. Below them:

- **Your questions to others**, with how long each has waited. A question waiting over a day turns amber.
- **Working now**: each member's tasks with the step.
- **Team activity** as one line you can open.

The **Team** switch in the sidebar counts the questions for you. Only these send you a notification.

## Reminders {#reminders}

If an answer is late, press **Remind** on the question. It sends one Slack message and one notification, at most once every 4 hours per question. The list then shows "reminded 2 h ago · next reminder in 2 h". Nothing reminds anyone on its own.

## Slack messages {#slack}

Your team owner connects your Slack workspace once: in **Settings › Team**, **Slack** › **Add to Slack**, then approve the QualityLayer app in Slack. The install link works once, for 10 minutes, in the browser that started it. Members see the connection; only the owner changes it.

The card shows what state the connection is in: not connected, connecting, connected, or failed with one sentence and the next step. When connected it says how many teammates it found in Slack, such as "128 of 130 teammates found in Slack", and names the ones it did not find. They still see their questions in the App. **Check again** asks Slack once more.

**Disconnect** cuts the connection and revokes the token. Messages still waiting to go out are dropped.

Teammates are matched by the e-mail address of their seat. Each member has a **Slack messages to you** switch in **Settings › Team**. Off stops Slack messages to that person only; the App still shows their questions.

From then on, teammates get a direct message in Slack when something waits for them or for you. There are six:

| Message | When |
| --- | --- |
| **Asked you** | A teammate asks you, or hands an ask on to you. It says whether the answer is needed before approval or opinion only, quotes the question and gives `/ql answer <ask>` for your own agent |
| **Reminds you** | The person who asked pressed **Remind** |
| **Answered you** | Someone answered your question. It quotes the answer and says which kind it was |
| **Your turn: every answer is in** | The last answer your approval waits for has come in. It goes to the task's owner |
| **Your turn: build finished** | The build of your task is done and now being checked |
| **Your turn: build stopped** | The build stopped and needs your decision |

Each message links to a page on qualitylayer.dev that tries to open the App at the right place. Without the App, the page offers **Open in this browser** or **Get the QualityLayer App**. On a phone it says to open the link on your computer and offers to copy it. No key ever passes through Slack.

![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress never notifies](pathname:///img/diagrams/attention-light.svg)
![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress never notifies](pathname:///img/diagrams/attention-dark.svg)

One rule holds for every channel: it speaks only when a person can act. Progress, checks and agents' own work never notify.

If the team service is busy for your computer, which happens at 600 requests an hour per licence, the card says so and until when. Questions and Slack messages wait until then. This limit belongs to QualityLayer's team service.

## People outside your team {#outside-links}

Under **Link for people outside the team**, **Copy link** shares the Plan as it is now. Anyone with the link can read it and comment under a name they type, without an account, and needs no seat. The link expires after 14 days; **Renew** shares the current Plan for another 14, and **Revoke** ends it at once.

The page uses the names of the steps: Discuss, Plan and Build. It shows the mockup and the diagrams, the slices and the contracts, and the questions you asked, with the same answers you offer in the App. Research is never shared.

**Outside reviewers comment only.** They have a name field ("No account needed"), their answers and comments, and one button that sends them to the person who shared, such as **Send to Max**. They cannot approve or ask for changes: approving is for your team, inside the App. Their comments reach you as an item under Needs you and in the Comments panel.

The link carries a key after the `#`, and your browser never sends that part to a server. The page opens the Plan with it, and a guest's comment is encrypted in the guest's browser before it is sent. A link without its key shows only the message "This link is missing its key".

## Groups

Groups split a team, so a shared task reaches only the people it concerns. Your team owner manages them in **Settings › Team › People and groups**: **New group**, a name, and the members to pick from the seats. **Select all** ticks every person shown, so a group of the whole team takes one click. A person can be in more than one group. Members see the groups read-only, with their own marked.

A task shared into a group is seen by that group, your team owner, the task's owner, and anyone asked on it. Everyone else sees neither the task nor its Plan; an old link to it says "This task isn't shared with you". In **Share**, the group picker chooses who sees it:

- With no groups set up, the whole team sees the task.
- In one group, that group is already picked.
- In several, you choose a group or **Whole team**. An ask on a task you haven't shared yet asks the same, and keeps what you wrote.

Asking someone outside the group lets them open that one task, and the ask says so before you send it. Deleting a group leaves its tasks hidden from everyone but their owners, your team owner and the people already asked, until you share a task again.

## What is shared, and who can read it

Sharing sends the Plan and its progress: the documents a reviewer reads with their mockups, the task's title and step, and the comments. It never sends your code, the diff or your logs.

Everything shared is encrypted on your machine before it leaves, so we can't read it. Only your team's computers, and people with a link, can open it. What stays readable to us is who shared a task, who was asked on it, an ID that tells tasks apart (never its title), when, and its step. The page behind a link loads its code from us; the Plan itself is opened in the guest's browser with the key in the link.

If you connect Slack, a message's task title and question pass through our server to Slack. When Slack is busy, they wait on our server for a retry, a day at most, and are deleted after that.

A new teammate needs no code, key or setup step: they install QualityLayer. One of your team's computers hands over the key the next time it checks in, normally within a minute. Until then, a shared task reads **Joining the team** and names who can let the computer in. Every new computer shows in **Settings › Team**, with your seats and members; seats are managed in the customer portal. When someone leaves the team, what you share from then on can't be read by their computer.

See [Files and privacy](../reference/files.md).
