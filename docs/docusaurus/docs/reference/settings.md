---
title: Settings
description: Global Settings, your and your team's instructions, project memory and the changes you can ask for on one task.
---

Open **Settings** with the gear at the bottom of the sidebar. Changes save at once and apply to every project on this computer.

## Memory (next release)

Pause local memory, search saved lessons or retire one that no longer applies. **Manage projects** opens a searchable list where you enable Git sharing separately for each repository. Your choice stays local to this computer. See [Project memory](../memory.md) for privacy, Pilot imports and command-line use.

![Settings, Workflow: the Level card with its two choices, the Planning and Building cards with a tab per agent, Independent review, Second opinion and Notifications, beside the tabs Licence, Team and About](pathname:///img/app/settings-light.webp)
![Settings, Workflow: the Level card with its two choices, the Planning and Building cards with a tab per agent, Independent review, Second opinion and Notifications, beside the tabs Licence, Team and About](pathname:///img/app/settings-dark.webp)

## Workflow

### Level {#level}

| Choice | A new task starts as |
| --- | --- |
| **Engineering** (default) | The full technical plan, with contracts, files and tests in view |
| **Product** | A product brief in product words, with engineering detail folded away |

Each task keeps its level; change it in the task header until you approve the Plan ([two levels](../intro.md#two-levels)).

### Your instructions {#instructions}

Your own standing instructions for every task, in every project: coding standards, things never to do, how you like a Plan written. **Edit** opens a Markdown editor with **Write** and **Preview**. **Start from an outline** gives you a few headings to fill in, and the text holds up to 12,000 characters. The text is kept in `~/.qualitylayer/instructions.md`, so you can also edit it there.

Your agent receives the text once per step, inside that step's workflow text, and follows it like your repository's own rules. Helpers, reviewers and the judge read it too. It is never copied into a task's documents. A heading named after a step (`## Plan`, `## Implement`, `## Verify`, …) keeps the lines under it for that step alone; lines under no step heading apply to every step. An edit reaches a running task at its next step reply.

Your team's instructions come first and win where the two disagree ([Team](#team)). Neither can switch off an approval: a line asking the agent to approve a gate itself is passed on and approves nothing.

### Planning and Building {#defaults}

Each card has a tab per agent: **Claude Code**, **Codex** and **Another agent**. The tab marked **Default** is the one **+ New** and Implement open on; **Make default** moves the mark, so you can plan with Claude Code and build with Codex. **Use recommended** resets a tab.

| Card | Used for | Recommended |
| --- | --- | --- |
| **Planning** | Discuss to Outline | The most capable model you can afford (Opus 5.5 or Fable 5.1), High effort or more |
| **Building** | [Implement](../steps/implement.md#start-implement) | Opus 5.5 orchestrator (or Fable 5.1), Sonnet 5.5 workers, High effort, a plain prompt, in the session that planned the task |

**Another agent** uses the models set in that agent, so there is nothing to pick here.

**No subagents** as the workers makes the session build and check everything itself, with no fresh agent anywhere, Polish included. The recommended setup keeps the workers: a fresh Polish agent adds the tests the build missed, and without it a medium change's own tests caught fewer planted faults ([Verify](../steps/verify.md#lanes)).

### Independent review {#independent-review}

An agent that never wrote the code decides whether a risky change passes [Verify](../steps/verify.md): **Fresh agent: When risky** (recommended) or **Always**. On a change that is not risky, the build session runs the same review itself and the page marks it **not independent**; measured, that changed nothing the checks catch on small and medium changes and saved the review's time and cost, while on a risky change the fresh agent found a security fault the checks missed. Pick its model for Claude Code (Opus 5.5) and for Codex (GPT-6.1 Sol), or switch it off.

### Second opinion {#second-opinion}

With Claude Code and Codex both installed, each reviews the other's work:

| When | Choices | What it reads |
| --- | --- | --- |
| **On the Plan** | **When risky** (recommended) or **Always** | Discuss, Research and the first full Plan draft, before the Plan reaches you |
| **On the built change** | **When risky** (recommended) or **Always** | The finished code, as [Verify's](../steps/verify.md#lanes) fifth check |

A change is risky when the Plan says so, when it touches sign-in, secrets or outside input, or when the Outline marks a slice risky. **Always** sends every Plan or every change to the other agent, a few minutes more each; if you picked **Always** before, it stays. With only one agent installed, a separate reviewer of that agent (Sonnet 5.5 in Claude Code) reads instead. **Reviewed by** in the Plan names who read it.

### Notifications {#notifications}

**Notifications** tell you when something needs you, or a task ships or stops. **Open comments by themselves** switches the right sidebar to Comments when a teammate writes to you, never while you type.

## For one task {#for-one-task}

Tell your agent in words: "skip security", "run a checkpoint after every slice", "get a second opinion", "no second opinion". A small change skips the second read of its Outline; ask to bring it back, or say "skip polish" to leave Polish out. No setting turns an approval off.

## Licence

Your plan or the days left of your trial. **Open billing account** opens qualitylayer.dev/billing for your subscription, invoices, seats and payment method. **On another computer** shows the command that moves your licence; if no activation is free, run `qualitylayer licence deactivate` on the old machine or write to mail@maxritter.net. The tab also lists what contacts QualityLayer ([Files and privacy](files.md#privacy)).

## Team

Your name as your team sees it; **People and groups** with seats, members and their computers; **Team instructions**; **Slack**, connected once by the team owner, with each member's own digest and quiet hours ([Slack](../team/plans.md#slack)); and **Shared links**, each with **Copy** and **Revoke**.

### Team instructions {#team-instructions}

The team owner writes standing instructions for the whole team, in the same editor as [your own](#instructions). They reach every teammate's agent in each step, before the teammate's own instructions, and win where the two disagree. Teammates see them read-only with **View**, along with who changed them last and when. The text is encrypted on the owner's computer with the team's key; the server keeps only the encrypted copy. Each computer keeps a local copy, so the instructions still apply while the team service cannot be reached. When two owner windows save at once, the second one is shown the newer text instead of overwriting it.

## About

The version, **Check now**, and what's new ([Updates](../install.md#updates)).
