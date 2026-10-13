---
title: Review
description: Settle what agents could not settle for you, look at the result, and approve. Then the pull request opens.
---

![The eight steps, with Review highlighted](pathname:///img/diagrams/track-review-light.svg)
![The eight steps, with Review highlighted](pathname:///img/diagrams/track-review-dark.svg)

The final approval is always yours. Review shows the whole change, from why it was made to how it was checked, with the proof for each **Done means** point.

![Review in the App: the Approve the change banner, and the change from top to bottom with each Done means point and its result](pathname:///img/app/review-light.webp)
![Review in the App: the Approve the change banner, and the change from top to bottom with each Done means point and its result](pathname:///img/app/review-dark.webp)

*Example task in a fictional project.*

## Your turn {#items}

**Your turn** holds what the checks could not settle, one at a time:

| Item | Your answers |
| --- | --- |
| **Only you can confirm** | **I confirm**, or ask the agent to record it |
| **Look at the result** | **Looks right**, or pin a change on the screenshot |
| **Found while checking** | **Accept**, or **Fix it** |
| **Decided while building** | **Fine**, or **Ask why** |

Each answer reaches your agent immediately and stays recorded beside its point. A fix goes back to the agent, which makes it, checks what it touched and asks again.

## The page {#the-page}

Under the approval card, **The change, top to bottom** always reads in this order:

| Section | What it shows |
| --- | --- |
| **Why** | One sentence on why the change exists, and what a reviewer must know |
| **What you asked for** | Each **Done means** point with its result, the slice that built it and the scenario that proved it |
| **Built, slice by slice** | Each slice with its decisions and files, every file with its diff inline; comment on any line |
| **Deliberately not changed** | What the Plan left out |
| **How it was checked** | The checks that ran, how to try it yourself, and what could not be checked |
| **Ship** | The branch, the pull request's target and any security findings |

At the **Product** level the page reads as a release note, and **Built, slice by slice** folds to its headline ([two levels](../intro.md#two-levels)). The page is `07-review.md`. Its first sections are the pull request's description, word for word.

When the task drew on a [lasting design](../designs.md#lasting), a card above the page, **This task changes App Model**, shows each page it changed, before and after. You pick the pages to **Fold … in** to the lasting design; they go into the task's commits and its pull request ([Fold in at Review](../designs.md#fold-in)).

## Approve {#approve}

The last question is "Approve the change?". Choose how it ships:

| Choice | What happens |
| --- | --- |
| **Approve and open a pull request** | Pushes the branch and opens the pull request with this page as its description. Needs `gh` and a branch of the task's own |
| **Approve only** | You push and open it yourself |
| **Copy the git commands** | Commit, push and open it from your terminal |

Once the pull request is open, your agent stays with it: it watches the checks, and fixes a failing check or a conflict itself, at most three times ([Pull request](pull-request.md#watch)).

When an answer asks for a change, the button reads **Send 1 change** instead. QualityLayer never pushes, opens a pull request or merges without your yes. A task built on your main branch has no branch to open a pull request from; see [where the build lands](implement.md#where-it-lands).

![One answer asks for a change, so the main button reads Send 1 change; the Comments tab of the right sidebar lists your comments, answered threads and your team’s](pathname:///img/diagrams/comments-light.svg)
![One answer asks for a change, so the main button reads Send 1 change; the Comments tab of the right sidebar lists your comments, answered threads and your team’s](pathname:///img/diagrams/comments-dark.svg)

With a team, teammates comment in their own App ([Change reviews](../team/changes.md)). After the approval the task stays open until its pull request is merged ([Pull request](pull-request.md)).

## Stop, archive or delete a task {#stop-archive-or-delete-a-task}

| | How | What stays |
| --- | --- | --- |
| **Stop** | Tell your agent, at any step | The documents |
| **Archive** | The task's **…** menu; **Restore** brings it back | Everything, off the sidebar |
| **Delete** | The same menu, after a confirmation | Nothing: the plan folder goes to the Trash |
