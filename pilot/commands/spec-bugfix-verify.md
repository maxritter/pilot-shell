---
description: "Bugfix verification phase - Behavior Contract audit, tests, process compliance"
argument-hint: "<path/to/plan.md>"
user-invocable: false
model: opus
hooks:
  Stop:
    - command: uv run python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_verify_validator.py"
---

# /spec-bugfix-verify - Bugfix Verification Phase

**Bugfix variant of Phase 3 of the /spec workflow.** Runs lightweight verification focused on the Behavior Contract: bug tests, preservation tests, process compliance, and plan verify commands.

**Input:** Path to a bugfix plan file with `Status: COMPLETE`
**Output:** Plan status set to VERIFIED (success) or looped back to implementation (failure)
**On success:** Workflow complete
**On failure:** → `Skill(skill='spec-implement', args='<plan-path>')`

**Why a separate verify for bugfixes:** Feature verification launches three review sub-agents (compliance, quality, goal) because features involve new architecture, complex wiring, and artifacts that can't be fully validated by tests alone. Bugfixes are categorically different — the Behavior Contract (Fix Property + Preservation Property) mathematically proves correctness through tests. The bug test proves the fix works. The preservation tests prove nothing else broke. Three sub-agents would largely re-verify what the tests already prove, at significant time and token cost.

---

## ⛔ KEY CONSTRAINTS (Rules Summary)

| #   | Rule                                                                                                  |
| --- | ----------------------------------------------------------------------------------------------------- |
| 1   | **NO review sub-agents** — The Behavior Contract + tests ARE the verification for bugfixes            |
| 2   | **NO stopping** — Everything is automatic. Never ask "Should I fix these?"                            |
| 3   | **Fix ALL issues automatically** — No permission needed                                               |
| 4   | **Quality over speed** — Never rush due to context pressure                                           |
| 5   | **Plan file is source of truth** — Survives across auto-compaction cycles                             |
| 6   | **Re-verification after fixes is MANDATORY** — Fixes can introduce new bugs. Always re-verify.        |

---

## The Process

```
Phase A — Verify the Behavior Contract:
  Full Test Suite → Behavior Contract Audit → Process Compliance → Plan Verify Commands → Artifact Check

Phase B — Final Checks:
  Build → Plan-Specific Runtime Verification (if any)

Final:
  Regression check → Worktree sync → Post-merge verification (if worktree) → Update plan status
```

**Why this is sufficient for bugfixes:** The Behavior Contract defines exactly two properties:
- **Fix Property (C ⟹ P):** Bug-condition tests must pass (bug is fixed)
- **Preservation Property (¬C ⟹ unchanged):** Preservation tests must pass (nothing else broke)

If both properties hold AND the full test suite passes AND process compliance is clean, the bugfix is verified. No sub-agent can add insight beyond what these tests already prove.

---

## Phase A: Verify the Behavior Contract

### Step 3.1: Run & Fix Tests

Run the full test suite (unit + integration) and fix any failures immediately.

**If failures:** Identify → Read test → Fix implementation → Re-run → Continue until all pass

### Step 3.2: Behavior Contract Audit

**⛔ CRITICAL: Explicitly verify the Fix Property and Preservation Property from the plan.**

This is the core verification step for bugfixes — the equivalent of three review agents for features.

1. **Read the Behavior Contract** from the plan file (the `## Behavior Contract` section)

2. **Verify Fix Property (C ⟹ P):** Run the regression tests listed under **"Must Change"** in the Behavior Contract (the `Regression test:` line). Run each individually:
   ```bash
   uv run pytest <test-path>::<test-class>::<test-name> -q
   ```
   Each must PASS (green). If any fail, the fix is incomplete — fix immediately.

3. **Verify Preservation Property (¬C ⟹ unchanged):** Check the **"Must NOT Change"** section's `Preservation:` line.
   - If it lists explicit test names: run each individually and verify they PASS.
   - If it says "Existing test suite": skip this step — the full suite run in Step 3.1 already verified preservation.
   ```bash
   uv run pytest <test-path>::<test-class>::<test-name> -q
   ```
   If any fail, the fix broke existing behavior — fix immediately.

4. **Cross-check scope:** Read the changed production files and confirm changes are limited to what the plan specifies. Flag any unplanned changes (scope creep). The fix should be minimal — if significant unplanned code was added, investigate whether the Behavior Contract still holds.

5. **Report:**

   ```
   ## Behavior Contract Audit

   **Fix Property (C ⟹ P):**
   - ✅ [test name] — PASS (bug condition fixed)

   **Preservation Property (¬C ⟹ unchanged):**
   - ✅ [test name] — PASS (existing behavior preserved)

   **Scope check:** [N files changed, M lines added — matches plan / has unplanned changes]
   ```

