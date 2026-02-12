---
slug: "robots-first-engineering"
title: "Claude Code Robots-First: Design Systems for AI"
description: "The future of software engineering is robots-first. Learn to build fully autonomous AI development systems designed for AI agents, not humans."
date: "2026-01-14"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 8
keywords: "ai, claude, code, design, engineering, first, robots, robotsfirst, systems"
---

Mechanics

# Robots-First Engineering: Building Software Systems Designed for AI Agents, Not Humans

The future of software engineering is robots-first. Learn to build fully autonomous AI development systems designed for AI agents, not humans.

Everything in software engineering was designed for humans. File systems. Terminal interfaces. JSON. Git workflows. Code review processes.

What happens when we redesign for machines?

This is robots-first engineering. And it's where autonomous software development is heading.

## [Development vs Engineering](#development-vs-engineering)

Here's a distinction that changes everything:

**Software development** is now automated. Writing code, running tests, committing changes. Agents do this. The cost is approximately $10/hour. It runs 24/7. It doesn't get tired.

**Software engineering** is designing the systems that keep automated development reliable. Building rails. Managing failure domains. Creating verification loops. Engineering back-pressure.

The job has shifted. You're no longer carrying cargo by hand onto the ship. The shipping containers are here. Your job is to operate the locomotive and keep it on the tracks.

This is the mindset shift that separates engineers who thrive with AI from those who struggle.

## [The Screwdriver and the Jackhammer](#the-screwdriver-and-the-jackhammer)

There's a progression to autonomous engineering:

**The Screwdriver**: Manual fundamentals. You shape specs by hand. You control context carefully. You steer search and linkage. You learn how to keep the system on rails before turning it loose.

**The Jackhammer**: Full-power automation. Ralph loops running unattended. Heavy orchestration. Multiple agents in parallel. Overnight feature builds.

The mistake most engineers make: reaching for the jackhammer before mastering the screwdriver.

If you go straight for full automation without understanding the fundamentals, you'll get terrible results. The screwdriver teaches you what the jackhammer needs to succeed.

Start manual. Understand why things work. Then graduate to power tools.

## [Loom: An Environment for Agents](#loom-an-environment-for-agents)

Loom represents the next evolution: a self-evolving software environment designed around agents rather than humans.

The design principle is radical. For every system component, ask:

1. Was this designed for humans?
2. If yes, can it be cut?
3. If cut, what value was lost and how is it replaced?

Examples of human-first assumptions being questioned:

- **Unix user space and TTY conventions** - Do agents need terminal interfaces?
- **Common agile/process practices** - Do agents need sprint planning?
- **JSON as data format** - Is JSON optimal for tokenization?
- **Code review workflows** - Can verification replace review?

Loom's architecture includes:

- Code hosting (GitHub-like, but agent-optimized)
- Source control using JJ (designed for machine workflows)
- Codespaces-like remote environments
- Multi-LLM "alloying" (mixing providers)
- Actor/pub-sub messaging patterns
- Erlang/OTP-style chaining

The key insight: **loops composed into chains**. Loops on loops on loops. Each small, focused. Together, a reactive system.

## [Context Windows Are Arrays](#context-windows-are-arrays)

A fundamental principle for robots-first thinking:

The context window is an array. The less you use in that array, the less the window needs to slide, the better outcomes you get.

More context means:

- More sliding
- Earlier compaction
- Compaction is lossy
- Loss drops critical anchors
- Drift follows

This is why [Ralph loops](/blog/guide/mechanics/ralph-wiggum-technique) work. They're designed to deterministically manage the array. Keep it focused. Avoid compaction. Preserve the pin.

The "pin" is your specification - the stable reference point that prevents invention. Every loop iteration references it. Without the pin, agents drift into hallucination.

## [Specs as Lookup Tables](#specs-as-lookup-tables)

Robots-first specs aren't just documentation. They're lookup tables optimized for agent search.

A well-designed spec includes:

```p-4
## User Authentication
 
**Also known as**: login, sign-in, auth, session management, identity
 
**Related files**: src/auth/, src/middleware/session.ts
 
**Key patterns**: JWT tokens, refresh rotation, secure cookies
 
**What NOT to do**: Don't implement custom crypto, don't store passwords in plain text
```

The "also known as" section improves search hit rates. When an agent searches for "login," it finds the auth spec. More descriptors mean more hits. More hits mean less invention.

The spec becomes a frame of reference for all functionality. Agents look up existing patterns instead of inventing new ones.

## [Linkage Over Fancy Formats](#linkage-over-fancy-formats)

Many engineers over-engineer their implementation plans. Complex JSON schemas. Nested task hierarchies. Fancy formatting.

The robots-first approach: **strong linkage beats fancy formats**.

What works:

- Bullet points with explicit references
- Cite the exact spec section
- Point to specific file locations
- Reference specific hunks (the read tool works in hunks)

```p-4
## Implementation Plan
 
- [ ] Add JWT validation middleware
 
  - Spec: auth-spec.md#token-validation
  - File: src/middleware/auth.ts (lines 45-60)
  - Pattern: Follow existing rate-limit middleware structure
 
- [ ] Create refresh token endpoint
  - Spec: auth-spec.md#refresh-flow
  - File: src/routes/auth/refresh.ts (new file)
  - Pattern: Match existing /auth/login endpoint structure
```

The agent can now search precisely. It finds the right hunks. It follows existing patterns. It doesn't invent.

## [The Robots-First Stack](#the-robots-first-stack)

