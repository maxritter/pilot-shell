---
sidebar_position: 2
title: /create-skill
description: Build reusable skills from any topic — explores the codebase and creates them interactively
---

# /create-skill

Build a reusable skill from any topic.

Provide a topic or workflow description, and `/create-skill` explores the codebase, gathers relevant patterns, and builds a well-structured skill interactively with you. If no topic is given, it evaluates the current session for extractable knowledge.

```bash
$ pilot
> /create-skill
> /create-skill "Vue 3 test migration pattern"
> /create-skill "How we set up MFE local development"
```

## What /create-skill Does

6 phases:

| Phase | Action |
|-------|--------|
| 0 | Load reference — use case categories, complexity spectrum, file structure, template, frontmatter fields, description formula, security restrictions |
| 1 | Understand the topic — explore codebase for relevant patterns, or evaluate session for extractable knowledge |
| 2 | Check existing skills — avoid duplicates, identify update opportunities |
| 3 | Create skill — write to `.claude/skills/` (project) or `~/.claude/skills/` (global), apply portability and determinism checklists |
| 4 | Quality gates — structure checklist, content checklist, triggering test, iteration signals |
| 5 | Test & iterate — run test prompts with sub-agents, evaluate results, optimize description triggering |

## Use Case Categories

| Category | Used For | Key Techniques |
|----------|----------|----------------|
| **Document & Asset Creation** | Consistent output (reports, designs, code) | Embedded style guides, templates, quality checklists |
| **Workflow Automation** | Multi-step processes with consistent methodology | Step-by-step gates, validation, iterative refinement |
| **MCP Enhancement** | Workflow guidance on top of MCP tool access | Multi-MCP coordination, domain expertise, error handling |

## How big should a skill be

Skills are designed with the simplest possible structure that does the job. Simpler = more reliable and cheaper to execute.

| Level | Style | Best For |
|-------|-------|----------|
| **Passive** | Context only | Background knowledge, coding standards |
| **Instructional** | Rules + guidelines | Code review, style guides |
| **CLI Wrapper** | Calls a binary/script | Automation, integrations |
| **Workflow** | Multi-step with validation | Deploy pipelines, migrations |
| **Generative** | Asks agent to write code | Scaffolding, code generation |

## Skill File Structure

```
your-skill-name/
├── SKILL.md              # Required (case-sensitive, exactly SKILL.md)
├── scripts/              # Optional — executable code
├── references/           # Optional — detailed docs loaded as needed
└── assets/               # Optional — templates, fonts, icons
```

## When to Use

- You want to capture a repeatable workflow
- You completed a non-obvious debugging session
- You want to standardize a multi-step process across your team
- You discovered an undocumented tool or API integration pattern

:::info
Skills are plain markdown files stored in `.claude/skills/`. They're loaded on-demand when relevant, created by `/create-skill`, and shareable across your team via the **Extensions page**.
:::
