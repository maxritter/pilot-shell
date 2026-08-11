---
title: "Claude Code /simplify and /batch Commands Guide"
description: "Claude Code /simplify runs 3-agent code review on your changes. /batch handles parallel codebase migrations. Mechanics, usage, and examples."
slug: simplify-batch-commands
date: 2026-02-28
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Claude Code /simplify runs 3-agent code review on your changes. /batch handles parallel codebase migrations. Mechanics, usage, and examples.

<!-- truncate -->

**Problem**: You just finished implementing a feature in Claude Code. The code works, but you know there's duplicated logic, a few functions that could be cleaner, and some inefficient patterns you didn't have time to address. Cleaning it up manually means re-reading every changed file, spotting issues yourself, and fixing them one by one. Or you ship it as-is and deal with tech debt later. Neither option moves the needle.

**Quick Win**: Run `/simplify` right after implementing any feature. It spawns three review agents in parallel -- one checking code reuse, one checking quality, one checking efficiency -- then aggregates their findings and applies fixes automatically. No need to craft a prompt. Just type the command.

```
# After implementing a feature
/simplify
 
# Focus on a specific concern
/simplify focus on memory efficiency
```

If you're new to Claude Code, see the getting started guide first. If you need something bigger -- migrating an entire codebase from one framework to another, or applying a change across dozens of files -- that's what `/batch` is for. These two commands shipped in Claude Code v2.1.63 and they cover two workflows that used to require careful multi-step prompting.

## What Claude Code /simplify Does

`/simplify` is a post-implementation cleanup command. After you've built something and it works, `/simplify` reviews what you changed and makes it better.

It starts by running `git diff` (or `git diff HEAD`) to identify what changed. If there are no git changes, it falls back to recently modified files. Then it launches three specialized review agents in parallel, each receiving the full diff:

| Agent | Focus Area | What It Actually Looks For |
| --- | --- | --- |
| **Code Reuse** | Duplicated logic, redundant patterns | Existing utilities that could replace new code, duplicate functions across files, hand-rolled string manipulation or path handling where helpers already exist, inline logic that should use existing abstractions |
| **Code Quality** | Readability, structure, conventions | Redundant state, parameter sprawl, copy-paste with slight variation, leaky abstractions, "stringly-typed" code using raw strings where typed constants exist |
| **Efficiency** | Performance and resource usage | Unnecessary work, missed concurrency opportunities, hot-path bloat (expensive logic in tight loops), time-of-check/time-of-use (TOCTOU) anti-patterns, memory leaks, overly broad operations like reading entire files when only portions are needed |

All three agents run simultaneously. Once they finish, `/simplify` aggregates their findings, fixes each valid issue directly, and silently skips findings it determines are false positives. You get a brief summary of what was fixed -- or confirmation that the code was already clean.

Boris Cherny, the Claude Code PM, put it well: these bundled commands "automate much of the work it used to take to shepherd a pull request to production." `/simplify` is the automated code review step between "it works" and "it's ready to merge."

### When to Use /simplify

The sweet spot is right after implementation, before you open a PR:

- **After finishing a feature** -- clean up before review
- **After a bug fix** -- make sure the fix didn't introduce shortcuts
- **After a prototype** -- tighten up experimental code you want to keep
- **Before a PR** -- catch issues a reviewer would flag

You can also pass optional text to narrow the focus:

```
/simplify focus on error handling
/simplify check for unnecessary dependencies
/simplify look at the database query patterns
```

This is useful when you know a specific area needs attention but don't want to write a full prompt describing the codebase context. The command already knows which files changed recently.

### What /simplify Is Not

`/simplify` is not a linter and it's not a formatter. It operates at a higher level -- architectural decisions, code structure, algorithm efficiency. It complements tools like ESLint or Biome, not replaces them. If you're using [hooks for validation](/blog/self-validating-agents), `/simplify` handles the concerns those tools can't catch.

It's also not a general-purpose refactoring tool. It focuses on recently changed files, not your entire codebase. For broad codebase changes, that's where `/batch` comes in.

## What Claude Code /batch Does

Claude Code's `/batch` command orchestrates large-scale changes across your codebase in parallel. The command's interface is deceptively simple -- just a description and usage examples:

```
/batch migrate from react to vue
/batch replace all uses of lodash with native equivalents
/batch add type annotations to all untyped function parameters
```

You describe what needs to change, and `/batch` triggers a deeper orchestration agent that handles the research, decomposition, execution, and PR creation. Here's what that orchestrator does under the hood -- a three-phase loop:

**Phase 1 -- Research and Plan.** The orchestrator enters plan mode, launches Explore agents to deeply research what the instruction touches -- finding all files, patterns, and call sites that need to change. It then decomposes the work into 5 to 30 self-contained units, depending on codebase size and change complexity. Each unit must be independently implementable in an isolated worktree and mergeable on its own without depending on another unit landing first. The orchestrator also figures out an end-to-end verification recipe -- whether that's browser automation, CLI testing, or running your existing test suite. If it can't determine a verification path, it asks you before proceeding.

