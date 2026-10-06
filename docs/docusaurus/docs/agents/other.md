---
title: Other agents
description: Any coding agent that can run shell commands can follow QualityLayer's five steps.
---

Claude Code and Codex are set up for you. Any other coding agent works too, as long as it can run shell commands in your repository.

![Connecting another coding agent: it needs the qualitylayer command on its path and the skill text from Copy, For another agent; then it follows the same five steps and you decide in the App](pathname:///img/diagrams/agents-other-light.svg)
![Connecting another coding agent: it needs the qualitylayer command on its path and the skill text from Copy, For another agent; then it follows the same five steps and you decide in the App](pathname:///img/diagrams/agents-other-dark.svg)

1. **Check the CLI.** In the agent's terminal, `qualitylayer help` lists the commands. If it does not, run `qualitylayer doctor`.
2. **Give it the prompt.** In the App, **+ New › Another agent** gives one prompt with your request; **Copy › For another agent** copies the skill text. Paste it into a session in your repository.
3. **Work as usual.** The task appears in the App, and you answer each decision there. For Implement, pick **Another agent** under **Build with** and paste the prompt into a fresh session. It runs on its own models and effort, set in that agent.

Everything in the five steps works the same. The [second opinion](../reference/settings.md#second-opinion) needs Claude Code and Codex both.
