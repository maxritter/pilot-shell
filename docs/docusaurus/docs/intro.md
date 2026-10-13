---
slug: /
title: Overview
description: QualityLayer takes your coding agent from a request to a merged pull request in eight steps, and shows you where you decide.
---

<figure class="ql-film">
  <video controls preload="none" playsinline poster="https://qualitylayer-media.max-ritter.workers.dev/overview.webp" src="https://qualitylayer-media.max-ritter.workers.dev/overview.mp4"></video>
  <figcaption>How QualityLayer works, in about five minutes: the problem it solves, the steps, and working on your own or with your team.</figcaption>
</figure>

QualityLayer takes your coding agent from a request to a merged pull request in eight steps. You agree on a plan before any code is written. Your agent builds it in small tested slices, and agents that did not write the code check the result against your request. You answer and approve in the **QualityLayer App**.

![The QualityLayer App at the Plan step: the step track across the top, the Plan with a diagram in the middle, Approve Plan and Give feedback at the top right, and Files and Comments on the right](pathname:///img/app/plan-light.webp)
![The QualityLayer App at the Plan step: the step track across the top, the Plan with a diagram in the middle, Approve Plan and Give feedback at the top right, and Files and Comments on the right](pathname:///img/app/plan-dark.webp)

*Example task in a fictional project.*

**Start here:** [Install](install.md) · [Your first task](first-task.md) · [The App](app.md) · [The eight steps](steps/discuss.md) · [Designs](designs.md)

## The eight steps {#the-seven-steps}

Every task takes the same steps, in order. The first seven each write one document; the last follows the pull request until it is merged. You approve twice: the Plan, and the finished change.

![The eight steps: Discuss, Research, Plan, Outline, Implement, Verify, Review and the pull request. You approve the Plan and the finished change and merge the pull request; your agent does the rest](pathname:///img/diagrams/flow-pr-light.svg)
![The eight steps: Discuss, Research, Plan, Outline, Implement, Verify, Review and the pull request. You approve the Plan and the finished change and merge the pull request; your agent does the rest](pathname:///img/diagrams/flow-pr-dark.svg)

| Step | What happens |
| --- | --- |
| **[Discuss](steps/discuss.md)** | Your agent asks, in batches, until it knows what you want and what done means |
| **[Research](steps/research.md)** | Agents read the code without your request in front of them; you settle what it leaves open |
| **[Plan](steps/plan.md)** | The decided design, with diagrams where they help. You approve it once, before any code |
| **[Outline](steps/outline.md)** | Your agent cuts the Plan into slices while you read it. Nothing to approve |
| **[Implement](steps/implement.md)** | One command starts the build, in small slices, each tested |
| **[Verify](steps/verify.md)** | Six checks, including agents that did not write the code |
| **[Review](steps/review.md)** | You settle what is left and approve; the pull request opens |
| **[Pull request](steps/pull-request.md)** | Your agent watches the checks and fixes failures, up to three times; QualityLayer follows the reviewers. You merge it, and the task closes |

A bug takes the same steps. Its cause is found in Research, before anything is planned.

## Who it is for

Medium and large changes in a repository you care about, on your own or with your team. When a request is too small for a plan, your agent closes the task and hands you a ready prompt for your plain agent.

It works with Claude Code and Codex, in the terminal, their desktop apps or your IDE, and with [any other agent](agents/other.md) that runs shell commands. Your agent writes the code on the subscription you already have.

## Two levels

Pick your level at **Setup** on the first start; change it any time in **Settings › Workflow**. The task header shows each task's level: change it there until you approve the Plan, or read the task as the other level at any time.

| | Engineering (default) | Product |
| --- | --- | --- |
| For | Engineers | Product owners, product managers, leadership |
| A task starts as | The full technical plan | A product brief |
| Discuss settles | The problem, what done means, the scope, a first look at the code | The problem, success measure, first release, what the user sees, what you are not doing |
| Discuss becomes | A request with numbered points of what done means | A PRD for Confluence, Google Docs or Jira |
| The Plan shows | Each decision with its diagram, plus contracts, patterns, files and tests | What changes for the user, and why |
| Folded away | Nothing: every section is open | Engineering detail, one click away under **More in this document** |
| Build, Verify, Review | The same | The same |

Both levels take the same steps and write the same files.

## How it fits together {#how-it-fits-together}

Everything runs on your computer. Your agent works through the **QualityLayer CLI**, which keeps each task as Markdown files in your repository. The **App** shows the same files. Sharing is optional: a Plan you share with your team or by link is encrypted on your computer first. The server at qualitylayer.dev never sees your plans or comments ([your data](reference/files.md#privacy)).

![How QualityLayer fits together: on your computer, your agent runs the QualityLayer CLI, which keeps each task in Markdown files in your repository, and the QualityLayer App reads the same files; only when you share, plans and comments go to the QualityLayer Server at qualitylayer.dev, encrypted, for your team and for people with a share link](pathname:///img/diagrams/architecture-light.svg)
![How QualityLayer fits together: on your computer, your agent runs the QualityLayer CLI, which keeps each task in Markdown files in your repository, and the QualityLayer App reads the same files; only when you share, plans and comments go to the QualityLayer Server at qualitylayer.dev, encrypted, for your team and for people with a share link](pathname:///img/diagrams/architecture-dark.svg)

The documents, `01-discuss.md` to `07-review.md`, are yours: committed with the change and kept when you uninstall ([what each holds](reference/files.md#documents)).

## Coming from plan mode in your IDE {#from-plan-mode}

Keep reading each change in your IDE's diff. QualityLayer adds three things around it:

| Plan mode | With QualityLayer |
| --- | --- |
| A plan in the chat | A Plan with mockups and diagrams that you and your team comment on, approved once |
| One long build | Tested slices from the approved Plan |
| You check the result | Agents that did not write the code check every point you agreed on; you settle what is left |
