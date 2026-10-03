---
title: Review
description: Your review of the finished change, alone or with your team, then your final approval and the pull request. Also how to stop, archive or delete a task.
---

![The five steps, with Review highlighted](pathname:///img/diagrams/track-review-light.svg)
![The five steps, with Review highlighted](pathname:///img/diagrams/track-review-dark.svg)

The final approval is always yours. Review puts everything you need to trust the change in one view: what changed, the evidence and the diff, with the pull request description already written.

![Review: what was built and checked, steps to try it, the files changed, Create pull request and the final approval](pathname:///img/diagrams/review-light.svg)
![Review: what was built and checked, steps to try it, the files changed, Create pull request and the final approval](pathname:///img/diagrams/review-dark.svg)

## In the App

| Tab | What it shows |
| --- | --- |
| Overview | Each point of your Done means with its proof and pictures, and a code health line: lines added and removed, each new module with its reason |
| Evidence | The recorded checks, the scenarios and Done means the judge ran, Polish and Security, and the second opinion when it ran |
| Try it | Steps to try the whole change yourself, written by the AI that checked it |
| Files changed | The change on your machine as a diff, files with open threads first; comment on any line |
| Conversation | Every thread with its context and state; filter Open, All or Resolved |

**Create pull request** pushes the branch and opens the pull request with the written description. QualityLayer does this only when you click it. Once the pull request exists, Review shows its number, state and checks.

## You decide

Press **Approve and ship**, or **Request changes** with a remark or line comments. Your comments go back to your agent. A fix is built test first and checked again. A comment that changes Done means is recorded as an agreed change to the Plan, in your words. Your agent opens the final approval with `qualitylayer gate open final`; you can also type `approve` in its chat.

With a Team plan, teammates comment on any line in their own App and review the code in the pull request. See [Review changes as a team](../team/changes.md).

## Shipped {#shipped}

Shipped means you gave the final approval and the task is finished.

![Shipped: the task keeps its documents and evidence; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-light.svg)
![Shipped: the task keeps its documents and evidence; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-dark.svg)

The task keeps its documents, the build record, the evidence and the approved pull request description, all in `docs/plans/` in your repository. A closing record goes into `00-discuss.md`. In the App you can still open the diff and the evidence.

QualityLayer never pushes or opens a pull request by itself. Merging, deploying and releasing stay with your own process. Shipped does not mean any of them has happened.

## Stop, archive or delete a task {#stop-archive-or-delete-a-task}

![Abandon stops the work and keeps the documents; Archive hides a task; Delete removes an archived task after asking](pathname:///img/diagrams/abandon-light.svg)
![Abandon stops the work and keeps the documents; Archive hides a task; Delete removes an archived task after asking](pathname:///img/diagrams/abandon-dark.svg)

- **Abandon:** tell your agent, at any step. The work stops; the documents and evidence stay in your repository.
- **Archive:** takes a task off the App's list. **Restore** brings it back.
- **Delete:** for archived tasks only. It asks first, then moves the files to the Trash. Commits and branches in git stay.

Tasks from an older QualityLayer flow stay readable in the App. One that is still open asks you to finish it with the version that started it, or to start it again with `/ql`.
