<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/site/public/brand/qualitylayer-mark.svg">
  <img src="docs/site/public/brand/qualitylayer-mark-light.svg" alt="QualityLayer" width="120">
</picture>

# QualityLayer

## The software factory with you in the loop

**Plan each change visually, then let your agents build and verify it.**<br>
Work side by side in the App or browser, or use your favourite terminal or IDE.

<a href="https://github.com/maxritter/qualitylayer"><img src="https://img.shields.io/github/stars/maxritter/qualitylayer?style=flat&amp;color=9d6607&amp;labelColor=30363d" alt="Stars"></a>
<a href="https://star-history.com/#maxritter/qualitylayer&amp;Date"><img src="https://img.shields.io/badge/Star_History-chart-6f4fc2?labelColor=30363d" alt="Star History"></a>
<a href="https://github.com/maxritter/qualitylayer/releases"><img src="https://img.shields.io/github/downloads/maxritter/qualitylayer/total?color=2076c5&amp;labelColor=30363d" alt="Downloads"></a>
<a href="https://github.com/maxritter/qualitylayer/pulls"><img src="https://img.shields.io/badge/PRs-welcome-2076C5.svg?labelColor=30363d" alt="PRs Welcome"></a>

<p>
  <a href="#install">Install</a> •
  <a href="#features">Features</a> •
  <a href="https://qualitylayer.dev/docs/">Docs</a> •
  <a href="https://qualitylayer.dev">Website</a> •
  <a href="https://qualitylayer.dev/docs/changelog">Changelog</a>
</p>

