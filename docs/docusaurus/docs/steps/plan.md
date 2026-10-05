---
title: Plan
description: The one document you approve before any code. Your decisions come first, as a mockup and diagrams, then the slices and the checks that prove the change.
---

![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-light.svg)
![The five steps, with Plan highlighted](pathname:///img/diagrams/track-plan-dark.svg)

The Plan is the one document you approve before any code is written. Human taste and engineering judgement pay most here, because agents build from the Plan afterwards. So the App puts first the parts an agent should not settle alone, and the Plan itself follows as one readable document.

![The Plan waiting for approval: the step line with Request changes and Approve, the items that need you, and the line of what agents checked](pathname:///img/diagrams/plan-light.svg)
![The Plan waiting for approval: the step line with Request changes and Approve, the items that need you, and the line of what agents checked](pathname:///img/diagrams/plan-dark.svg)

## What needs you {#items}

Your agent asks these in the terminal, one at a time, in this order. The App beside it reads "Waits for your approval", shows only what the current question is about, and folds the rest. The items:

1. **The mockup.** For a change people see: one clickable mockup with its empty, loading and error states, sandboxed. Looks right or Change, with a pin on the spot.
2. **Engineering decisions.** Each decision that changes behaviour comes with its diff or its diagram. Agree or Change.
3. **Done means**, from [Discuss](discuss.md). Unchanged since you looked, with your comments answered.
4. **Decided by the agent.** The choices your agent made for you, each with its reason. **Keep all**, or change one. The first few show; the rest open with **Show**.
5. **Extra review.** How much more review the risk deserves, such as "None planned: no login, secret or outside input changes". **Agree**, or **Add a review**: a security review, or a second opinion from the other vendor's AI.
6. **Decided with you in Discuss.** One settled line, with **Revisit**.

When nothing needs a closer look, the App says so: "Nothing needs a closer look; read the Plan and approve."

You can also comment anywhere in the Plan, on anything your agent does not ask. The App records each answer you give in the terminal as "answered in the chat".

### Diagrams you can comment on {#diagrams}

![An engineering decision as a diagram: a pinned comment opens a thread, the agent answers in it and changes the Plan](pathname:///img/diagrams/decision-light.svg)
![An engineering decision as a diagram: a pinned comment opens a thread, the agent answers in it and changes the Plan](pathname:///img/diagrams/decision-dark.svg)

Engineering judgement is easiest on a picture of the change. Each engineering item carries its diagram: the architecture after the change, the sequence of a flow that crosses programs, or the decision a rule makes. They are drawn in the App's own colours. Click a node or an arrow to pin a comment. The thread stays on the diagram, your agent answers there and the Plan changes with it. The same pins work on the share page for a teammate.

## Checked by agents

One violet line says what agents proved before the Plan reached you, for example: a second agent read the Plan on its own and found nothing missing; two facts tested on the live service, with the output saved; nine research questions answered. The chevron opens the reports.

## The Plan itself

| Section | What it holds |
| --- | --- |
| Summary | The change in a few lines |
| What changes | A picture of the system after the change, and what changes in each part |
| Out of scope · Assumptions | What stays outside this task, and what the Plan rests on. Each assumption names the task that depends on it. When you did not know an answer in Discuss, your agent takes its recommendation and lists it here as *unconfirmed*, so you can ask the teammate who knows |
| The build | The slices, each with one sentence on what works afterwards |
| How we'll know it works | The scenario titles that prove the change |
| For the agent | Contracts with their diffs, and each slice's task cards with their files and checks. Behind the **For the agent** switch, since builders read them |

For a bug, What changes becomes the reproduction, the symptom and root cause, the behaviour you need and the fix.

`02-plan.md` is what you review. `02-plan-details.md` holds what the builders read: the contracts, the patterns to follow, each slice with its task cards and the commands that check it, and the scenario steps. The **For the agent** switch at the end of the step tabs shows `02-plan-details.md` next to **For you**, with the number of open comments on each. You and your teammates can comment on either.

## Lines that decide what runs later {#plan-lines}

| Line | What it does |
| --- | --- |
| `**Trust boundary:**` | `none`, or what crosses it: outside input, sign-in, secrets. Anything but `none` adds a security review to [Verify](verify.md) |
| `**Risky:** <why>` | On a slice, such as a new dependency or an outside system. That slice gets a [checkpoint](implement.md#checkpoints) |
| `**Shared output:**` | A slice that rebuilds a shared file never builds beside another slice with the same output |
| `**Project checks:**` | The tests, lint, type check and build that run once before checking starts |
| `**Validation:**` | The commands that check each slice. Approving the Plan approves them |

Your agent states in one line what will run. For example: "3 slices, slices 1 and 2 side by side, a checkpoint after slice 3 (new mail service), no security review." You can change it in words, such as "skip security". See [Settings](../reference/settings.md#for-one-task).

## Before it reaches you

- **New things are tried first.** Your agent tries every new service, library or tool the Plan depends on, in a scratch folder, never in your project. Every try that counts as met links a file in `evidence/` with what happened, so Verify can use it.
- **A second agent reads it on its own.** It reads the Plan the way a new builder would and reports where it would get stuck. Your agent fixes those gaps first.
- **A big task gets a split proposal.** Above about 8 slices or 25 tasks, your agent proposes separate tasks.
- **A risky Plan gets a second opinion.** When the Plan crosses a trust boundary or marks a slice risky, the other vendor's AI reviews it too. Each of its findings is an item with your agent's own answer: **Change the Plan** or **Keep it**. See [Settings](../reference/settings.md#second-opinion).

## With reviewers {#reviewers}

One row under the step line shows who is reading: "Anna is reading · Ben approved". **Ask someone else** adds a reviewer, and **Approve without waiting for Anna** lets you go on when a required reviewer has not answered. A teammate's comment is an item with **Reply** and **Resolve**. See [Review plans as a team](../team/plans.md).

## When you ask for changes

Your agent answers each note and changes the Plan. The Plan comes back as "Waits for your approval · revision 2":

- Only your notes return, each with the agent's answer.
- Every part that changed carries **changed since your review**.
- What you settled stays settled, in one line.
- **Show the Plan's diff** opens the line-by-line change.

## You decide

When your agent puts the Plan up for review (`qualitylayer gate open 02-plan.md`), it asks one question per engineering decision, then the last one: "Approve the Plan?", with **Approve**, **Request changes** or **Review in the App first**. Answer in the terminal. You can also type `approve` in your agent's chat.

If you answered **Change** on any decision, an Approve becomes a request for changes that carries those answers. **Request changes** takes your words. Your agent revises the Plan and asks again.

After you approve, the App opens [Implement](implement.md) by itself. When the build later teaches something that changes the Plan, your agent records it as an added block and asks you if it touches what you decided.

Next: [Implement](implement.md).
