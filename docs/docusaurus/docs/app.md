---
title: The QualityLayer App
description: How every step of the App is laid out, the five kinds of items you answer, how your answers reach your agent, and where to find things, on macOS, Windows and Linux.
---

The QualityLayer App is where you decide. Your agents keep doing the work in their own apps. The App never starts, pauses or stops an agent: every answer you give is a file the waiting agent reads.

It runs on macOS (Intel and Apple silicon), Windows and Linux desktops. On WSL2, in a dev container or on a server, `qualitylayer app` opens the same App in your browser.

## One layout for all five steps

![The App with numbered parts: the sidebar, the step tabs, the step line, the items that need you, the line of what agents checked, and the work](pathname:///img/diagrams/app-marked-light.svg)
![The App with numbered parts: the sidebar, the step tabs, the step line, the items that need you, the line of what agents checked, and the work](pathname:///img/diagrams/app-marked-dark.svg)

The App shows you only what needs a decision, your taste or your engineering judgement. Everything an agent can check folds into one line of proof that opens on demand. Every step has the same four layers, so you always know where to look.

| Part | What it does |
| --- | --- |
| **1** Sidebar | Your tasks in three groups: **Needs you** (with the open count and the step), **Running** and **Shipped** |
| **2** Step tabs | Where the task stands. A filled dot is done, a blue open ring means agents are working, an amber ring with a number means that many items wait for you |
| **3** Step line | Whose turn it is, in one sentence, and the one main action of the step you are looking at |
| **4** Needs you | Only the items that need a person. Each names its kind, shows the thing itself, and offers its two answers |
| **5** Checked by agents | One violet line with what the agents proved. The chevron opens the details and the evidence |
| **6** The work | The document, the live build or the diff. You can comment anywhere in it |

A finished step says what happened and links to where the task is now. A step not reached yet says in one sentence what will happen there.

## Items and their answers {#items}

![The five families of items: Decide, Look, Confirm, Fix and Answer, each with its answers and the kinds of item in it](pathname:///img/diagrams/items-light.svg)
![The five families of items: Decide, Look, Confirm, Fix and Answer, each with its answers and the kinds of item in it](pathname:///img/diagrams/items-dark.svg)

An item shows the thing itself, such as a screen, a diagram, a diff or a sentence, and the two answers of its family. A comment can go with any answer.

| Family | Your answers | Items in it |
| --- | --- | --- |
| **Decide** | Agree · Change | An engineering decision, with its diagram. What the agent decided for you. What is out of scope. Extra review. Done means. Is this what you asked for |
| **Look** | Looks right · Change, with a pin on the spot | The mockup. A diagram. A screen or picture of the result |
| **Confirm** | I confirm · Ask the agent to record it | **Only you can confirm**: something no agent may do, such as a call to a live service |
| **Fix** | Accept · Fix it | **Found while checking**. **Decided by the agent while building** has Fine · Ask why. **Add to the Plan** has Add · Skip it |
| **Answer** | In your agent, or Looks right · Suggest a change · Reply | The agent's question, answered in Claude Code or Codex. A teammate's question for you |

Change, Fix it and Ask the agent to record it send work back to the agent. The agent then checks only what that work touched.

## How your answers reach your agent {#answers}

| Where | What happens |
| --- | --- |
| **Discuss** | The agent asks in its own picker in Claude Code or Codex. The App shows the question, its recommendation and the choices, counts it under Needs you, and records your answer |
| **Plan and Review** | Your answers are collected on this computer. The main button sends them all: **Approve**, or **Send 1 change** (or 2, 3 …) when an answer asks for a change. Comments ride along as notes |
| **Implement** | Comments and **Ask why** go at once. The build reads them after each task. **Add to the Plan** holds only that slice; the rest keeps building |
| **A stop** | When a checkpoint fails twice, or checking stops after two tries, the App offers the choices. Your choice is a decision the waiting agent reads |

With no agent attached to a task, your answers wait, and the App shows the command that resumes it.

You can change an answer until it is sent. After you send it, the agent's reply appears on the item. If the agent later changes something you settled, the item opens again, marked **changed since your review**. If you already decided in your agent's window, the App says where and when, and keeps your unsent answers as comments.

## Order and counts

What blocks work comes first: a question, a stop, something only you can confirm. Then decisions, then things to look at, then choices you may question. Settled items fold into one line per step after you decide.

- A step tab counts the open items in that step.
- The sidebar counts open items per task.
- The **Team** switch counts questions for you.

An item the agent changes while you read it shows **updated** and keeps your unsent answer.

## Comments

Select any passage, line or diagram part, or press **+** beside a block, and write a comment. The agent answers in the thread and says what it changed. **Ask Anna about this** passes the question on to a teammate.

On Plan and Review, **Comments** in the step line opens a panel with three lists: your drafts, which go out with your decision; threads the agent has answered; and what your team said. Each links back to its place.

## Keyboard

| Keys | What they do |
| --- | --- |
| **↑** **↓** | Move between items |
| **Enter** | Pick the first answer |
| **⌘↵** | Run the step's main button |
| **⌘K** | Jump to a task or a setting |
| **Esc** | Close a sheet |

## Home and ⌘K

**Home** gathers the items of all your tasks, grouped by task. Quick ones, such as confirm, accept and fix, you answer on the spot. Items that need a look say **Open** and take you to that item. Below sit questions from teammates, **Running** with one live line per task, and what shipped this week with its cost. When nothing needs you, Home says so and keeps Running.

**⌘K** opens a command box. It finds tasks by name or content, jumps to a setting and filters the list by need, agent or project. **Send feedback** is in it too.

The App opens where you left it: the same task, step and scroll position.

## Where things are

| Where | What is there |
| --- | --- |
| Sidebar foot | **Settings**, **Docs** and the theme switch as icon buttons, and **Feedback**. Your name and your licence ("Team licence", "Trial · 7 days left") sit above them |
| Task header | The title, the project, the agent and the branch. **Cost**, **Share** and **More** (Archive, Delete, copy the plan folder's path or the task's id) |
| **Update ready** line | Above your name when an update waits. See [Updates](updating.md) |
| Top of Home | One red line when the App cannot reach QualityLayer on this computer. It tries again every few seconds |

A task whose agent has been quiet for over ten minutes turns amber and says its session may have closed. It offers the exact command that resumes it, such as `/ql implement <task>` (`$ql` in Codex).

## Close it any time

Closing the window keeps the App in the menu bar or the tray until you choose **Quit**. Your agents keep working either way: with the App closed, quit or never opened, Claude Code and Codex carry a task on. Open it again and it shows exactly where each task stands.

Links your agent prints open the App at the right place. Without the App installed, they open the page in your browser.

## Notifications

The App speaks only when a person can act. That means a Plan or a review waits, a task stops or ships, a teammate asks you, a reminder arrives, or someone answers your question. It never notifies for agent progress. A notification uses the step line's words, such as "Settings cleanup needs your review". This also holds while the window is closed.

The tray menu lists the same lines. If none arrive, allow QualityLayer in your system's notification settings. You can turn them off in [Settings](reference/settings.md#notifications).

## Approve in the App or in the chat

The main button records your decision. You can also type `approve` as your message in the agent session that runs the task, in Claude Code or Codex. QualityLayer's prompt hook records it and tells the agent; Codex asks you once to trust the hook. Your agent cannot approve for you: if it runs the approve command itself, QualityLayer refuses.

## What it costs

![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-light.svg)
![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-dark.svg)

**Cost** in a task's header opens the panel. It shows the total, each step's time, tokens and cost, and under each step the agents named after their work and model: "Polish · Sonnet 5.5", "Checking · part 1 of 3 · Opus 5.5", "Your session · Opus 5.5". Project checks show their time at $0. When one agent or a repeat dominates a step, a **Worth a look** line says so.

Figures are estimated at list price. Where no list price is published yet, as for some Codex models, the panel shows the tokens and "price unknown". The App reads them from your agents' own logs on your computer; nothing is sent anywhere.

## In Claude Code

With Claude Code 2.1.287 or later, the installer adds a small QualityLayer add-on. It draws a slim band above your prompt while a task or a question for you is live.

![The band above the Claude Code prompt: the Plan needs you, how the build runs, or teammates' questions for you](pathname:///img/diagrams/band-light.svg)
![The band above the Claude Code prompt: the Plan needs you, how the build runs, or teammates' questions for you](pathname:///img/diagrams/band-dark.svg)

`/ql-app` opens the App at the task, and `/ql-pane` opens a pane with the steps and the build's progress. The add-on only shows; it never approves or changes anything. QualityLayer sets no status line, so yours stays as it is. In Codex, and where Claude Code draws no add-ons, your agent's own messages carry the links.

## Copy a document out

Every document has a **Copy** menu. **Copy formatted** pastes into Confluence, Google Docs, Notion or Word with headings, tables, code, diagrams and mockups as pictures. **Copy as Markdown** pastes into Jira, GitHub or Linear. The Discuss document also copies as a PRD. **For another agent** copies the prompt that connects an agent QualityLayer does not know; see [How to connect another coding agent](agents/other.md).

## Narrow windows and themes

Below 900 pixels the sidebar becomes a **Menu** button, the step tabs scroll and items stack. The App follows your system's light or dark mode until you choose one with the theme icon.

## What it costs your machine

The local server behind the App runs while you use it. After you quit the App, it stops by itself 30 idle minutes later. Waiting for your approval costs your agent's session under 0.5 % of one processor core. Linking Claude Code and Codex sessions costs under 1 %, for as long as the link is on.
