---
sidebar_position: 2
title: /create-skill
description: Build and verify one canonical project skill for Claude Code and Codex, or create an agent-local global skill.
---

# /create-skill

Build a reusable skill from any topic.

Provide a topic or workflow description, and `/create-skill` explores the codebase, gathers relevant patterns, and builds a well-structured skill interactively with you. In a Pilot-prepared repository, it writes project skills once under `.agents/skills/`; Pilot's shared hook regenerates `.claude/skills/` after supported edits from Claude Code or Codex and again at Stop as a Code Mode backstop. If no topic is given, it evaluates the current session for extractable knowledge.

```bash
# Claude Code
claude
> /create-skill
> /create-skill "Vue 3 test migration pattern"
> /create-skill "How we set up MFE local development"

# Codex CLI
codex
> $create-skill
> $create-skill "Vue 3 test migration pattern"
> $create-skill "How we set up MFE local development"
```

## What /create-skill Does

8 phases:

| Phase | Action |
|-------|--------|
| 1 | Load reference — use case categories, complexity spectrum, file structure, template, frontmatter fields, description formula, security restrictions |
| 2 | Understand the topic — explore codebase for relevant patterns, or evaluate session for extractable knowledge |
| 3 | Check existing skills — avoid duplicates, identify update and migration opportunities |
| 4 | Create or edit the canonical project skill under `.agents/skills/`; global skills remain agent-local |
| 5 | Run structure, content, cross-agent portability, triggering, and synchronization quality gates |
| 6 | Test and iterate with realistic prompts, then optimize description triggering |
| 7 | Check anti-patterns and troubleshooting guidance |
| 8 | Compare the result with a complete example |

## Project skill synchronization

Run `/setup-rules` once before creating repository skills. It installs `scripts/sync-agent-assets.mjs` and establishes the root `AGENTS.md` / `CLAUDE.md` contract.

For a project skill, edit only the canonical source:

```text
.agents/skills/my-project-skill/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

Pilot's shared hook mirrors the skill on SessionStart, after supported edits made through either agent, and at Stop when Code Mode emitted no edit event. Normally you only run the read-only verification:

```bash
node scripts/sync-agent-assets.mjs --check
```

If the check finds drift after a hook outage, `node scripts/sync-agent-assets.mjs --write` is the recovery command. It is not a normal authoring step.

The generated tracked files in `.claude/skills/my-project-skill/` are byte-identical. If Claude Code or Codex targets one directly, Pilot redirects the edit when supported or blocks it and reports the canonical `.agents/skills/` path. Agent identity works both ways; filesystem authority stays one-way. Untracked or ignored local agent-only extensions remain outside this repository contract.

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
Skills are plain markdown files using the same `SKILL.md` format on both agents. They're loaded on-demand when relevant and shareable across your team via the **Extensions page**. Claude Code uses `.claude/skills/` and `~/.claude/skills/`; Codex uses `.agents/skills/` and `~/.agents/skills/`.

For project scope, those directories are not two authoring locations: `.agents/skills/` is canonical and `.claude/skills/` is generated automatically by Pilot's shared hook. Global user skills remain agent-local unless promoted through Pilot's skill library.
:::
