---
title: Settings
description: Global Settings, your and your team's instructions, project memory and the changes you can ask for on one task.
---

Open **Settings** with the gear at the bottom of the sidebar. Changes save at once and apply to every project on this computer.

![Settings, Workflow: the Level card with its two choices, the Planning and Building cards with a tab per agent, Independent review, Second opinion and Notifications, beside the tabs Licence, Team and About](pathname:///img/app/settings-light.webp)
![Settings, Workflow: the Level card with its two choices, the Planning and Building cards with a tab per agent, Independent review, Second opinion and Notifications, beside the tabs Licence, Team and About](pathname:///img/app/settings-dark.webp)

## Memory {#memory}

Pause local memory, search saved lessons or retire one. **Manage projects** turns Git sharing on per repository; the choice stays on this computer. More in [Project memory](../memory.md).

## Workflow

### Level {#level}

| Choice | A new task starts as |
| --- | --- |
| **Engineering** (default) | The full technical plan, with contracts, files and tests in view |
| **Product** | A product brief in product words, with engineering detail folded away |

Each task keeps its level; change it in the task header until you approve the Plan ([two levels](../intro.md#two-levels)).

### Your instructions {#instructions}

Standing instructions for every task in every project: coding standards, things never to do, how you like a Plan written. **Edit** opens a Markdown editor; **Start from an outline** gives you headings to fill in. Up to 12,000 characters, kept in `~/.qualitylayer/instructions.md`.

| | How it applies |
| --- | --- |
| Who reads it | Your agent once per step, plus helpers, reviewers and the judge. Never copied into a task's documents |
| Per step | Lines under a step heading (`## Plan`, `## Implement`, `## Verify`, …) apply to that step only; other lines apply to all |
| Running tasks | An edit applies from the task's next step reply |
| Team instructions | Come first and win on conflict ([Team](#team-instructions)) |
| Approvals | No line can approve a gate |

### Planning and Building {#defaults}

Each card has a tab per agent: **Claude Code**, **Codex** and **Another agent**. **Make default** picks the tab that **+ New** and Implement open on, so you can plan with Claude Code and build with Codex. **Use recommended** resets a tab.

| Card | Used for | Recommended |
| --- | --- | --- |
| **Planning** | Discuss to Outline | The most capable model you can afford (Opus 5.5 or Fable 5.1), High effort or more |
| **Building** | [Implement](../steps/implement.md#start-implement) | Opus 5.5 orchestrator (or Fable 5.1), Sonnet 5.5 workers, High effort, a plain prompt, in the session that planned the task |

**Another agent** uses the models set in that agent.

**No subagents** makes the session build and check everything itself, Polish included. The recommended setup keeps workers: without a fresh Polish agent, a medium change's own tests caught fewer planted faults ([Verify](../steps/verify.md#lanes)).

### Independent review {#independent-review}

Who decides whether a change passes [Verify](../steps/verify.md): **Fresh agent: When risky** (recommended) or **Always**, or off. Pick its model for Claude Code (Opus 5.5) and Codex (GPT-6.1 Sol). On a change that is not risky, the build session reviews itself and the page marks it **not independent**. Measured: on small and medium changes this made no difference to what the checks catch and saved time and cost; on a risky change the fresh agent found a security fault the checks missed.

### Second opinion {#second-opinion}

With Claude Code and Codex both installed, each reviews the other's work:

| When | Choices | What it reads |
| --- | --- | --- |
| **On the Plan** | **When risky** (recommended) or **Always** | Discuss, Research and the first full Plan draft, before the Plan reaches you |
| **On the built change** | **When risky** (recommended) or **Always** | The finished code, alongside Polish and Security review in [Verify](../steps/verify.md#lanes) |

Risky means the Plan says so, the change touches sign-in, secrets or outside input, or the Outline marks a slice risky. **Always** adds a few minutes per Plan or change. With one agent installed, a separate reviewer of that agent reads instead (Sonnet 5.5 in Claude Code). **Reviewed by** in the Plan names who read it.

### Notifications {#notifications}

**Notifications** tell you when something needs you, or a task ships or stops. **Open comments by themselves** switches to Comments when a teammate writes to you, never while you type.

## For one task {#for-one-task}

Tell your agent: "skip security", "run a checkpoint after every slice", "get a second opinion", "no second opinion", "skip polish". A small change skips the second read of its Outline; ask to bring it back. No setting turns an approval off.

## Licence

Your plan or trial days left. **Open billing account** opens qualitylayer.dev/billing (subscription, invoices, seats, payment method). **On another computer** shows the command that moves your licence; if no activation is free, run `qualitylayer licence deactivate` on the old machine or write to mail@maxritter.net. The tab also lists what contacts QualityLayer ([Files and privacy](files.md#privacy)).

## Team

| Part | What it holds |
| --- | --- |
| Your name | How your team sees you |
| **People and groups** | Seats, members and their computers |
| **Team instructions** | See [below](#team-instructions) |
| **Slack** | Connected once by the team owner; each member sets digest and quiet hours ([Slack](../team/plans.md#slack)) |
| **Shared links** | Each with **Copy** and **Revoke** |

### Team instructions {#team-instructions}

The team owner writes instructions for the whole team in the same editor as [your own](#instructions). They reach every teammate's agent each step, before the teammate's own, and win on conflict. Teammates see them read-only with **View**, with who changed them last. The text is encrypted on the owner's computer with the team's key, and each computer keeps a local copy, so it applies offline too. If two owner windows save at once, the second sees the newer text instead of overwriting it.

## About

The version, **Check now**, and what's new ([Updates](../install.md#updates)).
