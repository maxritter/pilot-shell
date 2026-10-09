---
title: Verify
description: Agents that did not write the code check every Done means point, with its scenarios and evidence together and a live status of what runs now.
---

![The seven steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The seven steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts by itself when the last slice is built. Agents that did not write the code check it; you have nothing to do unless it stops for you.

## Six checks, in this order {#lanes}

Verify runs six named checks. The first two run side by side, and so do the fourth and fifth:

1. **Polish:** removes near-copies and dead code, adds missing tests, updates the docs and, for a screen, compares it with its design. It never hunts for bugs.
2. **Security review,** when the change crosses a trust boundary: sign-in, secrets or outside input. It only reads.
3. **Project checks:** your tests, types, lint and build, run once and recorded by QualityLayer. A result is reused when the code and the environment have not changed.
4. **Independent review:** agents that did not write the code prove every **Done means** point on the running program.
5. **Second opinion,** when the change is risky: the other coding agent reads what was built, hunting for what would break. By default it runs only on risky changes; [Settings](../reference/settings.md#second-opinion) can make it always.
6. **Fix rounds:** one agent per round fixes everything found at once, and only what failed or was touched is checked again.

The page shows these lanes in the order they run, each with who does it, a short line and its result; open one for its full text.

## Proof for each Done means point {#live}

![Verify: the agent's work above proof grouped by Done means point; its named status shows what is being checked](pathname:///img/diagrams/verify-light.svg)
![Verify: the agent's work above proof grouped by Done means point; its named status shows what is being checked](pathname:///img/diagrams/verify-dark.svg)

Each **Done means** point shows its checks and evidence together, filling in as they run. Open a point to read its scenarios and proof. The checks above and the agents' reviews stay available too. The independent review covers every point of **Done means**, every scenario of the Outline and the whole diff.

Each result keeps its proof: the output, a screenshot or a file. The page is `06-verify.md`: the lanes, each **Done means** point with its proof, then what was found while checking. The named agent status in the top bar says which check runs now; **Agent status** opens the details. With nothing waiting for you, the page shows the agent's work. A stopped check that needs a decision appears in **Your turn**.

## When a check fails {#fixes}

An agent writes a failing test, fixes the code, and the check runs again. You are not asked.

## When it stops {#when-it-stops}

After the initial review and two failed fixing rounds, **Your turn** shows what the recorded rounds fixed, their time and estimated cost, and what still fails. You choose **One more round**, **Review it as it is**, or **Stop here**. One more round allows exactly one additional review run; if it fails, the choice returns. Earlier records keep their actual history.

![The fixing hold lists recorded rounds and open failures, with One more round, Review it as it is and Stop here](pathname:///img/diagrams/stopped-light.svg)
![The fixing hold lists recorded rounds and open failures, with One more round, Review it as it is and Stop here](pathname:///img/diagrams/stopped-dark.svg)

During Verify, the **Task menu** also offers **Stop checking and review**. Its confirmation explains that open items will remain in Review.

## Only you can confirm {#only-you}

Some points no agent may settle, such as one live call to a paid service. They wait for you in Review.

Next: [Review](review.md).
