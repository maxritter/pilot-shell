---
description: "Bugfix spec planning phase - analyze bug, design fix, get approval"
argument-hint: "<bug description> or <path/to/plan.md>"
user-invocable: false
model: opus
hooks:
  Stop:
    - command: uv run python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_plan_validator.py"
---

# /spec-bugfix-plan - Bugfix Planning Phase

**Bugfix variant of Phase 1 of the /spec workflow.** Analyzes the bug, creates a right-sized fix plan with Behavior Contract, and gets user approval.

**Input:** Bug description (new bugfix plan) or plan path (continue unapproved bugfix plan)
**Output:** Approved bugfix plan file at `docs/plans/YYYY-MM-DD-<slug>.md` with `Type: Bugfix`
**Next phase:** On approval → `Skill(skill='spec-implement', args='<plan-path>')`

---

## ⛔ KEY CONSTRAINTS

| #   | Rule                                                                                             |
| --- | ------------------------------------------------------------------------------------------------ |
| 1   | **NO sub-agents during planning** — Direct tools only.                                           |
| 2   | **ONLY stopping point is plan approval** — Everything else is automatic.                         |
| 3   | **NEVER write code during planning** — Separate phases.                                          |
| 4   | **NEVER assume — verify by reading files.** Trace the bug to actual file:line.                   |
| 5   | **Plan file is source of truth** — Survives across auto-compaction cycles.                       |
| 6   | **Re-read plan after user edits** — Before asking for approval again.                            |
| 7   | **Right-size the plan** — Small bugs get lean plans. Don't over-engineer the process.            |

---

> **WARNING: DO NOT use the built-in `ExitPlanMode` or `EnterPlanMode` tools.**

---

## Step 1.1: Create Plan File Header (FIRST)

**Immediately upon starting, create the plan file header.**

1. **Parse worktree choice from arguments:**
   - Look for `--worktree=yes` or `--worktree=no` at the end of the arguments
   - Strip the `--worktree=...` flag from the bug description
   - Default to `No` if no flag is present

2. **Create worktree early (if `--worktree=yes`):** Follow same pattern as `spec-plan.md` Step 1.1.2.

3. **Generate filename:** `docs/plans/YYYY-MM-DD-<bug-slug>.md`
   - Create slug from first 3-4 words of bug description (lowercase, hyphens)

4. **Create directory if needed:** `mkdir -p docs/plans`

5. **Write initial header immediately:**

   ```markdown
   # [Bug Description] Fix Plan

   Created: [Date]
   Status: PENDING
   Approved: No
   Iterations: 0
   Worktree: [Yes|No]
   Type: Bugfix

   > Planning in progress...

   ## Summary

   **Goal:** [Bug description from user]

   ---

   _Analyzing bug..._
   ```

6. **Register plan association (MANDATORY):**

   ```bash
   ~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true
   ```

---

## Step 1.2: Bug Understanding & Targeted Exploration

**Goal: Trace the bug to a specific file:line root cause.**

### Step 1.2.1: State Your Understanding

Before exploring, restate the bug in your own words:
- What is the symptom (what does the user observe)?
- When does it trigger?
- What should happen instead?

If the bug description is too vague to trace, use AskUserQuestion to ask ONE focused question (reproduction steps, error message, version info, or minimal example that triggers it).

### Step 1.2.2: Targeted Code Exploration

**Read as many files as needed to fully understand the bug area.** Thorough exploration is valuable — understanding the codebase deeply before planning leads to better fixes.

For each file in the bug area:
1. Read it completely
2. Trace the execution path from user action → symptom
3. Note the specific line(s) where the bug occurs (hypothesize if not certain)

**Tools for targeted exploration:**

| Tool               | When to Use                     |
| ------------------ | ------------------------------- |
| **Vexor**          | Find files by intent/concept    |
| **Read/Grep/Glob** | Read specific files in bug area |

### Step 1.2.3: Derive the Bug Analysis

