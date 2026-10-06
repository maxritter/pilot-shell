---
title: Review
description: Settle what agents could not settle for you, look at the result, approve, and the pull request opens.
---

![The five steps, with Review highlighted](pathname:///img/diagrams/track-review-light.svg)
![The five steps, with Review highlighted](pathname:///img/diagrams/track-review-dark.svg)

The final approval is always yours. Review asks only what the checks could not settle; the proof that every point holds is one line above the approval.

![The Review step: one line names what needs you, what changed, what was settled with you, the line of what agents proved, and the card “Approve the change?” with Approve and open a pull request](pathname:///img/diagrams/review-light.svg)
![The Review step: one line names what needs you, what changed, what was settled with you, the line of what agents proved, and the card “Approve the change?” with Approve and open a pull request](pathname:///img/diagrams/review-dark.svg)

## What needs you {#items}

The App asks each item in the same card as every other question, and each answer lands under **Settled with you**:

| Item | Your answers |
| --- | --- |
| **Only you can confirm** | **I confirm**, or ask the agent to record it |
| **Look at the result** | **Looks right**, or pin a change on the screenshot |
| **Found while checking** | **Accept**, or **Fix it** |
| **Decided while building** | **Fine**, or **Ask why** |

Fixes go back to the agent, which makes them, checks what they touched, and asks again.

## The page {#the-page}

Review is `05-review.md`: **What changed** and **How to try it**, written by the agent, then the decisions made for you, what you settled, and the proof. The same file becomes the pull request's description.

## Approve {#approve}

![One answer asks for a change, so the main button reads Send 1 change; the Comments tab of the right sidebar lists your comments, answered threads and your team’s](pathname:///img/diagrams/comments-light.svg)
![One answer asks for a change, so the main button reads Send 1 change; the Comments tab of the right sidebar lists your comments, answered threads and your team’s](pathname:///img/diagrams/comments-dark.svg)

The last question is "Approve the change?". **Approve and open a pull request** pushes the branch and opens it with a description that says why the change exists, what changed and how each point was checked; **Approve only** leaves pushing to you. When an answer asks for a change, the button reads **Send 1 change** instead. QualityLayer never pushes, opens a pull request or merges without your yes.

With a team, teammates comment in their own App; see [Change reviews](../team/changes.md).

## Shipped {#shipped}

![Shipped: the task keeps its documents, what you decided and what it cost; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-light.svg)
![Shipped: the task keeps its documents, what you decided and what it cost; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-dark.svg)

The task keeps its documents and what it cost, in `docs/plans/` in your repository. Merging and deploying stay with your own process.

## Stop, archive or delete a task {#stop-archive-or-delete-a-task}

- **Stop:** tell your agent at any step. The documents stay.
- **Archive:** the small button in the task's header takes it off the sidebar; **Restore** brings it back.
- **Delete:** the button beside it moves the plan folder to the Trash after asking.
