---
slug: "custom-agents"
title: "Claude Code Custom Commands: Build Your Own AI Agents"
description: "Create custom Claude Code agents tailored to your workflow. Learn to build specialized commands that automate your unique development patterns."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, Agents]
readingTime: 5
keywords: "agents, ai, build, claude, code, commands, custom, own"
---

Agents

# Claude Code Custom Commands: Build Your Own AI Agents

Create custom Claude Code agents tailored to your workflow. Learn to build specialized commands that automate your unique development patterns.

**Problem**: Claude Code's default capabilities don't match your specific workflow. You need a code reviewer that follows your team's standards, or a deployment specialist that knows your infrastructure.

**Quick Win**: Create your first custom slash command in under 2 minutes:

```p-4
mkdir -p .claude/commands
```

Create `.claude/commands/code-review.md`:

```p-4
Review the recent code changes for quality and security:
 
1. Run git diff to see recent changes
2. Focus on modified files only
 
Review checklist:
 
- Code is readable and well-named
- No duplicated logic
- Proper error handling exists
- No exposed secrets or credentials
- Performance considerations addressed
 
Provide feedback by priority: Critical → Warnings → Suggestions
```

Then invoke it with `/project:code-review` in Claude Code.

**Understanding**: Custom slash commands are reusable prompts that invoke Claude with specialized instructions. They act like expert consultants you can summon with a single command.

## [How Custom Commands Transform Your Workflow](#how-custom-commands-transform-your-workflow)

Custom commands solve the "remembering the prompt" problem. Instead of typing out detailed instructions every time, you create reusable command files that encode your team's expertise.

**Three Approaches to Custom Agents**:

1. **Slash Commands** (`.claude/commands/`): Invoke on-demand with `/project:command-name`
2. **Agent Definitions** (`.claude/agents/`): Persistent sub-agent identities with YAML frontmatter that Claude's orchestrator spawns automatically
3. **CLAUDE.md Instructions**: Always-active behaviors that shape every interaction

**Commands vs. Agents**: These serve different purposes. Slash commands are prompts you invoke manually for specific workflows. Agent definitions in `.claude/agents/` configure persistent sub-agents that Claude's Task tool can spawn during orchestration. Think of commands as "tools you pick up" and agents as "team members always available."

Both support the same scoping model:

| Scope | Commands | Agents |
| --- | --- | --- |
| **Project** | `.claude/commands/` | `.claude/agents/` |
| **User** | `~/.claude/commands/` | `~/.claude/agents/` |

Project-scoped files are shareable via git. User-scoped files are personal to your machine and available across all projects.

**Separation of Concerns**: Like good software architecture, specialized commands perform better than general prompts. A security-focused command with specific checklists catches more issues than asking "review this code."

## [Creating Effective Custom Commands](#creating-effective-custom-commands)

**Start Simple**: Begin with one specific problem you face repeatedly.

Create `.claude/commands/security-audit.md`:

```p-4
You are a security expert. Scan this codebase for vulnerabilities.
 
Check for:
 
- SQL injection vulnerabilities
- XSS attack vectors
- Authentication bypass issues
- Exposed API keys or secrets
- OWASP Top 10 violations
 
For each finding, provide:
 
1. Vulnerability description
2. Risk level (Critical/High/Medium/Low)
3. Specific fix recommendation
4. Code example of the fix
 
Start by searching for common vulnerability patterns in the codebase.
```

Invoke with `/project:security-audit` whenever you need a security review.

**Dynamic Arguments**: Commands can accept arguments using `$ARGUMENTS`:

Create `.claude/commands/review-file.md`:

```p-4
Review this specific file for issues: $ARGUMENTS
 
Focus on: code quality, potential bugs, security concerns.
```

Invoke with `/project:review-file src/auth/login.ts`

## [CLAUDE.md: Always-Active Agent Behavior](#claudemd-always-active-agent-behavior)

For behaviors you want active in every session, add them to your project's `CLAUDE.md`:

```p-4
## Code Review Standards
 
When reviewing code, always check:
 
- All functions have error handling
- No console.log statements in production code
- API endpoints validate input parameters
- Database queries use parameterized statements
 
## Commit Message Format
 
Use conventional commits: type(scope): description
Types: feat, fix, docs, refactor, test, chore
```

These instructions shape Claude's behavior automatically without needing to invoke a command.

**Project vs User Commands**:

- `.claude/commands/` - Shared with your team via git
- `~/.claude/commands/` - Personal commands on your machine only

## [Persistent Sub-Agent Definitions with `.claude/agents/`](#persistent-sub-agent-definitions-with-claudeagents)

For sub-agents that Claude's orchestrator should be able to spawn automatically, use the `.claude/agents/` directory. These are Markdown files with YAML frontmatter that define the agent's identity, capabilities, and instructions.

Unlike slash commands (which you invoke manually), agent definitions are available to Claude's Task tool during orchestration. When Claude determines it needs a specialist for a particular task, it can spawn a defined agent with the right context and constraints already configured.

Agents defined here also inherit your project's [CLAUDE.md instructions](/blog/guide/mechanics/claude-md-mastery), so they automatically follow your coding standards and project conventions.

For a deeper look at how sub-agents work, including parallel execution, backgrounding with `Ctrl+B`, and invocation quality, see the [agent fundamentals guide](/blog/guide/agents/agent-fundamentals).

## [Common Command Examples](#common-command-examples)

**Database Optimizer** (`.claude/commands/db-optimize.md`):

```p-4
You are a database performance expert.
 
Analyze the database queries in this codebase:
 
1. Find slow or inefficient queries
2. Check for missing indexes
3. Review schema design
 
For each issue, provide:
 
- The problematic query or schema
- Why it's a problem
- Optimized version with explanation
```

**Documentation Writer** (`.claude/commands/write-docs.md`):

```p-4
Write documentation for: $ARGUMENTS
 
Include:
 
- Purpose and overview
- Setup instructions
- Usage examples
- Common troubleshooting
 
Target audience: developers new to this project.
Write in clear, concise language.
```

## [Prompting for Specialized Roles](#prompting-for-specialized-roles)

Sometimes you don't need a saved command. Just prompt Claude directly:

```p-4
Act as a senior security engineer. Review the authentication
flow in src/auth/ for vulnerabilities. Be thorough and paranoid.
```

This works well for one-off tasks. Save it as a command when you find yourself repeating it.

## [Next Actions](#next-actions)

Ready to build your specialist commands? Start with your biggest pain point:

- **Code Quality**: Create a reviewer command with your team's standards using our [agent fundamentals guide](/blog/guide/agents/agent-fundamentals)
- **Security Focus**: Build a vulnerability scanner with our [sub-agent design patterns](/blog/guide/agents/sub-agent-design)
- **Team Workflow**: Design collaboration patterns using [task distribution strategies](/blog/guide/agents/task-distribution)

Your custom commands become more valuable as you refine them. Commit them to git, share with your team, and build a library that encodes your collective expertise.

Last updated on

[Previous

Agent Teams](/blog/guide/agents/agent-teams)[Next

Agent Patterns](/blog/guide/agents/agent-patterns)
