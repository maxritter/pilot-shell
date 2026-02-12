---
slug: "agent-teams"
title: "Claude Code Agent Teams: Multi-Session Orchestration"
description: "Orchestrate teams of Claude Code sessions working together. Shared tasks, inter-agent messaging, and centralized management for parallel AI development."
date: "2026-02-05"
author: "Max Ritter"
tags: [Guide, Agents]
readingTime: 23
keywords: "agent, claude, code, multisession, orchestration, teams"
---

Agents

# Claude Code Agent Teams: Orchestrate Multiple Claude Sessions in Parallel

Orchestrate teams of Claude Code sessions working together. Shared tasks, inter-agent messaging, and centralized management for parallel AI development.

**Problem**: You're managing a complex codebase refactor that touches the API layer, database migrations, test coverage, and documentation. A single Claude Code session handles one piece at a time. [Subagents](/blog/guide/agents/agent-fundamentals) can parallelize work, but they report results back in isolation. They can't share findings, challenge assumptions, or coordinate directly with each other. When you need real collaboration between AI workers, subagents hit a wall.

**Quick Win**: Enable Claude Code Agent Teams and orchestrate a collaborative team in one prompt:

```p-4
# Add to your environment or settings.json
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

Then tell Claude:

```p-4
Create an agent team to refactor the payment module. Spawn three teammates:
one for the API layer, one for the database migrations, one for test coverage.
Have them coordinate through the shared task list.
```

Claude creates a team lead, spawns three independent teammates, and coordinates their work through a shared task list and direct messaging. Each teammate owns their scope. No conflicts, no isolation.

**Note on terminology**: This post covers Claude Code's native Agent Teams feature, an experimental built-in system for multi-agent collaboration. If you're looking for DIY builder-validator patterns using the Task tool, see [team orchestration with builder-validator chains](/blog/guide/agents/team-orchestration). Both approaches enable multi-agent workflows, but they work very differently under the hood.

## [What Are Claude Code Agent Teams?](#what-are-claude-code-agent-teams)

Agent Teams is an experimental feature that lets you orchestrate teams of Claude Code sessions working together on a shared project. One session acts as the team lead. It coordinates work, assigns tasks, and synthesizes results. Teammates work independently, each in its own context window, and communicate directly with each other.

The key difference from [subagents](/blog/guide/agents/agent-fundamentals) is communication. Subagents run within a single session and can only report results back to the main agent. They can't message each other, share discoveries mid-task, or coordinate without the main agent acting as intermediary. Agent Teams removes that bottleneck entirely. Teammates message each other, claim tasks from a shared list, and work through problems collaboratively. You can interact with individual teammates directly without going through the lead.

Think of it this way: subagents are contractors you send on separate errands. Agent Teams is a project team sitting in the same room, each working on their piece while staying in sync through conversation. It's the difference between managing a freelancer queue and managing a full crew.

## [Why Agent Teams Matter Now](#why-agent-teams-matter-now)

Anthropic shipped Agent Teams as an experimental feature with the Opus 4.6 release. The community had been building similar patterns independently for months, using tools like OpenClaw and custom orchestration scripts. Anthropic recognized the demand and built it into Claude Code natively.

This is significant for three reasons:

1. **Native integration beats bolted-on solutions.** The shared task list, mailbox system, and teammate lifecycle management are built into Claude Code's core. No external dependencies, no fragile scripts.
2. **The multi-agent paradigm is maturing.** Developers who build muscle memory with agent teams now will have a serious edge as these tools evolve. The gap between "uses Claude Code" and "orchestrates Claude Code teams" will widen.
3. **Complex projects demand collaboration, not just parallelism.** A [task distribution](/blog/guide/agents/task-distribution) strategy gets you parallel execution. Agent Teams gets you parallel execution with active coordination, where teammates can share context, challenge each other's approaches, and converge on better solutions together.

## [When to Use Agent Teams](#when-to-use-agent-teams)

Agent Teams add coordination overhead and use significantly more tokens than a single session. They work best when teammates can operate independently on distinct scopes while still benefiting from communication.

### [Strong Use Cases](#strong-use-cases)

- **Research and review**: Multiple teammates investigate different aspects of a problem simultaneously, then share and challenge each other's findings
- **New modules or features**: Teammates each own a separate component without stepping on each other's files
- **Debugging with competing hypotheses**: Teammates test different theories in parallel and actively try to disprove each other
- **Cross-layer coordination**: Changes that span frontend, backend, and tests, each owned by a different teammate
- **Debate and consensus**: Multiple teammates argue different positions on an architectural decision, converging on the strongest approach
- **Large-scale inventory or classification**: Teammates divide a large dataset and process segments independently

### [When to Skip Agent Teams](#when-to-skip-agent-teams)

For sequential tasks, same-file edits, or work with tight dependencies, a single session or [subagent patterns](/blog/guide/agents/sub-agent-best-practices) are more cost-effective. If your workers don't need to communicate with each other, the overhead of an Agent Team isn't worth it. Use [async workflows](/blog/guide/agents/async-workflows) for simple parallel execution without the collaboration layer.

## [Subagents vs Agent Teams: Choosing Your Approach](#subagents-vs-agent-teams-choosing-your-approach)

Both let you parallelize work, but they operate at different levels. The deciding question: do your workers need to communicate with each other?

| Feature | Subagents | Agent Teams |
| --- | --- | --- |
| **Context** | Own window, results summarized back to caller | Own window, fully independent |
| **Communication** | Report results back to the main agent only | Teammates message each other directly |
| **Coordination** | Main agent manages all work | Shared task list with self-coordination |
| **Best for** | Focused tasks where only the result matters | Complex work requiring discussion and collaboration |
| **Token cost** | Lower: results summarized back to main context | Higher: each teammate is a separate Claude instance |
| **Use case examples** | Code review, file analysis, research lookups | Multi-component features, debates, cross-layer refactors |
| **Setup required** | None (built into Claude Code) | Environment variable to enable |
| **Communication pattern** | Hub-and-spoke (all through main agent) | Mesh (any teammate to any teammate) |

Use subagents when you need quick, focused workers that report back. Use Agent Teams when teammates need to share findings, challenge each other, and coordinate on their own.

For more on subagent routing decisions, see [sub-agent best practices](/blog/guide/agents/sub-agent-best-practices).

## [Step-by-Step: Your First Agent Team in 5 Minutes](#step-by-step-your-first-agent-team-in-5-minutes)

### [Step 1: Enable Agent Teams](#step-1-enable-agent-teams)

Set the environment variable in your shell:

```p-4
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

