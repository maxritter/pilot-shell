---
title: Verify
description: Agents that did not write the code check every Done means point, with its scenarios and evidence together.
---

![The eight steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The eight steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts by itself when the last slice is built. Agents that did not write the code check it. You have nothing to do unless it stops for you.

![Verify in the App: the six checks with who runs each and its result](pathname:///img/app/verify-light.webp)
![Verify in the App: the six checks with who runs each and its result](pathname:///img/app/verify-dark.webp)

*Example task in a fictional project.*

## Six checks, in this order {#lanes}

| Check | What it does |
| --- | --- |
| **1. Polish** | Removes near-copies and dead code, adds missing tests, updates the docs, and compares a screen with its design. It does not hunt for bugs |
| **2. Security review** | Reads the change when it touches sign-in, secrets or outside input |
| **3. Project checks** | Your tests, types, lint and build, run and recorded by QualityLayer |
| **4. Independent review** | Agents that did not write the code prove every **Done means** point on the running program |
| **5. Second opinion** | On a risky change, the other coding agent looks for what would break ([Settings](../reference/settings.md#second-opinion) can make it always run) |
| **6. Fix rounds** | One agent fixes everything found at once; only what failed or what a fix touched runs again |

Checks 1 and 2 run side by side, and the Second opinion starts with them. Its findings are fixed before the Independent review starts, so that review runs once, on the final code. Every change gets Polish, a small one too: skipping it on small changes let their tests catch fewer planted faults. A risky change (the Plan's **Risky** line, a trust boundary, a risky slice) gets the Independent review from a fresh agent; on any other change the build session runs the same review itself, and the page marks it **not independent** ([Settings](../reference/settings.md#independent-review) can make the fresh agent review every change).

With **No subagents** in [Settings](../reference/settings.md#defaults), the build session runs every check itself, Polish included, and the page says so. A second opinion that does not run says why: the change is not risky, Settings switched it off, or you asked for none.

## Proof for each point {#live}

Each **Done means** point shows its checks and evidence as they come in. Open one for its scenarios and proof: the output, a screenshot or a file. The record is `06-verify.md`.

When a check fails, an agent writes a failing test, fixes the code and runs the check again. You are not asked.

## When it stops {#when-it-stops}

After the first review and two failed fix rounds, **Your turn** shows what was fixed, the time and estimated cost so far, and what still fails:

| Choice | What happens |
| --- | --- |
| **One more round** | One more review run; if it fails, the choice comes back |
| **Review it as it is** | Goes on to Review with the open items listed |
| **Stop here** | The work and its evidence stay |

![The fixing hold lists recorded rounds and open failures, with One more round, Review it as it is and Stop here](pathname:///img/diagrams/stopped-light.svg)
![The fixing hold lists recorded rounds and open failures, with One more round, Review it as it is and Stop here](pathname:///img/diagrams/stopped-dark.svg)

To end checking early, use **Stop checking and review** in the task menu. Some points no agent may settle, such as a live call to a paid service; they wait for you in Review.

Next: [Review](review.md).
