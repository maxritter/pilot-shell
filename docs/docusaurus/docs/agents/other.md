---
title: Other agents
description: Any coding agent that can run shell commands can follow QualityLayer's seven steps.
---

Claude Code and Codex are set up for you. Any other coding agent works too, as long as it can run shell commands in your repository.

![Connecting another coding agent: it needs the qualitylayer command on its path and the skill text from Copy, For another agent; then it follows the same seven steps and you decide in the App](pathname:///img/diagrams/agents-other-light.svg)
![Connecting another coding agent: it needs the qualitylayer command on its path and the skill text from Copy, For another agent; then it follows the same seven steps and you decide in the App](pathname:///img/diagrams/agents-other-dark.svg)

1. **Check the CLI.** In the agent's terminal, `qualitylayer help` lists the commands. If it does not, run `qualitylayer doctor`.
2. **Give it the prompt.** In the App, **+ New › Another agent** gives one prompt with your request; **Copy › For another agent** copies the skill text. Paste it into a session in your repository.
3. **Work as usual.** The task appears in the App, and you answer each decision there. For Implement, pick **Another agent** under **Build with** and paste the prompt into a fresh session. It runs on its own models and effort, set in that agent.

Everything in the seven steps works the same. The [second opinion](../reference/settings.md#second-opinion) needs Claude Code and Codex both.

When your agent can run a background command and resume when it ends, use `qualitylayer wait --until-event` for open App work. It returns on an event or after 30 minutes. A foreground `qualitylayer wait` keeps its 50-second default; handle its event or repeat after `pending`. See [the command reference](../reference/commands.md).

Approved checks run against a fresh copy of the committed tree. QualityLayer sets `QL_REPO_ROOT` to the original checkout so a command can find an ignored tool there, such as a Python environment:

```sh
"$QL_REPO_ROOT/.venv/bin/python" -m pytest tests/test_app.py
```

Keep tracked input paths relative to the fresh tree. If the original checkout has no required tool, include a setup step in the Plan.
