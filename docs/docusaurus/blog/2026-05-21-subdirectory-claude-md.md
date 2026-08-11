---
title: "Subdirectory CLAUDE.md: Layered Context"
description: "One CLAUDE.md does not scale. Layer them per subdirectory. Claude walks the tree, loads the right rules, and your context stays lean."
slug: subdirectory-claude-md
date: 2026-05-21
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

One CLAUDE.md does not scale. Layer them per subdirectory. Claude walks the tree, loads the right rules, and your context stays lean.

<!-- truncate -->

Your root CLAUDE.md started at 40 lines. It is now 380. React conventions, API guidelines, database rules, deploy commands, the same testing notes copy-pasted three times. Every session loads all of it, even when you are only touching one folder. Claude starts ignoring half the file. Performance gets worse, not better, the more you write.

The fix is structural, not editorial. You do not need a shorter root file. You need a **subdirectory claude md** structure that puts local rules next to the code they govern, then trusts Claude Code to load the right layers automatically.

## Why One Big CLAUDE.md Stops Working

There are three failure modes, and they compound at scale.

**Context cost.** Every byte in CLAUDE.md loads every session. A 400-line root file with 30 sessions a day is 12,000 lines of repeated context. Anthropic is direct about this: CLAUDE.md files should stay "focused on what applies broadly" to "prevent them from becoming a drag on performance." Root files should be "pointers and critical gotchas only; everything else drifts into noise."

**Relevance dilution.** A single file mixing API conventions, frontend patterns, and infra notes asks Claude to weigh all of them equally during every task. The model treats CLAUDE.md as high priority instruction, so when you edit a React component, the database rules still compete for attention. High priority everywhere means priority nowhere. We covered the underlying mechanics in [CLAUDE.md mastery](/blog/claude-md-mastery).

**Drift and merge pain.** One file owned by five teams becomes a merge-conflict magnet. Backend appends sections, frontend rewrites them, infra adds gotchas at the bottom, nobody trims. Six months later the file contradicts itself in three places.

You can keep editing harder. Or you can stop trying to put everything in one place.

## How Hierarchical Loading Actually Works

Anthropic ships a specific behavior here, and it is the whole point of this post. When you start Claude Code in a directory, it "automatically walks up the directory tree and loads every CLAUDE.md file it finds along the way, so root-level context is never lost." Files load "additively as it moves through the codebase: root file for the big picture, subdirectory files for local conventions."

Concretely, start Claude in `packages/api/handlers/` and it reads, in order:

1. `packages/api/handlers/CLAUDE.md` if present
2. `packages/api/CLAUDE.md` if present
3. `CLAUDE.md` at the repo root

Three files, one merged context, and Claude sees the most-specific rules last (which the model weights appropriately during generation). The root file stays lean because it only carries cross-cutting concerns. The subdirectory file stays focused because it only owns its slice.

```
repo/
├── CLAUDE.md                    # Stack overview, cross-cutting rules
├── packages/
│   ├── api/
│   │   ├── CLAUDE.md            # API conventions, test commands
│   │   └── handlers/
│   │       ├── CLAUDE.md        # Handler-specific gotchas
│   │       └── ...
│   └── web/
│       ├── CLAUDE.md            # React patterns, build commands
│       └── ...
└── infra/
    ├── CLAUDE.md                # Terraform conventions, deploy notes
    └── ...
```

The root file in this layout might be 60 lines covering the monorepo stack, branch protection, and a one-line pointer to each package. Each subdirectory file owns the rest.

## The Init-in-Subdirectory Trick

This is the move that almost nobody does, and it changes how Claude scopes the entire session. Instead of running `claude` at the repo root, change into the directory you are actually working in first.

```
cd packages/api && claude
```

Anthropic recommends "initializing in subdirectories, not at the repo root," noting that "Claude works best when it's scoped to the part of the codebase that's actually relevant to the task." Walk-up loading still pulls the root file, so you do not lose the big picture. What changes is Claude's default search radius for `grep`, file reads, and exploration. It stays in your slice unless you tell it otherwise.

When this is the right move:

- You know the work lives in one package or service
- The repo has hundreds of top-level folders and full-tree scans waste tokens
- A junior dev on your team is paired with Claude and you want to constrain blast radius

