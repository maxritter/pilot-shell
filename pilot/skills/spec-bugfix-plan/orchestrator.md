---
name: spec-bugfix-plan
description: "Planning phase of the /spec bugfix workflow — owns the bugfix plan file until the user approves it. Entered from the /spec dispatcher for a new bug task, or for an existing bugfix plan still marked Status: PENDING and Approved: No."
argument-hint: "<bug description> or <path/to/plan.md>"
user-invocable: false
hooks:
  Stop:
    - command: uv run --no-project --python python3 python "$HOME/.pilot/hooks/spec_plan_validator.py"
---

# /spec-bugfix-plan - Bugfix Planning Phase

**Phase 1 (bugfix).** Investigates root cause, creates lean fix plan, gets approval.

**Input:** Bug description (new) or plan path (continue unapproved)
**Output:** Approved bugfix plan at `docs/plans/YYYY-MM-DD-<slug>.md` with `Type: Bugfix`
<!-- CC-ONLY -->
**Next:** On approval → `Skill(skill='spec-implement', args='<plan-path>')`
<!-- /CC-ONLY -->
<!-- CODEX-START
**Next:** On approval → continue immediately with the `$spec-implement` skill instructions using arguments: `<plan-path>`.
CODEX-END -->

**Note:** This skill is invoked when the user types `/spec "<bug description>"` — they chose the full spec workflow. For a bugfix workflow without a plan file, users invoke `/fix` directly (separate user-facing command). The two are distinct entry points — honour the user's choice.

---

## Resuming an Unapproved Plan

When the argument ends with `.md`: read the plan, check `Status:` and `Approved:`. **Step 0 (toggle read + the 0.1a plan-mode/Fable sentinel that the later steps depend on) always runs first**, then resume from wherever planning left off:

- No investigation yet → Step 2 (Investigation)
- Has investigation, no tasks → Step 3 (Plan the Fix)
- Complete but unapproved → Step 6 (Approval)

---

## Iron Laws

```
1. NO FIXES WITHOUT ROOT CAUSE — traced to file:line, explained WHY.
2. NO CODE WITHOUT A FAILING REPRODUCING TEST — the RED must exist first.
3. FIX AT THE SOURCE — not where the error appears.
4. ONE UNIFORM STRUCTURE — every bugfix plan has the same three tasks.
```

If Step 2 is incomplete, you cannot propose fixes. Symptom fixes are failure. Retroactive tests are failure. "I know the fix, I'll skip the test" is failure.

---

## Critical Constraints

- **NEVER write production code during planning** — planning and implementation are separate phases. The ONE exception: temporary boundary instrumentation during Step 2 investigation (log/print lines marked `SPEC-DEBUG:`) is allowed to trace the root cause; it must be removed before the plan is written (and Step 1.5 of verification greps for the marker to catch leftovers).
- **NEVER assume — verify by reading files.** Trace the bug to actual file:line.
- **Lean ≠ skipping steps.** Small bugs get short tasks, not fewer tasks. The three-task structure (Reproducing Test → Fix → Quality Gate) is non-negotiable.
- **Plan file is source of truth** — survives across auto-compaction cycles
- **⛔ No workflow narration** — never output text describing what step you are about to execute ("I'm investigating root cause…", "The harness injected a reminder…"). Just do the work. The user sees tool calls and the final plan, not a running commentary.
<!-- CC-ONLY -->
- **Use the `AskUserQuestion` tool for clarifications** — it renders a structured form; don't fall back to plain-text numbered questions
<!-- /CC-ONLY -->
<!-- CODEX-START
- **Use plain-text numbered options for clarifications** — the Claude question tool isn't callable in Codex
CODEX-END -->
- **If `PILOT_PLAN_QUESTIONS_ENABLED` is `"false"` (from Step 0),** skip all `AskUserQuestion` calls (Steps 2.1, 2.5 escalation, 3 approach selection). Make reasonable default assumptions (including selecting the recommended fix approach) and document them in the plan. Continue autonomously.

<!-- CODEX-START

### Codex Bugfix Planning Speed Contract

For Codex, bugfix quality means a traced root cause, a reproducing RED test plan, and a source-level fix strategy. It does not mean exhaustive graph traversal.

- Reach the first complete bugfix plan before context reaches 35% unless the bug is not reproducible.
- **Planning context ceiling — total planning must not exceed ~55% of the context window (hard cap 60%).** The 35% first-draft target leaves headroom for the RED test plan and self-review, NOT deeper traversal. On the ~256K Codex window that is ≈140K tokens. If context approaches ~55% before approval, stop investigating and finalize the bugfix plan with the traced root cause, RED test name, and fix file you already have — the fix itself happens during implementation, which needs the remaining budget. Planning that eats >60% has already failed.
- Use a bounded investigation: one reproduction attempt path, at most one CodeGraph orientation call when the entry point is unknown, one Semble intent search, then targeted reads of the suspected files. Skip CodeGraph for docs, rules, markdown, config, UI copy, reviews of a known diff, or named paths.
- Run callers/callees/impact only after a likely root-cause function is known and the bug spans more than one component.
- Ask at most one bundled clarification prompt before the approval prompt. If the missing signal blocks reproduction, ask; otherwise record a Medium-confidence root cause and a verification task.
- Stop investigating once you can state `Root Cause: file:line — function() does X but should do Y`, name the RED test, and name the source file the fix must touch.
CODEX-END -->

> **NOTE: During `/spec`, use the structured workflow below — not CC's native plan mode.**
