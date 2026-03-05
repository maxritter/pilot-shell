---
description: "Spec verification phase - tests, execution, rules audit, code review"
argument-hint: "<path/to/plan.md>"
user-invocable: false
model: sonnet
hooks:
  Stop:
    - command: uv run python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_verify_validator.py"
---

# /spec-verify - Verification Phase

**Phase 3 of the /spec workflow (features).** Runs comprehensive verification: automated checks, code review, program execution, and E2E tests. For bugfix plans, use `spec-bugfix-verify` instead.

**Input:** Plan file with `Status: COMPLETE`
**Output:** Plan status → VERIFIED (success) or loop back to implementation (failure)

---

## ⛔ KEY CONSTRAINTS

1. **NEVER SKIP code review** — Step 3.1 launches `spec-reviewer` via `Task(subagent_type="pilot:spec-reviewer")`. Mandatory.
2. **NO stopping** — Everything automatic. Never ask "Should I fix these?"
3. **Fix ALL findings** — must_fix AND should_fix. No permission needed.
4. **Code changes finish BEFORE runtime testing** — Phase A then Phase B.
5. **Plan file is source of truth** — re-read it after auto-compaction, don't rely on conversation memory.
6. **Re-verification after fixes is MANDATORY** — fixes can introduce new bugs.
7. **Quality over speed** — never rush due to context pressure.

---

## The Process

```
Phase A — Finalize the code:
  Launch Reviewer → Automated Checks (tests + lint + verify commands) → Feature Parity (if migration) → Collect Review Results → Fix

Phase B — Verify the running program (depth depends on runtime profile):
  Build → Program Execution → Per-Task DoD Audit → E2E

Final:
  Regression check → Worktree sync → Post-merge verification → Update status
```

---

## Step 3.0: Classify Runtime Profile

**Determine verification depth based on what changed:**

| Profile | Criteria | Phase B Scope |
|---------|----------|---------------|
| **Minimal** | No server, no UI, no built artifacts (libraries, CLI tools, hooks, scripts) | Build check only |
| **API** | Server/API but no frontend changes | Build + program execution + DoD audit. Skip E2E. |
| **Full** | Frontend/UI changes or complex deployment | All Phase B steps |

Read the plan's Runtime Environment section (if present) and the changed file types to classify.

---

## Phase A: Finalize the Code

### Step 3.1: Launch Code Review Agent (Early)

Launch the reviewer IMMEDIATELY — it works in the background while you run automated checks.

#### 3.1a: Gather Context

```bash
git status --short  # Changed files
echo $PILOT_SESSION_ID
```

**Validate session ID:** If `$PILOT_SESSION_ID` is empty, fall back to `"default"` to avoid writing to `~/.pilot/sessions//`.

Collect: changed files list, test framework constraints, runtime environment info, plan risks section.

Output path: `~/.pilot/sessions/<session-id>/findings-spec-reviewer.json`

#### 3.1b: Launch

**⛔ Delete stale findings before launching** (same path may exist from a previous `/spec` in this session):

```bash
rm -f "$OUTPUT_PATH"
```

```
Task(
  subagent_type="pilot:spec-reviewer",
  run_in_background=true,
  prompt="""
  **Plan file:** <plan-path>
  **Changed files:** [file list]
  **Output path:** <absolute path to findings JSON>
  **Runtime environment:** [how to start, port, deploy path]
  **Test framework constraints:** [what it can/cannot test]

  Review implementation: compliance (plan match), quality (security, bugs, tests), goal (achievement, artifacts, wiring).
  Write findings JSON to output_path using Write tool.
  """
)
```

**Do NOT wait.** Proceed to Step 3.2 immediately.

### Step 3.2: Automated Checks

Run all mechanical checks in sequence. Fix any failures before proceeding.

