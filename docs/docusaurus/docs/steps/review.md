---
title: Review
description: Settle what agents could not settle for you, look at the result, approve, and the pull request opens.
---

![The seven steps, with Review highlighted](pathname:///img/diagrams/track-review-light.svg)
![The seven steps, with Review highlighted](pathname:///img/diagrams/track-review-dark.svg)

The final approval is always yours. Review groups the result and its proof by **Done means** point. **Your turn** holds the questions the checks could not settle and the final approval.

![Review: one Your turn card beside the result and proof for each Done means point, with live status in the top bar](pathname:///img/diagrams/review-light.svg)
![Review: one Your turn card beside the result and proof for each Done means point, with live status in the top bar](pathname:///img/diagrams/review-dark.svg)

## Your turn {#items}

**Your turn** shows one focused decision with the result it concerns. Move between decisions, choose an answer or write your own words and press **Send**. Each answer reaches your agent immediately and leaves the card. The answer stays recorded beside the point it settled; long settled lists fold in the document:

| Item | Your answers |
| --- | --- |
| **Only you can confirm** | **I confirm**, or ask the agent to record it |
| **Look at the result** | **Looks right**, or pin a change on the screenshot |
| **Found while checking** | **Accept**, or **Fix it** |
| **Decided while building** | **Fine**, or **Ask why** |

Fixes go back to the agent, which makes them, checks what they touched, and asks again.

## The page {#the-page}

Review is `07-review.md`: **Why the change**, **What a reviewer must know**, **What changed**, **How it was verified** and **Try it yourself**, then what was decided while building and what you settled. The first sections become the pull request's description exactly as written; each **Done means** point keeps its result and proof beside it. The live status at the top shows what the agent is working on; when nothing waits for you, the agent's turn takes the card's place.

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
- **Archive:** in the task's **…** menu, takes it off the sidebar; **Restore** brings it back.
- **Delete:** in the same menu, moves the plan folder to the Trash after asking.
