---
sidebar_position: 3
title: /prd
description: Brainstorm vague ideas into Product Requirements Documents through back-and-forth conversation, then hand off to /spec
---

# /prd

`/prd` is the **brainstorming surface** for ideas that aren't yet specs. Use it when you have a vague idea, a problem statement without a solution, or just want to think out loud and have Claude pressure-test directions before committing to a plan. The conversation produces a Product Requirements Document (PRD) you can hand directly to `/spec`.

```bash
$ pilot
> /prd "Add real-time notifications for team updates"
> /prd "We need better onboarding — users drop off after signup"
> /prd "Build an API for third-party integrations"
```

## When to Use

`/prd` and `/spec` chain together: `/prd` defines **what** and **why** when requirements are unclear, `/spec` plans and implements **how** once you know what you're building.

| Situation | Command |
|-----------|---------|
| Idea is vague, requirements unclear | `/prd` first, then `/spec` |
| Only have a problem statement, not a solution | `/prd` |
| Want to brainstorm back-and-forth before deciding | `/prd` |
| Multiple obviously-different shapes could satisfy the request | `/prd` |
| Need to explore trade-offs and alternatives | `/prd` |
| Want research on competitors or prior art | `/prd` with Standard or Deep research |
| Requirements are well-defined | `/spec` directly |
| Small task, no planning needed | Quick mode (just chat) |

## Two Modes Inside One Flow

`/prd` has two distinct conversational modes — divergent for generating ideas, convergent for locking them down:

- **Divergent (Ideate):** Free-form prose. Claude pitches 3-5 distinct directions, you react ("yes that one, but…"), Claude pressure-tests viability and pitches the next round. No structured forms — this is where the riffing happens.
- **Convergent (Clarify → Converge → Write):** Structured `AskUserQuestion` forms with predefined options. Used once the shape is known and you're nailing down details.

The skill picks the mode automatically based on how concrete your input is. A vague problem statement triggers Ideate; a concrete request like "Add Google OAuth" skips it.

## Workflow

```
Understand → Research (optional) → Ideate (if vague) → Clarify → Propose → Converge → Write PRD → Hand off to /spec
```

The entire flow is conversational — one question at a time, no rushing to solutions.

### 1. Understand the Idea

Restates your idea, explores project context with CodeGraph, identifies the core problem, and **scope-checks** — if the request describes multiple independent subsystems (e.g., "build a platform with chat, billing, and analytics"), helps you decompose into multiple PRDs before continuing. Doesn't jump to solutions.

### 2. Research (Optional)

Choose a research tier at the start:

| Tier | What It Does | Best For |
|------|-------------|----------|
| **Quick** | Skip research, go straight to brainstorming | Simple ideas, well-understood domains |
| **Standard** | Web search for competitors, prior art, best practices (5-10 queries) | Most features — quick context gathering |
| **Deep** | Parallel research agents covering multiple angles simultaneously | Complex domains, market research, technical exploration |

Research findings are embedded in the PRD under a dedicated section.

### 2b. Ideate (Optional — Divergent Brainstorming)

When the idea is vague, this step kicks in **before** structured questions. Claude pitches 3-5 distinct directions in plain prose:

> A few directions for "better onboarding":
> - **Reduce surface area** — cut the signup form to email-only, defer the rest
> - **Guided first-run** — keep signup, add a 3-step tour after first login
> - **Pre-fill from context** — infer company/role from email domain
> - **Async setup** — let users start using the product, complete profile later
>
> Which resonate, or where am I off?

You react in your own words. Claude pressure-tests your reaction (where does it break? what does it cost?), then pitches the next round shaped by your answer. Usually 1-3 rounds — the signal to converge is when you start saying "yes, and…" instead of "no, but…".

This step is **skipped automatically** when your input is concrete (e.g., "Add Google OAuth" — Claude won't pitch alternatives you didn't ask for).

### 3. Ask Clarifying Questions

Switches to structured `AskUserQuestion` forms. One question at a time, with 2-4 predefined options each. Focuses on purpose, users, constraints, success criteria, and scope boundaries. Challenges assumptions and surfaces trade-offs. Typically 3-6 questions.

### 4. Propose Approaches

Proposes 2-3 implementation approaches with clear trade-offs. Leads with a recommendation and explains why. Gets your choice before proceeding.

### 5. Converge on Scope

States what's in scope, what's explicitly out, identifies core user flows step-by-step, and notes technical context for `/spec`.

### 6. Write PRD

Saves a PRD to `docs/prd/YYYY-MM-DD-<slug>.md` with structured metadata and these sections:

| Section | Purpose |
|---------|---------|
| **Problem Statement** | What problem, for whom, why now — the north star |
| **Core User Flows** | Step-by-step from the user's perspective |
| **Scope** | In scope / explicitly out of scope with reasoning |
| **Technical Context** | Lightweight notes for the implementer — constraints, integration points |
| **Key Decisions** | Trade-offs made during the conversation with reasoning |
| **Research Findings** | Embedded research results (when research tier was Standard or Deep) |

After writing, Claude runs a 4-point self-review (placeholders, consistency, scope, ambiguity), then **asks you to open the file in your editor and read it through** before you confirm. If you request changes, Claude edits the specific sections in place — it doesn't rewrite the whole document, so you don't lose your editor scroll position or have to re-read everything.

### 7. Hand Off to /spec

After you confirm the PRD, asks whether to hand off to `/spec` immediately or save for later. If yes, `/spec` is invoked automatically with a reference to the PRD.

## PRD Output

PRDs are saved to `docs/prd/` — separate from implementation plans in `docs/plans/`. This keeps requirements documents (the "what" and "why") distinct from technical specs (the "how").

Each PRD includes structured metadata: Created date, Author, Category, Status (Draft/Final), and Research tier used.

PRDs are visible in the **Pilot Console** under the **Requirements** tab, where you can browse, annotate, share, and archive them — the same experience as the Specifications tab.

## Comparison with /spec

| Aspect | /prd | /spec |
|--------|------|-------|
| **Purpose** | Brainstorm and define requirements | Plan and implement |
| **Output** | PRD (what and why) | Implementation plan + code (how) |
| **Style** | Conversational, divergent then convergent | Structured, technical |
| **Best fit** | Vague ideas, problem statements, "I'm thinking…" | Concrete requirements, "I need to build X" |
| **Research** | Optional (Quick/Standard/Deep) | No research phase |
| **Questions** | One at a time, exploratory | Batched, focused on design |
| **When** | Idea stage, unclear requirements | Ready to build |
| **Duration** | 5-15 minutes of conversation | Hours of automated work |
