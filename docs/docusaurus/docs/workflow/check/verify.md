---
title: Verify
description: Optional extra checks, then an AI that did not build the change checks it against what you asked for, and keeps the evidence.
---

![The Feature route with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The Feature route with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify has two parts. First the optional [quality pass](#the-quality-pass) works on the change. Then the tests, linter, type checks and build run. A fresh helper that did not write the code runs the scenarios on the real program and checks every point of your Done means. If your agent cannot start helpers, it does this itself and the record says so.

![The Verify tab: rounds, then automated checks, Done means and scenarios, each with PASS and its evidence](pathname:///img/diagrams/verify-light.svg)
![The Verify tab: rounds, then automated checks, Done means and scenarios, each with PASS and its evidence](pathname:///img/diagrams/verify-dark.svg)

## The quality pass

When the last slice is built, each optional step that is on runs in its own fresh helper, one after the other:

| Step | What it does | Time limit |
| --- | --- | --- |
| **[Simplify](../build/simplify.md)** | Makes the whole change simpler, one commit per change | none |
| **Test gaps** | Adds the missing edge-case and error-path tests. A new test that fails is a defect: your agent fixes the code, test first, before the next step | 10 minutes |
| **Security review** | Looks for severe vulnerabilities in the change, from the trust boundaries it touches. It reads only; it never builds or runs anything | 10 minutes |
| **Docs update** | Brings the README, the docs and the changelog in line with the change | 5 minutes |
| **UI review** | For a task with a screen: compares the running app with the design's mockups | 10 minutes |

A Critical or High security finding is fixed by your agent, test first, and then checked again before the judge starts. Medium and Low findings are listed in the *Security* section of the pull request description and block nothing. A helper that runs out of time says what it checked and what it did not.

In the Cockpit, the Verify tab shows these steps in a dashed band above the judge, each with its result. A step you switched off stays visible, struck through. After a failed round, only the judge runs again.

## In the Cockpit

| Part | What it shows |
| --- | --- |
| Quality pass | Each optional step, its state and what it found |
| Rounds | Each complete check, who ran it, and whether it passed |
| Result cards | The automated checks, each task's definition of done, each scenario, the goal results and a review of the diff, each marked PASS, FAIL or MISSING |
| Evidence | The output, screenshot or file behind each result |

While a round runs, the tab says what it is checking now. The records are kept under *Quality pass* and *Verification* in `04-build.md`.

## What happens next

- **Pass:** on to [Review](review.md).
- **Fail:** the build fixes the gaps and the next round starts by itself.
- **Three failures in a row:** the task [stops for you](stops.md).
- **Accept as is:** if you decide the build is good enough, press **Accept as is** in the Cockpit, in Verify or when the task has stopped. The task goes to Review without another judge run, and the review lists what was left open: the judge's failed lines, steps not done and open security findings. Only you can do this, and the final approval still follows.

With the [second opinion](../../reference/settings.md#second-opinion) on, the other vendor's AI also reviews every plan document, the build record and the code change. A simplification that broke something is undone.
