---
slug: /
title: Overview
description: Your agent plans, builds and checks a change in eight steps, from request to merged pull request. You decide at the Plan and at the result.
---

<figure class="ql-film">
  <video controls preload="none" playsinline poster="https://qualitylayer-media.max-ritter.workers.dev/overview-v2026102001.webp" src="https://qualitylayer-media.max-ritter.workers.dev/overview-v2026102001.mp4"></video>
  <figcaption>How QualityLayer works, in about five minutes.</figcaption>
</figure>

**Quality by design.** QualityLayer is the software factory with you in the loop. The task is on the left and your agent in the right sidebar, in the App or your browser. Your agent reads the code and plans each change with you: architecture as diagrams, screens as clickable artifacts, every decision in the open. You approve the Plan before any code. Your agent then builds test first and opens a pull request, and agents that did not write the code check the result against your request.

![The visual Plan: request retries, replay and a write-once ledger, with Approve Plan](pathname:///img/app/plan-light.webp)
![The visual Plan: request retries, replay and a write-once ledger, with Approve Plan](pathname:///img/app/plan-dark.webp)

*Example task in a fictional project.*

**Start here:** [Install](install.md) · [Your first task](first-task.md) · [The App](app.md) · [Workflow](steps/discuss.md) · [Artifacts](artifacts.md)

## The eight steps {#the-seven-steps}

The first seven steps each write one document. You approve twice: the Plan, then the finished change. After you start the build, your agent runs Outline, Implement and Verify without workflow questions. Anything only you can do waits for Review.

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
| **[Review](steps/review.md)** | You settle what is left and approve. Opening a pull request is optional |
| **[Pull request](steps/pull-request.md)** | Your agent fixes failing checks, up to three times. You merge |

## Who it is for

Medium and large changes, alone or with a team.

- **Seven agents** run beside your task through [native integrations](agents/native.md): Claude Code, Codex, Cursor, Grok, Antigravity, Pi and OpenCode.
- **[Other coding agents](agents/other.md)** use the same workflow through the CLI.
- Your agent keeps its own login and provider settings.

## Two levels

Pick a level at **Setup**. Change it in **Settings › Workflow**, or per task in the task header until you approve its Plan.

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
