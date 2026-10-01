---
title: Commands
description: The commands you type, the ones your agent runs, and session messaging between agents.
---

`qualitylayer help` lists every command your installed version has. Add `--json` for machine-readable output, or `--task <slug>` when several tasks are open.

## For you

| Command | What it does |
| --- | --- |
| `qualitylayer cockpit` | Open the Cockpit; `cockpit stop` stops it |
| `qualitylayer find "<text>"` | Find a task |
| `qualitylayer tasks` | List tasks, by status or age |
| `qualitylayer doctor` | Check the setup; `--repair` fixes what it can |
| `qualitylayer update` | Update to the latest version |
| `qualitylayer uninstall` | Remove it; `--purge` also removes the licence and task state |
| `qualitylayer licence activate <key>` | Activate a licence; `licence portal` opens billing |
| `qualitylayer telemetry off` | Stop the anonymous events; `DO_NOT_TRACK=1` works too |

## Your agent runs

You rarely type these, but they explain what you see in your agent's chat.

| Command | What it does |
| --- | --- |
| `qualitylayer next "<request>"` | Start a task, or get its next step |
| `qualitylayer next "show me <topic>"` | Make a picture of how something works |
| `qualitylayer gate open <document>` | Put a document up for your review in the Cockpit |
| `qualitylayer comments take` | Collect the comments not yet answered, your team's included |
| `qualitylayer review wait design \| verify` | Wait for the second opinion, which starts on its own |
| `qualitylayer plan amend --by agent\|user` | Record a change to the approved plan during the build |
| `qualitylayer card T<n>` | Print one task card with the contract it builds |
| `qualitylayer validate <document>` | Check that a document is complete |
| `qualitylayer guide` | Print the workflow rules, for an agent started with a Goal |

An agent cannot record a change that touches what you decided; it asks you and records your words with `--by user`.

## Session messaging

![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-light.svg)
![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-dark.svg)

Claude Code and Codex sessions on your computer can message each other, in any direction. Your agents use it through the `qualitylayer-peers` skill; you can run it yourself:

```bash
qualitylayer peers list
qualitylayer peers send --to cc:<name> --message "The design is ready for review."
qualitylayer peers help
```

`ask` waits for the matching reply, `dispatch` hands over work you can carry on beside, and topics let several sessions follow one thread. A built-in limit stops two sessions from replying to each other forever. If a session is missing, run `qualitylayer peers doctor`.

Tell a session `buddy: @<name>` and it consults that peer by default, for reviews or a second opinion. A buddy's agreement is advice, never your approval. When the buddy does the work and your session steers, the buddy checks in at each gate and about every 15 minutes, and your session answers with every correction and decision in one reply, so nothing arrives late or crossed.

A Codex session that ends a turn without an answer now says so to whoever asked, instead of leaving them waiting. After you update QualityLayer, `qualitylayer peers restart <name>` brings an attached Codex session onto the new version and keeps its reply limit where it was.
