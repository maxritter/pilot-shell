---
title: Verify
description: Agents that did not write the code check every point of your request while you watch a live checklist. Only you can confirm what no agent may do.
---

![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-light.svg)
![The five steps, with Verify highlighted](pathname:///img/diagrams/track-verify-dark.svg)

Verify starts by itself when the last slice is built. Checking is agent work: the checks, the scenarios and every point of Done means are things an agent that did not write the code can decide. You have nothing to do here unless it stops for you.

## A live checklist {#live}

![The Verify step while agents check: every check listed from the start, how many have passed, where the minutes went, and what each checking agent does now](pathname:///img/diagrams/verify-light.svg)
![The Verify step while agents check: every check listed from the start, how many have passed, where the minutes went, and what each checking agent does now](pathname:///img/diagrams/verify-dark.svg)

The step line reads "Agents are checking". Every check is listed from the start and fills in as it runs.

| Part | What it shows |
| --- | --- |
| Header | "14 of 29 checks passed", a bar, and where the minutes went: polish, project checks, checking |
| **Before checking** | Polish, the security review when the change crosses a trust boundary, and the project checks (tests, types, lint, build) recorded at one commit |
| **Scenarios** | Every scenario of the Plan, run end to end |
| **Done means** | Each point, checked against the diff and the running program |
| **Code review** | Every changed file against its task |
| **Now** | What each checking agent does at this moment |

A check is waiting, running, passed or failed. Checking is split into parts that run side by side, so you can see which part runs which check.

**Stop checking and review** takes the build as it is and goes to Review, with what was left open listed.

### Polish and the security review {#polish}

| Step | What it does |
| --- | --- |
| **Polish** | Removes near-copies and code nothing uses, adds missing edge-case and error-path tests, and fixes docs the change made wrong. For a change people see, it compares the running screens with the mockup. One commit per change |
| **Security review** | Runs only when the change crosses a trust boundary: outside input, sign-in, secrets, files from users or other processes. It runs first and shows what it fixed. It reads only and changes nothing else |

Polish runs targeted tests after each change and the full suite once at the end. It also fixes the expectations of tests its own change broke. A critical or high security finding goes to an agent to fix, test first, and is checked again before checking starts. Medium and low findings are listed in the *Security* section of the pull request description and block nothing.

## Who checks

QualityLayer runs the project's tests, lint, type check and build once and records the result. Then agents that did not write the code, on Opus 5.5 by default, check the change. They check every point of your Done means against the running program, every scenario and every task's definition of done. They also read the whole diff for bugs and for code outside what the Plan named.

They cite the checks QualityLayer recorded and run again only what they doubt. Each one records its result as it goes, so the list fills in live. Every result keeps its evidence: the output, a screenshot or a file. They skip files Git ignores and files that are generated.

## Only you can confirm {#only-you}

Some points no agent may settle, such as one live call to a service. Discuss marks those points when it writes Done means. During Verify they never fail a check and never start a fix. They go to Review as an **Only you can confirm** item, where you answer **I confirm** or **Ask the agent to record it**.

## When all checks pass

The step line reads "Checked", for example "All 29 checks passed. 4 items wait for you in Review." One violet line holds the proof: how many checks passed, how many tests, the scenarios, the agents and the time. A **Waiting for you in Review** list names what moved on, and folds hold the scenarios, Done means, project checks and polish. **Open Review** takes you there.

## When a check fails {#fixes}

The step line reads "Fixing 1 failed check", and the failing point is named in red. It is the only red on the page.

- An agent writes a failing test and fixes the code. You are not asked.
- Then that check and what the fix touched are checked again.

When a second fix fails too, the task stops and asks you.

## When it stops {#when-it-stops}

After two tries at checking, the task stops, so your agent does not repeat the same fix without you. The step line reads "Stopped after checking twice". The App names the one failure that still stands, what each fix tried, and what checking again costs, for example about $7 and 9 minutes.

![When checking keeps failing: after two tries at checking the task stops with the one failure that remains, and you choose to check once more, take it as it is, or stop the task](pathname:///img/diagrams/stopped-light.svg)
![When checking keeps failing: after two tries at checking the task stops with the one failure that remains, and you choose to check once more, take it as it is, or stop the task](pathname:///img/diagrams/stopped-dark.svg)

| Choice | Meaning |
| --- | --- |
| Check once more | Check again; the count starts over |
| Take it as it is | Go to Review without checking again. The review lists what was left open |
| Stop the task | End the task and keep its documents and evidence |

**Take it as it is** works in Verify before the task stops too, as **Stop checking and review**. Only you can choose it, and your final approval still follows.

When the Plan crossed a trust boundary or marked a slice risky, a [second opinion](../reference/settings.md#second-opinion) from the other vendor's AI also reviews the built change.

## What is kept

The records are kept in `04-verify.md`, with the evidence under `evidence/`. An older task keeps them in `03-build.md`. Next: [Review](review.md).
