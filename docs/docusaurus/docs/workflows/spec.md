---
sidebar_position: 3
title: /spec
description: Plan, implement, and verify complex features with full automation using Spec-Driven Development
---

# /spec

Plan, implement, and verify complex features with full automation using Spec-Driven Development.

**Replaces Claude Code's built-in plan mode (Shift+Tab).** Best for complex features, refactoring tasks, or any work where you want to review a plan before implementation begins. The structured workflow prevents scope creep and ensures every task is tested and verified before being marked complete.

```bash
$ pilot
> /spec "Add user authentication with OAuth and JWT tokens"
> /spec "Migrate the REST API to GraphQL"
> /spec "Fix the crash when deleting nodes with two children"  # bugfix auto-detected
```

## Workflow

```
Discuss → Plan → Approve → Implement → Verify → Done
```

The only manual step is **Approve**. Everything else runs automatically. The Verify → Implement feedback loop repeats until all checks pass, then prompts for squash merge.

## Spec Types

### Feature Spec

Full exploration workflow for new functionality, refactoring, or any work where architecture decisions matter.

- Codebase exploration with Probe semantic search and codebase-memory-mcp structural analysis
- Architecture design decisions via Q&A
- Full plan with scope, risks, and Definition of Done
- Unified verification agent (optional, configurable in Console Settings)

### Bugfix Spec (auto-detected)

Investigation-first flow for targeted fixes. Finds the root cause before touching any code.

- Root cause tracing: backward through call chain to `file:line`
- Pattern analysis: compare broken vs working code paths
- Test-before-fix: regression test FAILS → fix → all tests PASS
- Lightweight verify: regression test + full suite, no sub-agents

## Three Phases

### Plan Phase

- Explores codebase with semantic search, asks clarifying questions
- Writes detailed spec with scope, tasks, and definition of done
- Plan-reviewer sub-agent validates completeness (optional, enabled by default)
- Waits for your approval — edit the plan directly before accepting

### Implement Phase

- Isolated git worktree on a dedicated branch (optional)
- Strict TDD for each task: RED → GREEN → REFACTOR
- Quality hooks auto-lint, format, and type-check every edit
- Full test suite after each task to catch regressions early

### Verify Phase

- Full test suite + type checking + lint + build verification
- Features: unified review sub-agent (optional, enabled by default)
- Bugfixes: regression test + full suite — no sub-agents needed
- Auto-fixes findings, loops back until all checks pass

## Configurable Toggles

All interaction points in `/spec` are configurable via **Console Settings → Spec Workflow** and **Console Settings → Reviewers**.

### Spec Workflow Toggles

| Toggle               | Default | Effect when disabled                                                      |
| -------------------- | ------- | ------------------------------------------------------------------------- |
| **Worktree Support** | On      | Worktree is never used — implementation always runs on the current branch |
| **Ask Questions**    | On      | Planning runs fully autonomous — no clarifying questions                  |
| **Plan Approval**    | On      | Implementation starts immediately after planning — no approval gate       |

When all three are disabled, `/spec` runs end-to-end without any user interaction. Start a task, come back to verified code.

### Reviewer Toggles

| Toggle          | Default | What it does                                                                                  |
| --------------- | ------- | --------------------------------------------------------------------------------------------- |
| **Plan Review** | On      | Validates the plan before implementation — checks alignment and flags risky assumptions       |
| **Spec Review** | On      | Reviews code after implementation — compliance, quality, and goal achievement |

Both reviewers run in a separate context window and don't consume the main session's context budget.

## Worktree Isolation (Optional)

When starting a `/spec` task, you can choose to work in an isolated git worktree. All implementation happens on a dedicated branch — `main` stays clean throughout. Pilot auto-stashes any uncommitted changes before creating the worktree and restores them after. After verification passes, choose to squash merge back. If the experiment doesn't work out, discard the worktree with no cleanup required.
