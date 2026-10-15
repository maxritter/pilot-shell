---
title: Verify
description: Agents that did not write the code check every Done means point, with its scenarios and evidence together.
---

![The eight steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The eight steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts when the last slice is built. Agents that did not write the code check it. You do nothing unless it stops for you.

![Verify in the App: the six checks and their results](pathname:///img/app/verify-light.webp)
![Verify in the App: the six checks and their results](pathname:///img/app/verify-dark.webp)

*Example task in a fictional project.*

## Six checks {#lanes}

Polish, Security review and Second opinion start side by side when enabled. Project checks and Independent review follow; Fix rounds handle what remains.

| Check | What it does |
| --- | --- |
| **1. Polish** | Removes dead code, adds missing tests, updates docs |
| **2. Security review** | When the change touches sign-in, secrets or outside input |
| **3. Second opinion** | Risky changes: the other coding agent looks for breakage; its findings are addressed before Independent review |
| **4. Project checks** | Your tests, types, lint and build |
| **5. Independent review** | Proves every **Done means** point on the running program |
| **6. Fix rounds** | Fixes everything found, then reruns what it touched |

On a change that is not risky, the build session runs the review itself and marks it **not independent**. [Settings](../reference/settings.md#independent-review) can change that, and the [second opinion](../reference/settings.md#second-opinion) too.

## Proof for each point {#live}

Each **Done means** point shows its evidence as it comes in: output, a screenshot or a file. Failures are fixed test first, without asking you.

## When it stops {#when-it-stops}

After two failed fix rounds, **Your turn** shows what still fails and the cost so far:

| Choice | What happens |
| --- | --- |
| **One more round** | One more review run |
| **Review it as it is** | Goes to Review with the open items listed |
| **Stop here** | The work and its evidence stay |

![The fixing hold with its three choices](pathname:///img/diagrams/stopped-light.svg)
![The fixing hold with its three choices](pathname:///img/diagrams/stopped-dark.svg)

Next: [Review](review.md).
