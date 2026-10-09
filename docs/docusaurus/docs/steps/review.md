---
title: Review
description: Settle what agents could not settle for you, look at the result, approve, and the pull request opens.
---

![The seven steps, with Review highlighted](pathname:///img/diagrams/track-review-light.svg)
![The seven steps, with Review highlighted](pathname:///img/diagrams/track-review-dark.svg)

The final approval is always yours. Review shows the whole change, from why it was made to how it was checked, with the proof for each **Done means** point. **Your turn** holds the questions the checks could not settle and the final approval.

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

Under the approval card, the page reads **The change, top to bottom**, in one fixed order:

1. **Why:** the one sentence your agent wrote for the change, and what a reviewer must know.
2. **What you asked for:** each **Done means** point with its result, the slice that built it and the scenario that proved it. A point only you can confirm says so.
3. **Built, slice by slice:** the slices of the Outline. Open one for its tasks, what was decided while building it and its files, each with its diff inline. You can comment on any line.
4. **Deliberately not changed:** what the Plan left out, and files another session committed on the branch.
5. **How it was checked:** the checks that ran, the steps to try it yourself and what could not be checked.
6. **Ship:** the branch, the pull request's target and the security findings.

QualityLayer draws this from the task's records, so your agent writes nothing extra for it. The live status at the top shows what the agent is working on; when nothing waits for you, the agent's turn takes the card's place.

Review is `07-review.md`. Its first sections become the pull request's description: **Why the change**, **What a reviewer must know**, **What changed**, the three sections QualityLayer writes from the records (**Built, slice by slice**, **What was asked for, and how each point was proved** and **Deliberately not changed**), **How it was verified**, **Try it yourself** and any security findings. After them come what was decided while building and what you settled. The **More in this document** strip lists the sections the page does not draw, and the description as GitHub receives it opens from **Files › Records**.

## Approve {#approve}

![One answer asks for a change, so the main button reads Send 1 change; the Comments tab of the right sidebar lists your comments, answered threads and your team’s](pathname:///img/diagrams/comments-light.svg)
![One answer asks for a change, so the main button reads Send 1 change; the Comments tab of the right sidebar lists your comments, answered threads and your team’s](pathname:///img/diagrams/comments-dark.svg)

The last question is "Approve the change?". **Approve and open a pull request** pushes the branch and opens it with a description in the same order as the page: why the change exists, what was asked for and how each point was proved, the slices with a link from every file to its own diff in the pull request, what was left alone and how it was checked. **Approve only** leaves pushing to you. When an answer asks for a change, the button reads **Send 1 change** instead. QualityLayer never pushes, opens a pull request or merges without your yes.

A task that started on your repository's main branch has no branch to open a pull request from. **Approve and open a pull request** then says so and gives the commands; see [where the build lands](implement.md#where-it-lands).

With a team, teammates comment in their own App; see [Change reviews](../team/changes.md).

## Shipped {#shipped}

![Shipped: the task keeps its documents, what you decided and what it cost; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-light.svg)
![Shipped: the task keeps its documents, what you decided and what it cost; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-dark.svg)

The task keeps its documents and what it cost, in `docs/plans/` in your repository. Merging and deploying stay with your own process.

### The pull request stays on the page {#pull-request}

The task is not finished while its pull request is open. After the approval, the Review page shows a card for the pull request: its checks with their names and results, who was asked to review and what they said. The walkthrough stays beneath it, folded, as you approved it. QualityLayer reads the pull request with `gh` about once a minute while the App is open, so `gh` has to be installed for this; without it the card says the pull request is not followed here, and the task closes at the approval.

When someone leaves a thread, asks for changes or a check fails, the task comes back under **Needs attention** on Home, in the sidebar and in the bell, with a line such as "Pull request · 2 threads, 1 check failing". The page then shows a **Your turn** card with the threads, the failing check and the command to copy:

```sh
/ql review <task>
```

Your agent goes through each thread with you, as it does for [your team's threads](../team/changes.md), reads the log of a failing check, fixes what needs fixing and checks again what the fix touched. The fix stays on your computer until you press **Push the fix**. QualityLayer never pushes on its own.

When the pull request is merged, the task closes and Shipped says so, with what the task cost. A pull request closed without a merge shows as closed.

## Stop, archive or delete a task {#stop-archive-or-delete-a-task}

- **Stop:** tell your agent at any step. The documents stay.
- **Archive:** in the task's **…** menu, takes it off the sidebar; **Restore** brings it back.
- **Delete:** in the same menu, moves the plan folder to the Trash after asking.
