---
title: "Claude Code Best Practices: 5 Agentic Engineering Techniques"
description: "Five Claude Code best practices that top engineers use daily. PRDs, modular rules, commands, context resets, and system evolution patterns."
slug: agentic-engineering-best-practices
date: 2026-03-12
authors:
  - max-ritter
tags:
  - guide
  - development
---

Five Claude Code best practices that top engineers use daily. PRDs, modular rules, commands, context resets, and system evolution patterns.

<!-- truncate -->

Most developers treat Claude Code like a chatbot. They type a vague request, get a vague result, and blame the tool. The developers getting 10x results are doing something different. They've built systems around Claude Code that make every session more productive than the last.

These are the five Claude Code best practices that separate engineers who ship from engineers who struggle. No plugins, no special setup. Just a better operating model for working with agentic AI.

## 1. PRD-First Development

The single biggest mistake in agentic coding is starting without a plan. You open Claude Code, describe a feature in two sentences, and let it run. Twenty minutes later, you're three tangents deep into code that doesn't match what you actually needed.

A Product Requirements Document fixes this. Not a 50-page corporate spec. A lightweight markdown file that takes five minutes to write.

```
# Feature: User Authentication
 
## Mission
 
Add email/password authentication with session management.
 
## In Scope
 
- Sign up, login, logout flows
- Password hashing with bcrypt
- JWT session tokens with 24-hour expiry
- Protected route middleware
 
## Out of Scope
 
- OAuth providers (Phase 2)
- Two-factor authentication (Phase 3)
- Password reset flow (separate task)
 
## Architecture
 
- Auth routes: /api/auth/signup, /api/auth/login, /api/auth/logout
- Middleware: src/middleware/auth.ts
- Database: users table with email, password_hash, created_at
```

Without a PRD, you get context drift. Claude starts making architectural decisions you never discussed. It adds OAuth because "that's what most auth systems include." It builds a password reset flow because it seemed relevant. You spend more time correcting course than building.

With a PRD, every session has guardrails. You tell Claude "read the PRD, then implement the signup flow." It knows exactly what's in scope, what's not, and what patterns to follow. When it finishes one section, you ask "based on the PRD, what should we build next?" and it stays on track.

This applies to existing projects too. For greenfield work, the PRD defines everything you need for your MVP. For brownfield development, the PRD documents what you already have and then specifies what you want to build next. Different starting points, same structure.

The PRD also solves the multi-session problem. Claude Code doesn't carry memory between conversations, but your PRD does. Each new session starts by reading the same document, so you pick up exactly where you left off. For structuring complex multi-session projects, our planning modes guide goes deeper on this.

## 2. Modular Rules Architecture

Most developers make the same mistake with their CLAUDE.md: they put everything in one file. Tech stack, coding conventions, testing rules, deployment procedures, API patterns. One massive wall of instructions.

The problem is context waste. Claude loads your entire CLAUDE.md at session start, and every token in it competes for attention. Your React patterns load when you're debugging a database migration. Your deployment rules load when you're writing unit tests.

A better approach: keep your CLAUDE.md lightweight and point to task-specific docs.

```
# CLAUDE.md
 
## Tech Stack
 
- Next.js 15 with App Router
- TypeScript strict mode
- PostgreSQL with Prisma ORM
- Tailwind CSS
 
## Standards
 
- Use path aliases (@/components, @/lib, @/utils)
- All functions require explicit return types
- Error handling: guard clauses with early returns
- Tests required for business logic
 
## Reference Docs (load when relevant)
 
- Frontend conventions: .claude/skills/react/SKILL.md
- API patterns: .claude/skills/api/SKILL.md
- Database rules: .claude/skills/postgres/SKILL.md
- Deployment: .claude/skills/infra/SKILL.md
```

This is about 15 lines. It covers the universal rules that apply to every task. The detailed knowledge lives in separate files that Claude loads only when the task requires them.

The folder structure looks like this:

```
.claude/
├── skills/
│   ├── react/          # Component patterns, hooks, state
│   ├── api/            # Route conventions, validation, auth
│   ├── postgres/       # Schema patterns, query optimization
│   └── infra/          # Docker, CI/CD, deployment
└── CLAUDE.md           # Lightweight global rules
```

Compare this to the "everything in one file" approach where developers cram 200+ lines of instructions into CLAUDE.md. That file burns context on every session, whether the rules are relevant or not. The modular approach loads domain knowledge on demand. Our [CLAUDE.md mastery guide](/blog/claude-md-mastery) covers the architectural principles behind this pattern.

## 3. Command-ify Everything

If you prompt something twice, it should be a command.

A command in Claude Code is a markdown file in `.claude/commands/` that defines a reusable workflow. When you type `/commit`, Claude reads the command file and follows the instructions. No retyping. No forgetting steps.

