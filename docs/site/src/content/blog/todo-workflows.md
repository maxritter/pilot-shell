---
slug: "todo-workflows"
title: "Claude Code Todo Lists: Perfect Task Execution Guide"
description: "Master Claude Code's todo system to ensure complete task execution. Learn how to structure todos that Claude follows perfectly every single time."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, Development]
readingTime: 4
keywords: "claude, code, execution, guide, lists, perfect, task, todo, workflows"
---

Development

# Claude Code Todo Lists: Mirror Your Instructions for Perfect Execution

Master Claude Code's todo system to ensure complete task execution. Learn how to structure todos that Claude follows perfectly every single time.

> **Update (Jan 2025)**: Claude Code now has a more powerful [task management system](/blog/guide/development/task-management) with dependencies, blockers, and multi-session collaboration. The fundamentals below still apply, but see the new guide for advanced workflows.

**Problem**: Claude Code sometimes misses steps or does tasks in the wrong order, leaving you wondering if your instructions were clear enough.

**Quick Win**: Add "create a todo list first" to any complex request:

```p-4
claude "add user authentication - create a todo list first, then implement each step"
```

A checklist appears in your terminal showing Claude's plan. You see misunderstandings before any code is written.

## [Todo Lists as Instruction Mirrors](#todo-lists-as-instruction-mirrors)

Your biggest frustration with AI coding isn't the bugs—it's wondering whether Claude truly understood what you asked for. Claude Code uses a built-in TodoWrite tool to create and manage task checklists that appear in your terminal UI.

Think of todos as Claude's "repeat back what I heard" confirmation. The checklist updates in real-time as Claude works, showing completed items, current focus, and remaining tasks. Perfect alignment = clear instructions. Divergence = communication gaps caught early.

### [Common Todo Divergence Patterns](#common-todo-divergence-patterns)

**Out of Order**: Instructions say A then B, todos list B then A
**Missing Steps**: You mention tests, todos skip testing entirely  
**Wrong Detail**: You want high-level "update docs," Claude lists individual files
**Misinterpretation**: You say "review changes," Claude plans "commit changes"

## [Real-Time Todo Steering](#real-time-todo-steering)

Claude's todo list updates in real-time as you provide feedback. This creates a powerful steering mechanism for complex tasks.

**Before Steering:**

```p-4
- [ ] Fix navigation menu alignment
- [ ] Update footer text
- [ ] Add contact form validation
- [ ] Change button color to blue
- [ ] Update documentation
```

**Mid-Task Steering:**

```p-4
claude "Actually make the button green instead of blue"
```

**After Steering:**

```p-4
- [x] Fix navigation menu alignment
- [x] Update footer text
- [ ] Add contact form validation
- [ ] Change button color to green # Updated
- [ ] Update documentation
```

Notice how Claude automatically updated the pending todo while preserving completed work.

## [Advanced Todo Patterns](#advanced-todo-patterns)

### [Get Specific Todos](#get-specific-todos)

Instead of vague todos like "style navbar," demand specifics:

```p-4
Bad: - [ ] Style the navigation bar
 
Good: - [ ] Change navbar height from 60px to 80px - [ ] Reduce padding from 16px to 12px
 
- [ ] Update background to rgba(255,255,255,0.95)
```

### [Phase-Based Dependencies](#phase-based-dependencies)

Structure todos with clear phases:

```p-4
Phase 1: Setup database schema, create user model
Phase 2: Build registration and login (needs Phase 1)
Phase 3: Add validation and styling (needs Phase 2)
```

### [Quality Checkpoints](#quality-checkpoints)

1. **Order**: Logical sequence?
2. **Complete**: All steps included?
3. **Right Detail**: Appropriate granularity?
4. **Clear**: Another dev could follow?

## [Troubleshooting Todo Issues](#troubleshooting-todo-issues)

**Claude skips todos**: Add "Check todo list before starting each step" to your [CLAUDE.md file](/blog/guide/mechanics/claude-md-mastery).

**Todos too generic**: Ask "Break this down into specific, measurable steps" after giving instructions.

**Wrong priorities**: Use numbered lists instead of bullets when order matters:

```p-4
1. First, backup the database
2. Then run migrations
3. Finally, restart services
```

## [Making Todos Stick](#making-todos-stick)

The most effective todo workflows become automatic. Add this pattern to your development routine:

1. Give Claude your task instructions
2. Ask "Create a detailed todo list"
3. Review for alignment with your intentions
4. Refine instructions if todos diverge
5. Proceed with confidence

Perfect todo alignment means perfect instruction clarity. When Claude's todos mirror your mental checklist exactly, you've achieved crystal-clear communication.

**Next Steps**:

- Learn about [git integration patterns](/blog/guide/development/git-integration) for todo-driven commits
- Master [feedback loops](/blog/guide/development/feedback-loops) to iterate on todo quality
- Check out [permission management](/blog/guide/development/permission-management) for secure todo execution
- Explore [planning modes](/blog/guide/mechanics/planning-modes) for structured todo creation
- Review [context management](/blog/guide/mechanics/context-management) to maintain todo history

Last updated on

[Previous

Feedback Loops](/blog/guide/development/feedback-loops)[Next

Task Management](/blog/guide/development/task-management)
