---
title: Overview
description: The three routes a task can take, and every place it waits for you.
---

Your agent suggests a route for each request, and you can change it. Each step writes its documents into `docs/plans/` in your repository.

![Three routes: Feature runs every step, Bug finds the cause before the fix, Quick change goes straight to a test and the change](pathname:///img/diagrams/routes-light.svg)
![Three routes: Feature runs every step, Bug finds the cause before the fix, Quick change goes straight to a test and the change](pathname:///img/diagrams/routes-dark.svg)

- **Feature:** [Plan](plan.md) → [Build](build.md) → [Check and ship](check.md). You approve every planning document before any code exists.
- **Bug:** the same, with [Diagnose](plan/diagnose.md) in place of research and design.
- **Quick change:** see below.

## Quick change

For a rename, a setting or an obvious fix. No planning documents, but it still starts with a failing test and is still checked before you approve it. If it turns out bigger, the agent moves it to the Feature route.

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

These stops are always on. In between, the agent works on its own, and the Cockpit [notifies you](../cockpit.md#notifications) when something waits.

## Who does the work

![You and your agent write the plan documents; helper agents research, build, test, simplify and check from them; a second AI from another vendor reviews](pathname:///img/diagrams/agents-light.svg)
![You and your agent write the plan documents; helper agents research, build, test, simplify and check from them; a second AI from another vendor reviews](pathname:///img/diagrams/agents-dark.svg)

You choose the model for each job in [Settings](../reference/settings.md).
