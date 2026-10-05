---
title: Implement
description: One command from the App starts the build, and agents build the approved Plan slice by slice, test first, with every check recorded by QualityLayer. Nothing waits for you, and the App lists what they decided on their own.
---

![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start Implement {#start-implement}

When you approve the Plan, the App opens this task's Implement page by itself, and the planning session says where to look. Until a build session reports in, the page shows a start card with one command.

![After you approve the Plan, the App shows the start card: Build with, the recommended setup, four rows to adjust it and one command with a Copy button](pathname:///img/diagrams/implement-start-light.svg)
![After you approve the Plan, the App shows the start card: Build with, the recommended setup, four rows to adjust it and one command with a Copy button](pathname:///img/diagrams/implement-start-dark.svg)

- **Build with:** Claude Code, Codex or another agent.
- **The recommended setup,** in one line with its reason: Sonnet 5.5 builds in Claude Code (GPT-6.1 Sol in Codex), high effort, and goal mode when your agent has one. Your own session is cleared only for the agent that planned, and a worktree is never the default.
- **Adjust:** four rows, **Model**, **Effort**, **Runs as** and **Start in**. Each hint says what the choice costs. **Reset** appears once anything differs from the recommendation.
- **One command,** with **Copy**. For Claude Code it looks like `claude --model sonnet --effort high "/goal /ql implement <task>"`. For Codex it uses `codex -m gpt-6.1-sol -c model_reasoning_effort=high '…'`, with single quotes because the prompt holds `$ql`. Another agent gets a plain prompt; see [How to connect another coding agent](../agents/other.md).

Paste the command into a terminal, your IDE or a desktop app. Choosing **This session** shows three lines to type instead: `/clear`, `/model <id>`, and the prompt. The build records your choice with its first step, and it stays fixed for this build. When the session reports in, the page becomes the live build.

The build starts from the approved Plan, never from the planning chat. QualityLayer never starts, stops or steers an agent. It builds on the branch you have checked out and never creates or switches one, unless you choose **New worktree** (Claude Code only).

## While agents build

![The Implement step: agents are building and nothing needs you; what the agent decided on its own is listed under Changed while building; the slices fill in with what each agent does now](pathname:///img/diagrams/implement-light.svg)
![The Implement step: agents are building and nothing needs you; what the agent decided on its own is listed under Changed while building; the slices fill in with what each agent does now](pathname:///img/diagrams/implement-dark.svg)

The step line reads "Agents are building", for example "Slices 2 and 3 run side by side. Nothing needs you." It has no Pause button, because the App cannot pause an agent. During the build nothing waits for you: when something does not go as planned, the agent takes the recommended way and notes it.

| Part | What it shows |
| --- | --- |
| **Changed while building** | A closed row with each decision the agent took itself when something did not go as planned, such as removing a prop that only served a removed row. Nothing here waits for you. Open it to read them, and ask about any of them in Review |
| **The build** | The slices, with a bar of segments for the tasks of each. A running slice says what its agent does now, such as "writing the failing test"; a finished one shows its commit |
| **Changes so far** | A fold with the files and lines changed, grouped by task |
| **Checked by agents** | One violet line: for example, 5 tasks green, test first, and 12 checks recorded |

A slice is a thin piece of the change that works end to end on its own. Every task in it starts with a failing test. Slices that share no files build side by side, and a slice that rebuilds a shared file waits for the other one. Your session hands out the work and commits each finished slice. When a check fails, an agent gets the gap and fixes it, test first.

You can comment on any slice or task while it builds. The App shows where the comment stands: sent, picked up after a task, answered with the change. Your agent reads comments after each task.

## Checks QualityLayer records {#checks}

![Implement and Verify: slices built test first, side by side where they share no files, a checkpoint after a risky slice, then Polish and the security review, then checking](pathname:///img/diagrams/slices-light.svg)
![Implement and Verify: slices built test first, side by side where they share no files, a checkpoint after a risky slice, then Polish and the security review, then checking](pathname:///img/diagrams/slices-dark.svg)

Your agent does not report its own test results. QualityLayer runs the commands approved in the Plan and records each one, with its exit code, under *Checks* in `03-build.md`.

| Command | What it runs |
| --- | --- |
| `qualitylayer check task T<n>` | The check on one task card |
| `qualitylayer check slice <n>` | The slice's commands from the Plan |
| `qualitylayer check all` | The project's tests, lint, type check and build, once before checking starts |

A command changed after you approved the Plan is not run by QualityLayer. Your agent runs it through its own permission prompt, and the record says so.

## When the build needs more than the Plan names {#add-to-the-plan}

Your approval covers the Plan as written. If the build needs a new task, a new slice or a file outside the Plan, the agent adds it and notes what it found and what it costs. The build goes on. For example: "Fix the copy outside slice 4's files that still offers the old switch. About 1 min of building." You read it afterwards, in the **Changed while building** row and in Review.

A change to what you decided, such as the problem, the scope or Done means, is still yours. Your agent asks you in its picker and records your words.

## Checkpoints {#checkpoints}

A slice the Plan marks `**Risky:**` gets a checkpoint. An agent runs that slice's scenarios on the real program and keeps the test output, logs and screenshots. Zero checkpoints is the normal case.

![A checkpoint after a risky slice: its scenarios run on the real program; a failure goes to an agent to fix and runs again with a different approach; after four failed runs the checkpoint is recorded as open, the build goes on, and the final review lists it](pathname:///img/diagrams/checkpoint-light.svg)
![A checkpoint after a risky slice: its scenarios run on the real program; a failure goes to an agent to fix and runs again with a different approach; after four failed runs the checkpoint is recorded as open, the build goes on, and the final review lists it](pathname:///img/diagrams/checkpoint-dark.svg)

A failed run goes to an agent, which fixes it at the source, and the scenarios run again. From the second failed run on, the agent tries a different approach from the earlier ones. A failing checkpoint never stops the build. After four failed runs in a row, the checkpoint is recorded as open and the build goes on with the next slices. The failure reaches the final review, where your agent names it in one plain sentence.

To run a checkpoint after every slice, say so for one task: "run a checkpoint after every slice". See [For one task](../reference/settings.md#for-one-task).

## When the build needs you

Nothing waits for you while it builds. The one exception is a change that would touch what you decided: Done means, the scope or a decision of yours. Your agent asks one question in its picker and records your answer in your words.

Everything you must provide, such as a login or a permission, is settled in the Plan, so the build does not stop for it. Whatever stays open reaches the final review. When the last slice is built, [Verify](verify.md) starts by itself.
