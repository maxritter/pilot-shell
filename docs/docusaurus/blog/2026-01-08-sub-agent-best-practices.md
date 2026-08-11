---
title: "Claude Code Sub-Agents: Parallel vs Sequential Patterns"
description: "Configure Claude Code to auto-choose parallel, sequential, or background execution patterns for sub-agents based on task dependencies."
slug: sub-agent-best-practices
date: 2026-01-08
authors:
  - max-ritter
tags:
  - guide
  - agents
---

Configure Claude Code to auto-choose parallel, sequential, or background execution patterns for sub-agents based on task dependencies.

<!-- truncate -->

**Problem**: Your main Claude Code session (the "central AI") spawns sub-agents constantly, but it doesn't inherently know when to run them in parallel versus sequential chains versus background. Without explicit routing rules in your CLAUDE.md, it guesses - and often guesses wrong.

**Quick Win**: Add this routing decision framework to your CLAUDE.md:

```
## Sub-Agent Routing Rules
 
**Parallel dispatch** (ALL conditions must be met):
 
- 3+ unrelated tasks or independent domains
- No shared state between tasks
- Clear file boundaries with no overlap
 
**Sequential dispatch** (ANY condition triggers):
 
- Tasks have dependencies (B needs output from A)
- Shared files or state (merge conflict risk)
- Unclear scope (need to understand before proceeding)
 
**Background dispatch**:
 
- Research or analysis tasks (not file modifications)
- Results aren't blocking your current work
```

Your central Claude thread reads these rules and makes smarter delegation decisions automatically.

## Teaching Your Central AI to Delegate

Here's what most developers miss: Claude Code isn't one AI - it's an orchestration system. Your main chat session is the "central AI" that coordinates specialist sub-agents. The quality of your work depends on how well you've taught that central thread to delegate.

The Task tool supports three execution modes. Each serves different needs:

| Pattern | Central AI Uses When | Risk If Wrong Choice |
| --- | --- | --- |
| **Parallel** | Independent domains, no file overlap | Merge conflicts, inconsistent state |
| **Sequential** | Dependencies exist, shared resources | Wasted time on serialized independent work |
| **Background** | Research while user continues working | Lost results if not checked |

Without explicit rules, your central AI defaults to conservative sequential execution - safe but slow.

## Parallel: Domain-Based Splitting

The central AI should dispatch parallel sub-agents when work spans independent domains. Configure domain-based routing in your CLAUDE.md:

```
## Domain Parallel Patterns
 
When implementing features across domains, spawn parallel agents:
 
- **Frontend agent**: React components, UI state, forms
- **Backend agent**: API routes, server actions, business logic
- **Database agent**: Schema, migrations, queries
 
Each agent owns their domain. No file overlap.
```

**The critical rule**: Parallel only works when agents touch different files. Your central AI needs to understand domain boundaries to route correctly.

## Sequential: Dependency Chains

When output from one step feeds the next, the central AI must enforce ordering. Common chains:

| Chain | Why Sequential |
| --- | --- |
| Schema -> API -> Frontend | Data structure must exist before interfaces |
| Research -> Planning -> Implementation | Understanding before execution |
| Implementation -> Testing -> Security | Build, validate, then audit |

Add chain definitions to your CLAUDE.md so the central AI recognizes dependency patterns and doesn't parallelize work that must be serial.

## Background: Non-Blocking Research

When the central AI spawns research tasks, it should background them automatically so you can continue working. Press `Ctrl+B` during any sub-agent execution, or configure automatic backgrounding:

```
## Background Execution Rules
 
Run in background automatically:
 
- Web research and documentation lookups
- Codebase exploration and analysis
- Security audits and performance profiling
- Any task where results aren't immediately needed
```

Check `/tasks` anytime to see background agent progress. Results surface when complete. See async workflows for the full background execution guide.

## Configuring Sub-Agent Behavior

Beyond routing rules, Claude Code gives you direct control over sub-agent configuration.

### Choose the Sub-Agent Model

Set `CLAUDE_CODE_SUBAGENT_MODEL` to control which model your sub-agents run on. This is one of the most impactful optimizations for cost and speed:

```
# Use a lighter model for sub-agents to save tokens
export CLAUDE_CODE_SUBAGENT_MODEL="claude-sonnet-4-5-20250929"
```

A common pattern: run your main session on Opus for complex reasoning while sub-agents handle focused tasks on Sonnet. This cuts costs significantly without sacrificing quality on well-scoped sub-agent work.

### Define Persistent Agents in `.claude/agents/`

Instead of relying on ad-hoc Task tool invocations, you can define persistent specialist agents as Markdown files with YAML frontmatter in `.claude/agents/`. These agents are available to Claude's orchestrator automatically.

**Project agents** (`.claude/agents/`) are specific to your repository and shareable with your team. **User agents** (`~/.claude/agents/`) work across all your projects.

Agents defined here inherit your project's CLAUDE.md context, so they pick up coding standards, conventions, and project-specific instructions without additional configuration.

### Restrict Agents with Permission Rules

Use `Task(AgentName)` rules in your permission settings to control which sub-agents can be invoked:

```
{
  "permissions": {
    "deny": ["Task(Explore)", "Task(Plan)"]
  }
}
```

You can also disable agents at launch with the `--disallowedTools` flag:

```
claude --disallowedTools "Task(Explore)"
```

This is useful for reducing token usage in cost-sensitive environments or preventing autonomous exploration in production codebases.

## The Invocation Quality Problem

Most sub-agent failures aren't execution failures - they're invocation failures. The central AI spawns a sub-agent with vague instructions, insufficient context, or unclear deliverables. The sub-agent does its best with bad input.

**Bad invocation**: "Fix authentication"

**Good invocation**: "Fix OAuth redirect loop where successful login redirects to /login instead of /dashboard. Reference the auth middleware in src/lib/auth.ts."

The difference is context density. Sub-agents have temporary context windows - they can't go back and ask clarifying questions. Your central AI needs rules for crafting complete invocations.

This is where most CLAUDE.md configurations stop. They handle routing but not invocation quality. Professional Claude Code setups include full invocation protocols that ensure sub-agents receive comprehensive context, explicit instructions, relevant file references, and clear success criteria with every dispatch.

## Common Orchestration Mistakes

**Over-parallelizing**: Launching 10 parallel agents for a simple feature wastes tokens and creates coordination overhead. Group related micro-tasks.

**Under-parallelizing**: Running four independent analyses sequentially when they could parallelize. Look for domain independence.

**Vague invocations**: Sending sub-agents with "implement the feature" instead of specific scope, file references, and expected outputs.

## Level Up Your Orchestration

The routing rules above will immediately improve how your central AI delegates work. But there's more to professional orchestration:

- **Constitutional invocation requirements** - ensuring every sub-agent dispatch includes the four essential components
- **Agent routing tables** - mapping task types to specialist agents by domain
- **Context handoff protocols** - preserving state across sequential agent chains
- **Session-based coordination** - tracking multi-phase implementations

Start with the routing rules. Add them to your [CLAUDE.md](/blog/claude-md-mastery) today and watch your central AI make smarter delegation decisions. For deeper patterns, explore task distribution and agent fundamentals.

Async Workflows
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** installs a structured workflow for agent work on top of Claude Code: `/spec` plans the change, runs implementation under TDD, and verifies with an automated reviewer pass. The orchestration loop most agent setups end up writing by hand.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
