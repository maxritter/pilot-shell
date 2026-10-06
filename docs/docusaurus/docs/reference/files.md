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

Everything stays on your computer until you share: your code, the diff, every plan document, the evidence and the cost view. Your agent keeps sending your code to its own provider, as it always does.

### Without sharing

Sharing is optional. Without it, the App and the CLI call QualityLayer only for:

- **Your licence:** a check about once a day, plus activating it or starting the trial.
- **The workflow texts** your agent follows, kept for a day.
- **Updates** of the App.

With a paid licence, the licence check also carries usage events: which steps ran and how they ended, marked with a short hash of your licence key, never a name, path, branch, title or text. Turn them off in **Settings › Licence**, with `qualitylayer telemetry off`, or with `DO_NOT_TRACK=1`.

### When you share {#sharing}

With a Team plan, the task title, the Plan, comments and link shares are encrypted on your computer with your team's key before they leave it. The server sees who is involved (names and e-mails), the step and when, not your plans or comments. A share link carries its own key, which never reaches the server. Never your code, the diff or your logs.

The QualityLayer API runs in Frankfurt, and backups are encrypted and kept in the EU. If your team connects Slack, the task title and the question pass through our server to Slack.

## Feedback {#feedback}

![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-light.svg)
![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-dark.svg)

**Feedback** in the sidebar sends your text, any screenshots you add and diagnostics you can read first under **Show what is sent**. It becomes an issue in a private repository. Diagnostics never include code, plan text, task titles, repository or branch names, or file paths.
