---
slug: "task-management"
title: "Claude Code Task Management: Native Multi-Session AI"
description: "The community built Ralph Wiggum. Anthropic built native task management. Multi-session coordination with dependencies and blockers built in."
date: "2026-02-05"
author: "Max Ritter"
tags: [Guide, Development]
readingTime: 6
keywords: "ai, claude, code, management, multisession, native, task"
---

Development

# Claude Code Task Management: Anthropic's Native Answer to Ralph Wiggum

The community built Ralph Wiggum. Anthropic built native task management. Multi-session coordination with dependencies and blockers built in.

**Problem**: The community solved autonomous coding with [Ralph Wiggum loops](/blog/guide/mechanics/ralph-wiggum-technique), external plan files, and stop hook hacks. It worked, but required workarounds for context persistence and multi-session coordination.

**Quick Win**: Anthropic made it native. Create persistent tasks with dependencies:

```p-4
claude "add user authentication - break into tasks with dependencies"
```

Tasks appear in your terminal (`Ctrl+T` to toggle) and persist across sessions. No more re-explaining where you left off.

## [Tasks: The Evolution of Todos](#tasks-the-evolution-of-todos)

Anthropic upgraded Claude Code's task management on January 23, 2025. This shifts from simple checklists to proper project management with dependencies, blockers, and multi-session collaboration.

The old TodoWrite tool tracked flat lists. The new system uses four specialized tools:

| Tool | Purpose |
| --- | --- |
| **TaskCreate** | Create tasks with subject, description, and status display |
| **TaskGet** | Retrieve full task details including dependencies |
| **TaskUpdate** | Update status, add blockers, modify details |
| **TaskList** | List all tasks with current state |

### [What Changes](#what-changes)

Before: Claude maintained todos in memory, lost on context reset.
After: Tasks persist in `~/.claude/tasks/` (your home directory, not the project) and broadcast updates across sessions.

The fundamentals from [todo workflows](/blog/guide/development/todo-workflows) still apply - tasks mirror your instructions, and misalignment reveals communication gaps. But now you get persistence and dependencies.

## [Tasks vs Ralph Wiggum: What Changes](#tasks-vs-ralph-wiggum-what-changes)

The [Ralph Wiggum technique](/blog/guide/mechanics/ralph-wiggum-technique) pioneered autonomous Claude Code loops. Developers used stop hooks, external plan files, and completion promises to keep Claude working overnight. It worked, but required workarounds.

Tasks solve these problems natively:

| Ralph Workaround | Native Tasks Solution |
| --- | --- |
| External plan.md files for tracking | Built-in storage at `~/.claude/tasks/` (home dir) |
| Stop hooks to check completion | Status lifecycle: `pending → in_progress → completed` |
| Fresh sessions to fight context rot | Tasks persist across context compactions |
| Completion promises ("complete") | Explicit `TaskUpdate` with status |
| Manual progress file coordination | `CLAUDE_CODE_TASK_LIST_ID` for multi-session sync |

**The core insight remains the same**: verification drives everything. Ralph taught us that Claude needs objective "done" criteria. Tasks just make the plumbing native.

If you're running Ralph loops today, you don't need to stop. But Tasks give you native primitives that the community was building manually. Anthropic saw what developers needed and shipped it.

## [Task Dependencies and Blockers](#task-dependencies-and-blockers)

The real power is in dependencies. Tasks can block other tasks:

```p-4
Task 1: Design database schema
Task 2: Create API endpoints (blocked by Task 1)
Task 3: Build frontend components (blocked by Task 2)
```

Claude tracks this automatically. When you mark Task 1 complete, Task 2 becomes available. This prevents parallel work from colliding.

### [Creating Dependent Tasks](#creating-dependent-tasks)

When Claude breaks down complex work, it sets up dependency chains:

```p-4
TaskCreate(subject="Design auth schema", description="...")
TaskCreate(subject="Implement auth API", description="...")
TaskUpdate(taskId="2", addBlockedBy=["1"])
```

