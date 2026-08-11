---
title: "Claude Code Team Orchestration: Builder-Validator Patterns"
description: "Pair builder and validator agents using the Claude Code task system. Build-then-validate workflows with dependency chains."
slug: team-orchestration
date: 2026-02-03
authors:
  - max-ritter
tags:
  - guide
  - agents
---

Pair builder and validator agents using the Claude Code task system. Build-then-validate workflows with dependency chains.

<!-- truncate -->

**Problem**: Spawning parallel Claude Code agents is fast, but without structured roles, agents produce inconsistent output that you manually review line by line. You need agents that check each other's work.

> **Looking for native Agent Teams?** Claude Code now has a built-in [Agent Teams feature](/blog/agent-teams) for multi-agent collaboration. This post covers the DIY approach using Task tools, which works without any experimental features enabled.

**Quick Win**: Add this builder-validator chain to your next multi-file task. The validator agent runs read-only after the builder finishes:

```
TaskCreate(subject="Build auth middleware", description="Create JWT validation middleware in src/middleware/auth.ts. Export verifyToken and requireAuth functions.")
TaskCreate(subject="Validate auth middleware", description="Read src/middleware/auth.ts. Verify: exports exist, error handling covers expired/malformed tokens, no hardcoded secrets. Report issues only. Do NOT modify files.")
TaskUpdate(taskId="2", addBlockedBy=["1"])
```

Task 2 won't start until Task 1 completes. The validator reads but never writes. Two agents, one reliable output.

## Why Pairs Beat Solo Agents

Agent fundamentals covers what subagents are and how they work. Task distribution covers spawning parallel agents for speed. [Sub-agent best practices](/blog/sub-agent-best-practices) covers routing decisions. This post covers something different: organizing agents into teams with defined roles.

The problem with solo agents is simple. An agent that builds code can't objectively review its own output. It has the same blind spots that created the bugs in the first place. Pairing a builder with an independent validator catches issues the builder missed because the validator starts fresh, with no context about implementation shortcuts or assumptions.

This mirrors how human teams work. You don't ask the developer who wrote the code to be the sole reviewer. You bring in a second set of eyes.

## The Builder-Validator Pattern

A builder agent writes code. A validator agent reads code. They never overlap.

**Builder prompt** - scoped to creation:

```
You are a builder agent. Your job:
 
1. Read the task description carefully
2. Implement the solution in the specified files
3. Run any relevant tests
4. Mark your task complete
 
Rules:
 
- Only modify files listed in your task
- Do not modify test files (validators handle test verification)
- If you hit a blocker, document it in the task description and mark complete
```

**Validator prompt** - scoped to verification:

```
You are a validator agent. Your job:
 
1. Read all files the builder created or modified
2. Check against the acceptance criteria in the task description
3. Run the test suite
4. Report findings as a new task if issues exist
 
Rules:
 
- Do NOT modify any source files
- Do NOT create new implementation code
- You may only create or update task entries to report issues
- Use Read and Bash (for tests) only - never Edit or Write
```

The key constraint: validators cannot write code. This forces them to surface problems instead of silently "fixing" things in ways that bypass review. When a validator finds issues, it creates a new task that routes back to a builder. You can enforce this at the tool level using custom agent definitions with `disallowedTools`, which prevents validators from accessing Edit or Write tools entirely.

## Dependency Chains for Build-Then-Validate

The `addBlockedBy` parameter in TaskUpdate is what makes this pattern work. Validators wait for builders automatically:

```
// Phase 1: Parallel builders
TaskCreate(subject="Build user API routes", description="Create CRUD endpoints in src/api/users.ts...")
TaskCreate(subject="Build user database schema", description="Create migration in src/db/migrations/...")

// Phase 2: Validators blocked by their builders
TaskCreate(subject="Validate API routes", description="Read src/api/users.ts. Verify REST conventions, error handling, input validation...")
TaskCreate(subject="Validate database schema", description="Read migration files. Verify column types, indexes, foreign keys...")

TaskUpdate(taskId="3", addBlockedBy=["1"])
TaskUpdate(taskId="4", addBlockedBy=["2"])
```

Tasks 1 and 2 run in parallel (different files, no conflicts). Tasks 3 and 4 each wait for their respective builder to finish. You get parallel speed on the build phase and independent validation on each output.

For cross-cutting validation that needs everything built first, add multiple blockers:

```
TaskCreate(subject="Integration validation", description="Verify API routes correctly reference the database schema. Check that all referenced tables and columns exist.")
TaskUpdate(taskId="5", addBlockedBy=["1", "2"])
```

## The Meta-Prompt: Generate Team Plans From Requirements

Instead of manually creating task chains, use a meta-prompt that turns a feature request into a structured team plan. Add this to your [CLAUDE.md configuration](/blog/claude-md-mastery):

```
## Team Plan Generation
 
When I say "team plan: [feature]", generate a task structure:
 
For each component:
 
1. TaskCreate a builder task with specific files and acceptance criteria
2. TaskCreate a validator task scoped to read-only verification
3. TaskUpdate to chain validator behind its builder
 
After all component pairs, add one integration validator blocked by ALL builders.
 
Format each task description with:
 
- **Files**: exact paths to create or read
- **Criteria**: measurable acceptance conditions
- **Constraints**: what this agent must NOT do
```

Then you just say: "team plan: add Stripe webhook handler." Claude generates the full task dependency graph, assigns builder-validator pairs per component, and adds an integration validator at the end. You review the plan, approve it, and the agents execute.

## Resuming Failed Validations

When a validator flags an issue, the cycle continues:

1. Validator creates a fix task describing what's wrong
2. Fix task gets assigned to a builder agent
3. A new validator task is chained behind the fix

```
// Validator found missing error handling
TaskCreate(subject="Fix: add error handling to user API", description="The GET /users/:id endpoint returns 500 on invalid ID format. Add input validation and return 400 for malformed IDs.")
TaskCreate(subject="Re-validate user API error handling", description="Verify GET /users/:id returns 400 for non-UUID strings, 404 for valid UUID not found, 200 for valid existing user.")
TaskUpdate(taskId="7", addBlockedBy=["6"])
```

Each cycle narrows the scope. The first builder handles the full feature. Fix builders handle specific issues. This feedback loop converges toward correct output without you manually debugging.

For complex validations, you can also enforce rules through [hooks](/blog/hooks-guide) that run automated checks on every file modification, catching issues before the validator agent even starts. You can go further by [embedding validation directly into agent definitions](/blog/self-validating-agents) so quality checks travel with the agent as part of its identity.

## Start With One Pair

Don't restructure your entire workflow. Pick your next feature that touches two or more files. Create one builder task and one validator task with `addBlockedBy`. Watch the validator catch something the builder missed.

Once you've seen the pattern work, scale it: parallel builders with chained validators, meta-prompts for automatic plan generation, and integration validators that verify components work together. Design your agent architecture around clear role separation, and let the task system handle coordination. You handle the decisions.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** installs a structured workflow for agent work on top of Claude Code: `/spec` plans the change, runs implementation under TDD, and verifies with an automated reviewer pass. The orchestration loop most agent setups end up writing by hand.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
