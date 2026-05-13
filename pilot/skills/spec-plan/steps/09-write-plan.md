## Step 9: Write Full Plan

**Save to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

**Parsimony rule:** every section below is either **required** or **conditional**. Conditional sections MUST be omitted entirely when they have nothing concrete to say — empty headings are noise. The reader should be able to skim the plan in under a minute.

**Dedup principle — each fact lives in ONE section:**

- **File paths and per-file changes** → `## Implementation Tasks` (per-task `Files:` block). Never in Summary, Approach, or anywhere else.
- **What gets built** → `## Implementation Tasks`. The task list IS the in-scope work — DO NOT add a separate "In Scope" bullet list that paraphrases task titles.
- **What does NOT get built** → `## Out of Scope`. Explicit boundary decisions a reasonable reader might assume.
- **Observable user-facing outcomes after the plan lands** → `## Goal Verification > ### Truths`.
- **Per-task acceptance criteria** → task `Definition of Done` (not duplicated as a Goal Verification truth).
- **Domain context an implementer can't infer from code** → `## Context for Implementer` (optional). Per-file gotchas go in that task's `Key Decisions`, not here.

If you find yourself writing the same fact in two places, delete one — the longer/more-specific version stays.

**Required sections:** Summary · Approach · Progress Tracking · Implementation Tasks.
**Conditional sections** (include only when applicable, omit entirely otherwise): Out of Scope · Context for Implementer · Runtime Environment · Feature Inventory · Assumptions · Risks and Mitigations · Goal Verification · E2E Test Scenarios · Open Questions · Deferred Ideas.

```markdown
# [Feature Name] Implementation Plan

Created: [Date]
Status: PENDING
Approved: No
Iterations: 0
Worktree: [Yes|No]
Type: Feature

## Summary

**Goal:** [One sentence — what the user can do / observe after this lands.]

## Out of Scope (only when there is an explicit boundary decision a reasonable reader might assume is included; otherwise omit the whole section)

- [Items a reasonable reader might assume are included but aren't. Skip CYA "don't edit build artifacts" bullets — those are obvious. If you can't name a real boundary decision, omit the section.]

## Approach

**Chosen:** [Short name referencing real symbols/files from the workspace scan.]
**Why:** [1-2 sentences — what it gives us and what it costs.]

## Context for Implementer (only when there is a non-obvious cross-task constraint that two or more tasks need to respect, AND it does not fit in any single task's `Key Decisions`; otherwise omit)

[One short paragraph — cross-task domain context an implementer can't infer from the code. If you find yourself listing per-file patterns or gotchas, move them to the relevant task's `Key Decisions` instead.]

## Runtime Environment (only if project has a running service AND `spec-verify` / `spec-implement` will need it)

- **Start command / Port / Health check / Restart procedure**

## Feature Inventory (only for migration/refactoring — see Migration section)

## Assumptions (only when an assumption, if wrong, would silently invalidate a task — link to the dependent task numbers)

- [What you assume] — Task N depends on this

## Risks and Mitigations (conditional — only when there's a Medium-or-higher real risk worth a mitigation commitment; omit entirely on plans where the answer is "be careful")

| Risk | Likelihood | Impact | Mitigation |

⚠️ Real risks only — drop hedges ("be careful when splitting files", "follow conventions"). Mitigations must be commitments verification can check.
✅ "Reset to null when project not in list" ❌ "Handle edge cases"

## Goal Verification (only when there is a cross-task observable outcome that NO single E2E scenario and NO single task DoD captures; otherwise omit the whole section — spec-verify Step 10 audits via E2E + task DoD source keys when this is absent)

> Skip-test: if every truth you would write reduces to `TS-NNN passes` or `Task N DoD verifies`, drop the section. Pure-reference truths are noise.

### Truths

> **Cap: 3 truths.** Each must be a cross-task user-perspective outcome that cannot be checked by reading one E2E scenario or one task's DoD. If you can't write a truth that isn't a paraphrase of an existing E2E/DoD, the section doesn't belong.

1. [Cross-task observable outcome — falsifiable, user-perspective]

## E2E Test Scenarios (only when there is a UI / server / user-facing entry point AND at least one task changes it — see Step 8)

[Scenarios from Step 8. Internal logic verifications belong in task DoD, not here.]

## Progress Tracking

- [ ] Task 1: [one-line summary]
- [ ] Task 2: [one-line summary]

> Source of truth for completion. `spec-implement` toggles `[ ]` → `[x]` here. Keep short — full task bodies live below.

## Implementation Tasks

[Tasks from Step 7 — full per-task bodies.]

## Open Questions (only if any remain unresolved at approval time)

## Deferred Ideas (only if any surfaced and the user wants them captured)
```
