---
title: Settings
description: The model for each helper job, the second opinion, notifications, your licence and your team.
---

![Settings: a model for each helper job in Claude Code and Codex, the second opinion, and notifications](pathname:///img/diagrams/settings-light.svg)
![Settings: a model for each helper job in Claude Code and Codex, the second opinion, and notifications](pathname:///img/diagrams/settings-dark.svg)

Open **Settings** at the bottom of the Cockpit's sidebar. Changes save at once and apply to every project on this computer. No setting skips a review: every plan document waits for your approval, and the final approval is always yours.

## Subagents

Helper agents start fresh, with no memory of your chat, and work only from the task's documents. That keeps their work independent.

| Job | What it does |
| --- | --- |
| Research | Answers the research questions without seeing your goal |
| Outline cold read | Reads the plan like a new builder and reports where it would get stuck |
| Slice builds | Builds one slice each, in plans with three or more slices |
| Build checkpoints | Runs the end-to-end scenarios after a slice |
| Simplify | Makes the finished change simpler, with the same behaviour |
| Verify judge | Checks the finished change against your request, with evidence |

Each job has a model for the agent you work in. In Claude Code you pick **Sonnet 5.5** (the default) or **Opus 5.5**. In Codex you pick **GPT-6.1 Sol** (the default), **GPT-6 Astra**, the most capable and the most expensive, or **GPT-6 Luna**, the fastest and cheapest. **Off** means your agent does the job itself. Every helper thinks at high effort, so there is no effort setting. You set the build session's own model at handoff.

## Second opinion

With Claude Code and Codex both installed, the other vendor's agent reviews your agent's work:

- **Design:** the frame, the research and the design, as soon as the design is up for your review. **Approve** unlocks once your agent has answered the findings.
- **Verify:** every plan document, the build record and the code change.

It runs through the other agent's command-line tool (`claude` or `codex`), so install it even if you work in a desktop app. It reads only the documents, never your chat, and changes nothing. Your agent fixes what it agrees with and says why it skips the rest. Each point and direction (**Codex reviews Claude Code**, **Claude Code reviews Codex**) has its own model from the same lists, on by default, or **Off**. A review that has not finished after ten minutes at design, or twelve at verify, is stopped and Approve unlocks anyway.

## Notifications

Your browser tells you when a document or the final change waits for you, when the build or verification stops, and when a task ships, while the Cockpit is open.

## Licence and team

**Licence** shows your plan, your version and a link to the customer portal for invoices, seats and payment. On another computer, run `qualitylayer licence activate <key>`. **Team** shows your seats, members and shared links, and the name your team sees on your comments.