The `addBlockedBy` parameter chains tasks together. The `addBlocks` parameter works in reverse, marking what a task blocks.

## [Multi-Session Collaboration](#multi-session-collaboration)

This is where Tasks transform how you work. Set an environment variable to share tasks across sessions:

```p-4
CLAUDE_CODE_TASK_LIST_ID=my-project claude
```

Now multiple Claude sessions coordinate on the same task list. When Session A completes a task, Session B sees the update immediately. This enables:

- **Parallel workstreams**: Frontend and backend sessions sharing blockers
- **Resume anywhere**: Close your laptop, open it tomorrow, tasks are exactly where you left them
- **Team coordination**: Multiple developers sharing task state

### [Practical Multi-Session Workflow](#practical-multi-session-workflow)

1. Start your main session with a named task list:

   ```p-4
   CLAUDE_CODE_TASK_LIST_ID=feature-auth claude
   ```
2. Break down work into tasks with dependencies
3. Spin up a second session for parallel work:

   ```p-4
   CLAUDE_CODE_TASK_LIST_ID=feature-auth claude  # Same ID
   ```
4. Both sessions see and update the shared task list

This works with the Agent SDK too, so [subagents](/blog/guide/agents/sub-agent-design) can claim and complete tasks from the shared list.

## [Task Status Lifecycle](#task-status-lifecycle)

```p-4
pending → in_progress → completed
```

Mark tasks `in_progress` when starting work. This shows a spinner in the task list and signals to other sessions that work is active. Mark `completed` only when fully done.

Tasks persist across context compactions, so even in long sessions with memory resets, the task state survives.

## [Keyboard Shortcuts](#keyboard-shortcuts)

Press `Ctrl+T` to toggle task list visibility in your terminal. You see:

- Pending tasks (up to 10 at a time)
- In-progress tasks with spinner
- Completed tasks with checkmark

Ask Claude "show me all tasks" or "clear all tasks" for direct manipulation.

## [When to Use Tasks](#when-to-use-tasks)

Tasks shine for complex work. Don't overcomplicate simple requests.

**Use Tasks when:**

- Multi-step implementation with dependencies
- Work spanning multiple sessions
- Parallel [subagent coordination](/blog/guide/agents/task-distribution)
- Projects where you'll pause and resume

**Skip Tasks when:**

- Single-file changes
- Quick questions
- One-shot commands

## [Configuring Task Behavior](#configuring-task-behavior)

Add task instructions to your [CLAUDE.md file](/blog/guide/mechanics/claude-md-mastery):

```p-4
## Task Management
 
- Use TaskCreate for multi-step work
- Set dependencies with addBlockedBy for sequential phases
- Update status to in_progress before starting each task
- Mark completed only after verification
```

For cross-session projects, you can also set the environment variable in your shell profile:

```p-4
# In .bashrc or .zshrc
export CLAUDE_CODE_TASK_LIST_ID=my-project
```

## [Migration from Todos](#migration-from-todos)

If you were using TodoWrite in your configuration, update your instructions:

**Old approach:**

```p-4
Keep session checklists in TodoWrite
```

**New approach:**

```p-4
Use TaskCreate for each checklist item
Update status via TaskUpdate (pending → in_progress → completed)
Set dependencies with addBlockedBy parameter
```

The `/todos` command still works as an alias, but the underlying system is now Tasks.

**Next Steps:**

- Master [Ralph Wiggum loops](/blog/guide/mechanics/ralph-wiggum-technique) to combine Tasks with autonomous workflows
- Review [todo workflow fundamentals](/blog/guide/development/todo-workflows) for instruction mirroring patterns
- Learn about [sub-agent patterns](/blog/guide/agents/sub-agent-design) for task-coordinated agents
- Explore [async workflows](/blog/guide/agents/async-workflows) for parallel task execution
- Check [context management](/blog/guide/mechanics/context-management) for long-running projects

Last updated on

[Previous

Todo Workflows](/blog/guide/development/todo-workflows)[Next

Project Templates](/blog/guide/development/project-templates)
