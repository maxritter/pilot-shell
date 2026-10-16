---
title: Plan
description: "The one document you approve before any code: what it rests on, the design and its decisions, and how you will know it works."
---

![The eight steps, with Plan highlighted](pathname:///img/diagrams/track-plan-light.svg)
![The eight steps, with Plan highlighted](pathname:///img/diagrams/track-plan-dark.svg)

The Plan is the one document you approve before any code is written. It puts the proposed change, important decisions and unresolved issues first.

![The Plan in the App, with Approve Plan and Give feedback at the top right](pathname:///img/app/plan-light.webp)
![The Plan in the App, with Approve Plan and Give feedback at the top right](pathname:///img/app/plan-dark.webp)

*Example task in a fictional project.*

## What you read {#items}

| Part | What it tells you |
| --- | --- |
| **The design** | A wireframe or finished design for anything people see ([Designs](../designs.md)) |
| **Engineering decisions** | Two sentences each, with a diagram where a picture is clearer |
| **Done means** | The results from [Discuss](discuss.md) |
| **Decisions made for you** | Your agent's smaller choices, with reasons |
| **Not doing**, **Before the build** | What stays untouched; what must be ready first, such as a login |

Both levels keep the important choices readable. Supporting engineering details can be expanded under **Reference** ([two levels](../intro.md#two-levels)).

### What to read first {#read-first}

Start with **Summary**, anything under **Needs you**, scope, decisions made for you, risks and how the result will be checked. Supporting material sits under **Reference**, including earlier answers and resolved review details.

**Risky** jumps to explicitly marked concerns and opens their section. Unresolved or unknown review findings remain visible; a recorded research source does not mean the Plan review is complete.

## Approve or give feedback {#answering}

A choice that only appears once a design is drawn is a **Your call** (at most two). **Your turn** shows them one at a time, with the part of the Plan each concerns, and each answer reaches your agent immediately. Findings from the technical review return to the planning agent; only a new hard choice reaches you.

1. Read the complete Plan.
2. Pin comments, or press **Give feedback**. Your agent revises; the diff shows what changed.
3. Press **Approve Plan** at the top right. It approves the Plan, **Done means** and the design together.

Only your click approves: answering a question does not approve the Plan.

## Comment on a diagram {#diagrams}

![A pinned comment on a diagram: the agent answers and changes the Plan](pathname:///img/diagrams/decision-light.svg)
![A pinned comment on a diagram: the agent answers and changes the Plan](pathname:///img/diagrams/decision-dark.svg)

Click any part of a diagram or passage to pin a comment. Your agent reads it when it next checks the task; a stopped or disconnected agent cannot answer yet. Teammates can comment too ([Plan reviews](../team/plans.md)).

## Before it reaches you {#before-it-reaches-you}

Your agent rereads every Plan as a reviewer would. A risky Plan also gets a second opinion from the other coding agent. While a required review is running, its amber reason sits beside the blocked **Approve Plan** button. Hover or focus the approval control to read why it is blocked. It unlocks once required findings and human choices are settled ([Settings](../reference/settings.md#second-opinion)).

Next: [Start Implement](implement.md#start-implement). The build session writes the [Outline](outline.md), then builds it.
