---
title: Plan
description: "The one document you approve before any code: a design and diagrams where they help, then the slices and the checks that prove the change."
---

![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-light.svg)
![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-dark.svg)

The Plan is the one document you approve before any code is written. Agents build from it afterwards, so this is where your judgement pays most.

## Your turn {#items}

Review the complete Plan, including its diagrams, designs and reasoning:

1. **The design**, for a change people see. Read it and comment on anything that needs correction. See [Designs](../designs.md).
2. **Engineering decisions**, each with its diagram and reasoning. These explain the agent's proposals; a heading does not automatically ask for your approval.
3. **Done means**, from [Discuss](discuss.md): review the proposed results and their reasoning. Your final Plan approval covers these criteria together with the Plan.
4. **Decisions made for you:** the smaller choices, each with its reason. Ask your agent to explain or revise any of them.
5. **Extra review:** whether the risk deserves a security review or a second opinion. Request one when you need it.

**Your turn** focuses one explicitly asked choice at a time. Open the document context when you need it. Each answer reaches your agent immediately and is recorded at the passage it settled. Technical review findings return to the planning agent to fix or answer; only a new ambiguous or hard choice needing your judgement becomes a question.

In a focused decision card, **1–9** selects the matching answer and **←/→** moves between decisions. **Enter** sends your words; **Shift+Enter** adds a line. Choice shortcuts leave typing fields and text composition alone, and do not run with **⌘**, **Ctrl** or **Alt**.

Once the real choices are answered, the complete Plan appears in the main pane. Use **Approve Plan** at the top right to approve it once, covering the proposed criteria, decisions and design together. **Give feedback** opens a place to write and send the changes you want. Approval waits while required reviewer work is still being processed; answering a question does not approve the Plan.

## Read the Plan full size {#full-size}

Read the complete Plan in the main pane before approving it. **Document full size** adds the outline when you want more room. Jump to a section, read the slices and checks, and comment on a passage without leaving the Plan. The document header holds its file chip, reading controls and menu for the agent's version and records.

![The full-size Plan with its document header, outline, line comments, named agent status and Files and Comments tabs](pathname:///img/diagrams/plan-full-light.svg)
![The full-size Plan with its document header, outline, line comments, named agent status and Files and Comments tabs](pathname:///img/diagrams/plan-full-dark.svg)

### Diagrams you can comment on {#diagrams}

![An engineering decision as a diagram: a pinned comment opens a thread, the agent answers in it and changes the Plan](pathname:///img/diagrams/decision-light.svg)
![An engineering decision as a diagram: a pinned comment opens a thread, the agent answers in it and changes the Plan](pathname:///img/diagrams/decision-dark.svg)

Click any part of a diagram to pin a comment. Your agent answers in the thread and changes the Plan. Teammates can do the same.

## Before it reaches you

A review checks whether a new builder could follow the Plan, and your agent fixes the gaps it finds. QualityLayer asks for a separate reviewer; when the client cannot start one, it provides a local review fallback. That fallback is a self-review, and does not prove that another agent checked the Plan. The App shows the recorded review facts. Anything new the Plan depends on is tried out first, outside your project. With Claude Code and Codex both installed, a risky Plan also gets a [second opinion](../reference/settings.md#second-opinion) from the other agent.

## With reviewers {#reviewers}

Ask teammates to read along; you see who has read and who approved. See [Plan reviews](../team/plans.md).

## When you ask for changes

Your agent answers each note and revises the Plan. Earlier answers and agreements stay saved. Changes to **Done means** invalidate the Plan's approval, so you can review the current document before approving again. The Plan's diff shows the document changes line by line.

After you approve, the App opens [Implement](implement.md).
