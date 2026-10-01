---
title: Build
description: Hand off the approved plan, build it slice by slice, and check it end to end as it goes.
---

![The Feature route with the build steps highlighted: Handoff to Simplify](pathname:///img/diagrams/track-build-light.svg)
![The Feature route with the build steps highlighted: Handoff to Simplify](pathname:///img/diagrams/track-build-dark.svg)

From the handoff on, the build runs by itself. It stops only for a decision that is yours.

| Step | What happens |
| --- | --- |
| **[Handoff](build/handoff.md)** | You pick the agent and model that build; the build starts from the plan, not the chat |
| **[Slices](build/slices.md)** | Each slice goes through every layer, task by task, test first |
| **[End-to-end checks](build/checks.md)** | After marked slices, the real program runs and the evidence is kept |
| **[Simplify](build/simplify.md)** | One pass makes the whole change simpler, with the same behaviour |

![Three slices, each through every layer, each starting with a failing test and ending with an end-to-end run; then one pass simplifies the whole change](pathname:///img/diagrams/slices-light.svg)
![Three slices, each through every layer, each starting with a failing test and ending with an end-to-end run; then one pass simplifies the whole change](pathname:///img/diagrams/slices-dark.svg)

## When the build needs you

- a change would touch what you decided: the agent asks one question in its chat;
- an end-to-end check fails three times: continue, pivot or abandon.

Logins, secrets and permissions are settled in the outline, before the handoff, so the build does not stop for them.
