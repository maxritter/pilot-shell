---
title: Code health
description: Let your agent spot complex functions and duplicated code, then review what needs changing.
---

QualityLayer checks edited code locally and gives your agent feedback on complexity and structure. Ask “Using QL, review code health in this project” for a closer look, including duplication.

![Edited code is checked locally. Your agent reads each finding, fixes a problem or records why the code should stay. Tests verify the change.](pathname:///img/diagrams/code-health-light.svg)
![Edited code is checked locally. Your agent reads each finding, fixes a problem or records why the code should stay. Tests verify the change.](pathname:///img/diagrams/code-health-dark.svg)

## What happens as you work

1. **You or your agent edits code.** At the end of the agent's turn, a local structure check looks at those files.
2. **Your agent gets the findings.** It reads the source and explains the consequence before changing anything.
3. **It fixes or reviews each finding.** A useful fix is checked with the affected tests. An intentional pattern keeps its review reason.

Checks do not start another agent turn. Findings reach it when the conversation next continues.

## What a finding means

| Finding | What your agent looks for |
| --- | --- |
| Complex function | Branches or responsibilities that make a change difficult to understand |
| Duplicated code | Copies that could drift apart; broader duplication checks run when you ask |
| Previously seen | A finding the tool already reported; it still needs review |
| Acknowledged | A finding retained with a specific reason; the code has not been repaired |

A changed function, analyzer configuration or duplication counterpart can require a new review. A higher metric can too.

## Ask for a broader check

Try “Check this project's duplication” or “Review the complexity of the files we changed.” Your agent can also run your project's enabled linters.

Code health is advisory. Your tests, security checks and release requirements still apply. A failed, skipped or unavailable check gives no passing evidence.

[Commands and setup troubleshooting](commands.md#code-health) · [Supported agents](../agents/native.md)
