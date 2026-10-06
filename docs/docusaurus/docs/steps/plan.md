---
title: Plan
description: "The one document you approve before any code: mockups and diagrams where they help, then the slices and the checks that prove the change."
---

![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-light.svg)
![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-dark.svg)

The Plan is the one document you approve before any code is written. Agents build from it afterwards, so this is where your judgement pays most.

![The Plan waiting for approval: the items that need you, your agent asking “Approve the Plan?” in the terminal, and the line of what agents checked](pathname:///img/diagrams/plan-light.svg)
![The Plan waiting for approval: the items that need you, your agent asking “Approve the Plan?” in the terminal, and the line of what agents checked](pathname:///img/diagrams/plan-dark.svg)

## What needs you {#items}

Your agent walks you through these one at a time, and the App shows each:

1. **The mockup**, for a change people see: Looks right, or Change.
2. **Engineering decisions**, each with its diagram: Agree, or Change.
3. **Done means**, from [Discuss](discuss.md).
4. **Decided by the agent:** the smaller choices, each with its reason. **Keep all**, or change one.
5. **Extra review:** whether the risk deserves a security review or a second opinion.

Then: "Approve the Plan?" Answer in the terminal, or **Review in the App first**.

### Diagrams you can comment on {#diagrams}

![An engineering decision as a diagram: a pinned comment opens a thread, the agent answers in it and changes the Plan](pathname:///img/diagrams/decision-light.svg)
![An engineering decision as a diagram: a pinned comment opens a thread, the agent answers in it and changes the Plan](pathname:///img/diagrams/decision-dark.svg)

Click any part of a diagram to pin a comment. Your agent answers in the thread and changes the Plan. Teammates can do the same.

## Before it reaches you

A second agent reads the Plan the way a new builder would, and your agent fixes the gaps it finds. Anything new the Plan depends on is tried out first, outside your project. With Claude Code and Codex both installed, a risky Plan also gets a [second opinion](../reference/settings.md#second-opinion) from the other agent.

## With reviewers {#reviewers}

Ask teammates to read along; you see who has read and who approved. See [Plan reviews](../team/plans.md).

## When you ask for changes

Your agent answers each note and comes back with revision 2: only your notes, with every changed part marked. **Show the Plan's diff** shows the change line by line.

After you approve, the App opens [Implement](implement.md).
