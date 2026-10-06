---
slug: /
title: Overview
description: How QualityLayer takes your coding agent from a request to a reviewed change, and where you decide along the way.
---

<figure class="ql-film">
  <video controls preload="none" playsinline poster="https://qualitylayer-media.max-ritter.workers.dev/overview.webp" src="https://qualitylayer-media.max-ritter.workers.dev/overview.mp4"></video>
  <figcaption>How QualityLayer works, in about four minutes: the problem it solves, the five steps, and working on your own or with your team.</figcaption>
</figure>

QualityLayer runs your coding agent through a proper engineering process and keeps the experienced engineer in the loop, where their judgement counts. You agree on a plan before any code is written, the agent builds it in small tested slices, and agents that did not write the code check the result. Your agent asks each decision; the **QualityLayer App** beside it shows what the question is about.

![The QualityLayer App: the sidebar, the five step tabs, the step line with Approve, the items that need you, the line of what agents checked, and the Plan](pathname:///img/diagrams/app-light.svg)
![The QualityLayer App: the sidebar, the five step tabs, the step line with Approve, the items that need you, the line of what agents checked, and the Plan](pathname:///img/diagrams/app-dark.svg)

**Start here:** [Install](install.md) · [Your first task](first-task.md) · [The App](app.md) · [The five steps](steps/discuss.md)

## How it fits together {#how-it-fits-together}

Everything runs on your computer. Your agent works through the **QualityLayer CLI**, which keeps each task in plain Markdown files in your repository. The **QualityLayer App** reads the same files and shows them to you. When you share a Plan with your team or by link, it is encrypted on your computer first, so the **QualityLayer Server** at qualitylayer.dev only stores what it cannot read.

![How QualityLayer fits together: on your computer, your agent runs the QualityLayer CLI, which keeps each task in Markdown files in your repository, and the QualityLayer App reads the same files; only encrypted plans, comments and asks go to the QualityLayer Server at qualitylayer.dev, for your team and for people with a share link](pathname:///img/diagrams/architecture-light.svg)
![How QualityLayer fits together: on your computer, your agent runs the QualityLayer CLI, which keeps each task in Markdown files in your repository, and the QualityLayer App reads the same files; only encrypted plans, comments and asks go to the QualityLayer Server at qualitylayer.dev, for your team and for people with a share link](pathname:///img/diagrams/architecture-dark.svg)

The files are yours, committed with the change, and they stay when you uninstall ([what each file holds](reference/files.md)). Your agent calls the CLI at every step; the [command reference](reference/commands.md) lists its commands.

## The five steps {#the-five-steps}

Every task takes the same five steps. You approve twice: the Plan before any code, and the finished change.

![The five steps: Discuss, Plan, Implement, Verify and Review. You approve the Plan and the finished change; your agent does the rest](pathname:///img/diagrams/flow-light.svg)
![The five steps: Discuss, Plan, Implement, Verify and Review. You approve the Plan and the finished change; your agent does the rest](pathname:///img/diagrams/flow-dark.svg)

| Step | What happens |
| --- | --- |
| **[Discuss](steps/discuss.md)** | Your agent asks until it knows what you want and what done means |
| **[Plan](steps/plan.md)** | Mockups and diagrams where they help; you approve it before any code |
| **[Implement](steps/implement.md)** | One command starts the build: small slices, each tested |
| **[Verify](steps/verify.md)** | Agents that did not write the code check every point |
| **[Review](steps/review.md)** | You settle what is left and approve; the pull request opens |

A bug takes the same steps. Its cause is found before anything is planned.

## Who it is for

Medium to large changes in a repository you care about, on your own or with your team. A request too small for it gets a ready prompt for your plain agent instead.

It works with Claude Code and Codex, in the terminal, their desktop apps or your IDE, and with [any other agent](agents/other.md) that runs shell commands. Your agent writes the code, on the subscription you already have.

## Who does what

![Who does what: you and your agent discuss and write the Plan; the implement session you start with one command hands work to workers; agents that did not write the code check it; a second opinion from another vendor reviews risky Plans](pathname:///img/diagrams/agents-light.svg)
![Who does what: you and your agent discuss and write the Plan; the implement session you start with one command hands work to workers; agents that did not write the code check it; a second opinion from another vendor reviews risky Plans](pathname:///img/diagrams/agents-dark.svg)

You and your agent discuss and plan in your own session. The build runs in a session you start with one command: an orchestrator hands each slice to a cheaper, faster model. Agents that did not write the code check the result, and the App shows what each step costs.

**Look something up:** [Commands](reference/commands.md) · [Settings](reference/settings.md) · [Plan reviews](team/plans.md)
