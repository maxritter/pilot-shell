---
slug: "planning-modes"
title: "Claude Code Planning Mode: Shift+Tab Twice"
description: "Shift+Tab twice. Claude Code lists all affected files and trade-offs. No code runs until you review and explicitly approve the plan."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 5
keywords: "claude, code, mode, modes, planning, shifttab, twice"
---

Mechanics

# Claude Code Planning Mode: Preview Changes Before Execution

Shift+Tab twice. Claude Code lists all affected files and trade-offs. No code runs until you review and explicitly approve the plan.

Avoid coding disasters before they happen. Planning mode separates thinking from execution, creating better solutions with zero risk.

**Quick Win**: Press `Shift+Tab` twice to enter planning mode right now. Claude will analyze your project but won't touch a single file until you approve.

Planning mode transforms how you approach complex changes. Instead of hoping Claude gets it right the first time, you review the strategy before any code executes.

## [Why Planning Mode Changes Everything](#why-planning-mode-changes-everything)

**The Problem**: Claude Code is incredibly fast at implementation. Sometimes too fast. You ask for a "quick fix" and suddenly 12 files are modified with breaking changes.

**Before Planning Mode**, developers constantly wrote prompts like:

> "Don't code anything yet, just analyze the problem and suggest approaches"

This worked inconsistently. Claude's suggestions varied wildly in format and detail. Sometimes you'd get a one-liner, sometimes a novel.

**With Planning Mode**, Claude delivers structured, predictable analysis every time. You get:

- Multiple numbered options with clear trade-offs
- Complexity assessments for each approach
- Required file changes outlined before implementation
- Consistent formatting that's easy to scan

## [How to Use Planning Mode](#how-to-use-planning-mode)

### [Activation and Control](#activation-and-control)

Enter planning mode with `Shift+Tab` twice. The interface confirms you're in planning mode - Claude can read everything but modify nothing.

Exit planning mode by pressing `Shift+Tab` once more. Claude asks for explicit confirmation before executing any changes.

**Pro Tip**: Plan mode works incredibly fast. Since Claude isn't executing tools or writing files, responses are lightning quick and use fewer tokens.

### [What Claude Can Do in Planning Mode](#what-claude-can-do-in-planning-mode)

**Read-Only Access**:

- File content analysis with Read and LS tools
- Codebase searching with Glob and Grep
- Web research with WebSearch and WebFetch
- Task organization with TodoRead/TodoWrite
- Jupyter notebook viewing with NotebookRead
- Project understanding through comprehensive analysis

**Restricted Actions**:

- No file editing (Edit/MultiEdit blocked)
- No file creation (Write blocked)
- No command execution (Bash blocked)
- No notebook modifications (NotebookEdit blocked)
- No modifications through MCP tools

Claude becomes your strategic advisor, not your implementer.

## [When to Use Planning Mode](#when-to-use-planning-mode)

### [Complex Refactoring Projects](#complex-refactoring-projects)

**Use planning mode when**:

- Refactoring affects multiple files
- Architectural changes impact system design
- You're unsure of the best implementation approach
- Legacy code needs careful modification

**Example Request**:

> "I need to migrate this Express app from CommonJS to ES modules. What's the safest approach?"

Claude analyzes your entire codebase, identifies dependencies, suggests migration strategies, and estimates complexity - all before touching code.

### [Feature Implementation Strategy](#feature-implementation-strategy)

**Use planning mode for**:

- New feature integration into existing systems
- Database schema changes
- API endpoint modifications that affect multiple consumers

**Example Response Pattern**:

```p-4
Option 1: Incremental Migration (Recommended)
- Risk: Low (backward compatible)
- Files affected: 6 core modules
- Benefits: Zero downtime, rollback-friendly

Option 2: Complete Rewrite
- Risk: High (breaking changes)
- Files affected: 15+ modules
- Benefits: Cleaner architecture, better performance
```

## [Common Planning Mode Workflows](#common-planning-mode-workflows)

### [Architecture Review](#architecture-review)

Tell Claude: *"Analyze my current project structure and suggest improvements"*

You'll get detailed analysis of your file organization, dependency patterns, and architectural bottlenecks with specific recommendations.

### [Performance Optimization](#performance-optimization)

Request: *"Review my database queries and suggest optimization strategies"*

Claude examines your queries, identifies N+1 problems, suggests indexing strategies, and compares multiple optimization approaches.

### [Security Assessment](#security-assessment)

Ask: *"Audit my authentication system for security vulnerabilities"*

Claude reviews your auth implementation, identifies potential issues, and suggests remediation strategies without making any changes.

## [Planning Mode Best Practices](#planning-mode-best-practices)

**Start Complex Sessions with Planning**: Before asking Claude to "refactor the entire user system," enter planning mode first. Understand the scope before committing.

**Use for Code Reviews**: Planning mode excels at analyzing existing code and suggesting improvements. Perfect for technical debt assessment.

**Research Unknown Technologies**: When integrating new libraries or frameworks, planning mode helps you understand integration points before implementation.

**Validate Before Executing**: Even for smaller changes, planning mode shows you exactly what Claude intends to modify. No surprises.

## [Integration with Your Workflow](#integration-with-your-workflow)

Planning mode works perfectly with other Claude Code mechanics:

- **[Context Management](/blog/guide/mechanics/context-management)**: Plan mode helps preserve context by encouraging upfront analysis
- **[CLAUDE.md Mastery](/blog/guide/mechanics/claude-md-mastery)**: Use planning to design CLAUDE.md improvements before implementation
- **[Auto-Planning Strategies](/blog/guide/mechanics/auto-planning-strategies)**: Combine with auto-planning for comprehensive project analysis
- **[Terminal Main Thread](/blog/guide/mechanics/terminal-main-thread)**: Planning mode reinforces the terminal-first development approach

## [Next Steps](#next-steps)

Master planning mode by practicing on your current projects:

1. **Enter planning mode** with `Shift+Tab` twice on your next feature request
2. **Review the analysis** - notice the structured, detailed responses
3. **Approve or iterate** - refine the plan before implementation
4. **Execute confidently** - exit planning mode knowing exactly what happens next

Ready to combine planning with advanced strategies? Learn **[Auto-Planning Strategies](/blog/guide/mechanics/auto-planning-strategies)** for systematic project analysis.

Planning mode is the foundation of PRD-first development. Learn how top developers combine this with four other techniques in our [Claude Code best practices](/blog/guide/development/agentic-engineering-best-practices) guide.

Last updated on

[Previous

Terminal Main Thread](/blog/guide/mechanics/terminal-main-thread)[Next

Auto-Planning Strategies](/blog/guide/mechanics/auto-planning-strategies)
