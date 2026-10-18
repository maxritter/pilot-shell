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
| **Build order** | Which slices build side by side; which risky one goes first |
| **Proof** | The scenario that proves each **Done means** point |
| **Commands** | Every command the build will run. A push or deploy needs the Plan's permission |

On a larger or risky build, a second agent checks that every card can be built.

The page shows the build map first, then the proof, in the order of `04-outline.md`. Nothing here waits for you, so there is no approval at the top. **Look here** lists each risky slice with its checkpoint, a gap the second agent found and the build session chose to keep, and an Outline that grew past the Plan's size. The build map groups the slices by wave, one row each with its number, title, task count and tags such as risky, checkpoint or depends on 4; open a row for the slice's story, its tasks and how it is validated, and a task opens its card. Under it, each **Done means** point is followed to the scenario that proves it and the slice after which it runs; points only you can confirm are marked. The decisions made while outlining and that second agent's check are collapsed, each with a one-line summary. The program design, the shape of the code, the scenarios and the commands are in the document.

Independent slices run side by side. When extra build waves are necessary, the Outline records why. Cards name source files; check output, pictures and other evidence stay in the task’s records.

## What you do {#what-you-do}

[Start the build](implement.md#start-implement). You can follow progress or comment on a slice. Missing human-only prerequisites stay unverified for Review while available work continues; they do not create another workflow approval here.

Next: [Implement](implement.md).
