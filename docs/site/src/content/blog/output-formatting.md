---
slug: "output-formatting"
title: "Claude Code Diff Review: 4 Essential Shortcuts"
description: "Press d for diffs, e to edit, y to accept, n to reject. Master the 4 keyboard shortcuts that control every Claude Code file change you make."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 4
keywords: "4, claude, code, diff, essential, formatting, output, review, shortcuts"
---

Mechanics

# Claude Code Diff Review: 4 Keys That Control Every Edit

Press d for diffs, e to edit, y to accept, n to reject. Master the 4 keyboard shortcuts that control every Claude Code file change you make.

**Problem**: You asked Claude Code to make changes but you are not sure what it actually modified, how to review it, or how to get output in the format you need.

**Quick Win**: Press `d` when Claude proposes a change to see the full diff before accepting:

```p-4
# Claude shows a proposed edit
# Press these keys to control what happens:
y - accept the change
n - reject and continue
d - show full diff
e - edit the change before accepting
```

**Understanding**: Claude Code writes files directly using built-in tools. You control every modification through an approval workflow that shows exactly what changes before they happen.

## [How Claude Code Handles File Output](#how-claude-code-handles-file-output)

Claude Code does not generate code for you to copy. It writes directly to your filesystem using two core tools:

**Write**: Creates new files or completely replaces existing ones
**Edit**: Makes surgical changes to specific parts of existing files

When Claude proposes a change, you see a preview of what will happen:

```p-4
Claude wants to edit src/utils/auth.ts:

- const TOKEN_EXPIRY = 3600;
+ const TOKEN_EXPIRY = 7200;
```

This diff format shows exactly what lines change. Red lines with `-` get removed. Green lines with `+` get added.

## [The Accept/Reject Workflow](#the-acceptreject-workflow)

Every file modification requires your approval. This is the core safety mechanism:

```p-4
# Claude proposes creating a new file
Claude wants to write to src/components/Button.tsx
 
# Your options:
y    Accept this change
n    Reject and tell Claude why
d    View full diff (for edits)
e    Edit before accepting
Esc  Abort current operation
```

For trusted operations, enable [auto-accept mode](/blog/guide/development/permission-management) with `Shift+Tab`. Claude then proceeds without prompting for each file.

## [Multi-File Operations](#multi-file-operations)

Claude handles multiple files sequentially, maintaining context between them. Ask for a complete feature and watch it create each file:

```p-4
claude "create a user authentication system with login, register, and password reset"
 
# Claude will:
# 1. Create src/auth/login.ts
# 2. Create src/auth/register.ts
# 3. Create src/auth/password-reset.ts
# 4. Update src/routes/index.ts to include new routes
# Each file prompts for approval (unless auto-accept is on)
```

The key advantage: Claude remembers what it created in file 1 when writing file 2. Import paths, type references, and function signatures stay consistent across all files.

## [Requesting Specific Output Formats](#requesting-specific-output-formats)

Claude responds in markdown by default. Control the format through your prompts:

```p-4
# Get structured data
claude "list all API endpoints in this project as a markdown table"
 
# Get code blocks with syntax highlighting
claude "show me the database schema as SQL"
 
# Get step-by-step output
claude "explain the authentication flow as a numbered list"
```

For code output you want to review but not save yet, use [plan mode](/blog/guide/mechanics/planning-modes). Claude analyzes and suggests without writing files.

## [Working with Large Outputs](#working-with-large-outputs)

When Claude generates substantial output, it streams to your terminal. For large codebases or complex operations:

```p-4
# Redirect output to a file for later review
claude "analyze all TODO comments in this project" > todos.md
 
# Pipe to other tools
claude "list dependencies that need updates" | grep "security"
```

## [Common Output Situations](#common-output-situations)

**Claude created the wrong file**: Press `n` to reject, then explain what you actually needed. Claude learns from your feedback in the same session.

**Diff is too long to review**: Press `d` to see the full diff, or ask Claude to break the change into smaller pieces: "make this change in smaller steps."

**Want code without file creation**: Start your prompt with "show me" or "explain" instead of "create" or "add." Claude outputs code blocks without triggering the write workflow.

**Need to undo a change**: Press `Esc` twice to access checkpoints. Claude automatically snapshots before changes so you can rewind.

## [Success Verification](#success-verification)

After accepting changes, verify the output works:

```p-4
# Check the file exists and looks right
cat src/components/Button.tsx
 
# Run your build to catch issues
npm run build
 
# Test the changes
npm test
```

## [Next Steps](#next-steps)

Master the full Claude Code workflow:

- Configure [permission management](/blog/guide/development/permission-management) for smoother accept/reject flow
- Learn [planning modes](/blog/guide/mechanics/planning-modes) to preview changes before committing
- Set up [feedback loops](/blog/guide/development/feedback-loops) for faster iteration
- Explore [context management](/blog/guide/mechanics/context-management) when outputs get complex
- Check [troubleshooting](/blog/guide/troubleshooting) if outputs fail

The key insight: Claude Code is not generating text for you to paste. It is an agent that writes code with your approval. Understanding this workflow transforms how you interact with it.

Last updated on

[Previous

Session Memory](/blog/guide/mechanics/session-memory)[Next

Ralph Wiggum Technique](/blog/guide/mechanics/ralph-wiggum-technique)
