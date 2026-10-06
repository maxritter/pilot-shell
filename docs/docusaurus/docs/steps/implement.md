---
title: Implement
description: One command starts the build. From there your agent works on its own until the final review, in small slices, each tested.
---

![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The five steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start Implement {#start-implement}

When you approve the Plan, Implement opens with your [Build defaults](../reference/settings.md#defaults), drawn as the build: an orchestrator that plans each slice, reads each report and writes no code, and workers that write the code, a slice each. One effort applies to both.

![Implement Start: Build with Claude Code, Codex or another agent; the orchestrator and its workers with their models; one effort for both; and the command to copy, with the lines to type first in the session that planned the task](pathname:///img/diagrams/implement-start-light.svg)
![Implement Start: Build with Claude Code, Codex or another agent; the orchestrator and its workers with their models; one effort for both; and the command to copy, with the lines to type first in the session that planned the task](pathname:///img/diagrams/implement-start-dark.svg)

- **Build with** Claude Code, Codex or another agent; another agent gets one prompt to paste.
- **Change anything** for this build only, the workers' model included. **Reset** brings your defaults back.
- **Where it starts:** by default in the session that planned the task. Implement Start then lists the lines to type first (`/clear`, `/model`, `/effort`), each with its own copy button. It can also start a new session or a new worktree.

Copy the command into a terminal, your IDE or a desktop app. The build starts from the approved Plan, never from your planning chat, on the branch you have checked out.

## While agents build

From the command on, your agent builds and checks the approved Plan through to the final review. You can still write to it at any time, for example to add something to the Plan.

![Implement: a login waits in Your turn while another slice keeps building; the live status names the slice, and the document records the build and its checks](pathname:///img/diagrams/implement-light.svg)
![Implement: a login waits in Your turn while another slice keeps building; the live status names the slice, and the document records the build and its checks](pathname:///img/diagrams/implement-dark.svg)

- **Vertical slices.** Each slice works end to end and is tested on its own, test first. Slices that share no files build side by side.
- **An orchestrator with a fresh context** hands out the slices and takes the hard problems; the routine work runs on a cheaper, faster model.
- **Checks are recorded by QualityLayer,** not reported by the agent.
- **The agent handles routine decisions.** When something does not go as planned, it takes the recommended way and lists it under **Decided while building**, where you can **Ask why**.

If the build needs a login, a secret or something only you can provide, **Your turn** names the slice that needs it. Set it in your own environment, then press **Done, it’s set**. The App never takes the secret itself. Other slices keep building; when no other work remains, the agent waits for that need to be resolved. When nothing waits for you, the agent's turn shows what is being built.

The page is `03-implement.md`, which QualityLayer keeps current from the build's records. You can comment on any slice while it builds; the agent reads comments after each task.

## Checkpoints {#checkpoints}

A slice the Plan marks risky gets a checkpoint: its scenarios run on the real program before the build goes on. A checkpoint that keeps failing is noted for the final review; it never stops the build.

When the last slice is built, [Verify](verify.md) starts by itself.
