---
slug: "claude-md-mastery"
title: "CLAUDE.md Mastery: Your AI's Operating System"
description: "CLAUDE.md is your AI's operating system, not documentation. Define orchestration, conversation management, and delegation patterns that work."
date: "2025-12-07"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 15
keywords: "ais, claude, claudemd, mastery, md, operating, system"
---

Mechanics

# CLAUDE.md Mastery: Your AI's Operating System

CLAUDE.md is your AI's operating system, not documentation. Define orchestration, conversation management, and delegation patterns that work.

Most guidance about CLAUDE.md gets it wrong. The common advice treats CLAUDE.md as project documentation - a place to describe your tech stack, list commands, and explain directory structure. This fundamentally misunderstands what CLAUDE.md should be.

**CLAUDE.md is your central AI's operating system.** It defines how Claude operates, how conversations are managed, and how work gets delegated. Project-specific knowledge belongs in skills - modular, dynamically-loaded components that activate when relevant.

## [Two Paradigms: Onboarding vs. Orchestration](#two-paradigms-onboarding-vs-orchestration)

### [The Inferior Approach: Project Onboarding](#the-inferior-approach-project-onboarding)

The conventional wisdom says CLAUDE.md should "onboard Claude to your codebase" by answering WHAT (tech stack), WHY (project purpose), and HOW (commands to run). Some even recommend keeping files under 60 lines.

This approach has problems:

**Priority saturation**: CLAUDE.md content receives **high priority** in Claude's context window - the model treats these instructions as authoritative. When you stuff everything into one file, all of it competes for that elevated attention. Your React patterns fight with your API guidelines, even when you're working on database migrations. High priority everywhere means priority nowhere.

**Context waste**: If your CLAUDE.md describes React patterns for a React project, that context loads every session - even when you're working on database migrations or deployment scripts.

**No behavioral control**: Listing your tech stack doesn't tell Claude how to approach problems, when to delegate, or how to manage complex multi-step work.

**Repetition across projects**: Every new project needs a new CLAUDE.md explaining similar patterns, leading to inconsistent AI behavior across your work.

**Static knowledge**: Project documentation becomes outdated. Your API patterns from six months ago may not reflect current best practices.

The onboarding approach treats Claude as a contractor who needs to be briefed on each job. The orchestration approach treats Claude as an intelligent system that needs operational parameters.

### [The Superior Approach: Orchestration Layer](#the-superior-approach-orchestration-layer)

CLAUDE.md should define:

1. **Operational workflows** - The sequence Claude follows for every request
2. **Context management strategy** - How to conserve and allocate context effectively
3. **Delegation patterns** - When to use sub-agents vs. handle directly
4. **Quality standards** - Coding practices, error handling, security requirements
5. **Coordination protocols** - How to manage parallel vs. sequential work

Project-specific knowledge - your tech stack, patterns, conventions - lives in **skills** that load dynamically when relevant. This separation provides:

- **Consistent AI behavior** across all projects
- **Efficient context usage** - domain knowledge loads only when needed
- **Portable expertise** - skills transfer between projects
- **Maintainable knowledge** - update a skill once, benefit everywhere

## [Structuring Your CLAUDE.md](#structuring-your-claudemd)

### [Core Principles Section](#core-principles-section)

Start with the fundamental behaviors you want from your AI. These should apply universally, regardless of what project or task you're working on.

```p-4
## Core Principles
 
### Skills-First Workflow
 
**EVERY user request follows this sequence:**
 
Request → Load Skills → Gather Context → Execute
 
Skills contain critical workflows and protocols not in base context.
Loading them first prevents missing key instructions.
 
### Context Management Strategy
 
**Central AI should conserve context to extend pre-compaction capacity**:
 
- Delegate file explorations and low-lift tasks to sub-agents
- Reserve context for coordination, user communication, and strategic decisions
- For straightforward tasks with clear scope: skip heavy orchestration, execute directly
 
**Sub-agents should maximize context collection**:
 
- Sub-agent context windows are temporary
- After execution, unused capacity = wasted opportunity
- Instruct sub-agents to read all relevant files, load skills, and gather examples
```

