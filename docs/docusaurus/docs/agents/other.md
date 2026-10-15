---
title: Other agents
description: Use QualityLayer with any coding agent that can run shell commands, including one that runs a model on your own machine.
---

[Claude Code, Codex, Pi and OpenCode](native.md) have native integrations. Any other agent that can run shell commands in your repository follows the same steps, including one on a local model.

![Another agent with the qualitylayer command and a prompt from the App follows the same steps](pathname:///img/diagrams/agents-other-light.svg)
![Another agent with the qualitylayer command and a prompt from the App follows the same steps](pathname:///img/diagrams/agents-other-dark.svg)

## Start a task {#start}

1. In the agent's terminal, run `qualitylayer help`. Nothing listed? Run `qualitylayer doctor`.
2. In the App, choose **+ New › Another agent**, describe the change and copy the prompt.
3. Paste it into your agent. Answer its questions and approve the Plan in the App.

## Plan with one agent, build with another {#mix}

![Plan with Claude Code, approve the Plan, build with another agent, then the same checks and your approval](pathname:///img/diagrams/agents-mix-light.svg)
![Plan with Claude Code, approve the Plan, build with another agent, then the same checks and your approval](pathname:///img/diagrams/agents-mix-dark.svg)

Pick **Another agent** under **Build with** when the build starts. To make it the default, use **Make default** in Settings › Workflow › [Planning and building](../reference/settings.md#defaults).

## Let the App open your agent {#app-start}

1. In Settings › Workflow › Agents › **More**, enter your agent's program and its arguments as a JSON array, such as `["--model", "my-model"]`.
2. Start with **Another agent** and press **Send the request** when its window is ready.

## What changes {#differences}

| | The four native agents | Another agent |
| --- | --- | --- |
| Setup | Done when you install | One pasted prompt |
| Model and effort | Set in QualityLayer | Set in your agent |
| Building | Workers build slices side by side | One session builds every slice |
| Window controls | Interrupt, Stop, Resume, Move | Stop |
| Cost panel | Per step | Not shown |
| [Second opinion](../reference/settings.md#second-opinion) | Choose an installed native reviewer | Can use an installed native reviewer |

Results depend on the model: it has to call tools reliably over many turns.

<details>
<summary>For the agent's author</summary>

The prompt asks the agent to run `qualitylayer next --json`, follow the reply and read the files it names, until the reply says done or stop.

To keep working after a question, run `qualitylayer wait --until-event` in the background. It returns on an answer, comment, review result or finished check, or after 30 minutes.

Checks run on a clean copy of the commit, without `.venv` or `node_modules`. Use `$QL_REPO_ROOT` to reach your folder, for example `"$QL_REPO_ROOT/.venv/bin/python" -m pytest`.

</details>
