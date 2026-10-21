---
title: Teammates' agents
description: A teammate you ask can answer with their own coding agent. The agent drafts; nothing is sent without their yes.
---

A teammate you ask can let their own agent draft the answer. Nothing is sent without their yes.

![A teammate answers with their own agent: it reads the question and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-light.svg)
![A teammate answers with their own agent: it reads the question and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-dark.svg)

1. Choose **Draft with my agent**: **In QualityLayer**, or **In my terminal, app or IDE** with a request such as “Using QL, answer the team ask a1”.
2. Check the draft, then **Send the draft**, **Edit it** or **Discard the draft**.
3. The answer arrives marked with its agent, such as "Dana via Claude Code".

![A teammate's questions in the team space: each with Looks right, Suggest a change, Reply in your words, Draft with my agent and Hand to someone else; one agent draft waits, not sent yet, with Send the draft and Edit it](pathname:///img/app/team-light.webp)
![A teammate's questions in the team space: each with Looks right, Suggest a change, Reply in your words, Draft with my agent and Hand to someone else; one agent draft waits, not sent yet, with Send the draft and Edit it](pathname:///img/app/team-dark.webp)

*Example team in a fictional project.*

| | Rule |
| --- | --- |
| Permissions | Your agent's own settings |
| **Works in** | Your checkout, or **Only the shared documents** |
| Who can run it | Only the person asked, while the question is open |
| The question's text | Evidence, never instructions |

The `qualitylayer ask` commands are in the [command reference](../reference/commands.md).