Here's where it gets radical. If you control the entire stack, you can optimize for machines:

**Serialization**: JSON is not optimal for tokenization. Every quote, bracket, and comma consumes tokens. Binary formats or agent-optimized text formats could be dramatically more efficient.

**User Space**: Why do agents need Unix user space conventions? TTY was designed for human terminals. Agents don't need terminal emulation.

**Garbage Collection**: What does memory management mean when your "process" is a stateless API call? The assumptions change completely.

**Message Passing**: Erlang/OTP principles become relevant again. Actors. Supervision trees. Let-it-crash philosophy. These patterns suit agent orchestration.

Engineers who control their stack can:

- Optimize tokenization
- Reduce costs dramatically
- Build faster reactive systems
- Operate cheaper than competitors

This is competitive advantage territory.

## [Weavers: Fully Autonomous Agents](#weavers-fully-autonomous-agents)

The destination of robots-first engineering: **Weavers**.

Weavers are autonomous agents that:

- Ship code behind feature flags
- Deploy without code review
- Observe product analytics
- Decide if changes fixed errors
- Decide whether to optimize further
- Iterate automatically

No human in the loop. Full autonomy.

This sounds terrifying. That's the correct initial reaction. But consider:

Every objection you have is an engineering problem. "What if it breaks production?" Engineer rollback mechanisms. "What if it makes bad decisions?" Engineer verification loops. "What if it goes off-rails?" Engineer back-pressure.

The job of software engineering becomes: **engineer away the concerns**.

Listen to your objections. Then build systems that address them. That's the new job.

## [Back-Pressure Engineering](#back-pressure-engineering)

Autonomous loops create many failure domains. Your engineering work becomes building rails:

- Add constraints to specs
- Tighten plan linkage
- Improve search guidance
- Increase gating (tests, linting, formatting, security checks)

When outcomes are poor, remediation is another loop:

- Refactor loop
- Convention loop
- Security loop
- i18n loop

Back-pressure keeps the generative function on the rails. The locomotive stays on track because you've engineered the track.

## [The Scaling Path](#the-scaling-path)

Robots-first engineering scales through composition:

**Level 1: Manual Fundamentals**

- Generate specs via conversation
- Edit and tighten constraints
- Keep context minimal
- Operate attended

**Level 2: Unattended Looping**

- `while true` style runs
- Single objective per iteration
- Automated tests + commit/push
- Checkpointed state

**Level 3: Multi-Loop Orchestration**

- Multiple loops running
- Reactive chaining as needed
- Actor/pub-sub patterns

**Level 4: Autonomous Product Systems**

- Weavers shipping features
- Analytics-driven decisions
- No code review required
- Full product autonomy

Each level builds on the previous. You can't skip to Level 4 without mastering Levels 1-3.

## [The Mindset](#the-mindset)

Robots-first engineering requires a fundamental shift:

**Old mindset**: "How do I write this code?"
**New mindset**: "How do I design systems that write this code reliably?"

**Old mindset**: "How do I review this PR?"
**New mindset**: "How do I build verification that makes review unnecessary?"

**Old mindset**: "How do I debug this issue?"
**New mindset**: "How do I engineer feedback loops that prevent this class of issues?"

You're not coding anymore. You're designing autonomous systems. You're a locomotive engineer, not a cargo carrier.

## [Getting Started](#getting-started)

You don't need to build Loom to think robots-first. Start with questions:

1. **What human assumptions am I encoding?** Look at your workflows. Which steps exist because humans needed them?
2. **What could be a lookup table?** Your specs, your patterns, your conventions. Can they be structured for agent search?
3. **Where is linkage weak?** Your plans probably reference things vaguely. Can you add explicit file paths, line numbers, hunks?
4. **What's my back-pressure strategy?** When agents go wrong, how do you correct them? Build those mechanisms before you need them.
5. **What would full autonomy require?** Imagine removing yourself from the loop. What breaks? Those are your engineering priorities.

## [The Future](#the-future)

This is 2026. Strap yourself in.

The gap between teams that can run reliable autonomous loops and teams that can't is widening. The economics are stark: $10/hour for automated development versus $100+/hour for human developers.

Teams that master robots-first engineering will ship at fundamentally different rates. They'll operate cheaper. They'll iterate faster. They'll compound improvements automatically.

The developers clinging to human-first workflows will fall behind. Not because they're bad engineers. Because they're optimizing for the wrong constraints.

Software engineering has changed. Again. It will change again.

The engineers who thrive are the ones who see each change as an opportunity to redesign from first principles. That's always been true. It's just more obvious now.

Start with the screwdriver. Master the fundamentals. Then reach for the jackhammer.

The locomotive is waiting.

## [Related Reading](#related-reading)

- [Ralph Wiggum Technique](/blog/guide/mechanics/ralph-wiggum-technique) - The foundation for autonomous loops
- [Thread-Based Engineering](/blog/guide/mechanics/thread-based-engineering) - Framework for scaling agent work
- [Autonomous Agent Loops](/blog/guide/mechanics/autonomous-agent-loops) - Combining Ralph and threads
- [Feedback Loops](/blog/guide/development/feedback-loops) - Verification patterns
- [Context Engineering](/blog/guide/mechanics/context-engineering) - Managing the array

Last updated on

[Previous

Autonomous Agent Loops](/blog/guide/mechanics/autonomous-agent-loops)[Next

Agentic Practices](/blog/guide/development/agentic-engineering-best-practices)
