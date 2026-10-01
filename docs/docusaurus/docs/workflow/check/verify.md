---
title: Verify
description: An AI that did not build the change checks it against what you asked for, and keeps the evidence.
---

![The Feature route with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The Feature route with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

First the tests, linter, type checks and build run. Then a fresh helper that did not write the code runs the scenarios on the real program and checks every point of your Done means. If your agent cannot start helpers, it does this itself and the record says so.

![The Verify tab: rounds, then automated checks, Done means and scenarios, each with PASS and its evidence](pathname:///img/diagrams/verify-light.svg)
![The Verify tab: rounds, then automated checks, Done means and scenarios, each with PASS and its evidence](pathname:///img/diagrams/verify-dark.svg)

## In the Cockpit

| Part | What it shows |
| --- | --- |
| Rounds | Each complete check, who ran it, and whether it passed |
| Result cards | The automated checks, each task's definition of done, each scenario, the goal results and a review of the diff, each marked PASS, FAIL or MISSING |
| Evidence | The output, screenshot or file behind each result |

While a round runs, the tab says what it is checking now. The records are kept under *Verification* in `04-build.md`.

## What happens next

- **Pass:** on to [Review](review.md).
- **Fail:** the build fixes the gaps and the next round starts by itself.
- **Three failures in a row:** the task [stops for you](stops.md).

With the [second opinion](../../reference/settings.md#second-opinion) on, the other vendor's AI also reviews every plan document, the build record and the code change. After [Simplify](../build/simplify.md), a simplification that broke something is undone, not patched.
