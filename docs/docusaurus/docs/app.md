---
title: The App
description: Read the work, answer questions and give feedback beside your agent’s conversation.
---

The App is where you answer questions, read documents and give feedback while your agent works. It runs on macOS, Windows and Linux; without a screen, `qualitylayer app` opens it in your browser.

![Discuss with a question, document and sidebar in an earlier App layout](pathname:///img/app/discuss-light.webp)
![Discuss with a question, document and sidebar in an earlier App layout](pathname:///img/app/discuss-dark.webp)

*Example task in a fictional project; the illustration shows an earlier layout. Current controls are described below.*

| Part | What it does |
| --- | --- |
| **Sidebar** | Home, Team, Designs and your tasks by project. **+ New** starts a task |
| **Agent status** | The top-bar chip: working, needs you, quiet or stopped |
| **Step track** | Where the task stands. A person icon marks the two steps you approve |
| **Your turn** | One question or decision that needs you |
| **Step page** | The parts of the step's document that matter now |
| **Right sidebar** | **Files**, **Feedback** and the task’s **Agent** conversation |

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
| **Home** | Your own **Needs you** queue and **Running** work ([Home](#home)) |
| **Team** | **My attention**, **Everyone** and **My questions** for shared work |
| **Designs** | A compact **Library** grouped by project, with **Archived** and recovery ([Designs](designs.md#designs-place)) |

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

## Feedback and designs {#comments-and-designs}

Select a passage, a line or part of a diagram and choose **Give feedback**. The thread keeps that context with your words. Choose **To agent**, ask a teammate a question, or address feedback to a person. Person-only feedback is not sent to the agent.

Working designs are compact entries in **Files**. **Open design canvas** opens the full page, its Feedback and its base design. The document header opens Files and Feedback; **Agent** opens the task’s conversation. The **Agent status** chip shows current activity. See [Designs](designs.md).

## Home {#home}

![Home: a Needs you section for your own questions and approvals, followed by a separate Running section for your agents' work](pathname:///img/app/home-light.webp)
![Home: a Needs you section for your own questions and approvals, followed by a separate Running section for your agents' work](pathname:///img/app/home-dark.webp)

**Needs you** is your move: questions, approvals and tasks you can continue. **Running** is your agents' work, with its current step and activity. A row opens the exact task or document. Teammate questions and answers belong to Team.

Notifications are configured in **Settings › Workflow**. Home shows no spending or shipped summary. The App notifies you only when you can act:

![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress and checks never notify](pathname:///img/diagrams/attention-light.svg)
![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress and checks never notify](pathname:///img/diagrams/attention-dark.svg)

## What it costs {#cost}

![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-light.svg)
![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-dark.svg)

The **Cost** control in a task's header opens the cost per step and agent, estimated from list prices and your agents' local logs. Dollar amounts stay hidden until you open it. Unpriced usage shows **tokens unpriced**, so an unknown price is never shown as free. Nothing is sent anywhere.

## Agent runs {#agent-runs}

**New task** and **Start the build** let you choose an installed agent, model, effort and workspace. **In the App** opens its conversation in the task’s **Agent** tab. **In my terminal** gives you the launch command.

The App checks the local runtime before starting. If it cannot start the selected agent here, it explains why and keeps the terminal option available. Permissions and sign-in prompts still belong to your agent.

| To | Do |
| --- | --- |
| Read the task beside the conversation | Open **Agent** in the right sidebar; drag the divider to resize it |
| Keep working elsewhere | Close the sidebar or open another task; this does not stop the run |
| Type from another window | Use **Take control**; one window types at a time |
| Interrupt or end the run | Use **Interrupt** or **Stop** in the agent menu |
| Return to a saved conversation | Use its available **Resume** or **Open the conversation** action |
| Move to your terminal | **Move to my terminal** gives the supported resume command |

**Settings → Workflow → Agents** controls where agents run by default, appearance, other paired browsers and quitting the App. Choose models, effort and workspace when starting a run. See [Settings](reference/settings.md#defaults).

An agent can wait for a permission, sign-in, answer or approval. A visible running process is not proof that it is making progress; read its current status and conversation. **Stop** and a user pause remain boundaries.

Other coding agents use the copied terminal prompt. Terminal output stays local and is not included in shared tasks.

## In Claude Code

A band above your prompt says when something waits for you in the App. `/task-pane` opens a pane with the steps and the build's progress.

![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-light.svg)
![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-dark.svg)
