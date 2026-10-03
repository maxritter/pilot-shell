---
slug: /
title: QualityLayer documentation
description: How QualityLayer takes your coding agent from a request to a reviewed change, and where you decide along the way.
---

QualityLayer runs your coding agent through a proper engineering process. You approve one plan before any code is written. The agent builds it test first, and an AI that did not write the code checks the result against what you asked for. You read, comment and approve in the **QualityLayer App**.

![The QualityLayer App: the task list, the five steps, the Plan under review with a diagram, a teammate's comment, a clickable mockup, and Approve](pathname:///img/diagrams/app-light.svg)
![The QualityLayer App: the task list, the five steps, the Plan under review with a diagram, a teammate's comment, a clickable mockup, and Approve](pathname:///img/diagrams/app-dark.svg)

**Start here:** [Install](install.md) · [Your first task](first-task.md) · [The five steps](steps/discuss.md)

## The five steps {#the-five-steps}

Every task takes the same five steps. You approve twice: the Plan before any code, and the finished change at the end.

![The five steps: Discuss, Plan, Implement, Verify and Review. You approve the Plan and the finished change; your agent does the rest](pathname:///img/diagrams/flow-light.svg)
![The five steps: Discuss, Plan, Implement, Verify and Review. You approve the Plan and the finished change; your agent does the rest](pathname:///img/diagrams/flow-dark.svg)

| Step | What happens |
| --- | --- |
| **[Discuss](steps/discuss.md)** | Your agent asks until it understands what you want and what done means |
| **[Plan](steps/plan.md)** | One document: the decisions, the mockup, the slices and the checks that prove it. You approve it |
| **[Implement](steps/implement.md)** | Slices built test first, each check recorded by QualityLayer |
| **[Verify](steps/verify.md)** | An AI that did not write the code checks it against what done means |
| **[Review](steps/review.md)** | You review the change with its evidence, your team weighs in, and you approve |

A bug takes the same steps. Its cause is found before anything is planned.

## Who it is for

QualityLayer is for medium to large changes in a repository you care about. When a request is too small for it, your agent says so. It writes a ready prompt for your plain agent and offers to run it. You can still insist on a QualityLayer task.

It works inside Claude Code and Codex, in the terminal, their desktop apps or your IDE. Your agent still writes the code, on the subscription you already have.

## Who does what

![Who does what: you and your agent discuss and write the Plan; the implement session you start hands work to helpers; a judge that did not write the code checks it; a second opinion is optional](pathname:///img/diagrams/agents-light.svg)
![Who does what: you and your agent discuss and write the Plan; the implement session you start hands work to helpers; a judge that did not write the code checks it; a second opinion is optional](pathname:///img/diagrams/agents-dark.svg)

Opus 5.5 is recommended for Discuss and Plan, in your own session. You start Implement in a fresh session, with Sonnet 5.5 recommended. Helper agents build the slices from the Plan, never from your chat. The judge runs on Opus 5.5. The App shows what each step costs.

**Look something up:** [Commands](reference/commands.md) · [Settings](reference/settings.md) · [Review plans as a team](team/plans.md)
