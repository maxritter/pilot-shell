---
title: The QualityLayer App
description: Where you read your agent's documents, comment, approve, follow the build and see what each step costs, on macOS, Windows and Linux.
---

The QualityLayer App is where you review and approve. Your agents keep doing the work in their own apps. The App never starts, stops or steers an agent.

It runs on macOS (Intel and Apple silicon), Windows and Linux desktops. On WSL2, in a dev container or on a server, `qualitylayer app` opens the same App in your browser.

![The App with numbered parts: the task list, the five steps, the review bar, a diagram, a comment and a clickable mockup](pathname:///img/diagrams/app-marked-light.svg)
![The App with numbered parts: the task list, the five steps, the review bar, a diagram, a comment and a clickable mockup](pathname:///img/diagrams/app-marked-dark.svg)

| Part | What it does |
| --- | --- |
| **1** Task list | Tasks by who acts next: **Needs you**, **In progress**, **Shipped**. Filter by project or agent, or search |
| **2** The five steps | Where the task stands; steps not reached yet stay greyed out |
| **3** Review bar | Who acts next, and **Request changes** or **Approve** |
| **4** Diagrams | Pictures of the system; open them full screen |
| **5** Comments | Select any line or press **+** beside a block; your comments go to your agent together |
| **6** Mockups | Clickable, with their empty, loading and error states, running sandboxed |

Each document has a short version **For you** and a detailed one **For the agent**; the switch sits in the review bar. **Show me** collects the pictures your agent made for the task, and **Share** lets your [team](team/plans.md) in.

## Close it any time

Closing the window keeps the App in the menu bar or the tray until you choose **Quit**. Your agents keep working either way: with the App closed, quit or never opened, Claude Code and Codex carry a task on. Open it again and it shows exactly where each task stands.

Links your agent prints open the App at the right place. Without the App installed, they open the page in your browser.

## Notifications

The App tells you when the Plan or the finished change waits for you and when a teammate asks you something, also while its window is closed. A finished or stopped task is announced too, and everything collects under the bell. If none arrive, allow QualityLayer in your system's notification settings; you can turn them off in [Settings](reference/settings.md#notifications).

## Approve in the App or in the chat

**Approve** in the review bar records your decision. You can also type `approve` as your message in the agent session that runs the task, in Claude Code or Codex. QualityLayer's prompt hook records it and tells the agent; Codex asks you once to trust the hook. Your agent cannot approve for you: if it runs the approve command itself, QualityLayer refuses.

## Follow the build

**Implement**, **Verify** and **Review** form one timeline: what is running now, each slice with its tasks, each checkpoint with its runs, Polish and Security, and every judge round with its evidence. Several helpers at work show side by side. You can comment at any time; your agent reads it at its next step. See [Implement](steps/implement.md) and [Verify](steps/verify.md).

## What it costs

![The cost view: tokens and estimated cost at list price for each step and each helper](pathname:///img/diagrams/cost-light.svg)
![The cost view: tokens and estimated cost at list price for each step and each helper](pathname:///img/diagrams/cost-dark.svg)

The **Cost** button in a task's header opens the cost panel: the tokens and the estimated cost per step, per helper and in total, marked "estimated, list price". Where no list price is published yet, as for some Codex models, it shows the tokens and "price unknown". The App reads these numbers from your agents' own logs on your computer; nothing is sent anywhere.

## In Claude Code

With Claude Code 2.1.287 or later, the installer adds a small QualityLayer add-on. It draws a slim band above your prompt while a task or a question for you is live.

![The band above the Claude Code prompt: the Plan waits for you, how the build runs, or a teammate's question for you](pathname:///img/diagrams/band-light.svg)
![The band above the Claude Code prompt: the Plan waits for you, how the build runs, or a teammate's question for you](pathname:///img/diagrams/band-dark.svg)

`/ql-app` opens the App at the task, and `/ql-pane` opens a pane with the steps and the build's progress. The add-on only shows; it never approves or changes anything. QualityLayer sets no status line, so yours stays as it is. In Codex, and where Claude Code draws no add-ons, your agent's own messages carry the links.

## Copy a document out

Every document has a **Copy** menu. **Copy formatted** pastes into Confluence, Google Docs, Notion or Word with headings, tables, code, diagrams and mockups as pictures. **Copy as Markdown** pastes into Jira, GitHub or Linear. The Discuss document also copies as a PRD. People outside QualityLayer then read it where they already work.

## Keep it tidy

**Archive** takes a task off the list; **Restore** brings it back. **Delete** removes an archived task and its files, after asking once more. The App follows your system's light or dark mode until you pick one, and remembers your filters.

## What it costs your machine

The local server behind the App runs while you use it. After you quit the App, it stops by itself 30 idle minutes later. Waiting for your approval costs your agent's session under 0.5 % of one processor core. Linking Claude Code and Codex sessions costs under 1 %, for as long as the link is on.
