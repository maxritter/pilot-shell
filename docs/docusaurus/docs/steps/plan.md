---
title: Plan
description: "The one document you approve before any code: what it rests on, the design and its decisions, the contracts the build is held to, and how you will know it works."
---

![The seven steps, with Plan highlighted](pathname:///img/diagrams/track-plan-light.svg)
![The seven steps, with Plan highlighted](pathname:///img/diagrams/track-plan-dark.svg)

The Plan is the one document you approve before any code is written. Agents build from it afterwards, so this is where your judgement pays most. It rests on the [Research](research.md); the slices come afterwards, in the [Outline](outline.md), which needs no approval.

## Your turn {#items}

Review the complete Plan, including its diagrams, designs and reasoning:

1. **What the Plan rests on:** the research findings it builds on, each in one sentence, so you can see why it looks the way it does.
2. **The design**, for a change people see. Read it and comment on anything that needs correction. See [Designs](../designs.md).
3. **Engineering decisions**, each with its diagram and reasoning. These explain the agent's proposals; a heading does not automatically ask for your approval. Below them, the **contracts** between the parts, folded to one headline each, show what the build is held to; open one with **Read in full**.
4. **Done means**, from [Discuss](discuss.md): review the proposed results and their reasoning. Your final Plan approval covers these criteria together with the Plan.
5. **Decided by you** and **Decisions made for you:** your answers from Discuss and Research, then the smaller choices your agent took, each with its reason. Ask your agent to explain or revise any of them.
6. **Not doing** and **Before the build:** what the build will leave alone, and what must be in place before it starts, such as a login only you can provide.
7. **How we will know it works:** the one check that tells whether the whole change works, and the expected size.

The Plan asks no batch of questions. A choice that appears only once a design is drawn sits inside the Plan as **Your call**, with two options, a recommendation and the design; there are at most two, and **Approve Plan** stays locked until each is settled. **Your turn** focuses one explicitly asked choice at a time. Open the document context when you need it. Each answer reaches your agent immediately and is recorded at the passage it settled. Technical review findings return to the planning agent to fix or answer; only a new ambiguous or hard choice needing your judgement becomes a question.

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

## Before it reaches you {#before-it-reaches-you}

The review starts with the first full draft, not when you are told. With Claude Code and Codex both installed, the other agent reads the Plan: decisions that do not follow from what you agreed, a simpler shape, missed risks, contradictions with the code and a size that looks off. With only one installed, a separate Sonnet reviewer of that agent reads it with the same questions. Your agent folds the findings in, and only then does the Plan reach you, so the Plan you are told about is ready to approve. **Reviewed by** shows who read it, what they found and what happened to each finding. [Settings](../reference/settings.md#second-opinion) lets you choose when the other agent reads the Plan. Anything new the Plan depends on is tried out first, outside your project.

## With reviewers {#reviewers}

Ask teammates to read along; you see who has read and who approved. See [Plan reviews](../team/plans.md).

## When you ask for changes

Your agent answers each note and revises the Plan. Earlier answers and agreements stay saved. Changes to **Done means** invalidate the Plan's approval, so you can review the current document before approving again. The Plan's diff shows the document changes line by line.

While you read, your agent writes the [Outline](outline.md); the status at the top says so. After you approve, the Outline is finished and the App opens [Implement](implement.md).
