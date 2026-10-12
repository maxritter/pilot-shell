---
title: Implement
description: One command starts the build. From there your agent works on its own until the final review, in small slices, each tested.
---

![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-light.svg)
![The eight steps, with Implement highlighted](pathname:///img/diagrams/track-implement-dark.svg)

## Start Implement {#start-implement}

Once you approve the Plan, Implement shows the one command that starts the build, with your defaults from [Settings](../reference/settings.md#defaults). Copy it into a terminal, your IDE or a desktop app. The build works from the approved Plan, never from your planning chat.

![Implement Start in the App: Build with Claude Code, Codex or another agent, the model and effort in one line, the branch the build lands on, and the lines to type with a Copy button each](pathname:///img/app/implement-start-light.webp)
![Implement Start in the App: Build with Claude Code, Codex or another agent, the model and effort in one line, the branch the build lands on, and the lines to type with a Copy button each](pathname:///img/app/implement-start-dark.webp)

*Example task in a fictional project.*

| On the card | What it picks |
| --- | --- |
| **Build with** | Claude Code, Codex or another agent (one prompt to paste) |
| **Orchestrator** | The model that hands out slices and reads each report; it writes no code. A small Plan builds in one session, and this reads **Builder** |
| **Workers** | The model that writes the code, one slice each. **No subagents** keeps it all in one session |
| **Effort for both** | One effort for the session and every worker |
| **Runs as** | A plain prompt, or **Goal** where your agent has a keep-going mode |
| **Start in** | **This session** (the default: the card lists `/clear`, `/model`, `/effort` to type first), **New session** or **New worktree** |
| **Hand to the team** | A teammate builds it instead ([Hand over](../team/plans.md#hand-over)) |

**Change** sets any of these for this build only.

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
