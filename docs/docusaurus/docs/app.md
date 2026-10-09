---
title: The App
description: Where you answer, read and comment while your agent works. One page per step, one layout for all seven.
---

The QualityLayer App shows one focused question or decision in **Your turn**, with the context you need to answer. Your agent keeps working on anything that does not depend on your answer. Open the step's document to read, comment on its diagrams and designs, and follow the build and its proof. Close the App any time; your agents keep working.

It runs on macOS, Windows and Linux. Without a screen, `qualitylayer app` opens it in your browser.

## One page for every step

| Part | What it does |
| --- | --- |
| Sidebar | Your tasks under **Your turn**, **Running** and **Shipped**. **+ New** starts a task |
| Live status | What the agent is working on, when it needs you, and whether it is quiet or stopped. Open it for details |
| Step track in the top bar | Where the task stands in its seven steps: Discuss, Research, Plan, Outline, Implement, Verify and Review. A person icon marks the two where you approve |
| Your turn | One focused question or decision when your judgement is needed |
| Step page | The step's document, as the parts that matter now, with your answers, the build and its proof |
| Right sidebar | **Files** and **Comments**; compact designs are listed in **Files** |

The file chip in the document header names the step's document. Its menu copies the path, opens the file in your editor, reveals it in the Finder, or opens the task folder.

Tasks you started before the seven steps keep the five they began with; the App draws the steps a task has.

## Three views of one document {#documents}

Every step writes one Markdown file, and the App shows it three ways:

| View | What it shows |
| --- | --- |
| **Step page** | The sections that matter now, drawn as parts: the **Done means** list, decisions with their diagrams, the slice list, the checks. Beside them, the live cards: a batch of questions, a **Your call**, the start card, an approval. A strip, **More in this document**, names the sections the page leaves out |
| **Reader** | The whole file, every section in order, with an **On this page** outline. Sections that the step page leaves out are dimmed and tagged. Reach a section from the strip, the outline or any **Read the…** link |
| **Files** | **Documents:** the seven files as one list, each with its state: not yet, started early, being written, your turn or done. **Designs.** **Reviews** the other agents wrote, only those that ran. **Records:** the output of every command and the evidence the checks kept |

A document is listed before its step arrives when it is being written early: `02-research.md` while Discuss's batch is open, and `04-outline.md` while you read the Plan. The reader is where code shapes, file paths and commands live; the step page stays in plain words.

## Answering questions {#questions}

Independent questions can arrive together, and the card shows one question at a time. Answer in any order: use **Skip for now** to reach another question, then return to the skipped one. Each question has choices and a marked recommendation. A strip above the card lists the whole batch, with answered questions ticked and still changeable. Where the choices need facts, they sit in columns side by side, with a **From Research** link to the finding they rest on. **Your own answer** stays visible; type your words and press **Send**. **Tell me more** asks for the context you need before deciding. **Use the recommendations for all N** answers the rest of the batch at once.

Each answer goes to the agent at once and appears in the folded **Decided with you** history. The item leaves **Your turn**, and the card, sidebar and notification counts update together. **Change** corrects an earlier answer. If the agent has stopped, your answer stays saved for when it continues.

The agent keeps working on independent parts of the task while questions remain open. Answering a batch does not approve the Plan or the finished change; each approval remains your own action. Questions come in batches only in Discuss and Research. The Plan asks none: a choice that only appears once a design is drawn sits inside it as **Your call**, at most two per task.

With the question card focused, **1–9** chooses the matching answer, **Enter** or **R** takes the recommendation, **M** opens Tell me more, and **↑/↓** moves between questions. **Tab** from the card opens your own answer. In the answer field, **Enter** sends and **Shift+Enter** adds a line. Choice shortcuts leave typing fields, links, menus and dialogs alone; **⌘**, **Ctrl**, **Alt** and text composition do not submit a choice.

## Agreements and live status

**Done means** is proposed document content in Discuss, and the Plan carries it. Comment on anything that needs correcting; the complete Plan approval covers the criteria together. Only explicitly asked choices need separate answers. Technical reviewer findings go to your planning agent to fix or answer.

The top bar keeps the agent's name stable while work changes. Open its chip for current work, process signals, the agents running now and the history of those that finished, or use **Agent status** in the task menu on narrow screens. Cost details remain accessible there. Ordinary activity stays out of the document body; stopped recovery, build slices and recorded checks stay available. Escape or an outside click closes the activity panel.

## Full-size reading

Every step's document opens in the reader, in reading order. While an actual choice needs your answer, its focused card can open the document context. After those choices close, the complete Plan appears with **Approve Plan** and **Give feedback** at the top right. Open **Document full size** to give it more room, use the outline to jump between sections, and comment as you read.

Implement shows **Build**: the slices, changes and checks as they happen. Its written record, `05-implement.md`, is available from **Files**. See [Implement](steps/implement.md).

## Home

Home has four areas: **Needs attention**, **Running**, **Spent on agents**, and **Shipped**. Each attention row opens the task where you can answer or review. Shipped tasks show their time and estimated cost when those records are available.

The notification bell keeps questions, comments and stopped tasks within reach. Its count updates as you answer. Spending shows known dollar estimates; expand **About the estimate** for unpriced usage and calculation details.

![Home with compact task destinations under Needs attention and Running, alongside spending and Shipped](pathname:///img/diagrams/home-light.svg)
![Home with compact task destinations under Needs attention and Running, alongside spending and Shipped](pathname:///img/diagrams/home-dark.svg)

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
