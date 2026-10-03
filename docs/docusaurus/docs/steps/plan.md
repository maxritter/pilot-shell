---
title: Plan
description: The one document you approve before any code, with the decisions, the mockup, the slices and the checks that prove the change.
---

![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-light.svg)
![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-dark.svg)

The Plan is the one document you approve before any code is written. Decisions come first, as pictures and a clickable mockup. Then the slices, and the scenarios that prove the change works.

![The Plan: what changes as a picture, the decisions made for you, the trust boundary line, Approve, and the slices and scenarios the App draws from the details](pathname:///img/diagrams/plan-light.svg)
![The Plan: what changes as a picture, the decisions made for you, the trust boundary line, Approve, and the slices and scenarios the App draws from the details](pathname:///img/diagrams/plan-dark.svg)

## In the App

| Section | What it holds |
| --- | --- |
| Summary | The change in a few lines |
| What changes | One picture of the system after the change, and what changes in each part |
| Interface | For a change people see: one clickable mockup with its empty, loading and error states |
| Decided by you | The choices you made, with your answers |
| Decisions made for you | What your agent decided, and why. Comment on any of them to change it |
| Not doing | What stays outside this task |
| Before the build | What you must provide or grant first, such as a login or a permission |
| Slices and scenarios | Drawn by the App from the details: each slice with what works afterwards, and the end-to-end scenarios |

For a bug, What changes becomes the reproduction, the symptom and root cause, the behaviour you need and the fix.

The mockup shows as soon as it renders, and changes when you ask. Options side by side come only when you want to compare.

`02-plan.md` is what you review. `02-plan-details.md` holds what the builders read: the contracts, the patterns to follow, each slice with its task cards and the commands that check it, and the scenario steps.

## Lines that decide what runs later {#plan-lines}

| Line | What it does |
| --- | --- |
| `**Trust boundary:**` | `none`, or what crosses it: outside input, sign-in, secrets. Anything but `none` adds a security review to [Verify](verify.md) |
| `**Risky:** <why>` | On a slice, such as a new dependency or an outside system. That slice gets a [checkpoint](implement.md#checkpoints) |
| `**Shared output:**` | A slice that rebuilds a shared file never builds beside another slice with the same output |
| `**Project checks:**` | The tests, lint, type check and build that run once before the judge |
| `**Validation:**` | The commands that check each slice. Approving the Plan approves them |

Your agent states in one line what will run. For example: "3 slices, slices 1 and 2 side by side, a checkpoint after slice 3 (new mail service), no security review." You can change it in words, such as "skip security". See [Settings](../reference/settings.md#for-one-task).

## Before it reaches you

- **New things are tried first.** Your agent tries every new service, library or tool the Plan depends on, in a scratch folder, never in your project. The details record what was tried and what happened.
- **A fresh agent reads it cold.** It reads the Plan the way a new builder would and reports where it would get stuck. Your agent fixes those gaps first.
- **A big task gets a split proposal.** Above about 8 slices or 25 tasks, your agent proposes separate tasks.
- **The second opinion, when on,** reviews the Plan too. See [Settings](../reference/settings.md#second-opinion).

## You decide

Read it from the first draft. Select any line, table or diagram to comment, and press **Request changes** while your agent still writes. **Approve** unlocks once your agent puts the Plan up for review (`qualitylayer gate open 02-plan.md`). You can also type `approve` in your agent's chat.

When the build later teaches something that changes the Plan, your agent records it as an added block and asks you if it touches what you decided.

Next: [Implement](implement.md).
