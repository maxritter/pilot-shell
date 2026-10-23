# Changelog

Notable changes to QualityLayer and its predecessor, Pilot Shell.

## 12.1.0

Plan in the App and build where you like, with seven coding agents, and see what each one is doing.

- **Plan in the App, build in your terminal, or the other way round.** The App follows an agent working outside it, says where each step ran and offers **Continue it here**. When an agent asks you something in the terminal, the App says where to answer, and you can answer in the App instead.
- **Seven coding agents.** Cursor, Grok and Antigravity join Claude Code, Codex, Pi and OpenCode, each with its own sign-in and its own permission modes. QualityLayer finds Codex and Claude Code where their installers put them, including the ChatGPT app, npm and Homebrew.
- **Small changes stay small.** A change to one area and a few files gets a one-page Plan. One fresh agent adds the missing tests and checks the work against your request.
- **Review before you approve.** Open the code review from the Review page, also for builds outside the App. Each file says why it changed. The second opinion can come from another model maker, so GPT checks Claude's work and Claude checks GPT's.
- **Every comment gets an answer.** Comments on a step's document or an artifact show whether they are queued, being read, answered or changed. When the agent is busy, a helper answers within about 90 seconds.
- **Home shows whose move it is.** Each task shows its step and its next move, such as "Answer Anna" or "Codex working". A failing check, a requested change or a conflict on its pull request lands in Needs you and wakes the agent.
- **Plan limits and cost.** See how much of your Claude Code and Codex plans is left, including Codex credits. A build stopped by a limit can continue by itself when the window resets. Settings › Usage shows tokens and estimated cost by agent and model.
- **Signed Windows downloads.** The Windows App, installer and command line are signed by Maximilian Ritter.
- **A conversation that is easier to read.** Finished turns fold into one line, and files and commits become chips. A message you send while the agent works waits in a queue, where you can send it at once or remove it.
- **Find things faster.** ⌘K searches actions, projects, tasks and files. Settings has its own sidebar with a search, and a guided tour walks through the App.
- **Sessions and settings.** Settings › Sessions lists the running agents with their memory use and stops idle ones, after 8 hours by default. Settings › About sets the server port and the update channel, Stable or Beta.

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