**After exploration, formalize the bug:**

**Bug Condition (C):** The specific input partition or state where the bug triggers.
- Be precise: "When X is Y AND Z is W..."

**Root Cause Hypothesis:** The specific code location causing the bug.
- Format: "In `file/path.py:lineN`, `function_name()` does X but should do Y"
- Include the actual line of code if possible
- Explain WHY it causes the observed symptom

**Postcondition (P):** What "fixed" means — the observable outcome when the fix is correct.
- Be precise: "Given C, the system returns/does/produces X instead of Y"

---

## Step 1.3: Behavior Contract

**Formalize what MUST and MUST NOT change.**

```
Fix Property:           C ⟹ P         (when bug condition holds, fix applies)
Preservation Property:  ¬C ⟹ unchanged (when bug condition doesn't hold, behavior unchanged)
```

**Must Change (Fix Property: C ⟹ P):**
- WHEN [bug condition C] THEN [correct behavior P]
- Describe the regression test: what existing entry point it calls, what it asserts, why it fails on current code

**Must NOT Change (¬C ⟹ unchanged):**

Explicit preservation tests are only needed when the fix modifies code paths shared with non-bug scenarios. Ask:
- Does the fix change a function that existing non-bug callers also use?
- Does the fix alter control flow in a shared path (not just adding a new branch)?

**If YES:** List 1-3 specific preservation scenarios where the fix could realistically break behavior.

**If NO (fix is isolated — new code path, new function, additive change):** Write "Existing test suite covers preservation." No explicit preservation tests needed — the full suite run during verification is the preservation check.

**Property-based testing recommendation:** If the Bug Condition depends on data structure properties, input shape, or size (not a single specific value), recommend using `hypothesis` (Python), `fast-check` (TypeScript), or `go test -fuzz` (Go).

---

## Step 1.4: Size the Task Structure

**Right-size the implementation tasks based on fix complexity.**

| Size | Criteria | Tasks |
|------|----------|-------|
| **Compact** (default) | ≤3 files changed, clear root cause | 2 tasks |
| **Full** | 4+ files, multiple failure modes, shared-path modifications | 3 tasks |

**Default to Compact.** Only use Full when the bug has multiple interacting root causes or the fix modifies many shared code paths.

### Compact: 2 Tasks (most bugs)

**Task 1: Reproduce & Fix**
- Write a regression test → verify it FAILS on current code (the bug exists)
- If preservation tests needed (per Step 1.3): write them → verify they PASS
- Implement the minimal fix
- Verify: regression test PASSES, preservation tests still PASS

**Task 2: Verify**
- Full test suite, linting, type checking

### Full: 3 Tasks (complex bugs)

**Task 1: Write Tests**
- Bug reproduction tests + preservation tests
- Verify: reproduction tests FAIL, preservation tests PASS

**Task 2: Implement Fix**
- Minimal fix at each root cause location
- Verify: all tests PASS

**Task 3: Verify**
- Full test suite, linting, type checking

### ⛔ How to Write Bug Reproduction Tests

The test must exercise the **existing public entry point** (the function/class users interact with), not internal helpers you plan to create.

**✅ Correct:** Test `PrerequisitesStep.run()` with Linux+no-Homebrew mocks, assert Node.js installation is attempted via system package manager. Fails because current code has no fallback — behavioral failure.

**❌ Wrong:** Test `_install_nodejs_via_pkg()` which doesn't exist yet. Fails with `AttributeError` — import error, not behavioral failure.

The test answers: "Under bug condition C, does the system produce correct result P?" If "no" on current code → correct test.

---

## Step 1.5: Write the Bugfix Plan

**Save plan to:** `docs/plans/YYYY-MM-DD-<bug-name>.md`

**Template:**

