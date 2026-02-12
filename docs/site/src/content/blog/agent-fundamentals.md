---
slug: "agent-fundamentals"
title: "Claude Code Agents: Engineering Autonomous AI Assistants"
description: "Master agent engineering in Claude Code. Design and deploy autonomous agents that handle complex multi-step tasks independently and reliably."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, Agents]
readingTime: 5
keywords: "agent, agents, ai, assistants, autonomous, claude, code, engineering, fundamentals"
---

Agents

# Claude Code Agents: Engineering Autonomous AI Assistants

Master agent engineering in Claude Code. Design and deploy autonomous agents that handle complex multi-step tasks independently and reliably.

**Problem**: Complex projects demand multiple perspectives - security reviewer, performance analyst, documentation writer. Switching mental contexts burns time and dilutes focus.

**Quick Win**: Spawn a sub-agent to handle a parallel task right now:

```p-4
Use a sub-agent to review the authentication module for security vulnerabilities while I continue working on the API endpoints.
```

Claude Code launches an isolated sub-agent that works independently, then reports findings back to your main session.

**Understanding**: Claude Code provides multiple ways to create agent-like behavior - from built-in sub-agents to custom slash commands. Each approach serves different needs. Master these fundamentals before exploring [advanced agent patterns](/blog/guide/agents/agent-patterns).

## [Five Agent Approaches in Claude Code](#five-agent-approaches-in-claude-code)

Claude Code offers several ways to achieve specialized, agent-like behavior:

| Approach | Best For | Persistence |
| --- | --- | --- |
| **Task Tool (Sub-agents)** | Parallel execution, isolated work | Session only |
| **`.claude/agents/` Definitions** | Persistent specialist sub-agents | Permanent |
| **Custom Slash Commands** | Reusable workflows, team sharing | Permanent |
| **CLAUDE.md Personas** | Project-wide behavior rules | Permanent |
| **Perspective Prompting** | Quick context switches | Single request |

Each approach has trade-offs. Sub-agents excel at parallel work; `.claude/agents/` definitions give sub-agents persistent identities; slash commands excel at reusability.

## [Sub-Agents: Built-in Parallel Execution](#sub-agents-built-in-parallel-execution)

The Task tool spawns mini Claude Code instances inside your session. Each sub-agent gets its own context window, works independently, and returns results to the orchestrator.

**Launch parallel sub-agents:**

```p-4
Complete these tasks using 3 sub-agents in parallel:
1. Review src/auth/ for security vulnerabilities
2. Analyze src/api/ for performance bottlenecks
3. Check src/utils/ for code duplication
```

**Why sub-agents matter:**

- Isolated context prevents pollution between tasks
- Parallel execution speeds up multi-file analysis
- Failed sub-agents don't crash your main session
- Background execution lets you continue working (press `Ctrl+B`)

**New**: When Claude spawns sub-agents, you can now background them with `Ctrl+B` and continue chatting with the main agent on other tasks. Results surface automatically when complete. See [async workflows](/blog/guide/agents/async-workflows) for the full guide.

Learn more about [sub-agent design patterns](/blog/guide/agents/sub-agent-design) for complex orchestration.

## [Persistent Agent Definitions with `.claude/agents/`](#persistent-agent-definitions-with-claudeagents)

Claude Code now supports defining custom sub-agents as Markdown files with YAML frontmatter in a dedicated `agents/` directory. These are distinct from slash commands. While slash commands are prompts you invoke manually, agent definitions configure persistent sub-agents that Claude's orchestrator can spawn automatically when needed.

**Two scopes for agent definitions:**

- **Project agents** (`.claude/agents/`) - Specific to your repository, shareable with your team via git
- **User agents** (`~/.claude/agents/`) - Available across all your projects, personal to your machine

Sub-agents defined in `.claude/agents/` inherit your project's CLAUDE.md context, so they automatically pick up your coding standards, conventions, and project-specific instructions.

**Controlling the sub-agent model**: Set the `CLAUDE_CODE_SUBAGENT_MODEL` environment variable to choose which model your sub-agents use. This is useful for cost optimization (running sub-agents on a lighter model) or for tasks that benefit from stronger reasoning.

