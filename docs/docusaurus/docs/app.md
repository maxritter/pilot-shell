---
title: The App
description: Where you answer, read and comment while your agent works. One page for every step.
---

The QualityLayer App is where you answer, read and comment while your agent works. It runs on macOS, Windows and Linux, and without a screen `qualitylayer app` opens it in your browser. Closing a window leaves work running. Quitting follows the run setting described below.

![The App at Discuss: your tasks grouped by project on the left, the step track across the top, one question in Your turn with its choices and a field for your own answer, the Discuss document below, and Files and Comments on the right](pathname:///img/app/discuss-light.webp)
![The App at Discuss: your tasks grouped by project on the left, the step track across the top, one question in Your turn with its choices and a field for your own answer, the Discuss document below, and Files and Comments on the right](pathname:///img/app/discuss-dark.webp)

*Example task in a fictional project.*

| Part | What it does |
| --- | --- |
| **Sidebar** | The places (Home, Team, Designs) and your tasks under their projects. **+ New** starts one ([The sidebar](#sidebar)) |
| **Agent status** | The chip in the top bar: what the agent does now, whether it needs you, is quiet or has stopped |
| **Step track** | Where the task stands. A person icon marks the two steps you approve |
| **Your turn** | One question or decision, when your judgement is needed |
| **Step page** | The step's document as the parts that matter now |
| **Right sidebar** | **Files** (documents, designs, reviews, records) and **Comments** |

## The sidebar {#sidebar}

Your tasks stand under the project they come from. A project is a repository on this computer. Its header has a colored tile with two letters and its name; its open tasks follow, the ones that wait on you first, then stopped, working, quiet and pull request open. One row at the end, such as **Shipped 3 · archived 1**, holds finished work. A project with nothing open reads **Nothing open** with **New task** beside it.

A project appears by itself when you start a task in its repository. **Add a project** (the folder button above the list) picks a folder, then asks for the name and color the project shows.

| You want to | How |
| --- | --- |
| Fold a project | Click its header, or press **←** on it. A folded project keeps a sign: an amber count of what waits on you, else a ring while an agent works, else the number of open tasks |
| Reorder projects | Drag a header, or press **⌥↑** and **⌥↓**, or choose **Move up** and **Move down** |
| Change a color | One of eight in the project menu: Gray, Slate, Teal, Green, Olive, Brown, Rose or Plum. Blue, amber, violet and red are left out because they already mean agent work, your turn, checks and failure |
| Rename a project | **Rename** in the project menu. It changes the name shown in the list; the folder keeps its name |
| Hide a project | **Hide from the list** moves it into **Hidden projects** at the bottom; **Show again** brings it back |
| Start a task in a project | **+** on its header opens **New task** with that project chosen |

The task you have open always stays in the list, even under a folded project, a hidden project or a filter.

The project menu opens from the **⋯** on a header or with a right-click on it. It also holds **New task here**, **Fold the others**, **Open in Finder** and **Copy path**. A right-click on a task offers **Open**, **Rename**, **Archive** or **Restore**, and **Delete**. Renaming a task changes its title; its folder keeps its name.

The sliders button above the list opens **View**:

| Choice | What it does |
| --- | --- |
| **Group by** | **Project** (the default) or **Status**. Status shows today's groups (Your turn, Running, Shipped, Archived) with a small project tile at the end of each row |
| **Show** | **Everything open**, **What needs you**, **Running** or **Shipped**, each with its count |
| **Agent** | **Any**, **Claude Code** or **Codex** |
| **Rows** | **Two lines**, or **One line** with the step at the end |
| **Fold all projects**, **Unfold all projects** | Fold or unfold every project at once |

The search button opens **Find**, which filters by task and project name across everything, shipped and archived work included. A filter shows a chip with **Show all**, and a line such as "2 projects have nothing that needs you". **⌘K** still searches everything, and choosing a project there shows only that project.

With the list focused, **↑** and **↓** move through projects and tasks, **←** and **→** fold and unfold a project, and **Enter** opens. A project's tile and name also appear on Home's rows and in each task's header, so you can tell where a task comes from at a glance. On a phone the same list opens as a sheet with larger rows.

The order, colors, names and hidden projects are kept on the computer that runs the App, so a paired phone or browser shows your projects the same way. Folds, grouping, rows and Find belong to the window you use.

With a team, **Team** groups the tasks your teammates shared by project in the same way when the task names its project, with your name for it. Questions waiting for you stay on top.

### The places {#places}

Three places sit above the list.

| Place | What it shows |
| --- | --- |
| **Home** | What needs you, what runs, the cost and what shipped ([Home](#home)) |
| **Team** | With a Team plan: the questions teammates wait on you for, and the tasks they shared |
| **Designs** | Every project's lasting designs and the drafts in open tasks ([Designs](designs.md#designs-place)) |

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

A document can appear before its step: `02-research.md` while you answer Discuss, or a small task's `04-outline.md` while the Plan waits for approval. Other Outlines are written by the build session from the approved Plan. The file chip in the header copies the path, opens the file in your editor or shows it in its folder. **Copy document** pastes it into Confluence, Notion, Jira or GitHub.

## Comments and designs

Select a passage, a line or part of a diagram and comment. Your agent answers in the thread and says what it changed; **Ask…** passes the question to a teammate. Designs appear as compact entries in **Files**; open one full size and comment on a spot. **Open design canvas** compares its named artboards. The designs a project keeps for good, and the drafts that change them, are in the **Designs** place ([Designs](designs.md)). File actions belong to the document header.

## Home {#home}

![Home: Needs attention with a row for each task that waits, Spent on agents with the estimated cost, and Shipped](pathname:///img/app/home-light.webp)
![Home: Needs attention with a row for each task that waits, Spent on agents with the estimated cost, and Shipped](pathname:///img/app/home-dark.webp)

Four areas: **Needs attention**, **Running**, **Spent on agents** and **Shipped**. Each row in **Needs attention** and **Running** shows its project's tile and name before the title. A row in **Needs attention** opens the task where you answer or review; with a team it also lists what teammates wait on you for. The bell and the counts show the same number. The App notifies you only when you can act.

## What it costs {#cost}

![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-light.svg)
![The cost panel: the total, each step with its time, tokens and cost, and each agent named after its work](pathname:///img/diagrams/cost-dark.svg)

The dollar amount in a task's header opens its cost per step and per agent. It is an estimate from list prices and your agents' logs on this computer; nothing is sent anywhere. Tokens without a known price show as **tokens unpriced** and stay out of the total.

## Agent runs {#agent-runs}

:::note Local candidate
Starting agents inside the App is an unreleased feature under local verification. Windows App runs are planned for later; the App's task workflow and terminal commands remain available there.
:::

**+ New**, **Start Implement** and **Draft with my agent** offer **Here in the App** or **In my terminal**. An App run opens the installed agent's own interactive program. Use its normal keys, input methods and paste; folder-trust and permission prompts appear in that same window. **Esc** goes to the agent while you type in its window.

The window can fold into a compact dock while work continues. It stays attached when you navigate between tasks, Home, Team and Settings. Reopen it to see recent output. Earlier output can be trimmed; the agent keeps its own conversation history. If the window cannot draw, the run keeps working and the App shows the resume command.

### Who can type and stop

The computer's App session is key-paired. Other paired browsers watch by default and can still Stop a run. Settings › **Typing and starting agents** can also allow them to start runs and take typing control; changing run settings or protected defaults still requires a key-paired session. One viewer types at a time. **Take control** transfers typing to that window. A phone watches by default without opening its keyboard and never changes the agent's terminal size.

Watching and Stop authority are separate. A key-paired session can still stop a run it watches. **Interrupt** sends the agent's interrupt key, usually Esc. **Stop** ends the run and its confirmed helper processes. A failed cleanup remains visible; the App does not claim the run was fully stopped when it cannot confirm that.

### Permissions and working folder

**Your agent's own settings** preserves its configured approval behavior. **Fewer prompts** asks Claude Code's auto mode or Codex's own reviewer to handle approvals. Codex's reviewer uses its judgment about requests; this choice is not a promise that it will refuse a dangerous request. **Bypass prompts** removes the agent's approval and sandbox restrictions and asks for a separate confirmation each time it starts or restarts a run.

**Works in** chooses the checkout independently of **Session**. A fresh session can work in the current checkout. New-task planning can use a new worktree; an approved build uses its recorded checkout and does not create another worktree. **Lands on** shows the branch the build uses and lets you explicitly create a new branch.

### Resume, move and quit

On a stopped known-agent run, **Open the session** opens the conversation and waits for what you type. **Resume here** continues this task with its next instruction. **Move to my terminal** stops the App run and gives its resume line after cleanup. Changes to a known agent's settings offer **Restart with these settings** only at a confirmed turn boundary. Silence and an interrupt do not by themselves establish that boundary.

Settings › Workflow › **Where agents run** sets the default place, permissions, typing access, window behavior and **When you quit the App**. **Agents keep running** leaves runs alive; **Stop agents** asks them to stop on Quit. Closing or folding a window keeps work running. Updating, relaunching or a failure exit preserves runs regardless of that setting. An unsuccessful Quit cleanup is shown when the App returns.

### Another agent

Set a literal program path and a JSON array of arguments in Settings. Each argument is passed as written; the App does not run a shell command. The window opens first, then **Send request** types the request once when you choose. Interrupt, Restart, Move and automatic Resume are unavailable for an unknown agent. Stop and the terminal option remain available.

Agent windows and their output are local, owner-only records. Sharing a task does not share terminal output, launch settings or host logs. [Team drafting](team/agents.md) always uses the agent's own settings and leaves Send to the person.

## In Claude Code

A slim band above your prompt says when something waits for you in the App. `/task-pane` opens a pane with the steps and the build's progress.

![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-light.svg)
![The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you](pathname:///img/diagrams/band-dark.svg)

**⌘K** finds a task or a setting.
