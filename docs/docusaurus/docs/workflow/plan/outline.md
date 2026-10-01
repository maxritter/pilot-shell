---
title: Outline
description: The build plan, in slices of test-first tasks, with the end-to-end checks and everything to settle before the build.
---

![The Feature route with Outline highlighted](pathname:///img/diagrams/track-outline-light.svg)
![The Feature route with Outline highlighted](pathname:///img/diagrams/track-outline-dark.svg)

The outline turns the approved design, or a bug's diagnosis, into an ordered plan of slices. A slice is a thin piece of the change that works end to end on its own.

![An outline: slices of test-first tasks, end-to-end checks after marked slices, and what you settle before the build](pathname:///img/diagrams/outline-light.svg)
![An outline: slices of test-first tasks, end-to-end checks after marked slices, and what you settle before the build](pathname:///img/diagrams/outline-dark.svg)

## In the Cockpit

| Part | What it shows |
| --- | --- |
| Slices | Each slice with its tasks, in build order |
| Task cards | The files, the design contract, the test to write first, and the definition of done |
| End-to-end checks | The scenarios that run on the real program, and after which slice |
| Before the build | Everything you must decide, grant or provide, such as a login, a secret or a permission, each marked met or granted |

`03-outline-overview.md` is for you; `03-outline.md` holds the full task cards. You can comment on any slice, task or scenario.

The outline settles every step that needs you before the handoff. Where your agent can do a step itself, such as running a deploy command, it proposes to do it with a permission you grant once. The outline cannot be put up for your review while a step is still open. After you approve it, the build runs from handoff to verification without waiting for you, except for a decision that is yours.

Before you see it, a helper reads the whole plan the way a new builder would and reports where it would get stuck. Your agent fixes those gaps first.

## You decide

Check the scope, the order, where the checks run, and what you have to settle before the build. Approval leads to [Handoff](../build/handoff.md).
