---
title: How to connect another coding agent
description: Any coding agent that can run shell commands can follow QualityLayer's five steps. What it needs, how to give it the skill, and what works without Claude Code or Codex.
---

Claude Code and Codex are set up for you. Any other coding agent can use QualityLayer too, as long as it can run shell commands and read files in your repository. Setup lists it as one row, **Another coding agent**, with **How to connect it** linking here.

![Connecting another coding agent: it needs the qualitylayer command on its path and the skill text from Copy, For another agent; then it follows the same five steps and you decide in the App](pathname:///img/diagrams/agents-other-light.svg)
![Connecting another coding agent: it needs the qualitylayer command on its path and the skill text from Copy, For another agent; then it follows the same five steps and you decide in the App](pathname:///img/diagrams/agents-other-dark.svg)

## What the agent needs

1. **The command line on its path.** The App's first start puts `qualitylayer` (and `ql`) where your agents call it. In the agent's terminal, `qualitylayer help` should list the commands. If it does not, run `qualitylayer doctor`, or install with the [terminal installer](../install.md#the-terminal-installer).
2. **The skill text.** It tells the agent how to start a task, what each step asks of it and which commands to run. Use either of these:
   - **Copy › For another agent**, on any document in the App, copies a prompt for your agent. Paste it into a session in your repository.
   - If your agent reads skills from a folder, copy `~/.qualitylayer/skill/ql` into that folder. The agent then starts a task when you call it.

## How it goes

You describe the change to your agent, in a session in your repository, together with the prompt. The agent runs `qualitylayer next "<your request>"`. QualityLayer holds the task's state and tells the agent what the current step is, so the agent never decides the workflow itself. The task appears in the App, and the agent asks you each decision in its own window, as in [Discuss](../steps/discuss.md), [Plan](../steps/plan.md) and [Review](../steps/review.md).
For Implement, choose **Another agent** under **Build with** on the start card. It gives a plain prompt for the build: paste it into a fresh session.

## What works without Claude Code or Codex

Everything in the five steps. The App, the checks QualityLayer records and your approvals work the same for any agent.

The [second opinion](../reference/settings.md#second-opinion), where the other vendor's AI reviews the work, needs Claude Code and Codex both. [Session messaging](../reference/commands.md#session-messaging) works between Claude Code and Codex sessions.

## If it does not start

- The agent cannot find `qualitylayer`: its shell has a different path from yours. Run `qualitylayer doctor` in its terminal.
- The task does not show in the App: open the App from the same computer, or run `qualitylayer app`.
- The agent skips the steps: paste the prompt again at the start of the session. QualityLayer runs only when you ask for it.
