---
title: Supported agents
sidebar_label: Supported agents
description: Set up the four native coding agents, choose their models and reviewers, and control their sessions in the App.
---

# Supported agents {#claude-code-codex-pi-and-opencode}

QualityLayer connects **Claude Code**, **Codex**, **Pi** and **OpenCode** to the same workflow. Install your agent, sign in through its own login and start it once, then run QualityLayer setup. The App and CLI installers add the integration for each agent they find.

| Agent | Start a task | What QualityLayer adds |
| --- | --- | --- |
| [Claude Code](https://docs.claude.com/en/docs/claude-code/setup) | `/ql your request` | Skill, lifecycle hooks and its existing prompt integration |
| [Codex](https://developers.openai.com/codex/cli) | `$ql your request` | Skill, invocation policy and lifecycle hooks |
| [Pi](https://pi.dev/) 1.2.0 or later | `/skill:ql your request` | Skill, lifecycle extension and fresh helper sessions |
| [OpenCode](https://opencode.ai/docs/) 2.0.29 or later | `/ql your request` | Skill, command and lifecycle plugin |

An ordinary coding request stays an ordinary request. QualityLayer starts when you invoke its workflow or explicitly ask it to handle a task by name.

## Models and reviews

Choose the agent, model and effort when starting a task or build. Settings › Workflow keeps the review models and general run controls. Pi and OpenCode use provider-qualified model IDs, such as `openai-codex/gpt-6.1-sol` in Pi and `openai/gpt-6.1-sol` in OpenCode. Workflow defaults use High effort; your native login and provider settings stay in your agent.

**Second opinion by** selects an installed reviewer. **Automatic** chooses another installed agent when available; you can choose a particular one for a fresh review. The reviewer inspects files in a separate context and does not edit them.

Pi and OpenCode can use the same model provider as your working agent. Choose a different model or provider when you want a second model family, as well as a fresh context.

## Sessions in the App

Choose the agent, model, effort and workspace when you start a task or build. The task’s **Agent** tab holds its conversation in the App. Closing the sidebar keeps the run; **Stop** ends it. If the local runtime cannot start an App session, use **In my terminal**.

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

Both QualityLayer installers add skills and lifecycle files to the initialized agents they discover. Pi uses `~/.pi/agent`; OpenCode uses `~/.config/opencode`. Their configured root overrides are respected. QualityLayer does not replace their authentication or personal model settings.

An update replaces unchanged integration files it owns. Uninstall removes those files and preserves your native settings, login and session history. Files you edited are kept.

Other coding agents can still [follow the same workflow](other.md) through the CLI.