Or add it to your `settings.json` for persistence across sessions:

```p-4
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### [Step 2: Describe Your Task and Team Structure](#step-2-describe-your-task-and-team-structure)

Tell Claude what you need in natural language. Be specific about roles and scope:

```p-4
Create an agent team to review our authentication system. Spawn three teammates:
- Security reviewer: audit for vulnerabilities, check token handling
- Performance analyst: profile response times, identify bottlenecks
- Test coverage checker: verify edge cases, find untested paths
Have them share findings and coordinate through the task list.
```

### [Step 3: Watch the Team Form](#step-3-watch-the-team-form)

Claude creates a team lead (your main session), spawns the teammates, and distributes work through the shared task list. You'll see teammates appear in the interface.

Claude can also propose creating a team on its own. If it determines your task would benefit from parallel work, it may suggest forming a team. You confirm before it proceeds. Either way, you stay in control.

### [Step 4: Monitor and Steer](#step-4-monitor-and-steer)

Use the keyboard shortcuts to track progress:

- **Shift+Up/Down**: Select a teammate to view or message
- **Enter**: View a teammate's full session
- **Ctrl+T**: Toggle the task list
- **Escape**: Interrupt a teammate's current turn

### [Step 5: Clean Up](#step-5-clean-up)

When work is done, shut down teammates and clean up:

```p-4
Ask all teammates to shut down, then clean up the team.
```

When a teammate receives a shutdown request, it can approve (exiting gracefully) or reject with an explanation if it still has pending work. Teammates finish their current request or tool call before shutting down, so this can take time.

Shut down all teammates before running cleanup. The lead checks for active teammates and won't clean up if any are still running. Always use the lead to clean up. Teammates should not run cleanup because their team context may not resolve correctly, potentially leaving shared resources in an inconsistent state.

## [Architecture: How Agent Teams Work](#architecture-how-agent-teams-work)

An Agent Team has four components working together:

| Component | Purpose |
| --- | --- |
| **Team Lead** | Your main Claude Code session. Creates the team, spawns teammates, assigns tasks, and synthesizes results. |
| **Teammates** | Separate Claude Code instances. Each gets its own context window and works on assigned tasks. |
| **Shared Task List** | Central work queue all agents can see. Tasks have states (pending, in progress, completed) and support dependencies. |
| **Mailbox** | Messaging system for communication between agents. |

Teams and their configuration live locally:

- Team config: `~/.claude/teams/{team-name}/config.json`
- Task list: `~/.claude/tasks/{team-name}/`

The team config contains a members array with each teammate's name, agent ID, and agent type.

### [Context and Communication](#context-and-communication)

Each teammate has its own context window. When spawned, a teammate loads the same project context as a regular Claude Code session: your [CLAUDE.md](/blog/guide/mechanics/claude-md-mastery), MCP servers, and [skills](/blog/guide/mechanics/claude-skills-guide). It also receives the spawn prompt from the lead. The lead's conversation history does not carry over.

Communication works through several channels:

- **Automatic message delivery**: when teammates send messages, they are delivered automatically to recipients
- **Idle notifications**: when a teammate finishes and stops, they automatically notify the lead
- **Shared task list**: all agents can see task status and claim available work
- **Message**: send to one specific teammate
- **Broadcast**: send to all teammates simultaneously (use sparingly, since costs scale with team size)

### [Permissions](#permissions)

Teammates start with the lead's permission settings. If the lead runs with `--dangerously-skip-permissions`, all teammates do too. After spawning, you can change individual teammate modes, but you cannot set per-teammate modes at spawn time.

## [Display Modes: Watching Your Team Work](#display-modes-watching-your-team-work)

Agent Teams supports two ways to view what's happening.

### [In-Process Mode (Default)](#in-process-mode-default)

All teammates run inside your main terminal. You see the lead's output by default and can switch between teammates using keyboard shortcuts:

| Shortcut | Action |
| --- | --- |
| **Shift+Up/Down** | Select a teammate to view or message |
| **Enter** | View a teammate's full session |
| **Escape** | Interrupt a teammate's current turn |
| **Ctrl+T** | Toggle the task list |
| **Shift+Tab** | Cycle through modes (including delegate) |

This works in any terminal. No extra setup required.

### [Split Pane Mode](#split-pane-mode)

Each teammate gets its own terminal pane. You see everyone's output simultaneously and click into any pane to interact with their session directly. This requires tmux or iTerm2.

tmux has known limitations on certain operating systems and traditionally works best on macOS. Using `tmux -CC` in iTerm2 is the suggested entrypoint into tmux.

To configure display mode, set `teammateMode` in your `settings.json`:

```p-4
{
  "teammateMode": "in-process"
}
```

The three options:

- `"auto"` (default): Uses split panes if you're already inside a tmux session, otherwise falls back to in-process
- `"tmux"`: Enables split panes, auto-detects between tmux and iTerm2 based on your terminal
- `"in-process"`: Forces all teammates into the main terminal

You can also override per-session with a flag:

```p-4
claude --teammate-mode in-process
```

## [Delegate Mode: Keep the Lead Focused](#delegate-mode-keep-the-lead-focused)

Without delegate mode, the lead sometimes starts implementing tasks itself instead of waiting for teammates. This defeats the purpose of having a team.

Press **Shift+Tab** to cycle into delegate mode after starting a team. This restricts the lead to coordination-only tools: spawning teammates, messaging, shutting them down, and managing tasks. The lead can't touch code directly. It focuses entirely on orchestration.

Use delegate mode when you want the lead to act as a project manager rather than an individual contributor. This is especially important for larger teams where the lead's job is coordination, not implementation.

## [Plan Approval: Review Before Execution](#plan-approval-review-before-execution)

For complex or risky tasks, require teammates to plan before they implement anything. The teammate works in read-only plan mode until the lead approves their approach.

```p-4
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

