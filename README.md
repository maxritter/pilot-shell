<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/site/public/brand/qualitylayer-mark.svg">
  <img src="docs/site/public/brand/qualitylayer-mark-light.svg" alt="QualityLayer" width="120">
</picture>

# QualityLayer

### The software factory with you in the loop

**Plan each change visually with your coding agent and your team, then let your agents build it.**<br>
Native integrations for Claude Code, Codex, Pi and OpenCode. Other coding agents use the same workflow through the CLI.

<a href="https://github.com/maxritter/pilot-shell"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/github/stars/maxritter/pilot-shell?style=flat&amp;color=9d6607&amp;labelColor=30363d">
  <img src="https://img.shields.io/github/stars/maxritter/pilot-shell?style=flat&amp;color=9d6607&amp;labelColor=555555" alt="Stars">
</picture></a>
<a href="https://star-history.com/#maxritter/pilot-shell&amp;Date"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/Star_History-chart-6f4fc2?labelColor=30363d">
  <img src="https://img.shields.io/badge/Star_History-chart-6f4fc2?labelColor=555555" alt="Star History">
</picture></a>
<a href="https://github.com/maxritter/pilot-shell/releases"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/github/downloads/maxritter/pilot-shell/total?color=2076c5&amp;labelColor=30363d">
  <img src="https://img.shields.io/github/downloads/maxritter/pilot-shell/total?color=2076c5&amp;labelColor=555555" alt="Downloads">
</picture></a>
<a href="https://github.com/maxritter/pilot-shell/pulls"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/PRs-welcome-2076C5.svg?labelColor=30363d">
  <img src="https://img.shields.io/badge/PRs-welcome-2076C5.svg?labelColor=555555" alt="PRs Welcome">
</picture></a>

<p>
  <a href="#install">Install</a> •
  <a href="#features">Features</a> •
  <a href="https://qualitylayer.dev/docs/">Docs</a> •
  <a href="https://qualitylayer.dev">Website</a> •
  <a href="https://qualitylayer.dev/docs/changelog">Changelog</a>
