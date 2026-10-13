---
title: Pull request
description: After you approve, QualityLayer opens the pull request and follows its checks and reviewers until you merge it.
---

![The eight steps, with Pull request highlighted](pathname:///img/diagrams/track-pull-request-light.svg)
![The eight steps, with Pull request highlighted](pathname:///img/diagrams/track-pull-request-dark.svg)

A task is not finished while its pull request is open. After **Approve and open a pull request** in [Review](review.md#approve), QualityLayer follows the pull request on GitHub and closes the task when you merge it. It never merges, and the first push is your click. Fixes during the watch go to that same branch.

![The Review page after the approval: the pull request with its checks and the reviewers who were asked, and the change from top to bottom folded beneath it](pathname:///img/app/pull-request-light.webp)
![The Review page after the approval: the pull request with its checks and the reviewers who were asked, and the change from top to bottom folded beneath it](pathname:///img/app/pull-request-dark.webp)

*Example task in a fictional project.*

## Following it {#following}

The Review page shows the pull request's checks, who was asked to review and what they said, with the approved change folded beneath. The step track reads **pull request open**. QualityLayer asks `gh` about once a minute while the App is open; without `gh`, the task closes at the approval.

## Your agent watches the checks {#watch}

Once the pull request is open, the agent that opened it stays with it until its checks pass. It runs `qualitylayer pr watch`, which waits for the checks to start and finish and then tells it what to do:

| Answer | What your agent does |
| --- | --- |
| Checks pass | Says so in one line and stops |
| A check fails | Reads the end of that check's log, fixes the cause in the task's code, runs the task's checks, commits, pushes the task's branch and watches again. It never weakens, skips or deletes a check |
| The branch conflicts with its base | Writes a short plan in the Review document, merges or rebases the way the repository does, resolves the files, runs the task's checks, pushes and watches again |
| Three attempts are used | Reports what still fails and stops for you |

Failing checks and conflicts share three fix attempts for each pull request. If you ask for more, the agent gets three again. It never merges and never force-pushes commits that are not its own.

The pull request card on the Review page shows the watch while it lasts: **Agent is watching checks**, **Fixing test · attempt 2 of 3**, **Resolving conflicts**, **Checks pass**, or **Stopped after 3 attempts: test still fails**. The sidebar and Home use the same words after "Pull request ·" while the agent is fixing, resolving or has stopped. A check that still fails after the third attempt keeps the task in **Needs attention**.

## When something waits for you {#waits}

![The pull request step: you approve and QualityLayer opens the pull request and follows its checks and reviewers; when a thread, a request for changes or a failing check arrives, your agent goes through it with you and you push the fix; you merge, and the task closes](pathname:///img/diagrams/pull-request-light.svg)
![The pull request step: you approve and QualityLayer opens the pull request and follows its checks and reviewers; when a thread, a request for changes or a failing check arrives, your agent goes through it with you and you push the fix; you merge, and the task closes](pathname:///img/diagrams/pull-request-dark.svg)

A new thread, a request for changes or a failing check brings the task back to **Needs attention**, with a line such as "Pull request · 2 threads, 1 check failing". **Your turn** gives you one command to copy: `/ql review <task>` (`$ql review <task>` in Codex).

1. Your agent goes through each thread with you and reads the log of a failing check, then fixes what needs fixing.
2. The fix stays on your computer until you press **Push the fix**.
3. GitHub runs its checks again, and QualityLayer keeps following.

Answers you settle are posted on GitHub in your name. **Leave them for now** keeps the threads open until something new arrives.

## Merged or closed {#merged}

When you merge, the task closes and moves to **Shipped** with what it cost. A pull request closed without a merge shows as closed. Either way the task keeps its documents in `docs/plans/`.
