---
title: Implement
description: Start the build in the App or your terminal. Your agent works through tested slices until the final review.
---

![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start Implement {#start-implement}

After you approve the Plan, the start card shows your defaults from [Settings](../reference/settings.md#defaults). **Change** sets any of them for this build only.

![The Implement start card](pathname:///img/app/implement-start-light.webp)
![The Implement start card](pathname:///img/app/implement-start-dark.webp)

*Example task in a fictional project.*

| On the card | What it picks |
| --- | --- |
| **Build with** | Claude Code, Codex, Pi, OpenCode or another agent |
| **Orchestrator** | The model that hands out slices; it writes no code |
| **Workers** | The model that writes each slice |
| **Where agents run** | **Here in the App** or **In my terminal** (Windows: terminal) |
| **Permissions** | Your agent's own settings, fewer prompts, or none |
| **Hand to the team** | A teammate builds it ([Hand over](../team/plans.md#hand-over)) |

Press **Start the build**. In the App, the agent's window opens and keeps running while you switch tasks; **Stop** and **Resume here** control it ([agent runs](../app.md#agent-runs)).

### Where the build lands {#where-it-lands}

Choose **Stay on** your branch or **Start on a new branch** (`ql/<task>`), or run `qualitylayer branch new [name]`. On your main branch the row turns amber: a pull request needs its own branch. QualityLayer never merges or pushes on its own.

## While agents build

![Implement in the App: slices and their progress](pathname:///img/app/implement-light.webp)
![Implement in the App: slices and their progress](pathname:///img/app/implement-dark.webp)

*Example task in a fictional project.*

![Slices built test first, side by side, then the checks in Verify](pathname:///img/diagrams/slices-light.svg)
![Slices built test first, side by side, then the checks in Verify](pathname:///img/diagrams/slices-dark.svg)

Each slice is written test first. QualityLayer runs and records every check itself.

Your agent does not stop to ask; its choices appear under **Decided while building**. The exception is what only you hold, such as a login, a secret or access: **Your turn** names the slice. Set it in your own environment and press **It's set**; the App never takes the secret. Other slices keep building; when nothing else is left, the agent waits for that need to be resolved.

## Checkpoints {#checkpoints}

![A checkpoint: scenarios run on the real program, failures go back to an agent](pathname:///img/diagrams/checkpoint-light.svg)
![A checkpoint: scenarios run on the real program, failures go back to an agent](pathname:///img/diagrams/checkpoint-dark.svg)

After a risky slice others build on, its scenarios run on the real program. A failure goes back to an agent; after four failed runs it is noted for Review and the build goes on. Then [Verify](verify.md) starts by itself.
