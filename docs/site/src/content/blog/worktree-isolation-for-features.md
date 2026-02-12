---
slug: "worktree-isolation-for-features"
title: "Git Worktree Isolation for AI-Built Features"
description: "Run AI work on a separate branch so your main branch stays clean. Squash merge when verified, discard if something goes wrong."
date: "2026-01-27"
author: "Max Ritter"
tags: [Guide, Git]
readingTime: 4
keywords: "git worktree, Claude Code isolation, feature branches, squash merge, Claude Code git, safe AI development"
---

# Git Worktree Isolation for AI-Built Features

When Claude builds a feature, it modifies files directly on your working branch. If something goes wrong — a bad refactor, a broken integration — you're left cleaning up the mess. Worktree isolation solves this by running AI work on a separate branch in a separate directory.

## The Risk of Direct Branch Work

Without isolation, Claude's changes mix with your uncommitted work. Problems:

- A failed feature attempt leaves your branch dirty
- You can't easily diff "before Claude" vs "after Claude"
- Reverting means cherry-picking or manual file restoration
- Parallel work on the same branch creates conflicts

## How Worktree Isolation Works

Git worktrees create a second working directory linked to the same repository. Claude works in the worktree on a dedicated branch while your main branch stays untouched.

```
your-project/           ← Your branch (clean)
.worktrees/spec-auth/   ← Claude's branch (isolated)
```

Both directories share the same git history. Changes in the worktree don't affect your main directory until you explicitly merge them.

## The Workflow

1. **Create** — A worktree is created with a dedicated branch
2. **Implement** — All code changes happen in the worktree
3. **Verify** — Tests, linting, and review run against the worktree
4. **Sync** — Changes are squash-merged back to your branch
5. **Cleanup** — Worktree and branch are removed

If anything goes wrong, you skip step 4 and cleanup — your branch was never touched.

## Squash Merge

When syncing back, all worktree commits are squash-merged into a single commit on your branch. This gives you:

- **Clean history** — One commit per feature instead of dozens of intermediate ones
- **Easy revert** — `git revert` one commit undoes the entire feature
- **Review-friendly** — One diff to review, not a chain of incremental changes

## Per-Task Commits

Inside the worktree, Claude commits after each task. This enables:

- `git bisect` to find which task introduced a problem
- Independent revert of individual tasks
- Better failure recovery — completed tasks are preserved

These intermediate commits disappear in the squash merge, but they're useful during development.

## When to Use Worktree Isolation

| Scenario | Use Worktree? |
|----------|--------------|
| Quick bug fix | No — too much overhead |
| Small feature (1-3 files) | Optional |
| Large feature (5+ files) | **Yes** |
| Risky refactor | **Yes** |
| Experimental work | **Yes** |

## How Pilot Manages Worktrees

Pilot's `/spec` command creates worktrees automatically when `Worktree: Yes` (the default). The entire lifecycle — create, implement, verify, sync, cleanup — is handled without manual git commands.

If your working tree has uncommitted changes when creating a worktree, Pilot asks whether to commit, stash, or skip isolation. No work is lost.
