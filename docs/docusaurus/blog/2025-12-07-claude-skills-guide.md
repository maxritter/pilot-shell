---
title: "Claude Skills: Stop Repeating Instructions Forever"
description: "Skills are Claude Code's missing link between prompts and MCP. Load instructions on-demand, save context, give Claude domain expertise."
slug: claude-skills-guide
date: 2025-12-07
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Skills are Claude Code's missing link between prompts and MCP. Load instructions on-demand, save context, give Claude domain expertise.

<!-- truncate -->

**Problem**: You type the same instructions into Claude Code every session. "Follow our brand guidelines." "Use our deployment process." "Check security patterns first." Context wasted. Time lost. Instructions forgotten.

**Quick Win**: Create your first skill right now:

```
.claude/skills/code-review/SKILL.md
```

```
---
name: code-review
description: Reviews staged or modified code for security flaws, missing input validation, and unhandled error paths. Triggers on requests like "review my changes" or "check this code".
---
 
# Code Review Process
 
1. Run `git diff --staged` (or use the file the user names)
2. Check each change against:
   - SQL injection: parameterized queries only
   - Missing input validation at function entry
   - Catch blocks that swallow errors silently
   - Hardcoded credentials or API keys
3. Report findings as: severity, file:line, fix suggestion
```

That is a complete skill. Drop it in your project, and Claude automatically loads it when you ask for code review.

## What Are Skills?

**Skills are folders containing instructions that Claude discovers and loads dynamically.** Think of them as specialized training manuals Claude references only when needed.

Unlike prompts (which disappear after each conversation) or MCP servers (which connect to external tools), skills teach Claude *how to do things*. They encode procedural knowledge: workflows, guidelines, checklists, and domain expertise.

Simon Willison noted this efficiency: "Each skill only takes up a few dozen extra tokens, with the full details only loaded in should the user request a task that the skill can help solve."

## How Progressive Disclosure Works

Skills use a two-stage loading system that saves your context window:

**Stage 1 — Metadata only (~100 tokens per skill).** Claude sees skill names and descriptions. Just enough to know what is available without burning context on instructions Claude may never need.

**Stage 2 — Full instructions (when needed).** Only when Claude determines a skill matches your task does it load full instructions, typically under 5,000 tokens. Reference files inside the skill folder load on demand from there.

```
my-skill/
├── SKILL.md              # Core instructions (loads when needed)
├── scripts/              # Automation scripts
├── references/           # Documentation Claude can read
└── assets/               # Templates and files
```

This architecture means you can have dozens of skills available without overwhelming Claude's working memory.

## How Claude Decides to Activate a Skill

Activation is description-driven, not name-driven. Here's the actual decision flow:

1. **Per-prompt scan.** On every user message, Claude reads the metadata (name + description) for every skill registered in the project and your global config.
2. **Description matching.** Claude semantically matches the user's prompt against each skill's `description` field. The name alone almost never triggers activation; the description does.
3. **Disambiguation.** When two skills could plausibly apply, Claude either asks you to confirm, or picks the one with the more specific description. This is why vague descriptions like "helps with documents" rarely fire — they get beaten by anything more specific.
4. **Load and execute.** Once a skill matches, Claude loads the full SKILL.md content, treats it as authoritative for the duration of that task, and follows the procedure as written.

**Practical implication**: Your `description` field is doing the work of an intent classifier. Write it for that job. Mention the trigger phrases users actually type. Mention the file types or task types the skill applies to. Skip marketing language.

A description like `"Reviews staged or modified code for security flaws. Triggers on phrases like 'review my changes' or 'security check'"` will activate reliably. A description like `"Helps you with code"` will not.

## Skills vs CLAUDE.md: When to Use Each

The fastest way to lose hours is mixing these up. Use this split:

| Need | Use This |
| --- | --- |
| Always-loaded project context (stack, conventions, paths) | CLAUDE.md |
| Procedural knowledge that fires on specific tasks | Skill |
| One-off rule for this conversation | Prompt |
| External data or API access | MCP |

**CLAUDE.md** is read at session start and stays in context for every prompt. Anything you want Claude to remember *all the time* — your tech stack, file structure, naming conventions, "always run lint before commit" — belongs there.

**Skills** are loaded on demand based on what you ask. Anything that's a multi-step procedure tied to a specific task — code review checklist, deployment runbook, incident response steps — belongs in a skill.

The rule of thumb: if Claude needs the information whether or not you mention the topic, it's CLAUDE.md. If Claude only needs it when you raise a specific request, it's a skill.