### Step 3.3: Process Compliance Check

Run mechanical verification tools:

1. **Type checker** — `basedpyright` / `tsc --noEmit` / equivalent
2. **Linter** — `ruff check` / `eslint` / equivalent
3. **File length** — Check all changed production files (non-test). Any file >300 lines must be refactored. Files >500 lines are a hard blocker.

**Fix all errors before proceeding.** Warnings are acceptable; errors are blockers.

### Step 3.4: Run Plan Verify Commands

**Re-run each task's verification commands to catch regressions.**

For each task in the plan, read its `Verify:` section and run each command:

1. **Wrap each command in a timeout:** `timeout 30 <cmd> || echo 'TIMEOUT'`
2. **If a command fails** → fix immediately (same as Step 3.1 test failure handling)
3. **If a command times out** (30s) → log `TIMEOUT: <command> — deferred to Phase B` and continue

**Skip heuristic for server-dependent commands:** If the command contains `curl`, `wget`, `http://`, `localhost`, `integration`, or `playwright-cli`, defer to Phase B. Log: `DEFERRED to Phase B: <command>`

### Step 3.5: Artifact Existence Check

Verify all planned files exist:

1. **Artifact existence:** Read the plan's task `Files:` sections. For each `Create:` or `Test:` file, verify it exists:
   ```bash
   test -f <path> && echo "OK: <path>" || echo "MISSING: <path>"
   ```

2. **If any file is MISSING** → serious issue. Check if the file was accidentally deleted or never created. Fix immediately.

---

## Phase B: Final Checks

### Step 3.6: Build Verification

Build/compile the project. Verify zero errors.

### Step 3.7: Plan-Specific Runtime Verification

**Only run if the plan's verify commands include runtime checks** (commands containing `curl`, `localhost`, `http://`, or similar runtime-dependent patterns that were deferred in Step 3.4).

If no runtime verify commands were deferred, skip to the Final section.

For any deferred commands:

1. Start the required service (if applicable)
2. Run the deferred verify commands
3. Stop the service
4. Fix any failures immediately

---

## Final

### Step 3.8: Final Regression Check

Run the test suite and type checker one final time to catch any regressions from Phase B fixes (if any code changed):

1. Run full test suite — all pass
2. Run type checker — zero errors
3. Verify build still succeeds

**If no code changed during Phase B**, this confirms the same green state from Phase A. Still run it — it's cheap insurance.

### Step 3.9: Worktree Sync (if worktree is active)

**After all verification passes, sync worktree changes back to the original branch with user approval.**

This is the THIRD user interaction point in the `/spec` workflow (first is worktree choice, second is plan approval).

1. **Extract plan slug** from the plan file path:
   - `docs/plans/2026-02-09-fix-auth.md` → plan_slug = `fix-auth` (strip date prefix and `.md`)

2. **Check for active worktree:**

   ```bash
   ~/.pilot/bin/pilot worktree detect --json <plan_slug>
   # Returns: {"found": true, "path": "...", "branch": "...", "base_branch": "..."} or {"found": false}
   ```

3. **If no worktree is active** (`"found": false`): Skip to Step 3.11 (this is a non-worktree spec run or worktree was already synced).

4. **Pre-sync: Check working tree is clean (MANDATORY)**

   ```bash
   git -C <project_root> status --porcelain
   ```

   **If output is non-empty (dirty working tree):**
   - Report to user: "Cannot sync: the main branch has uncommitted changes. Please commit or `git stash` them first, then re-run `/spec <plan_path>` to resume verification."
   - Do NOT proceed with sync. Step 3.11 will loop back to implementation.

5. **Save plan file to project root (MANDATORY)**

   Plan files are gitignored and live only in the worktree. Copy the plan to the project root before deleting the worktree so it persists locally for reference.

   ```bash
   mkdir -p <project_root>/docs/plans
   cp <worktree_plan_path> <project_root>/docs/plans/<plan_filename>
   ```

6. **Show diff summary:**

   ```bash
   ~/.pilot/bin/pilot worktree diff --json <plan_slug>
   ```

