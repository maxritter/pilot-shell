---
title: Files and privacy
description: What a task writes into your repository, what stays on your computer, and what leaves it.
---

## A task's files

![A task folder in docs/plans: seven documents, local interactive designs, reviews, command output, and evidence pictures and recordings](pathname:///img/diagrams/files-light.svg)
![A task folder in docs/plans: seven documents, local interactive designs, reviews, command output, and evidence pictures and recordings](pathname:///img/diagrams/files-dark.svg)

Each task gets a folder in `docs/plans/`: plain Markdown, committed with the change, so it goes through your normal review and history. Uninstalling never touches it.

| In the folder | What it holds |
| --- | --- |
| **Seven documents** | One per step, readable on GitHub too. The App draws its live parts over sections QualityLayer marks |
| `design/` | Local designs and their revision history. Sharing includes them only when you choose **Include designs** ([Designs](../designs.md)) |
| `reviews/` | What the other agents wrote: the Plan review, the Outline check, the second opinion. Only those that ran |
| `records/` | The raw output of every command, and `pull-request-body.md` once Review starts |
| `evidence/` | Pictures and recordings the checks made |

The pull request step writes no document; the pull request lives on GitHub.

## The seven documents {#documents}

Each document opens with what you read first, then working sections (code shapes, paths, commands) that only the reader shows. QualityLayer refuses a document whose marked sections were edited by hand.

| File | What it holds |
| --- | --- |
| `01-discuss.md` | Your request, the problem, **Done means**, the scope and what you decided. A bug adds when it happens; the Product level adds the success measure, first release and what the user sees |
| `02-research.md` | **How the code works today:** findings, risks, how it is tested, what you decided. A bug's is **Why it breaks** |
| `03-plan.md` | **The decided design:** what it rests on, the designs and decisions, **Not doing**, **Before the build**, how we will know it works, who reviewed it |
| `04-outline.md` | **The build, slice by slice:** order, slices, how each point is proved, and every command the build runs |
| `05-implement.md` | **The build as it runs:** slices and their state, every recorded check, what was decided while building |
| `06-verify.md` | **What was checked:** the six checks, each point with its evidence, what is still open |
| `07-review.md` | **The change:** first the pull request's description, word for word, then what you settled and how it ships |

## Lasting designs and how projects look {#lasting}

| File | What it holds |
| --- | --- |
| `.qualitylayer/designs/<name>/` in the repository | A [lasting design](../designs.md#keep): its pages, scripts, styles, fonts and pictures, and a `design.json` with its title, what it shows, its first page (`entry`) and, if you gave one, its Claude Design link. Commit it with the change; it goes through pull requests like code |
| `design.json` `source` | Optional. Names another folder of the same repository where the design's files are, for a design that already lives there. A folder outside the repository, or one that crosses a symbolic link, is refused |
| `docs/designs/` | Designs kept only on this Mac. Git does not see them |
| `~/.qualitylayer/project-look.json` | How the sidebar shows your projects on this computer: their order, color, display name, whether each is hidden, and the lasting designs of other projects listed under it. The folders keep their own names. Delete the file to start from the defaults |

Folds, grouping and rows are remembered by the App window you use; they are not in a file you can edit.

## What stays on your computer, and what leaves it {#privacy}

![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-light.svg)
![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-dark.svg)

Your code, the diff, every plan document, the evidence and the cost view stay on your computer until you share. Your agent keeps sending code to its own provider, as it always does.

| | What is sent |
| --- | --- |
| **Always** | A daily licence check to qualitylayer.dev (plus activation or the trial start), the workflow texts your agent follows, and App updates. No usage events |
| **When you share** | Tasks, documents and comments, encrypted on your computer with your team's key. **Include designs** adds the task's selected design previews; it starts off for existing shares. The server sees names, e-mails, the step and when; never the content. A share link carries its own key, which never reaches the server |
| **Never** | Repository code, the diff, host logs, launch settings, terminal output and command output. Shared design previews disable scripts and navigation; they do not give a reviewer your local interactive session |
| **With Slack** | The task title and the question, through the QualityLayer server to Slack |
| **Instructions** | Your own instructions (`~/.qualitylayer/instructions.md`) never leave your computer. The team owner's are encrypted with the team's key before they are sent; each teammate's computer keeps a local copy, readable by its user alone ([Team instructions](settings.md#team-instructions)) |
| **Lasting designs** | A design kept **In the repository** is a file in `.qualitylayer/designs/`. It travels with your commits and pull requests, so anyone who can read the repository can read it. **Only on this Mac** keeps it out of git |
| **Project lessons (next release)** | Local lessons stay in your QualityLayer home. For repositories where you enable memory sharing, eligible lessons become readable files under `.qualitylayer/memories/` and travel through your normal Git commits and pushes. This is separate from encrypted task sharing. See [Project memory](../memory.md) |

The QualityLayer API runs in Frankfurt, and backups are encrypted and kept in the EU.

The unreleased App-run candidate keeps terminal output and process records in owner-only local run folders. They are separate from the task's Markdown and stay out of Team and public copies. An image you deliberately attach to feedback can contain that output; review it before sending.

## Feedback {#feedback}

![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-light.svg)
![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-dark.svg)

**Feedback** in the sidebar sends your text, any screenshots you add, and diagnostics you can read first under **Show what is sent**. It becomes an issue in a private repository. Diagnostics never include code, plan text, task titles, repository or branch names, or file paths.