```p-4
# Run sub-agents on Sonnet for cost savings
export CLAUDE_CODE_SUBAGENT_MODEL="claude-sonnet-4-5-20250929"
```

### [Restricting Sub-Agent Access with Permission Rules](#restricting-sub-agent-access-with-permission-rules)

You can control which sub-agents Claude is allowed to invoke using `Task(AgentName)` [permission rules](/blog/guide/development/permission-management). Add these to the `deny` array in your `settings.json` or use the `--disallowedTools` CLI flag:

```p-4
{
  "permissions": {
    "deny": ["Task(Explore)"]
  }
}
```

This prevents Claude from spawning the `Explore` sub-agent. Built-in agent names include `Explore`, `Plan`, and `Verify`. You can also disable agents at launch:

```p-4
claude --disallowedTools "Task(Plan)" "Task(Verify)"
```

Use this when you want tighter control over agent behavior in sensitive environments or to reduce token usage from autonomous exploration.

## [Custom Slash Commands: Reusable Specialists](#custom-slash-commands-reusable-specialists)

Create permanent, reusable commands by adding Markdown files to `.claude/commands/`:

```p-4
## <!-- .claude/commands/security-review.md -->
 
description: "Security-focused code review"
allowed-tools: ["Read", "Grep", "Bash"]
 
---
 
Review the specified code for security vulnerabilities:
 
1. Check for SQL injection risks
2. Identify authentication bypasses
3. Flag hardcoded secrets
4. Report findings with severity ratings
 
Target: $ARGUMENTS
```

Now run `/project:security-review src/auth/` to invoke your specialist.

**Command locations:**

- `.claude/commands/` - Project-specific, shareable via git
- `~/.claude/commands/` - Personal, available everywhere

## [CLAUDE.md: Persistent Agent Behavior](#claudemd-persistent-agent-behavior)

Your [CLAUDE.md file](/blog/guide/mechanics/claude-md-mastery) shapes Claude's behavior for every interaction in your project:

```p-4
<!-- CLAUDE.md -->
 
## Code Review Protocol
 
When reviewing code, always:
 
1. Check for security vulnerabilities first
2. Identify performance implications
3. Suggest specific improvements with code examples
4. Flag any deviation from project conventions
```

This creates agent-like consistency without explicit invocation.

## [Perspective Prompting: Quick Context Switches](#perspective-prompting-quick-context-switches)

For one-off analysis, prompt Claude to adopt a specific perspective:

```p-4
Analyze this authentication flow from three perspectives:
1. Security engineer: What vulnerabilities exist?
2. Performance engineer: What bottlenecks could occur at scale?
3. Junior developer: What parts are confusing or poorly documented?
```

No setup required - immediate specialized analysis.

## [Choosing Your Approach](#choosing-your-approach)

**Use sub-agents when:** You need parallel execution or isolated context for multiple tasks.

**Use `.claude/agents/` when:** You want persistent, named specialist agents that Claude's orchestrator can invoke automatically based on task type.

**Use slash commands when:** You repeat the same workflow across sessions or want to share with your team.

**Use CLAUDE.md when:** You want consistent behavior applied automatically to all interactions.

**Use perspective prompting when:** You need quick, one-time specialized analysis.

**Next Action**: Create your first slash command in `.claude/commands/` for a workflow you repeat often, then explore [task distribution strategies](/blog/guide/agents/task-distribution) for complex orchestration.

**Explore More Agent Concepts**:

- [Sub-Agent Best Practices](/blog/guide/agents/sub-agent-best-practices) - When to use parallel, sequential, or background execution
- [Sub-Agent Design](/blog/guide/agents/sub-agent-design) - Architecture patterns for orchestrating multiple agents
- [Custom Agents](/blog/guide/agents/custom-agents) - Build specialized agents with slash commands
- [Agent Patterns](/blog/guide/agents/agent-patterns) - Proven design patterns for agent systems
- [Human-Like Agents](/blog/guide/agents/human-like-agents) - Create agents with distinct personalities

Last updated on

[Previous

Efficiency Patterns](/blog/guide/performance/efficiency-patterns)[Next

Async Workflows](/blog/guide/agents/async-workflows)
