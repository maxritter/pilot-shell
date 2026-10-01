---
title: Review
description: Your review of the finished change, alone or with your team, from its proofs, evidence, steps to try it, the diff and the pull request.
---

![The Feature route with Review highlighted](pathname:///img/diagrams/track-approve-light.svg)
![The Feature route with Review highlighted](pathname:///img/diagrams/track-approve-dark.svg)

The final approval is always yours. Review puts everything you need to trust the change in one place, like a pull request that also shows why the change was made and how it was checked.

![The Review stage: what was built and checked, steps to try it, the files changed, and the final decision](pathname:///img/diagrams/approve-light.svg)
![The Review stage: what was built and checked, steps to try it, the files changed, and the final decision](pathname:///img/diagrams/approve-dark.svg)

## In the Cockpit

| Tab | What it shows |
| --- | --- |
| Overview | Each point of your Done means with its proof and pictures, and a Code health line: lines added and removed, each new module with its reason, and what Simplify removed |
| Evidence | The checks, scenarios and Done means the independent check ran, and the second review by an AI from another vendor |
| Try it | Steps to try the whole change yourself, written by the AI that checked it |
| Files changed | The change on your machine as a diff, files with open threads first; comment on any line |
| Conversation | Every thread with its context and state; filter Open, All or Resolved |

**Create pull request** pushes the branch and opens the pull request with the description drafted from the plan. QualityLayer does this only when you click it. Once the pull request exists, Review shows its number, state and checks.

## You decide

**Approve and ship**, or **Request changes** with a remark or line comments. A fix is built test-first and checked again. A comment that changes Done means is recorded as an agreed change to the plan, in your words.

With a Team plan, teammates review the same change in their own Cockpit and the code in the pull request. See [Review changes as a team](../../team/changes.md).
