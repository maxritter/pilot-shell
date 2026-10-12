---
title: The App
description: Where you answer, read and comment while your agent works. One page for every step.
---

The QualityLayer App is where you answer, read and comment while your agent works. Close it any time; your agents keep working. It runs on macOS, Windows and Linux, and without a screen `qualitylayer app` opens it in your browser.

![The App at Discuss: your tasks on the left, the step track across the top, one question in Your turn with its choices and a field for your own answer, the Discuss document below, and Files and Comments on the right](pathname:///img/app/discuss-light.webp)
![The App at Discuss: your tasks on the left, the step track across the top, one question in Your turn with its choices and a field for your own answer, the Discuss document below, and Files and Comments on the right](pathname:///img/app/discuss-dark.webp)

*Example task in a fictional project.*

| Part | What it does |
| --- | --- |
| **Sidebar** | Your tasks: what needs you, what runs, what shipped. **+ New** starts one |
| **Agent status** | The chip in the top bar: what the agent does now, whether it needs you, is quiet or has stopped |
| **Step track** | Where the task stands. A person icon marks the two steps you approve |
| **Your turn** | One question or decision, when your judgement is needed |
| **Step page** | The step's document as the parts that matter now |
| **Right sidebar** | **Files** (documents, designs, reviews, records) and **Comments** |

## Answering questions {#questions}

Independent questions come as a batch. **Your turn** shows one question at a time, with a strip listing the whole batch. Each answer reaches your agent immediately, and your agent keeps working on whatever does not depend on it.

| Control | What it does |
| --- | --- |
| A choice | Answers. The recommended one is marked; **From Research** opens the finding behind it |
| **Your own answer** | Type your words and press **Send** |
| **Tell me more** | Asks for the context you need first |
| **Skip for now** | Moves on, so you can answer in any order |
| **Use the recommendations for all N** | Answers the rest of the batch |
| **Change** | Corrects an earlier answer, from **Decided with you** |

Answering never approves the Plan or the change; each approval is its own click. Questions come only in Discuss and Research. A choice that appears only once a design is drawn sits in the Plan as a **Your call**, at most two per task.

<details>
<summary>Keyboard shortcuts</summary>

With the question card focused:

| Key | What it does |
| --- | --- |
| **1–9** | Choose the matching answer |
| **Enter** or **R** | Take the recommendation |
| **M** | Open Tell me more |
| **↑ / ↓** | Move between questions |
| **Tab** | Open your own answer |

In the answer field, **Enter** sends and **Shift+Enter** adds a line.

</details>

## Reading a document {#documents}

Every step writes one Markdown file. The App shows it three ways:

| View | What it shows |
| --- | --- |
| **Step page** | The parts that matter now, in plain words: **Done means**, decisions with diagrams, slices, checks. **More in this document** names what it leaves out |
| **Reader** | The whole file in order, with **On this page**. Code shapes, paths and commands live here |
| **Files** | The seven documents with their state, the designs, the reviews, and the records of every command and check |

A document can appear before its step: `02-research.md` while you answer Discuss. `04-outline.md` appears once the build session you start after approving the Plan writes it. The file chip in the header copies the path, opens the file in your editor or shows it in its folder. **Copy document** pastes it into Confluence, Notion, Jira or GitHub.

## Comments and designs

Select a passage, a line or part of a diagram and comment. Your agent answers in the thread and says what it changed; **Ask…** passes the question to a teammate. Pages your agent draws appear in **Files**; open one full size and comment on a spot ([Designs](designs.md)).

## Home

![Home: Needs attention with a row for each task that waits, Spent on agents with the estimated cost, and Shipped](pathname:///img/app/home-light.webp)
![Home: Needs attention with a row for each task that waits, Spent on agents with the estimated cost, and Shipped](pathname:///img/app/home-dark.webp)

Four areas: **Needs attention**, **Running**, **Spent on agents** and **Shipped**. Each row in **Needs attention** opens the task where you answer or review; with a team it also lists what teammates wait on you for. The bell and the counts show the same number. The App notifies you only when you can act.

## What it costs {#cost}

![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-light.svg)
![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-dark.svg)

The dollar amount in a task's header opens its cost per step and per agent. It is an estimate from list prices and your agents' logs on this computer; nothing is sent anywhere. Tokens without a known price show as **tokens unpriced** and stay out of the total.

## In Claude Code

A slim band above your prompt says when something waits for you in the App. `/task-pane` opens a pane with the steps and the build's progress.

![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-light.svg)
![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-dark.svg)

**⌘K** finds a task or a setting.
