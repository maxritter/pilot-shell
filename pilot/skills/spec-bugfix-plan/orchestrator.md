---
name: spec-bugfix-plan
description: "Bugfix spec planning phase - investigate root cause, design fix, get approval"
argument-hint: "<bug description> or <path/to/plan.md>"
user-invocable: false
model: opus
hooks:
  Stop:
    - command: uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_plan_validator.py"
---

# /spec-bugfix-plan - Bugfix Planning Phase

**Phase 1 (bugfix).** Investigates root cause, creates lean fix plan, gets approval.

**Input:** Bug description (new) or plan path (continue unapproved)
**Output:** Approved bugfix plan at `docs/plans/YYYY-MM-DD-<slug>.md` with `Type: Bugfix`
**Next:** On approval → `Skill(skill='spec-implement', args='<plan-path>')`

---

## Iron Laws

```
1. NO FIXES WITHOUT ROOT CAUSE — traced to file:line, explained WHY.
2. NO CODE WITHOUT A FAILING REPRODUCING TEST — the RED must exist first.
3. FIX AT THE SOURCE — not where the error appears.
4. ONE UNIFORM STRUCTURE — every bugfix plan has the same three tasks.
```

If Step 3 is incomplete, you cannot propose fixes. Symptom fixes are failure. Retroactive tests are failure. "I know the fix, I'll skip the test" is failure.

---

## Critical Constraints

- **NEVER write code during planning** — planning and implementation are separate phases
- **NEVER assume — verify by reading files.** Trace the bug to actual file:line.
- **Lean ≠ skipping steps.** Small bugs get short tasks, not fewer tasks. The three-task structure (Reproducing Test → Fix → Quality Gate) is non-negotiable.
- **Plan file is source of truth** — survives across auto-compaction cycles
- **ALWAYS use `AskUserQuestion` tool** for clarifications — never list numbered questions in plain text
- **⛔ If `PILOT_PLAN_QUESTIONS_ENABLED` is `"false"` (from Step 0),** skip all `AskUserQuestion` calls (Steps 3.1, 3.5 escalation, 4 approach selection). Make reasonable default assumptions (including selecting the recommended fix approach) and document them in the plan. Continue autonomously.

> **NOTE: During `/spec`, use the structured workflow below — not CC's native plan mode.**
