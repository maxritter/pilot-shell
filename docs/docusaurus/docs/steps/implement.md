---
title: Implement
description: You start a fresh session, and agents build the approved Plan slice by slice, test first, with every check recorded by QualityLayer. The App shows what they decided on their own.
---

![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start Implement {#start-implement}

Once you approve the Plan, the planning session stops. The App shows "Start the build", with the command and a **Claude Code | Codex** switch.

![After you approve the Plan, the App shows the command /ql implement settings-cleanup with a Claude Code and Codex switch and a Copy button](pathname:///img/diagrams/implement-start-light.svg)
![After you approve the Plan, the App shows the command /ql implement settings-cleanup with a Claude Code and Codex switch and a Copy button](pathname:///img/diagrams/implement-start-dark.svg)

Start a fresh session the way you like: the terminal, your IDE or a desktop app. Sonnet 5.5 is recommended (GPT-6.1 Sol in Codex). Type `/ql implement <task>`, or `$ql implement <task>` in Codex. With another coding agent, give it the prompt from **Copy › For another agent**; see [How to connect another coding agent](../agents/other.md). Goal mode is an option in your agent; it is not needed.

The items you settled fold into one line: "Approved by you at 13:27 · 4 items settled". The build starts from the approved Plan, never from the planning chat. QualityLayer never starts, stops or steers an agent. It builds on the branch you have checked out and never creates or switches one; start a worktree yourself if you want one.

## While agents build

![The Implement step: agents are building and nothing needs you; choices the agent made outside the Plan wait with Fine and Ask why; the slices fill in with what each agent does now](pathname:///img/diagrams/implement-light.svg)
![The Implement step: agents are building and nothing needs you; choices the agent made outside the Plan wait with Fine and Ask why; the slices fill in with what each agent does now](pathname:///img/diagrams/implement-dark.svg)

The step line reads "Agents are building", for example "Slices 2 and 3 run side by side. Nothing needs you." It has no Pause button, because the App cannot pause an agent.

| Part | What it shows |
| --- | --- |
| **Decided by the agent while building** | Each choice the build made outside the Plan, such as removing a prop that only served a removed row. **Fine** or **Ask why**. The build goes on; ask about any of them now or in Review |
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

## When the build wants to add to the Plan {#add-to-the-plan}

Your approval covers the Plan as written. If the build needs a new task, a new slice or a file outside the Plan, it does not add it by itself. The App shows an item, **Add to the Plan**, with what the agent found and what it costs, for example "Fix the copy outside slice 4's files that still offers the old switch. About 1 min of building."

Choose **Add T12** or **Skip it**. That slice waits for your answer. The other slices keep building.

## Checkpoints {#checkpoints}

A slice the Plan marks `**Risky:**` gets a checkpoint. An agent runs that slice's scenarios on the real program and keeps the test output, logs and screenshots. Zero checkpoints is the normal case.

![A checkpoint after a risky slice: its scenarios run on the real program; a failure goes to an agent to fix and runs again, and after two failed runs you choose: try another fix, change the Plan or continue anyway](pathname:///img/diagrams/checkpoint-light.svg)
![A checkpoint after a risky slice: its scenarios run on the real program; a failure goes to an agent to fix and runs again, and after two failed runs you choose: try another fix, change the Plan or continue anyway](pathname:///img/diagrams/checkpoint-dark.svg)

A failed run goes to an agent, which fixes it at the source, and the scenarios run again. After two failed runs the build stops. The step line reads "Stopped after a failed checkpoint". An item describes both tries and keeps their output. You choose:

- **Try another fix.** Optionally add a hint for the third try, such as where the cause is read.
- **Change the Plan.** Your agent updates the Plan with your words.
- **Continue anyway.** Go on without that checkpoint passing.

To run a checkpoint after every slice, say so for one task: "run a checkpoint after every slice". See [For one task](../reference/settings.md#for-one-task).

## When the build needs you

- A choice outside the Plan wants your answer: **Add to the Plan**.
- A checkpoint fails twice.
- A change would touch what you decided: Done means, the scope or a decision of yours. Your agent asks one question and records your answer in your words.

Everything you must provide, such as a login or a permission, is settled in the Plan, so the build does not stop for it. When the last slice is built, [Verify](verify.md) starts by itself.
