---
title: Slices
description: How the build works through the plan, slice by slice and test first, and what you see while it runs.
---

![The Feature route with Build highlighted](pathname:///img/diagrams/track-slices-light.svg)
![The Feature route with Build highlighted](pathname:///img/diagrams/track-slices-dark.svg)

Each slice goes through every layer, from the screen to the database, and each task starts with a failing test. In a plan with three or more slices, a fresh helper on a smaller, cheaper model builds each slice while your session coordinates, and slices that do not depend on each other build side by side.

![Three slices, each through every layer, each starting with a failing test and ending with an end-to-end run; then an optional quality pass works on the whole change before Verify](pathname:///img/diagrams/slices-light.svg)
![Three slices, each through every layer, each starting with a failing test and ending with an end-to-end run; then an optional quality pass works on the whole change before Verify](pathname:///img/diagrams/slices-dark.svg)

## In the Cockpit

![The Build tab: what the agent does now, slices with ticked tasks, a passed checkpoint, and the notes on a task](pathname:///img/diagrams/build-light.svg)
![The Build tab: what the agent does now, slices with ticked tasks, a passed checkpoint, and the notes on a task](pathname:///img/diagrams/build-dark.svg)

| Part | What it shows |
| --- | --- |
| Working now | Who is working at this moment, your agent or a helper, and on what |
| The diff | The change so far, live, in a drawer beside the build |
| Checkpoints | Each [end-to-end check](checks.md) with its runs, its pictures and the steps to try it yourself |

Comment on any slice, task or checkpoint while it builds; the agent reads your feedback at its next step.

## Notes

Every surprise becomes one line on its task, kept in `04-build.md`:

| Note | Meaning |
| --- | --- |
| `tactical` | A detail differed; the approach held |
| `amended` | The agent changed the plan within its limits, such as splitting a task |
| `agreed` | You decided a change during the build; your words are kept |
| `judged` | A fix that verification asked for |
| `found by checkpoint N` | A fix that an end-to-end check asked for |

## When the build needs you

- a change would touch what you decided (Done means, the scope, your design choices, a new dependency): the agent asks one question and records your answer;
- an end-to-end check fails three times.

A helper that stops without its report is restarted at once. The build does not ask you about it.

Every change to the plan is listed in [Review](../check/review.md), with its diff.
