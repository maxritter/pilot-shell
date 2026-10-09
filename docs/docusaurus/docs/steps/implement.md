---
title: Implement
description: One command starts the build. From there your agent works on its own until the final review, in small slices, each tested.
---

![The seven steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The seven steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start Implement {#start-implement}

When you approve the Plan, the [Outline](outline.md) is finished and Implement opens with your [Build defaults](../reference/settings.md#defaults). It shows the orchestrator, which plans each slice and reads each report, and the workers, which write the code. The orchestrator writes no code. One effort applies to both.

![Implement Start: Build with Claude Code, Codex or another agent; the orchestrator and its workers with their models; one effort for both; and the command to copy, with the lines to type first in the session that planned the task](pathname:///img/diagrams/implement-start-light.svg)
![Implement Start: Build with Claude Code, Codex or another agent; the orchestrator and its workers with their models; one effort for both; and the command to copy, with the lines to type first in the session that planned the task](pathname:///img/diagrams/implement-start-dark.svg)

- **Build with** Claude Code, Codex or another agent; another agent gets one prompt to paste.
- **Change anything** for this build only, the workers' model included. **Reset** brings your defaults back.
- **Where it starts:** by default in the session that planned the task. Implement Start then lists the lines to type first (`/clear`, `/model`, `/effort`), each with its own copy button. It can also start a new session or a new worktree.

Copy the command into a terminal, your IDE or a desktop app. The build starts from the approved Plan, never from your planning chat.

### Where the build lands {#where-it-lands}

Below your defaults, a **Lands on** row names the branch you have checked out and the branch a pull request will go into, the main line of your repository. It offers two choices: **Stay on** your branch, or **Start on a new branch** named `ql/` and the task's name. Nothing changes until you pick: choosing the new branch creates it in your checkout at that click, and the commands below follow.

- **On your main branch** the row turns amber. A pull request cannot be opened from the branch it goes into, so Review would offer none. The new branch is recommended, and `git switch -c ql/<task>` shows first among the commands if you would rather run it yourself.
- **If git refuses** the new branch, for example because the name exists, the card shows git's reason and keeps that command for you to run.
- **A new worktree** keeps its own branch, and the row says so.

You can do the same from a terminal with `qualitylayer branch new`, or `qualitylayer branch new <name>` for a name of your own. QualityLayer creates a branch only when you ask, and never merges or pushes one.

## While agents build

From the command on, your agent builds and checks the approved Plan through to the final review. You can still write to it at any time, for example to add something to the Plan.

![Implement: a login waits in Your turn while another slice keeps building; the live status names the slice, and the document records the build and its checks](pathname:///img/diagrams/implement-light.svg)
![Implement: a login waits in Your turn while another slice keeps building; the live status names the slice, and the document records the build and its checks](pathname:///img/diagrams/implement-dark.svg)

- **Vertical slices,** as the [Outline](outline.md) cut them. Each slice works end to end and is tested on its own, test first. Slices that share no files build side by side.
- **An orchestrator with a fresh context** hands out the slices and takes the hard problems; the routine work runs on a cheaper, faster model.
- **Checks are recorded by QualityLayer,** not reported by the agent.
- **The agent handles routine decisions.** When something does not go as planned, it takes the recommended way and lists it under **Decided while building**, where you can **Ask why**.

If the build needs a login, a secret or something only you can provide, **Your turn** names the slice that needs it. Set it in your own environment, then press **Done, it’s set**. The App never takes the secret itself. Other slices keep building; when no other work remains, the agent waits for that need to be resolved. When nothing waits for you, the agent's turn shows what is being built.

Implement opens on **Build**, with the slices, changed files and checks as they happen. You can comment on any slice while it builds; the agent reads comments after each task. QualityLayer also keeps `05-implement.md` current from the build's records: the slices and their state, every recorded check, and what was decided while building. Open that document from **Files** when you want the complete written record, including each checkpoint and every deviation; it is not another Implement tab.

## Checkpoints {#checkpoints}

A slice the Plan marks risky gets a checkpoint: its scenarios run on the real program before the build goes on. A checkpoint that keeps failing is noted for the final review; it never stops the build.

When the last slice is built, [Verify](verify.md) starts by itself.