1. **Full test suite** — `uv run pytest -q` / `bun test` / `npm test`. Fix failures immediately.
2. **Type checker** — `basedpyright` / `tsc --noEmit`. Zero errors required.
3. **Linter** — `ruff check` / `eslint`. Errors are blockers, warnings acceptable.
4. **Coverage** — Verify ≥ 80%.
5. **Build** — Clean build, zero errors.
6. **File length** — Changed production files (non-test): >800 lines consider splitting, >1000 flag for review.
7. **Plan verify commands** — For each task's `Verify:` section, run each command wrapped in `timeout 30 <cmd> || echo 'TIMEOUT'`. Defer server-dependent commands (containing `curl`, `localhost`, `http://`, `playwright-cli`) to Phase B.

### Step 3.3: Feature Parity Check (migration/refactoring only)

Skip unless the plan has a Feature Inventory section.

1. Compare old vs new implementation
2. Verify each feature exists in new code
3. Run new code and verify same behavior

**If features are MISSING:** Add tasks with `[MISSING]` prefix, set `Status: PENDING`, increment `Iterations`, register status change, invoke `Skill(skill='spec-implement', args='<plan-path>')`.

### Step 3.4: Collect Review Results

**⛔ MANDATORY. Never skip** — even if you're confident, context is high, or tests pass.

**⛔ NEVER use `TaskOutput`** to retrieve results — it dumps the full agent transcript into context, wasting thousands of tokens.

**Wait for results (bash polling — NOT Read loop):**

```bash
OUTPUT_PATH="<findings-path>"
for i in $(seq 1 50); do [ -f "$OUTPUT_PATH" ] && echo "READY" && break; sleep 10; done
```

Then Read the file once. If not READY after ~8 min, re-launch synchronously.

#### Fix Findings

**Fix automatically — no user permission needed.**

1. **must_fix** → Fix immediately (security, crashes, TDD violations)
2. **should_fix** → Fix immediately (spec deviations, missing tests, error handling)
3. **suggestions** → Implement if quick

For each fix: implement → run relevant tests → log "Fixed: [title]"

**Report:**
```
## Code Verification Complete
**Issues Found:** X
### Goal Achievement: N/M truths verified
### Must Fix (N) | Should Fix (N) | Suggestions (N)
```

### Step 3.5: Re-verification (Only for Structural Fixes)

**Skip** when fixes were localized (terminology, error handling, test updates, minor bugs). Run tests + lint to confirm, proceed to Phase B.

**Re-verify** when fixes required new functionality, changed APIs, or significant new code paths: re-launch spec-reviewer, fix new findings. Max 2 iterations before adding remaining issues to plan.

---

## Phase B: Verify the Running Program

All code is finalized. No more code changes except critical bugs found during execution.

**If runtime profile is Minimal:** Run build check (Step 3.6a), then skip to Final section.

### Step 3.6: Build, Deploy, and Verify Code Identity

#### 3.6a: Build

Build/compile the project. Verify zero errors.

#### 3.6b: Deploy (if applicable)

If project builds artifacts deployed separately from source: copy to install location, restart services. Check `ps aux | grep <service>` before restarting shared services.

#### 3.6c: Code Identity Verification

**⛔ Prove the running instance uses your new code before testing it.**

1. Identify a behavioral change unique to this implementation
2. Craft a request only new code handles correctly (e.g., query with new parameter — new code returns filtered results, old code ignores parameter)
3. If response matches OLD behavior → redeploy, restart, re-verify
4. **Do NOT proceed** to execution testing until code identity is confirmed

### Step 3.7: Program Execution Verification

**If runtime profile is Minimal:** Skip.

**⚠️ Parallel spec warning:** Before starting a server, check port availability: `lsof -i :<port>`. If another `/spec` session occupies it, wait or use a different port.

- Program starts without errors
- Inspect logs for errors/warnings/stack traces
- **Verify output correctness** — fetch source data independently, compare against program output. If mismatch → BUG.
- Test with real/sample data

**Bugs:** Minor → fix, re-run, continue. Major → add task to plan, set PENDING, loop back to implementation.

### Step 3.8: Per-Task DoD Audit

**If runtime profile is Minimal:** Skip.

For EACH task, verify its Definition of Done criteria against the running program with evidence (command output, API response, screenshot).

