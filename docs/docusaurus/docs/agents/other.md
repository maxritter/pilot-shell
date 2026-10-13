---
title: Other agents
description: Any coding agent that can run shell commands can follow QualityLayer's steps.
---

Claude Code and Codex are set up for you. Any agent that can run shell commands in your repository works too.

![Another agent with the qualitylayer command and the skill text follows the same steps](pathname:///img/diagrams/agents-other-light.svg)
![Another agent with the qualitylayer command and the skill text follows the same steps](pathname:///img/diagrams/agents-other-dark.svg)

1. In the agent's terminal, run `qualitylayer help`. No commands listed? Run `qualitylayer doctor`.
2. In the App, **+ New › Another agent** gives you a prompt. Paste it into a session in your repository.
3. Answer in the App. For Implement, pick **Another agent** under **Build with**.

Only the [second opinion](../reference/settings.md#second-opinion) needs both Claude Code and Codex.

<details>
<summary>For the agent's author</summary>

Run `qualitylayer wait --until-event` in the background; it returns on an event or after 30 minutes.

Checks run on a clean copy of the commit, without `.venv` or `node_modules`. Reach your folder with `$QL_REPO_ROOT`, for example `"$QL_REPO_ROOT/.venv/bin/python" -m pytest`.

</details>