This establishes behavioral patterns that govern every interaction - not project facts that may or may not be relevant.

### [Routing and Delegation Logic](#routing-and-delegation-logic)

Define when Claude should handle work directly versus delegate to specialists:

```p-4
### Routing Decision
 
**Direct Execution**:
 
- Simple/bounded task with clear scope
- Single-component changes
- Quick fixes and trivial modifications
 
**Sub-Agent Delegation**:
 
- Complex/multi-phase implementations
- Tasks requiring specialized domain expertise
- Work that benefits from isolated context
 
**Master Orchestrator**:
 
- Ambiguous requirements needing research
- Architectural decisions with wide impact
- Multi-day features requiring session management
```

This routing logic ensures Claude makes intelligent decisions about work distribution rather than either doing everything itself or delegating unnecessarily.

### [Operational Protocols](#operational-protocols)

Define how Claude should coordinate work, especially when parallelism is possible:

```p-4
## Operational Protocols
 
### Agent Coordination
 
**Parallel** (REQUIRED when applicable):
 
- Multiple Task tool invocations in single message
- Independent tasks execute simultaneously
- Bash commands run in parallel
 
**Sequential** (ENFORCE for dependencies):
 
- Database → API → Frontend
- Research → Planning → Implementation
- Implementation → Testing → Security
 
### Quality Self-Checks
 
Before finalizing code, verify:
 
- All inputs have validation
- Authentication/authorization checks exist
- All external calls have error handling
- Import paths verified against existing codebase examples
```

### [Coding Standards and Practices](#coding-standards-and-practices)

Include universal coding principles that should govern all work:

```p-4
## Coding Best Practices
 
**Priority Order** (when trade-offs arise):
Correctness > Maintainability > Performance > Brevity
 
### Task Complexity Assessment
 
Before starting, classify:
 
- **Trivial** (single file, obvious fix) → execute directly
- **Moderate** (2-5 files, clear scope) → brief planning then execute
- **Complex** (architectural impact, ambiguous requirements) → full research first
 
Match effort to complexity. Don't over-engineer trivial tasks or under-plan complex ones.
 
### Integration Safety
 
Before modifying any feature:
 
- Identify all downstream consumers using codebase search
- Validate changes against all consumers
- Test integration points to prevent breakage
```

## [The Rules Directory: Modular Instructions](#the-rules-directory-modular-instructions)

As of Claude Code v2.0.64, you have another option for organizing instructions: the `.claude/rules/` directory. This solves the priority saturation problem by letting you distribute high-priority instructions across targeted files.

**Key insight from Anthropic**: Rules files load with the **same high priority as CLAUDE.md**. The difference is you can scope when that priority applies using path targeting.

### [When Rules Beat CLAUDE.md](#when-rules-beat-claudemd)

The rules directory shines when your instructions have **domain boundaries**:

```p-4
.claude/rules/
├── api-guidelines.md     # Only relevant for API work
├── react-patterns.md     # Only relevant for frontend
├── testing-rules.md      # Only relevant for test files
└── security-rules.md     # Only relevant for auth/payment code
```

Each file loads as project memory, but you can target rules to specific file patterns:

```p-4
---
paths: src/api/**/*.ts
---
 
# API Development Rules
 
- All endpoints must validate input with Zod
- Return consistent error shapes
```

This rule **only activates when Claude touches API files**. Your API guidelines stay out of the way during frontend work.

### [The Instruction Priority Hierarchy](#the-instruction-priority-hierarchy)

Think of it as layers combining priority level with loading behavior:

