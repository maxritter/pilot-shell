---
title: Implement
description: You start a fresh session, and the approved Plan is built slice by slice, test first, with every check recorded by QualityLayer.
---

![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start Implement {#start-implement}

Once you approve the Plan, the planning session stops. The App and the chat show the same short prompt with a **Copy** button.

![After you approve the Plan, the App shows the prompt /ql implement csv-export with a Copy button and the advice to start a fresh session with Sonnet 5.5](pathname:///img/diagrams/implement-start-light.svg)
![After you approve the Plan, the App shows the prompt /ql implement csv-export with a Copy button and the advice to start a fresh session with Sonnet 5.5](pathname:///img/diagrams/implement-start-dark.svg)

Start a fresh session the way you like: the terminal, your IDE or a desktop app. Sonnet 5.5 is recommended (GPT-6.1 Sol in Codex). Type `/ql implement <task>`, or `$ql implement <task>` in Codex. Goal mode is an option in your agent; it is not needed.

The build starts from the approved Plan, never from the planning chat. QualityLayer never starts, stops or steers an agent. It builds on the branch you have checked out and never creates or switches one; start a worktree yourself if you want one.

## Slices, test first

![Implement and Verify: slices built test first, side by side where they share no files, a checkpoint after a risky slice, then Polish and Security side by side, then one judge](pathname:///img/diagrams/slices-light.svg)
![Implement and Verify: slices built test first, side by side where they share no files, a checkpoint after a risky slice, then Polish and Security side by side, then one judge](pathname:///img/diagrams/slices-dark.svg)

A slice is a thin piece of the change that works end to end on its own. Every task in it starts with a failing test. With three or more slices, helper agents build them while your session coordinates. Slices that share no files build side by side.

Your session hands out the work and commits each finished slice. When a check fails, a fresh agent gets the gap and fixes it, test first.

## Checks QualityLayer records {#checks}

Your agent does not report its own test results. QualityLayer runs the commands approved in the Plan and records each one, with its exit code, under *Checks* in `03-build.md`.

| Command | What it runs |
| --- | --- |
| `qualitylayer check task T<n>` | The check on one task card |
| `qualitylayer check slice <n>` | The slice's commands from the Plan |
| `qualitylayer check all` | The project's tests, lint, type check and build, once before the judge |

A command changed after you approved the Plan is not run by QualityLayer. Your agent runs it through its own permission prompt, and the record says so.

## In the App

![The Implement tab: each task building, verified or done, two slices side by side, and the checks QualityLayer recorded with their exit codes](pathname:///img/diagrams/implement-light.svg)
![The Implement tab: each task building, verified or done, two slices side by side, and the checks QualityLayer recorded with their exit codes](pathname:///img/diagrams/implement-dark.svg)

Each task shows as **building** while a helper is on it, **verified** once its check passed, and **done** once its box is ticked. The diff so far opens in a drawer beside the build. Comment on any slice or task while it builds; your agent reads it at its next step. A surprise during the build becomes one line on its task.

## Checkpoints {#checkpoints}

A slice the Plan marks `**Risky:**` gets a checkpoint. A fresh helper runs that slice's scenarios on the real program and keeps the test output, logs and screenshots. Zero checkpoints is the normal case.

![A checkpoint after a risky slice: its scenarios run on the real program; a failure goes to a fresh agent and runs again, and after two failed runs you decide](pathname:///img/diagrams/checkpoint-light.svg)
![A checkpoint after a risky slice: its scenarios run on the real program; a failure goes to a fresh agent and runs again, and after two failed runs you decide](pathname:///img/diagrams/checkpoint-dark.svg)

A failed run goes to a fresh agent, which fixes it at the source, and the scenarios run again. After two failed runs the build stops and asks you, with a recommendation:

- **Continue:** try once more, another way.
- **Pivot:** change the approach; your agent updates the Plan with your words.
- **Abandon:** stop; the documents and finished slices stay.

To run a checkpoint after every slice, switch on **Checkpoint after every slice** in [Settings](../reference/settings.md#checkpoint-after-every-slice), or say so for one task.

## When the build needs you

- A change would touch what you decided: Done means, the scope or a decision of yours. Your agent asks one question and records your answer in your words.
- A checkpoint fails twice.

Everything you must provide, such as a login or a permission, is settled in the Plan, so the build does not stop for it. When the last slice is built, [Verify](verify.md) starts by itself.
