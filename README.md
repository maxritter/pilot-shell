<div align="center">

<img src="docs/site/public/logo.png" alt="QualityLayer" width="120">

# QualityLayer

### The software factory for your coding agents

You approve one plan before any code is written. Your agent builds it test first.<br>
**Then agents that did not write the code check the result against your request.**

[![Stars](https://img.shields.io/github/stars/maxritter/pilot-shell?style=flat&color=F59E0B)](https://github.com/maxritter/pilot-shell)
[![Star History](https://img.shields.io/badge/Star_History-chart-8B5CF6)](https://star-history.com/#maxritter/pilot-shell&Date)
[![Downloads](https://img.shields.io/github/downloads/maxritter/pilot-shell/total?color=3B82F6)](https://github.com/maxritter/pilot-shell/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-2076C5.svg)](https://github.com/maxritter/pilot-shell/pulls)

<p>
  <a href="#install">Install</a> •
  <a href="#why">Why</a> •
  <a href="#how">How it works</a> •
  <a href="#team">Teams</a> •
  <a href="https://qualitylayer.dev/docs/">Docs</a> •
  <a href="https://qualitylayer.dev">Website</a> •
  <a href="https://github.com/maxritter/pilot-shell/releases">Changelog</a>
</p>

**[Download the App](https://qualitylayer.dev/download)** for macOS, Windows or Linux. On a server, in WSL or in a container:

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash
```

**For Claude Code and Codex · terminal, desktop app or IDE · 7-day trial**

</div>

---

> [!TIP]
> **QualityLayer's open design companion:** [Open Claude Design](https://github.com/maxritter/open-claude-design) connects Claude Design to the coding agent you already use, with codebase-grounded creation and conflict-aware synchronization. Together with [Impeccable](https://github.com/pbakaus/impeccable), product context, visual iteration, deterministic checks, and engineering verification work as one design layer.

---

<h2 id="why">Why QualityLayer</h2>

**Coding agents write code fast, but even the best models don't keep a codebase healthy on their own.** Every change passes its tests and still leaves something behind: a copy, a workaround, code nobody reads. Over months, the codebase drifts into something nobody can safely change. Good software still needs people deciding what gets built, before the code exists.

**QualityLayer works inside the agent you already use.** Claude Code or Codex does the work in the terminal, its desktop app or your IDE. You answer in the QualityLayer App, which shows what each question is about:

- **One plan before any code:** the design and each engineering decision as a diagram you can comment on. Then the slices, and the scenarios that prove the change works.
- **One question at a time:** your agent asks each decision in the App, with its recommendation: click a choice, type your own answer, or ask it to tell you more. The last question is the approval of the plan.
- **Designs on your computer:** ask your agent to draw a page, open it full size in the App, and point at what should change. A design is never shared.
- **Built test first:** every task starts with a failing test, and QualityLayer records every test run itself.
- **No waiting while it builds:** when something does not go as planned, your agent takes the recommended way and lists it for you to read afterwards.
- **Checked for you:** agents that did not write the code check every point of your request against the running program. You watch a live checklist and can open the evidence.
- **Only what needs you:** what an agent can check folds into one line of proof, and what only you can confirm is asked at the end.
- **Your team, early:** teammates answer questions about the plan while it is still cheap to change, with their own agent if they like.
- **You stay in charge of cost:** pick the models, and see the time and estimated cost of every step.

QualityLayer is for medium and large changes. When a request is too small for a plan, your agent writes a ready prompt for the plain agent instead.

### From Pilot Shell to QualityLayer

Pilot Shell replaced much of the setup around your agent with its own hooks, rules and tools. Today's models work best with the tools their makers ship, so QualityLayer leaves those alone. It keeps what made Pilot Shell worth using and puts it on top of Claude Code and Codex, or any agent that runs shell commands: one plan you approve, a recorded build, an independent check, and your team in the loop.

---

<h2 id="install">Getting started</h2>

### What you need

**A coding agent.** The App sets up Claude Code and Codex for you. Any other agent that runs shell commands works too: [how to connect it](https://qualitylayer.dev/docs/agents/other).

- **Claude Code:** install with the [native installer](https://code.claude.com/docs/en/quickstart); remove an `npm` or `brew` copy first. Needs a Claude subscription: [Max 5x or 20x](https://claude.com/pricing) for one developer, [Team Premium](https://claude.com/pricing) or [Enterprise](https://claude.com/pricing) for a company.
- **Codex:** install the [Codex CLI](https://developers.openai.com/codex/cli). Needs an OpenAI subscription: [Plus or Pro](https://developers.openai.com/codex/pricing) for one developer, [Business or Enterprise](https://developers.openai.com/codex/pricing) for a company.

Start your agent once before you install, so its folder (`~/.claude` or `~/.codex`) exists.

### Install

One rule: a machine with a screen gets the App; one without gets the command line and opens the App in a browser.

| Machine | Install | Updates |
| --- | --- | --- |
| macOS (Intel, Apple silicon), Windows, Linux desktop | [Download the App](https://qualitylayer.dev/download) and open it. Its first start sets up the command line, your agents and your licence. The terminal installer below does the same and fetches the App. | The App updates itself and its command line together. It checks daily, downloads in the background and shows **Update ready** in the sidebar, with the release notes; on Windows it waits for running agent commands. `qualitylayer update` hands over to the App. |
| WSL2 | The terminal installer inside WSL: command line only. Links open in your Windows browser. | `qualitylayer update` |
| VS Code dev container | The terminal installer in the container: command line only. VS Code forwards the printed link. | `qualitylayer update` |
| Linux server | The terminal installer over SSH: command line only. Forward the port and open the printed link; you pair once, and links carry no key. | `qualitylayer update` |
| Pilot Shell 11, any of the above | Nothing to do: Pilot Shell's updater runs the installer, which moves the machine over by the same rule. | As above |

The terminal installer:

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash      # macOS, Linux, WSL
irm https://qualitylayer.dev/install.ps1 | iex             # Windows PowerShell
```

<details>
<summary><b>What gets installed</b></summary>

The installer downloads the binary for your platform, checks its SHA-256 checksum, then runs `qualitylayer install`, which adds:

- the binary in `~/.qualitylayer/bin/` (on Windows `%USERPROFILE%\.qualitylayer\bin\qualitylayer.exe`, with a `ql.cmd` shortcut)
- the `ql` skill for Claude Code and Codex, which their desktop apps and IDE extensions use too
- the `ql-peers` skill, so agent sessions can message each other
- Codex metadata so the skill runs only when you call it
- a `qualitylayer` link in `~/.local/bin` when that folder is on your `PATH`

It leaves your shell profile alone and adds no MCP server. It turns on the few agent settings QualityLayer needs, only where they are missing, and lists each one it changes. These are high reasoning effort, Claude Code's task tools, Codex's plan tool and, when Codex knows your model's limits, its largest context window. A value you already set stays as it is.

Claude Code also gets a band above the prompt while a review waits for you. QualityLayer sets no status line, so yours stays as it is.

A few hooks keep the App's status of each session current, keep a running build from stopping on a question in the agent's own chat, and record an approval you type in the chat yourself. Session hooks attach agent messaging. The installer records these additions so uninstall can remove them while keeping your own configuration.

</details>

<details>
<summary><b>Update, uninstall and older versions</b></summary>

```bash
qualitylayer update               # on a desktop, hands over to the App
qualitylayer uninstall            # remove exactly what install added
qualitylayer uninstall --purge    # … and the licence and task state
curl -fsSL https://qualitylayer.dev/install.sh | VERSION=12.0.0-beta.1 bash   # a specific release
```

Plans in your repositories stay. Earlier releases are on the [releases page](https://github.com/maxritter/pilot-shell/releases).

</details>

<details>
<summary><b>Coming from Pilot Shell 11</b></summary>

Pilot Shell's updater moves you over, and so does opening the App or running the terminal installer. The move asks nothing: Pilot Shell's own hooks, rules and settings go; the tools it installed and its memories stay, and the report says how to remove them. Your plans carry over, and a paid licence keeps working; without one, your 7-day trial starts.

</details>

### Your first task

Describe a change to your agent in any repository:

```text
/ql retry failed webhooks, and stop after a few tries     # Claude Code
$ql retry failed webhooks, and stop after a few tries     # Codex
```

Or click **+ New** in the App: say what you want, pick the model, the effort and where it starts, and copy one command. Your agent asks each decision in the App, and its terminal shows a single line while it waits. Click a choice, type your own answer, or ask it to tell you more. The last question is "Approve the Plan?". `qualitylayer app` opens the App any time.

After you approve, Implement opens with your Build defaults and one command that starts the build, such as `claude --model opus --effort high "/goal /ql implement retry-webhooks"`. From there your agent works on its own until the final review.

QualityLayer runs only when you ask for it: with `/ql` (`$ql` in Codex), `/ql implement`, or a request to resume a named task. Everything else works as before.

<details>
<summary><b>Privacy</b></summary>

Plans are files in your repository, and the App runs on your computer. A few anonymous events go out with the daily licence check, such as a task started or shipped, a step entered or a check result. Never a repository name, path, branch, title or text. Turn them off in Settings, with `qualitylayer telemetry off`, or with `DO_NOT_TRACK=1`.

Feedback is sent only when you press Send feedback. It becomes one issue in a private repository, with your text, the screenshots you add and diagnostics you can read first. Never code, plan or document text, task titles, repository or branch names, or file paths.

</details>

---

<h2 id="how">How it works</h2>

### Five steps from request to pull request

Every task takes the same five steps. You decide twice: when you approve the plan, and when you approve the finished change.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/flow-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/flow-light.svg" alt="Discuss, Plan, Implement, Verify, Review: you approve at Plan and at Review; your agent works in between" width="1000">
</picture>

- **Discuss:** your agent reads the code and asks one question at a time, each with its recommendation, in a card above the page. The page shows what you decided and what done means. A bug is reproduced and its cause found first.
- **Plan:** the design and each engineering decision as a diagram, then the slices and the scenarios that prove the change works. A second agent reads the plan before it reaches you. The same card takes each decision in turn, then asks "Approve the Plan?".
- **Implement:** the App opens with your Build defaults and one command that starts the build: an orchestrator that writes no code, and workers that build the slices. Every task starts with a failing test. Nothing waits for you: when something does not go as planned, your agent takes the recommended way and lists it under "Decided while building".
- **Verify:** polish and, across a trust boundary, a security review, then agents that did not write the code check every point of your request, on a live checklist.
- **Review:** the App asks the few items left and shows the result to look at. The last question is "Approve the change?", and the pull request opens with its proof.

Each step is one Markdown file in the task's folder, from `01-discuss.md` to `05-review.md`, written for you; the agents' own records go to `agent/`. On GitHub the files read as plain Markdown.

QualityLayer works on the branch and worktree you have checked out and never switches them.

### Built test first, checked by other agents

QualityLayer records every test run itself, with its exit code, so a passing claim always has a run behind it. A slice the plan marks risky gets a checkpoint: its scenarios run on the real program. A failure goes to an agent to fix and never stops the build. Whatever stays open reaches the final review.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/slices-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/slices-light.svg" alt="Slices built test first, two of them side by side, a checkpoint after the risky slice; then polish and security review side by side, then agents check every point" width="1000">
</picture>

While agents check, every check is listed from the start and fills in live.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/screen-verify-dark.png">
  <img src="docs/docusaurus/static/img/diagrams/screen-verify-light.png" alt="The Verify step in the App: Agents are checking, 12 of 22 checks passed, with project checks, scenarios and the points of Done means listed, and Nothing needs you while it checks" width="1000">
</picture>

### The models you choose, the cost you can see

You plan with your best model; Opus 5.5 is the default for Discuss and Plan, and Fable 5.1 can plan and orchestrate too. Workers build on a smaller model, Sonnet 5.5 by default, and start from the written plan, so none of them needs your chat history.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/agents-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/agents-light.svg" alt="You and your agent write the plan; workers build from it; agents that did not write the code check it; another vendor's AI can give a second opinion" width="1000">
</picture>

Settings keeps it short. Planning defaults and Build defaults set the model, the effort and where each session starts, for Claude Code and Codex each, so you can plan with one and build with the other. Independent review picks the model of the agent that never wrote the code and decides whether the change passes, and the second opinion comes from the other coding agent on risky plans. The App shows the time, tokens and estimated cost of every step, with each agent named after its work.

---

<h2 id="app">The QualityLayer App</h2>

The App is where you answer, read and look, on macOS, Windows and Linux. Each step is one page: its document, with the live parts drawn over it, and one line at the top that names what needs you. A pill in the header always says what is going on: an agent at work, a question for you, or your move. The right sidebar holds the task's Comments and its Designs. Close the App, and your tasks keep running: a notification, and the band in Claude Code, tell you when something needs you.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/app-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/app-light.svg" alt="The QualityLayer App: the sidebar, the five step tabs, the step line with Approve, the items that need you, the line of what agents checked, and the plan" width="1000">
</picture>

Each item has its own two answers. Agree or change a decision. Looks right, or change a design. Confirm what only you can confirm. Accept or fix a finding.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/items-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/items-light.svg" alt="Five families of items, each with its answers: Decide, Look, Confirm, Fix and Answer" width="1000">
</picture>

An answer goes to your waiting agent at once; Change on its receipt corrects it. The App never starts, pauses or stops an agent. After you approve the plan, it opens Implement with your Build defaults drawn as the build: the orchestrator, its workers, one effort for both, and one command to copy.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/implement-start-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/implement-start-light.svg" alt="Implement Start: Build with Claude Code, Codex or another agent; the orchestrator and its workers with their models; one effort for both; one command with a Copy button" width="1000">
</picture>

**Designs.** Ask your agent to "mock up the settings page" and it draws one HTML page in your project. The App lists it under Designs, opens it full size, and takes a comment on any spot. The agent changes the same page and says in one line what changed. Designs stay on your computer: never on a share link, the website or a pull request.

Updates arrive quietly: the App checks once a day, downloads in the background and shows an Update ready line with the release notes. Feedback is one click in the sidebar.

---

<h2 id="team">Bring your team in</h2>

With a Team plan, teammates help shape the plan and review the change, each from their own App. Working on your own is just as complete: every feature above works without a team.

**Ask while it is still a plan.** Pick a passage, a diagram, a section or the whole plan, and choose who to ask. They get a Slack message that opens the question in their App, and answer with looks right, a suggested change, or a reply. You get a message when they answer. The answer goes straight to your agent; you decide.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/team-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/team-light.svg" alt="You ask a teammate about a passage; they get a Slack message, answer in their App, and the answer reaches your agent" width="1000">
</picture>

**Answer with your own agent.** A teammate can hand the question to their own coding agent with `/ql answer`. It reads the plan and their code, asks them what it needs, and drafts the answer. Nothing is sent without their yes, and the answer shows which agent wrote it.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/team-agents-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/team-agents-light.svg" alt="A teammate's agent drafts an answer; they send or edit it; the sent answer is marked via Claude Code" width="1000">
</picture>

**Review the change together.** After the build, teammates comment on any line of the finished change, with its proof. Their comments go back to your agent. The code itself is reviewed in your pull request, as always.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/team-change-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/team-change-light.svg" alt="Change review: the team comments on the finished change; open comments go back to your agent, which settles each one" width="1000">
</picture>

The Team space lists the questions waiting for you first, then your questions to others, with a reminder at most every four hours, and what each teammate is working on. People outside the team read and comment through a link, without an account; they cannot approve. The link always shows the task as it stands, with the time it was last updated. Sharing sends the plan and its progress, encrypted on your machine, and never your code or your designs.

### Agent sessions that message each other

Claude Code and Codex sessions on your computer can message each other: Claude to Claude, Codex to Codex, or across. One can ask another for a review, hand over a task, or talk a problem through.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/peers-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/peers-light.svg" alt="Four agent sessions on one computer: one asks another for a review, one hands over a task, two talk a problem through" width="1000">
</picture>

---

## Videos

Two films show it: an overview, and every step in the App. Watch them on the [website](https://qualitylayer.dev/#films), or [scroll through a whole task](https://qualitylayer.dev/#tour).

---

## Documentation

- [Install](https://qualitylayer.dev/docs/install) (with [updates](https://qualitylayer.dev/docs/install#updates)), [your first task](https://qualitylayer.dev/docs/first-task), [other agents](https://qualitylayer.dev/docs/agents/other) and [moving from Pilot Shell 11](https://qualitylayer.dev/docs/moving-from-pilot-shell)
- The five steps: [Discuss](https://qualitylayer.dev/docs/steps/discuss), [Plan](https://qualitylayer.dev/docs/steps/plan), [Implement](https://qualitylayer.dev/docs/steps/implement), [Verify](https://qualitylayer.dev/docs/steps/verify), [Review](https://qualitylayer.dev/docs/steps/review)
- [The App](https://qualitylayer.dev/docs/app), [team plans](https://qualitylayer.dev/docs/team/plans), [teammates' agents](https://qualitylayer.dev/docs/team/agents) and [change review](https://qualitylayer.dev/docs/team/changes)
- [Commands](https://qualitylayer.dev/docs/reference/commands), [settings](https://qualitylayer.dev/docs/reference/settings), and [files and privacy](https://qualitylayer.dev/docs/reference/files)

## Changelog

See [the changelog](https://qualitylayer.dev/docs/changelog) or [GitHub Releases](https://github.com/maxritter/pilot-shell/releases).

## Contributing

Found a bug or missing a feature? [Open an issue](https://github.com/maxritter/pilot-shell/issues).

## License

See [LICENSE](LICENSE).

---

<div align="center">

**The software factory for your coding agents**

Made by [Max Ritter](https://maxritter.net)

</div>

[osai-verify: 8d67182dee08d42091c5]: #
