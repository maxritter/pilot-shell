---
title: Review
description: Settle what agents could not settle for you, look at the result, and approve. Then the pull request opens.
---

![The eight steps, with Review highlighted](pathname:///img/diagrams/track-review-light.svg)
![The eight steps, with Review highlighted](pathname:///img/diagrams/track-review-dark.svg)

The final approval is always yours. After Outline, Implement and Verify, Review brings back the decisions and unverified checks that need you. It shows the whole change with proof for each **Done means** point.

![Review in the App: the change walkthrough, requested outcomes and approval prompt](pathname:///img/app/review-light.webp)
![Review in the App: the change walkthrough, requested outcomes and approval prompt](pathname:///img/app/review-dark.webp)

*Example task in a fictional project.*

## Your turn {#items}

| Item | Your answers |
| --- | --- |
| **Only you can confirm** | **I confirm**, or ask the agent to record it |
| **Look at the result** | **Looks right**, or pin a change on the screenshot |
| **Found while checking** | **Accept**, or **Fix it** |

Routine build decisions stay under **Decided while building**. Open the record to read them or **Ask why**; they do not each require a confirmation.

## The page {#the-page}

The App puts what needs you first: the approval, each point only you can confirm, and anything the checks left open. **Look here** then lists an unverified point, an item you accepted as open and any commit by another session that the push includes. Below the summary, one walkthrough runs top to bottom: what you asked for, with what needs attention first; the built slices, collapsed; the screens that changed, one picture for each; what was deliberately not changed; how it was checked, collapsed; and the way to ship it. The decisions made while building, grouped by where they were made, and what you settled sit in collapsed sections. Full paths, commit IDs and evidence remain accessible, including other sessions' changes carried by the branch.

`07-review.md` keeps the complete record in the order the pull request description needs, which is why this page draws the walkthrough instead of following the file. Its top becomes the pull request's description. If the task changed a [lasting design](../designs.md#lasting), you pick which pages to [fold in](../designs.md#fold-in).

## Approve {#approve}

| Choice | What happens |
| --- | --- |
| **Approve and open a pull request** | Pushes the task's branch and opens the pull request. Needs `gh` |
| **Approve only** | You push and open it yourself |
| **Copy the git commands** | Run them in your terminal |

![When an answer asks for a change, the button reads Send 1 change](pathname:///img/diagrams/comments-light.svg)
![When an answer asks for a change, the button reads Send 1 change](pathname:///img/diagrams/comments-dark.svg)

Nothing is pushed or merged without your yes. A task built on your main branch has no branch to open a pull request from ([where the build lands](implement.md#where-it-lands)). After approval, your agent [watches the checks](pull-request.md#watch). Teammates comment in their own App ([Change reviews](../team/changes.md)).

## Stop, archive or delete a task {#stop-archive-or-delete-a-task}

| | How | What stays |
| --- | --- | --- |
| **Stop** | Tell your agent | The documents |
| **Archive** | The task's **…** menu; **Restore** undoes it | Everything |
| **Delete** | The same menu | Nothing: the plan folder goes to the Trash |
