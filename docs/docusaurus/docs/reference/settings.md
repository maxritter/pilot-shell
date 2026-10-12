---
title: Settings
description: The four Settings tabs, Workflow, Licence, Team and About, and the changes you can ask for on one task.
---

Open **Settings** with the gear at the bottom of the sidebar. Changes save at once and apply to every project on this computer.

![Settings, Workflow: the Level card with its two choices, the Planning and Building cards with a tab per agent, Independent review, Second opinion and Notifications, beside the tabs Licence, Team and About](pathname:///img/app/settings-light.webp)
![Settings, Workflow: the Level card with its two choices, the Planning and Building cards with a tab per agent, Independent review, Second opinion and Notifications, beside the tabs Licence, Team and About](pathname:///img/app/settings-dark.webp)

## Workflow

### Level {#level}

| Choice | A new task starts as |
| --- | --- |
| **Engineering** (default) | The full technical plan, with contracts, files and tests in view |
| **Product** | A product brief in product words, with engineering detail folded away |

Each task keeps its level; change it in the task header until you approve the Plan ([two levels](../intro.md#two-levels)).

### Planning and Building {#defaults}

Each card has a tab per agent: **Claude Code**, **Codex** and **Another agent**. The tab marked **Default** is the one **+ New** and Implement open on; **Make default** moves the mark, so you can plan with Claude Code and build with Codex. **Use recommended** resets a tab.

| Card | Used for | Recommended |
| --- | --- | --- |
| **Planning** | Discuss to Outline | The most capable model you can afford (Opus 5.5 or Fable 5.1), High effort or more |
| **Building** | [Implement](../steps/implement.md#start-implement) | Opus 5.5 orchestrator (or Fable 5.1), Sonnet 5.5 workers, High effort, a plain prompt, in the session that planned the task |

**Another agent** uses the models set in that agent, so there is nothing to pick here.

**No subagents** as the workers makes the session build and check everything itself, with no fresh agent anywhere. It is faster and cheaper, but on a risky change the tests it writes catch far fewer faults ([Verify](../steps/verify.md#lanes)), so the recommended setup keeps the workers.

### Independent review {#independent-review}

On every task, an agent that never wrote the code decides whether the change passes [Verify](../steps/verify.md). Pick its model for Claude Code (Opus 5.5) and for Codex (GPT-6.1 Sol), or switch it off. A small change's review runs on the helpers' model (Sonnet 5.5 in Claude Code) unless you picked a model here yourself.

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

Tell your agent in words: "skip security", "run a checkpoint after every slice", "get a second opinion", "no second opinion". A small change skips Polish and the second read of its Outline; ask to bring either back. No setting turns an approval off.

## Licence

Your plan or the days left of your trial. **Open billing account** opens qualitylayer.dev/billing for your subscription, invoices, seats and payment method. **On another computer** shows the command that moves your licence; if no activation is free, run `qualitylayer licence deactivate` on the old machine or write to mail@maxritter.net. The tab also lists what contacts QualityLayer ([Files and privacy](files.md#privacy)).

## Team

Your name as your team sees it; **People and groups** with seats, members and their computers; **Slack**, connected once by the team owner, with each member's own digest and quiet hours ([Slack](../team/plans.md#slack)); and **Shared links**, each with **Copy** and **Revoke**.

## About

The version, **Check now**, and what's new ([Updates](../install.md#updates)).
