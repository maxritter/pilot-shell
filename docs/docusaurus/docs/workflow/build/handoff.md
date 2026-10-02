---
title: Handoff
description: Choose the agent that builds, check its setup, and start the build from the approved plan.
---

![The Feature route with Handoff highlighted](pathname:///img/diagrams/track-handoff-light.svg)
![The Feature route with Handoff highlighted](pathname:///img/diagrams/track-handoff-dark.svg)

Planning stops here on purpose, so you choose who builds the change. The build starts from the approved documents, never from the planning chat, so any agent or model can take over.

![The Cockpit handoff: choose Claude Code, Codex or another agent, see the recommended setup and the optional steps, and copy the build prompt](pathname:///img/diagrams/handoff-light.svg)
![The Cockpit handoff: choose Claude Code, Codex or another agent, see the recommended setup and the optional steps, and copy the build prompt](pathname:///img/diagrams/handoff-dark.svg)

## In the Cockpit

| Part | What it does |
| --- | --- |
| Build with | Claude Code, Codex or another agent |
| Recommended | Build in this session if it planned the change, or in a fresh one if another agent builds. The model, with the reason |
| Your setup | The model, the effort and how many optional steps are on, in one line |
| Optional steps for this build | A switch for each step that runs from here on, starting from [Settings](../../reference/settings.md#optional-steps). A step that does not fit the task, such as UI review on a task without a screen, is greyed out |
| Adjust | Change the model, Goal or plain prompt, or start in a new worktree |
| Launch steps | The commands to clear the session and set the model, and the effort too when yours is not already high |
| Build prompt | One prompt that continues from the approved documents |
| Watch it here | The build stops for you at Review, or earlier only for a decision that is yours |

The session that builds coordinates on your best model (Opus 5.5 in Claude Code, GPT-6.1 Sol in Codex) while helpers on the [subagent model](../../reference/settings.md#subagents) you chose write the slices. A plan of fewer than three slices has no slice helpers, so the session writes the code itself and the recommendation is the coding model. A changed setup shows **Your setup**; **Reset** brings back the recommendation.

## Good to know

- Switching a step off here adds it to the build prompt, for example `--steps -docs`. The build session records the choice with its first command, and from then on it is fixed for this build.
- Start clean: clearing the session leaves the long planning conversation behind. The plan documents are what the build works from.
- The launch steps are terminal commands. In a desktop app or IDE extension, open a new session, pick the model there and paste the build prompt.
- QualityLayer builds on the branch you have checked out and never creates or switches one. Pick the branch before you plan; start a worktree yourself if you want one.
- When another task is building in the same checkout, the page names it. The recommendation stays the same, and a new worktree remains your choice.

## You decide

Pick the builder, run the launch steps, paste the prompt. Next: [Slices](slices.md).
