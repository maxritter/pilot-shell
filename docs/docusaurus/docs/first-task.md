---
title: Your first task
description: One change, from your request to a merged pull request.
---

![Your first task in seven moves: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-light.svg)
![Your first task in seven moves: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-dark.svg)

Pick a medium-sized feature in a repository you know, and keep the App open beside your agent. Your agent asks each decision in the App, and its terminal shows a single line while it waits.

| | You do | Where |
| --- | --- | --- |
| 1 | **Describe the change:** `/ql add a CSV export to the reports page` (`$ql` in Codex), or **+ New** | Your agent or the App |
| 2 | **Answer the questions.** They arrive as a batch in **Your turn**; each answer reaches your agent immediately | App |
| 3 | **Read the Plan**, then **Approve Plan** or **Give feedback** | App |
| 4 | **Start the build** with the one command Implement shows | Your agent |
| 5 | Nothing: agents build and check on their own | |
| 6 | **Confirm what only you can**, look at the result, approve | App |
| 7 | **Merge the pull request** in your own process | GitHub |

<details>
<summary>Good to know</summary>

- Saying "Using QualityLayer, plan …" works too. Without the name, nothing starts.
- In **Your turn**, **Skip for now** moves on; **Tell me more** asks for detail.
- A comment you leave on any passage reaches your agent within a minute and is answered on the comment.
- The Outline needs no approval: the build session you start writes it from the approved Plan, then builds it.
- With several approved Plans waiting, "Implement this using QualityLayer" lists their commands.

</details>

Next: [The App](app.md), then [the steps](steps/discuss.md).
