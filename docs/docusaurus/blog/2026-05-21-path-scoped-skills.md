---
title: "Path-Scoped Claude Code Skills"
description: "Skills can be scoped to file paths. Workflows load only where they apply. Here is how, plus the rules vs workflows mental model."
slug: path-scoped-skills
date: 2026-05-21
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Skills can be scoped to file paths. Workflows load only where they apply. Here is how, plus the rules vs workflows mental model.

<!-- truncate -->

You have 20 skills installed. Claude is working in `services/billing`. Eighteen of those skills have nothing to do with billing, but their descriptions still get listed at session start, eating tokens you do not get back. That is the problem path-scoped skills in Claude Code were designed to solve: bind a skill to a directory glob so Claude only sees it when the work touches that path.

This post covers the `paths:` frontmatter parameter (verified against Cole Medin's [helpline reference repo](https://github.com/coleam00/helpline)), the rules-vs-workflows mental model, and the scoping strategies that scale on a monorepo. It is a [Claude Code skills](/blog/claude-skills-guide) deep dive. The [AI Layer pillar](/blog/the-ai-layer) puts skills in context with the other six harness components.

## Rules vs. Workflows: The Mental Model

The single most common skill mistake is putting workflows in CLAUDE.md or rules in skills. Anthropic's recent guidance makes the split explicit. Cole's framing is the cleanest version:

- **CLAUDE.md holds rules.** Conventions that must hold every time Claude touches the relevant area. Loaded automatically, always in context.
- **Skills hold workflows.** Multi-step procedures that fire only on specific task types. Loaded on demand.

Both can be scoped by path. The question is which you reach for. The decision tree:

1. Does this need to be true every time Claude reads or writes in this folder, regardless of what the user asked? It is a rule. Put it in a [layered CLAUDE.md](/blog/subdirectory-claude-md).
2. Does this only matter when the user is doing a specific kind of task (adding a route, reviewing money code, writing a migration)? It is a workflow. Put it in a skill.
3. Is it both? Split it. The convention goes in CLAUDE.md, the procedure goes in a skill, and the skill references the CLAUDE.md rule.

Get this wrong and you pay twice. Rules in skills means Claude misses the rule on the 80% of tasks where the skill never activates. Workflows in CLAUDE.md means the procedure burns tokens in every session even when irrelevant, the bloat problem the [skill listing budget](/blog/skill-listing-budget) was added to police.

## How Path-Scoped Skills in Claude Code Work: The `paths:` Parameter

Path scoping lives in the YAML frontmatter of any `SKILL.md`. The exact key is `paths:` (plural). It accepts either a single glob string or a YAML list of globs.

```
---
name: billing-money-rules
description: >-
  Use when creating or editing code under services/billing. Enforces money rules:
  integer cents only, seat limits, and BillingError for every violation.
paths: services/billing/**
---
```

Or the list form when one skill should cover several roots:

```
---
name: scoped-tests
description: >-
  Use after changing code, before claiming work is done. Picks the correctly
  scoped pytest command instead of running the whole suite.
paths:
  - services/**
  - packages/**
  - tests/**
---
```

Both shapes are valid. Globs follow standard rules: `**` matches any nesting depth, `*` matches one segment, prefix paths are relative to the project root.

How Claude decides whether to surface the skill: it scans the file paths Claude has touched or is about to touch. Skills whose `paths:` glob matches enter the discovery set. Non-matching skills get filtered out before their descriptions land in the system prompt. That filtering pushes [progressive disclosure](/blog/claude-skills-guide) one level deeper: not just "load the body when needed" but "do not list the skill if the work is somewhere else."

## A Worked Example

Take an API-route skill scoped to `services/api/**`:

```
---
name: api-add-route
description: >-
  Use when adding or changing an HTTP route under services/api. Walks the exact
  steps so the new route follows the gateway conventions.
paths: services/api/**
---
 
# Adding an API route
 
1. Write the handler in the matching module. Signature is `(request: dict) -> dict`.
2. Validate inputs first. Bad input raises `ValidationError`, never return an error dict by hand.
3. No business logic in the handler. Call a repo or another service.
4. Register the route in `routes.py` inside `build_app()`.
5. Add a test in `tests/` that builds the app and dispatches the route.
```

Why this is right:

- Putting these five steps in root CLAUDE.md burns 500 tokens per session on a procedure that fires maybe one session in ten. The workflow-in-rules error.
- Leaving the skill unscoped surfaces it during frontend, infra, and CI work where it has no relevance. Claude might still pick it from the description, but you pay for that decision in tokens on every prompt.
- The narrow `paths:` scope means it appears in discovery only when Claude is editing under `services/api/`. Outside that folder, Claude does not know the skill exists.

## Scoping Strategies That Work

Four patterns cover almost every real case.

**Service-specific skills.** One skill per top-level service, scoped to that service root. The Helpline pattern: `billing-money-rules` at `services/billing/**`, `api-add-route` at `services/api/**`. Maps cleanly onto microservice or workspace boundaries.

**File-type skills.** Scope by extension or filename when the workflow is tied to a file type rather than a directory. A migration-review skill scoped to `db/migrations/**/*.sql`, or a translations skill scoped to `**/i18n/*.json`.

**Mirror your folder structure.** When the codebase already partitions cleanly, mirror the partition in skills. One per package, one per service, named after its scope. New engineers can guess where a skill lives before opening the folder.

**Do not scope cross-cutting skills.** Anything that fires regardless of where Claude is working stays unscoped. Examples: a git commit skill, a code review checklist, an incident response runbook. Adding `paths:` to these is a categorization error: they are not bound to a location.

## How Discovery Works at Session Start

Skill discovery is description-driven, not name-driven. Claude reads the `name:` plus `description:` for every skill that survives the `paths:` filter and decides activation based on whether the description matches the user's prompt.

Scoping does not let you write lazy descriptions. The path filter shrinks the candidate set; the description still has to win against the others in that set. "Helps with backend code" loses to "Use when adding an HTTP route under services/api" every time.

The [skill activation hook](/blog/skill-activation-hook) is the safety net when description matching is not enough. It runs keyword and intent matching on the user prompt and appends explicit skill recommendations before Claude sees the message. Pair it with path scoping and you get a two-stage filter: paths limit visibility, description plus hook decide what fires.

## Composing With Layered CLAUDE.md

Path-scoped skills compose naturally with [subdirectory CLAUDE.md files](/blog/subdirectory-claude-md). The pattern:

```
project/
├── CLAUDE.md                              # cross-cutting conventions
├── services/
│   ├── api/
│   │   ├── CLAUDE.md                      # API conventions (rules)
│   │   └── ...
│   └── billing/
│       ├── CLAUDE.md                      # billing conventions (rules)
│       └── ...
└── .claude/
    └── skills/
        ├── api-add-route/SKILL.md         # paths: services/api/**
        ├── billing-money-rules/SKILL.md   # paths: services/billing/**
        └── scoped-tests/SKILL.md          # paths: services/**, packages/**
```

Inside `services/api`, Claude loads the root CLAUDE.md, the `services/api/CLAUDE.md`, and the `api-add-route` skill enters discovery. Inside `services/billing`, Claude sees the billing rules, the billing CLAUDE.md, and a different skill. Same Claude, two different harnesses, zero overlap. This is the foundation any [large codebase playbook](/blog/large-codebase-playbook) is built on.

## Anti-Patterns

Three failure modes show up consistently:

1. **Scoping too narrowly.** A glob like `services/api/handlers/payments.py` means the skill only activates when Claude is editing that exact file. Most edits in `services/api` will not match, and the skill will feel broken. Scope to the directory, not the file.
2. **Scoping too broadly.** `paths: **/*` is the same as not scoping. It surfaces the skill on every session, which is the bloat you were trying to avoid.
3. **Mixing rules into skills (or workflows into CLAUDE.md).** Re-read the decision tree above. If you find yourself writing "always do X" in a SKILL.md, it belongs in CLAUDE.md. If you find yourself writing a 12-step procedure in CLAUDE.md, it belongs in a skill.

The [skill listing budget setting](/blog/skill-listing-budget) (`skillListingBudgetFraction`) silently drops descriptions when the listing exceeds 1% of context. Path scoping is one of the cleanest ways to stay under that budget without losing skills.

## Where This Fits in the Harness

Skills are one of the seven pieces of [Anthropic's harness model](/blog/the-ai-layer). Path scoping is the lever that lets the skills component scale past a handful of installed skills without flooding the listing. Without it, every new skill is a tax on every session. With it, skills behave like the IDE features they pattern-match against: visible when relevant, invisible otherwise.

## Conclusion

The principle behind path-scoped skills in Claude Code is the same one behind every well-tuned harness: load only what is relevant, only when it is relevant. A flat listing was workable at three skills. At twenty, scoping is not optional.

Two takeaways. First, the rules-vs-workflows split is load-bearing: conventions go in CLAUDE.md, procedures go in skills, and `paths:` binds the procedure to the location it serves. Second, the `paths:` parameter is plural, takes a single glob or a list, and filters before description matching.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
