---
title: Pull request
description: Choose to open a pull request from Review, then follow its checks and reviewers until you merge it.
---

![The eight steps, with Pull request highlighted](pathname:///img/diagrams/track-pull-request-light.svg)
![The eight steps, with Pull request highlighted](pathname:///img/diagrams/track-pull-request-dark.svg)

After **Approve and open a pull request** in [Review](review.md#approve), QualityLayer follows the pull request on GitHub until you merge it. It never merges.

![The pull request with its checks and reviewers](pathname:///img/app/pull-request-light.webp)
![The pull request with its checks and reviewers](pathname:///img/app/pull-request-dark.webp)

*Example task in a fictional project.*

## Following it {#following}

The Review page shows the checks and reviewers, read through `gh` while the App is open. Without `gh`, the task closes at the approval.

## Your agent watches the checks {#watch}

The agent runs `qualitylayer pr watch` until the checks pass:

| Result | What your agent does |
| --- | --- |
| A check fails | Reads the log, fixes the cause, pushes, watches again. Never weakens or skips a check |
| The branch conflicts | Merges or rebases the way your repository does, then pushes |
| Three attempts used | Reports what still fails and stops |

It never force-pushes commits that are not its own.

## When something waits for you {#waits}

![Review threads and failing checks come back to you; you push the fix; you merge](pathname:///img/diagrams/pull-request-light.svg)
![Review threads and failing checks come back to you; you push the fix; you merge](pathname:///img/diagrams/pull-request-dark.svg)

A failing check, a review asking for changes or a conflict appears in **Needs you** and wakes the task's agent, resuming its session if it stopped. This works while the App is open and the pull request is open. The **Watch pull requests** switch in **Settings › Git and editor** is on by default.

The agent wakes once per event, at most 3 times a day per pull request, and not with less than 10 % of the plan left. Past a limit, the event only shows in Needs you, with the reason.

A new review thread or failing check moves the task to **Needs attention**:

1. Ask your agent: “Using QL, review task retry-webhooks”, naming your actual task.
2. Your agent works through each thread with you and fixes what needs fixing.
3. Press **Push the fix**. Your answers post on GitHub in your name.

## Merged or closed {#merged}

When you merge, the task moves to **Shipped** with what it cost. Its documents stay in `docs/plans/`.
