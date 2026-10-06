---
title: Files and privacy
description: What a task writes into your repository, what stays on your computer, and what leaves it.
---

## A task's files

![A task folder in docs/plans: one file per step, from 01-discuss to 05-review, with the agent's details beside Discuss, Plan and Implement, research or diagnosis, mockups, reviews and evidence](pathname:///img/diagrams/files-light.svg)
![A task folder in docs/plans: one file per step, from 01-discuss to 05-review, with the agent's details beside Discuss, Plan and Implement, research or diagnosis, mockups, reviews and evidence](pathname:///img/diagrams/files-dark.svg)

Each task gets a folder in `docs/plans/` in your repository: plain Markdown, committed with the change, so it goes through your normal review and history. Uninstalling QualityLayer never touches it.

Each step has one file for you (`01-discuss.md`, `02-plan.md`, `03-implement.md`, `04-verify.md`, `05-review.md`) and, where it helps, a `-details` file for the agents. `artifacts/` holds mockups and diagrams, `evidence/` the test output, logs and screenshots. The path of the file you are reading is at the top of the App.

## What stays on your computer, and what leaves it {#privacy}

![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-light.svg)
![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-dark.svg)

- **Stays on your computer:** your code, the diff, every plan document, the evidence and the cost view.
- **Your agent's provider:** your agent keeps sending your code to its own provider, as it always does.
- **The daily licence check** carries a few anonymous usage events, never a name, path, branch, title or text. Turn them off in **Settings › Licence**, with `qualitylayer telemetry off`, or with `DO_NOT_TRACK=1`.
- **When you share:** the Plan, its progress and the comments, encrypted on your computer so the QualityLayer Server cannot read them. Never your code, the diff or your logs. See [How it fits together](../intro.md#how-it-fits-together).

## Feedback {#feedback}

![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-light.svg)
![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-dark.svg)

**Feedback** in the sidebar sends your text, any screenshots you add and diagnostics you can read first under **Show what is sent**. It becomes an issue in a private repository. Diagnostics never include code, plan text, task titles, repository or branch names, or file paths.
