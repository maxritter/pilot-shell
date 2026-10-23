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
| **Sidebar** | A **Search** row, Home, Team, Artifacts and your tasks by project, with your plan limits or usage at the foot. **+ New** starts a task |
| **Agent status** | The top-bar chip: the agent's mark and whether it is working, needs you, quiet or stopped |
| **Step track** | Where the task stands. A person icon marks the two steps you approve |
| **Your turn** | One question or decision that needs you |
| **Step page** | What needs you, what to look at, then the part of the step's document that matters now ([how it is built](#step-pages)) |
| **Right sidebar** | the task’s **Agent** conversation, **Files** and **Feedback** |

## Chat {#chat}

**+ New** offers **Chat** beside Feature and Bugfix. Chat starts a direct conversation with Claude Code or Codex. The conversation fills the task page, with **Conversation** and **Terminal** views of the same session and no workflow steps or approval gates.

The agent's own questions appear as clickable choices, with number keys and a typed answer. Its task list shows pending, running and done items above the composer. The same task list also appears in workflow conversations. You can resume or archive a Chat like other tasks.

Ask for a saved plan, slice building, artifacts, checks or an independent review as needed. **Start the workflow** asks Feature or Bugfix and moves this task into Discuss, keeping the conversation and saved work as context. Chat has no team sharing in this release. See [Chat](chat.md) for starting in a terminal and the optional tools.

## The sidebar {#sidebar}

Tasks sit under their project (a repository on this computer), the ones waiting on you first. A project appears when you start a task in it; the folder button adds one by hand.

Each task row shows its age, a dot while something is unread, its branch, its pull request with the state of its checks and the mark of the agent working on it. **View › Rows** switches to **Two lines** or **One line**; **Detailed** is the default.

