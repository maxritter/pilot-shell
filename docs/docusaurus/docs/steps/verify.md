---
title: Verify
description: Agents that did not write the code check every Done means point, with its scenarios and evidence together and a live status of what runs now.
---

![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts by itself when the last slice is built. Agents that did not write the code check it; you have nothing to do unless it stops for you.

## Proof for each Done means point {#live}

![Verify: the agent's work above proof grouped by Done means point; its named status shows what is being checked](pathname:///img/diagrams/verify-light.svg)
![Verify: the agent's work above proof grouped by Done means point; its named status shows what is being checked](pathname:///img/diagrams/verify-dark.svg)

Each **Done means** point shows its checks and evidence together, filling in as they run. Open a point to read its scenarios and proof. Project checks and the agents' reviews stay available too:

- **Polish:** removes near-copies and dead code, adds missing tests.
- **Security review,** when the change touches sign-in, secrets or outside input.
- **Your project's checks:** tests, types, lint and build.
- **Every point of Done means,** every scenario of the Plan, and the whole diff.

Each result keeps its proof: the output, a screenshot or a file. The page is `04-verify.md`: each **Done means** point with its proof, then what agents checked. The named agent status in the top bar says which check runs now; **Agent status** opens the details. With nothing waiting for you, the page shows the agent's work. A stopped check that needs a decision appears in **Your turn**.

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
