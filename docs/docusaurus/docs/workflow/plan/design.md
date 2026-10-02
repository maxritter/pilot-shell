---
title: Design
description: Decide what gets built, with a clickable mockup, a picture of the system and every choice written down.
---

![The Feature route with Design highlighted](pathname:///img/diagrams/track-design-light.svg)
![The Feature route with Design highlighted](pathname:///img/diagrams/track-design-dark.svg)

The design settles every decision that changes what gets built, before a single task is written.

![The Cockpit: a design under review with a system diagram, a teammate's comment and a clickable mockup](pathname:///img/diagrams/cockpit-light.svg)
![The Cockpit: a design under review with a system diagram, a teammate's comment and a clickable mockup](pathname:///img/diagrams/cockpit-dark.svg)

## In the Cockpit

| Section | What it holds |
| --- | --- |
| Interface | A clickable mockup for a screen, with its empty, loading and error states |
| System design | A picture of the system after the change, and what changes in each part |
| Decided by you | The choices you were asked to make, with your answers |
| Decisions made for you | What the agent decided, and why |
| Not doing | What stays outside this task |

`02-design-details.md` holds the contracts, data shapes and risks for the builder. Each task in the outline names the contract it builds.

The design also says where each new piece of code lives and why it is needed.

On the [product route](../plan.md#for-product-managers-the-product-route), this document is the TDD. It also holds the program design, the part of the design that says how the code is laid out.

## What the design stands on

Before you are asked to approve, your agent tries out everything new the design depends on: a service, a library, a feature of the platform, a tool. It does this in a scratch folder, never in your project. The details list each one with what was tried and what happened, or say that nothing new is needed. Anything that cannot be tried before the approval is either your decision or the first slice of the outline, so the plan does not rest on a guess. The design cannot go up for your review while this part is missing.

## The second opinion

![The second opinion: while you review the design, the other vendor's AI reviews it too; your agent answers its findings, then Approve unlocks](pathname:///img/diagrams/secondop-light.svg)
![The second opinion: while you review the design, the other vendor's AI reviews it too; your agent answers its findings, then Approve unlocks](pathname:///img/diagrams/secondop-dark.svg)

With Claude Code and Codex both installed, the other vendor's AI reviews the frame, the research and the design while you read. You can comment meanwhile. **Approve** unlocks once your agent has worked in the findings it agrees with and said why it skipped the rest. [Settings](../../reference/settings.md#second-opinion) chooses its model, and the **Second opinion** switch turns it off, for every task or for one.

## You decide

Try the mockup, check the behaviour and the boundaries, then approve or request changes.

Next: [Outline](outline.md).
