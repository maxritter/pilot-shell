---
title: Verify
description: Agents that did not write the code check every Done means point, with its scenarios and evidence together and a live status of what runs now.
---

![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts by itself when the last slice is built. Agents that did not write the code check it; you have nothing to do unless it stops for you.

## Proof for each Done means point {#live}

![Verify: the agent's turn beside proof grouped by Done means point; the live status says which point is being checked](pathname:///img/diagrams/verify-light.svg)
![Verify: the agent's turn beside proof grouped by Done means point; the live status says which point is being checked](pathname:///img/diagrams/verify-dark.svg)

Each **Done means** point shows its checks and evidence together, filling in as they run. Open a point to read its scenarios and proof. Project checks and the agents' reviews stay available too:

- **Polish:** removes near-copies and dead code, adds missing tests.
- **Security review,** when the change touches sign-in, secrets or outside input.
- **Your project's checks:** tests, types, lint and build.
- **Every point of Done means,** every scenario of the Plan, and the whole diff.

Each result keeps its proof: the output, a screenshot or a file. The page is `04-verify.md`: each **Done means** point with its proof, then what agents checked. The live status in the top bar says which check runs now. With nothing waiting for you, the agent's turn shows beside the work; a stopped check that needs a decision appears in **Your turn**.

## When a check fails {#fixes}

An agent writes a failing test, fixes the code, and the check runs again. You are not asked.

## When it stops {#when-it-stops}

If checking fails twice, the task stops and names the one failure that remains. You choose: **Check once more**, **Take it as it is**, or **Stop the task**.

![When checking keeps failing: after two tries at checking the task stops with the one failure that remains, and you choose to check once more, take it as it is, or stop the task](pathname:///img/diagrams/stopped-light.svg)
![When checking keeps failing: after two tries at checking the task stops with the one failure that remains, and you choose to check once more, take it as it is, or stop the task](pathname:///img/diagrams/stopped-dark.svg)

## Only you can confirm {#only-you}

Some points no agent may settle, such as one live call to a paid service. They wait for you in Review.

Next: [Review](review.md).
