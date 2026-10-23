---
title: Implement
description: Start the build in the App or your terminal. Your agent works through tested slices until the final review.
---

![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start the build {#start-implement}

After you approve the Plan, **Start the build** appears on that Plan page. Choose where the agent runs and, with **In the App**, the agent, model, effort and branch for this build. The card opens with your last choice.

![The Implement start card](pathname:///img/app/implement-start-light.webp)
![The Implement start card](pathname:///img/app/implement-start-dark.webp)

*Example task in a fictional project.*

| On the card | What it picks |
| --- | --- |
| **Where the agent runs** | **In the App** (recommended) or **In my terminal**, according to the local runtime’s capabilities |
| **Agent** | An installed native agent, or Another agent for your terminal |
| **Model and effort** | The choices for this run |
| **Branch** | **Current branch**, **New branch** or **New worktree** |

Press **Approve & start**, or **Approve & copy prompt** with **In my terminal**.

- **In the App**, the task's **Agent** conversation opens beside **Files** and **Feedback**. Every question and piece of feedback happens in the App.
- **In my terminal**, the copied prompt says `implement the approved task` and names it. The agent asks its questions and takes your feedback in its own chat.

Closing the sidebar or switching tasks keeps the run. Use its session controls to stop or return to it ([agent runs](../app.md#agent-runs)).

### Where the build lands {#where-it-lands}

Under **Branch**, choose:

- **Current branch**
- **New branch**
- **New worktree**, which takes a name that sets its folder and branch. QualityLayer puts the folder next to your project.

A new branch or worktree starts from this checkout’s HEAD. The pull request target is shown separately, and a pull request needs a branch different from its target. `qualitylayer branch new [name]` creates a task branch from the terminal. A push or deployment requires the Plan’s authorization; merging remains yours.

## While agents build

![Implement in the App: slices and their progress](pathname:///img/app/implement-light.webp)
![Implement in the App: slices and their progress](pathname:///img/app/implement-dark.webp)

*Example task in a fictional project.*

![Slices built test first, side by side, then the checks in Verify](pathname:///img/diagrams/slices-light.svg)
![Slices built test first, side by side, then the checks in Verify](pathname:///img/diagrams/slices-dark.svg)

Each slice is written test first. QualityLayer runs and records every check itself.

Follow the slice board to see what is running and what is finished. **Look here** highlights anything only you can supply. Open the recorded checks for their output.

Routine choices appear under **Decided while building**. Outline, Implement and Verify continue without workflow questions until Review.

A login, secret, account or other human-only prerequisite is recorded with the affected task and stays unverified for Review. Available work continues; blocked checks retain their evidence instead of being marked passed. The App never takes the secret.

Runs start with the agent's own permission settings. You can switch to another of its [permission modes](../agents/native.md#permission-modes) in the row under the message box; a mode that skips every check asks you to confirm. Native permission or sign-in prompts still require their normal response. An explicit stop or pause remains in force.

## Checkpoints {#checkpoints}

![A checkpoint: scenarios run on the real program, failures go back to an agent](pathname:///img/diagrams/checkpoint-light.svg)
![A checkpoint: scenarios run on the real program, failures go back to an agent](pathname:///img/diagrams/checkpoint-dark.svg)

After a risky slice that others build on, its scenarios run on the real program. A failure goes back to an agent for a fix. The recorded result and any unresolved failure stay with the task for Review. When the build is ready, [Verify](verify.md) follows.
