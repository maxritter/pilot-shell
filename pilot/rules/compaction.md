# Context Compaction — Preservation Guide

**Auto-compaction fires at ~83% context usage.** When compaction occurs, preserve these Pilot-specific elements in your summary:

## Critical State to Preserve

### 1. Active Plan
- **Plan file path** (e.g., `docs/plans/2026-02-16-feature.md`)
- **Current status** (PENDING, COMPLETE, VERIFIED)
- **Task progress** (e.g., "Task 3/6 in progress", which tasks are done)
- **Current objective** (what Task N is implementing)

### 2. Technical Context
- **Key decisions made** (architectural choices, trade-offs, approach selected)
- **Files being modified** (list of files actively being worked on)
- **Errors being debugged** (specific error messages, root cause analysis in progress)
- **Dependencies discovered** (libraries, APIs, patterns found during exploration)

### 3. Task State
- **Current task objective** (brief description of what's being implemented)
- **TDD state** (red/green/refactor phase, which tests exist)
- **Blockers or issues** (anything preventing progress)

## What Can Be Condensed

- **Conversational pleasantries** (greetings, acknowledgments)
- **Intermediate exploration** (file reads that led to understanding, but not the understanding itself)
- **Repetitive patterns** (multiple similar examples can be summarized as "explored N similar implementations")

## Post-Compaction Note

After compaction completes, the `SessionStart(compact)` hook will re-inject Pilot-specific context automatically. Your preserved summary complements this automatic restoration.
