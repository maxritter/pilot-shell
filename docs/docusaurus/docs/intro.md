---
slug: /
title: Overview
description: How QualityLayer takes your coding agent from a request to a reviewed change, and where you decide along the way.
---

<figure class="ql-film">
  <video controls preload="none" playsinline poster="https://qualitylayer-media.max-ritter.workers.dev/overview.webp" src="https://qualitylayer-media.max-ritter.workers.dev/overview.mp4"></video>
  <figcaption>How QualityLayer works, in about four minutes: the problem it solves, the five steps, and working on your own or with your team.</figcaption>
</figure>

QualityLayer runs your coding agent through an engineering process with your decisions recorded along the way. You agree on a plan before any code is written, the agent builds it in small tested slices, and agents that did not write the code check the result. **Your turn** in the **QualityLayer App** shows one focused question. Independent questions can arrive together; skip one for now or write your own answer and press **Send**. Each answer reaches your agent immediately, while it keeps working on the rest.

![The QualityLayer App: a named agent status and the five steps, one focused question, and Files and Comments in the right sidebar](pathname:///img/diagrams/app-light.svg)
![The QualityLayer App: a named agent status and the five steps, one focused question, and Files and Comments in the right sidebar](pathname:///img/diagrams/app-dark.svg)

**Start here:** [Install](install.md) · [Your first task](first-task.md) · [The App](app.md) · [The five steps](steps/discuss.md) · [Designs](designs.md)

## How it fits together {#how-it-fits-together}

Your agent works through the **QualityLayer CLI** on your computer, which keeps each task in plain Markdown files in your repository. The **QualityLayer App** reads the same files and shows them to you. Sharing is optional. A Plan shared with your team or by link is encrypted on your computer first. The **QualityLayer Server** at qualitylayer.dev sees who is involved and the step; it cannot read your plans or comments ([your data](reference/files.md#privacy)).

![How QualityLayer fits together: on your computer, your agent runs the QualityLayer CLI, which keeps each task in Markdown files in your repository, and the QualityLayer App reads the same files; only when you share, plans and comments go to the QualityLayer Server at qualitylayer.dev, encrypted, for your team and for people with a share link](pathname:///img/diagrams/architecture-light.svg)
![How QualityLayer fits together: on your computer, your agent runs the QualityLayer CLI, which keeps each task in Markdown files in your repository, and the QualityLayer App reads the same files; only when you share, plans and comments go to the QualityLayer Server at qualitylayer.dev, encrypted, for your team and for people with a share link](pathname:///img/diagrams/architecture-dark.svg)

Each step is one document, from `01-discuss.md` to `05-review.md`; the agents' own records go to `agent/`. The files are yours, committed with the change, and they stay when you uninstall ([what each file holds](reference/files.md)). Interactive designs stay on your computer; an explicitly shared Plan can include a labelled raster still. Your agent calls the CLI at every step; the [command reference](reference/commands.md) lists its commands.

## The five steps {#the-five-steps}

Every task takes the same five steps. You approve twice: the Plan before any code, and the finished change.

![The five steps: Discuss, Plan, Implement, Verify and Review. You approve the Plan and the finished change; your agent does the rest](pathname:///img/diagrams/flow-light.svg)
![The five steps: Discuss, Plan, Implement, Verify and Review. You approve the Plan and the finished change; your agent does the rest](pathname:///img/diagrams/flow-dark.svg)

| Step | What happens |
| --- | --- |
| **[Discuss](steps/discuss.md)** | Your agent asks until it knows what you want and what done means |
| **[Plan](steps/plan.md)** | A design and diagrams where they help; you approve it before any code |
| **[Implement](steps/implement.md)** | One command starts the build; it runs on its own in small slices, each tested |
| **[Verify](steps/verify.md)** | Agents that did not write the code check every point |
| **[Review](steps/review.md)** | You settle what is left and approve; the pull request opens |

A bug takes the same steps. Its cause is found before anything is planned.

## Who it is for

Medium to large changes in a repository you care about, on your own or with your team. A new request first gets a named Discuss task. If it is too small for a plan, that task closes with its document preserved and a ready prompt for your plain agent.

It works with Claude Code and Codex, in the terminal, their desktop apps or your IDE, and with [any other agent](agents/other.md) that runs shell commands. Your agent writes the code, on the subscription you already have.

## Coming from plan mode in your IDE {#from-plan-mode}

If you use Claude's plan mode in PhpStorm or VS Code, you can keep reading each change in the IDE's diff. QualityLayer adds these steps around that work:

- **You approve the plan:** your agent asks each decision, and the Plan shows mockups and diagrams you and your team can comment on.
- **The build runs in tested slices** from the approved Plan, and agents that did not write the code check every point you agreed on.
- **You review what is left,** with the proof beside it. The diff stays where you like to read it, in your IDE.

## Who does what

![Who does what: you and your agent discuss and write the Plan; the orchestrator you start with one command writes no code and hands each slice to workers; agents that did not write the code check it; a second opinion from the other coding agent reviews risky Plans](pathname:///img/diagrams/agents-light.svg)
![Who does what: you and your agent discuss and write the Plan; the orchestrator you start with one command writes no code and hands each slice to workers; agents that did not write the code check it; a second opinion from the other coding agent reviews risky Plans](pathname:///img/diagrams/agents-dark.svg)

You and your agent discuss and plan with your [Planning defaults](reference/settings.md#defaults). One command starts the build with your Build defaults. An orchestrator that writes no code hands each slice to the workers' model. Your agent then works on its own until the final review. Agents that did not write the code check the result, and the App shows what each step costs.

**Look something up:** [Commands](reference/commands.md) · [Settings](reference/settings.md) · [Plan reviews](team/plans.md)
