---
description: "Bugfix verification phase - Behavior Contract audit, tests, process compliance"
argument-hint: "<path/to/plan.md>"
user-invocable: false
model: sonnet
hooks:
  Stop:
    - command: uv run python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_verify_validator.py"
---

# /spec-bugfix-verify - Bugfix Verification Phase

**Bugfix variant of Phase 3.** Lightweight verification focused on Behavior Contract: bug tests, preservation tests, process compliance.

**Input:** Bugfix plan with `Status: COMPLETE`
**Output:** Plan → VERIFIED (success) or loop back to implementation (failure)

**Why no sub-agents:** The Behavior Contract (Fix + Preservation properties) proves correctness through tests. Bug test proves fix works, preservation tests prove nothing else broke. Sub-agents would re-verify what tests already prove.

---

## ⛔ Critical Constraints

- **NO review sub-agents** — the Behavior Contract + tests ARE the verification for bugfixes
- **NO stopping** — everything automatic. Never ask "Should I fix these?"
- **Fix ALL issues automatically** — no permission needed
- **Quality over speed** — never rush due to context pressure
- **Plan file is source of truth** — re-read after auto-compaction
- **Re-verification after fixes is MANDATORY** — fixes can introduce new bugs

---

## The Process

```
Phase A: Full Test Suite → Behavior Contract Audit → Process Compliance → Plan Verify Commands → Artifact Check
Phase B: Build → Runtime Verification (if deferred commands exist)
Final:   Regression check → Worktree sync → Post-merge → Status update
```

---

## Phase A: Verify the Behavior Contract

### Step 3.1: Run & Fix Tests

Full test suite. Fix any failures immediately.

### Step 3.2: Behavior Contract Audit

**⛔ Core verification step for bugfixes.**

1. **Read** the `## Behavior Contract` section from the plan

2. **Fix Property (C ⟹ P):** Run regression tests listed under "Must Change":
   ```bash
   uv run pytest <test-path>::<test-name> -q
   ```
   Each must PASS. If any fail: fix is incomplete — fix immediately.

3. **Preservation Property (¬C ⟹ unchanged):** Check "Must NOT Change":
   - Explicit test names → run each, verify PASS
   - "Existing test suite" → already verified in Step 3.1

4. **Scope check:** Read changed files, confirm changes match plan scope. Flag unplanned changes.

5. **Report:**
   ```
   ## Behavior Contract Audit
   **Fix Property (C ⟹ P):** ✅ [test] — PASS
   **Preservation (¬C ⟹ unchanged):** ✅ [test] — PASS
   **Scope:** N files, M lines — matches plan
   ```

### Step 3.3: Process Compliance

1. Type checker — zero errors
2. Linter — errors are blockers
3. File length — >800 lines consider splitting, >1000 flag for review

### Step 3.4: Plan Verify Commands

Re-run each task's `Verify:` commands: `timeout 30 <cmd> || echo 'TIMEOUT'`. Defer server-dependent commands (containing `curl`, `localhost`, `http://`, `playwright-cli`) to Phase B.

### Step 3.5: Artifact Check

For each `Create:` / `Test:` file in plan: `test -f <path>`. Fix any MISSING immediately.

---

## Phase B: Final Checks

### Step 3.6: Build

Build/compile. Zero errors.

### Step 3.7: Runtime Verification (only if deferred commands exist)

If no server-dependent commands were deferred in Step 3.4: skip to Final.

Otherwise: start service → run deferred commands → stop service → fix failures.

---

## Final

### Step 3.8: Final Regression Check

Re-run test suite + type checker + build one final time. If code changed during Phase B this catches regressions. If no code changed, it confirms Phase A's green state — cheap insurance.

### Step 3.9: Worktree Sync (if worktree active)

1. Detect: `~/.pilot/bin/pilot worktree detect --json <plan_slug>`
2. If no worktree: skip to Step 3.11.
3. Pre-sync: verify clean working tree on base branch
4. Save plan to project root: `cp <worktree_plan> <project_root>/docs/plans/`
5. Show diff: `~/.pilot/bin/pilot worktree diff --json <plan_slug>`
6. Notify + AskUserQuestion: "Yes, squash merge" | "No, keep" | "Discard"
7. Handle:
   - **Squash:** `worktree sync` then `cleanup --force` + `cd` in SAME bash call
   - **Keep:** Report path
   - **Discard:** `cleanup --force` + `cd` in SAME bash call

   ⛔ NEVER separate cleanup and cd into different Bash calls.

### Step 3.10: Post-Merge Verification (after squash merge only)

1. Full test suite
2. Type checker / linter
3. Build

If any fails: fix on base branch, re-run, commit fix separately.

### Step 3.11: Update Plan Status

**All passes:** Set `Status: VERIFIED`, register, report:
```
✅ Workflow complete! Behavior Contract: Fix ✅ | Preservation ✅
```

**Fails:** Add fix tasks, set `Status: PENDING`, increment `Iterations`, write `## Verification Gaps` table, invoke `Skill(skill='spec-implement', args='<plan-path>')`.

ARGUMENTS: $ARGUMENTS
