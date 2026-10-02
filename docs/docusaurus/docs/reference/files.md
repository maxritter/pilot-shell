---
title: Files and privacy
description: What a task writes into your repository, what stays on your computer, and what leaves it.
---

## A task's files

![A task folder in docs/plans: a short and a detailed document per planning step, mockups, the build record, reviews, evidence and the pull request text](pathname:///img/diagrams/files-light.svg)
![A task folder in docs/plans: a short and a detailed document per planning step, mockups, the build record, reviews, evidence and the pull request text](pathname:///img/diagrams/files-dark.svg)

Each task gets a folder in `docs/plans/` in your repository. Its documents are plain Markdown, committed with the change on the branch you are working on, so they go through your normal review and history. Uninstalling QualityLayer never touches them.

## What stays on your computer, and what leaves it

![What stays on your computer, what the licence check sends, and what sharing sends to the team service](pathname:///img/diagrams/privacy-light.svg)
![What stays on your computer, what the licence check sends, and what sharing sends to the team service](pathname:///img/diagrams/privacy-dark.svg)

- **Your computer:** your code, the diff, every plan document, the evidence and the Cockpit itself.
- **Your agent's provider:** your agent keeps sending your code to its own provider, as it always does. QualityLayer does not change that.
- **The licence check:** once a day, with five anonymous events (task started, step entered, check result, task shipped, and the name of a step). Never a repository name, path, branch, title or text. Turn the events off with `qualitylayer telemetry off` or `DO_NOT_TRACK=1`.
- **The team service, only when you share:** the documents a reviewer reads, the task's title and step, and the comments, encrypted on your machine so we can't read them. Only your team, or whoever has your link, can open them. We see who shared, an ID for the task, when and its stage. Never your code, the diff or your logs. See [Review plans as a team](../team/plans.md).
- **In a team review of the change:** Done means with its proof, the steps to try it, the check results and the screenshots they cite. The code is reviewed in your pull request, as always. See [Review changes as a team](../team/changes.md).

## What uninstalling removes

`qualitylayer uninstall` removes exactly what the installer added and puts back the settings it changed. `--purge` also removes your licence and the task state on your computer. Your plans in `docs/plans/` always stay.
