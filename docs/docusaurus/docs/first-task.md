---
title: Your first task
description: One change, from your request to a merged pull request.
---

![Your first task in seven moves: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-light.svg)
![Your first task in seven moves: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-dark.svg)

Open QualityLayer in the App or browser and pick a medium-sized feature in a repository you know. The task is on the left; your agent works in the **Agent** sidebar on the right.

| | You do | Where |
| --- | --- | --- |
| 1 | Choose **+ New** and **Feature** or **Bugfix**. Describe the change, attach files if needed, then choose your agent | App or browser |
| 2 | **Answer the questions.** They arrive as a batch in **Your turn**; each answer reaches your agent immediately | App or browser |
| 3 | **Read the Plan**, then **Approve Plan** or **Give feedback** | App or browser |
| 4 | **Start the build** | App or browser |
| 5 | Follow Outline, Implement and Verify. Human-only prerequisites and blocked checks are recorded for Review | App or browser |
| 6 | **Confirm what only you can**, look at the result, approve | App or browser |
| 7 | **Merge the pull request** | GitHub |

**New task** asks for a **Feature** or **Bugfix**, your request with any files, and where the agent runs. **Start the build** asks the same last question.

- **In QualityLayer** (recommended): pick the agent (Claude Code, Codex, Pi or OpenCode), model, effort, project and branch. The agent opens in the right sidebar beside the task, and every question and piece of feedback happens in the App.
- **In my terminal, app or IDE**: copy one prompt into any coding agent. Files you attached are listed in the prompt by path. The agent asks its questions and takes your feedback in its own chat.

New task and Start the build open with your last choice. See [Agent runs](app.md#agent-runs).

Claude Code, Codex, Pi and OpenCode have [native setup and session controls](agents/native.md). Other coding agents [use the CLI and a copied prompt](agents/other.md). Global settings cover appearance and reviewers; launch choices apply to the current run.

<details>
<summary>Good to know</summary>

- When the agent runs in your terminal, app or IDE, it asks each decision in its own chat. The App shows those questions without answering them.
- Name QualityLayer or QL when asking it to start work; follow-up answers continue the authorized task. No slash command is needed.
- Each step's page opens with what needs you, then the gist, then **Look here** for anything only you can still do. The rest opens from its row or in the document ([the step page](app.md#step-pages)).
- **Skip for now** moves to the next question; **Tell me more** asks for detail.
- Select a passage to give feedback. It reaches the agent when it next reads the task; a stopped or disconnected agent cannot answer yet.
- You can stop or pause the run. Your agent's own permission and sign-in prompts still require their normal response.
- To continue elsewhere, stop the old run if it is still active. Name the same task: “Using QL, continue implementation of task retry-webhooks.” Its recorded stage, approved Plan and evidence are kept.
- With several approved Plans waiting, "Implement this using QualityLayer" lists their commands.

</details>

Next: [The App](app.md), then [the steps](steps/discuss.md).