```markdown
# [Bug Description] Fix Plan

Created: [Date]
Status: PENDING
Approved: No
Iterations: 0
Worktree: [Yes|No]
Type: Bugfix

## Summary

**Goal:** [One sentence: fix [symptom] when [bug condition]]

**Root Cause:** `file/path.py:lineN` — [what's wrong and why]

**Bug Condition (C):** [Precise trigger condition]

**Postcondition (P):** [What "fixed" looks like]

**Symptom:** [What the user observes — error message, wrong output, crash]

## Behavior Contract

### Must Change (C ⟹ P)

- WHEN [condition] THEN [correct behavior]
- **Regression test:** `test_file.py::TestClass::test_name` — [what it tests]

### Must NOT Change (¬C ⟹ unchanged)

- WHEN [normal case] THEN [preserved]
- **Preservation:** [explicit test names, OR "Existing test suite"]

## Scope

**Change:** [files to modify]
**Test:** [test files to add/modify]
**Out of scope:** [deferred items]

## Context for Implementer

- **Root cause:** `file:line` — [explanation]
- **Pattern to follow:** [reference to existing similar code in codebase]
- **Gotchas:** [non-obvious dependencies]
- **Test location:** [where to put tests, which fixtures to use]

## Progress Tracking

- [ ] Task 1: [title]
- [ ] Task 2: [title]

**Tasks:** N | **Done:** 0

## Implementation Tasks

### Task 1: [Title — e.g., "Reproduce & Fix" or "Write Tests"]

**Objective:** [what to accomplish]

**Files:**
- [file list]

**TDD Flow:**
1. [step-by-step sequence — test first, then fix]

**Verify:** `[command]`

---

### Task 2: [Title — e.g., "Verify" or "Implement Fix"]

**Objective:** [what to accomplish]

**Verify:** `[command]`

---

[### Task 3 — only for Full-size bugs]

## Open Questions

- [remaining questions, or "None"]

### Deferred Ideas

- [related improvements out of scope]
```

**What NOT to include (these waste tokens):**
- Status lifecycle explanation blockquote (implementer already knows this)
- Separate "Bug Report" section (merged into Summary's Symptom field)
- "Testing Strategy" section (redundant with Behavior Contract)
- "Goal Verification / Truths / Artifacts / Key Links" sections (redundant)
- "Risks and Mitigations" table (same boilerplate every time)
- "Prerequisites" section (almost always "None")
- "Definition of Done" checklists per task (the Verify command IS the definition of done)
- "Dependencies" per task (ordering is implicit from task numbering)

---

## Step 1.6: Get User Approval

**⛔ MANDATORY APPROVAL GATE**

0. **Send notification:**
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Bugfix Plan Ready" "<plan-slug> — your approval is needed to proceed with implementation" --plan-path "<plan_path>" 2>/dev/null || true
   ```

1. **Summarize the plan:**
   - Bug being fixed (symptom + root cause)
   - Behavior Contract (Must Change / Must NOT Change)
   - Task structure (Compact or Full)

2. **Use AskUserQuestion:**
   ```
   Question: "Do you approve this bugfix plan for implementation?"
   Header: "Plan Review"
   Options:
     - "Yes, proceed with implementation" - Plan looks good
     - "No, I need to make changes" - Let me edit the plan first
   ```

3. **Based on response:**
   - **Yes:** Update `Approved: No` → `Approved: Yes` in plan, invoke `Skill(skill='spec-implement', args='<plan-path>')`
   - **No:** Tell user to edit plan, wait for "ready", re-read, ask again
   - **Other feedback:** Incorporate into plan, ask again

---

## Continuing Unapproved Bugfix Plans

**When arguments end with `.md` (existing plan path):**

1. Read the plan file, check `Status` and `Approved` fields
2. If `Status: PENDING` and `Approved: No`: resume from wherever planning left off
3. If plan has bug analysis but no tasks yet: proceed to Step 1.4
4. If plan is complete but approval not granted: proceed to Step 1.6

---

## Context Management

Context is managed automatically by auto-compaction. No agent action needed — just keep working.

ARGUMENTS: $ARGUMENTS