| Layer | Priority | Contains | Loads |
| --- | --- | --- | --- |
| **CLAUDE.md** | High | Operational workflows, routing logic | Always |
| **Rules Directory** | High | Domain-specific guidelines | Always (filtered by path) |
| **Skills** | Medium | Reusable procedures, cross-project expertise | On-demand |
| **File contents** | Standard | Code, documentation | When read |

**Use CLAUDE.md** for universal behavior that deserves constant high priority. **Use rules** for domain-specific instructions - they get high priority only when relevant files are in scope. **Use skills** for portable expertise - medium priority, loaded on-demand.

For a deep dive into path-targeted rules and migration strategies, see the [Rules Directory guide](/blog/guide/mechanics/rules-directory).

### [Loading CLAUDE.md from Additional Directories](#loading-claudemd-from-additional-directories)

As of Claude Code v2.1.20, you can load CLAUDE.md files from directories outside your current project. This is particularly useful for monorepos, shared team standards, or multi-project workflows.

**How it works:**

```p-4
# Enable the feature and specify additional directories
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-standards
 
# Multiple directories work too
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config ../team-rules
```

When enabled, Claude loads from each additional directory:

- `CLAUDE.md` files
- `.claude/CLAUDE.md` files
- `.claude/rules/*.md` files

**Why this matters vs. verbally referencing files:**

| Approach | Loads Automatically | Persists Across Sessions | Context Efficient |
| --- | --- | --- | --- |
| `--add-dir` with env var | Yes | Yes | Yes (system memory) |
| "Read that CLAUDE.md" | No | No | No (costs tokens each time) |

The `--add-dir` approach treats external CLAUDE.md files as proper system memory rather than conversation context. They load automatically, persist across sessions, and respect the priority hierarchy.

**Practical use cases:**

**Monorepo with shared standards:**

```p-4
company/
├── shared-standards/
│   └── CLAUDE.md          # Company coding guidelines
├── apps/
│   ├── web/
│   │   └── CLAUDE.md      # Web-specific rules
│   └── api/
│       └── CLAUDE.md      # API-specific rules
```

From the `web/` directory:

```p-4
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../../shared-standards
```

**Cross-project consistency:** Keep your personal development standards in a central location and load them into any project without duplicating files.

**Team onboarding:** New team members can point to a shared directory containing team conventions, eliminating the "every project has slightly different CLAUDE.md" problem.

**Updated priority hierarchy:**

| Layer | Priority | Contains | Loads |
| --- | --- | --- | --- |
| **CLAUDE.md** | High | Operational workflows, routing logic | Always |
| **Rules Directory** | High | Domain-specific guidelines | Always (filtered by path) |
| **Additional Directories** | High | Shared/external CLAUDE.md files | When `--add-dir` specified |
| **Skills** | Medium | Reusable procedures, cross-project expertise | On-demand |
| **File contents** | Standard | Code, documentation | When read |

**Note:** The environment variable `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` must be set for this feature to work. The `--add-dir` flag alone only grants file access to those directories without loading their CLAUDE.md files.

### [@import Syntax: A Simpler Alternative](#import-syntax-a-simpler-alternative)

While `--add-dir` is powerful for loading entire external directories, there's a lighter-weight option for pulling in specific files. CLAUDE.md files support `@path/to/import` syntax for composable memory:

```p-4
See @README for project overview and @package.json for available npm commands.
 
# Standards
 
- coding guidelines @docs/coding-standards.md
- git workflow @docs/git-instructions.md
```

Both relative and absolute paths work. Relative paths resolve from the file containing the import, not from your working directory.

**How this differs from `--add-dir`:**

| Approach | Granularity | Loads | Requires env var |
| --- | --- | --- | --- |
| `@import` | Individual files | Specified files only | No |
| `--add-dir` | Entire directory | All CLAUDE.md + rules | Yes |

**First-time approval**: When Claude Code encounters imports for the first time in a project, it shows an approval dialog listing the specific files. This is a one-time decision per project. Once declined, the dialog does not resurface and those imports remain disabled.

