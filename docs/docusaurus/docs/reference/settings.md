---
title: Settings
description: The four Settings tabs, Workflow, Licence, Team and About, the changes you can ask for on one task, and notifications.
---

![Settings, Workflow: the Subagents grid, the Second opinion pickers and Notifications, beside the tabs Licence, Team and About; and the overrides for one task, said in words](pathname:///img/diagrams/settings-light.svg)
![Settings, Workflow: the Subagents grid, the Second opinion pickers and Notifications, beside the tabs Licence, Team and About; and the overrides for one task, said in words](pathname:///img/diagrams/settings-dark.svg)

Open **Settings** with the gear in the App's sidebar foot. It has four tabs: **Workflow**, **Licence**, **Team** and **About**. Changes save at once and apply to every project on this computer. They live in QualityLayer's config file; the keys are named below.

## Workflow

**Settings › Workflow** has a **Subagents** grid, a **Second opinion** card and a **Notifications** switch.

| Card | Setting | Default | Key |
| --- | --- | --- | --- |
| Subagents | [Workers](#subagents) | Sonnet 5.5 · GPT-6.1 Sol in Codex | `models.<agent>.helpers` |
| Subagents | [Checking](#checking) | Opus 5.5 · GPT-6.1 Sol in Codex | `models.<agent>.judge` |
| Second opinion | [The reviewer models](#second-opinion) | Sonnet 5.5 · GPT-6.1 Sol in Codex | `secondOpinion.models` |

Your own session's model is yours to pick in your agent. Opus 5.5 is recommended for Discuss and Plan, and Sonnet 5.5 for the session that runs Implement.

### Subagents {#subagents}

Subagents are fresh agents your agent starts for parts of the work. They start with no memory of your chat and see only their brief, which comes from the Plan. The grid has a row per role and a column per coding agent, In Claude Code and In Codex. **Workers** research, build slices, fix what a check found, run checkpoints, and do Polish and the security review.

In Claude Code you pick **Sonnet 5.5** (the default), **Opus 5.5** or **Fable 5.1**. In Codex you pick **GPT-6.1 Sol** (the default), **GPT-6 Astra**, the most capable and the most expensive, or **GPT-6 Luna**, the fastest and cheapest. Pick **No subagents** for Workers to have your agent do every step itself: cheaper, with less independent checking.

### Checking {#checking}

The Checking row sets the model of the agents that check the finished change in [Verify](../steps/verify.md). They never wrote the code, so they get the stronger model: **Opus 5.5** by default in Claude Code, which also offers Sonnet 5.5 and Fable 5.1, and **GPT-6.1 Sol** in Codex.

### Second opinion {#second-opinion}

With Claude Code and Codex both installed, the other vendor's AI reviews your agent's work by itself when the Plan crosses a trust boundary or marks a slice risky. It reads the Plan while it is up for your review, and the built change in Verify. Each finding becomes an item for you to answer. **Approve** unlocks once your agent has answered its findings. Say "get a second opinion" or "no second opinion" to change it for one task, or choose **Add a review** on the Plan's Extra review item.

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

**Notifications** is one switch: "When something needs you, or a task ships or stops". It controls the App's system notifications: a Plan or review that waits, a task that stops or ships, a teammate's question, a reminder and an answer to your question. Never agent progress. In the App's window, the system shows them: if none arrive, allow QualityLayer in your system's notification settings. In a browser, the page offers **Allow them in this browser** until you answer.

## Licence

**Licence** shows your plan ("Team licence", or the days left of your trial) and a link to the customer portal for invoices, seats and the payment method. **On another computer** shows `qualitylayer licence activate <key>` with a **Copy** button. **Anonymous usage events** switches the events that go with the daily licence check; see [what they carry](files.md#privacy).

## Team

**Team** shows, from top to bottom:

- **Your name**, shown to your team on questions and shared tasks.
- **People and groups**: your seats and members with their computers, **Manage seats** (the customer portal), and the groups. The group editor has **Select all** and a **Save** that names the count.
- **Slack**, in its states: not connected, connecting, connected with who was found, failed, busy. See [Slack messages](../team/plans.md#slack). Each member has a **Slack messages to you** switch.
- **Shared links**: each link's scope and expiry, with **Copy** and **Revoke**.

## About

**About** holds the version and the update check: "12.0.0-beta.14 is ready · checked today at 09:12 · updates are checked once a day", with **Restart and update** or **Check now**. Below are what's new in that version, grouped as New, Fixed and Good to know, a fold with earlier releases, and links to the documentation and to feedback. See [Updates and release notes](../updating.md).

## In a browser tab

A browser tab shows the same tabs and one extra card, **This browser**. It has a **Remember for 30 days** switch, so links open here without pairing again, and a **Download** for the App.
