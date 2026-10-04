---
title: Files and privacy
description: What a task writes into your repository, what stays on your computer, and what leaves it.
---

## A task's files

![A task folder in docs/plans: the Discuss and Plan documents with their details, research or diagnosis, mockups, the build record, reviews, evidence and the pull request text](pathname:///img/diagrams/files-light.svg)
![A task folder in docs/plans: the Discuss and Plan documents with their details, research or diagnosis, mockups, the build record, reviews, evidence and the pull request text](pathname:///img/diagrams/files-dark.svg)

Each task gets a folder in `docs/plans/` in your repository. Its documents are plain Markdown, committed with the change on the branch you are working on, so they go through your normal review and history. Uninstalling QualityLayer never touches them.

| File | Who reads it | What it holds |
| --- | --- | --- |
| `00-discuss.md` | You, in the App | The problem, Done means, what was decided with you; PRD sections when what to build was open |
| `00-discuss-details.md` | Your agent | Your words, verbatim, and the starting points in the code |
| `01-research.md` | Your agent | Research findings, when research ran |
| `01-diagnosis.md` | Your agent | A bug's reproduction and investigation |
| `02-plan.md` | You, in the App | The Plan you approve |
| `02-plan-details.md` | The builders | Contracts, patterns, the slices with their task cards, the scenarios |
| `03-build.md` | Your agent, the checking agents, the App | Notes from the build, the recorded checks, checkpoints, Polish and Security, verification |
| `03-build-details.md` | Your agent | Changes to the Plan made during the build |
| `artifacts/` | You | Mockups and diagrams |
| `evidence/` | You, the checking agents | Test output, logs and screenshots |
| `reviews/` | Your agent | Second-opinion findings, when it ran |
| `pr-description.md` | You | The approved pull request text |

Tasks planned with an older QualityLayer keep their older document names and still open in the App.

## What stays on your computer, and what leaves it {#privacy}

![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-light.svg)
![What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue](pathname:///img/diagrams/privacy-dark.svg)

- **Your computer:** your code, the diff, every plan document, the evidence, the App and its cost view. The cost view reads your agents' logs on your computer and sends nothing.
- **Your agent's provider:** your agent keeps sending your code to its own provider, as it always does. QualityLayer does not change that.
- **The licence check and usage events:** once a day. They carry a few anonymous events: a task started or shipped, a step entered, a check result, the name of a workflow step handed to your agent, a request handed back as too small. Never a repository name, path, branch, title or text. Turn the events off in **Settings › Licence**, with `qualitylayer telemetry off`, or with `DO_NOT_TRACK=1`.
- **The team service, only when you share:** the Plan and its progress, the task's title and step, and the comments. They are encrypted on your machine, so we can't read them. Only your team, or whoever has your link, can open them. We see who shared, an ID for the task, when and its step. Never your code, the diff or your logs. See [Review plans as a team](../team/plans.md).
- **A teammate's agent** reads a question and its task's documents on that teammate's own computer.
- **In a team review of the change:** Done means with its proof, the steps to try it, the check results and the screenshots they cite. The code is reviewed in your pull request, as always. See [Review changes as a team](../team/changes.md).

### What a feedback report sends {#feedback}

Feedback is the **Feedback** button in the sidebar, **Send feedback** in ⌘K, **Report this** on an error, or `qualitylayer feedback "<text>"`. Nothing is sent until you press **Send feedback**.

![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-light.svg)
![Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer](pathname:///img/diagrams/feedback-dark.svg)

A report goes to QualityLayer's service and becomes one issue in a **private** GitHub repository that only its maintainer can read. It carries:

- **Your text**, up to 5,000 characters, and whether it is something that does not work or an idea.
- **Screenshots you add**, up to five, stored privately with links that stop working after 90 days. A screenshot can show code or plans, so the sheet reminds you to check them.
- **Who it is from.** With a licence, your name and e-mail come from the licence, and the issue says they were verified. During the trial the sheet asks for a name and an e-mail so a reply can reach you; they are used for that report only.
- **Diagnostics**, on by default, and shown in full under **Show what is sent** before you send: the App and command-line versions, your system, the versions of Claude Code and Codex, the page you were on as a kind ("a task · Review step · Approve menu open"), your licence tier, and how many errors of which kinds happened in the last hour.

Diagnostics never include code, plan or document text, task titles, repository or branch names, or file paths. This is the same promise as the usage events.

You get a reference such as QL-128, and a reply goes to your e-mail when there is news. Offline, the report is saved on your computer and sent by itself when you are back online; **Copy it as text** is there if you would rather send it another way.

## What uninstalling removes

`qualitylayer uninstall` removes exactly what the installer added and puts back the settings it changed. `--purge` also removes your licence and the task state on your computer. Your plans in `docs/plans/` always stay.
