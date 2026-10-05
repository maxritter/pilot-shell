---
slug: /
title: QualityLayer documentation
description: How QualityLayer takes your coding agent from a request to a reviewed change, and where you decide along the way.
---

QualityLayer runs your coding agent through a proper engineering process. You approve one plan before any code is written. The agent builds it test first, and agents that did not write the code check the result against what you asked for. Your agent asks you each decision in its own window. The **QualityLayer App** beside it shows what the question is about: the diagrams, the screens to look at, and the proof.

![The QualityLayer App: the sidebar, the five step tabs, the step line with Approve, the items that need you, the line of what agents checked, and the Plan](pathname:///img/diagrams/app-light.svg)
![The QualityLayer App: the sidebar, the five step tabs, the step line with Approve, the items that need you, the line of what agents checked, and the Plan](pathname:///img/diagrams/app-dark.svg)

**Start here:** [Install](install.md) · [Your first task](first-task.md) · [The App](app.md) · [The five steps](steps/discuss.md)

## The five steps {#the-five-steps}

Every task takes the same five steps. You approve twice: the Plan before any code, and the finished change at the end. Every step has the same layout in the App, so you always know where to look.

![The five steps: Discuss, Plan, Implement, Verify and Review. You approve the Plan and the finished change; your agent does the rest](pathname:///img/diagrams/flow-light.svg)
![The five steps: Discuss, Plan, Implement, Verify and Review. You approve the Plan and the finished change; your agent does the rest](pathname:///img/diagrams/flow-dark.svg)

| Step | What happens |
| --- | --- |
| **[Discuss](steps/discuss.md)** | Your agent asks until it understands what you want and what done means. You answer in your agent |
| **[Plan](steps/plan.md)** | The mockup, the engineering decisions as diagrams, and the slices and checks that prove it. Your agent asks each decision, then "Approve the Plan?" |
| **[Implement](steps/implement.md)** | One command starts the build. Slices built test first, each check recorded by QualityLayer. Nothing waits for you, and you read the choices the build made on its own |
| **[Verify](steps/verify.md)** | Agents that did not write the code check it against what done means, on a live checklist |
| **[Review](steps/review.md)** | Your agent asks the few items left, you look at the result, and approve. The Approve menu can open the pull request |

A bug takes the same steps. Its cause is found before anything is planned.

## Who it is for

QualityLayer is for medium to large changes in a repository you care about. When a request is too small for it, your agent says so. It writes a ready prompt for your plain agent and offers to run it. You can still insist on a QualityLayer task.

It works inside Claude Code and Codex, in the terminal, their desktop apps or your IDE, and with any other coding agent that can run shell commands ([how to connect it](agents/other.md)). Your agent still writes the code, on the subscription you already have. You can work on your own or with your whole team.

## Who does what

![Who does what: you and your agent discuss and write the Plan; the implement session you start with one command hands work to workers; agents that did not write the code check it; a second opinion from another vendor reviews risky Plans](pathname:///img/diagrams/agents-light.svg)
![Who does what: you and your agent discuss and write the Plan; the implement session you start with one command hands work to workers; agents that did not write the code check it; a second opinion from another vendor reviews risky Plans](pathname:///img/diagrams/agents-dark.svg)

Opus 5.5 is recommended for Discuss and Plan, in your own session. You start Implement with one command from the App, with Sonnet 5.5 recommended. Workers build the slices from the Plan, never from your chat. The agents that check the result run on Opus 5.5. The App shows what each step costs.

**Look something up:** [Commands](reference/commands.md) · [Settings](reference/settings.md) · [Review plans as a team](team/plans.md)
