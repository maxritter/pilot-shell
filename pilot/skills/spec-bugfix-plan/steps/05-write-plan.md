---

## Step 5: Write the Bugfix Plan

**Save to:** `docs/plans/YYYY-MM-DD-<bug-name>.md`

```markdown
# [Bug Description] Fix Plan

Created: [Date]
Status: PENDING
Approved: No
Iterations: 0
Worktree: [Yes|No]
Type: Bugfix

## Summary

**Symptom:** [What user observes]
**Trigger:** [When/how it happens]
**Root Cause:** `file/path.py:lineN` — [what's wrong and why]

## Investigation

- [Key findings from tracing — breadcrumb trail so implementer understands the bug]
- [Working example for comparison, if relevant]
- [Recent changes that may have caused it, if relevant]

## Fix Approach

**Chosen:** [Name of selected approach]
**Why:** [1-2 sentences — what it fixes and what it costs]
**Alternatives considered:** [Brief list of other approaches with why they were rejected — omit for trivial bugs]

**Files:** [files to modify]
**Strategy:** [how to fix — reference pattern from working code if applicable]
**Tests:** [test files to create/modify]
**Defense-in-depth:** [additional validation layers, if applicable — skip for isolated fixes]

## Verification Scenario (only for UI-facing bugs — omit otherwise)

### TS-001: [Bug Trigger / Fix Confirmation]
**Preconditions:** [State that triggers the bug]

| Step | Action | Expected Result (after fix) |
|------|--------|-----------------------------|
| 1 | [User action that triggered bug] | [Correct behavior] |
| 2 | [Follow-up verification] | [No regression] |

## Progress

- [ ] Task 1: [title]
- [ ] Task 2: [title]
      **Tasks:** N | **Done:** 0

## Tasks

### Task 1: [Title]

**Objective:** [what]
**Files:** [list]
**TDD:** Write regression test → verify FAILS → implement fix → verify all PASS
**Verify:** `[command]`

### Task 2: Verify

**Objective:** Full suite + quality checks
**Verify:** `uv run pytest -q && ruff check . && basedpyright launcher`
```

**Do NOT include:** "Goal Verification" sections, "Risks and Mitigations" table, "Assumptions" section, per-task "Definition of Done" checklists, per-task "Dependencies" field.

**Include `## Verification Scenario` only for UI-facing bugs** (from the Verification Scenario guidance in Step 4). Omit entirely for backend/non-UI bugs.
