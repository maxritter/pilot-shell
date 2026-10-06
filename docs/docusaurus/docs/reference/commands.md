---
title: Commands
description: What you type in your agent, the commands you run, the ones your agent runs, designs, and session messaging between agents.
---

`qualitylayer help` lists every command your installed version has. Add `--json` for machine-readable output, or `--task <slug>` when several tasks are open.

`ql` is the short name for the same command.

## In your agent

| You type | What it does |
| --- | --- |
| `/ql <request>` | Start a task with [Discuss](../steps/discuss.md). **+ New** in the App gives the whole command, with the model, effort and where it starts |
| `/ql implement <task>` | Build an approved Plan. Implement Start gives the whole command, with your Build defaults. See [Implement](../steps/implement.md#start-implement) |
| `/ql review <task>` | Go through your team's review threads. See [Change reviews](../team/changes.md) |
| `/ql answer <ask>` | Answer a teammate's question with your agent. See [Teammates' agents](../team/agents.md) |
| `/ql-pane` | Open the pane with the steps and the build's progress (Claude Code) |

In Codex, type `$ql` in place of `/ql`.


## For you

| Command | What it does |
| --- | --- |
| `qualitylayer app` | Open the App; on a machine without it, open it in your browser and pair the browser once |
| `qualitylayer app --forget-browsers` | Make every paired browser pair again |
| `qualitylayer find "<text>"` | Find a task |
| `qualitylayer tasks` | List tasks, by status or age |
| `qualitylayer doctor` | Check the setup; `--repair` fixes what it can |
| `qualitylayer update` | Update and print the release notes; with the App, it hands over to the App. See [Updates](../install.md#updates) |
| `qualitylayer feedback "<text>" [--idea] [--image <file>]` | Send feedback from a terminal, the same way as the App's sheet. See [what a report sends](files.md#feedback) |
| `qualitylayer uninstall` | Remove it; `--purge` also removes the licence and task state |
| `qualitylayer licence activate <key>` | Activate a licence; `licence portal` opens billing |
| `qualitylayer telemetry off` | Stop the usage events; `DO_NOT_TRACK=1` works too |

## Your agent runs

You rarely type these; they are what you see in your agent's chat.

| Command | What it does |
| --- | --- |
| `qualitylayer next` | Start a task, or get the next step of the open one; it also brings new comments on designs |
| `qualitylayer question ask` | Ask you a question in the App and wait for your answer; the terminal shows one line meanwhile |
| `qualitylayer gate open 02-plan.md` · `gate open final` | Put the Plan or the finished change up for your approval |
| `qualitylayer check slice <n>` | Run a slice's approved checks and record them |
| `qualitylayer comments take` | Collect the comments not yet answered |
| `qualitylayer ask list` · `ask answer` · `ask draft` | A teammate's agent reads and answers a question; see [Teammates' agents](../team/agents.md) |

Your agent cannot approve for you unless you tell it to in its chat, in your own words; the App then shows that it did. It cannot record a change that touches what you decided without asking you.

## Designs {#designs}

Your agent draws [designs](../designs.md) with these, at any step, inside a task or outside one:

| Command | What it does |
| --- | --- |
| `qualitylayer design new <name> [--purpose "<line>"] [--project]` | Start a design in the task's `design/` folder, or in `docs/designs/` outside a task or with `--project` |
| `qualitylayer design show <name> [--changed "<line>"]` | Mark it updated, with one line of what changed, so you see it as soon as it renders |
| `qualitylayer design list` | List the designs |
| `qualitylayer design shot <name> [--width <px>] [--theme light\|dark]` | Take a picture of a design, so the agent can look at its own work |
| `qualitylayer design comments <name>` | The open comments on a design, each with its spot |

## Session messaging

![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-light.svg)
![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-dark.svg)

Claude Code and Codex sessions on your computer can message each other, in any direction. Your agents use it through the `agent-peers` skill; you can run it yourself:

```bash
qualitylayer peers list
qualitylayer peers send --to cc:<name> --message "The Plan is ready for review."
qualitylayer peers help
```

`peers list` says what every live session is doing, even one that set no status: its QualityLayer task and step, its own title, or the first thing it was asked, each marked as a guess. Each session also shows its git branch and how long ago it last did something. Nothing that looks like a password, key or token is ever shown.

If a session is missing, run `qualitylayer peers doctor`.