The workflow:

1. Teammate receives the task and works in read-only mode
2. Teammate creates a plan and sends a plan approval request to the lead
3. Lead reviews the plan and either approves or rejects with feedback
4. If rejected, the teammate stays in plan mode, revises, and resubmits
5. Once approved, the teammate exits plan mode and begins implementation

The lead makes approval decisions autonomously. Influence its judgment through your initial prompt: "only approve plans that include test coverage" or "reject plans that modify the database schema."

## [Quality Gates with Hooks](#quality-gates-with-hooks)

Agent Teams integrates with Claude Code's hook system for automated quality checks. Two hooks are particularly useful for team workflows:

**TeammateIdle**: Runs when a teammate is about to go idle. Exit with code 2 to send feedback and keep the teammate working. Use this to automatically assign follow-up tasks or redirect a teammate that finished early.

**TaskCompleted**: Runs when a task is being marked complete. Exit with code 2 to prevent completion and send feedback. Use this to enforce quality gates: require tests to pass, code review to happen, or specific acceptance criteria to be met before a task can close.

These hooks let you build structured quality gates without manual intervention. The team operates with built-in guardrails that enforce your standards automatically. For more on hooks, see the [hooks guide](/blog/tools/hooks/hooks-guide).

## [Talking to Teammates Directly](#talking-to-teammates-directly)