</p>

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash
```

**macOS · Windows · Linux**, or [download the App](https://qualitylayer.dev/download). 7-day trial.

<br>

<a href="https://qualitylayer-media.max-ritter.workers.dev/overview.mp4"><img src="docs/img/film-poster.webp" alt="Play the film: How QualityLayer works, 5 minutes" width="700"></a>

</div>

---

## Why QualityLayer

> “With QualityLayer, developing software with agents finally feels like doing real engineering again.”
>
> *An engineer who uses QualityLayer*

**Coding agents write code fast**, but each change still leaves copies, workarounds and dead code behind. QualityLayer puts you back in the loop while the change is still a plan:

- Your agent reads the code and draws up one plan: the architecture as diagrams, the screens as clickable designs, each decision with its reasons.
- You comment on any part and approve the plan before anything changes; with a Team plan, your teammates comment too.
- Your agent builds it in small slices, each starting with a failing test.
- Agents that did not write the code check every point of your request against the running program.
- Your agent settles routine choices and records them; only real decisions reach you.
- Every step shows its time and estimated cost.
- It runs on your own subscription, and each step is one Markdown file in your repository.

Made for medium and large changes. Small requests keep a short Plan and one slice; ask for a ready prompt if you prefer your plain agent.

---

<h2 id="install">Getting Started</h2>

### Prerequisites

- **A coding agent**, ready to run shell commands in your repository: Claude Code, Codex, Pi, OpenCode, or [any other agent](https://qualitylayer.dev/docs/agents/other). The four native integrations also work in the App.
- **Your own subscription** (Claude or ChatGPT plan, or API key). QualityLayer never charges for model usage.
- **Git** and a repository.

### Installation

**[Download the App](https://qualitylayer.dev/download)** and open it. Setup activates your licence or starts the trial, installs the `qualitylayer` command and connects your agents. On a server, in WSL or in a container:

```bash
curl -fsSL https://qualitylayer.dev/install.sh | bash      # macOS, Linux, WSL
irm https://qualitylayer.dev/install.ps1 | iex             # Windows PowerShell
```

The App updates itself; without it, run `qualitylayer update`. [Installation guide](https://qualitylayer.dev/docs/install).

<details>
<summary><b>Uninstalling</b></summary>

`qualitylayer uninstall` undoes what the installer changed; your plans stay. On Windows, even when the App is gone:

```powershell
& ([scriptblock]::Create((irm https://qualitylayer.dev/install.ps1))) -Uninstall
```

</details>

<details>
<summary><b>Coming from Pilot Shell 11</b></summary>

Its updater moves you over with your plans and licence. [Moving from Pilot Shell](https://qualitylayer.dev/docs/moving-from-pilot-shell).

</details>

### First Steps

```text
/ql retry failed webhooks, and stop after a few tries     # Claude Code
$ql retry failed webhooks, and stop after a few tries     # Codex
/skill:ql retry failed webhooks, and stop after a few tries # Pi
/ql retry failed webhooks, and stop after a few tries     # OpenCode
```

Answer your agent's questions in the App, approve the Plan, then start the build. Your agent continues through Outline, Implement and Verify until Review. Human-only prerequisites and blocked checks stay unverified for your decision there. QualityLayer runs only when you ask for it. [Your first task](https://qualitylayer.dev/docs/first-task).

Choose the agent, model, effort and workspace when starting a task or build. **In the App** opens the task's **Agent** conversation beside **Files** and **Feedback**; **In my terminal** gives you the launch command. Settings keeps global run controls and review models. [Supported agents](https://qualitylayer.dev/docs/agents/native).

---

<h2 id="features">The Workflow</h2>

Each of the first seven steps writes one Markdown file. You approve twice: the plan and the finished change. QualityLayer never merges and pushes only with your approval.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/flow-pr-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/flow-pr-light.svg" alt="Discuss, Research, Plan, Outline, Implement, Verify, Review and the pull request: you approve at Plan and at Review and merge the pull request; your agent works in between" width="1000">
</picture>

| Step | What happens |
|---|---|
| [Discuss](https://qualitylayer.dev/docs/steps/discuss) | Settles what done means and clarifies a bug report |
| [Research](https://qualitylayer.dev/docs/steps/research) | Agents read how your code works today; a bug is reproduced and diagnosed here |
| [Plan](https://qualitylayer.dev/docs/steps/plan) | Design, diagrams and checks, **approved by you** |
| [Outline](https://qualitylayer.dev/docs/steps/outline) | The build session splits the approved Plan into small slices |
| [Implement](https://qualitylayer.dev/docs/steps/implement) | Each slice starts with a failing test |
| [Verify](https://qualitylayer.dev/docs/steps/verify) | Every point of your request, with its evidence |
| [Review](https://qualitylayer.dev/docs/steps/review) | A walkthrough of the change, **approved by you** |
| [Pull request](https://qualitylayer.dev/docs/steps/pull-request) | Failing checks fixed; the task stays open until you merge |

### Two levels

Engineering (default) starts from a technical plan, Product from a brief that becomes a PRD. Pick one at Setup, change it in Settings › Workflow, or per task in the task header. [How they differ](https://qualitylayer.dev/docs/#two-levels).

## Designs

Ask your agent for a mockup, diagram or clickable design. Compare versions in the App, pin feedback and restore earlier versions. Keep the designs every task builds on in your repository. [Designs](https://qualitylayer.dev/docs/designs).

## QualityLayer App

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/site/public/product/plan-dark.webp">
  <img src="docs/site/public/product/plan-light.webp" alt="The Plan step in the App for a fictional task, usage-based billing across nine services: the design, its decisions and the Approve Plan button" width="1000">
</picture>

- Answer your agent's questions and comment on any passage; answers reach it at once.
- Follow every task with what needs you shown first, plus time and cost per step.
- Choose model, effort and workspace at launch. Keep standing instructions, reviewer models and general run controls in [Settings](https://qualitylayer.dev/docs/reference/settings).
- Work beside your agent in the **Agent** sidebar. Closing the sidebar keeps its session running.
- Your agents reuse lessons from earlier tasks, and can share them through Git. [Project memory](https://qualitylayer.dev/docs/memory).
- With a Team plan, ask a teammate about any passage over Slack, and let them review the finished change. [Team plans](https://qualitylayer.dev/docs/team/plans).

Your code and usage data stay on your computer; shared tasks are encrypted first. [Files and privacy](https://qualitylayer.dev/docs/reference/files#privacy).

[Explore the App →](https://qualitylayer.dev/docs/app)

---

## Documentation

For every step, [command](https://qualitylayer.dev/docs/reference/commands) and [setting](https://qualitylayer.dev/docs/reference/settings), see the **[Documentation](https://qualitylayer.dev/docs/)**.

---

## Changelog

See [the changelog](https://qualitylayer.dev/docs/changelog) or [GitHub Releases](https://github.com/maxritter/pilot-shell/releases).

---

## Contributing

Found a bug or missing a feature? [Open an issue](https://github.com/maxritter/pilot-shell/issues).

---

## License

See [LICENSE](LICENSE).

---

<div align="center">

**The software factory with you in the loop**

Made by [Max Ritter](https://maxritter.net)

</div>

[osai-verify: 8d67182dee08d42091c5]: #
