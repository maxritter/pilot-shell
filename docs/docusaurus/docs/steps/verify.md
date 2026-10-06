---
title: Verify
description: Agents that did not write the code check every point you agreed on, on a live checklist. Nothing waits for you unless a fix keeps failing.
---

![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts by itself when the last slice is built. Agents that did not write the code check it; you have nothing to do unless it stops for you.

## A live checklist {#live}

![The Verify step while agents check: the status pill, every check listed from the start, how many have passed, where the minutes went, and what each checking agent does now](pathname:///img/diagrams/verify-light.svg)
![The Verify step while agents check: the status pill, every check listed from the start, how many have passed, where the minutes went, and what each checking agent does now](pathname:///img/diagrams/verify-dark.svg)

Every check is listed from the start and fills in as it runs:

- **Polish:** removes near-copies and dead code, adds missing tests.
- **Security review,** when the change touches sign-in, secrets or outside input.
- **Your project's checks:** tests, types, lint and build.
- **Every point of Done means,** every scenario of the Plan, and the whole diff.

Each result keeps its proof: the output, a screenshot or a file. The page is `04-verify.md`: the open items first, then each point of Done means with its proof, then what agents checked. The status pill in the header says which check runs now.

## When a check fails {#fixes}

An agent writes a failing test, fixes the code, and the check runs again. You are not asked.

## When it stops {#when-it-stops}

If checking fails twice, the task stops and names the one failure that remains. You choose: **Check once more**, **Take it as it is**, or **Stop the task**.

![When checking keeps failing: after two tries at checking the task stops with the one failure that remains, and you choose to check once more, take it as it is, or stop the task](pathname:///img/diagrams/stopped-light.svg)
![When checking keeps failing: after two tries at checking the task stops with the one failure that remains, and you choose to check once more, take it as it is, or stop the task](pathname:///img/diagrams/stopped-dark.svg)

## Only you can confirm {#only-you}

Some points no agent may settle, such as one live call to a paid service. They wait for you in Review.

Next: [Review](review.md).
