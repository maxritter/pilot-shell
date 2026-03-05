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

**Bugfix variant of Phase 1.** Analyzes bug, creates right-sized fix plan with Behavior Contract, gets approval.

**Input:** Bug description (new) or plan path (continue unapproved)
**Output:** Approved bugfix plan at `docs/plans/YYYY-MM-DD-<slug>.md` with `Type: Bugfix`
**Next:** On approval → `Skill(skill='spec-implement', args='<plan-path>')`

---

## ⛔ Critical Constraints

- **NEVER write code during planning** — planning and implementation are separate phases
- **NEVER assume — verify by reading files.** Trace the bug to actual file:line.
- **Plan file is source of truth** — survives across auto-compaction cycles
- **Re-read plan after user edits** before asking for approval again
- **Right-size the plan** — small bugs get lean plans. Don't over-engineer.
- **⛔ ALWAYS use `AskUserQuestion` tool** for clarifications — never list numbered questions in plain text. Provide structured options users can select.

> **NOTE: During `/spec`, use the structured workflow below — not CC's native plan mode.**

---

## Step 1.1: Create Plan File Header (FIRST)

1. **Parse worktree** from arguments: `--worktree=yes|no` (default: `No`). Strip flag.
2. **Create worktree early (if yes):** Same pattern as spec-plan Step 1.1.
3. **Generate filename:** `docs/plans/YYYY-MM-DD-<bug-slug>.md`
4. `mkdir -p docs/plans`
5. **Write header:**
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
6. **Register:** `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`

---

## Step 1.2: Bug Understanding & Targeted Exploration

### 1.2.1: State Understanding

Restate: symptom (what user observes), trigger (when), expected behavior. If too vague, AskUserQuestion with ONE focused question.

### 1.2.2: Targeted Code Exploration

**Read as many files as needed** to fully understand the bug area. For each file: read completely, trace execution path from user action → symptom, note specific lines where bug occurs.

Tools: Vexor (find by intent), Read/Grep/Glob (direct exploration).

### 1.2.3: Bug Analysis

**Bug Condition (C):** Precise input partition or state where bug triggers.

**Root Cause Hypothesis:** `file/path.py:lineN` — `function_name()` does X but should do Y. Include actual line, explain WHY it causes the symptom.

**Postcondition (P):** What "fixed" means — "Given C, the system returns/does X instead of Y."

---

## Step 1.3: Behavior Contract

```
Fix Property:           C ⟹ P         (bug condition → fix applies)
Preservation Property:  ¬C ⟹ unchanged (non-bug scenarios → unchanged)
```

**Must Change (C ⟹ P):** WHEN [condition] THEN [correct behavior]. Describe the regression test: entry point, assertion, why it fails now.

**Must NOT Change (¬C ⟹ unchanged):** Does the fix modify shared code paths?
- **YES:** List 1-3 specific preservation scenarios.
- **NO (isolated fix):** "Existing test suite covers preservation."

**Property-based testing:** Recommend if Bug Condition depends on data shape/ranges/combinations (not a single value).

---

## Step 1.4: Size the Task Structure

| Size | Criteria | Tasks |
|------|----------|-------|
| **Compact** (default) | ≤3 files, clear root cause | 2: Reproduce & Fix → Verify |
| **Full** | 4+ files, multiple failure modes | 3: Write Tests → Implement Fix → Verify |

### Compact (most bugs)

**Task 1: Reproduce & Fix** — Write regression test → verify FAILS → preservation tests if needed → verify PASS → implement fix → verify all PASS.
**Task 2: Verify** — Full test suite, lint, type check.

### Full (complex bugs)

**Task 1: Write Tests** — reproduction + preservation tests.
**Task 2: Implement Fix** — minimal fix at each root cause.
**Task 3: Verify** — full suite, lint, type check.

**Bug reproduction tests must exercise existing public entry points** (not internal helpers you plan to create). The test answers: "Under condition C, does the system produce correct result P?"

---

## Step 1.5: Write the Bugfix Plan

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
**Goal:** Fix [symptom] when [bug condition]
**Root Cause:** `file/path.py:lineN` — [what's wrong and why]
**Bug Condition (C):** [precise trigger]
**Postcondition (P):** [what "fixed" looks like]
**Symptom:** [what user observes]

## Behavior Contract

### Must Change (C ⟹ P)
- WHEN [condition] THEN [correct behavior]
- **Regression test:** `test_file.py::test_name` — [what it tests]

### Must NOT Change (¬C ⟹ unchanged)
- **Preservation:** [test names, OR "Existing test suite"]

## Scope
**Change:** [files to modify]
**Test:** [test files]
**Out of scope:** [deferred items, if any]

## Context for Implementer
- **Root cause:** `file:line` — [explanation]
- **Pattern to follow:** [reference similar code]
- **Test location:** [where, which fixtures]

## Progress Tracking
- [ ] Task 1: [title]
- [ ] Task 2: [title]
**Tasks:** N | **Done:** 0

## Implementation Tasks
### Task 1: [Title]
**Objective:** [what]
**Files:** [list]
**TDD Flow:** [steps]
**Verify:** `[command]`

### Task 2: [Title]
**Objective:** [what]
**Verify:** `[command]`
```

**Do NOT include** (these waste tokens in bugfix plans): Status lifecycle blockquote, separate "Bug Report" section, "Testing Strategy" section, "Goal Verification / Truths / Artifacts" sections, "Risks and Mitigations" table, "Prerequisites" section, per-task "Definition of Done" checklists, per-task "Dependencies" field.

---

## Step 1.6: Get User Approval

0. Notify:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Bugfix Plan Ready" "<plan-slug> — approval needed" --plan-path "<plan_path>" 2>/dev/null || true
   ```
1. Summarize: symptom + root cause, Behavior Contract, task structure
2. AskUserQuestion: "Yes, proceed" | "No, let me edit"
3. **Yes:** Set `Approved: Yes`, invoke `Skill(skill='spec-implement', args='<plan-path>')`
   **No:** User edits, re-read, ask again. **Other:** Incorporate, re-ask.

---

## Continuing Unapproved Bugfix Plans

When arguments end with `.md`: read plan, check Status/Approved. Resume from wherever planning left off: no analysis yet → Step 1.2. Has analysis, no tasks → Step 1.4. Complete but unapproved → Step 1.6.

ARGUMENTS: $ARGUMENTS