If any criterion unmet: fix inline if possible, or add task and loop back.

### Step 3.9: E2E Verification (Full profile only)

**If runtime profile is not Full:** Skip.

#### 3.9a: Resolve Playwright Session

```bash
PW_SESSION="${PILOT_SESSION_ID:-default}"
# ALL playwright-cli commands use: -s="$PW_SESSION"
```

#### 3.9b: Happy Path

Test the primary user workflow end-to-end. Walk through main scenario: every view, interaction, state transition.

#### 3.9c: Edge Cases

| Category | What to test |
|----------|-------------|
| Empty state | No data, no results |
| Invalid input | Bad params, wrong types, injection |
| Stale state | References to deleted data |
| Error state | Backend unreachable |
| Boundary | Max values, zero, single item |

```bash
playwright-cli -s="$PW_SESSION" close  # Cleanup after E2E
```

---

## Final

### Step 3.10: Final Regression Check

Re-run full test suite + type checker + build one final time. If code changed during Phase B this catches regressions. If no code changed, it confirms Phase A's green state — cheap insurance.

### Step 3.11: Worktree Sync (if worktree active)

1. Extract plan slug from path (strip date prefix and `.md`)

2. Check: `~/.pilot/bin/pilot worktree detect --json <plan_slug>`

3. **If no worktree:** Skip to Step 3.13.

4. **Pre-sync:** Verify clean working tree on base branch:
   ```bash
   git -C <project_root> status --porcelain
   ```
   If dirty: report "Cannot sync: main branch has uncommitted changes. Please commit or `git stash` first, then re-run `/spec <plan_path>`." Do NOT proceed.

5. **Save plan to project root** (gitignored, local reference):
   ```bash
   mkdir -p <project_root>/docs/plans
   cp <worktree_plan_path> <project_root>/docs/plans/<plan_filename>
   ```

6. **Show diff:** `~/.pilot/bin/pilot worktree diff --json <plan_slug>`

7. **Notify and ask:**
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Worktree Sync" "<plan_name> — approve merge" --plan-path "<plan_path>" 2>/dev/null || true
   ```
   AskUserQuestion: "Yes, squash merge" (Recommended) | "No, keep worktree" | "Discard all changes"

8. **Handle choice:**

   **Squash merge:**
   ```bash
   ~/.pilot/bin/pilot worktree sync --json <plan_slug>
   # Then cleanup + cd in SAME bash call:
   PROJECT_ROOT=$(~/.pilot/bin/pilot worktree cleanup --force --json <plan_slug> | python3 -c "import sys,json; print(json.load(sys.stdin)['project_root'])") && cd "$PROJECT_ROOT"
   ```
   ⛔ NEVER call cleanup and cd in separate Bash calls — worktree deletion invalidates CWD.

   **Keep worktree:** Report path, user can sync later.
   **Discard:** Same cleanup+cd command as above.

### Step 3.12: Post-Merge Verification (after squash merge only)

**Mandatory after successful worktree sync.** The squash merge can introduce breakage from base branch divergence.

1. Run full test suite
2. Run type checker / linter
3. Build verification
4. Program launch smoke test

If any fails: fix on base branch, re-run, commit fix separately (e.g., `fix: resolve post-merge regression from spec/<slug>`).

**⛔ Do NOT proceed to Step 3.13 until all post-merge checks pass.**

### Step 3.13: Update Plan Status

**When ALL passes:**

1. Set `Status: VERIFIED` in plan
2. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "VERIFIED" 2>/dev/null || true`
3. Report completion with summary

**When verification FAILS (missing features, serious bugs):**

1. Add fix tasks to plan
2. Set `Status: PENDING`, increment `Iterations`
3. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`
4. Write `## Verification Gaps` table to plan (overwrite if exists):
   ```markdown
   | Gap | Type | Severity | Affected Files | Fix Description |
   ```
5. Invoke `Skill(skill='spec-implement', args='<plan-path>')`

ARGUMENTS: $ARGUMENTS
