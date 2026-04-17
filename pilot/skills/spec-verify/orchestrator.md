---
name: spec-verify
description: "Spec verification phase - tests, execution, rules audit, code review"
argument-hint: "<path/to/plan.md>"
user-invocable: false
effort: high
model: sonnet
hooks:
  Stop:
    - command: uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_verify_validator.py"
---

# /spec-verify - Verification Phase

**Phase 3 of the /spec workflow (features).** Runs comprehensive verification: automated checks, code review, program execution, and E2E tests. For bugfix plans, use `spec-bugfix-verify` instead.

**Input:** Plan file with `Status: COMPLETE`
**Output:** Plan status → VERIFIED (success) or loop back to implementation (failure)

---

## ⛔ KEY CONSTRAINTS

1. **Run code review when enabled** — Step 4 launches `changes-review` via `Task(subagent_type="pilot:changes-review")` when `PILOT_CHANGES_REVIEW_ENABLED` is not `"false"` (read in Step 0). To disable, use Console Settings → Reviewers → Changes Review toggle.
2. **Only changes-review — NEVER spec-review** — Do NOT launch `spec-review` during verification. Do NOT read or reference `findings-spec-review-*.json` files — they are stale artifacts from the planning phase that were already addressed during implementation. If you encounter a spec-review findings file, **ignore it completely**.
3. **NO stopping** — Everything automatic. Never ask "Should I fix these?"
4. **Fix ALL findings** — must_fix AND should_fix. No permission needed.
5. **Code changes finish BEFORE runtime testing** — Phase A then Phase B.
6. **Plan file is source of truth** — re-read it after auto-compaction, don't rely on conversation memory.
7. **Re-verification after fixes is MANDATORY** — fixes can introduce new bugs.
8. **Quality over speed** — never rush due to context pressure.
