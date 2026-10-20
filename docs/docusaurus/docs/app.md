---
title: The App
description: Read the work, answer questions and give feedback beside your agent’s conversation.
---

Read the task on the left and work with your agent in the right sidebar. Answer questions, inspect diagrams and give feedback beside its conversation. Use the desktop App on macOS, Windows or Linux, or run `qualitylayer app` to open the same workspace in your browser.

![A visual billing Plan explains retries, buffering and replay beside Claude Code messages and tool calls in QualityLayer's Conversation view](pathname:///img/app/plan-light.webp)
![A visual billing Plan explains retries, buffering and replay beside Claude Code messages and tool calls in QualityLayer's Conversation view](pathname:///img/app/plan-dark.webp)

*Example task in a fictional project.*

| Part | What it does |
| --- | --- |
| **Sidebar** | Home, Team, Artifacts and your tasks by project. **+ New** starts a task |
| **Agent status** | The top-bar chip: working, needs you, quiet or stopped |
| **Step track** | Where the task stands. A person icon marks the two steps you approve |
| **Your turn** | One question or decision that needs you |
| **Step page** | What needs you, what to look at, then the part of the step's document that matters now ([how it is built](#step-pages)) |
| **Right sidebar** | the task’s **Agent** conversation, **Files** and **Feedback** |

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
| **Home** | **Needs you** for your tasks and teammate requests, plus your agents' **Running** work ([Home](#home)) |
| **Team** | **My attention**, **Everyone** and **My questions** for shared work |
| **Artifacts** | A compact **Library** grouped by project, with **Archived** and recovery ([Artifacts](artifacts.md#artifacts-place)) |

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
| **Files** | All seven documents, artifacts, reviews and command records |

**Copy document** pastes a document into Confluence, Notion, Jira or GitHub.

### The step page {#step-pages}

Every step page reads top to bottom in the same way:

| Part | What it shows |
| --- | --- |
| **What needs you** | Only your own cards: a batch of questions, a **Your call**, the approval, a confirmation. A step with nothing for you leaves it out |
| **Look here** | Up to three lines, one for each kind of thing: failures first, then what only you can confirm, then what the agent marked risky or unsure. Each names its first item and how many there are, and jumps to it |
| **The gist** | The step as a takeaway for this task, who writes or runs it and when, a short summary and up to five counts |
| **The core** | The part that is the step, as rows you can open: the numbered **Done means** in Discuss, the findings in Research, the artifacts and decisions in the Plan, the build map in the Outline, the board in Implement, the checked points in Verify, the walkthrough in Review |
| **Collapsed sections** | The other sections the step leads with, one line each: heading, count and takeaway. Open one in place |
| **More in this document** | Links to the working sections, which open in the Reader |

The sections come in the order of the file, so the page, the Reader and GitHub tell the same story. Review is the exception: its file keeps the order of the pull request description, and its page draws the walkthrough. An artifact, a wireframe, a diagram or a screen is always shown where it stands, never collapsed. The engineering and product levels show the same page and collapse the same sections; they differ in words and in how far a row opens ([two levels](intro.md#two-levels)). A step you have not reached shows one quiet line, a finished step keeps its page without the part for you, and a closed task or a link shows it read-only.

The page is laid out for the column beside an open **Agent** sidebar, so each part is one column that stays readable on a laptop screen.

## Feedback and artifacts {#comments-and-artifacts}

Select a passage, a line or part of a diagram and choose **Give feedback**. The thread keeps that context with your words. The **To** picker chooses the agent, a named teammate or **Everyone on the task** when access is known. Each recipient keeps its own draft. Person-only feedback is not sent to the agent.

Working artifacts are compact entries in **Files**. **Open artifact canvas** opens the full page, its Feedback and its base artifact. The document header opens Files and Feedback; **Agent** opens the task’s conversation. The **Agent status** chip shows current activity. See [Artifacts](artifacts.md).

## Home {#home}

![Home: a Needs you section for your own questions and approvals, followed by a separate Running section for your agents' work](pathname:///img/app/home-light.webp)
![Home: a Needs you section for your own questions and approvals, followed by a separate Running section for your agents' work](pathname:///img/app/home-dark.webp)

**Needs you** combines your questions, approvals and tasks you can continue with teammate questions, review requests and replies. Shared rows name the person and open the exact passage, diagram or artifact spot. **Running** is your agents' work, with its current step and activity. Team keeps the shared history.

Notifications are configured in **Settings › Workflow**. Home shows no spending or shipped summary. The App notifies you only when you can act:

![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress and checks never notify](pathname:///img/diagrams/attention-light.svg)
![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress and checks never notify](pathname:///img/diagrams/attention-dark.svg)

## What it costs {#cost}

![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-light.svg)
![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-dark.svg)

The **Cost** control in a task's header opens the cost per step and agent, estimated from list prices and your agents' local logs. Dollar amounts stay hidden until you open it. Unpriced usage shows **tokens unpriced**, so an unknown price is never shown as free. Nothing is sent anywhere.

## Agent runs {#agent-runs}

**New task** and **Start the build** let you choose an installed agent, model, effort and workspace. **In QualityLayer** opens its conversation in the task’s **Agent** tab. **In my terminal, app or IDE** copies a request for your agent.

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
