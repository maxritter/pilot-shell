---
title: Teammates' agents
description: A teammate you ask can answer with their own coding agent. The agent drafts; nothing is sent without their yes.
---

When you ask a teammate about your Plan, they can hand the question to their own agent. It reads the question and the Plan, looks at their code, asks them what it needs and drafts the answer. Nothing is sent without their yes.

![A teammate answers with their own agent: it reads the question and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-light.svg)
![A teammate answers with their own agent: it reads the question and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-dark.svg)

1. In the unreleased App-run candidate, **Draft with my agent** offers **Here in the App** or **In my terminal**. The terminal option keeps `/ql answer <ask>` (`$ql answer <ask>` in Codex).
2. The agent drafts. The App shows it as "not sent yet", with **Send the draft**, **Edit it** and **Discard the draft**. For App runs, only your click on **Send the draft** publishes the draft you reviewed. If it changed, read the new draft before sending.
3. The answer reaches you marked with its agent, such as "Dana via Claude Code", and your agent picks it up.

![A teammate's questions in the team space: each with Looks right, Suggest a change, Reply in your words, Draft with my agent and Hand to someone else; one agent draft waits, not sent yet, with Send the draft and Edit it](pathname:///img/app/team-light.webp)
![A teammate's questions in the team space: each with Looks right, Suggest a change, Reply in your words, Draft with my agent and Hand to someone else; one agent draft waits, not sent yet, with Send the draft and Edit it](pathname:///img/app/team-dark.webp)

*Example team in a fictional project.*

App drafting is an unreleased local candidate. It always uses **your agent's own settings**; Fewer prompts and Bypass are unavailable. Choose your local project checkout or **Only the shared documents** under **Works in**. A project choice lets the agent read the code you have locally; shared documents alone provide no repository checkout.

Only the person addressed by the question can start or resume its App run. The question must still be open. A teammate cannot start, type into or steer your agent. If a question is answered, handed over or withdrawn, its run stops at the next confirmed turn boundary. Its words and shared documents provide evidence for the answer, never permission to execute their instructions.

The `qualitylayer ask` commands are in the [command reference](../reference/commands.md).
