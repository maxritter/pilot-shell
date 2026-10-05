---
title: Commands
description: What you type in your agent, the commands you run, the ones your agent runs, and session messaging between agents.
---

`qualitylayer help` lists every command your installed version has. Add `--json` for machine-readable output, or `--task <slug>` when several tasks are open.

`ql` is the short name for the same command: `ql app` is `qualitylayer app`. If another command on your computer is already called `ql`, the installer leaves it alone and says so; `qualitylayer` always works.

## In your agent

| You type | What it does |
| --- | --- |
| `/ql <request>` | Start a task with [Discuss](../steps/discuss.md) |
| `/ql implement <task>` | Build an approved Plan. The App's start card gives the whole command, with the model and effort. See [Implement](../steps/implement.md#start-implement) |
| `/ql review <task>` | Go through your team's review threads. See [Review changes as a team](../team/changes.md) |
| `/ql answer <ask>` | Answer a teammate's question with your agent. See [Teammates' agents](../team/agents.md) |
| `/ql-pane` | Open the pane with the steps and the build's progress (Claude Code) |

In Codex, type `$ql` in place of `/ql`. Your agent gives you the App's link when you need it, and the App shows the current task.

Your agent asks every decision in its picker, so you rarely type a command. The Claude Code band names the question it asks next.

## For you

| Command | What it does |
| --- | --- |
| `qualitylayer app` | Open the App; on a machine without it, open it in your browser and pair the browser once |
| `qualitylayer app --forget-browsers` | Make every paired browser pair again |
| `qualitylayer find "<text>"` | Find a task |
| `qualitylayer tasks` | List tasks, by status or age |
| `qualitylayer doctor` | Check the setup; `--repair` fixes what it can |
| `qualitylayer update` | Update and print the release notes; with the App, it hands over to the App. See [Updates](../updating.md) |
| `qualitylayer feedback "<text>" [--idea] [--image <file>]` | Send feedback from a terminal, the same way as the App's sheet. See [what a report sends](files.md#feedback) |
| `qualitylayer uninstall` | Remove it; `--purge` also removes the licence and task state |
| `qualitylayer licence activate <key>` | Activate a licence; `licence portal` opens billing |
| `qualitylayer telemetry off` | Stop the anonymous events; `DO_NOT_TRACK=1` works too |
| `qualitylayer ask list` | Questions to you and from you; see [Teammates' agents](../team/agents.md#from-the-command-line) for the rest |

## Your agent runs

You rarely type these, but they explain what you see in your agent's chat.

| Command | What it does |
| --- | --- |
| `qualitylayer next "<request>"` | Start Discuss, or get the next step of the open task |
| `qualitylayer next start feature: <problem>` | Create the task after the first questions; `bug:` for a bug |
| `qualitylayer next handback "<reason>"` | End a request that is too small; no task is created |
| `qualitylayer next done` | Finish Discuss and move on to the Plan |
| `qualitylayer question show '<json>'` | Show the question being asked in your agent's picker in the App. The JSON holds `question`, `lead`, `choices` (each with a `label` and a `detail`), `recommended` and `of`. For a decision of a Plan it also names the `gate` and the `item`. It does not wait. Add `--task <slug>` when several tasks are open |
| `qualitylayer question answered "<choice>"` | Close the question in the App, which shows your answer as "answered in the chat" |
| `qualitylayer next "show me <topic>"` | Make a picture of how something works |
| `qualitylayer gate open 02-plan.md` | Put the Plan up for your approval. The reply lists the questions your agent asks you, one per decision, and "Approve the Plan?" last |
| `qualitylayer gate open final` | Put the finished change up for your final approval, with "Approve the change?" last |
| `qualitylayer hook prompt` · `qualitylayer hook activity` | Run by your agent's hooks, which the installer sets. They record `approve` typed in the session, and the answer you pick in your agent's picker |
| `qualitylayer check slice <n>` | Run a slice's approved commands and record them |
| `qualitylayer check task T<n>` | Run one task card's check and record it |
| `qualitylayer check all` | Run the project's tests, lint, type check and build and record them |
| `qualitylayer verdict <assignment> <item> pass\|fail\|missing\|user\|note "<text>"` | Record the result of one check as an agent makes it, so the Verify checklist fills in live. `user` marks a point only you can confirm |
| `qualitylayer attest <item> "<what you said>" [--evidence <file>]` | Record what you confirmed, such as an **Ask the agent to record it** answer on an Only you can confirm item. It is kept with your words, outside the build log. An agent cannot settle a point only you can confirm on its own |
| `qualitylayer gate stop '<json>'` | Stop checking after two failed tries, so your agent asks you how to go on in its picker. Wait for your choice with `qualitylayer gate wait` |
| `qualitylayer card T<n>` | Print one task card with the contract it builds |
| `qualitylayer progress build --for T<n> "<line>"` | Report that a task is being built |
| `qualitylayer comments take` | Collect the comments not yet answered, your team's included |
| `qualitylayer plan amend --by agent\|user --for T<n>` | Record a change to the approved Plan, one entry for each task named |
| `qualitylayer task override +security` | Record a change you asked for on this task; see [Settings](settings.md#for-one-task) |
| `qualitylayer validate <document>` | Check that a document is complete |
| `qualitylayer guide` | Print the workflow rules, for an agent started with a goal |

An agent cannot record a change that touches what you decided. It asks you and records your words with `--by user`.

## Session messaging

![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-light.svg)
![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-dark.svg)

Claude Code and Codex sessions on your computer can message each other, in any direction. Your agents use it through the `ql-peers` skill; you can run it yourself:

```bash
qualitylayer peers list
qualitylayer peers send --to cc:<name> --message "The Plan is ready for review."
qualitylayer peers help
```

`ask` waits for the matching reply, `dispatch` hands over work you can carry on beside, and topics let several sessions follow one thread. A built-in limit stops two sessions from replying to each other forever. If a session is missing, run `qualitylayer peers doctor`.

Tell a session `buddy: @<name>` and it consults that peer by default, for reviews or a second opinion. A buddy's agreement is advice, never your approval. When the buddy does the work and your session steers, the buddy checks in at each approval and about every 15 minutes. Your session answers with every correction and decision in one reply, so nothing arrives late or crossed.

A Codex session that ends a turn without an answer tells whoever asked, so nobody waits for nothing. After you update QualityLayer, `qualitylayer peers restart <name>` brings an attached Codex session onto the new version and keeps its reply limit where it was.