7. **Notify and ask user for sync decision:**

   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Worktree Sync" "<plan_name> — approve merging worktree changes back to main" --plan-path "<plan_path>" 2>/dev/null || true
   ```

   ```
   AskUserQuestion:
     question: "Sync worktree changes to <base_branch>?"
     options:
       - "Yes, squash merge" (Recommended) — Merge all changes as a single commit on <base_branch>
       - "No, keep worktree" — Leave the worktree intact for manual review
       - "Discard all changes" — Remove worktree and branch without merging
   ```

8. **Handle user choice:**

   **If "Yes, squash merge":**

   ```bash
   ~/.pilot/bin/pilot worktree sync --json <plan_slug>
   ```

   If sync fails, report the error and ask user to resolve manually.

   If sync succeeds, clean up **and immediately cd back** in the SAME bash invocation:

   ```bash
   PROJECT_ROOT=$(~/.pilot/bin/pilot worktree cleanup --force --json <plan_slug> | python3 -c "import sys,json; print(json.load(sys.stdin)['project_root'])") && cd "$PROJECT_ROOT"
   ```

   **⛔ NEVER call cleanup and cd in separate Bash tool calls.** Deleting the worktree invalidates the shell's CWD.

   Report: "Changes synced to `<base_branch>` — N files changed, commit `<hash>`"

   **If "No, keep worktree":**
   Report: "Worktree preserved at `<worktree_path>`. You can sync later via `pilot worktree sync <plan-slug>` or discard via `pilot worktree cleanup <plan-slug>`."

   **If "Discard all changes":**

   ```bash
   PROJECT_ROOT=$(~/.pilot/bin/pilot worktree cleanup --force --json <plan_slug> | python3 -c "import sys,json; print(json.load(sys.stdin)['project_root'])") && cd "$PROJECT_ROOT"
   ```

   Report: "Worktree and branch discarded."

### Step 3.10: Post-Merge Verification (worktree sync only)

**After a successful worktree sync, verify the merged code on the base branch before marking VERIFIED.**

**⛔ This step is MANDATORY after a successful "Yes, squash merge" in Step 3.9.** Skip only if no worktree was active or user chose "No, keep worktree" or "Discard all changes".

**Post-merge checks (run on base branch after sync + cleanup):**

1. **Run full test suite** — All tests must pass.
2. **Run type checker / linter** — Zero errors.
3. **Build verification** — Clean build with no errors.

**If any check fails:**

1. Report the specific failure clearly
2. Fix the issue immediately (you are now on the base branch)
3. Re-run the failing check to confirm the fix
4. Re-run the full test suite to catch cascading failures
5. Commit the fix separately (e.g. `fix: resolve post-merge regression from spec/<slug>`)

**⛔ Do NOT proceed to Step 3.11 (VERIFIED) until all post-merge checks pass.**

### Step 3.11: Update Plan Status

**Status Lifecycle:** `PENDING` → `COMPLETE` → `VERIFIED`

**When ALL verification passes (tests green, Behavior Contract verified, process compliant):**

1. **MANDATORY: Update plan status to VERIFIED**
   ```
   Edit the plan file and change the Status line:
   Status: COMPLETE  →  Status: VERIFIED
   ```
2. **Register status change (auto-notifies dashboard):** `~/.pilot/bin/pilot register-plan "<plan_path>" "VERIFIED" 2>/dev/null || true`
3. Read the Iterations count from the plan file
4. Report completion:

   ```
   ✅ Workflow complete! Plan status: VERIFIED

   Summary:
   - [Brief summary of what was fixed]
   - Behavior Contract: Fix Property verified ✅ | Preservation Property verified ✅
   - [Test results: N tests passed]

   💡 Run /clear to free context before starting new work.
   ```

**When verification FAILS (broken tests, unmet Behavior Contract, or unfixed issues):**

1. Add new tasks to the plan for missing fixes
2. **Set status back to PENDING and increment Iterations:**
   ```
   Edit the plan file:
   Status: COMPLETE  →  Status: PENDING
   Iterations: N     →  Iterations: N+1
   ```
3. **Register status change (auto-notifies dashboard):** `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`
4. **Write structured gap table** to the plan file under a `## Verification Gaps` section:

   ```markdown
   ## Verification Gaps

   | Gap | Type | Severity | Affected Files | Fix Description |
   |-----|------|----------|---------------|-----------------|
   | [Fix Property test still failing] | fix_property | must_fix | [files] | [what needs to happen] |
   | [Preservation test broken] | preservation | must_fix | [files] | [revert or fix regression] |
   | [Scope creep detected] | scope | should_fix | [files] | [remove unplanned changes] |
   ```

5. Inform user: "Iteration N+1: Issues found, fixing and re-verifying..."
6. **Invoke implementation phase:** `Skill(skill='spec-implement', args='<plan-path>')`

---

## Context Management

Context is managed automatically by auto-compaction. No agent action needed — just keep working.

ARGUMENTS: $ARGUMENTS
