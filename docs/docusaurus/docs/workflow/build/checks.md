---
title: End-to-end checks
description: The checks that run the real program after marked slices, and what happens when one keeps failing.
---

![The Feature route with Checkpoint highlighted](pathname:///img/diagrams/track-checkpoint-light.svg)
![The Feature route with Checkpoint highlighted](pathname:///img/diagrams/track-checkpoint-dark.svg)

After each slice the outline marks, a fresh helper runs the scenarios on the real program and keeps the test output, logs and screenshots. A pass lets the build go on by itself. These checks are on by default. Switch them off in [Settings](../../reference/settings.md#optional-steps), when a task starts, or at the handoff, and the marks in the outline stop holding up any slice.

![A checkpoint: after a slice the scenarios run; a pass goes on, a failure is fixed and run again, and three failures stop for you](pathname:///img/diagrams/checkpoint-light.svg)
![A checkpoint: after a slice the scenarios run; a pass goes on, a failure is fixed and run again, and three failures stop for you](pathname:///img/diagrams/checkpoint-dark.svg)

## In the Cockpit

| State | Meaning |
| --- | --- |
| Waiting | The slice is not built yet |
| Running | The helper is running the scenarios now |
| Passed | Every scenario held |
| Failed | A scenario failed; the build fixes it at the source and runs again |
| Stopped | Three runs failed; the build waits for you |

Open a check to see every run: the step that failed, what it showed, and the evidence.

## Where they go

The outline marks the slices where a check pays off: usually the first slice that runs at all, the first time everything works together, and the riskiest connection to another system. The last slice needs none, because verification follows.

## You decide, if one keeps failing

After three failed runs the build stops, and the agent asks you with its recommendation:

- **Continue:** keep the approach, try once more another way.
- **Pivot:** change the approach; the agent updates the plan with your words.
- **Abandon:** stop; the documents and finished slices stay.
