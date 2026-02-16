---
slug: "claude-code-task-management"
title: "Multi-Session Task Management in Claude Code"
description: "Track work across sessions with built-in task management. Dependencies, progress tracking, and cross-session persistence."
date: "2026-02-06"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 4
keywords: "Claude Code tasks, task management, multi-session, Claude Code workflow, task dependencies, progress tracking"
---

# Multi-Session Task Management in Claude Code

Claude Code includes a built-in task system for coordinating work across sessions. Tasks persist between sessions, support dependencies, and show real-time progress in your terminal.

## Task Operations

### Creating Tasks

Break work into trackable units:

```
TaskCreate: "Add user authentication"
TaskCreate: "Write auth integration tests" [blockedBy: task-1]
TaskCreate: "Update API documentation" [blockedBy: task-1]
```

Each task gets a unique ID and status tracking: `pending` → `in_progress` → `completed`.

### Managing Progress

| Operation | What It Does |
|-----------|-------------|
| **TaskCreate** | Add a new task with description and dependencies |
| **TaskList** | See all tasks, their status, and what's blocked |
| **TaskGet** | Read full details of a specific task |
| **TaskUpdate** | Change status, add dependencies, update description |

Mark tasks as you work:

```
TaskUpdate: task-1, status: "in_progress"   # Starting work
TaskUpdate: task-1, status: "completed"      # Done
```

### Dependencies

Tasks can block other tasks. A blocked task won't show as ready until its dependencies complete:

```
Task 1: Set up database schema
Task 2: Implement user model [blockedBy: 1]
Task 3: Add API endpoints [blockedBy: 2]
Task 4: Write E2E tests [blockedBy: 3]
```

This prevents Claude from jumping ahead and building on incomplete foundations. Tasks 3 and 4 can also run in parallel once task 2 completes — just set both to depend on task 2.

## Progress Tracking

Tasks show real-time status in your terminal via `Ctrl+T`:

- Which task is currently in progress (with a spinner)
- How many tasks are completed vs remaining
- What's blocked and why

This visibility is especially valuable for long features where you need to track progress across hours of work.

## Cross-Session Persistence

Tasks survive session restarts. When auto-compaction triggers, the new session picks up the task list exactly where the old one left off. At the start of a new session, Claude checks `TaskList` to find where to resume.

Stale tasks from previous sessions are cleaned up automatically — each session starts by reviewing the task list and removing anything no longer relevant.

## When to Use Tasks

| Scenario | Use Tasks? |
|----------|-----------|
| Quick bug fix | No — just do it |
| Feature with 3+ steps | Yes |
| Multi-file refactor | Yes |
| User provides a list of items | Yes |
| Spec-driven development | Automatic |

## How Pilot Uses Tasks

During `/spec` implementation, Pilot automatically creates tasks from the plan. Each plan task becomes a tracked item with proper dependencies. The TDD loop runs for each task in sequence, with real-time progress visible in your terminal throughout. When context fills up and auto-compaction triggers, the task list is preserved and work continues from the first uncompleted task.
