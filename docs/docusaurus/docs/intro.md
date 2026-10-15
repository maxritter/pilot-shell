---
slug: /
title: Overview
description: QualityLayer takes your coding agent from a request to a merged pull request in eight steps, and shows you where you decide.
---

<figure class="ql-film">
  <video controls preload="none" playsinline poster="https://qualitylayer-media.max-ritter.workers.dev/overview.webp" src="https://qualitylayer-media.max-ritter.workers.dev/overview.mp4"></video>
  <figcaption>How QualityLayer works, in about five minutes.</figcaption>
</figure>

QualityLayer is the software factory with you in the loop. Your agent reads the code and plans each change with you in the **App**: the architecture as diagrams, the screens as clickable designs, every decision in the open. Once you and your team agree on the plan, your agent builds it test first and takes it to a pull request; agents that did not write the code check the result against your request.

![The QualityLayer App at the Plan step: the step track, the Plan with a diagram, and Approve Plan and Give feedback at the top right](pathname:///img/app/plan-light.webp)
![The QualityLayer App at the Plan step: the step track, the Plan with a diagram, and Approve Plan and Give feedback at the top right](pathname:///img/app/plan-dark.webp)

*Example task in a fictional project.*

**Start here:** [Install](install.md) · [Your first task](first-task.md) · [The App](app.md) · [The eight steps](steps/discuss.md) · [Designs](designs.md)

## The eight steps {#the-seven-steps}

Each of the first seven steps writes one document. You approve twice: the Plan, and the finished change.

![The eight steps from Discuss to the pull request; you approve the Plan and the finished change, and merge](pathname:///img/diagrams/flow-pr-light.svg)
![The eight steps from Discuss to the pull request; you approve the Plan and the finished change, and merge](pathname:///img/diagrams/flow-pr-dark.svg)

| Step | What happens |
| --- | --- |
| **[Discuss](steps/discuss.md)** | Your agent asks until it knows what done means |
| **[Research](steps/research.md)** | Agents read the code; a bug's cause is found here |
| **[Plan](steps/plan.md)** | The design, with diagrams. You approve it before any code |
| **[Outline](steps/outline.md)** | Your agent cuts the Plan into slices. Nothing to approve |
| **[Implement](steps/implement.md)** | One command starts the build, in small tested slices |
| **[Verify](steps/verify.md)** | Six checks, including agents that did not write the code |
| **[Review](steps/review.md)** | You settle what is left and approve; the pull request opens |
| **[Pull request](steps/pull-request.md)** | Your agent fixes failing checks, up to three times. You merge |

## Who it is for

Medium and large changes, solo or with a team, in Claude Code, Codex or [any other agent](agents/other.md) that runs shell commands, on the subscription you already have.

## Two levels

Pick a level at **Setup**; change it in **Settings › Workflow**, or per task in the task header until you approve its Plan.

| | Engineering (default) | Product |
| --- | --- | --- |
| For | Engineers | Product owners, managers, leadership |
| Discuss becomes | Numbered points of what done means | A PRD for Confluence, Google Docs or Jira |
| The Plan shows | Each decision with its diagram, contracts, files and tests | What changes for the user; engineering detail one click away |

Both levels take the same steps and write the same files.

## How it fits together {#how-it-fits-together}

![On your computer, your agent runs the QualityLayer CLI, which keeps each task in Markdown files in your repository, and the App reads the same files; only shared plans and comments go to the QualityLayer server, encrypted](pathname:///img/diagrams/architecture-light.svg)
![On your computer, your agent runs the QualityLayer CLI, which keeps each task in Markdown files in your repository, and the App reads the same files; only shared plans and comments go to the QualityLayer server, encrypted](pathname:///img/diagrams/architecture-dark.svg)

The task documents, `01-discuss.md` to `07-review.md`, live in your repository and stay when you uninstall ([what each holds](reference/files.md#documents)). Anything you share is encrypted on your computer first ([your data](reference/files.md#privacy)).

## Coming from plan mode in your IDE {#from-plan-mode}

| Plan mode | With QualityLayer |
| --- | --- |
| A plan in the chat | A Plan with mockups and diagrams your team can comment on |
| One long build | Tested slices from the approved Plan |
| You check the result | Agents that did not write the code check every point you agreed on |
