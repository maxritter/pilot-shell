---
title: Outline
description: While you read the Plan, your agent cuts it into slices. The Outline needs no approval from you.
---

![The seven steps, with Outline highlighted](pathname:///img/diagrams/track-outline-light.svg)
![The seven steps, with Outline highlighted](pathname:///img/diagrams/track-outline-dark.svg)

The Plan says what the change is. The Outline says how it is built, slice by slice. Your agent writes it while you read the Plan, so the build can start the moment you approve. You do not approve the Outline.

## What your agent does {#what-the-agent-does}

Once the Plan is ready for you, your agent writes `04-outline.md` while it waits for your decision:

- **Slices.** The change is cut into vertical slices, each of which works from end to end and can be checked on its own. The first is the thinnest path that works. Each slice has task cards: what to do, which files, the test to write first and how to know it is done.
- **Waves.** QualityLayer works out which slices can be built side by side because they share no files, and which risky slice is tried on the running program before the build goes on.
- **Scenarios and the one oracle.** Every point of **Done means** lands in a scenario that proves it, a definition of done, or the oracle: the single check that tells whether the whole change works.

If you ask for changes to the Plan, your agent applies them to the Plan first, then revises the Outline where a decision moved. A second agent that did not write the Outline reads it the way a builder would, looking for cards nobody could build and requirements nothing proves; your agent fixes what it finds.

## What you do {#what-you-do}

Nothing is required. You can read the Outline, comment on it, or start the build early: this page offers [Implement Start](implement.md#start-implement) once the Plan is approved, and a build session that starts before the Outline is finished waits for it, then begins by itself. A conflict with a decision you approved is recorded and reaches the final review; the build never asks you about it mid-way.

## The page {#the-page}

![Outline: the waves, the slices, how each Done means point is proved and the check by a second reader](pathname:///img/diagrams/outline-light.svg)
![Outline: the waves, the slices, how each Done means point is proved and the check by a second reader](pathname:///img/diagrams/outline-dark.svg)

The step page shows:

- **Summary:** how many slices and tasks, in what order, and what is risky.
- **How the build runs:** the waves, and where a risky slice is tried before the build goes on.
- **Slices,** each folded to its two-sentence story. Open one for its task cards.
- **Oracle,** and **Decided while outlining:** program-level calls with their reasons. Comment on one to change it.
- **How each point is proved:** each **Done means** point, the scenario that proves it and the slice it runs after.
- **Checked by a second reader:** the gaps found and fixed.

**More in this document** names what stays in the whole file: the program design, the shape of the code, the scenarios and every command the build will run, so nothing runs unseen. A command that pushes, deploys, publishes or reaches an outside address is refused unless **Before the build** in the Plan granted it.

Next: [Implement](implement.md).
