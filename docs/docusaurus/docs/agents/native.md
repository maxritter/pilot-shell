---
title: Supported agents
sidebar_label: Supported agents
description: Set up the four native coding agents, choose their models and reviewers, and control their sessions in the App.
---

# Supported agents {#claude-code-codex-pi-and-opencode}

QualityLayer connects **Claude Code**, **Codex**, **Pi** and **OpenCode** to the same workflow. Install your agent, sign in through its own login and start it once, then run QualityLayer setup. The App and CLI installers add the integration for each agent they find.

In the App or browser, choose **+ New**, pick your agent and describe the change. The task stays on the left and its agent conversation opens in the right sidebar.

In your own terminal, VS Code or another IDE, say “Using QualityLayer, plan a CSV export”. The same wording works with **QL** and requests to implement, verify or continue an existing task.

| Agent | What QualityLayer adds |
| --- | --- |
| [Claude Code](https://code.claude.com/docs/en/setup) | Skills, lifecycle hooks and its existing prompt integration |
| [Codex](https://developers.openai.com/codex/cli) | Skills, implicit invocation policies and lifecycle hooks |
| [Pi](https://pi.dev/) 1.2.0 or later | Skills, a lifecycle extension and fresh helper sessions |
| [OpenCode](https://opencode.ai/docs/) 2.0.29 or later | Skills, a command and lifecycle plugin |

An ordinary coding request stays an ordinary request. Ask QualityLayer or QL to carry the work; merely discussing the product or quoting an example does not start a workflow. Natural wording, clear spelling variants and requests in other languages are supported.

The installed skills are `ql-workflow`, `ql-artifact`, `ql-peer`, `ql-manage` and `ql-quality`. Your agent loads the one the request needs. A standalone artifact, peer message or settings operation does not create a workflow task. The artifact skill points to the CLI's artifact guide, which is read once per assignment.

The `ql-quality` skill helps your agent inspect local Qlty findings. Automatic feedback checks edited files for structural issues; deliberate CLI checks cover broader duplication and function metrics. See [Code health](../reference/code-health.md) for availability, review decisions and project controls.

## Models and reviews

Choose the agent, model and effort when starting a task or build. Settings › Workflow keeps the review models and general run controls. Pi and OpenCode use provider-qualified model IDs, such as `openai-codex/gpt-6.1-sol` in Pi and `openai/gpt-6.1-sol` in OpenCode. Workflow defaults use High effort; your native login and provider settings stay in your agent.

**Second opinion by** selects an installed reviewer. **Automatic** chooses another installed agent when available; you can choose a particular one for a fresh review. The reviewer inspects files in a separate context and does not edit them.

Pi and OpenCode can use the same model provider as your working agent. Choose a different model or provider when you want a second model family, as well as a fresh context.

## Sessions in the App or browser

With **In QualityLayer**, choose the agent, model, effort, project and branch when you start a task or build. The task’s **Agent** tab holds its conversation in QualityLayer. Closing the sidebar keeps the run; **Stop** ends it. If the local runtime cannot start a session, use **In my terminal, app or IDE**.

To continue after a crash or in another agent, stop the previous run if it is still active, then name the same task and intended stage: “Using QL, continue verification of task retry-webhooks.” Keep the task's recorded approvals, changes and evidence; the CLI resolves ownership before work resumes.

The App records the native conversation, accepts one typing controller and offers Interrupt, Stop, Resume, Move and settings changes at a completed turn. Resume requires saved native state and verified process cleanup. If the conversation is still open in another terminal, the App refuses to resume it there.

| Agent | Permission choices |
| --- | --- |
| Claude Code | Own settings, Fewer prompts or a confirmed bypass |
| Codex | Own settings, Fewer prompts or a confirmed bypass |
| Pi | Its own tool permissions |
| OpenCode | Own settings or Fewer prompts; explicit deny rules remain in force |

The App uses a private OpenCode server for each managed run, with its build agent for workflow work and its plan agent for read-only reviews. A session in your terminal keeps your native agent choice. Stopping a managed run leaves other OpenCode sessions alone. Available permission controls depend on the installed client and its supported options.

## Peer sessions

All four agents use `qualitylayer peers` for messages, correlated requests, buddy selection, task status and checkout claims. Pi and OpenCode register through their installed integrations. Use the `pi:<uuid>` or `opencode:<uuid>` address printed by `qualitylayer peers list`; OpenCode's peer UUID maps to its native session ID.

A queued message confirms transport. The recipient acknowledges it with `qualitylayer peers ack --message-id <uuid>`, and a correlated request gets its own explicit reply. Native peer reply chains stop after three consecutive outgoing messages until the person's next prompt or thirty quiet minutes. Review workers stay outside the peer registry.

## Setup and removal

Settings › Workflow › Agents shows a compact row for all four agents. Open an agent's help for its last executable/version result and installation link; **Check again** runs a fresh check. A responding version does not prove account access, which is checked when a session starts. The same results are available through `qualitylayer agents list` and `qualitylayer agents check`.

Both QualityLayer installers add skills and lifecycle files to the initialized agents they discover. Pi uses `~/.pi/agent`; OpenCode uses `~/.config/opencode`. Their configured root overrides are respected. QualityLayer does not replace their authentication or personal model settings.

An update replaces unchanged integration files it owns and retires its legacy skill names. Edited legacy files are backed up outside skill discovery, so they do not activate alongside the new names. Unrelated custom skills stay. Uninstall preserves your native settings, login and session history, along with files you edited.

Other coding agents can still [follow the same workflow](other.md) through the CLI.