When you should still root-init:

- The change crosses three or more packages
- You are doing a refactor that touches shared types
- You are exploring an unfamiliar repo and need the full map

## A Sample Subdirectory CLAUDE.md

A good subdirectory file is short, specific, and answers the questions Claude will actually have while working there. Here is a realistic one for an API handlers folder:

```
# packages/api/handlers/CLAUDE.md
 
## Scope
 
This folder owns HTTP handlers for the public REST API. Internal RPC
lives in packages/rpc/. Auth middleware is in packages/api/middleware/.
 
## Conventions
 
- Every handler returns `Result<T, ApiError>`, never throws
- Validate input with Zod schemas in `schemas/`, do not inline
- Errors use the shared `ApiError` discriminated union, no custom shapes
- Log with `req.log` (already scoped to request_id)
 
## Commands
 
- Test this slice: `pnpm --filter @repo/api test handlers`
- Lint: `pnpm --filter @repo/api lint`
- Local server: `pnpm --filter @repo/api dev`
 
## Gotchas
 
- DO NOT import from `packages/web/*`, handlers must stay frontend-agnostic
- The `legacy/` subfolder is frozen, ticket required for changes
- Rate limiter is async-init, see `setup.ts` before adding new handlers
```

Thirty lines. Zero overlap with the root file. Loads only when work touches this folder. Compare that to repeating the same content in a 400-line root file that ships to every session.

If you want even finer control over what loads where, the [Claude Code rules directory pattern](/blog/rules-directory) layers a `.claude/rules/` folder with path frontmatter on top of this. CLAUDE.md handles per-folder conventions; rules files handle per-path predicates. Both can live in the same repo.

## When Not to Fragment

Layering is not free. Each new CLAUDE.md is one more file your team needs to maintain. Skip fragmentation when:

- The repo is under 30k lines and the rules genuinely apply everywhere
- It is a solo project and the conventions never diverge
- The folders do not have meaningfully different domains (a single Next.js app with one `app/` directory does not need three CLAUDE.md files)

The signal that you have crossed the threshold is usually obvious: you find yourself writing "if you are working in `packages/api/`, then..." inside your root file. That is the moment to split.

## Per-Folder Test and Lint Commands

This is the second highest-leverage win after layered files. Anthropic is explicit: "CLAUDE.md files at the subdirectory level should specify the commands that apply to that part of the codebase," because running full suites "causes timeouts and wastes context on irrelevant output."

In a monorepo, telling Claude to run `pnpm test` at root might trigger 40 packages, blow past timeouts, and dump 2,000 lines of unrelated output into context. The subdirectory CLAUDE.md should say `pnpm --filter @repo/api test`, and that is what Claude will run. Faster feedback, cleaner context, fewer false negatives.

The caveat Anthropic notes is real: compiled-language monorepos with cross-package type dependencies sometimes need a full build before any one package's tests are valid. Document that in the subdirectory file too. "Before changes that touch shared types, run `pnpm build:types` at root."

## Where This Fits in the Harness

Layered CLAUDE.md is the base layer in the seven-part Claude Code harness model. Hooks, skills, LSP, MCP servers, sub-agents, and plugins compose around it. We mapped the whole stack in [the AI layer pillar](/blog/the-ai-layer).

The pattern composes especially well with [path-scoped skills](/blog/path-scoped-skills): CLAUDE.md owns the conventions, skills own the workflows, and both can be scoped by directory. Together they are the foundation of [running Claude Code in a large codebase](/blog/large-codebase-playbook) without burning context on rules that do not apply.

## The Mental Model

Rules live as close to the code they govern as possible. A frontend convention belongs next to the frontend. An API gotcha belongs next to the API. The root file holds only what every session genuinely needs.

You are not writing less. You are writing the same content in better-aimed places, so Claude loads the right slice at the right moment and ignores the rest. The bigger the codebase, the bigger the win. By the time your repo is hundreds of folders deep, this is the difference between a tool that helps and a tool that drowns in its own instructions. Combined with [strong context engineering practices](/blog/context-engineering), it is how Claude Code stays useful past the side-project scale.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