**[Download the App](https://qualitylayer.dev/download)** for macOS, Windows or Linux. 7-day trial.

<br>

<a href="https://qualitylayer-media.max-ritter.workers.dev/overview-v2026102001.mp4" aria-label="Watch the QualityLayer walkthrough, 5 minutes 20 seconds"><img src="docs/img/film-poster-dark.webp" alt="Play video: QualityLayer’s seven-step workflow, 5 minutes 20 seconds" width="700"></a>

**[▶ Watch the 5:20 walkthrough](https://qualitylayer-media.max-ritter.workers.dev/overview-v2026102001.mp4)**

</div>

---

## Why QualityLayer

> “With QualityLayer, developing software with agents finally feels like doing real engineering again.”
>
> *An engineer who uses QualityLayer*

QualityLayer keeps design decisions and verification visible while your agents work.

| You get | How it works |
| --- | --- |
| **Your own agent and plan** | Claude Code, Codex, Cursor and four more run on the subscription or API key you already have. QualityLayer never charges for AI usage. |
| **A design you can review** | Comment on diagrams and clickable screens, then approve the Plan before code changes. |
| **Small, tested changes** | Your agent builds in slices, each starting with a failing test. |
| **An independent check** | Agents that did not write the code check it against your request. Anything they cannot verify stays open for your decision. |
| **Code health checks** | Local checks flag complex functions and deeply nested code for your agent to review. Ask for a wider check to find duplication. [Code health](https://qualitylayer.dev/docs/reference/code-health). |
| **Visible decisions and effort** | Each step records its decisions and results in your repository, with time and estimated model cost shown in the App. |

Made for medium and large changes. Small requests keep a short Plan and one slice; ask for a ready prompt if you prefer your plain agent.

---

<h2 id="install">Getting Started</h2>

### Prerequisites

- **A coding agent:** Claude Code, Codex, Cursor, Grok, Antigravity, Pi or OpenCode, installed and signed in. Choose it in the App or browser. [Other agents](https://qualitylayer.dev/docs/agents/other) connect through the CLI.
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

Run `pilot update` to install QualityLayer v12, or download it directly. Keep Pilot Shell 11 alongside it until you are ready to remove it; your paid licence works with both. Import memories per project when you are ready. [Moving from Pilot Shell](https://qualitylayer.dev/docs/moving-from-pilot-shell).

</details>

### First Steps

In the App or browser, choose **+ New**, pick your repository and agent, and describe the change:

```text
Plan retries for failed webhooks and stop after a few tries.
```

1. Answer your agent's questions and comment on the Plan beside its conversation.
2. Approve the Plan and start the build. Your agent continues through Outline, Implement and Verify.
3. Review the result and its evidence. Checks that need you, or could not run, stay open for your decision.

| Where you work | How to start |
| --- | --- |
| **App or browser** | Choose **In the App** to keep the agent beside the task. |
| **Your terminal or IDE** | Choose **In my terminal** to copy the request, or ask there: “Using QualityLayer, plan retries for failed webhooks.” |
| **Another agent** | Agents that run shell commands can use the CLI. [Supported agents](https://qualitylayer.dev/docs/agents/native). |

To continue elsewhere, stop the active run, then ask: “Using QL, continue verification of task retry-webhooks.” Your Plan, changes and evidence stay with the task.

QualityLayer runs only when you ask for it. [Your first task](https://qualitylayer.dev/docs/first-task).

---

<h2 id="features">The Workflow</h2>

Each step writes a Markdown file in your repository. Read questions, decisions and results in the App. You approve the Plan and the finished change; QualityLayer pushes only with your approval and leaves merging to you.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/docusaurus/static/img/diagrams/flow-pr-dark.svg">
  <img src="docs/docusaurus/static/img/diagrams/flow-pr-light.svg" alt="Discuss, Research, Plan, Outline, Implement, Verify, Review and the pull request: you approve at Plan and at Review and merge the pull request; your agent works in between" width="1000">
</picture>

| Step | What happens |
|---|---|
| [Discuss](https://qualitylayer.dev/docs/steps/discuss) | Settles what done means and clarifies a bug report |
| [Research](https://qualitylayer.dev/docs/steps/research) | Agents read how your code works today; a bug is reproduced and diagnosed here |
| [Plan](https://qualitylayer.dev/docs/steps/plan) | Diagrams, clickable artifacts and checks, **approved by you** |
| [Outline](https://qualitylayer.dev/docs/steps/outline) | The build session splits the approved Plan into small slices |
| [Implement](https://qualitylayer.dev/docs/steps/implement) | Each slice starts with a failing test |
| [Verify](https://qualitylayer.dev/docs/steps/verify) | Every point of your request, with its evidence |
| [Review](https://qualitylayer.dev/docs/steps/review) | A walkthrough of the change, **approved by you** |
| [Pull request](https://qualitylayer.dev/docs/steps/pull-request) | Failing checks fixed; the task stays open until you merge |

### Two levels

**Engineering** starts with a technical plan. **Product** starts with a brief that becomes a product requirements document. Choose at Setup or change it in Settings › Workflow or the task header. [How they differ](https://qualitylayer.dev/docs/#two-levels).

## Artifacts

An artifact is a mockup, diagram or clickable page your agent draws, so you can try a flow before any code exists. Click a spot to say what should change; your agent edits the page and answers. Keep the ones every task builds on in your repository. [Artifacts](https://qualitylayer.dev/docs/artifacts).

<a href="docs/site/public/product/artifact-dark.webp">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/site/public/product/artifact-dark.webp">
    <img src="docs/site/public/product/artifact-light.webp" alt="A queue migration console drawn as an artifact, with pinned comments and the agent's reply beside it. Fictional project." width="1000">
  </picture>
</a>

## QualityLayer App

<a href="docs/site/public/product/plan-dark.webp">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/site/public/product/plan-dark.webp">
    <img src="docs/site/public/product/plan-light.webp" alt="A billing architecture diagram beside Claude Code’s conversation in QualityLayer. Fictional project." width="1000">
  </picture>
</a>

| In the App | What you can do |
| --- | --- |
| **Agent workspace** | Read artifacts beside the conversation. Answer questions and pin feedback. |
| **Run controls** | Choose agent, model, effort, permission mode and branch. Seven agents run in their own terminals, with their own sign-in. |
| **Plan limits** | See how much of your Claude Code and Codex plans is left, and when each window resets. |
| **Files and Review** | See the branch and what changed, and open any file in VS Code, Cursor, Zed, Finder or Terminal. |
| **Settings** | Agents, usage, sessions, notifications, editor, appearance and the update channel. [Settings](https://qualitylayer.dev/docs/reference/settings). |
| **Project memory** | Reuse lessons across tasks and share them through Git. [Project memory](https://qualitylayer.dev/docs/memory). |
| **Team review** | Ask teammates over Slack and review shared work with a [Team plan](https://qualitylayer.dev/docs/team/plans). |

QualityLayer keeps task files on your computer and encrypts shared tasks first. Your coding agent uses its own provider. [Files and privacy](https://qualitylayer.dev/docs/reference/files#privacy).

[Explore the App →](https://qualitylayer.dev/docs/app)

---

## Documentation

Guides for [getting started](https://qualitylayer.dev/docs/), [commands](https://qualitylayer.dev/docs/reference/commands) and [settings](https://qualitylayer.dev/docs/reference/settings).

---

## Changelog

See [the changelog](https://qualitylayer.dev/docs/changelog) or [GitHub Releases](https://github.com/maxritter/qualitylayer/releases).

---

## Contributing

Found a bug or missing a feature? [Open an issue](https://github.com/maxritter/qualitylayer/issues).

---

## License

See [LICENSE](LICENSE).

---

<div align="center">

**Quality by design.** The software factory with you in the loop.

Made by [Max Ritter](https://maxritter.net)

</div>

[osai-verify: 8d67182dee08d42091c5]: #
