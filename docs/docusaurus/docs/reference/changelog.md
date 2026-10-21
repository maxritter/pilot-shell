---
title: Changelog
slug: /changelog
description: Current QualityLayer development changes and preserved Pilot Shell release history.
toc_max_heading_level: 2
---

Notable changes to QualityLayer and its predecessor, Pilot Shell.

<section class="cl-rel cl-latest">

<header class="cl-version">

## 12.1.0-beta.1

<p class="cl-published"><time data-release-version="12.1.0-beta.1">Publication date unavailable</time></p>

</header>

Run seven coding agents, see how much of each plan is left, and find your way around faster.

- **Seven coding agents.** Cursor, Grok and Antigravity join Claude Code, Codex, Pi and OpenCode. Each runs in its own terminal with its own sign-in. Setup shows each one with its plan and offers **Install…** for one that is missing.
- **Each agent's own permission modes.** The row under the message box lists the modes your agent really has, such as Ask first, Auto or Accept edits. A mode that skips every check asks you to confirm.
- **Plan limits.** See how much of your Claude Code and Codex plans is left in the sidebar, as a warning under the message box and in Settings. A build that stops on a limit can continue by itself when the window resets. The other agents report no limits, and the App says so.
- **Usage and cost.** Settings › Usage adds up tokens and estimated cost for the last 7, 30 or 90 days, by agent and by model.
- **Settings in the sidebar's place.** Workflow, Agents, Usage, Sessions, Notifications, Git and editor, Appearance, Memory, Licence, Team and About, each opening with one line, with a search for any setting.
- **Sessions you can see.** List the agents running now with the memory they use, and stop idle ones at once. QualityLayer can also stop agents that sit idle for 2 hours, 8 hours (the default) or a day. A stopped agent keeps its conversation.
- **Search everything with ⌘K.** Actions, projects with ⌘1 to ⌘9, tasks and the open task's files, in one box. Type `›` for actions only or `/` for files only.
- **A calmer sidebar and task header.** Task rows show the branch, the pull request with its checks and the agent's mark. Archive and Delete moved into the task's **More** menu, beside Copy branch name and Show task folder.
- **A conversation that is easier to read.** Finished turns fold into one line, files and commits become chips, each turn that changed files ends with its changes, and a strip of marks jumps between turns. Long sessions open at their last turns.
- **Files and Review.** The Files tab opens with the branch, its pull request and what changed. Open any file, or the checkout, in VS Code, Cursor, Zed, Finder or Terminal. Review shows the same file marks.
- **Pull requests watched.** QualityLayer reads an open pull request every 2 minutes. A failing check, a review asking for changes or a conflict appears in Needs you and wakes the task's agent, resuming its session if it stopped. It wakes it at most once per event and 3 times a day per pull request.
- **Your projects in Setup.** Setup lists the repositories your agents worked in lately, so you can add them in one step.
- **Update channel.** Choose Stable or Beta in Settings › About. Switching never takes you back to an older version.
- **Design review setting.** Choose whether a fresh agent checks each finished design once before you see it.



</section>

<section class="cl-rel">

<header class="cl-version">

## 12.0.0

<p class="cl-published"><time data-release-version="12.0.0">Publication date unavailable</time></p>

</header>

Plan coding tasks, work with your coding agents, and review the result before you approve it.

- Pilot Shell is now QualityLayer. Your active licence works with both products. Keep Pilot Shell 11 until you are ready to switch.
- **Seven steps with your approval.** Follow Discuss, Research, Plan, Outline, Implement, Verify and Review. Approve the Plan before implementation and inspect the result before shipping.
- **Your choice of coding agent.** Run Claude Code, Codex, Pi or OpenCode in the App, or connect a coding agent from your terminal, app or IDE.
- **Interactive artifacts.** Create screens, diagrams and other pages to agree on the design. Keep reusable artifacts in your Library and review changes from task drafts.
- **Code and evidence together.** Read changed files, diffs, review findings, check results and captured screenshots before approving the work.
- **Encrypted team collaboration.** Share tasks, artifacts, comments and attachments with your team. Set artifact access to view, comment or edit, and inspect saved versions.
- **Questions and handovers.** Ask teammates questions, request feedback and review replies in context. Pass approved work to a teammate through Git.
- **Agent session controls.** Choose the model and effort, follow Conversation or Terminal, and interrupt, stop or resume supported sessions.
- **Local project memory.** Search saved project lessons and choose which lessons to retain or share through your repository.



</section>

## Earlier releases

<details>
<summary>Pilot Shell release history</summary>

#### [11.0.9](https://github.com/maxritter/qualitylayer/releases/tag/v11.0.9) — 2026-10-21

- Sync project skills only for repositories that opted in.
- Update upstream tools to their latest stable releases.
- Update documentation development dependencies for follow-redirects and launch-editor security fixes.

</details>

[Published release downloads](https://github.com/maxritter/qualitylayer/releases)
