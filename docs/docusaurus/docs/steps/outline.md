---
title: Outline
description: The Outline orders the tested slices. The build session writes it from the approved Plan; a small task can have it ready earlier. You do not approve it again.
---

![The eight steps, with Outline highlighted](pathname:///img/diagrams/track-outline-light.svg)
![The eight steps, with Outline highlighted](pathname:///img/diagrams/track-outline-dark.svg)

The Plan says what changes; the Outline says how it is built, slice by slice. The build session writes it from the approved Plan. **You do not approve it again.**

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

## What you do {#what-you-do}

[Start the build](implement.md#start-implement). Comment on any slice if you want.

Next: [Implement](implement.md).
