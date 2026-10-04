---
title: Teammates' agents
description: A teammate you ask can answer with their own coding agent. The agent drafts; nothing is sent without their yes.
---

When you ask a teammate about your Plan, they can hand the question to their own agent. The agent reads the question and the Plan, looks at their code, asks them what it needs, and drafts the answer. Nothing is sent without their yes.

![A teammate answers with their own agent: it reads the question and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-light.svg)
![A teammate answers with their own agent: it reads the question and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-dark.svg)

## Start their agent on a question

In their App, every question for them offers **Draft with my agent**:

- **Claude Code** copies `/ql answer <ask>` to paste into a session.
- **Codex** copies `$ql answer <ask>`.
- **Another agent** takes the prompt from **Copy › For another agent**. See [How to connect another coding agent](../agents/other.md).

The Slack message for a question carries the same command. While their agent works, the question shows which agent is on it, since when, and in which folder.

## What their agent does

1. Reads the question, the passage it is about and the task's documents.
2. Looks at the teammate's own repository where that helps.
3. Asks the teammate what it needs, one question at a time.
4. Writes a draft, then asks: **Send this as your answer?**

The teammate chooses **Send**, **Edit**, or **I'll send it myself**. A draft they keep shows in their App in blue, "not sent yet", with **Send the draft** and **Edit**.

## What you see

The answer arrives like any other, marked with its agent: "Dana via Claude Code" or "via Codex". You get a Slack message and a notification with the answer quoted. Your agent picks it up as usual and you decide, as with every answer.

## From the command line

Their agent uses these commands, and a teammate can run them too:

| Command | What it does |
| --- | --- |
| `qualitylayer ask list` | Questions to them and from them, on every shared task |
| `qualitylayer ask show <ask>` | The question, the passage it is about, and the task's documents |
| `qualitylayer ask answer <ask> --kind ok\|change\|reply` | Send an answer |
| `qualitylayer ask draft <ask>` | Keep a draft for the App; sends nothing |
| `qualitylayer ask hand <ask> --to <member>` | Hand the question on to someone else |

`<ask>` is the question's ID or the start of it, such as `7f3a`.
