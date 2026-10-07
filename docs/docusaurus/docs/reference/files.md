---
title: Files and privacy
description: What a task writes into your repository, what stays on your computer, and what leaves it.
---

## A task's files

![A task folder in docs/plans: five human documents, local interactive designs, evidence pictures and recordings, and private agent details, logs and records](pathname:///img/diagrams/files-light.svg)
![A task folder in docs/plans: five human documents, local interactive designs, evidence pictures and recordings, and private agent details, logs and records](pathname:///img/diagrams/files-dark.svg)

Each task gets a folder in `docs/plans/` in your repository: plain Markdown, committed with the change, so it goes through your normal review and history. Uninstalling QualityLayer never touches it.

- **Five documents, one per step, for you:** `01-discuss.md`, `02-plan.md`, `03-implement.md`, `04-verify.md` and `05-review.md`. Each step's page in the App is its document; QualityLayer draws the live parts over the sections it marks, and keeps a plain Markdown version underneath, so the files read well on GitHub too. `05-review.md` becomes the pull request's description.
- **`agent/`** holds the agents' records: research, contracts, task cards, the build and checking logs, raw command output and second opinions. It is never shared. The document menu opens the agent's version and records in a read-only reader, with a way back to the human document.
- **`design/`** holds the pages your agent drew for this task. Designs stay on your computer and out of Git; see [Designs](../designs.md). Designs for the whole project live in `docs/designs/`.
- **`evidence/`** keeps the pictures and recordings the checks made.

Tasks you started before keep the files they have. **Files** lists the five documents and compact designs; **Comments** holds their threads. The file chip in the document header names its document, and its menu copies the path or opens it in your editor. Discuss and Plan show the complete text in reading order; Implement opens on **Build** and keeps its written record available from **Files**.

## What stays on your computer, and what leaves it {#privacy}

![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-light.svg)
![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-dark.svg)

Everything stays on your computer until you share: your code, the diff, every plan document, the evidence and the cost view. Your agent keeps sending your code to its own provider, as it always does.

### Without sharing

Sharing is optional. Without it, the App and the CLI contact QualityLayer for:

- **Your licence:** a daily check to qualitylayer.dev, plus activating it or starting the trial.
- **The workflow texts** your agent follows, kept for a day.
- **Updates** of the App.

QualityLayer sends no usage events. **Settings › Licence** describes what leaves this computer.

### When you share {#sharing}

With team sharing on, shared tasks, documents and comments go to the team backend. The task title, the Plan, comments and link shares are encrypted on your computer with your team's key before they leave it. The server sees who is involved (names and e-mails), the step and when, not your plans or comments. A share link carries its own key, which never reaches the server. Your code, the diff and your logs stay local.

Shared documents contain readable prose and proof from the reached steps. Code, raw HTML, agent records and interactive design pages stay outside that copy. An explicitly shared Plan may include a validated raster still of its named design, labelled as a picture. See [Design privacy](../designs.md#never-shared).

The QualityLayer API runs in Frankfurt, and backups are encrypted and kept in the EU. With Slack set up, notices go there. The task title and the question pass through our server to Slack.

## Feedback {#feedback}

![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-light.svg)
![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-dark.svg)

**Feedback** in the sidebar sends your text, any screenshots you add and diagnostics you can read first under **Show what is sent**. It becomes an issue in a private repository. Diagnostics never include code, plan text, task titles, repository or branch names, or file paths.
