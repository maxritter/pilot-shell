---
title: Implement
description: One command starts the build. Agents build the approved Plan in small slices, each tested on its own, and nothing waits for you.
---

![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start Implement {#start-implement}

When you approve the Plan, the App shows one command with its recommended setup. Copy it into a terminal, your IDE or a desktop app; you can change the model or effort first.

![After you approve the Plan, the App shows the start card: Build with, the recommended setup, four rows to adjust it and one command with a Copy button](pathname:///img/diagrams/implement-start-light.svg)
![After you approve the Plan, the App shows the start card: Build with, the recommended setup, four rows to adjust it and one command with a Copy button](pathname:///img/diagrams/implement-start-dark.svg)

The build starts from the approved Plan, never from your planning chat, on the branch you have checked out.

## While agents build

![The Implement step: agents are building and nothing needs you; what the agent decided on its own is listed under Changed while building; the slices fill in with what each agent does now](pathname:///img/diagrams/implement-light.svg)
![The Implement step: agents are building and nothing needs you; what the agent decided on its own is listed under Changed while building; the slices fill in with what each agent does now](pathname:///img/diagrams/implement-dark.svg)

- **Vertical slices.** Each slice works end to end and is tested on its own, test first. Slices that share no files build side by side.
- **An orchestrator with a fresh context** hands out the slices and takes the hard problems; the routine work runs on a cheaper, faster model.
- **Checks are recorded by QualityLayer,** not reported by the agent.
- **Nothing waits for you.** When something does not go as planned, the agent takes the recommended way and lists it under **Changed while building**, for you to read in Review.

You can comment on any slice while it builds; the agent reads comments after each task.

## Checkpoints {#checkpoints}

A slice the Plan marks risky gets a checkpoint: its scenarios run on the real program before the build goes on. A checkpoint that keeps failing is noted for the final review; it never stops the build.

When the last slice is built, [Verify](verify.md) starts by itself.