**Recursive imports**: Imported files can themselves import additional files, with a max-depth of 5 hops. This lets you build layered instruction sets:

```p-4
# CLAUDE.md imports standards.md
 
@.claude/standards.md
 
# standards.md imports sub-files
 
@.claude/standards/api.md
@.claude/standards/testing.md
```

Imports are not evaluated inside markdown code spans or code blocks, so code examples containing `@path` references won't trigger unintended loads.

### [CLAUDE.local.md: Personal Project Preferences](#claudelocalmd-personal-project-preferences)

For project-specific preferences that should not be shared with your team, use `CLAUDE.local.md`. This file is automatically added to `.gitignore` and loads alongside `CLAUDE.md` with the same priority.

This is the right place for:

- Your local dev server URLs and sandbox endpoints
- Personal test data preferences
- Branch naming conventions you prefer
- Editor and tool configurations specific to your setup

**Git worktree tip**: Since `CLAUDE.local.md` only exists in one worktree, use a home-directory import to share personal instructions across all worktrees:

```p-4
# CLAUDE.local.md
 
@~/.claude/my-project-instructions.md
```

### [Viewing Loaded Memory with /memory](#viewing-loaded-memory-with-memory)

Use the `/memory` command to see what files are currently loaded into Claude's context and to open any memory file in your system editor. This is essential for debugging when instructions appear to be missing or when you need to verify that imports and rules are loading correctly.

## [Skills: Where Domain Knowledge Lives](#skills-where-domain-knowledge-lives)

Skills are the counterpart to your CLAUDE.md operating system. While CLAUDE.md defines **how** Claude operates, skills provide **what** Claude knows about specific domains.

### [The Skills Architecture](#the-skills-architecture)

Anthropic describes the distinction clearly: "Projects say 'here's what you need to know.' Skills say 'here's how to do things.'"

Skills use progressive disclosure:

1. **Metadata loads first** (~100 tokens) - enough to know when the skill is relevant
2. **Full instructions load when needed** (<5k tokens)
3. **Bundled files/scripts load only as required**

This architecture means you can have dozens of skills available without overwhelming context. Claude accesses exactly what it needs, when it needs it.

### [What Belongs in Skills](#what-belongs-in-skills)

**Technology patterns**:

- Framework conventions (React patterns, API design)
- Database operations and migrations
- Testing strategies and utilities

**Domain workflows**:

- Payment processing integrations
- Authentication implementations
- Deployment procedures

**Project-specific context**:

- Codebase navigation guides
- Architecture documentation
- Team conventions

### [Example: Separating Concerns](#example-separating-concerns)

Instead of putting this in CLAUDE.md:

```p-4
## About This Project
 
FastAPI REST API for user authentication.
Uses SQLAlchemy for database operations.
 
## Commands
 
uvicorn app.main:app --reload
pytest tests/ -v
```

Create a `backend-api` skill:

```p-4
# Backend API Development Skill
 
## Framework
 
FastAPI with SQLAlchemy ORM, Pydantic validation.
 
## Development Commands
 
- `uvicorn app.main:app --reload` - Start dev server
- `pytest tests/ -v` - Run test suite
- `alembic upgrade head` - Apply migrations
 
## Patterns
 
[Detailed patterns, examples, conventions...]
```

Your CLAUDE.md references the skill system:

```p-4
### Key Skills
 
`backend-api`, `frontend-react`, `database-ops`, `deployment`
 
Load relevant skills before beginning domain-specific work.
```

Now the backend knowledge loads only during backend work, preserving context for everything else.

## [The Line Count Debate](#the-line-count-debate)

Some popular guidance recommends keeping CLAUDE.md under 60 lines, claiming Claude "ignores" longer files. This advice misunderstands how Claude processes context.

