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

## Behavior Contract

**Given:** [precondition / state / input that triggers the bug]
**When:** [the action or call that exercises the code path]
**Currently (bug):** [actual, incorrect behavior — the symptom]
**Expected (fix):** [correct behavior the fix must produce]
**Anti-regression:** [what must still work — behavior the fix must NOT break]

## Fix Approach

**Chosen:** [Name of selected approach]
**Why:** [1-2 sentences — what it fixes and what it costs]
**Alternatives considered:** [Brief list of other approaches with why they were rejected — omit for trivial bugs]

**Files:** [files to modify]
**Strategy:** [how to fix — reference pattern from working code if applicable]
**Tests:** [test files to create/modify — MUST exist before any fix code]
**Defense-in-depth:** [additional validation layers, if applicable — skip for isolated fixes]

## Verification Scenario (only for UI-facing bugs — omit otherwise)

### TS-001: [Bug Trigger / Fix Confirmation]
**Preconditions:** [State that triggers the bug]

| Step | Action | Expected Result (after fix) |
|------|--------|-----------------------------|
| 1 | [User action that triggered bug] | [Correct behavior] |
| 2 | [Follow-up verification] | [No regression] |

## Progress

- [ ] Task 1: Write Reproducing Test (RED)
- [ ] Task 2: Implement Fix at Root Cause
- [ ] Task 3: Quality Gate
      **Tasks:** 3 | **Done:** 0

## Tasks

### Task 1: Write Reproducing Test (RED)

**Objective:** Encode the Behavior Contract as a failing test BEFORE writing any fix code.
**Files:** [test files to create/modify]
**Entry point:** [public function or endpoint the test exercises — not internal helpers]
**DoD:** Test exists, named `test_<function>_<bug>_<expected>`, runs, fails with an error matching the documented `Currently (bug)` behavior. In worktree mode: committed as its own commit.
**Verify:** `[command that runs ONLY this test — must FAIL]`

### Task 2: Implement Fix at Root Cause

**Objective:** Minimal change at `Root Cause: file:line` that makes the reproducing test pass without breaking `Anti-regression`.
**Files:** [files to modify — must include the root cause file]
**Strategy:** [how the fix satisfies the Behavior Contract — fix at source, not at symptom]
**DoD:** Reproducing test PASSES. Full test suite PASSES (anti-regression gate for the fix). Diff touches the root-cause file. No try/except wrappers hiding the bad value; no callsite patches around the symptom.
**Verify:** `[command that runs the reproducing test — must PASS]`

### Task 3: Quality Gate

**Objective:** Lint + type check + build clean, with the full suite re-run to catch regressions introduced by any auto-fixes applied in this task.
**DoD:** Lint clean, type check clean, build green (if applicable), full suite green. Performance audit passed (no expensive uncached work on hot paths in the diff).
**Verify:** `[lint] && [type check] && [build if applicable] && [full suite command]`

**Why the suite runs again here:** lint/type checkers and formatters may auto-modify code (imports, type annotations, whitespace). A checkbox marked green should mean "suite green AFTER this task's code touches." The verify phase then runs it once more as the authoritative signal — that small redundancy is quality insurance, not waste.
```

**Always three tasks.** Never collapse Task 1 + Task 2 into "Fix (test + code)". The separation is what prevents "I'll just write the code and add a test after."

**Do NOT include:** "Goal Verification" sections, "Risks and Mitigations" table, "Assumptions" section, per-task "Dependencies" field.

**Include `## Verification Scenario` only for UI-facing bugs** (from the Verification Scenario guidance in Step 4). Omit entirely for backend/non-UI bugs.

**The `## Behavior Contract` section is MANDATORY for every bugfix plan** — it is the source of truth for what the reproducing test encodes and what verification audits.
