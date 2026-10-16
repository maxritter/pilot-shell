---
title: Your first task
description: One change, from your request to a merged pull request.
---

![Your first task in seven moves: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-light.svg)
![Your first task in seven moves: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-dark.svg)

Pick a medium-sized feature in a repository you know. Your agent asks each decision in the App, and its terminal shows a single line while it waits.

| | You do | Where |
| --- | --- | --- |
| 1 | **Describe the change:** `/ql add a CSV export to the reports page` (`$ql` in Codex, `/skill:ql` in Pi), or **+ New** | Your agent or the App |
| 2 | **Answer the questions.** They arrive as a batch in **Your turn**; each answer reaches your agent immediately | App |
| 3 | **Read the Plan**, then **Approve Plan** or **Give feedback** | App |
| 4 | **Start the build** | App or your agent |
| 5 | Follow Outline, Implement and Verify. Human-only prerequisites and blocked checks are recorded for Review | App or terminal |
| 6 | **Confirm what only you can**, look at the result, approve | App |
| 7 | **Merge the pull request** | GitHub |

**New task** and **Start the build** let you choose the agent, model, effort and workspace for that run. **In the App** opens the task's **Agent** conversation beside **Files** and **Feedback**; **In my terminal** gives you the launch command. See [App runs](app.md#agent-runs).

Claude Code, Codex, Pi and OpenCode have [native setup and session controls](agents/native.md). Other coding agents [use the CLI and a copied prompt](agents/other.md). Global settings cover run location, appearance and reviewers; launch choices apply to the current run.

<details>
<summary>Good to know</summary>

- "Using QualityLayer, plan …" works too. Without the name, nothing starts.
- **Skip for now** moves to the next question; **Tell me more** asks for detail.
- Select a passage to give feedback. It reaches the agent when it next reads the task; a stopped or disconnected agent cannot answer yet.
- You can stop or pause the run. Your agent's own permission and sign-in prompts still require their normal response.
- With several approved Plans waiting, "Implement this using QualityLayer" lists their commands.

</details>

Next: [The App](app.md), then [the steps](steps/discuss.md).
