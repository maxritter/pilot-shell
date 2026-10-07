---
title: The App
description: Where you answer, read and comment while your agent works. One page per step, one layout for all five.
---

The QualityLayer App shows one focused question or decision in **Your turn**, with the context you need to answer. Your agent keeps working on anything that does not depend on your answer. Open the step's document to read, comment on its diagrams and designs, and follow the build and its proof. Close the App any time; your agents keep working.

It runs on macOS, Windows and Linux. Without a screen, `qualitylayer app` opens it in your browser.

## One page for every step

| Part | What it does |
| --- | --- |
| Sidebar | Your tasks under **Your turn**, **Running** and **Shipped**. **+ New** starts a task |
| Live status | What the agent is working on, when it needs you, and whether it is quiet or stopped. Open it for details |
| Step track in the top bar | Where the task stands in Discuss, Plan, Implement, Verify and Review |
| Now | **Your turn** when a decision waits for you; the agent's progress while it works |
| Your turn | One focused question or decision, followed by agreements and approvals |
| Document | The step's page, with your answers, the build and its proof |
| Right sidebar | **Files** and **Comments**; compact designs are listed in **Files** |

The file chip in the document header names the step's document. Its menu copies the path, opens the file in your editor, reveals it in the Finder, or opens the task folder. It also opens the agent's version and records in a read-only reader.

## Answering questions {#questions}

Independent questions can arrive together, and the card shows one question at a time. Answer in any order: use **Skip for now** to reach another question, then return to the skipped one. Each question has choices and a marked recommendation. **Your own answer** stays visible; type your words and press **Send**. **Tell me more** asks for the context you need before deciding.

Each answer goes to the agent at once and appears in the folded **Decided with you** history. The item leaves **Your turn**, and the card, sidebar and notification counts update together. **Change** corrects an earlier answer. If the agent has stopped, your answer stays saved for when it continues.

The agent keeps working on independent parts of the task while questions remain open. Answering a batch does not approve the Plan or the finished change; each approval remains your own action.

With the question card focused, **1–9** chooses the matching answer, **Enter** or **R** takes the recommendation, **M** opens Tell me more, and **↑/↓** moves between questions. **Tab** from the card opens your own answer. In the answer field, **Enter** sends and **Shift+Enter** adds a line. Choice shortcuts leave typing fields, links, menus and dialogs alone; **⌘**, **Ctrl**, **Alt** and text composition do not submit a choice.

## Agreements and live status

Agree to each **Done means** point separately. If its words change, you see the old and new wording and agree again to that point. Unchanged points keep your agreement.

The top bar names the agent and shows whether it is working, waiting for you, quiet or stopped. Open **Agent status** for its current work, other active agents and, when it has stopped, the command to continue. Answers and comments stay saved.

## Full-size reading

Discuss and Plan offer the complete document in reading order. The App opens full reading before Plan approval and when you return to a completed Discuss. Open **Document full size** to give it more room, use the outline to jump between sections, and comment as you read. Long decision lists fold without removing their contents from the file. The document menu opens the agent's version and records with a way back to the human document.

Implement shows **Build**: the slices, changes and checks as they happen. Its generated document is available from **Files**. See [Implement](steps/implement.md).

## Home

Home brings together what needs your answer, what your agents are working on, and what shipped. Shipped tasks show their time and estimated cost when those records are available.

The notification bell keeps questions, comments and stopped tasks within reach. Its count updates as you answer. Home also shows how many tasks are in each step.

![Home with Your turn, agents at work, shipped tasks with time and estimated cost, counts in each step and notifications](pathname:///img/diagrams/home-light.svg)
![Home with Your turn, agents at work, shipped tasks with time and estimated cost, counts in each step and notifications](pathname:///img/diagrams/home-dark.svg)

## Items and their answers {#items}

![The five families of items: Decide, Look, Confirm, Fix and Answer, each with its answers and the kinds of item in it](pathname:///img/diagrams/items-light.svg)
![The five families of items: Decide, Look, Confirm, Fix and Answer, each with its answers and the kinds of item in it](pathname:///img/diagrams/items-dark.svg)

Every item has short answers, such as **Agree** or **Change**, **Looks right**, **I confirm**, or **Fix it**.

## Comments

Select any passage, line or part of a diagram and write a comment; it shows in the **Comments** tab. Your agent answers in the thread and says what it changed. **Ask Anna about this** passes the question to a teammate.

## Designs

Ask your agent to draw a page and it appears as a compact entry in **Files**. Open it full size and comment on a spot. See [Designs](designs.md).

## What it costs {#cost}

![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-light.svg)
![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-dark.svg)

The dollar amount in a task's header opens its cost: the total, each step's time, tokens and cost, and the agents that did the work. Estimates use list prices and your agents' logs on this computer. Tokens with no known price appear as muted **tokens unpriced** detail; they are not added to the dollar total. Nothing is sent anywhere.

## In Claude Code

A slim band above your prompt says when something waits for you in the App. `/task-pane` opens a pane with the steps and the build's progress.

![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-light.svg)
![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-dark.svg)

## Handy to know

- **⌘K** finds a task or a setting.
- **Copy** on any document pastes it into Confluence, Notion, Jira or GitHub.
- The App notifies you only when you can act: a question or a review waits, a task stops or ships, or a teammate asks you.
