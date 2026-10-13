---
title: Your first task
description: One change, from your request to a merged pull request.
---

![Your first task in seven moves: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-light.svg)
![Your first task in seven moves: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-dark.svg)

Pick a medium-sized feature in a repository you know. Your agent asks each decision in the App, and its terminal shows a single line while it waits. You can keep its terminal beside the App, or use **Here in the App** in the unreleased App-run candidate.

:::note Local candidate
App runs are built but still undergoing qualification. These instructions describe the unreleased candidate. Windows uses **In my terminal** for now.
:::

| | You do | Where |
| --- | --- | --- |
| 1 | **Describe the change:** `/ql add a CSV export to the reports page` (`$ql` in Codex), or **+ New** | Your agent or the App |
| 2 | **Answer the questions.** They arrive as a batch in **Your turn**; each answer reaches your agent immediately | App |
| 3 | **Read the Plan**, then **Approve Plan** or **Give feedback** | App |
| 4 | **Start the build** in the App, or copy the terminal command Implement shows | App or your agent |
| 5 | Nothing: agents build and check on their own | |
| 6 | **Confirm what only you can**, look at the result, approve | App |
| 7 | **Merge the pull request** in your own process | GitHub |

<details>
<summary>Good to know</summary>

- Saying "Using QualityLayer, plan …" works too. Without the name, nothing starts.
- In **Your turn**, **Skip for now** moves on; **Tell me more** asks for detail.
- A comment you leave on any passage reaches your agent within a minute and is answered on the comment.
- The Outline needs no approval: the build session writes it from the approved Plan, then builds it. For a small task, planning can write it while the Plan waits.
- With several approved Plans waiting, "Implement this using QualityLayer" lists their commands.

</details>

In **+ New**, choose **Here in the App**, your agent and the repository, then write your request. The window opens for any folder-trust or permission prompt. It stays open until the agent starts its first turn; later it can fold into the dock. Folding the window keeps the run going. **In my terminal** shows the command instead.

Before starting, check **Permissions** and **Works in**. Your agent's own settings preserve its normal prompts. Bypass needs a separate confirmation for this run. A new session can use the current checkout; it does not require a new worktree. Read [App runs](app.md#agent-runs) for typing, Stop and resume.

Next: [The App](app.md), then [the steps](steps/discuss.md).
