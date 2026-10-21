---
title: Verify
description: Agents that did not write the code check every Done means point, with its scenarios and evidence together.
---

![The eight steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The eight steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts when the last slice is built. Agents that did not write the code check it and continue available work until Review, without workflow questions.

![Verify in the App: the six checks and their results](pathname:///img/app/verify-light.webp)
![Verify in the App: the six checks and their results](pathname:///img/app/verify-dark.webp)

*Example task in a fictional project.*

## Six checks {#lanes}

Polish, Security review and Second opinion start side by side when enabled. Project checks and Independent review follow; Fix rounds handle what remains.

| Check | What it does |
| --- | --- |
| **1. Polish** | Removes dead code, adds missing tests, updates docs |
| **2. Security review** | When the change touches sign-in, secrets or outside input |
| **3. Second opinion** | Risky changes: a separate reviewer checks for breakage using the installed agent selected in [Settings](../reference/settings.md#second-opinion); its findings are addressed before Independent review |
| **4. Project checks** | Your tests, types, lint and build |
| **5. Independent review** | Proves every **Done means** point on the running program |
| **6. Fix rounds** | Fixes everything found, then reruns what it touched |

On a change that is not risky, the build session runs the review itself and marks it **not independent**. [Settings](../reference/settings.md#independent-review) can change that, and the [second opinion](../reference/settings.md#second-opinion) too.

## Proof for each point {#live}

Each **Done means** point shows its evidence as it comes in: output, a screenshot or a file. Failures are fixed test first, without asking you.

**Done means, checked** shows each result with its evidence. Failed and blocked points come first; open a check for its commands and output. Fix rounds and full review records remain available below.

## What reaches Review {#when-it-stops}

Failed checks keep their results and evidence. Human-only prerequisites, unavailable environments and exhausted fix rounds reach Review as unresolved work. They do not become passed checks or ask you to approve another build step.

In Review, you can request another fix round or decide what to do with the remaining gaps. Your agent's native permissions and your explicit stop or pause still apply.


Next: [Review](review.md).
