---
title: Build
description: Hand off the approved plan, build it slice by slice, and check it end to end as it goes.
---

![The Feature route with the build steps highlighted: Handoff to Checkpoint](pathname:///img/diagrams/track-build-light.svg)
![The Feature route with the build steps highlighted: Handoff to Checkpoint](pathname:///img/diagrams/track-build-dark.svg)

From the handoff on, the build runs by itself. It stops only for a decision that is yours.

| Step | What happens |
| --- | --- |
| **[Handoff](build/handoff.md)** | You pick the agent and model that build and which optional steps run; the build starts from the plan, not the chat |
| **[Slices](build/slices.md)** | Each slice goes through every layer, task by task, test first |
| **[End-to-end checks](build/checks.md)** (optional) | After marked slices, the real program runs and the evidence is kept |

When the last slice is built, [Verify](check/verify.md) begins with the [quality pass](check/verify.md#the-quality-pass). Its optional steps [simplify](build/simplify.md) the change, add missing tests, review it for security and update the docs.

![Three slices, each through every layer, each starting with a failing test and ending with an end-to-end run; then an optional quality pass works on the whole change before Verify](pathname:///img/diagrams/slices-light.svg)
![Three slices, each through every layer, each starting with a failing test and ending with an end-to-end run; then an optional quality pass works on the whole change before Verify](pathname:///img/diagrams/slices-dark.svg)

## Optional steps

The end-to-end checks and the steps of the quality pass are optional, and all are on by default. Switch any of them off in [Settings](../reference/settings.md#optional-steps) for every new task, in the question your agent asks when a task starts, or at the handoff for this build only. The Cockpit shows them dashed, apart from the steps every task runs. Once the build has started, the list is fixed.

Every approval stays on, whatever you switch off.

## When the build needs you

- a change would touch what you decided: the agent asks one question in its chat;
- an end-to-end check fails three times: continue, pivot or abandon.

Logins, secrets and permissions are settled in the outline, before the handoff, so the build does not stop for them.