When the same content lives in both places, CLAUDE.md takes precedence (it's loaded first). Avoid the duplication.

## Three Real-World Skill Examples

**Example 1 — Brand voice consistency**

```
---
name: brand-voice
description: Rewrites or reviews marketing copy, blog posts, and customer-facing text for brand voice consistency. Triggers on "review this copy", "make this on-brand", or any content writing request.
---
 
# Brand Voice Application
 
Voice: confident, peer-level, specific. Not formal. Not hyperbolic.
 
Always:
 
- Active voice
- Specific numbers over vague claims
- Contractions OK ("you're", "don't")
- Lead with the problem or benefit
 
Never:
 
- "Cutting-edge", "revolutionary", "game-changing", "leverage" as a verb
- Hedging ("might", "could potentially")
- Generic openings ("In this article we will explore")
 
When reviewing, list each off-brand line with a suggested rewrite. When writing fresh, ship copy that already passes the rules above.
```

**Example 2 — Database query patterns**

```
---
name: postgres-query-review
description: Reviews PostgreSQL queries for performance and safety. Triggers when user shares SQL, asks about query optimization, or runs EXPLAIN.
allowed-tools: "Read,Bash"
---
 
# Postgres Query Checklist
 
Run through every query the user shares:
 
1. **Index coverage**: confirm WHERE/JOIN columns are indexed
2. **Sequential scans**: flag any full table scan over 10K rows
3. **N+1 patterns**: in app code, check for queries inside loops
4. **Parameterization**: reject string-concatenated SQL on sight
5. **EXPLAIN ANALYZE**: run for any query touching >100K rows
 
When suggesting fixes, show the query before and after, plus the expected change in planner output. Reference the `postgres-best-practices` skill for deep optimization patterns.
```

**Example 3 — Deployment runbook**

```
---
name: deploy-production
description: Walks through the production deployment checklist. Triggers on "deploy", "ship to prod", "release", or after the user merges a PR to main.
---
 
# Production Deploy
 
Pre-deploy:
 
1. Confirm CI is green on main
2. Confirm migrations have been reviewed and are reversible
3. Confirm feature flags for new code default to OFF
 
Deploy: 4. Trigger the deploy workflow in GitHub Actions 5. Wait for the smoke test job to pass 6. Spot-check `/healthz` and the auth endpoint
 
Post-deploy (within 30 minutes): 7. Check Sentry for new errors 8. Check the dashboard for traffic anomalies 9. Flip feature flags ON one at a time, watching the dashboard between each
 
If any step fails, halt and investigate. Do not roll forward with errors present.
```

These three together cover three different shapes: content review, technical review, and procedural runbook. The pattern repeats across hundreds of use cases.

## Pre-Built Skills from Anthropic

Anthropic maintains official skills you can use immediately:

- **pdf**: Extract text and tables from PDF documents
- **docx**: Create and edit Word documents with tracked changes
- **xlsx**: Manipulate Excel spreadsheets
- **pptx**: Generate PowerPoint presentations
- **brand-guidelines**: Apply consistent styling

Find them at [github.com/anthropics/skills](https://github.com/anthropics/skills) or create your own following their patterns. Claude Code also ships bundled commands like [`/simplify` and `/batch`](/blog/simplify-batch-commands) that handle code review and codebase-wide migrations without any setup.

## Common Mistakes (and How to Fix Them)

**1. Vague descriptions.** "This skill helps with documents" never beats a more specific competitor. Fix: name the trigger phrases and the artifact types in the description itself.

**2. Overloaded SKILL.md files.** When the file passes ~5,000 tokens, you've stopped writing a skill and started writing a manual. Fix: split detail into `references/` files and link to them from SKILL.md. Claude reads them on demand.

**3. Missing `allowed-tools`.** If your skill needs to write files or run shell commands, declare it. Without `allowed-tools`, Claude may have access disabled per project policy and silently skip the steps. Fix: add `allowed-tools: "Read,Write,Bash"` (or whichever subset) to the frontmatter.

**4. Overlap with another skill.** Two skills with overlapping descriptions cause Claude to ping-pong between them or pick the wrong one. Fix: either merge, or sharpen each description so the boundaries are obvious.

**5. Conflict with CLAUDE.md.** If your skill says "use TypeScript" and CLAUDE.md says "use JavaScript", the skill loses. Fix: align skills to the conventions already in CLAUDE.md, or update CLAUDE.md if the skill represents the new standard.

**6. No "what this skill does NOT do" boundary.** Skills without negative space tend to over-fire. Fix: add a short "Out of scope" section so Claude doesn't activate the skill on adjacent but distinct requests.

### Real Failure Modes

These are the patterns that show up over and over once you have more than a handful of skills.

**The Silent No-Op.** Skill loads, runs, returns nothing useful. Almost always a missing `allowed-tools` declaration or a SKILL.md that describes what to do without saying which file or directory to do it on. Fix: every step in your procedure should reference a concrete artifact or tool.

**The Wrong Trigger.** A skill named `database-migration` keeps firing on SELECT-only queries because the description mentions "database". Fix: tighten the description with the actual trigger conditions ("triggers on schema changes, migration scripts, or `CREATE TABLE` requests").

**The Drift.** Skill worked great for three months, then quietly broke when the underlying tool changed. Fix: include a version or date in the SKILL.md header noting what tool versions you tested against, and add a quarterly review to your repo hygiene.

## Your Next Steps

1. **Create one skill** for your most repeated instruction
2. **Test triggering** with natural requests (not just explicit commands)
3. **Iterate** based on how it performs in real sessions
4. Explore context management to maximize your skill efficiency
5. Learn how skills fit into [context engineering](/blog/context-engineering) for production AI
6. Review [CLAUDE.md mastery](/blog/claude-md-mastery) for the always-on context layer that pairs with skills

Skills are one of five techniques that top agentic engineers use daily. See all five in our [Claude Code best practices](/blog/agentic-engineering-best-practices) guide.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
