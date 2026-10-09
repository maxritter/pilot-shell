---
title: Commands
description: What you type in your agent, the commands you run, the ones your agent runs, designs, and session messaging between agents.
---

`qualitylayer help` lists every command your installed version has. Add `--json` for machine-readable output, or `--task <slug>` when several tasks are open.

`ql` is the short name for the same command.

## In your agent

`/ql` is the only command you need: QualityLayer adds no other command that starts with ql. The `agent-peers` skill works on its own when you ask one agent session to message another.

| You type | What it does |
| --- | --- |
| `/ql <request>` | Start a task with [Discuss](../steps/discuss.md); Research, the Plan and the Outline follow in the same session. **+ New** in the App gives the whole command, with the model, effort and where it starts |
| `/ql implement <task>` | Build an approved Plan. Implement Start gives the whole command, with your Build defaults. See [Implement](../steps/implement.md#start-implement) |
| `/ql review <task>` | Go through your team's review threads. See [Change reviews](../team/changes.md) |
| `/ql answer <ask>` | Answer a teammate's question with your agent. See [Teammates' agents](../team/agents.md) |
| `/task-pane` | Open the pane with the steps and the build's progress (Claude Code) |

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

## Read a public share

```sh
qualitylayer share fetch --link-file /path/to/private-link.txt --out ./shared-copies --json
qualitylayer share fetch --link-stdin --out ./shared-copies --json < /path/to/private-link.txt
qualitylayer share fetch '<complete-link>' --out ./shared-copies --json
```

Supply exactly one link source and an explicit output directory. File and standard-input sources keep the full link out of command arguments and shell history. The fragment key decrypts locally and is excluded from requests, errors, and the manifest. Only HTTPS links on `qualitylayer.dev` or `www.qualitylayer.dev` are accepted; redirects are refused.

The binary can read a share without a licence, workflow opt-in, or installed agent skills. Fetching leaves local tasks and sessions alone and grants no approval or publication rights.

Every success writes a new snapshot folder containing only the reached human Markdown documents and `manifest.json`. JSON output returns its paths, revision, expiry, fetch time, and per-file SHA-256 hashes. Designs, reviews, command output, code, and logs are excluded. Local edits and earlier downloads are preserved. Use a private output directory: ownership and permission checks on Unix, or directory access rules on Windows, must show that other users cannot replace its path components. Symbolic links and unsafe directories are refused. Existing directories' permissions are left unchanged.

A snapshot stays at the fetched revision. Fetch again to read the latest published copy. Network, revoked-link, and expired-link errors never report an older snapshot as current. Revocation cannot remove files you already downloaded. Network reads have a 15-second timeout and a 512 KiB decrypted-copy limit.

## Your agent runs

You rarely type these; they are what you see in your agent's chat.

| Command | What it does |
| --- | --- |
| `qualitylayer next` | Start a task, or get the next step of the open one; it also brings new comments on designs |
| `qualitylayer next done` | Finish the current step. In [Discuss](../steps/discuss.md) and [Research](../steps/research.md) it checks the document and moves on; in the [Outline](../steps/outline.md) it checks that every **Done means** point has a scenario and moves to Implement |
| `qualitylayer question ask` | Ask you a question in the App and wait for your answer; the terminal shows one line meanwhile |
| `qualitylayer question ask --batch` | Ask a batch. Only Discuss and Research may ask one (the Plan only a **Your call**, at most two). A batch has 3 to 6 questions, or 1 to 2 with a reason; more than 7 is refused. A third batch in a step needs a reason, and a fourth is refused |
| `qualitylayer question poll` | Read answers and delivery receipts for the current question batch |
| `qualitylayer question answered "<your words>" --id <question-id>` | Record what you actually answered in the agent's chat, on that exact open question |
| `qualitylayer question cancel --id <question-id>` · `cancel --batch <batch-id>` | Withdraw an open question or batch raised by the same session, keeping its history |
| `qualitylayer wait` · `wait --until-event` | Wait for an answer, comment, review result or finished check |
| `qualitylayer plan draft` | Check the Plan and start its review, without asking you anything yet; your agent opens the approval once the findings are folded in |
| `qualitylayer gate open 03-plan.md` · `gate open final` | Put the Plan or the finished change up for your approval (`02-plan.md` for a task started before the seven steps) |
| `qualitylayer plan amend` · `outline amend` | Record a change to the Plan or the Outline made while building, with the reason; it reaches the final review |
| `qualitylayer check slice <n>` | Run a slice's approved checks and record them |
| `qualitylayer comments take` | Collect the comments not yet answered |
| `qualitylayer ask list` · `ask answer` · `ask draft` | A teammate's agent reads and answers a question; see [Teammates' agents](../team/agents.md) |

Your agent cannot approve for you unless you tell it to in its chat, in your own words; the App then shows that it did. It cannot record a change that touches what you decided without asking you.

`qualitylayer wait` returns after an event or 50 seconds. For a background command, use `qualitylayer wait --until-event`: it waits for an event or up to 1,800 seconds. `--seconds` accepts 1 to 1,800 seconds. A timeout returns `pending`; keep the open work and wait again. If your shell still reports a running process, wait for that process's result.

Use `question answered --id` only for an answer you gave in the agent's chat. QualityLayer records it in **Decided with you**; the agent updates its own details. Cancelling a question records its withdrawal and preserves earlier answers. Existing taskless Home questions can be polled or cancelled with `--home`. New local intake questions belong to a named Discuss task.

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
qualitylayer peers send --to 'cc:<name-or-uuid>' --message-file ./review-request.txt --json
qualitylayer peers help
```

`peers list` shows what each live session is doing. It uses the session's status, task and step, title, or first request; inferred descriptions are marked as guesses. It also shows the git branch and time since the last activity. Descriptions replace text matching its password, key and token patterns with `[hidden]`.

If a session is missing, run `qualitylayer peers doctor`.

Use `cc:` for a native Claude Code session and `codex:` for a native Codex thread. Copy its name or UUID from `peers list`. A Codex stand-in uses the Codex thread UUID, even though Claude Code can see its socket.

| Command | What it records |
| --- | --- |
| `qualitylayer peers inbox --json` | This session's pending requests and ordinary messages; returning an ordinary message records `picked_up` |
| `qualitylayer peers ack --message-id <uuid> --json` | The native recipient explicitly acknowledges an ordinary message |
| `qualitylayer peers receipt --message-id <uuid> --json` | The native sender reads its ordinary message's delivery and acknowledgment status |
| `qualitylayer peers dispatch --to cc:<name-or-uuid> --message-file <file> --json` | Open a request and return its ID; `codex:` also works |
| `qualitylayer peers await --request <uuid> --json` | Read that request's reply from its original sending session |
| `qualitylayer peers reply --request <uuid> --message-file <file>` | The named native recipient answers the request once |

`queued` and `socket_write_succeeded` confirm transport submission. `picked_up` means the recipient's inbox command returned the message. `acknowledged` confirms its explicit ACK. A busy Codex thread may process its native queue after the current turn; an agent can poll its own inbox at checkpoints. Older queued messages are not imported into this inbox. Requests expire at their timeout; an `await` that returns `pending` can be run again while the request remains valid.
