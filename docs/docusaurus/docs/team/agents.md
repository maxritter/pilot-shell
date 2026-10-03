---
title: Teammates' agents
description: A teammate you ask can answer with their own Claude Code, Codex or Grok Bot. The agent drafts; nothing is sent without their yes.
---

When you ask a teammate about your Plan, they can hand the question to their own agent. The agent reads the question and the Plan, looks at their code, asks them what it needs, and drafts the answer. Nothing is sent without their yes.

![A teammate answers with their own agent: Claude Code, Codex or Grok Bot reads the ask and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-light.svg)
![A teammate answers with their own agent: Claude Code, Codex or Grok Bot reads the ask and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent](pathname:///img/diagrams/team-agents-dark.svg)

## Start their agent on a question

In their App, every question for them offers **Work on it with your agent**:

- **Claude Code** copies `/ql answer <ask>` to paste into a session.
- **Codex** copies `$ql answer <ask>`.
- **Grok Bot** sends the question to their bot.

The Slack message for a question carries the same command. While their agent works, the question shows which agent is on it, since when, and in which folder.

## What their agent does

1. Reads the question, the passage it is about and the task's documents.
2. Looks at the teammate's own repository where that helps.
3. Asks the teammate what it needs, one question at a time.
4. Writes a draft, then asks: **Send this as your answer?**

The teammate chooses **Send**, **Edit**, or **I'll send it myself**. A draft they keep shows in their App with **Send**, **Edit** and **Discard**.

## What you see

The answer arrives like any other, marked with its agent: "Dana via Claude Code", "via Codex" or "via Grok Bot". Your agent picks it up as usual and you decide, as with every answer.

## Grok Bot

Grok Bot works through the teammate's own computer. In their App's setup page, **Add the ql skill** puts the QualityLayer skill into their Grok Bot library. It needs the `gbot` command line; when it is missing, the App shows the install command to copy:

```bash
npm install -g grok-bot-cli
```

The bot runs every command on their computer through Grok Bot's computer access, asks them in the Grok chat, and sends nothing until they say "send it". QualityLayer is never installed on Grok Bot's own cloud computer, so team keys stay on theirs.

## From the command line

Their agent uses these commands, and a teammate can run them too:

| Command | What it does |
| --- | --- |
| `qualitylayer ask list` | Questions to them and from them, on every shared task |
| `qualitylayer ask show <ask>` | The question, the passage it is about, and the task's documents |
| `qualitylayer ask answer <ask> --kind ok\|change\|reply` | Send an answer |
| `qualitylayer ask draft <ask>` | Keep a draft for the App; sends nothing |
| `qualitylayer ask hand <ask> --to <member>` | Hand the question on to someone else |
| `qualitylayer ask grok <ask>` | Send the question to their Grok Bot |
| `qualitylayer grok setup` | Add the ql skill to their Grok Bot |

`<ask>` is the question's ID or the start of it, such as `7f3a`.