**The reality**: Anthropic recommends skill files be 500 lines maximum. If a dynamically-loaded skill can effectively use 500 lines, your always-loaded CLAUDE.md can certainly use 200-400 lines for comprehensive operational instructions.

The key isn't brevity - it's **relevance**. A 60-line file full of project-specific details that don't apply to every task wastes more effective context than a 300-line file of universally-applicable operational protocols.

**The sweet spot is 200-400 lines** of:

- Operational workflows (always relevant)
- Routing logic (always relevant)
- Quality standards (always relevant)
- Coordination protocols (always relevant)

Not 60 lines of project facts that may or may not matter for any given task.

## [Framework Evolution](#framework-evolution)

Your CLAUDE.md should include instructions for its own improvement:

```p-4
### Framework Improvement
 
**Recognize patterns that warrant updates:**
 
**Update existing skill when**:
 
- A workaround was needed for something the skill should have covered
- New library version changes established patterns
- A better approach was discovered during implementation
 
**Create new skill when**:
 
- Same domain-specific context needed across 2+ sessions
- A payment processor, API, or tool integration was figured out
- Reusable patterns emerged that will apply to future projects
 
**Action**: Prompt user with: "This [pattern/workaround/integration] seems
reusable. Should I update [skill] or create a new skill to capture this?"
```

This creates a self-improving system where Claude actively identifies opportunities to enhance the framework.

## [Why This Approach Works](#why-this-approach-works)

### [Multi-Agent Orchestration](#multi-agent-orchestration)

Modern Claude Code development increasingly involves sub-agents - specialized instances handling discrete tasks. Your CLAUDE.md defines how the central AI orchestrates these agents.

As Anthropic notes, Opus 4.5 is explicitly trained to manage teams of sub-agents. Your CLAUDE.md should leverage this by defining:

- When to delegate vs. handle directly
- How to construct sub-agent prompts
- How sub-agent results flow back to the main conversation

### [Context Economics](#context-economics)

Context is finite. Every token of project-specific documentation in CLAUDE.md is a token unavailable for actual work. The orchestration approach optimizes context allocation:

- **CLAUDE.md**: Operational instructions (always needed)
- **Skills**: Domain knowledge (loaded on demand)
- **Sub-agents**: Fresh context for specialized work

### [Consistency Across Projects](#consistency-across-projects)

When CLAUDE.md defines behavior rather than project facts, you get consistent AI assistance regardless of what you're working on. The same routing logic, quality standards, and coordination patterns apply whether you're building a React app or a Python CLI tool.

## [Quick Reference](#quick-reference)

```p-4
Request → Load Skills → Route Decision → Execute
```

**Routing**:

- Simple/bounded task → Direct execution
- Complex/multi-phase → Sub-agent delegation or session management

**CLAUDE.md Contains**:

- Operational workflows
- Context management strategy
- Routing and delegation logic
- Quality standards
- Coordination protocols

**Skills Contain**:

- Tech stack specifics
- Framework patterns
- Project conventions
- Domain workflows

## [Next Steps](#next-steps)

1. **Audit your current CLAUDE.md**: Is it project documentation or operational instructions?
2. **Extract domain knowledge to skills**: Move tech stack, patterns, and conventions out of CLAUDE.md
3. **Define your operational workflows**: How should Claude approach every request?
4. **Establish routing logic**: When should Claude delegate vs. handle directly?
5. **Set quality standards**: What practices should govern all work?

**Remember**: CLAUDE.md isn't documentation for Claude to read - it's an operating system for Claude to run. Define behavior, delegate knowledge to skills, and build a system that improves itself over time.

For a complete system that builds on these principles, see our guide to [5 Claude Code best practices](/blog/guide/development/agentic-engineering-best-practices) that separate top developers.

Last updated on

[Previous

Dynamic Starting Context](/blog/guide/mechanics/claude-code-session-context)[Next

Rules Directory](/blog/guide/mechanics/rules-directory)
