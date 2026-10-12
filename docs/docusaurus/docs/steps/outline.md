---
title: Outline
description: After you approve the Plan, the build session cuts it into slices, then builds them. The Outline needs no approval from you.
---

![The eight steps, with Outline highlighted](pathname:///img/diagrams/track-outline-light.svg)
![The eight steps, with Outline highlighted](pathname:///img/diagrams/track-outline-dark.svg)

The Plan says what the change is; the Outline says how it is built, slice by slice. The session you start after approving the Plan writes it from the Plan in a few minutes, then builds it in the same session. **You do not approve it.**

![Outline: the build order, the slices, how each Done means point is proved and the check by a second reader](pathname:///img/diagrams/outline-light.svg)
![Outline: the build order, the slices, how each Done means point is proved and the check by a second reader](pathname:///img/diagrams/outline-dark.svg)

## What is in it {#what-the-agent-does}

| Part | What it holds |
| --- | --- |
| **Slices** | The change cut into slices that each work end to end and can be checked alone; the first is the thinnest path that works. A small change is one slice of one to three tasks. Each task card is short: what to do, which files, the test to write first |
| **Build order** | Which slices build side by side because they share no files, and which risky slice is tried on the running program first |
| **How each point is proved** | Every point of **Done means**, with the scenario that proves it |
| **Gaps checked** | Cancelling, empty or duplicate input, the limits, two things at once. Each real gap becomes a scenario or a line under *Not doing* |
| **Every command the build will run** | In the whole file, so nothing runs unseen. A push, deploy, publish or outside call is refused unless the Plan's **Before the build** allows it |

The Outline follows the Plan's size: fewer, larger tasks build faster than many small ones. For a risky Plan, or a build of four or more slices, a second agent also reads the Outline as a builder would, looking for cards nobody could build and points nothing proves; the build session fixes what it finds.

## What you do {#what-you-do}

Start the build with the prompt the App shows once you approve the Plan ([Start Implement](implement.md#start-implement)). A build session you started before approving waits for your approval, then writes the Outline and builds. You can read the Outline and comment on any slice; the build reads your comment.

Next: [Implement](implement.md).
