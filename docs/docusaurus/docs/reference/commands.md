---
title: Commands
description: Ask in plain language, or look up the CLI commands for tasks, artifacts, code health and memory.
---

`qualitylayer help` lists every command your installed version has. Add `--json` for machine-readable output, or `--task <slug>` when several tasks are open. `ql` is the short name for the same command.

## In your agent

![A visual Plan beside its agent conversation](pathname:///img/app/plan-light.webp)
![A visual Plan beside its agent conversation](pathname:///img/app/plan-dark.webp)


Ask your agent in natural language, naming **QualityLayer** or **QL**. The same wording works in Claude Code, Codex, Pi and OpenCode; no slash or dollar skill invocation is required.

| Example request | What it does |
| --- | --- |
| “Using QualityLayer, plan a CSV export” | Start a task with [Discuss](../steps/discuss.md); Research and the Plan follow in the same session |
| “Using QL, implement the approved plan for task retry-webhooks” | Build an approved Plan ([Implement](../steps/implement.md#start-implement)) |
| “Using QL, review task retry-webhooks” | Go through review threads: your team's ([Change reviews](../team/changes.md)) or the pull request's ([Pull request](../steps/pull-request.md)) |
| “Using QL, answer the team ask a1” | Answer a teammate's question with your agent ([Teammates' agents](../team/agents.md)) |
| “Using QL, continue verification of task retry-webhooks in this IDE” | Continue the recorded task after resolving the previous run's ownership |
| “Open the current QualityLayer artifact in my browser at Billing” | Open the exact artifact page and section; clarify an ambiguous current artifact |
| `/task-pane` | Open the pane with the steps and the build's progress (Claude Code) |

**+ New** and **Start the build** offer **In QualityLayer** and **In my terminal, app or IDE**. The external option copies a request; choose the model and effort in the agent receiving it. See [App runs](../app.md#agent-runs) for platform support.

Your agent loads `ql-workflow` for workflow execution, `ql-artifact` for artifacts, `ql-peer` for other agent sessions, and `ql-manage` for lookup, memory, sharing, setup and diagnostics. Standalone artifact and administrative requests do not create a workflow task. Each skill uses the current CLI's instructions for the operation.

## Terminal mode

Ask “Using QualityLayer in the terminal, plan a CSV export” to answer questions and approve the Plan and finished change in your agent's chat. Claude Code, Codex, Pi and OpenCode use their available question picker; numbered chat choices are the fallback. Only your own picks or words count as answers and approvals.

Where the agent runs decides where you answer: **In QualityLayer** keeps questions and approvals in the App, **In my terminal, app or IDE** in the agent's chat. `qualitylayer task set answers=app|terminal` changes it later for the current task. A computer without a screen selects Terminal mode automatically; existing tasks retain their saved choice. The App can still show the task without opening or notifying by itself.

| Command | What it does |
| --- | --- |
| `qualitylayer settings get [<key>]` | Read all saved settings or one key, including dotted keys such as `notifications.gateOpened` |
| `qualitylayer settings set answers terminal` | Set where you answer for tasks started without a location, such as a plain terminal request; use `app` to answer in QualityLayer |
| `qualitylayer task set answers=terminal` | Change where you answer for the current task; use `answers=app` to return |
| `qualitylayer read 03-plan.md [--width 100] [--lead]` | Read a task document with diagrams drawn as terminal text; `--lead` selects its leading sections |
| `qualitylayer read artifact <name> [--page <page>] [--width 100]` | Read a text sketch of the exact artifact page |
| `qualitylayer artifact show <name> --page <page> --terminal` | Show a text sketch and save a screenshot when Chrome is available; otherwise explain how to add Chrome |

Terminal artifact feedback uses `qualitylayer artifact comments add <name> --page <page> --section <id> --asked "<your exact words>"`. The command checks those words against your session. Task lists, saved lessons and teammate asks remain available through the commands below.

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
| `qualitylayer agents list` | Read the last executable/version results without running another check |
| `qualitylayer agents check [all\|claude-code\|codex\|pi\|opencode]` | Check installed executables and versions with the current login PATH; account access is checked when a session starts |
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
- **The snapshot.** Every successful fetch writes a new folder with the reached Markdown documents, explicitly included task artifacts and `manifest.json`. The manifest records the title, reached step, share ID, revision, expiry, fetch time and a SHA-256 hash for each file. JSON output returns the same paths and values. Agent records, repository source, command output and logs are excluded. Local edits and earlier downloads are kept.
- **A snapshot stays at the fetched revision.** Fetch again to read the latest published copy. Network, revoked-link and expired-link errors never present an older snapshot as current. Revoking a link cannot remove files you already downloaded.
- **The output directory** should be private. Ownership and permission checks on Unix, or directory access rules on Windows, must show that other users cannot replace its path components. Symbolic links and unsafe directories are refused, and an existing directory's permissions are left unchanged.

</details>

## Your agent runs

You rarely type these; they are what you see in your agent's chat.

<details>
<summary>Commands your agent runs</summary>

| Command | What it does |
| --- | --- |
| `qualitylayer next` | Start a task, or get the next step of the open one; it also brings new comments on artifacts |
| `qualitylayer next --implement` | Build the one approved Plan waiting for implementation, or list the candidates and stop when the target is unclear |
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

## Artifacts {#artifacts}

![Open a lasting artifact, choose a page and continue with its agent](pathname:///img/app/artifacts-open-light.webp)
![Open a lasting artifact, choose a page and continue with its agent](pathname:///img/app/artifacts-open-dark.webp)

Ask your agent to create, open or revise an artifact. [The visual guide](../artifacts.md) explains the workspace.

<details>
<summary>Artifact CLI commands and file locations</summary>


Your agent draws [artifacts](../artifacts.md) with these, at any step, inside a task or outside one:

| Command | What it does |
| --- | --- |
| `qualitylayer artifact guide [authoring\|review]` | Read the authoring or review prompt once per artifact assignment; works without a task or repository |
| `qualitylayer artifact new <name> [--purpose "<line>"] [--project]` | Start an artifact in the task's `artifacts/` folder, or in `docs/artifacts/` on this computer outside a task or with `--project` |
| `qualitylayer artifact new <name> --wire` | Start a wireframe instead: grey boxes and real labels that settle the layout. A name ending in `-options` gets two layouts side by side. The finished artifact for the Plan is made without `--wire` |
| `qualitylayer artifact new <name> --folder` | Start an artifact of several pages: a folder with `index.html`, to which you add more pages, scripts (JSX is allowed and React is provided), styles, fonts and pictures. It opens interactive and loads nothing from the network |
| `qualitylayer artifact new <name> --on <artifact>[/<page>]` | Copy a lasting artifact or one of its pages, keeping its ancestry. In a task, draft on it and fold changes back in at [Review](../artifacts.md#fold-in). Outside a task, create a personal copy in `docs/artifacts/` |
| `qualitylayer artifact new <name> --on shared:<name>[/<page>]` | In a task, start a draft from the newest version of an artifact your team shares, or from one page and the files it uses. The draft remembers that version ([Shared artifacts](../artifacts.md#shared-save)) |
| `qualitylayer artifact show <name> [--task <slug>] [--page <page>] [--changed "<line>"]` | Mark it updated, with one line of what changed, so you see it as soon as it renders. `--page` names a page of an artifact of several pages |
| `qualitylayer artifact open <name> [--project] [--task <slug>] [--page <page>] [--section <id-or-label>] [--browser] [--no-open]` | Open an exact artifact page in QualityLayer or the browser viewer. A missing or ambiguous section is reported in the viewer. `--no-open` prepares the link |
| `qualitylayer artifact keep <name> [--only-here] [--title "<title>"] [--purpose "<line>"]` | Make a draft a lasting artifact of the project, in `.qualitylayer/artifacts/<name>/` where it goes into the task's changes and pull request. `--only-here` keeps it in `docs/artifacts/` on this computer instead, out of git. The draft stays as it is ([Keep](../artifacts.md#keep)) |
| `qualitylayer artifact list [--task <slug>]` | List the artifacts: the task's drafts with what each drafts on, the project's lasting artifacts with their pages, and the artifacts only on this computer. Each shows whether its design tokens still match the project's design file: `current`, `drifted` (with how many differ), `n/a` or `unassessed` |
| `qualitylayer artifact context` | Read the local product documents and tokens before authoring |
| `qualitylayer artifact inspect <name>` | Read HTML, metadata and the source revision, and whether its design tokens match the design file |
| `qualitylayer artifact tokens <name> [--project] [--page <page>] [--refresh --if-match <revision>]` | List the colour, type and spacing values of the page that differ from the project's design file. `--refresh` rewrites exactly those values in the page and the stylesheets it links, in a task or project draft; it writes nothing if any of those files changed since. A lasting artifact is refreshed in a task draft of it |
| `qualitylayer artifact library inspect <name>` | Read a lasting artifact's title, state, pages and management revision, including deleted entries |
| `qualitylayer artifact library rename <name> --title "<title>" [--purpose "<line>"] --if-match <revision>` | Change a lasting artifact's display title or description while keeping its identity and links |
| `qualitylayer artifact library copy <name> --to <copy-name> --title "<title>" [--to-project <id>] --if-match <revision>` | Make an independent copy in the current or another registered project |
| `qualitylayer artifact library archive\|restore\|delete <name> --if-match <revision> [--confirm-in-use]` | Retire or restore a Library entry. Deletion keeps its source files and requires explicit confirmation when active drafts use it |
| `qualitylayer artifact push <name> --from <html> --if-match <revision\|0>` | Create or update from a local file; `0` requires an absent artifact, and stale revisions are refused |
| `qualitylayer artifact pull <name> --out <html>` | Export the current self-contained source to a new file; `import` and `export` alias `push` and `pull` |
| `qualitylayer artifact metadata <name> [--title <title>] [--purpose <purpose>] --if-match <revision>` | Update the title, purpose or both; provide at least one |
| `qualitylayer artifact copy\|rename <name> --to <name> --if-match <revision>` | Duplicate an artboard or change its filename |
| `qualitylayer artifact delete <name> --if-match <revision>` | Remove an unreferenced artifact, retaining its source in history |
| `qualitylayer artifact history <name>` | List saved source revisions |
| `qualitylayer artifact restore <name> --revision <id> --if-match <revision\|0>` | Restore a revision while keeping the current source |
| `qualitylayer artifact check <name> [--task <slug>] [--render]` | Check HTML structure and local resources. `--render` also loads the page at its width and at 390 px, light and dark, and reports script errors, blocked requests and failed pictures; needs Chrome. Visual quality still needs the pictures and interactions |
| `qualitylayer artifact sharing [--on\|--off]` | Include or exclude the selected task's artifacts in its team copy and public link; access follows the workflow's share controls |
| `qualitylayer artifact shot <name> [--page <page>] [--width <px>] [--theme light\|dark] [--section <label>] [--out <file>]` | Render a PNG of the page or a named section, with the script errors and blocked requests it raised; needs Chrome. `--page` picks a page of an artifact of several pages |
| `qualitylayer artifact shot <name> --matrix [--page <page>]` | Render four PNGs: the artifact's width (or 1280) and 390 px, each light and dark, with the errors and blocked requests of each |
| `qualitylayer artifact claude <name> status\|publish --if-match <revision> [--title "<title>"]\|update [--if-remote <sha256>]\|comments [--open-only]` | Publish through Open Claude Design 1.8.0 or later, update on request, or read comments. The artifact keeps the link ([Publish to Claude](../artifacts.md#claude-design)) |
| `qualitylayer artifact shared list [--json]` | List the artifacts your team shares with you: name, title, owner, newest version, your access (`You own it`, `Can edit`, `Can comment`) and remote id |
| `qualitylayer artifact shared versions <name> [--json]` | List every saved version of a shared artifact: who saved it, through what, and its note. With `--json`, `saved_by` names the team member whose sign-in saved a version when that is a different person from the author |
| `qualitylayer artifact shared restore <name> --version <n>` | Save version `<n>` again as the newest. The older version stays in the list. Needs Can edit or ownership |
| `qualitylayer artifact shared pull <draft>` | Merge the team's newer version into a draft, file by file. A file changed on both sides stays unmerged, with the team's copy beside it as `<file>.team<ext>`, and is listed |
| `qualitylayer artifact shared save <draft> [--note '<what changed>'] [--delete <path>]...` | Save the draft as the next version for everyone. Refused when the team has a newer version, when conflicts remain, or when you can only comment. `--delete` removes a file and can repeat |
| `qualitylayer artifact comments <name>` | The open comments on an artifact, each with its spot |
| `qualitylayer artifact comments <name> resolve <id…\|all> [--answer "<line>"]` | Resolve selected comments or all open comments, optionally recording an answer |

Existing artifacts are found in the selected task first, then `docs/artifacts/`. A project's lasting artifacts are in `.qualitylayer/artifacts/`; read them with `artifact list` and draft on them with `artifact new --on`. Add `--project` to target the project's copy explicitly. `show`, `open`, `check` and `list` accept `--task <slug>` to select another task's drafts of this repository without binding the session to it; `--task` with `--project` is refused. New artifacts go in the task's folder unless you use `--project` or work outside a task. `import` aliases `push`; `export` aliases `pull`. `pull` and `export` require a new output path.

For `artifact shared`, `<name>` is the artifact's folder name. If two shared artifacts have the same name, use the remote id from `artifact shared list`. `pull`, `save` and `artifact new --on shared:` work in a task; `restore` works inside the repository you work on. See [Share an artifact with your team](../artifacts.md#team-shared).

Get the current revision with `artifact inspect` before changing an artifact. `--if-match 0` creates an absent artifact; any other value must match its current revision. Closed task artifacts are read-only. A referenced artifact cannot be deleted until its references are removed.

Library operations use the revision from `artifact library inspect`, which includes metadata and every source dependency. `artifact show` reports a source-folder revision for a source-backed artifact and a separate `page_revision` for its HTML. The viewer refreshes source changes while keeping its selected page. Its expand control hides both sidebars within the current window; toggling it again restores their previous state and refits the artifact.

`artifact shot` needs Chrome. If the agent's sandbox prevents Chrome from starting, inspect the same page in the App; a successful source check does not establish that it rendered correctly.

</details>

## Code health {#code-health}

![Local checks feed findings back to your agent, which fixes or reviews them](pathname:///img/diagrams/code-health-light.svg)
![Local checks feed findings back to your agent, which fixes or reviews them](pathname:///img/diagrams/code-health-dark.svg)


Local Qlty checks are advisory. See [Code health](code-health.md) for automatic feedback, availability and how to review findings.

| Command | What it does |
| --- | --- |
| `qualitylayer quality status` · `quality setup` | Inspect availability or retry managed tool setup |
| `qualitylayer quality check [paths...] [--all] [--duplication] [--fail-on-new]` | Check changed or named source; `--all` selects the project, `--duplication` broadens the analysis, and `--fail-on-new` explicitly fails while findings remain unreviewed |
| `qualitylayer quality metrics [paths...] [--all]` | Return function metrics with source capture metadata |
| `qualitylayer quality lint [paths...] [--all]` | Run enabled project linters without autofixes; plugin tools may need setup |
| `qualitylayer quality acknowledge <id> --reason "<evidence>"` | Retain an intentional or deferred finding with a specific reason; source or metric changes require review again |
| `qualitylayer quality on` · `quality off` | Resume or pause checks in this project |

With no paths, `check` selects changed and untracked source files. A focused duplication check compares only its selected files; use `--all --duplication` for a project-wide review.

<details>
<summary>Availability and reviewing findings</summary>

Automatic structure checks use a managed local Qlty binary, without model calls or plugin downloads. Installation and updates prepare it; retry `quality setup` if it is unavailable. Native builds cover macOS and Linux on x64 and ARM64, and Windows x64. Windows ARM64 reports unavailable.

Read every finding against the source. `known` means seen before, not reviewed. Acknowledge an intentional pattern or deferred improvement with its evidence and repair boundary. Acknowledging retains the finding; it does not repair the code. Changed source, analyzer settings, duplication counterparts or increased metrics require review again.

Manual linting uses the project's enabled Qlty plugins and may need their tools or runtimes. QualityLayer acknowledgments cover built-in structure and duplication findings. Review plugin findings through the linter's own controls.

Checks are advisory unless you add `--fail-on-new`. Failed, skipped or unavailable checks give no passing evidence. Pause and resume per project with `quality off` and `quality on`.

</details>

## Project memory {#memory}

![Memory settings, saved lessons and project sharing](pathname:///img/app/memory-light.webp)
![Memory settings, saved lessons and project sharing](pathname:///img/app/memory-dark.webp)


The App and agents use the same local lesson store. Lessons sent to a cloud agent may reach its provider; local storage and local embedding do not prevent that. Run project commands inside the repository. Sharing remains off until you enable it locally; exchange writes files for your normal Git review and commit. See [Project memory](../memory.md).

<details>
<summary>Memory CLI commands</summary>

| Command | What it does |
| --- | --- |
| `qualitylayer memory overview` | Show the project's active lesson counts and local memory status |
| `qualitylayer memory projects [--query text] [--limit n] [--cursor token]` | List registered repositories in bounded pages |
| `qualitylayer memory list [--query text] [--source task\|repository\|pilot\|manual\|all] [--scope private\|project\|all] [--limit n] [--cursor token]` | Browse previews in the current repository, including retired lessons |
| `qualitylayer memory search text` · `memory context text` | Retrieve up to eight relevant lessons with distinct content |
| `qualitylayer memory read id [--around 1..3]` | Read one lesson in the current repository; `--around` also names the lessons saved just before and after it |
| `qualitylayer memory store --title text --content text [--kind decision\|architecture\|bugfix\|pattern\|discovery\|preference] [--replaces id]` | Save or revise a lesson; `--replaces` retires an older lesson this one makes obsolete. Sharing requires an eligible project lesson and the repository’s sharing switch; passing checks are not required |
| `qualitylayer memory pin id` · `memory unpin id` | Put a lesson in every session's lesson block, up to five per project, or take it out |
| `qualitylayer memory sessions on` · `memory sessions off` | Turn the lessons agents receive at the start of a session on or off |
| `qualitylayer memory mcp` | Serve `memory_search`, `memory_read` and `memory_save` over standard input and output; install registers it with Claude Code and Codex. Pi and OpenCode expose the same tools through their native integrations |
| `qualitylayer memory tool memory_search\|memory_read\|memory_save [json]` | Run one of those tools with its arguments as JSON, for plugins and scripts |
| `qualitylayer memory reindex` | Rebuild the meaning index of every saved lesson |
| `qualitylayer memory retire id` · `memory restore id` | Retire a lesson or explicitly reactivate it |
| `qualitylayer memory pause` · `memory resume` | Pause or resume local capture and task retrieval, preserving saved lessons |
| `qualitylayer memory share on` · `memory share off` | Change your sharing choice for this repository |
| `qualitylayer memory sync` · `memory export` · `memory import` | Exchange eligible lesson records with tracked repository files; all three use the same exchange and make no commits or pushes |
| `qualitylayer memory import-pilot file…` | Import bounded Pilot JSONL/Markdown records as private lessons |

All commands accept `--json`. Page sizes are 1–100; queries are at most 500 characters. Pilot CLI imports accept at most 32 files, each at most 1 MB and 2 MB in total.

</details>

## Session messaging

![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-light.svg)
![Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through](pathname:///img/diagrams/peers-dark.svg)

Claude Code, Codex, Pi and OpenCode sessions on your computer can message each other. Ask one session to ask another for a review, hand over a task or talk a problem through; your agents use `ql-peer` for it. You can run it yourself:

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
