---
title: Commands
description: What you type in your agent, the commands you run, the ones your agent runs, designs, and session messaging between agents.
---

`qualitylayer help` lists every command your installed version has. Add `--json` for machine-readable output, or `--task <slug>` when several tasks are open. `ql` is the short name for the same command.

## In your agent

`/ql` is the only command you need: QualityLayer adds no other command that starts with ql. The `agent-peers` skill works on its own when you ask one agent session to message another. In Codex, type `$ql` instead.

| You type | What it does |
| --- | --- |
| `/ql <request>` | Start a task with [Discuss](../steps/discuss.md); Research and the Plan follow in the same session |
| `/ql implement <task>` | Build an approved Plan ([Implement](../steps/implement.md#start-implement)) |
| `/ql review <task>` | Go through review threads: your team's ([Change reviews](../team/changes.md)) or the pull request's ([Pull request](../steps/pull-request.md)) |
| `/ql answer <ask>` | Answer a teammate's question with your agent ([Teammates' agents](../team/agents.md)) |
| `/task-pane` | Open the pane with the steps and the build's progress (Claude Code) |

**+ New** and Implement show the terminal command with the model and effort. **Here in the App** starts the interactive agent without copying a command. See [App runs](../app.md#agent-runs) for platform support.

## For you

| Command | What it does |
| --- | --- |
| `qualitylayer app` | Open the App; on a machine without it, open it in your browser and pair the browser once |
| `qualitylayer app --forget-browsers` | Make every paired browser pair again |
| `qualitylayer agent-runs stop --all --reason app-quit [--json]` | The App's Quit helper. It asks confirmed local hosts to stop only when Settings says **Stop agents**; it keeps runs when Settings says **Agents keep running** |
| `qualitylayer branch new [name]` | Start the build on a new branch: create `ql/<task>`, or the name you give, switch to it and note it on the task. See [where the build lands](../steps/implement.md#where-it-lands) |
| `qualitylayer find "<text>"` | Find a task |
| `qualitylayer tasks` | List tasks, by status or age |
| `qualitylayer doctor` | Check the setup; `--repair` fixes what it can |
| `qualitylayer update` | Update and print the release notes; with the App, it hands over to the App. See [Updates](../install.md#updates) |
| `qualitylayer feedback "<text>" [--idea] [--image <file>]` | Send feedback from a terminal, the same way as the App's sheet. See [what a report sends](files.md#feedback) |
| `qualitylayer uninstall` | Remove it; `--purge` also removes the licence and task state |
| `qualitylayer reset --first-start` | Start the App as on its first day (Setup, the first-task page, the tour), keeping the licence and the team. The settings, projects, cost and the App's page storage move into a dated folder; `reset --restore <folder>` puts them back |
| `qualitylayer licence activate <key>` | Activate a licence on this computer |
| `qualitylayer licence deactivate` | Free this computer's activation, for example to use the licence elsewhere |
| `qualitylayer licence portal` | Open your billing account at qualitylayer.dev/billing |

## Read a public share

```sh
qualitylayer share fetch --link-file /path/to/private-link.txt --out ./shared-copies --json
qualitylayer share fetch --link-stdin --out ./shared-copies --json < /path/to/private-link.txt
```

Give one link source and an output folder. Reading a link from a file or standard input keeps it out of your shell history. No licence is needed, and fetching approves, publishes and changes nothing.

<details>
<summary>What a fetch reads, writes and checks</summary>

- **The link.** Only HTTPS links on `qualitylayer.dev` or `www.qualitylayer.dev` are accepted, and redirects are refused. The fragment key decrypts the copy on your computer. It is left out of requests, errors and the manifest. Network reads time out after 15 seconds and accept a decrypted copy of up to 512 KiB.
- **The snapshot.** Every successful fetch writes a new folder with the reached Markdown documents, explicitly included task designs and `manifest.json`. The manifest records the title, reached step, share ID, revision, expiry, fetch time and a SHA-256 hash for each file. JSON output returns the same paths and values. Agent records, repository source, command output and logs are excluded. Local edits and earlier downloads are kept.
- **A snapshot stays at the fetched revision.** Fetch again to read the latest published copy. Network, revoked-link and expired-link errors never present an older snapshot as current. Revoking a link cannot remove files you already downloaded.
- **The output directory** should be private. Ownership and permission checks on Unix, or directory access rules on Windows, must show that other users cannot replace its path components. Symbolic links and unsafe directories are refused, and an existing directory's permissions are left unchanged.

</details>

## Your agent runs

You rarely type these; they are what you see in your agent's chat.

<details>
<summary>Commands your agent runs</summary>

| Command | What it does |
| --- | --- |
| `qualitylayer next` | Start a task, or get the next step of the open one; it also brings new comments on designs |
| `qualitylayer next --implement` | The same as `next --task <task>` without a task name: build the one approved Plan, or list the approved Plans that wait and stop. It is what `/ql implement` runs |
| `qualitylayer next done` | Finish the current step. In [Discuss](../steps/discuss.md) and [Research](../steps/research.md) it checks the document and moves on; in the [Outline](../steps/outline.md) it checks that every **Done means** point has a scenario and moves to Implement |
| `qualitylayer question ask` | Ask you a question in the App and wait for your answer; the terminal shows one line meanwhile |
| `qualitylayer question ask --batch` | Ask a batch. Only Discuss and Research may ask one (the Plan only a **Your call**, at most two). A batch has 3 to 6 questions, or 1 to 2 with a reason. A second batch in a step needs no reason, a third does, and a fourth is refused. The reply says which batch of the step it is |
| `qualitylayer question link <question-id> --points 1,3` · `--points none` | Say which **Done means** points an answer settles, once those points exist |
| `qualitylayer question more <question-id> --file <json>` | Answer a **Tell me more**: the agent sends the question again in plainer words, with what was missing |
| `qualitylayer question show <batch-id>` | Read one batch with every answer given so far |
| `qualitylayer question poll` | Read answers and delivery receipts for the current question batch |
| `qualitylayer question answered "<your words>" --id <question-id>` | Record what you answered in the agent's chat, on that exact open question |
| `qualitylayer question cancel --id <question-id>` · `cancel --batch <batch-id>` | Withdraw an open question or batch raised by the same session, keeping its history |
| `qualitylayer helper result <helper-id>` | Save a research agent's finished report, so Research is written from the file |
| `qualitylayer research fold` | Write Research's **Findings** and **Code references** from the reports the research agents saved, in the order they started. A second run replaces that text and leaves the planner's own words |
| `qualitylayer wait` · `wait --until-event` | Wait for an answer, comment, review result or finished check |
| `qualitylayer wait --batch <batch-id>` · `--quiet <seconds>` | Wait for a whole batch: it returns when every question is answered, or when no new answer came for the quiet time (45 seconds unless set) |
| `qualitylayer wait --json` | The same reply as one JSON object, each answer with its `answer_at` time; the plain reply opens with one line per answer |
| `qualitylayer need "<what. why>" --for T<n>` | Say the build needs something only you can do, such as a login or a secret. Nothing stops; other slices keep building |
| `qualitylayer plan draft` | Check the Plan and start its review, without asking you anything yet; your agent opens the approval once the findings are folded in |
| `qualitylayer gate open 03-plan.md` · `gate open final` | Put the Plan or the finished change up for your approval |
| `qualitylayer plan amend` · `outline amend` | Record a change to the Plan or the Outline made after the Plan was approved, with the reason; it reaches the final review. `--for T<n> --add-file <path>` puts a file on one task card, and `--add-file T<n>:<path>` names the card in each flag, for several cards in one call. Only the build session runs it |
| `qualitylayer task override +security` · `-security` · `+checkpoint:all` · `+checkpoint` · `-checkpoint` · `+second-opinion` · `-second-opinion` | Change which optional checks one task gets, as when you say "skip security" in words |
| `qualitylayer check slice <n>` | Run a slice's approved checks and record them |
| `qualitylayer check failed` | Rerun only the test files that failed in the last full run, with the fast project checks; `--background` runs it detached |
| `qualitylayer commit fix` | Commit the files this task's sessions edited since the latest fix agent was handed out, the way `commit slice` commits a slice; `--message` and `--take-staged` work as there |
| `qualitylayer comments take` | Collect the comments not yet answered |
| `qualitylayer pr watch [--wait <seconds>] [--limit <seconds>] [--again]` | After the pull request opens, wait for its checks and answer what to do next: nothing (they pass), fix these failing checks (each with the end of its log), resolve this conflict, or stop for you. At most three fix attempts for the pull request, failures and conflicts together; `--again` allows three more when you ask. `--wait` is the time before the first read (300 seconds), `--limit` how long one call waits for running checks (540). The pull request card shows the watch ([Pull request](../steps/pull-request.md#watch)) |
| `qualitylayer handover` · `handover --push` | Hand an approved Plan to your team: write its approval record and commit the task's files, then list the commits that would go. `--push` pushes the branch and, with a Team plan, lists the task for your teammates. It is the terminal's way to the **Hand over** button |
| `qualitylayer attest handover "<what the person said>"` | On a teammate's machine without a Team plan, record that you build from the approval on this branch. The first `qualitylayer next` there asks you for it |
| `qualitylayer ask list` · `ask answer` · `ask draft` | A teammate's agent reads and answers a question; see [Teammates' agents](../team/agents.md) |

Your agent cannot approve for you unless you tell it to in its chat, in your own words; the App then shows that it did. It cannot record a change that touches what you decided without asking you.

`qualitylayer wait` returns after an event or 50 seconds. For a background command, use `qualitylayer wait --until-event`: it waits for an event or up to 1,800 seconds. `--seconds` accepts 1 to 1,800 seconds. A timeout returns `pending`; keep the open work and wait again. If your shell still reports a running process, wait for that process's result.

Use `question answered --id` only for an answer you gave in the agent's chat. QualityLayer records it in **Decided with you**; the agent updates its own details. Cancelling a question records its withdrawal and keeps earlier answers. Existing taskless Home questions can be polled or cancelled with `--home`. New local intake questions belong to a named Discuss task.

</details>

## Designs {#designs}

Your agent draws [designs](../designs.md) with these, at any step, inside a task or outside one:

| Command | What it does |
| --- | --- |
| `qualitylayer design guide [authoring\|review]` | Read the authoring or review prompt once per design assignment; works without a task or repository |
| `qualitylayer design new <name> [--purpose "<line>"] [--project]` | Start a design in the task's `design/` folder, or in `docs/designs/` on this Mac outside a task or with `--project` |
| `qualitylayer design new <name> --wire` | Start a wireframe instead: grey boxes and real labels that settle the layout. A name ending in `-options` gets two layouts side by side. The finished design for the Plan is made without `--wire` |
| `qualitylayer design new <name> --folder` | Start a design of several pages: a folder with `index.html`, to which you add more pages, scripts (JSX is allowed and React is provided), styles, fonts and pictures. It opens interactive and loads nothing from the network |
| `qualitylayer design new <name> --on <design>[/<page>]` | Copy a lasting design or one of its pages, keeping its ancestry. In a task, draft on it and fold changes back in at [Review](../designs.md#fold-in). Outside a task, create a personal copy in `docs/designs/` |
| `qualitylayer design show <name> [--page <page>] [--changed "<line>"]` | Mark it updated, with one line of what changed, so you see it as soon as it renders. `--page` names a page of a design of several pages |
| `qualitylayer design keep <name> [--only-here] [--title "<title>"] [--purpose "<line>"]` | Make a draft a lasting design of the project, in `.qualitylayer/designs/<name>/` where it goes into the task's changes and pull request. `--only-here` keeps it in `docs/designs/` on this Mac instead, out of git. The draft stays as it is ([Keep](../designs.md#keep)) |
| `qualitylayer design list` | List the designs: the task's drafts with what each drafts on, the project's lasting designs with their pages, and the designs only on this Mac |
| `qualitylayer design context` | Read the local product documents and tokens before authoring |
| `qualitylayer design inspect <name>` | Read HTML, metadata and the source revision |
| `qualitylayer design push <name> --from <html> --if-match <revision\|0>` | Create or update from a local file; `0` requires an absent design, and stale revisions are refused |
| `qualitylayer design pull <name> --out <html>` | Export the current self-contained source to a new file; `import` and `export` alias `push` and `pull` |
| `qualitylayer design metadata <name> [--title <title>] [--purpose <purpose>] --if-match <revision>` | Update the title, purpose or both; provide at least one |
| `qualitylayer design copy\|rename <name> --to <name> --if-match <revision>` | Duplicate an artboard or change its filename |
| `qualitylayer design delete <name> --if-match <revision>` | Remove an unreferenced design, retaining its source in history |
| `qualitylayer design history <name>` | List saved source revisions |
| `qualitylayer design restore <name> --revision <id> --if-match <revision\|0>` | Restore a revision while keeping the current source |
| `qualitylayer design check <name>` | Check HTML structure and local resources; rendered quality still needs screenshots and interactions |
| `qualitylayer design sharing [--on\|--off]` | Include or exclude the selected task's designs in its team copy and public link; access follows the workflow's share controls |
| `qualitylayer design shot <name> [--page <page>] [--width <px>] [--theme light\|dark] [--section <label>] [--out <file>]` | Render a PNG of the page or a named section; needs Chrome. `--page` picks a page of a design of several pages |
| `qualitylayer design comments <name>` | The open comments on a design, each with its spot |
| `qualitylayer design comments <name> resolve <id…\|all> [--answer "<line>"]` | Resolve selected comments or all open comments, optionally recording an answer |

Existing designs are found in the selected task first, then `docs/designs/`. A project's lasting designs are in `.qualitylayer/designs/`; read them with `design list` and draft on them with `design new --on`. Add `--project` to target the project's copy explicitly. New designs go in the task's folder unless you use `--project` or work outside a task. `import` aliases `push`; `export` aliases `pull`. `pull` and `export` require a new output path.

Get the current revision with `design inspect` before changing a design. `--if-match 0` creates an absent design; any other value must match its current revision. Closed task designs are read-only. A referenced design cannot be deleted until its references are removed.

`design shot` needs Chrome. If the agent's sandbox prevents Chrome from starting, inspect the same page in the App; a successful source check does not establish that it rendered correctly.

## Project memory {#memory}

The App and agents use the same local lesson store. Run project commands inside the repository. Sharing remains off until you enable it locally; exchange writes files for your normal Git review and commit. See [Project memory](../memory.md).

| Command | What it does |
| --- | --- |
| `qualitylayer memory overview` | Show the project's active lesson counts and local memory status |
| `qualitylayer memory projects [--query text] [--limit n] [--cursor token]` | List registered repositories in bounded pages |
| `qualitylayer memory list [--query text] [--source task\|repository\|pilot\|manual\|all] [--scope private\|project\|all] [--limit n] [--cursor token]` | Browse previews in the current repository, including retired lessons |
| `qualitylayer memory search text` · `memory context text` | Retrieve up to eight relevant lessons with distinct content |
| `qualitylayer memory read id [--around 1..3]` | Read one lesson in the current repository; `--around` also names the lessons saved just before and after it |
| `qualitylayer memory store --title text --content text [--kind decision\|architecture\|bugfix\|pattern\|discovery\|preference] [--replaces id]` | Save or revise a lesson; `--replaces` retires an older lesson this one makes obsolete. Publication requires recorded task/check evidence |
| `qualitylayer memory pin id` · `memory unpin id` | Put a lesson in every session's lesson block, up to five per project, or take it out |
| `qualitylayer memory sessions on` · `memory sessions off` | Turn the lessons agents receive at the start of a session on or off |
| `qualitylayer memory mcp` | Serve `memory_search`, `memory_read` and `memory_save` over standard input and output for an agent; install registers it with Claude Code and Codex |
| `qualitylayer memory tool memory_search\|memory_read\|memory_save [json]` | Run one of those tools with its arguments as JSON, for plugins and scripts |
| `qualitylayer memory reindex` | Rebuild the meaning index of every saved lesson |
| `qualitylayer memory retire id` · `memory restore id` | Retire a lesson or explicitly reactivate it |
| `qualitylayer memory pause` · `memory resume` | Pause or resume local capture and task retrieval, preserving saved lessons |
| `qualitylayer memory share on` · `memory share off` | Change your sharing choice for this repository |
| `qualitylayer memory sync` · `memory export` · `memory import` | Exchange eligible lesson records with tracked repository files; all three use the same exchange and make no commits or pushes |
| `qualitylayer memory import-pilot file…` | Import bounded Pilot JSONL/Markdown records as private lessons |

All commands accept `--json`. Page sizes are 1–100; queries are at most 500 characters. Pilot CLI imports accept at most 32 files, each at most 1 MB and 2 MB in total.

## Session messaging

![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-light.svg)
![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-dark.svg)

Claude Code, Codex, Pi and OpenCode sessions on your computer can message each other. Ask one session to ask another for a review, hand over a task or talk a problem through; your agents use the `agent-peers` skill for it. You can run it yourself:

```bash
qualitylayer peers list
qualitylayer peers send --to 'cc:<name-or-uuid>' --message-file ./review-request.txt --json
```

`peers list` shows each live session's task, step, branch and last activity, with passwords and keys replaced by `[hidden]`. Use `cc:` for Claude Code, `codex:` for Codex, `pi:` for Pi or `opencode:` for OpenCode, followed by the name or UUID from the list. A session is missing? Run `qualitylayer peers doctor`.

<details>
<summary>Receipts and requests</summary>

| Command | What it records |
| --- | --- |
| `qualitylayer peers inbox --json` | This session's pending requests and ordinary messages; returning an ordinary message records `picked_up` |
| `qualitylayer peers ack --message-id <uuid> --json` | The native recipient explicitly acknowledges an ordinary message |
| `qualitylayer peers receipt --message-id <uuid> --json` | The native sender reads its ordinary message's delivery and acknowledgment status |
| `qualitylayer peers dispatch --to cc:<name-or-uuid> --message-file <file> --json` | Open a request and return its ID; `codex:` also works |
| `qualitylayer peers await --request <uuid> --json` | Read that request's reply from its original sending session |
| `qualitylayer peers reply --request <uuid> --message-file <file>` | The named native recipient answers the request once |

`queued` and `socket_write_succeeded` confirm transport submission. `picked_up` means the recipient's inbox command returned the message. `acknowledged` confirms its explicit ACK. A busy Codex thread may process its native queue after the current turn, so an agent can poll its own inbox at checkpoints. Older queued messages are not imported into this inbox. Requests expire at their timeout; an `await` that returns `pending` can be run again while the request remains valid.

</details>
