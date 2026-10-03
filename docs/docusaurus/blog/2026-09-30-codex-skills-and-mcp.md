---
title: "Codex skills and MCP: choosing the right place for a workflow"
description: "Separate reusable Codex instructions from live MCP tools, then keep task state and review decisions explicit when combining them."
slug: codex-skills-and-mcp
date: 2026-09-30
authors: [max-ritter]
tags: ["codex","guide"]
image: https://qualitylayer.dev/og.png
---

A skill and an MCP connection solve different parts of an agent workflow. Choosing the right home for each responsibility makes the setup easier to maintain.

<!-- truncate -->

OpenAI describes skills as packages of instructions and resources that give ChatGPT and Codex task-specific capabilities. They can include supporting scripts. [Build skills](https://learn.chatgpt.com/docs/build-skills).

## Start with a responsibility map

| Need | A useful place |
| --- | --- |
| Explain how to perform a repeatable task | A skill |
| Explain this repository's structure and checks | AGENTS.md |
| Reach a live service through controlled tools | An MCP integration |
| Track a particular change and its decisions | The task's state and documents |

These pieces can be combined. Keeping their boundaries visible helps you understand what must change when a tool or process changes.

For example, a support workflow might use a skill to explain the steps, MCP tools to retrieve a ticket and a task record to preserve the decisions. The skill should not pretend its description is the live ticket data.

## Keep the instructions specific

A skill needs a recognizable purpose. It should describe the starting information, the useful tool sequence and the result the user should receive.

An instruction such as “be a better engineer” leaves the session to invent the process. A workflow that asks for a reproduction, captures the observed result and returns a checked correction gives it a concrete path.

Avoid including every available tool merely because it exists. A shorter tool path can be easier to verify and more dependable.

## Make incomplete work visible

For every external operation, decide what counts as success. Sending a request, receiving data and completing the user's task are different events.

If the service is unavailable, the workflow should return the specific missing information. It should not fill in plausible data or claim that an action happened.

When tools can write, keep the requested action and its scope visible to the user. A broad workflow description does not settle every future decision.

## Give task state an owner

A conversation can describe progress, but a durable task record gives later sessions something concrete to inspect.

QualityLayer combines an agent skill with a local CLI that holds task state. The skill explains the workflow; the CLI supplies the next step and records review decisions. The [Cockpit](/docs/app) provides a view of that state.

An MCP service may be useful beside that workflow, for example to retrieve current documentation. It does not replace the task's approved documents or acceptance checks.

## Test the combination

Try one successful task and one incomplete case. Check whether the output distinguishes them, whether the state persists and whether another session can pick up the task without reconstructing the conversation.

That is a more useful integration check than counting how many tools are connected.

Related: [repository instructions](/blog/codex-agents-md-repository-guide), [session communication](/docs/reference/commands#session-messaging) and [starting a task](/docs/first-task).
