---
slug: "async-workflows"
title: "Claude Code Async: Background Agents & Parallel Tasks"
description: "Run Claude Code sub-agents in the background while you keep working. True parallel AI development that eliminates blocking and boosts throughput."
date: "2025-12-11"
author: "Max Ritter"
tags: [Guide, Agents]
readingTime: 4
keywords: "agents, async, background, claude, code, parallel, tasks, workflows"
---

Agents

# Claude Code Async: Background Agents & Parallel Tasks

Run Claude Code sub-agents in the background while you keep working. True parallel AI development that eliminates blocking and boosts throughput.

**Problem**: When Claude Code spawns a sub-agent for research or complex analysis, your entire session blocks. You wait while the sub-agent works, unable to continue the conversation.

**Quick Win**: When Claude spawns a sub-agent, press `Ctrl+B` to move it to the background:

```p-4
You: Research authentication best practices for our Next.js app
Claude: I'll spawn a sub-agent to research this...
[Sub-agent starts]
You: [Press Ctrl+B]
You: While that runs, let's work on the database schema...
```

Your session continues. The sub-agent works independently and surfaces results when done.

## [Background Agents: True Parallel Execution](#background-agents-true-parallel-execution)

Claude Code now supports asynchronous agent execution. When the main agent spawns sub-agents, you can background them and keep working with Claude on other tasks.

**The workflow:**

1. **Request**: Ask Claude to handle a task that benefits from a sub-agent
2. **Claude spawns**: The main agent creates a sub-agent for the work
3. **Background it**: Press `Ctrl+B` while the sub-agent runs
4. **Continue working**: Keep chatting with the main agent on other tasks
5. **Auto-resume**: When the sub-agent completes, it wakes up the main agent with results

Check running agents anytime with `/tasks`:

```p-4
/tasks
```

You'll see each background agent's status, token usage, and progress. Click any agent to inspect details.

## [When Background Agents Excel](#when-background-agents-excel)

**Perfect for background execution:**

- Research tasks requiring web searches
- Code analysis across large codebases
- Documentation generation
- Security audits and vulnerability scans
- Performance profiling reports

**Keep in foreground:**

- Tasks requiring your immediate input
- File modifications you need to review
- Anything with sequential dependencies on your current work

## [Background Bash Commands](#background-bash-commands)

The same pattern works for long-running shell commands. When Claude runs `npm install`, `docker build`, or `ffmpeg` and it takes a while, background it:

```p-4
Claude: Running npm install...
[Command starts]
You: [Press Ctrl+B]
You: While that installs, can you review the API routes?
```

Monitor with `/tasks`, same as agents.

## [The `--agent` Flag: Debug Your Sub-Agents](#the---agent-flag-debug-your-sub-agents)

New CLI flag lets you run Claude Code AS any sub-agent:

```p-4
claude --agent plan
```

This launches Claude Code with the planning agent's configuration. Ask it questions, test its behavior, verify it works as expected before deploying in workflows.

**Use cases:**

- Debug custom sub-agents before production use
- Test agent instructions and tool access
- Run specialized agents manually for one-off tasks
- Understand built-in agent capabilities

Works with built-in agents (`plan`, `explore`, etc.) and your custom agents in `.claude/agents/`.

## [Also in This Release](#also-in-this-release)

Anthropic shipped several other features alongside background agents:

**Instant compaction**: The `/compact` command now executes immediately. Claude maintains a continuous session memory, so compaction just loads the summary into a fresh context. Learn more in our [context management guide](/blog/guide/mechanics/context-management).

**Session memory architecture**: Every session now maintains a structured summary including status, completed work, discussion points, and a work log. See [memory optimization](/blog/guide/mechanics/memory-optimization) for details.

**Stats dashboard**: Run `/stats` to see your usage patterns, favorite models, token counts, and streaks. Press `Ctrl+S` to copy for sharing.

**Session naming**: Use `/rename` to name sessions, then resume by name with `claude --resume session-name`. The `/resume` screen now groups forked sessions and adds keyboard shortcuts (`P` preview, `R` rename, `B` browse forks).

**MCP quick toggle**: Enable or disable MCP servers without editing config files. See our [MCP basics guide](/blog/tools/mcp-extensions/mcp-basics) for the commands.

**Slack integration**: Delegate tasks to Claude Code directly from Slack channels. Tag @Claude with bug reports or feature requests for team workflows.

## [Common Issues](#common-issues)

**Agent doesn't background**: Press `Ctrl+B` while the agent is actively running, not after it completes.

**Lost track of agents**: Use `/tasks` to see all running background processes with their IDs.

**Agent completed but no results**: The `AgentOutputTool` automatically surfaces results. If missed, check `/tasks` for the completed agent's output.

## [Next Steps](#next-steps)

- **Execution patterns**: Master [parallel, sequential, and background patterns](/blog/guide/agents/sub-agent-best-practices) to choose the right approach
- **Foundation**: Understand [agent fundamentals](/blog/guide/agents/agent-fundamentals) before building complex workflows
- **Design patterns**: Learn [sub-agent design](/blog/guide/agents/sub-agent-design) for effective task delegation
- **Distribution**: Master [task distribution](/blog/guide/agents/task-distribution) for multi-agent orchestration
- **Custom agents**: Build specialized agents with [custom agent patterns](/blog/guide/agents/custom-agents)

Background agents transform Claude Code from a turn-based assistant into a parallel development environment. Launch research, continue building, get results when ready.

Last updated on

[Previous

Agent Fundamentals](/blog/guide/agents/agent-fundamentals)[Next

Sub-Agent Patterns](/blog/guide/agents/sub-agent-best-practices)
