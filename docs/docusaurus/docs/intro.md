---
slug: /
title: Overview
description: QualityLayer takes your coding agent from a request to a merged pull request in eight steps, and shows you where you decide.
---

<figure class="ql-film">
  <video controls preload="none" playsinline poster="https://qualitylayer-media.max-ritter.workers.dev/overview-v20261020.webp" src="https://qualitylayer-media.max-ritter.workers.dev/overview-v20261020.mp4"></video>
  <figcaption>How QualityLayer works, in about five minutes.</figcaption>
</figure>

**Quality by design.** QualityLayer is the software factory with you in the loop. Use the **App or browser**, with the task on the left and your agent in the right sidebar. Your agent reads the code and plans each change with you: the architecture as diagrams, the screens as clickable designs, every decision in the open. Once you and your team agree on the plan, your agent builds it test first and takes it to a pull request; agents that did not write the code check the result against your request.

![The visual Plan: request retries, replay and a write-once ledger, with Approve Plan](pathname:///img/app/plan-light.webp)
![The visual Plan: request retries, replay and a write-once ledger, with Approve Plan](pathname:///img/app/plan-dark.webp)

*Example task in a fictional project.*

**Start here:** [Install](install.md) · [Your first task](first-task.md) · [The App](app.md) · [Workflow](steps/discuss.md) · [Artifacts](artifacts.md)

## The eight steps {#the-seven-steps}

Each of the first seven steps writes one document. You approve twice: the Plan, and the finished change. After you start the build, your agent continues through Outline, Implement and Verify without workflow questions. Human-only prerequisites and blocked checks stay unverified for Review.

![The eight steps from Discuss to the pull request; you approve the Plan and the finished change, and merge](pathname:///img/diagrams/flow-pr-light.svg)
![The eight steps from Discuss to the pull request; you approve the Plan and the finished change, and merge](pathname:///img/diagrams/flow-pr-dark.svg)

| Step | What happens |
| --- | --- |
| **[Discuss](steps/discuss.md)** | Your agent asks until it knows what done means |
| **[Research](steps/research.md)** | Agents read the code; a bug's cause is found here |
| **[Plan](steps/plan.md)** | The artifact, with diagrams. You approve it before any code |
| **[Outline](steps/outline.md)** | Your agent cuts the Plan into slices. Nothing to approve |
| **[Implement](steps/implement.md)** | Your agent builds the approved Plan in small tested slices |
| **[Verify](steps/verify.md)** | Six checks, including agents that did not write the code |
| **[Review](steps/review.md)** | You settle what is left and approve; opening a pull request is optional |
| **[Pull request](steps/pull-request.md)** | Your agent fixes failing checks, up to three times. You merge |

## Who it is for

Use it for medium and large changes, solo or with a team. Claude Code, Codex, Pi and OpenCode run beside your task in the App or browser through [native integrations](agents/native.md). [Other coding agents](agents/other.md) use the same workflow through the CLI. Your agent keeps its own login and provider settings.

## Two levels

Pick a level at **Setup**; change it in **Settings › Workflow**, or per task in the task header until you approve its Plan.

| | Engineering (default) | Product |
| --- | --- | --- |
| For | Engineers | Product owners, managers, leadership |
| Discuss becomes | Numbered points of what done means | A PRD for Confluence, Google Docs or Jira |
| The Plan shows | Each decision with its diagram, contracts, files and tests | What changes for the user; engineering detail one click away |

Both levels take the same steps and write the same files.

## How it fits together {#how-it-fits-together}

![QualityLayer in the App or browser: your task on the left, your agent on the right. Task files stay in your repository; the CLI also connects external agents. Shared plans and comments reach the server encrypted](pathname:///img/diagrams/architecture-light.svg)
![QualityLayer in the App or browser: your task on the left, your agent on the right. Task files stay in your repository; the CLI also connects external agents. Shared plans and comments reach the server encrypted](pathname:///img/diagrams/architecture-dark.svg)

The task documents, `01-discuss.md` to `07-review.md`, live in your repository and stay when you uninstall ([what each holds](reference/files.md#documents)). Anything you share is encrypted on your computer first ([your data](reference/files.md#privacy)).

## Coming from plan mode in your IDE {#from-plan-mode}

| Plan mode | With QualityLayer |
| --- | --- |
| A plan in the chat | A Plan with mockups and diagrams your team can comment on |
| One long build | Tested slices from the approved Plan |
| You check the result | Agents that did not write the code check every point you agreed on |
