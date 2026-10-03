---
title: Settings
description: Four models, auto-advance, the optional steps, your role, notifications, your licence and your team.
---

![Settings: one subagent model per agent, one second-opinion model per reviewing agent, a switch for each optional step, and notifications](pathname:///img/diagrams/settings-light.svg)
![Settings: one subagent model per agent, one second-opinion model per reviewing agent, a switch for each optional step, and notifications](pathname:///img/diagrams/settings-dark.svg)

Open **Settings** at the bottom of the Cockpit's sidebar. Changes save at once and apply to every project on this computer. With auto-advance on, the frame and the research go on without a review; the design, the outline and the final approval always wait for you.

## Your role

**I mostly work as** is **Developer** or **Product manager**. It decides which route your agent offers first for a new feature. A developer gets the Feature route, with a frame and a design. A product manager gets the product route, with a PRD and a TDD. The build and its result are the same. You are asked once, in the Cockpit or in your agent's chat, and every task still lets you pick another route.

## Models

Every helper agent and every second opinion thinks at high effort, so there is no effort setting. You set the build session's own model at handoff.

### Subagents

Helper agents start fresh, with no memory of your chat, and work only from the task's documents. That keeps their work independent. They research, read the outline like a new builder, build slices, run the end-to-end checks, run the quality pass and judge the finished change.

One model covers all of them, per coding agent. In Claude Code you pick **Sonnet 5.5** (the default) or **Opus 5.5**. In Codex you pick **GPT-6.1 Sol** (the default), **GPT-6 Astra**, the most capable and the most expensive, or **GPT-6 Luna**, the fastest and cheapest. **This session** means no helpers: your agent does every step itself.

### Second opinion

With Claude Code and Codex both installed, the other vendor's agent reviews your agent's work:

- **Design:** the frame, the research and the design, as soon as the design is up for your review. **Approve** unlocks once your agent has answered the findings.
- **Verify:** every plan document, the build record and the code change.

It runs through the other agent's command-line tool (`claude` or `codex`), so install it even if you work in a desktop app. It reads only the documents, never your chat, and changes nothing. Your agent fixes what it agrees with and says why it skips the rest. Each direction (**Codex reviews Claude Code**, **Claude Code reviews Codex**) has one model from the same lists. A review that has not finished after ten minutes at design, or twelve at verify, is stopped and Approve unlocks anyway. Whether the second opinion runs at all is its switch under Optional steps.

## Auto-advance

Two switches, both on by default:

- **Frame → Research:** once you have answered your agent's questions in the chat, the frame is approved and the research starts.
- **Research → Design:** the research goes on to the design without a review.

The documents stay in the Cockpit to read, and your comments still reach the agent. The design is your first full review. A teammate's required answer or a second opinion still holds a gate. Switch one off to review that stage before your agent goes on.

## Optional steps

Each of these steps has a switch, on by default. A switch sets the default for every new task. When a task starts, your agent's question can switch steps off for that task, and the [handoff](../workflow/build/handoff.md) changes the build-time steps for one build. After the build starts, the list is fixed.

| Group | Step | What it does |
| --- | --- | --- |
| While planning | Outline cold read | A fresh helper reads the outline like a new builder and reports where it would get stuck |
| While planning | Second opinion | The other vendor's agent reviews the design and the finished change |
| While building | Checkpoints | Runs the end-to-end scenarios after marked slices |
| Quality pass | Simplify | Reads the whole change once and makes it simpler |
| Quality pass | Test gaps | Adds the missing edge-case and error-path tests |
| Quality pass | Security review | Looks for severe issues in the change, in at most 10 minutes |
| Quality pass | Docs update | Brings the README, the docs and the changelog in line with the change |
| Quality pass | UI review | For tasks with a screen: compares the running app with the design's mockups |

The [quality pass](../workflow/check/verify.md#the-quality-pass) runs at the start of Verify, before the judge. No step switch turns an approval off.

## Notifications

Your browser tells you when a document or the final change waits for you, when the build or verification stops, and when a task ships, while the Cockpit is open.

## Licence and team

**Licence** shows your plan, your version and a link to the customer portal for invoices, seats and payment. On another computer, run `qualitylayer licence activate <key>`. **Team** shows your seats, your members and their computers, your shared links, and the name your team sees on your comments.
