---
title: Review
description: Settle what agents could not settle for you, look at the result, approve, and the pull request opens.
---

![The five steps, with Review highlighted](pathname:///img/diagrams/track-review-light.svg)
![The five steps, with Review highlighted](pathname:///img/diagrams/track-review-dark.svg)

The final approval is always yours. Review shows only what the checks could not settle; the proof that every point holds is one line above the diff.

![Review: the items that need you, your agent asking "Approve the change?" in the terminal, the line of what agents proved, and the changes by task](pathname:///img/diagrams/review-light.svg)
![Review: the items that need you, your agent asking "Approve the change?" in the terminal, the line of what agents proved, and the changes by task](pathname:///img/diagrams/review-dark.svg)

## What needs you {#items}

Your agent asks each item in the terminal, and the App shows it:

| Item | Your answers |
| --- | --- |
| **Only you can confirm** | **I confirm**, or ask the agent to record it |
| **Look at the result** | **Looks right**, or pin a change on the screenshot |
| **Found while checking** | **Accept**, or **Fix it** |
| **Changed while building** | **Fine**, or **Ask why** |

Fixes go back to the agent, which makes them, checks what they touched, and asks again.

## Approve {#approve}

![One answer asks for a change, so the main button reads Send 1 change; the Comments panel lists your drafts, answered threads and your team's comments](pathname:///img/diagrams/comments-light.svg)
![One answer asks for a change, so the main button reads Send 1 change; the Comments panel lists your drafts, answered threads and your team's comments](pathname:///img/diagrams/comments-dark.svg)

The last question is "Approve the change?". After you approve, your agent offers to open the pull request, with a description that says why the change exists, what changed and how each point was checked. QualityLayer never pushes, opens a pull request or merges without your yes.

With a team, teammates comment in their own App; see [Change reviews](../team/changes.md).

## Shipped {#shipped}

![Shipped: the task keeps its documents, what you decided and what it cost; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-light.svg)
![Shipped: the task keeps its documents, what you decided and what it cost; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-dark.svg)

The task keeps its documents and what it cost, in `docs/plans/` in your repository. Merging and deploying stay with your own process.

## Stop, archive or delete a task {#stop-archive-or-delete-a-task}

- **Stop:** tell your agent at any step. The documents stay.
- **Archive:** takes a task off the sidebar; **Restore** brings it back.
- **Delete:** in **More**; it moves the plan folder to the Trash after asking.
