---
name: spec-verify
description: "Spec verification phase - tests, execution, rules audit, code review"
argument-hint: "<path/to/plan.md>"
user-invocable: false
---

# /spec-verify - Verification Phase

**Phase 3 of the /spec workflow (features).** Runs comprehensive verification: automated checks, code review, program execution, and E2E tests. For bugfix plans, use `spec-bugfix-verify` instead.

**Input:** Plan file with `Status: COMPLETE`
**Output:** Plan status → VERIFIED (success) or loop back to implementation (failure)

---

## ⛔ KEY CONSTRAINTS

<!-- CC-ONLY -->
1. **Run the changes review when enabled** — active whenever `PILOT_CHANGES_REVIEW_ENABLED` is not `"false"` (read in Step 0). Step 1 launches the single `changes-review` sub-agent in the background; Step 3 collects its findings file. To disable, use Console Settings → Spec Workflow → Review Agents → Changes Review.
2. **`changes-review` is the ONLY reviewer sub-agent this phase launches** — via the Agent tool, ONLY via the Step 1 launch (background, findings file, no `TaskOutput`). NEVER launch `spec-review` during verification: `findings-spec-review-*.json` files are stale planning artifacts, ignore them completely. `findings-changes-review-*.json` is valid ONLY when it is the file this run's Step 1 launch wrote (Step 1a deletes stale ones first).
   ⛔ **Never `Skill(skill='code-review', ...)`.** That skill carries `disable-model-invocation` — the call is rejected, and a workflow that treats it as its review silently verifies nothing. A deeper multi-agent review is the user's to start by typing `/code-review`.
<!-- /CC-ONLY -->
<!-- CODEX-START
1. **Run native Codex changes review when enabled** — Step 1 launches the managed `changes-review` custom agent via `multi_agent_v1.spawn_agent` when `PILOT_CHANGES_REVIEW_ENABLED` is not `"false"` (read in Step 0). Step 3 waits for and applies its findings.
2. **Only changes-review — NEVER spec-review** — Do NOT launch `spec-review` during verification. Planning findings are stale artifacts from the planning phase and must be ignored.
CODEX-END -->
3. **NO stopping** — Everything automatic. Never ask "Should I fix these?"
4. **Fix ALL findings** — must_fix AND should_fix. No permission needed.
5. **Code changes finish BEFORE runtime testing** — Phase A then Phase B.
6. **Plan file is source of truth** — re-read it after auto-compaction, don't rely on conversation memory.
7. **Re-verification after fixes is MANDATORY** — fixes can introduce new bugs.
8. **Quality over speed** — never rush due to context pressure.
