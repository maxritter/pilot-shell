# Changelog

Notable changes to QualityLayer and its predecessor, Pilot Shell.

## 12.1.0

Run seven coding agents, plan in the App and build where you like, and see at every moment what your agents are doing.

- **Small changes stay small.** A change that touches one area and a few files gets a one-page Plan. One fresh agent that did not write the code adds the missing tests and checks the work against your request.
- **Plan in the App, build in your terminal, or the other way round.** The App follows an agent working outside it, shows its progress, and offers **Continue it here**. The planning agent finishes once the build is picked up. Every step page says where it ran, such as "Built in Codex · terminal".
- **Questions say where to answer.** When an agent asks in your terminal, the App's card says **Answer in Codex** and offers **Answer here instead**. An answer typed in the chat, such as "1. Approve", counts as your answer.
- **Every comment gets an answer.** Comments on a step's document or an artifact show where they are: queued, being read, answered or changed. If the agent is busy, a helper answers within about 90 seconds, or at once with **Answer now with a helper**. Comment text can be selected and copied.
- **Review before you approve.** Open the code review from the Review page, also when the agent built outside the App. Each file says why it changed and which task card wrote it. Generated files and the task's own documents fold away. A fix you asked for and no longer want can be taken back.
- **Home shows whose move it is.** Needs you and Running show each task's step out of seven and its next move, such as "Answer Anna" or "Codex working".
- **A second opinion from another model maker.** Settings › Workflow › Second opinion can pick an agent from another maker, so GPT checks Claude's work and Claude checks GPT's.
- **The server port is a setting.** Settings › About › Server shows the port in use and lets you change it. `QUALITYLAYER_PORT` sets it for one start, `qualitylayer app status` prints it, and a taken port moves to the next free one without changing your setting. Useful when several machines forward to one laptop.
- **Agents are found where they install.** Codex from its standalone installer, the ChatGPT app, npm, nvm or Homebrew, and Claude Code in `~/.local/bin`, appear in New task and Settings. Settings › Agents shows where each was found, and a missing one says where QualityLayer looked.
- **Codex asks with its choice list.** Outside Plan mode, Codex shows QualityLayer's questions in its own picker. An untouched list closes after two minutes and comes back as numbered choices in the chat.
- **Signed Windows downloads.** The Windows App, installer and command line are signed by Maximilian Ritter.
- **Clearer waiting.** Home, the Artifacts list, artifact pages, tasks and the App's first window show what is loading. When an agent stops at its own start-up question, such as trusting a folder, the App shows it with **Open the terminal**.
- **A guided tour.** Twelve stops through the App's real views, from your first task to feedback and the Conversation and Terminal switch.
- **Settings details.** About shows how much disk QualityLayer uses. Licence shows your masked key with **Change…** and when the plan renews. Team renews a shared link in place. Appearance › Animations follows your system or can be reduced.
- **Seven coding agents.** Cursor, Grok and Antigravity join Claude Code, Codex, Pi and OpenCode. Each runs in its own terminal with its own sign-in. Setup shows each one with its plan and offers **Install…** for one that is missing.
- **Each agent's own permission modes.** The row under the message box lists the modes your agent really has, such as Ask first, Auto or Accept edits. A mode that skips every check asks you to confirm.
- **Plan limits.** See how much of your Claude Code and Codex plans is left in the sidebar, as a warning under the message box and in Settings. When Codex's weekly limit is used up, the App says it runs on credits and shows the balance. A build that stops on a limit can continue by itself when the window resets. The other agents report no limits, and the App says so.
- **Usage and cost.** Settings › Usage adds up tokens and estimated cost for the last 7, 30 or 90 days, by agent and by model. The Conversation footer shows the session's usage and the files it changed.
- **Messages wait their turn.** A message sent while the agent works waits in the App with **Interrupt and send** or **Remove from queue**. While a question waits on you, it goes to the agent at once.
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

## 12.0.0

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

## [11.0.9](https://github.com/maxritter/qualitylayer/releases/tag/v11.0.9) — 2026-10-21

- Sync project skills only for repositories that opted in.
- Update upstream tools to their latest stable releases.
- Update documentation development dependencies for follow-redirects and launch-editor security fixes.
