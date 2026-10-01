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

## The second opinion

![The second opinion: while you review the design, the other vendor's AI reviews it too; your agent answers its findings, then Approve unlocks](pathname:///img/diagrams/secondop-light.svg)
![The second opinion: while you review the design, the other vendor's AI reviews it too; your agent answers its findings, then Approve unlocks](pathname:///img/diagrams/secondop-dark.svg)

With Claude Code and Codex both installed, the other vendor's AI reviews the frame, the research and the design while you read. You can comment meanwhile. **Approve** unlocks once your agent has worked in the findings it agrees with and said why it skipped the rest. [Settings](../../reference/settings.md#second-opinion) chooses its model, or turns it off.

## You decide

Try the mockup, check the behaviour and the boundaries, then approve or request changes.

Next: [Outline](outline.md).
