---
title: Files and privacy
description: What a task writes into your repository, what stays on your computer, and what leaves it.
---

## A task's files

![A task folder in docs/plans: seven documents, local interactive designs, reviews, command output, and evidence pictures and recordings](pathname:///img/diagrams/files-light.svg)
![A task folder in docs/plans: seven documents, local interactive designs, reviews, command output, and evidence pictures and recordings](pathname:///img/diagrams/files-dark.svg)

Each task gets a folder in `docs/plans/` in your repository: plain Markdown, committed with the change, so it goes through your normal review and history. Uninstalling QualityLayer never touches it.

- **Seven documents, one per step:** each holds everything about its step, and the App decides what to show where. The step page shows the sections that matter now; the reader shows the whole file. QualityLayer draws the live parts over the sections it marks and keeps plain Markdown underneath, so the files read well on GitHub too.
- **`design/`** holds the pages your agent drew for this task. Designs stay on your computer and out of Git; see [Designs](../designs.md). Designs for the whole project live in `docs/designs/`.
- **`reviews/`** holds what the other agents wrote, as they wrote it: the Plan review, the check of the Outline and the second opinion on the change. Only the reviews that ran appear.
- **`records/`** holds the raw output of every command the build and the checks ran. Once Review starts it also holds `pull-request-body.md`, the description the pull request is opened with. Its file lines link to their diffs in the pull request once it exists, and the reader marks the sections QualityLayer wrote as generated.
- **`evidence/`** keeps the pictures and recordings the checks made.

Nothing else goes in the folder.

## The seven documents {#documents}

Each document starts with the sections you read first, then the working sections: code shapes, file paths and commands, which the step page leaves to the reader. Who writes each part is fixed: your agent, QualityLayer itself between marked lines, or agents appending a block under its heading. QualityLayer refuses a document whose marked text was changed.

| File | What it holds |
| --- | --- |
| `01-discuss.md` | Your request in your own words, the problem, **Done means**, the scope, what you decided, and (for a bug) when it happens and what must keep working. Working sections: the links you gave and the first look at the code |
| `02-research.md` | **How the code works today:** a summary, the research questions, the findings, what the goal puts at risk, how the code is tested today, the open questions and what you decided. For a bug it is titled **Why it breaks**: the reproduction, the cause, what was ruled out. Working section: the code references |
| `03-plan.md` | **The decided design:** what it rests on, today and after the change, the designs, the engineering decisions, what you decided and what was decided for you, **Not doing**, **Before the build**, how we will know it works and who reviewed it. Working sections: the contracts between the parts, patterns to follow, what was proved before the build and the risks |
| `04-outline.md` | **The build, slice by slice:** how the build runs, the slices, the oracle, what was decided while outlining, how each point is proved and the check of the Outline. Working sections: the program design, the shape of the code, the scenarios and every command the build runs |
| `05-implement.md` | **The build as it runs:** the slices and their state, every recorded check and what was decided while building. Working sections: checkpoints, deviations, plan amendments and what a restarted session found |
| `06-verify.md` | **What was checked:** the six checks in order, each **Done means** point with its verdict and evidence, and what is still open. Working sections: the quality pass, the recorded project checks, each independent review, the fix rounds and the second opinion |
| `07-review.md` | **The change.** The first sections are the pull request's description, exactly as written: why the change, what a reviewer must know, what changed, three sections QualityLayer writes (the slices and their files, what was asked for and how each point was proved, and what was deliberately not changed), how it was verified, **Try it yourself** and any security findings. Then what was accepted with open items, what was decided while building, what you settled and the ship |

Your agent writes only the sections it owns. `05-implement.md` and `06-verify.md` are created when their steps start; the Plan, the Outline and the review sections are written by your agent.

Tasks you started before the seven steps keep the files and the five steps they began with. **Files** lists **Documents** with the state of each, then **Designs**, **Reviews** and **Records**; **Comments** holds their threads. The file chip in the document header names its document, and its menu copies the path or opens it in your editor. Implement opens on **Build** and keeps its written record available from **Files**.

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

Shared documents are the whole files of the reached steps, working sections included. Code, raw HTML, command output and interactive design pages stay outside that copy. An explicitly shared Plan may include a validated raster still of its named design, labelled as a picture. See [Design privacy](../designs.md#never-shared).

The QualityLayer API runs in Frankfurt, and backups are encrypted and kept in the EU. With Slack set up, notices go there. The task title and the question pass through our server to Slack.

## Feedback {#feedback}

![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-light.svg)
![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-dark.svg)

**Feedback** in the sidebar sends your text, any screenshots you add and diagnostics you can read first under **Show what is sent**. It becomes an issue in a private repository. Diagnostics never include code, plan text, task titles, repository or branch names, or file paths.
