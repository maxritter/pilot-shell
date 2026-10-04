---
title: Settings
description: The workflow settings, changes for one task, notifications, your licence and your team.
---

![Settings, Workflow: the Subagents and Second opinion cards and Notifications; and the overrides for one task, said in words](pathname:///img/diagrams/settings-light.svg)
![Settings, Workflow: the Subagents and Second opinion cards and Notifications; and the overrides for one task, said in words](pathname:///img/diagrams/settings-dark.svg)

Open **Settings** at the bottom of the App's sidebar. Changes save at once and apply to every project on this computer. They live in QualityLayer's config file; the keys are named below.

## Workflow

**Settings › Workflow** has two cards, **Subagents** and **Second opinion**, and a **Notifications** switch below them.

| Card | Setting | Default | Key |
| --- | --- | --- | --- |
| Subagents | [Workers](#subagents) | Sonnet 5.5 · GPT-6.1 Sol in Codex | `models.<agent>.helpers` |
| Subagents | [Judge](#judge) | Opus 5.5 · GPT-6.1 Sol in Codex | `models.<agent>.judge` |
| Second opinion | [The reviewer models](#second-opinion) | Sonnet 5.5 · GPT-6.1 Sol in Codex | `secondOpinion.models` |

Your own session's model is yours to pick in your agent. Opus 5.5 is recommended for Discuss and Plan, and Sonnet 5.5 for the session that runs Implement.

### Subagents {#subagents}

Subagents are fresh agents your agent starts for parts of the work. They start with no memory of your chat and see only their brief, which comes from the Plan. **Workers** research, build slices, fix what a check found, run checkpoints, and do Polish and Security. One model covers all of them, per coding agent.

In Claude Code you pick **Sonnet 5.5** (the default), **Opus 5.5** or **Fable 5.1**. In Codex you pick **GPT-6.1 Sol** (the default), **GPT-6 Astra**, the most capable and the most expensive, or **GPT-6 Luna**, the fastest and cheapest. **No subagents** means your agent does every step itself: cheaper, with less independent checking.

### Judge {#judge}

The judge decides pass or fail on the finished change in [Verify](../steps/verify.md). It never wrote the code, so it gets the stronger model: **Opus 5.5** by default in Claude Code, which also offers Sonnet 5.5 and Fable 5.1, and **GPT-6.1 Sol** in Codex.

### Second opinion {#second-opinion}

With Claude Code and Codex both installed, the other vendor's AI reviews your agent's work by itself when the Plan crosses a trust boundary or marks a slice risky. It reads the Plan while it is up for your review, and the built change in Verify. **Approve** unlocks once your agent has answered its findings. Say "get a second opinion" or "no second opinion" to change it for one task.

It runs through the other agent's command line (`claude` or `codex`) on that agent's own plan, so install it even if you work in a desktop app. It reads only the documents and the change, never your chat, and changes nothing. Your agent fixes what it agrees with and says why it skips the rest. The two settings are the model each direction uses: **Codex reviews Claude Code's work** and **Claude Code reviews Codex's work**. In Claude Code you pick Sonnet 5.5, Opus 5.5 or Fable 5.1.

## For one task {#for-one-task}

Say it in words, such as "skip security" or "run a checkpoint after every slice". Your agent records it on the task with `qualitylayer task override`:

| Override | What it does |
| --- | --- |
| `+security` · `-security` | Run the security review, or skip it |
| `+checkpoint:all` | A checkpoint after every slice with its own scenario |
| `-checkpoint` | No checkpoints, not even for risky slices |
| `+second-opinion` · `-second-opinion` | Turn the second opinion on or off for this task |
| `-ui-review` | Skip comparing the screens with the mockup in Polish |

No setting or override turns an approval off.

## Notifications

**Notifications** tells you when a review waits for you, or a task ships or stops; they also collect under the bell. In the App's window, the system shows them: if none arrive, allow QualityLayer in your system's notification settings. In a browser, the page offers **Allow them in this browser** until you answer.

## Licence and team

**Licence** shows your plan, your version and a link to the customer portal for invoices, seats and payment. On another computer, run `qualitylayer licence activate <key>`. **Team** shows your seats, your members and their computers, your shared links, your Slack connection and groups, and the name your team sees on your comments.