**Phase 2 -- Spawn Workers.** After you approve the plan, the orchestrator launches one background agent per unit -- all in a single message block so they run in true parallel. Each agent gets `isolation: "worktree"` for a clean git worktree. Each agent's prompt is fully self-contained: the overall goal, its specific task, and codebase conventions discovered during research. It also includes the end-to-end test recipe and worker instructions. After implementing, each worker runs `/simplify` on its own changes, executes the test suite, commits, pushes, and opens a PR with `gh pr create`.

**Phase 3 -- Track Progress.** The orchestrator renders a status table and updates it as agents complete, pulling PR URLs from each agent's output. You get a final summary like "22/24 units landed as PRs."

The worktree isolation is what makes this work. Each agent gets its own branch and working copy, meaning they don't step on each other's changes. There's no merge conflict chaos. Each unit is independently testable and reviewable.

```
# Large-scale migration
/batch migrate src/ from Solid to React
 
# Pattern application
/batch add input validation to all API endpoints
 
# Convention enforcement
/batch rename all database columns from camelCase to snake_case
 
# Dependency update
/batch update all axios calls to use the new fetch wrapper
```

### The Plan Step

Before any code changes happen, `/batch` shows you exactly what it plans to do. You see each unit of work, what files it'll touch, and what the change involves. You approve the plan before agents start executing.

This makes `/batch` predictable. You're not handing your codebase to an autonomous process and hoping for the best. You see the decomposition, verify it makes sense, and then let it run.

If the plan looks wrong -- maybe it missed some files, or grouped things incorrectly -- you can adjust before execution starts. This is similar to how planning modes work for individual tasks, but scaled to codebase-wide operations.

### Requirements

`/batch` requires a git repository. This isn't optional. Each agent unit runs in its own git worktree, and each one opens a pull request when it's done. If you're not in a git repo, `/batch` won't run.

The git worktree requirement also means your changes are safe. Each agent's work is isolated in its own branch. If one unit fails or produces bad output, the others aren't affected. You can merge the PRs that work and discard the ones that don't.

### When to Use /batch

`/batch` is built for work that's parallelizable. That means dozens or hundreds of files need the same kind of change, and each change is independent of the others.

Good fits:

- **Framework migrations** -- converting components from one framework to another
- **API contract changes** -- updating all callers when an interface changes
- **Convention enforcement** -- applying naming conventions, adding error handling, or standardizing patterns across the codebase
- **Dependency swaps** -- replacing one library with another across all usage sites
- **Test generation** -- adding test coverage to untested modules

Bad fits:

- **Tightly coupled changes** where file A depends on file B's new output (these aren't independent units)
- **Exploratory refactoring** where you don't know the end state yet
- **Single-file changes** that don't warrant decomposition

If your change requires coordination between units -- agent A creates a shared utility and agent B needs to import it -- `/batch` isn't the right tool. Use standard Claude Code sessions or [agent teams](/blog/agent-teams) for coordinated multi-agent work instead.

## /simplify vs /batch: When to Use Each Command

These commands solve different problems at different scales. Here's the decision framework:

| Dimension | /simplify | /batch |
| --- | --- | --- |
| **Scale** | Recently changed files | Entire codebase |
| **Timing** | After implementation | Before implementation |
| **Work type** | Review and improve existing code | Apply changes across many files |
| **Agent count** | 3 parallel reviewers | 5-30 parallel implementers |
| **Output** | Applied fixes to your branch | Multiple PRs (one per unit) |
| **Git requirement** | No | Yes (uses worktrees) |
| **Approval step** | Review diffs | Approve plan, then review PRs |
| **Best for** | Polishing | Migrating |

A useful mental model: in Claude Code, `/simplify` is your code reviewer. `/batch` is your migration team.

They're also designed to work together. Each `/batch` worker automatically runs `/simplify` on its own changes before committing. So every PR that `/batch` produces has already been through the three-agent review pass. You don't need to chain them manually -- the integration is built in.

## Practical Workflow Examples

### Example 1: Feature Development Cycle

You just built a new authentication flow across 4 files:

```
# 1. Implement the feature (normal Claude Code session)
"Add JWT authentication with refresh tokens to the API"
 
# 2. Clean up with /simplify
/simplify
 
# 3. Focus on specific concerns if needed
/simplify focus on security patterns in the auth flow
```

The three review agents check your auth implementation for duplicated token validation logic, quality issues like inconsistent error responses, and efficiency problems like unnecessary token decoding.

### Example 2: Framework Migration

Your frontend has 45 React class components that need to become functional components with hooks:

```
# 1. Describe the migration
/batch convert all React class components in src/components/ to functional components with hooks
 
# 2. Review the plan (batch shows 15 units of ~3 components each)
# 3. Approve
# 4. Each agent creates a PR with its batch of conversions
# 5. Review and merge PRs individually
```

