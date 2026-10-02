---
title: Plan
description: Frame, research, design and outline, each approved by you before any code is written.
---

![The Feature route with the planning steps highlighted: Frame to Outline](pathname:///img/diagrams/track-plan-light.svg)
![The Feature route with the planning steps highlighted: Frame to Outline](pathname:///img/diagrams/track-plan-dark.svg)

## Before the first step

Every task starts with a picture in your agent's chat: the route it suggests, which steps wait for you, and which steps are optional. You answer one question: start as shown, switch some optional steps off for this task, or pick a different route. No task is created until you answer.

Every planning step writes a short document **for you** and a detailed one **for the agent**, and waits for your approval in the [Cockpit](../cockpit.md). A change of mind here costs minutes; after the build it costs days.

| Step | You review |
| --- | --- |
| **[Frame](plan/frame.md)** | The problem and Done means, the results you will accept the change by |
| **[Research](plan/research.md)** | How the code works today, with a picture and findings that point to the code |
| **[Diagnose](plan/diagnose.md)** | For a bug: how to reproduce it, its cause, what should happen instead |
| **[Design](plan/design.md)** | A clickable mockup, a picture of the system, every decision written down |
| **[Outline](plan/outline.md)** | Slices of test-first tasks, the end-to-end checks, and what you settle before the build |

![The Cockpit: a design under review with a system diagram, a teammate's comment and a clickable mockup](pathname:///img/diagrams/cockpit-light.svg)
![The Cockpit: a design under review with a system diagram, a teammate's comment and a clickable mockup](pathname:///img/diagrams/cockpit-dark.svg)

## The documents

| Step | For you | For the agent |
| --- | --- | --- |
| Frame (PRD on the product route) | `00-frame.md` | `00-frame-details.md` |
| Research | `01-research.md` | `01-research-details.md` |
| Diagnose | `01-diagnosis.md` | `01-diagnosis-details.md` |
| Design (TDD on the product route) | `02-design.md` | `02-design-details.md` |
| Outline | `03-outline-overview.md` | `03-outline.md` |

## For product managers: the product route

On the **Product feature** route, you review a PRD and a TDD in place of the frame and the design. The planning steps, the four approvals and the build that follows are the same as on the Feature route.

| Document | What it holds |
| --- | --- |
| **PRD** (product requirements document) | The problem, how you will know it worked, what the solution looks like with mockups, the alternatives considered, the first release and what is left out |
| **TDD** (technical design document) | The system design and the program design: how the parts fit together and where each new piece of code lives, for the engineers who read it |

The PRD takes the place of `00-frame.md` and the TDD of `02-design.md`, so the task's tabs read PRD, Research, TDD and Outline. [Copy](../cockpit.md#copy-a-document-out) either one into Confluence, Google Docs or Jira for people who do not use QualityLayer.

You do not set this route up. The first time you use QualityLayer, it asks whether you mostly work as a **Developer** or a **Product manager**, in the Cockpit or in your agent's chat. Change it any time in [Settings](../reference/settings.md#your-role). A product manager is then offered the product route for a new feature, and a developer the Feature route. Naming a PRD or a TDD in your request also offers the product route. At the start of every task you can pick another route.

## While the agent writes

Each document opens in the Cockpit from its first draft. You can read it, comment and press **Request changes** while your agent is still writing; **Approve** stays locked, with the reason in its tooltip, until your agent puts the document up for your review and any [second opinion](plan/design.md#the-second-opinion) is back.

When a later step teaches something that belongs in an earlier document, your agent writes it there as a marked **Added in design** block (or research, or outline). It is listed at the top of the review it came with, and you approve it together with that step.

[Files and privacy](../reference/files.md) shows the whole task folder.
