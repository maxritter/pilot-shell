---
title: The App
description: Where you answer, read and comment while your agent works. One page for every step.
---

The App is where you answer questions, read documents and comment while your agent works. It runs on macOS, Windows and Linux; without a screen, `qualitylayer app` opens it in your browser.

![The App at Discuss: your tasks grouped by project on the left, the step track across the top, one question in Your turn with its choices and a field for your own answer, the Discuss document below, and Files and Comments on the right](pathname:///img/app/discuss-light.webp)
![The App at Discuss: your tasks grouped by project on the left, the step track across the top, one question in Your turn with its choices and a field for your own answer, the Discuss document below, and Files and Comments on the right](pathname:///img/app/discuss-dark.webp)

*Example task in a fictional project.*

| Part | What it does |
| --- | --- |
| **Sidebar** | Home, Team, Designs and your tasks by project. **+ New** starts a task |
| **Agent status** | The top-bar chip: working, needs you, quiet or stopped |
| **Step track** | Where the task stands. A person icon marks the two steps you approve |
| **Your turn** | One question or decision that needs you |
| **Step page** | The parts of the step's document that matter now |
| **Right sidebar** | **Files** and **Comments** |

## The sidebar {#sidebar}

Tasks sit under their project (a repository on this computer), the ones waiting on you first. A project appears when you start a task in it; the folder button adds one by hand.

| To | Do |
| --- | --- |
| Fold a project | Click its header or press **←**. Folded, it still shows what waits on you |
| Reorder projects | Drag a header, or **⌥↑** / **⌥↓** |
| Rename, recolor or hide a project | The project menu (**⋯** or right-click) |
| Start a task in a project | **+** on its header |
| Rename, archive or delete a task | Right-click it |
| Filter or regroup | **View** (sliders button) or **Find** (search button). **⌘K** searches everything |

Order, colors, names and hidden projects are stored on the computer that runs the App, so every paired browser shows the same list.

### The places {#places}

| Place | What it shows |
| --- | --- |
| **Home** | What needs you, what runs, the cost and what shipped ([Home](#home)) |
| **Team** | With a Team plan: questions teammates wait on you for, and tasks they shared |
| **Designs** | Every project's lasting designs and the drafts in open tasks ([Designs](designs.md#designs-place)) |

## Answering questions {#questions}

Questions come in Discuss and Research. Independent questions arrive as a batch, and **Your turn** shows one question at a time. Each answer reaches your agent at once.

| Control | Key | What it does |
| --- | --- | --- |
| A choice | **1–9** | Answers. The recommended one is marked (**Enter** or **R** takes it) |
| **Your own answer** | **Tab** | Type and press **Send** |
| **Tell me more** | **M** | Asks for more context first |
| **Skip for now** | | Moves on, so you can answer in any order |
| **Use the recommendations for all N** | | Answers the rest of the batch |
| **Change** | | Corrects an earlier answer, under **Decided with you** |

**↑** / **↓** move between questions. Answering never approves anything. Approving the Plan and the change are separate clicks.

## Reading a document {#documents}

Every step writes one Markdown file, shown three ways:

| View | What it shows |
| --- | --- |
| **Step page** | What matters now: **Done means**, decisions with diagrams, slices, checks |
| **Reader** | The whole file, with code shapes, paths and commands |
| **Files** | All seven documents, designs, reviews and command records |

**Copy document** pastes a document into Confluence, Notion, Jira or GitHub.

## Comments and designs

Select a passage, a line or part of a diagram to comment. Your agent answers in the thread and says what it changed. **Ask…** sends the question to a teammate. Designs have their own page: [Designs](designs.md).

## Home {#home}

![Home: Needs attention with a row for each task that waits, Spent on agents with the estimated cost, and Shipped](pathname:///img/app/home-light.webp)
![Home: Needs attention with a row for each task that waits, Spent on agents with the estimated cost, and Shipped](pathname:///img/app/home-dark.webp)

**Needs attention**, **Running**, **Spent on agents** and **Shipped**. The App notifies you only when you can act:

![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress and checks never notify](pathname:///img/diagrams/attention-light.svg)
![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress and checks never notify](pathname:///img/diagrams/attention-dark.svg)

## What it costs {#cost}

![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-light.svg)
![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-dark.svg)

The dollar amount in a task's header opens the cost per step and agent, estimated from list prices and your agents' local logs. Nothing is sent anywhere.

## Agent runs {#agent-runs}

**+ New**, **Start the build** and **Draft with my agent** run the agent **Here in the App** or **In my terminal**. In the App, the agent's own program opens in a window with its usual keys and prompts. On Windows, use your terminal.

![Start the build: Build myself or Hand to the team, the agent tabs, the branch it lands on, permissions, and Here in the App or In my terminal above the Start the build button](pathname:///img/app/implement-start-light.webp)
![Start the build: Build myself or Hand to the team, the agent tabs, the branch it lands on, permissions, and Here in the App or In my terminal above the Start the build button](pathname:///img/app/implement-start-dark.webp)

| To | Do |
| --- | --- |
| Keep working elsewhere | Fold the window into the dock; the run continues |
| Type from another window | **Take control**. One window types at a time |
| Interrupt the agent | **Interrupt** (usually sends Esc) |
| End the run | **Stop**. A failed cleanup stays visible |
| Continue a stopped run | **Resume here** or **Open the session** |
| Move to your terminal | **Move to my terminal** gives the resume command |

Defaults live in Settings › Workflow › **Where agents run**:

| Setting | Choices |
| --- | --- |
| **Permissions** | **Your agent's own settings**; **Fewer prompts** (Claude Code's auto mode or Codex's reviewer, which may not refuse every risky request); **Bypass prompts** (no approvals or sandbox, confirmed at every start) |
| **Works in** | The checkout. **Lands on** shows the branch or creates a new one |
| **Typing and starting agents** | Whether other paired browsers may start runs and type |
| **When you quit the App** | **Agents keep running** or **Stop agents**. Closing a window never stops work |

For **Another agent**, set its program path and arguments in Settings; Interrupt, Restart, Move and Resume are not available. Terminal output stays on this computer and is never shared.

## In Claude Code

A band above your prompt says when something waits for you in the App. `/task-pane` opens a pane with the steps and the build's progress.

![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-light.svg)
![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-dark.svg)
