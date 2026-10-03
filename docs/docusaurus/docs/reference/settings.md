---
title: Settings
description: The five workflow settings, changes for one task, links, notifications, your licence and your team.
---

![Settings, Workflow: helper model, judge model, second opinion, always run checkpoints and token budget; and the overrides for one task, said in words](pathname:///img/diagrams/settings-light.svg)
![Settings, Workflow: helper model, judge model, second opinion, always run checkpoints and token budget; and the overrides for one task, said in words](pathname:///img/diagrams/settings-dark.svg)

Open **Settings** at the bottom of the App's sidebar. Changes save at once and apply to every project on this computer. They live in QualityLayer's config file; the keys are named below.

## Workflow

| Setting | Default | Key |
| --- | --- | --- |
| [Helper model](#helper-model) | Sonnet 5.5 · GPT-6.1 Sol in Codex | `models.<agent>.helpers` |
| [Judge model](#judge-model) | Opus 5.5 · GPT-6.1 Sol in Codex | `models.<agent>.judge` |
| [Second opinion](#second-opinion) | Off | `secondOpinion.on`, `secondOpinion.models` |
| [Always run checkpoints](#always-run-checkpoints) | Off | `alwaysCheckpoints` |
| [Token budget](#token-budget) | None | `budget.tokens` |

Your own session's model is yours to pick in your agent. Opus 5.5 is recommended for Discuss and Plan, and Sonnet 5.5 for the session that runs Implement.

### Helper model {#helper-model}

Helper agents start fresh, with no memory of your chat, and work from the Plan. They research, build slices, fix what a check found, run checkpoints, and do Polish and Security. One model covers all of them, per coding agent.

In Claude Code you pick **Sonnet 5.5** (the default) or **Opus 5.5**. In Codex you pick **GPT-6.1 Sol** (the default), **GPT-6 Astra**, the most capable and the most expensive, or **GPT-6 Luna**, the fastest and cheapest. **This session** means no helpers: your agent does every step itself.

### Judge model {#judge-model}

The model of the AI that checks the finished change in [Verify](../steps/verify.md). It never wrote the code. The default is **Opus 5.5** in Claude Code and **GPT-6.1 Sol** in Codex.

### Second opinion {#second-opinion}

Off by default. With Claude Code and Codex both installed, the other vendor's AI reviews your agent's work. It reads the Plan while it is up for your review, and the built change in Verify. **Approve** unlocks once your agent has answered its findings.

It runs through the other agent's command line (`claude` or `codex`), so install it even if you work in a desktop app. It reads only the documents, never your chat, and changes nothing. Your agent fixes what it agrees with and says why it skips the rest. Each direction (**Codex reviews Claude Code**, **Claude Code reviews Codex**) has its own model.

### Always run checkpoints {#always-run-checkpoints}

Off by default: only a slice the Plan marks risky gets a [checkpoint](../steps/implement.md#checkpoints). On, every slice with its own scenario gets one.

### Token budget {#token-budget}

A soft limit per task, in tokens. When a task passes it, the App shows a notice and your agent tells you once; the task goes on. See [What it costs](../app.md#what-it-costs).

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

## Links and notifications

**Links** opens your agent's links in the App, or always in your browser. **Notifications** turns the App's notifications on; your system asks once.

## Licence and team

**Licence** shows your plan, your version and a link to the customer portal for invoices, seats and payment. On another computer, run `qualitylayer licence activate <key>`. **Team** shows your seats, your members and their computers, your shared links, your Slack connection and groups, and the name your team sees on your comments.
