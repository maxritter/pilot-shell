---
title: Outline
description: The Outline orders the tested slices. The build session writes it from the approved Plan; a small task can have it ready earlier. You do not approve it again.
---

![The workflow, with Outline highlighted](pathname:///img/diagrams/track-outline-light.svg)
![The workflow, with Outline highlighted](pathname:///img/diagrams/track-outline-dark.svg)

The Plan says what changes; the Outline says how it is built, slice by slice. The build session writes it from the approved Plan, then continues through Implement and Verify until human Review. **You do not approve the Outline again.**

![Outline: build order, slices, and how each Done means point is proved](pathname:///img/diagrams/outline-light.svg)
![Outline: build order, slices, and how each Done means point is proved](pathname:///img/diagrams/outline-dark.svg)

## What is in it {#what-the-agent-does}

| Part | What it holds |
| --- | --- |
| **Slices** | Pieces that each work end to end, thinnest first, with the test to write first |
| **Build order** | The order the slices are built in, and which slices are risky |
| **Proof** | The scenario that proves each **Done means** point |
| **Commands** | Every command the build will run. A push or deploy needs the Plan's permission |

The build map lists the slices in the order they are built. Open a slice for its tasks and tests. Each **Done means** point links to the scenario and slice that prove it.

The build session works through the cards in this order. Cards name source files; a file outside the cards needs no amendment, and Review lists it. Check output and pictures stay in the task’s records.

## What you do {#what-you-do}

[Start the build](implement.md#start-implement). You can follow progress or comment on a slice. Human-only prerequisites that are missing stay unverified for Review while available work continues. They create no new approval here.

Next: [Implement](implement.md).
