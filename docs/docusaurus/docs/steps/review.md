---
title: Review
description: Settle the few items agents could not settle for you, look at the result, then approve and ship. Also how to stop, archive or delete a task.
---

![The five steps, with Review highlighted](pathname:///img/diagrams/track-review-light.svg)
![The five steps, with Review highlighted](pathname:///img/diagrams/track-review-dark.svg)

The final approval is always yours. Review opens on what the checks could not settle for you. The proof that every point holds is one violet line, and the diff follows, grouped by the task that changed each file.

![Review: the items that need you, the Approve menu with its three ways to ship, the line of what agents proved, and the changes by task](pathname:///img/diagrams/review-light.svg)
![Review: the items that need you, the Approve menu with its three ways to ship, the line of what agents proved, and the changes by task](pathname:///img/diagrams/review-dark.svg)

## What needs you {#items}

The step line reads "Waits for your review", with how many items need you. Four kinds of item can wait:

| Item | Your answers |
| --- | --- |
| **Only you can confirm** | **I confirm**, or **Ask the agent to record it**. Something no agent may do, such as a call to a live service |
| **Look at the result** | **Looks right**, or **Change** with a pin on the spot. A real screenshot of the running App, for example. Click anywhere on it to pin a change |
| **Found while checking** | **Accept**, or **Fix it**. A note from the checking agents, with the file and what it costs to fix |
| **Decided by the agent during the build** | **Fine**, or **Ask why**. Choices the agent made on its own, which you may have already answered during Implement |

Fixes go back to the agent. It makes them, and only what they touch is checked again; then Review comes back to you. While it works, the step line reads "The agent is making your changes", and each of your notes shows picked up, done or checked.

## What the rest of the page shows

- **Checked by agents.** One violet line, for example 11 of 11 points of Done passed, 11 scenarios, 1,374 tests, evidence for each. It opens to the evidence. Each screenshot names the point of Done it proves.
- **What changed.** A short summary of the change.
- **Changes by task.** Each file carries the task that changed it. Files that other sessions committed, in the same range, are named **not this task** and are left out of the pull request.
- **A diff** where you can comment on any line. Your comments go to the agent with your decision.
- **Try it yourself.** Steps to try the whole change, in a fold, written by the agents that checked it.

## Approve, or send changes {#approve}

![One answer asks for a change, so the main button reads Send 1 change; the Comments panel lists your drafts, answered threads and your team's comments](pathname:///img/diagrams/comments-light.svg)
![One answer asks for a change, so the main button reads Send 1 change; the Comments panel lists your drafts, answered threads and your team's comments](pathname:///img/diagrams/comments-dark.svg)

Your answers are collected on your computer, like on the [Plan](plan.md). The main button sends them. If any answer asks for a change, it reads **Send 1 change** (or 2, 3 …) instead of Approve, and your comments go with it. **Comments · 3** in the step line opens a panel with your drafts, threads the agent has answered, and what your team said.

**Request changes…** sends free text to the agent.

The **Approve ▾** menu is where shipping lives:

| Choice | What it does |
| --- | --- |
| **Approve and open a pull request** | Pushes the branch and opens the pull request with the summary and the evidence. Needs `gh` |
| **Approve only** | You push and open the pull request yourself |
| **Copy the git commands** | For a machine without `gh` |

QualityLayer does this only when you click it. It never merges, and never switches your branch. A comment that changes Done means is recorded as an agreed change to the Plan, in your words. Your agent opens the final approval with `qualitylayer gate open final`; you can also type `approve` in its chat.

With a Team plan, teammates comment on any line in their own App and review the code in the pull request. See [Review changes as a team](../team/changes.md).

## Ready to ship

When every item is settled, the step line reads "Ready to ship": "All 5 items are settled. The 2 fixes are in and checked." The main button is **Approve and open a pull request**. The page also says how many files are not from this task and left out.

## Shipped {#shipped}

Shipped means you gave the final approval and the task is finished. The step line reads, for example, "Approved at 15:42. Pull request #412 is open on GitHub." The page keeps three facts: the pull request, with **Open on GitHub**; what you decided, with **Show**; and what it cost, with the cost by step. **Archive** moves the task out of the sidebar.

![Shipped: the task keeps its documents, what you decided and what it cost; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-light.svg)
![Shipped: the task keeps its documents, what you decided and what it cost; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-dark.svg)

The task keeps its documents, the build record, the evidence and the approved pull request description, all in `docs/plans/` in your repository. A closing record goes into `00-discuss.md`. In the App you can still open the diff and the evidence.

QualityLayer never pushes or opens a pull request by itself. Merging, deploying and releasing stay with your own process.

## Stop, archive or delete a task {#stop-archive-or-delete-a-task}

![Stop the task ends the work and keeps the documents; Archive hides a task; Delete removes its plan folder after asking](pathname:///img/diagrams/abandon-light.svg)
![Stop the task ends the work and keeps the documents; Archive hides a task; Delete removes its plan folder after asking](pathname:///img/diagrams/abandon-dark.svg)

- **Stop the task:** tell your agent, at any step, or choose it when checking stops. The work ends; the documents and evidence stay in your repository.
- **Archive:** takes a task off the sidebar. **Restore** brings it back. The Shipped list on Home shows how each task closed and what it cost.
- **Delete:** in **More**. The dialog names what is removed (the plan folder and its state) and what stays (commits and branches in git), and offers **Archive it instead**. It moves the files to the Trash.

Tasks from an older QualityLayer flow stay readable in the App. One that is still open asks you to finish it with the version that started it, or to start it again with `/ql`.
