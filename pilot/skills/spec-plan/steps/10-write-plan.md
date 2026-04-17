---

## Step 10: Write Full Plan

**Save to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

**Required sections:**

```markdown
# [Feature Name] Implementation Plan

Created: [Date]
Status: PENDING
Approved: No
Iterations: 0
Worktree: [Yes|No]
Type: Feature

## Summary

**Goal:** [One sentence]
**Architecture:** [2-3 sentences]
**Tech Stack:** [Key technologies]

## Scope

### In Scope

### Out of Scope

## Approach

**Chosen:** [Name of selected approach]
**Why:** [1-2 sentences — what it gives us and what it costs]
**Alternatives considered:** [Brief list of other approaches with why they were rejected]

## Context for Implementer

> Write for an implementer who has never seen the codebase.

- **Patterns to follow:** [file:line references]
- **Conventions:** [naming, organization, error handling]
- **Key files:** [important files with descriptions]
- **Gotchas:** [non-obvious dependencies]
- **Domain context:** [business logic needed to understand task]

## Runtime Environment (only if project has a running service)

- **Start command / Port / Deploy path / Health check / Restart procedure**

## Feature Inventory (only for migration/refactoring — see Migration section)

## Assumptions

- [What you assume] — supported by [finding/file:line] — Tasks N, M depend on this
- [What you assume] — supported by [finding/file:line] — Task N depends on this

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
⚠️ Mitigations are commitments — verification checks they're implemented.
✅ "Reset to null when project not in list" ❌ "Handle edge cases"

## Goal Verification

### Truths

### Artifacts

## E2E Test Scenarios (omit section for Minimal runtime profile)

[Scenarios from Step 9]

## Progress Tracking

- [ ] Task 1: [summary]
      **Total Tasks:** N | **Completed:** 0 | **Remaining:** N

## Implementation Tasks

[Tasks from Step 8]

## Open Questions (only if any remain)

### Deferred Ideas (only if any surfaced)
```
