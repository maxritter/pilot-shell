---
title: Plan
description: "The one document you approve before any code: a design and diagrams where they help, then the slices and the checks that prove the change."
---

![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-light.svg)
![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-dark.svg)

The Plan is the one document you approve before any code is written. Agents build from it afterwards, so this is where your judgement pays most.

## Your turn {#items}

Independent questions come in batches in one **Your turn** card. Answer the decisions you can make now in any order; each answer reaches your agent immediately:

1. **The design**, for a change people see: Looks right, or Change. See [Designs](../designs.md).
2. **Engineering decisions**, each with its diagram: Agree, or Change.
3. **Done means**, from [Discuss](discuss.md): agree to each point separately. Only a point whose words change needs your agreement again.
4. **Decisions made for you:** the smaller choices, each with its reason. **Ask why** about any of them.
5. **Extra review:** whether the risk deserves a security review or a second opinion.

Each answer leaves the card and is recorded at the passage it settled. **Undo** is available for five seconds. Your agent can keep working on the parts that do not depend on an open answer; its live status at the top shows what it is doing.

Approving the Plan is a separate action after you settle its decisions. Sending answers does not approve it. When you request changes, send them back to the agent to revise the Plan.

![Plan: a changed Done means point returns as Was and Now in Your turn; the other point stays agreed and approval is separate](pathname:///img/diagrams/plan-light.svg)
![Plan: a changed Done means point returns as Was and Now in Your turn; the other point stays agreed and approval is separate](pathname:///img/diagrams/plan-dark.svg)

## Read the Plan full size {#full-size}

Open the document full size to give it more room. The task list collapses, while the outline and the right sidebar stay within reach. Jump to a section, read the slices and checks, and comment on a passage without leaving the Plan. Exit full size to return to the task view.

![The full-size Plan with its outline, line comments, live agent status and the Comments, Files and Designs tabs](pathname:///img/diagrams/plan-full-light.svg)
![The full-size Plan with its outline, line comments, live agent status and the Comments, Files and Designs tabs](pathname:///img/diagrams/plan-full-dark.svg)

### Diagrams you can comment on {#diagrams}

![An engineering decision as a diagram: a pinned comment opens a thread, the agent answers in it and changes the Plan](pathname:///img/diagrams/decision-light.svg)
![An engineering decision as a diagram: a pinned comment opens a thread, the agent answers in it and changes the Plan](pathname:///img/diagrams/decision-dark.svg)

Click any part of a diagram to pin a comment. Your agent answers in the thread and changes the Plan. Teammates can do the same.

## Before it reaches you

A second agent reads the Plan the way a new builder would, and your agent fixes the gaps it finds. Anything new the Plan depends on is tried out first, outside your project. With Claude Code and Codex both installed, a risky Plan also gets a [second opinion](../reference/settings.md#second-opinion) from the other agent.

## With reviewers {#reviewers}

Ask teammates to read along; you see who has read and who approved. See [Plan reviews](../team/plans.md).

## When you ask for changes

Your agent answers each note and revises the Plan. A changed **Done means** point shows its old and new words together; your agreements to unchanged points remain saved. The Plan's diff shows the document changes line by line.

After you approve, the App opens [Implement](implement.md).
