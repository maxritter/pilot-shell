---
title: Overview
description: The routes a task can take, and every place it waits for you.
---

For each request, your agent draws the route it suggests in the chat, with the steps that wait for you and the optional ones. It asks you once: start as shown, switch some optional steps off for this task, or take a different route. Each step writes its documents into `docs/plans/` in your repository.

![Four routes: Feature runs every step, Product feature writes a PRD and a TDD in place of the frame and the design, Bug finds the cause before the fix, Quick change goes straight to a test and the change; the optional quality pass is dashed](pathname:///img/diagrams/routes-light.svg)
![Four routes: Feature runs every step, Product feature writes a PRD and a TDD in place of the frame and the design, Bug finds the cause before the fix, Quick change goes straight to a test and the change; the optional quality pass is dashed](pathname:///img/diagrams/routes-dark.svg)

- **Feature:** [Plan](plan.md) → [Build](build.md) → [Check and ship](check.md). You approve every planning document before any code exists.
- **Product feature:** the same steps, with a PRD and a TDD in place of the frame and the design. See [the product route](plan.md#for-product-managers-the-product-route).
- **Bug:** the same as a feature, with [Diagnose](plan/diagnose.md) in place of research and design.
- **Quick change** and **quick fix:** see below.

## Quick change

For a rename, a setting or an obvious fix; a quick fix is the same for a small bug. No planning documents, but it still starts with a failing test and is still checked before you approve it. If it turns out bigger, the agent moves it to the Feature route.

![A quick change: a failing test, the change, a check and your approval; a bigger task moves to the Feature route](pathname:///img/diagrams/quick-light.svg)
![A quick change: a failing test, the change, a check and your approval; a bigger task moves to the Feature route](pathname:///img/diagrams/quick-dark.svg)

## Where a task waits for you

| When | What you do |
| --- | --- |
| A planning document is ready | Approve it, or comment and request changes |
| Handoff | Choose who builds, paste the build prompt |
| A change would touch what you decided | Answer one question in your agent's chat |
| A check fails three times | Continue, change the approach, or stop |
| The change has passed its checks | Give the final approval |

These stops are always on, whatever optional steps you switch off. In between, the agent works on its own, and the Cockpit [notifies you](../cockpit.md#notifications) when something waits.

## Optional steps

Eight steps are optional and on by default: the outline cold read, the second opinion, end-to-end checks after marked slices, and a quality pass of Simplify, Test gaps, Security review, Docs update and UI review. The Cockpit draws them dashed. [Settings](../reference/settings.md#optional-steps) sets which are on for new tasks; the start question and the [handoff](build/handoff.md) change them for one task.

## Who does the work

![You and your agent write the plan documents; helper agents research, build, test, run the quality pass and check from them; a second AI from another vendor reviews](pathname:///img/diagrams/agents-light.svg)
![You and your agent write the plan documents; helper agents research, build, test, run the quality pass and check from them; a second AI from another vendor reviews](pathname:///img/diagrams/agents-dark.svg)

You choose one model for your helper agents per coding agent, and one for the second opinion, in [Settings](../reference/settings.md).
