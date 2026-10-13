---
title: Files and privacy
description: What a task writes into your repository, what stays on your computer, and what leaves it.
---

## A task's files

![A task folder in docs/plans: seven documents, local interactive designs, reviews, command output, and evidence pictures and recordings](pathname:///img/diagrams/files-light.svg)
![A task folder in docs/plans: seven documents, local interactive designs, reviews, command output, and evidence pictures and recordings](pathname:///img/diagrams/files-dark.svg)

Each task gets a folder in `docs/plans/`: plain Markdown, committed with the change. Uninstalling never touches it.

| In the folder | What it holds |
| --- | --- |
| **Seven documents** | One per step, readable on GitHub too. The App draws its live parts over sections QualityLayer marks |
| `design/` | Local designs and their revisions. Shared only with **Include designs** ([Designs](../designs.md)) |
| `reviews/` | What the other agents wrote: the Plan review, the Outline check, the second opinion, when they ran |
| `records/` | The raw output of every command, and `pull-request-body.md` once Review starts |
| `evidence/` | Pictures and recordings the checks made |

The pull request step writes no document; the pull request lives on GitHub.

## The seven documents {#documents}

Each document opens with what you read first, then working sections (code shapes, paths, commands) shown only in the reader. QualityLayer refuses a document whose marked sections were edited by hand.

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
| `.qualitylayer/designs/<name>/` in the repository | A [lasting design](../designs.md#keep): its pages, scripts, styles, fonts and pictures, and a `design.json` with its title, what it shows, its first page (`entry`) and an optional Claude Design link. Committed with the change |
| `design.json` `source` | Optional. Another folder of the same repository that holds the design's files. A folder outside the repository, or behind a symbolic link, is refused |
| `docs/designs/` | Designs kept only on this Mac, out of git |
| `~/.qualitylayer/project-look.json` | How the sidebar shows your projects on this computer: order, color, display name, hidden, and other projects' lasting designs listed under each. Delete it to reset |

Folds, grouping and rows belong to the App window, not to a file.

## What stays on your computer, and what leaves it {#privacy}

![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-light.svg)
![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-dark.svg)

Your code, the diff, plan documents, evidence and the cost view stay on your computer until you share. Your agent still sends code to its own provider, as it always does.

| | What is sent |
| --- | --- |
| **Always** | A daily licence check to qualitylayer.dev (plus activation or the trial start), the workflow texts your agent follows, and App updates. No usage events |
| **When you share** | Tasks, documents and comments, encrypted on your computer with your team's key. **Include designs** adds the task's design previews; it starts off for existing shares. The server sees names, e-mails, the step and when, never the content. A share link carries its own key, which never reaches the server |
| **Never** | Repository code, the diff, host logs, launch settings, terminal output and command output. Shared design previews run no scripts |
| **With Slack** | The task title and the question, through the QualityLayer server to Slack |
| **Instructions** | Yours (`~/.qualitylayer/instructions.md`) never leave your computer. The team owner's are encrypted with the team's key before sending; each teammate's computer keeps a copy only its user can read ([Team instructions](settings.md#team-instructions)) |
| **Lasting designs** | A design kept **In the repository** travels with your commits and pull requests, so anyone who can read the repository can read it. **Only on this Mac** keeps it out of git |
| **Project lessons** | Local lessons stay in your QualityLayer home. Where you turn on memory sharing, eligible lessons become files under `.qualitylayer/memories/` and travel through your Git pushes, separate from encrypted task sharing ([Project memory](../memory.md)) |

The QualityLayer API runs in Frankfurt; backups are encrypted and kept in the EU.

Agent runs started in the App keep terminal output in local folders only you can read, outside the task's Markdown and never in shared copies. A screenshot you attach to feedback can show that output, so check it first.

## Feedback {#feedback}

![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-light.svg)
![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-dark.svg)

**Feedback** in the sidebar sends your text, any screenshots, and diagnostics you can read first under **Show what is sent**. It becomes an issue in a private repository. Diagnostics never include code, plan text, task titles, repository or branch names, or file paths.
