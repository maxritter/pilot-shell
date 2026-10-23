---
title: Files and privacy
description: What a task writes into your repository, what stays on your computer, and what leaves it.
---

## A task's files

![A task folder in docs/plans: seven documents, local interactive artifacts, reviews, command output, and evidence pictures and recordings](pathname:///img/diagrams/files-light.svg)
![A task folder in docs/plans: seven documents, local interactive artifacts, reviews, command output, and evidence pictures and recordings](pathname:///img/diagrams/files-dark.svg)

Each task gets a folder in `docs/plans/`: plain Markdown, committed with the change. Uninstalling never touches it. Feature and Bugfix tasks use the seven documents below. A [Chat](../chat.md) starts without those workflow documents and saves optional work in its own task folder.

| Chat file | What it holds |
| --- | --- |
| `chat-plan.md` | The Markdown plan saved on request, opened in the Reader |
| `chat-slices.md` | The build outline derived from that saved plan, with task cards and validation commands |
| `artifacts/`, `reviews/`, `records/` | Optional artifacts, independent review reports and helper records |

The conversation belongs to the agent's local session history. **Start the workflow** keeps the task and conversation, and uses the saved Chat work as Discuss context; it does not treat the Chat plan as an approved workflow Plan.

| In the folder | What it holds |
| --- | --- |
| **Seven documents** | One per step, readable on GitHub too. The App draws its live parts over sections QualityLayer marks |
| `artifacts/` | Local artifacts and their revisions. Shared only with **Include artifacts** ([Artifacts](../artifacts.md)) |
| `reviews/` | What the other agents wrote: the Plan review and the second opinion, when they ran |
| `records/` | The raw output of every command, and `pull-request-body.md` once Review starts |
| `evidence/` | Pictures and recordings the checks made |

The pull request step writes no document; the pull request lives on GitHub.

## The seven documents {#documents}

Each document opens with what you read first, then working sections (code shapes, paths, commands) shown only in the reader. QualityLayer refuses a document whose marked sections were edited by hand.

| File | What it holds |
| --- | --- |
| `01-discuss.md` | Your request, the problem, **Done means**, the scope and what you decided. A bug adds when it happens; the Product level adds the success measure, first release and what the user sees |
| `02-research.md` | **How the code works today:** findings, risks, how it is tested, what you decided. A bug's is **Why it breaks** |
| `03-plan.md` | **The decided design:** what it rests on, the artifacts and decisions, **Not doing**, **Before the build**, how we will know it works, who reviewed it |
| `04-outline.md` | **The build, slice by slice:** order, slices, how each point is proved, and every command the build runs |
| `05-implement.md` | **The build as it runs:** slices and their state, the recorded checks, what was decided while building |
| `06-verify.md` | **What was checked:** the checks and their results, each point with its evidence, what is still open |
| `07-review.md` | **The change:** first the pull request's description, word for word, then what you settled and how it ships |

## Lasting artifacts and how projects look {#lasting}

| File | What it holds |
| --- | --- |
| `.qualitylayer/artifacts/<name>/` in the repository | A [lasting artifact](../artifacts.md#keep): its pages, scripts, styles, fonts and pictures, and an `artifact.json` with its title, what it shows, its first page (`entry`) and an optional Claude Design link. Committed with the change. Artifacts stored earlier in `.qualitylayer/designs/` are still read as artifacts; saves go to the artifacts folder |
| `artifact.json` `source` | Optional. Another folder of the same repository that holds the artifact's files. A folder outside the repository, or behind a symbolic link, is refused |
| `docs/artifacts/` | Artifacts kept only on this computer, out of git |
| `~/.qualitylayer/project-look.json` | How the sidebar shows your projects on this computer: order, color, display name, hidden, and other projects' lasting artifacts listed under each. Delete it to reset |

Folds, grouping and rows belong to the App window, not to a file.

## What stays on your computer, and what leaves it {#privacy}

![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-light.svg)
![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-dark.svg)

Your code, the diff, plan documents, evidence and the cost view stay on your computer until you share. Code your team reviews travels only through your own Git remote. Your agent still sends code to its own provider, as it always does.

| | What is sent |
| --- | --- |
| **Always** | A daily licence check to qualitylayer.dev (plus activation or the trial start), the workflow texts your agent follows, and App updates. No usage events |
| **When you share** | Tasks, documents and comments, encrypted on your computer with your team's key. **Include artifacts** adds the task's artifact previews; it starts off for existing shares. The server sees names, e-mails, the step and when, never the content. A share link carries its own key, which never reaches the server |
| **When your team reviews the code** | **Ask for review** pushes the task's branch to your own Git remote, only when you click it. QualityLayer's servers store the team's comments on lines, the short lines of code they quote (up to 300 characters each) and the repository, branch and commits they point to, all encrypted with your team's key. They never receive the code itself |
| **Not included automatically** | Repository source, diffs, host logs, launch settings, terminal output and command output. Text or attachments you explicitly share can contain code or other sensitive content. Shared artifact previews run no scripts |
| **With Slack** | The task title and the question, through the QualityLayer server to Slack |
| **Instructions** | Yours (`~/.qualitylayer/instructions.md`) are stored locally and supplied to your agent; a cloud agent may send them to its provider. The team owner's are encrypted with the team's key before sending; each teammate's computer keeps a copy only its user can read ([Team instructions](settings.md#team-instructions)) |
| **Lasting artifacts** | An artifact kept **In the repository** travels with your commits and pull requests, so anyone who can read the repository can read it. **Only on this computer** keeps it out of git |
| **Project lessons** | Local lessons stay in your QualityLayer home. Where you turn on memory sharing, eligible lessons become files under `.qualitylayer/memories/` and travel through your Git pushes, separate from encrypted task sharing ([Project memory](../memory.md)) |

The QualityLayer API runs in Frankfurt; backups are encrypted and kept in the EU.

Agent runs started in the App keep terminal output in local folders only you can read, outside the task's Markdown and never in shared copies. A screenshot you attach to feedback can show that output, so check it first.

## Report a problem {#feedback}

![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-light.svg)
![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-dark.svg)

**Report** in the sidebar sends your text, any screenshots, and diagnostics you can read first under **Show what is sent**. It becomes an issue in a private repository. Diagnostics never include code, plan text, task titles, repository or branch names, or file paths.