Each teammate is a full, independent Claude Code session. You can message any teammate directly without going through the lead.

**In-process mode**: Use Shift+Up/Down to select a teammate, then type to send them a message. Press Enter to view a teammate's session, then Escape to interrupt their current turn. Press Ctrl+T to toggle the task list.

**Split-pane mode**: Click into a teammate's pane to interact with their session directly.

## [Task Assignment and Claiming](#task-assignment-and-claiming)

The shared task list coordinates all work. The lead creates tasks and teammates work through them. Tasks have three states: **pending**, **in progress**, and **completed**. Tasks can depend on other tasks: a pending task with unresolved dependencies cannot be claimed until those dependencies are completed. This mirrors the dependency chain patterns from [team orchestration](/blog/guide/agents/team-orchestration).

The lead can assign tasks explicitly, or teammates can self-claim available work. After finishing a task, a teammate picks up the next unassigned, unblocked task on its own.

Task claiming uses file locking to prevent race conditions where two teammates grab the same task. This is the coordination layer that prevents teammates from stepping on each other's toes. The system manages task dependencies automatically: when a teammate completes a task that other tasks depend on, blocked tasks unblock without manual intervention.

For more on task coordination patterns, see [task distribution](/blog/guide/agents/task-distribution) and [todo workflows](/blog/guide/development/todo-workflows).

## [Real-World Use Cases with Prompt Templates](#real-world-use-cases-with-prompt-templates)

Here are battle-tested prompts you can copy and adapt for common scenarios.

### [1. Parallel Code Review](#1-parallel-code-review)

```p-4
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings. Use delegate mode so the
lead synthesizes a final review without doing its own analysis.
```

Each reviewer works from the same PR but applies a different lens. The lead synthesizes findings into a comprehensive review that catches issues a single reviewer would miss by focusing on only one concern at a time.

### [2. Debugging with Competing Hypotheses](#2-debugging-with-competing-hypotheses)

```p-4
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk
to each other to try to disprove each other's theories, like a scientific
debate. Update the findings doc with whatever consensus emerges.
```

The debate structure fights anchoring bias. Multiple independent investigators actively trying to disprove each other means the surviving theory is more likely correct. Instead of testing theories sequentially (where you tend to stop at the first plausible explanation), parallel investigation with active challenge produces more reliable conclusions.

### [3. Full-Stack Feature Implementation](#3-full-stack-feature-implementation)

```p-4
Create an agent team to implement the user notifications system.
Spawn four teammates:
- Backend: Create the notification service, database schema, and API endpoints
- Frontend: Build the notification bell component, dropdown, and read/unread states
- Tests: Write integration tests for the full notification flow
- Docs: Update the API documentation and add usage examples

Assign each teammate clear file boundaries. Backend owns src/api/notifications/
and src/db/migrations/. Frontend owns src/components/notifications/.
Tests own tests/notifications/. No file overlap.
```

File-level boundaries prevent merge conflicts. Each teammate knows exactly which directories they own, and the shared task list keeps everyone synchronized on progress.

### [4. Architecture Decision Record](#4-architecture-decision-record)

```p-4
Create an agent team to evaluate database options for our new analytics feature.
Spawn three teammates, each advocating for a different approach:
- Teammate 1: Argue for PostgreSQL with materialized views
- Teammate 2: Argue for ClickHouse as a dedicated analytics store
- Teammate 3: Argue for keeping everything in the existing MongoDB

Have them challenge each other's arguments. Focus on: query performance
at 10M+ rows, operational complexity, migration effort, and cost.
The lead should synthesize a decision document with the strongest arguments
from each side.
```

This deliberation pattern produces better architectural decisions than a single agent weighing options alone. Each teammate commits fully to their position and looks for weaknesses in the others.

