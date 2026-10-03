---
title: Verify
description: Polish and a security review, then an AI that did not write the code checks the change against your request and keeps the evidence.
---

![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts by itself when the last slice is built. You have nothing to do here unless it stops for you.

## Polish and Security {#polish}

Two helpers work on the whole change, side by side:

| Helper | What it does |
| --- | --- |
| **Polish** | Removes near-copies and code nothing uses, adds missing edge-case and error-path tests, and fixes docs the change made wrong. For a change people see, it compares the running screens with the mockup. One commit per change |
| **Security** | Runs only when the change crosses a trust boundary: outside input, sign-in, secrets, files from users or other processes. It reads only and changes nothing |

Polish runs targeted tests after each change and the full suite once at the end. A critical or high security finding goes to a fresh agent to fix, test first, and is checked again before the judge starts. Medium and low findings are listed in the *Security* section of the pull request description and block nothing.

## The judge

Then QualityLayer runs the project's tests, lint, type check and build once and records the result. An AI that did not write the code, Opus 5.5 by default, checks the change:

- every point of your Done means, against the running program;
- every scenario and every task's definition of done;
- the whole diff, for bugs and for code outside what the Plan named.

It cites the checks QualityLayer recorded and runs again only what it doubts. Every result keeps its evidence: the output, a screenshot or a file.

![The Verify tab: rounds on the left, then the recorded checks, Done means and scenarios, each with PASS and its evidence](pathname:///img/diagrams/verify-light.svg)
![The Verify tab: rounds on the left, then the recorded checks, Done means and scenarios, each with PASS and its evidence](pathname:///img/diagrams/verify-dark.svg)

## In the App

| Part | What it shows |
| --- | --- |
| Polish and Security | Each helper, its state and what it found |
| Rounds | Each judge run, and whether it passed |
| Result cards | The recorded checks, Done means, the scenarios, each task's definition of done and the diff review, each marked PASS, FAIL or MISSING |
| Evidence | The output, screenshot or file behind each result |

The records are kept under *Quality pass* and *Verification* in `03-build.md`.

## What happens next

- **Pass:** on to [Review](review.md).
- **Fail:** a fresh agent fixes the gaps, and the judge checks again what the fix could reach.
- **Two failed judge runs:** the task stops for you.

With the [second opinion](../reference/settings.md#second-opinion) on, an AI from the other vendor also reviews the built change.

## When it stops {#when-it-stops}

After two failed judge runs, the task stops, so your agent does not repeat the same fix without you. The App shows what still fails and notifies you.

![When verification keeps failing: after two failed judge runs the task stops, and you choose to continue, pivot, abandon or accept it as is](pathname:///img/diagrams/stopped-light.svg)
![When verification keeps failing: after two failed judge runs the task stops, and you choose to continue, pivot, abandon or accept it as is](pathname:///img/diagrams/stopped-dark.svg)

Your agent explains what it tried and why the approach seems stuck. You choose:

| Choice | Meaning |
| --- | --- |
| Continue | Keep the approach and try again; the count starts over |
| Pivot | Agree on a different approach and review the changed Plan |
| Abandon | Stop the task and keep its documents |
| Accept as is | Go to Review without another judge run. The review lists what was left open |

**Accept as is** works in Verify too, before the task stops. Only you can choose it, and your final approval still follows.
