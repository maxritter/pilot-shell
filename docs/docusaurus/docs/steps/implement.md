---
title: Implement
description: Start the build in the App or your terminal. Your agent works through tested slices until the final review.
---

![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start the build {#start-implement}

After you approve the Plan, **Start the build** appears on that Plan page. Choose where the agent runs, and for **In QualityLayer** the agent, model, effort and branch for this build. It opens with your last choice.

![The Implement start card](pathname:///img/app/implement-start-light.webp)
![The Implement start card](pathname:///img/app/implement-start-dark.webp)

*Example task in a fictional project.*

| On the card | What it picks |
| --- | --- |
| **Where the agent runs** | **In QualityLayer** (recommended) or **In my terminal, app or IDE**, according to the local runtime’s capabilities |
| **Agent** | Claude Code, Codex, Pi or OpenCode, when it runs in QualityLayer |
| **Model and effort** | The choices for this run |
| **Branch** | **Current branch**, **New branch** or **New worktree** |
| **Who builds** | Build it yourself or hand it to a teammate ([Hand over](../team/plans.md#hand-over)) |

Press **Approve & start**, or **Approve & copy prompt** with **In my terminal, app or IDE**. In QualityLayer, the task's **Agent** conversation opens beside **Files** and **Feedback**, and every question and piece of feedback happens in the App. In your terminal, app or IDE, the copied prompt says `implement the approved task` and names it; the agent asks its questions and takes your feedback in its own chat. Closing the sidebar or switching tasks keeps the run. Use its available session controls to stop or return to it ([agent runs](../app.md#agent-runs)).

### Where the build lands {#where-it-lands}

Under **Branch**, keep the **Current branch**, create a **New branch**, or use a **New worktree**. A worktree takes a name, which gives its folder and its branch; QualityLayer puts the folder next to your project. A new branch or worktree starts from this checkout’s HEAD; the pull request target is shown separately. A pull request needs a branch different from its target. `qualitylayer branch new [name]` creates a task branch from the terminal. A push or deployment requires the Plan’s authorization; merging remains yours.

## While agents build

![Implement in the App: slices and their progress](pathname:///img/app/implement-light.webp)
![Implement in the App: slices and their progress](pathname:///img/app/implement-dark.webp)

*Example task in a fictional project.*

![Slices built test first, side by side, then the checks in Verify](pathname:///img/diagrams/slices-light.svg)
![Slices built test first, side by side, then the checks in Verify](pathname:///img/diagrams/slices-dark.svg)

Each slice is written test first. QualityLayer runs and records every check itself.

The page shows the board of slices, in the order of `05-implement.md`. Every slice is a row, finished and still to come, and the running one is open to its tasks. Nothing here asks for your approval. **Look here** lists what needs a glance: a checkpoint left open after two failed runs, a stopped session or helper, something only you can supply, queued for Review, a deviation that changes what you approved, and a failure that was there before the build. The decisions made while building, the recorded checks and the checkpoints are collapsed, each with a count and a one-line summary. The deviations, plan changes and restarts are in the document.

Routine choices appear under **Decided while building**. Outline, Implement and Verify continue without workflow questions until Review. A login, secret, account or other human-only prerequisite is recorded with the affected task and stays unverified for Review. Available work continues; blocked checks retain their evidence instead of being marked passed. The App never takes the secret.

Runs start with the agent's own permission settings. Native permission or sign-in prompts still require their normal response. An explicit stop or pause remains in force.

## Checkpoints {#checkpoints}

![A checkpoint: scenarios run on the real program, failures go back to an agent](pathname:///img/diagrams/checkpoint-light.svg)
![A checkpoint: scenarios run on the real program, failures go back to an agent](pathname:///img/diagrams/checkpoint-dark.svg)

After a risky slice others build on, its scenarios run on the real program. A failure goes back to an agent for a fix. The recorded result and any unresolved failure stay with the task for Review. Once the build is ready, [Verify](verify.md) follows.