Each PR is independently reviewable and mergeable. If one conversion is tricky and needs manual attention, you handle that PR separately without blocking the others.

### Example 3: API Standardization

Your API endpoints use inconsistent error response formats:

```
/batch standardize all API error responses to use { error: string, code: number, details?: object } format
```

`/batch` identifies every endpoint, groups them into independent units (probably by route file or domain), and has each agent update its assigned routes. Every unit runs the existing tests after making changes, so you know nothing broke.

## Bundled Commands vs Custom Slash Commands

`/simplify` and `/batch` are bundled Claude Code commands -- they ship with every installation and work out of the box. Custom slash commands, by contrast, are project-specific prompts you write yourself in your [CLAUDE.md configuration](/blog/claude-md-mastery) or `.claude/commands/` directory, like skills you define for your workflow. Bundled commands are maintained by Anthropic and receive updates with each Claude Code release.

The distinction matters because bundled commands can access internal capabilities that custom commands can't. `/batch` can spawn agents in isolated worktrees and create PRs automatically. `/simplify` can run its three-agent review pipeline without you needing to write the orchestration logic.

That said, they complement each other. Your custom commands handle project-specific workflows (your deployment process, your testing conventions, your code generation patterns). The bundled commands handle universal workflows (code review, codebase-wide changes) that apply to any project.

If you've built custom [sub-agent workflows](/blog/sub-agent-best-practices) that manually orchestrate multi-agent review passes, `/simplify` might replace them entirely. If you've been writing scripts to apply repetitive changes across files, `/batch` is the Claude-native replacement.

## Tips for Using /simplify and /batch Effectively

**Run /simplify before every PR.** Make it a habit. The three-agent review catches things you'll miss after hours of focused implementation work. In practice, `/simplify` consistently catches 3-5 issues per feature branch that would otherwise surface during code review -- the efficiency agent is particularly good at spotting unnecessary iterations and missed concurrency opportunities.

**Be specific with /batch descriptions.** "Update the codebase" is too vague. "Replace all moment.js imports with dayjs, updating the API calls to match dayjs's syntax" gives the planner enough context to decompose accurately.

**Check the /batch plan carefully.** The decomposition step is where most issues surface. If a unit spans too many files or mixes independent changes, ask for a different split before approving.

**Use /simplify's optional focus text.** When you know an area is rough -- maybe you took a shortcut during prototyping -- point `/simplify` at it specifically. The targeted review produces better results than a general pass.

**Combine /batch with your test suite.** Each `/batch` agent runs tests after making changes. Make sure your test suite actually catches regressions. Weak tests mean `/batch` agents will "pass" broken code.

## FAQ

**Does /simplify modify files automatically?**

Yes. `/simplify` applies fixes directly to your working copy. You can review the changes with `git diff` before committing. If a fix is wrong, `git checkout` the affected file to revert it.

**What happens if a /batch worker fails?**

Failed workers don't affect other workers. Each runs in its own git worktree on its own branch. You'll see the failure in the status table, and you can either retry that unit or handle it manually. Successfully completed PRs are unaffected.

**What version of Claude Code do I need?**

`/simplify` and `/batch` shipped in Claude Code v2.1.63. Run `claude --version` to check. If you're on an earlier version, run `claude update` to get these commands.

**Can /batch handle monorepos?**

Yes. `/batch` works in any git repository. In a monorepo, be specific about which packages or directories to target in your description so the planner decomposes work correctly.

**How is /simplify different from a linter?**

Linters catch syntax and style issues. `/simplify` catches architectural problems -- duplicated logic, missed abstractions, performance inefficiencies, and patterns that a human code reviewer would flag. They complement each other.

## Next Steps

- Read about [git worktrees in Claude Code](/blog/worktree-guide) to understand the isolation model `/batch` uses
- See how `/simplify` and `/batch` fit into the full [interactive mode](/blog/interactive-mode) slash command system, including session controls, keyboard shortcuts, and /btw side questions
- Learn how [agent teams](/blog/agent-teams) work for coordinated multi-agent tasks that `/batch` can't handle
- Explore custom slash commands to build project-specific workflows alongside these bundled ones
- Check [sub-agent best practices](/blog/sub-agent-best-practices) for designing your own multi-agent patterns
- Review the feedback loops guide for building review cycles into your development process
- See the full v2.1.63 changelog for everything else that shipped with these commands
- Need to install or update Claude Code? The installation guide covers setup on all platforms, including the one-line install commands

`/simplify` and `/batch` signal where Claude Code is headed: bundled multi-agent workflows that handle common engineering patterns out of the box. You still review every diff and approve every plan. But the orchestration -- spinning up parallel agents, managing worktrees, aggregating results -- is no longer something you build yourself. Expect more bundled commands like these as the platform matures.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
