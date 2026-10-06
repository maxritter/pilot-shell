---
title: Teammates' agents
description: A teammate you ask can answer with their own coding agent. The agent drafts; nothing is sent without their yes.
---

When you ask a teammate about your Plan, they can hand the question to their own agent. It reads the question and the Plan, looks at their code, asks them what it needs, and drafts the answer. Nothing is sent without their yes.

![A teammate answers with their own agent: it reads the question and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-light.svg)
![A teammate answers with their own agent: it reads the question and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-dark.svg)

1. In their App, the question offers **Draft with my agent**, which copies one command: `/ql answer <ask>` for Claude Code, `$ql answer <ask>` for Codex.
2. Their agent drafts, then asks: **Send this as your answer?**
3. The answer reaches you marked with its agent, such as "Dana via Claude Code", and your agent picks it up.

The `qualitylayer ask` commands are in the [command reference](../reference/commands.md).