Here's what a simple command looks like:

```
# /commit
 
Review all staged changes with `git diff --cached`.
Write a commit message that:
 
- Starts with a verb (add, fix, update, remove)
- Summarizes the WHY, not the WHAT
- Stays under 72 characters
- Uses lowercase
 
Create the commit. Do not push.
```

Save that as `.claude/commands/commit.md` and you never write commit instructions again.

Five starter commands worth building:

- **`/commit`** for consistent, well-formatted git commits
- **`/review`** for code review against your project's standards
- **`/plan`** for generating a structured implementation plan before writing code
- **`/prime`** for loading session context at the start of each conversation
- **`/execute`** for running a plan document that was created in a previous session

Each command takes five minutes to write and saves hundreds of prompts over a project's lifetime. They also enforce consistency. Your commits always follow the same format. Your code reviews always check the same things. The compound effect is real.

For deeper coverage on building reusable instruction packages, see the Claude skills guide.

## 4. The Context Reset

This is the one Claude Code best practice that feels counterintuitive: planning and execution should happen in separate conversations.

Here's the flow:

1. **Plan session**: Research the problem, discuss tradeoffs, explore approaches. Claude outputs a structured plan document (a markdown file saved to your project).
2. **Clear context**: Exit the conversation entirely. Kill the session.
3. **Execute session**: Start fresh. Feed Claude only the plan document from step one. Nothing else.

Why go through this trouble? Because context window degradation is real.

After a long planning conversation, Claude's context is full of exploratory tangents, rejected approaches, and intermediate reasoning that no longer applies. When you then say "okay, now build it," Claude carries all that noise into execution. It might avoid an approach you discussed and discarded, even if your final plan recommends it. It might carry forward assumptions from early in the conversation that you corrected later.

A fresh context with just the plan document means Claude starts execution with a clean mental model. No baggage from the planning phase. No stale assumptions. Just the spec. And because you're not burning tokens on planning history, Claude has more room to reason about implementation details and self-validate its work.

The plan document needs to be comprehensive enough to stand alone. A good plan includes the feature description, user story, architecture context, references to relevant components, and a task-by-task breakdown. If Claude needs to ask clarifying questions during execution, your plan has gaps.

In practice, this looks like:

```
# Planning session
claude "Research auth patterns for our Next.js app and create
an implementation plan. Save it to docs/auth-plan.md"
 
# (exit, start new session)
 
# Execution session
claude "Read docs/auth-plan.md and implement Phase 1"
```

The plan document acts as a handoff between your planning brain and your execution brain. Both sessions are sharper because neither one is trying to do both jobs. For more on why this works and advanced token optimization strategies, see our context management guide.

## 5. System Evolution Mindset

Every bug is a system failure, not a one-time mistake. The difference between good and great agentic engineering is whether you fix the instance or fix the system.

Three real examples:

**Wrong import style.** Claude keeps using relative imports (`../../components/Button`) instead of your path aliases. You could fix each one manually. Or you add a single line to your CLAUDE.md: "Always use @ path aliases for imports, never relative paths." The bug never happens again.

**Forgot to run tests.** You finish a feature, push to CI, and tests fail because Claude never ran them locally. Instead of remembering to prompt "run tests" every time, you update your `/execute` command template to include a mandatory testing step at the end of every implementation. Now every execution session finishes with a test run by default.

**Wrong auth flow.** Claude implements JWT auth with cookies when your project uses bearer tokens in headers. It happened because there's no reference document for your auth patterns. You create `.claude/skills/auth/SKILL.md` with your token format, header conventions, and middleware patterns. Next time anyone (including future you) works on auth, Claude loads the correct patterns automatically.

The pattern is always the same: something goes wrong, you trace it back to a missing instruction or a missing reference, and you add it to your system. Over weeks, your configuration becomes increasingly airtight. Claude makes fewer mistakes because your system has fewer gaps.

A practical way to build this habit: after finishing each feature, ask Claude to review your rules and commands, compare how execution went versus the plan, and suggest what to improve. "Read CLAUDE.md and the commands we used. What rules or process changes would have prevented the issues we hit?" This turns system evolution from an afterthought into a routine step.

This is what separates a Claude Code user from a Claude Code practitioner. The user fixes bugs. The practitioner fixes the system that produced the bug. Our experimentation mindset guide explores this compounding improvement philosophy further.

## Putting It All Together

These five practices aren't independent tips. They form a system.

The PRD scopes your work. Modular rules keep context clean. Commands eliminate repetition. Context resets keep sessions sharp. System evolution makes everything better over time.

None of this requires new tools or expensive setups. It's a set of habits that compound with every project you build. Start with whichever practice addresses your biggest pain point today, and add the rest as you go.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
