---
title: Verify
description: A fresh agent that did not write the code adds missing tests and checks every Done means point on the running program, with evidence.
---

![The eight steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The eight steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts when the build is committed. The checks below run in order and continue available work until Review, without workflow questions. Nothing is marked passed without evidence.

![Verify in the App: the checks and their results](pathname:///img/app/verify-light.webp)
![Verify in the App: the checks and their results](pathname:///img/app/verify-dark.webp)

*Example task in a fictional project.*

## The checks {#lanes}

| Check | What it does |
| --- | --- |
| **Security review** | Only when the Plan names a trust boundary, such as sign-in, secrets or outside input. It reads and changes nothing. Critical and high findings become gaps to fix; medium and low findings go into the pull request |
| **Project checks** | Your tests, types, lint and build, run once on the committed build and recorded. A red check does not stop the review. A failure this task caused becomes a gap; one that was already there is disclosed in Review with its evidence |
| **Independent review** | One fresh agent that did not write the code. It adds the tests the build missed (tests and docs only) and compares changed screens with their artifacts. It runs the scenarios on the running program, rules on every **Done means** point and reads the whole diff |
| **Second opinion** | Beside the independent review on a risky change, or always when [Settings](../reference/settings.md#second-opinion) say so: a separate reviewer checks for breakage using the installed agent selected there. Each finding is answered in Review |
| **Fix rounds** | The build session fixes the gaps itself, or hands a large batch to one helper, and commits. The next round re-checks the failed points and what the fix touched |

If you turn **Independent review** off in [Settings](../reference/settings.md#independent-review), no fresh agent checks the change; Verify records **Checked without an independent judge**.

## Rounds {#rounds}

Verify has two rounds. The first is a full independent review. If it finds gaps, your agent fixes them, and a second fresh agent rechecks what failed and what the fix touched; everything that passed before keeps its evidence. A meter above the checks shows how many rounds are used.

If something is still open after the recheck, the task goes to Review with the open items first. **Fix open items** there runs one more round on just those items.

## Proof for each point {#live}

Each **Done means** point shows its evidence as it comes in: output, a screenshot or a file. Failures are fixed test first, without asking you.

**Done means, checked** shows each result with its evidence. Failed and blocked points come first; open a check for its commands and output. Full review records stay below.

## What reaches Review {#when-it-stops}

Failed checks keep their results and evidence. Human-only prerequisites, unavailable environments and points still open after the last round reach Review as unresolved work. They never count as passed, and they ask you to approve no further build step.

In Review, you can run one more round on the open items or decide what to do with them. Your agent's native permissions and your explicit stop or pause still apply.

Next: [Review](review.md).