### [5. Bottleneck Analysis](#5-bottleneck-analysis)

```p-4
Create an agent team to identify performance bottlenecks in the application.
Spawn three teammates:
- One profiling API response times across all endpoints
- One analyzing database query performance and indexing
- One reviewing frontend bundle size and rendering performance

Have them share findings when they discover something that affects
another teammate's domain (e.g., slow API caused by missing DB index).
```

Cross-domain communication is where Agent Teams shine over subagents. When the database analyst discovers a missing index that explains the API teammate's slow endpoint, they can share that finding directly.

### [6. Inventory Classification](#6-inventory-classification)

```p-4
Create an agent team to classify our product catalog. We have 500 items
that need categorization, tagging, and description updates.
Spawn 4 teammates, each handling a segment:
- Teammate 1: Items 1-125
- Teammate 2: Items 126-250
- Teammate 3: Items 251-375
- Teammate 4: Items 376-500

Use the classification schema in docs/taxonomy.md. Have teammates
flag edge cases for the lead to review.
```

Data-parallel work scales linearly with teammates. Each works through their segment independently, flagging ambiguous items for human review.

## [Specifying Teammates and Models](#specifying-teammates-and-models)

Claude decides the number of teammates based on the complexity of your task, or you can specify exactly what you want:

```p-4
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

You can also mix models. Run the lead on Opus for strategic coordination while teammates run on Sonnet for focused implementation. This balances cost with capability.

## [Token Cost Considerations](#token-cost-considerations)

Agent Teams use significantly more tokens than a single session. Each teammate has its own context window, and token usage scales with the number of active teammates.

**Where the tokens go:**

- Each teammate loads project context independently (CLAUDE.md, skills, project files)
- Communication adds cost: every message consumes tokens in both the sender's and receiver's context
- Broadcasting multiplies cost by the number of teammates receiving the message
- The lead consumes tokens for coordination, task management, and synthesis

**When the cost is worth it:**

- Research and review tasks where multiple perspectives catch issues a single pass would miss
- Debugging sessions where parallel hypothesis testing resolves issues faster
- Large feature implementations where the time savings justify the token spend
- Architectural decisions where thorough evaluation prevents costly mistakes later

**When to keep costs down:**

- Use Sonnet for teammates doing focused implementation work; reserve Opus for the lead
- Prefer direct messages over broadcasts
- Limit team size to what the task requires (3 teammates is often better than 6)
- Use subagents or single sessions for routine tasks that don't need inter-agent communication
- Set clear scope for each teammate to prevent unnecessary exploration

**Rough guideline**: A 3-teammate team running for 30 minutes will use roughly 3-4x the tokens of a single session doing the same work sequentially. The trade-off is speed and coverage versus cost.

## [Best Practices](#best-practices)

- **Give teammates enough context**: Include task-specific details in the spawn prompt so teammates don't start blind. Reference specific files, acceptance criteria, and constraints.
- **Size tasks appropriately**: Not too small, not too large. Aim for self-contained units with clear deliverables, roughly 5-6 tasks per teammate.
- **Wait for teammates to finish before proceeding**: Don't let the lead race ahead while teammates are still working. Use delegate mode to enforce this.
- **Start with research and review before implementation**: Build intuition for when teams add value before applying them to implementation-heavy workflows.
- **Avoid file conflicts**: Each teammate should own different files. Two teammates editing the same file leads to overwrites. Define clear directory boundaries in your spawn prompt.
- **Monitor and steer**: Check progress regularly with Ctrl+T and redirect approaches that are going off track.
- **Use delegate mode by default**: It prevents the lead from doing work that teammates should handle, keeping the coordination clean.

## [Troubleshooting](#troubleshooting)

| Issue | Solution |
| --- | --- |
| Teammates not appearing | Check Shift+Down, verify task complexity warrants a team, check tmux/iTerm2 setup for split-pane mode |
| Too many permission prompts | Pre-approve common operations in your permission settings |
| Teammates stopping on errors | Give additional instructions or spawn replacement teammates |
| Lead shuts down before work is done | Tell the lead to keep going and wait for teammates to finish |
| Orphaned tmux sessions | Run `tmux ls` to list sessions, then `tmux kill-session -t <session-name>` to clean up |
| Teammates stepping on each other | Define explicit file boundaries in the spawn prompt; use directory-level ownership |
| Task status looks stuck | Teammates sometimes forget to mark tasks complete; check manually with Ctrl+T and prompt the teammate |

## [Current Limitations](#current-limitations)

Agent Teams is experimental. These constraints are worth knowing before you commit to a team-based workflow:

- **No session resumption**: In-process teammates are not restored when using `/resume` or `/rewind`. After resuming, the lead may try to message teammates that no longer exist. Tell it to spawn replacements.
- **Task status can lag**: Teammates sometimes forget to mark tasks as completed, blocking dependent work. Check manually if something looks stuck.
- **Slow shutdown**: Teammates finish their current request or tool call before shutting down. This can take time.
- **One team per session**: A lead manages one team at a time. Clean up the current team before starting another.
- **No nested teams**: Teammates cannot spawn their own teams. Only the lead manages the team hierarchy.
- **Fixed lead**: The session that creates the team stays the lead for its lifetime. You cannot promote a teammate or transfer leadership.
- **Permissions set at spawn**: All teammates start with the lead's permission settings. You can change individual modes after spawning, but not at spawn time.
- **Split panes require tmux or iTerm2**: Split-pane mode is not supported in other terminals.
- **CLAUDE.md works normally**: Teammates load project instructions the same way any session does.

Being transparent about these limitations matters. Agent Teams is a powerful tool with rough edges. The developers who learn the workarounds now will be ready when Anthropic polishes the feature.

## [Managing Agent Coordination at Scale](#managing-agent-coordination-at-scale)

As your agent teams grow in complexity, the coordination challenge shifts from "can I parallelize?" to "how do I manage the orchestration?" The spawn prompts, task boundaries, permission settings, and model selection decisions add up.

This is where structured frameworks help.

## [Getting Started: A Progressive Path](#getting-started-a-progressive-path)

If you're new to Agent Teams, start simple and build up.

### [Week 1: Research and Review](#week-1-research-and-review)

Pick a PR that needs review. Enable Agent Teams, then run:

```p-4
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

