---
title: Plan
description: Frame, research, design and outline, each approved by you before any code is written.
---

![The Feature route with the planning steps highlighted: Frame to Outline](pathname:///img/diagrams/track-plan-light.svg)
![The Feature route with the planning steps highlighted: Frame to Outline](pathname:///img/diagrams/track-plan-dark.svg)

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
| Frame | `00-frame.md` | `00-frame-details.md` |
| Research | `01-research.md` | `01-research-details.md` |
| Diagnose | `01-diagnosis.md` | `01-diagnosis-details.md` |
| Design | `02-design.md` | `02-design-details.md` |
| Outline | `03-outline-overview.md` | `03-outline.md` |

## While the agent writes

Each document opens in the Cockpit from its first draft. You can read it, comment and press **Request changes** while your agent is still writing; **Approve** stays locked, with the reason in its tooltip, until your agent puts the document up for your review and any [second opinion](plan/design.md#the-second-opinion) is back.

When a later step teaches something that belongs in an earlier document, your agent writes it there as a marked **Added in design** block (or research, or outline). It is listed at the top of the review it came with, and you approve it together with that step.

[Files and privacy](../reference/files.md) shows the whole task folder.
