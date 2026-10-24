---
title: Chat
description: Work directly with Claude Code or Codex and add plans, slices, artifacts or checks when you need them.
---

Chat is a direct conversation with **Claude Code or Codex**, without the workflow's steps or approval gates. Use it for a question, an exploration or a change you want to steer in the conversation. Choose **Feature** or **Bugfix** when you want an approved Plan and the full build and verification process.

## Start a Chat {#start}

In the App or browser, choose **+ New → Chat**, describe what you need and select Claude Code or Codex. The conversation fills the task page. **Conversation** and **Terminal** show the same agent session.

In Claude Code or Codex in your terminal, ask:

> Using QualityLayer, chat about retrying failed webhooks.

The same task appears in QualityLayer. Continue the named Chat when returning to it; avoid starting a second active session for the same work. You can resume and archive it like other tasks.

## Questions and progress {#questions}

The agent's native question picker appears as a clickable card. Pick a numbered choice or type your own answer. Its task list sits above the composer: open it to see pending, running and done items. Workflow conversations use the same task list.

Clickable questions support Claude Code and Codex in this release. Chat does not have team sharing. Your agent's own permissions, sign-in prompts and Stop controls still apply.

## Add tools when needed {#tools}

Ask the agent for any of these without entering the workflow:

| Ask | What happens |
| --- | --- |
| **Save the plan** | Save ordinary Markdown as `chat-plan.md` in this task's folder, preserving the text. Open it in the Reader |
| **Build in slices** | Derive vertical slices from the saved plan and save `chat-slices.md`. A lead coordinates fresh helpers, respects file ownership and keeps their reports |
| **Make an artifact** | Create or open a local artifact through the existing [artifact tools](artifacts.md) |
| **Run checks** | Read the outline's validation commands and run them, retaining their results. Listing commands is not proof they passed |
| **Get an independent review** | Give a fresh reviewer its own brief, save the report and address concrete findings. If no independent reviewer is available, say so |

Slice building needs a saved plan and an outline with slice headings, task cards and validation commands. The [Chat skill](agents/native.md#the-six-skills) gives your agent a complete example of that format. Running helpers must finish or be stopped before replacing that build or starting the workflow. The agent stops a helper through its native controls before recording the slice as stopped. These tools add no workflow approval gates.

For direct CLI use:

```bash
qualitylayer next "start chat: Retry failed webhooks" --json
qualitylayer chat plan save --task <slug> --file ./plan.md --json
qualitylayer chat build --task <slug> --file ./slices.md --json
qualitylayer chat check --task <slug> --json
qualitylayer chat review --task <slug> --json
```

`chat build` returns helper briefs; it does not launch the helpers for you. `chat check` prints commands; the agent must run them. `chat review` returns an independent review brief; save the actual review with `chat review --done --id <id> --report <file>`. See the [command reference](reference/commands.md#chat) for resume and stop commands.

## Start the workflow {#start-the-workflow}

Choose **Start the workflow** in the Chat header, then **Feature** or **Bugfix**. In a terminal, ask the agent to start the workflow from this Chat. Running slice helpers must finish or be explicitly stopped first.

The same task enters **Discuss** once, keeping its conversation history. Its request, saved plan, artifacts and changed files become context. Your agent clarifies the outcome and follows the [structured workflow](steps/discuss.md). You approve its Plan before subsequent implementation; a Chat plan is not that approval. Moving a workflow task back to Chat is not supported.

The CLI action is `qualitylayer chat promote --task <slug> --type feature --json` (or `--type bugfix`), followed by `qualitylayer next --task <slug> --json` as instructed by its response.