Three reviewers, three lenses, one comprehensive review. You'll see how teammates work through the task list, communicate findings, and deliver results. Low risk, high learning.

### [Week 2: Debugging with Debate](#week-2-debugging-with-debate)

Take a bug report and use the competing hypotheses pattern:

```p-4
Users report intermittent 500 errors on the checkout endpoint.
Spawn 3 teammates to investigate different hypotheses:
- One checking database connection pooling
- One investigating race conditions in the payment flow
- One analyzing server resource limits
Have them share findings and challenge each other's theories.
```

This teaches you how inter-agent communication works in practice.

### [Week 3: Implementation](#week-3-implementation)

Once you're comfortable with coordination patterns, try a feature implementation with clear file boundaries:

```p-4
Create an agent team to build the webhook system.
Assign directory-level ownership to prevent conflicts.
Use delegate mode for the lead.
```

By week three, you'll have intuition for when teams add value and when a single session or [subagent approach](/blog/guide/agents/sub-agent-design) is the better choice.

## [The Multi-Agent Spectrum](#the-multi-agent-spectrum)

Agent Teams sits at one end of a spectrum of multi-agent approaches in Claude Code. Understanding where each tool fits helps you choose the right one:

| Approach | Communication | Best For | Guide |
| --- | --- | --- | --- |
| **Single session** | N/A | Sequential, focused tasks | [Context management](/blog/guide/mechanics/context-management) |
| **Subagents (Task tool)** | Results only, back to main | Parallel focused work | [Agent fundamentals](/blog/guide/agents/agent-fundamentals) |
| **Builder-validator pairs** | Structured handoff via tasks | Quality-gated implementation | [Team orchestration](/blog/guide/agents/team-orchestration) |
| **Agent Teams** | Full mesh, direct messaging | Collaborative exploration | This guide |

Combine these approaches based on your needs. Use Agent Teams for the collaborative exploration phase, then switch to [builder-validator patterns](/blog/guide/agents/team-orchestration) for the implementation phase where quality gates matter. For [keeping context manageable](/blog/guide/performance/context-preservation) across long-running team sessions, apply the same strategies you would with any multi-agent workflow.

The developers building agent team muscle memory today are investing in a skill that will compound as multi-agent AI tooling matures. Start with a review task this week. The overhead is low, and the capabilities will change how you think about complex development work.

Last updated on

[Previous

Team Orchestration](/blog/guide/agents/team-orchestration)[Next

Custom Agents](/blog/guide/agents/custom-agents)