| To | Do |
| --- | --- |
| Search everything | The **Search** row or **⌘K** ([below](#command-box)) |
| Fold a project | Click its header or press **←**. Folded, it still shows what waits on you |
| Reorder projects | Drag a header, or **⌥↑** / **⌥↓** |
| Rename, recolor or hide a project | The project menu (**⋯** or right-click) |
| Start a task in a project | **+** on its header |
| Rename, archive or delete a task | Right-click it, or **⋯ More** in its header |
| Filter or regroup | **View** (sliders button) |

Order, colors, names and hidden projects are stored on the computer that runs the App, so every paired browser shows the same list.

### Usage at the foot {#limits}

For each agent on a plan that reports its limits (Claude Code and Codex), the foot of the sidebar shows the window with the least left. For an agent billed by use, on an API key or through a gateway, it shows what that agent cost today as an estimate, with the last seven days as a small chart and their total. Billed by use and on a plan are never added together. Open it for every limit window, a marker where an even pace would leave it now, and when it resets; for use billed by a key, the week by agent and by day; for a plan, today's tokens, sessions and most used model. The block is hidden when there is nothing to show. It reads when the sidebar shows, when a turn ends and when you open it, never on a timer. More in [plan limits](agents/native.md#plan-limits) and **Settings › Usage**.

### Search with ⌘K {#command-box}

**⌘K** (**Ctrl+K** elsewhere) opens one box for actions, projects, tasks and the open task's files. Actions come first and name their keys. Projects answer **⌘1** to **⌘9** while the box is open, and each task shows its agent's mark. Type `›` first to see only actions, or `/` to see only the open task's files. **⌘U** opens **Settings › Usage**, **⇧⌘N** starts a task and **⌘P** goes to a file.

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

Questions and approvals appear first. **Look here** points to failures, risks and anything only you can confirm. Below that, read the step's summary and main result: requirements, findings, the Plan, the slice board or checked outcomes.

Open a row for its details, or switch to **Reader** for the complete document. Diagrams and artifacts stay visible where you need them. Both workflow levels use the same page, with more engineering detail at the Engineering level.

## Feedback and artifacts {#comments-and-artifacts}

Select a passage, a line or part of a diagram and choose **Give feedback**. The thread keeps that context with your words. The **To** picker chooses the agent, a named teammate or **Everyone on the task** when access is known. Each recipient keeps its own draft. Person-only feedback is not sent to the agent.

Working artifacts are compact entries in **Files**. **Open artifact canvas** opens the full page, its Feedback and its base artifact. The document header opens Files and Feedback; **Agent** opens the task’s conversation. The **Agent status** chip shows current activity. See [Artifacts](artifacts.md).

## Files and Review {#files}

The **Files** tab opens with the task's checkout: its branch and pull request, then what the build changed, each file with its mark, plus and minus counts, and a way into **Review the code**. **Open** opens the checkout in your editor, shown by its mark; the arrow beside it picks VS Code, Cursor, Zed, Finder or Terminal. The choice is saved in **Settings › Git and editor**. Below the card, Files groups Documents, Artifacts, Reviews and Records.

In Review, files carry the same marks in the tree and in their headers, and **Open** uses your editor, shown by its mark.

## Home {#home}

![Home: a Needs you section for your own questions and approvals, followed by a separate Running section for your agents' work](pathname:///img/app/home-light.webp)
![Home: a Needs you section for your own questions and approvals, followed by a separate Running section for your agents' work](pathname:///img/app/home-dark.webp)

**Needs you** combines your questions, approvals and tasks you can continue with teammate questions, review requests and replies. Shared rows name the person and open the exact passage, diagram or artifact spot. **Running** is your agents' work, with its current step and activity. Team keeps the shared history.

Notifications are configured in **Settings › Notifications**. The App notifies you only when you can act:

![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress and checks never notify](pathname:///img/diagrams/attention-light.svg)
![Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress and checks never notify](pathname:///img/diagrams/attention-dark.svg)

## What it costs {#cost}

![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-light.svg)
![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-dark.svg)

The **Cost** control in a task's header opens the cost per step and agent, estimated from list prices and your agents' local logs. Dollar amounts stay hidden until you open it. Unpriced usage shows **tokens unpriced**, so an unknown price is never shown as free. Nothing is sent anywhere.

## Agent runs {#agent-runs}

**New task** offers **Chat**, **Feature** and **Bugfix**. Chat supports Claude Code and Codex ([above](#chat)). For Feature and Bugfix, enter your request and files, then choose where the agent runs. **Start the build** asks the same last question.

| Choice | What you do | Where you answer |
| --- | --- | --- |
| **In the App** (recommended) | Pick the agent (Claude Code, Codex, Cursor, Grok, Antigravity, Pi or OpenCode, each with its mark), model, effort, project and branch. Its conversation opens in the task’s **Agent** tab | Questions, approvals and feedback happen in the App |
| **In my terminal** | Copy one prompt into any coding agent, app or IDE. Files you attached are saved on this computer and listed in the prompt by path | The agent asks its questions and takes your feedback in its own chat. The App shows the questions without answering them |

The branch is **Current branch**, **New branch** or **New worktree**. A worktree takes a name, which gives its folder and its branch; QualityLayer puts the folder next to your project, so other work in the project stays untouched.

The prompt for a new task starts with “Using QualityLayer” and says `start feature` or `start bug`, followed by your request. The build’s prompt says `implement the approved task` and names the task. New task and Start the build open with your last choice.

The App checks the local runtime before starting. If it cannot start the selected agent here, it explains why and keeps the terminal option available. Permissions and sign-in prompts still belong to your agent.

| To | Do |
| --- | --- |
| Read the task beside the conversation | Open **Agent** in the right sidebar; drag the divider to resize it |
| Keep working elsewhere | Close the sidebar or open another task; this does not stop the run |
| Type from another window | Use **Take control**; one window types at a time |
| Interrupt or end the run | Use **Interrupt** or **Stop** in the agent menu |
| Return to a saved conversation | Use its available **Resume** or **Open the conversation** action |
| Move to your terminal | **Move to my terminal** gives the supported resume command |

**Settings › Agents** shows each agent's sign-in and how it starts; **Sessions** holds the running agents, other paired browsers and quitting the App; **Appearance** holds the terminal's look. Choose the agent, model, effort and branch when starting a run. See [Settings](reference/settings.md#defaults).

An agent can wait for a permission, sign-in, answer or approval. A visible running process is not proof that it is making progress; read its current status and conversation. **Stop** and a user pause remain boundaries.

Any other coding agent can take the copied prompt. Terminal output stays local and is not included in shared tasks.

### The conversation {#conversation}

The agent's **Conversation** view reads its session record, and **Terminal** shows the program itself. In the Conversation:

- A finished turn folds its thinking and tool calls into one line, such as “Worked for 2 min”. The answer, the workflow's own messages, errors and anything that needs you stay open.
- A file or commit the agent names becomes a chip. A turn that changed files ends with those files and their plus and minus counts, recorded in QualityLayer's own folder, never in your repository.
- A strip of marks in the left margin has one mark per turn. Click one, or use the arrow keys, to jump to that turn.
- A long session opens at its last turns. **Show N earlier messages** loads the rest, and a long tool output opens with **Show more**.

One row under the message box holds the controls: the **model** with its agent's mark, the **effort** (not shown for an agent that has none), the **permission mode** and the **context** ring. When a plan window runs low, the row warns with “N % left”. The row lists each agent's real [permission modes](agents/native.md#permission-modes); a mode that skips every check asks you to confirm. Subagents are listed above the box.

## In Claude Code

A band above your prompt says when something waits for you in the App. `/task-pane` opens a pane with the steps and the build's progress.

![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-light.svg)
![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-dark.svg)
