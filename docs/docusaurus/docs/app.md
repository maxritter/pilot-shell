---
title: The App
description: Where you answer, read and comment while your agent works. One page for every step.
---

The QualityLayer App is where you answer, read and comment while your agent works. It runs on macOS, Windows and Linux, and without a screen `qualitylayer app` opens it in your browser. Closing a window leaves work running. Quitting follows the run setting described below.

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

A document can appear before its step: `02-research.md` while you answer Discuss, or a small task's `04-outline.md` while the Plan waits for approval. Other Outlines are written by the build session from the approved Plan. The file chip in the header copies the path, opens the file in your editor or shows it in its folder. **Copy document** pastes it into Confluence, Notion, Jira or GitHub.

## Comments and designs

Select a passage, a line or part of a diagram and comment. Your agent answers in the thread and says what it changed; **Ask…** passes the question to a teammate. Designs appear as compact entries in **Files**; open one full size and comment on a spot. **Open design canvas** compares its named artboards ([Designs](designs.md)). File actions belong to the document header.

## Home


![Home: Needs attention with a row for each task that waits, Spent on agents with the estimated cost, and Shipped](pathname:///img/app/home-light.webp)
![Home: Needs attention with a row for each task that waits, Spent on agents with the estimated cost, and Shipped](pathname:///img/app/home-dark.webp)

Four areas: **Needs attention**, **Running**, **Spent on agents** and **Shipped**. Each row in **Needs attention** opens the task where you answer or review; with a team it also lists what teammates wait on you for. The bell and the counts show the same number. The App notifies you only when you can act.

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
