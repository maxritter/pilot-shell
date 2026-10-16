---
title: Implement
description: Start the build in the App or your terminal. Your agent works through tested slices until the final review.
---

![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start the build {#start-implement}

After you approve the Plan, **Start the build** appears on that Plan page. Choose the agent, model, effort and workspace for this build. [Settings](../reference/settings.md#defaults) keeps the general run controls.

![The Implement start card](pathname:///img/app/implement-start-light.webp)
![The Implement start card](pathname:///img/app/implement-start-dark.webp)

*Example task in a fictional project.*

| On the card | What it picks |
| --- | --- |
| **Agent** | An installed native agent, or **Another agent** for your terminal |
| **Model and effort** | The choices for this run |
| **Workspace** | **Project checkout**, **New branch** or **New worktree** |
| **Where agents run** | **In the App** or **In my terminal**, according to the local runtime’s capabilities |
| **Who builds** | Build it yourself or hand it to a teammate ([Hand over](../team/plans.md#hand-over)) |

Press **Start the build**, or copy the command with **In my terminal**. In the App, the task's **Agent** conversation opens beside **Files** and **Feedback**. Closing the sidebar or switching tasks keeps the run. Use its available session controls to stop or return to it ([agent runs](../app.md#agent-runs)).

### Where the build lands {#where-it-lands}

Open **Workspace** to keep the project checkout, create a **New branch**, or use a **New worktree** with its own branch and folder. A new workspace starts from this checkout’s HEAD; the pull request target is shown separately. A pull request needs a branch different from its target. `qualitylayer branch new [name]` creates a task branch from the terminal. A push or deployment requires the Plan’s authorization; merging remains yours.

## While agents build

![Implement in the App: slices and their progress](pathname:///img/app/implement-light.webp)
![Implement in the App: slices and their progress](pathname:///img/app/implement-dark.webp)

*Example task in a fictional project.*

![Slices built test first, side by side, then the checks in Verify](pathname:///img/diagrams/slices-light.svg)
![Slices built test first, side by side, then the checks in Verify](pathname:///img/diagrams/slices-dark.svg)

Each slice is written test first. QualityLayer runs and records every check itself.

Routine choices appear under **Decided while building**. Outline, Implement and Verify continue without workflow questions until Review. A login, secret, account or other human-only prerequisite is recorded with the affected task and stays unverified for Review. Available work continues; blocked checks retain their evidence instead of being marked passed. The App never takes the secret.

Runs start with the agent's own permission settings. Native permission or sign-in prompts still require their normal response. An explicit stop or pause remains in force.

## Checkpoints {#checkpoints}

![A checkpoint: scenarios run on the real program, failures go back to an agent](pathname:///img/diagrams/checkpoint-light.svg)
![A checkpoint: scenarios run on the real program, failures go back to an agent](pathname:///img/diagrams/checkpoint-dark.svg)

After a risky slice others build on, its scenarios run on the real program. A failure goes back to an agent for a fix. The recorded result and any unresolved failure stay with the task for Review. Once the build is ready, [Verify](verify.md) follows.
