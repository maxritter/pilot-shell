---
title: Implement
description: Start the build in the App or your terminal. Your agent works through tested slices until the final review.
---

![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start Implement {#start-implement}

Once you approve the Plan, Implement shows your build defaults from [Settings](../reference/settings.md#defaults). The unreleased App-run candidate offers **Here in the App** and **In my terminal**. The first opens the agent's interactive window; the second shows the command to copy into a terminal, IDE or agent app. Windows uses the terminal option for now. The build works from the approved Plan and Outline.

:::note Local candidate
App runs are still undergoing qualification and have not been released. The screenshots below show illustrative tasks, not installed-App verification.
:::

![Implement Start: the agent, model and workers, branch choice, permissions, Here in the App and In my terminal, and Start the build](pathname:///img/app/implement-start-light.webp)
![Implement Start: the agent, model and workers, branch choice, permissions, Here in the App and In my terminal, and Start the build](pathname:///img/app/implement-start-dark.webp)

*Example task in a fictional project.*

| On the card | What it picks |
| --- | --- |
| **Build with** | Claude Code, Codex or another agent (one prompt to paste) |
| **Orchestrator** | The model that hands out slices and reads each report; it writes no code. A small Plan builds in one session, and this reads **Builder** |
| **Workers** | The model that writes the code, one slice each. **No subagents** keeps it all in one session |
| **Effort for both** | One effort for the session and every worker |
| **Runs as** | A plain prompt, or **Goal** where your agent has a keep-going mode |
| **Where agents run** | **Here in the App** or **In my terminal** |
| **Permissions** | **Your agent's own settings**, **Fewer prompts** or **Bypass prompts**; Bypass needs a separate confirmation for this run |
| **Session** | App runs start a fresh session. The terminal option can reuse this session or start a new one |
| **Works in** | The checked-out project. A new worktree is a separate planning choice; it is unavailable for starting an approved build |
| **Hand to the team** | A teammate builds it instead ([Hand over](../team/plans.md#hand-over)) |

**Change** sets any of these for this build only.

Choose Claude Code or Codex and **Here in the App**, then press **Start the build** to start one run. Its window shows the agent's own prompts, including folder trust. Folding it or opening another task leaves the run working. A second start is refused while the task's build is active; **Start anyway** is an explicit choice when work is already running in an external terminal.

**Interrupt** sends the agent's interrupt key. It does not end the process. **Stop** ends the run and its confirmed helpers. When stopped, **Open the session** opens the conversation without continuing; **Resume here** continues the task. Changing settings between turns offers **Restart with these settings**. See [App controls and permissions](../app.md#agent-runs).

### Where the build lands {#where-it-lands}

**Lands on** names your checked-out branch and the branch the pull request goes into. Choose **Stay on**, or **Start on a new branch** named `ql/<task>`; nothing changes until you pick. On your main branch the row turns amber, since a pull request cannot come from the branch it goes into. From a terminal, `qualitylayer branch new [name]` does the same. QualityLayer never merges or pushes a branch on its own.

## While agents build

![Implement in the App: the slices with their task cards and progress, while the build runs](pathname:///img/app/implement-light.webp)
![Implement in the App: the slices with their task cards and progress, while the build runs](pathname:///img/app/implement-dark.webp)

*Example task in a fictional project.*

The **Build** page shows the slices, changed files and checks as they happen. Each slice is written test first, and slices that share no files build side by side. QualityLayer runs and records every check itself, so you never rely on the agent's word for a result.

Your agent does not stop to ask. When something does not go as planned, it takes the recommended way and lists it under **Decided while building**, where you can **Ask why**. The one exception is something only you can give, such as a login, a secret or access only you hold: **Your turn** names the slice that needs it. Set it in your own environment and press **It's set**; the App never takes the secret. Other slices keep building; when no other work remains, the agent waits for that need to be resolved.

Comment on any slice while it builds, or write to your agent at any time. The full record, `05-implement.md`, is in **Files**.

## Checkpoints {#checkpoints}

![A checkpoint after a risky slice: its scenarios run on the real program, a failure goes to an agent to fix and runs again, and after four failed runs it is recorded as open while the build goes on](pathname:///img/diagrams/checkpoint-light.svg)
![A checkpoint after a risky slice: its scenarios run on the real program, a failure goes to an agent to fix and runs again, and after four failed runs it is recorded as open while the build goes on](pathname:///img/diagrams/checkpoint-dark.svg)

After a risky slice that two or more slices build on, its scenarios run on the real program. A failure goes to an agent to fix; after four failed runs it is noted for the final review and the build goes on.

When the last slice is built, [Verify](verify.md) starts by itself.
