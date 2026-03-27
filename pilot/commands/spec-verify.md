---
description: "Spec verification phase - tests, execution, rules audit, code review"
argument-hint: "<path/to/plan.md>"
user-invocable: false
effort: high
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

1. **Run code review when enabled** — Step 3.1 launches `spec-reviewer` via `Task(subagent_type="pilot:spec-reviewer")` when `PILOT_SPEC_REVIEWER_ENABLED` is not `"false"` (read in Step 0). To disable, use Console Settings → Reviewers → Code Review toggle.
2. **Only spec-reviewer — NEVER plan-reviewer** — Do NOT launch `plan-reviewer` during verification. Do NOT read or reference `findings-plan-reviewer-*.json` files — they are stale artifacts from the planning phase that were already addressed during implementation. If you encounter a plan-reviewer findings file, **ignore it completely**.
3. **NO stopping** — Everything automatic. Never ask "Should I fix these?"
4. **Fix ALL findings** — must_fix AND should_fix. No permission needed.
5. **Code changes finish BEFORE runtime testing** — Phase A then Phase B.
6. **Plan file is source of truth** — re-read it after auto-compaction, don't rely on conversation memory.
7. **Re-verification after fixes is MANDATORY** — fixes can introduce new bugs.
8. **Quality over speed** — never rush due to context pressure.

---

## Step 0: Read Toggle Configuration

**⛔ Run FIRST, before any other step.** Read the reviewer toggle env var:

```bash
echo "REVIEWER=$PILOT_SPEC_REVIEWER_ENABLED"
```

Reference this value in Steps 3.1, 3.4, and 3.5.

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

### Step 3.0b: Clean Up Stale Plan-Reviewer Findings

**⛔ ALWAYS run this step** — regardless of whether spec-reviewer is enabled. Plan-reviewer findings are stale artifacts from the planning phase that were already addressed during implementation.

```bash
rm -f ~/.pilot/sessions/$PILOT_SESSION_ID/findings-plan-reviewer-*.json
```

### Step 3.1: Launch Code Review Agent (Early)

**⛔ If `PILOT_SPEC_REVIEWER_ENABLED` is `"false"` (from Step 0),** skip this step entirely and proceed to Step 3.2. (Automated checks in Step 3.2 still run; only the agent-based review is skipped.)

**When enabled:** Launch the reviewer IMMEDIATELY — it works in the background while you run automated checks.

#### 3.1a: Gather Context

```bash
git status --short  # Changed files
echo $PILOT_SESSION_ID
```

**Validate session ID:** If `$PILOT_SESSION_ID` is empty, fall back to `"default"` to avoid writing to `~/.pilot/sessions//`.

Collect: changed files list, test framework constraints, runtime environment info, plan risks section.

**Derive plan slug** from the plan filename: strip the date prefix (`YYYY-MM-DD-`) and `.md` extension. Example: `2026-03-02-sku-builder-modal-cleanup.md` → `sku-builder-modal-cleanup`.

Output path: `~/.pilot/sessions/<session-id>/findings-spec-reviewer-<plan-slug>.json`

#### 3.1b: Launch

**⛔ Delete stale spec-reviewer findings before launching** (previous run may have left a file):

```bash
rm -f ~/.pilot/sessions/$PILOT_SESSION_ID/findings-spec-reviewer-*.json
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

  Review implementation: compliance (plan match), quality (security, bugs, tests, performance), goal (achievement, artifacts, wiring).
  Performance: check for expensive uncached work on hot paths, heavy dependency imports with lighter alternatives, and repeated invocations that redo work when input hasn't changed.
  Write findings JSON to output_path using Write tool.
  IMPORTANT: Include the plan file path in your output JSON as the "plan_file" field.
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
7. **Plan verify commands** — For each task's `Verify:` section, run each command wrapped in `timeout 30 <cmd> || echo 'TIMEOUT'`. Defer server-dependent commands (containing `curl`, `localhost`, `http://`, `agent-browser`) to Phase B.
8. **Performance audit** — For each changed file on a hot path (UI render, request handler, polling loop, CLI inner loop): is expensive work (parsing, serialization, I/O, dependency loading) cached/memoized? Are heavy dependencies imported fully when lighter alternatives exist? Does repeated invocation redo work when input hasn't changed? **This is a static code review — no running program needed.** Performance issues from missing caching are structural and visible in the source.

### Step 3.3: Feature Parity Check (migration/refactoring only)

Skip unless the plan has a Feature Inventory section.

1. Compare old vs new implementation
2. Verify each feature exists in new code
3. Run new code and verify same behavior

**If features are MISSING:** Add tasks with `[MISSING]` prefix, set `Status: PENDING`, increment `Iterations`, register status change, invoke `Skill(skill='spec-implement', args='<plan-path>')`.

### Step 3.4: Collect Review Results

**⛔ If `PILOT_SPEC_REVIEWER_ENABLED` is `"false"` (from Step 0 — Step 3.1 was skipped),** skip this step entirely and proceed to Step 3.6 (Phase B). There are no findings to collect.

**When enabled — mandatory. Never skip** — even if you're confident, context is high, or tests pass.

**⛔ NEVER use `TaskOutput`** to retrieve results — it dumps the full agent transcript into context, wasting thousands of tokens.

**Wait for results (bash polling — NOT Read loop):**

```bash
OUTPUT_PATH="<findings-path>"
for i in $(seq 1 50); do [ -f "$OUTPUT_PATH" ] && echo "READY" && break; sleep 10; done
```

Then Read the file once. If not READY after ~8 min, re-launch synchronously.

**⛔ Validate findings:** After reading the JSON, verify that the `plan_file` field matches the current plan path. If it doesn't match, the findings are stale from a previous `/spec` — delete the file, re-launch the reviewer, and wait again.

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

**⛔ If `PILOT_SPEC_REVIEWER_ENABLED` is `"false"` (from Step 0 — Steps 3.1/3.4 were skipped),** skip this step entirely and proceed to Phase B.

**When enabled:** **Skip** when fixes were localized (terminology, error handling, test updates, minor bugs). Run tests + lint to confirm, proceed to Phase B.

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
- **Performance check (UI changes):** Open the page, monitor for lag or high CPU. Watch for: components rendering expensive operations without `useMemo`/`useCallback`, eager loading of all data on mount (lazy-load instead), missing virtualization for large lists, network request storms (N+1 fetches). If page feels sluggish → profile and fix before proceeding.

**Bugs:** Minor → fix, re-run, continue. Major → add task to plan, set PENDING, loop back to implementation.

### Step 3.8: Per-Task DoD Audit

**If runtime profile is Minimal:** Skip.

For EACH task, verify its Definition of Done criteria against the running program with evidence (command output, API response, screenshot).

If any criterion unmet: fix inline if possible, or add task and loop back.

### Step 3.8b: Not Verified Acknowledgment

List what was **NOT** verified and why. Include in the verification report (Step 3.13). Every gap must have a reason:

| Not Verified | Reason |
|-------------|--------|
| [criterion or scenario] | No test environment / Out of scope / Untestable statically / Deferred |

"None — all criteria have automated verification" is a valid answer if true. Do not omit this section: absence of acknowledged gaps ≠ absence of real gaps.

### Step 3.9: E2E Verification (Full profile only)

**If runtime profile is not Full:** Skip.

#### 3.9a: Resolve Browser Session

```bash
AB_SESSION="${PILOT_SESSION_ID:-default}"
# ALL agent-browser commands use: --session "$AB_SESSION"
```

#### 3.9b: Check for Structured Scenarios

Read the plan's `## E2E Test Scenarios` section (if it exists).

**If structured scenarios exist (TS-NNN format):** Follow 3.9c below.

**If no structured scenarios:** Fall back to ad-hoc verification — test the primary user workflow (every view, interaction, state transition), then cover edge cases:

| Category | What to test |
|----------|-------------|
| Empty state | No data, no results |
| Invalid input | Bad params, wrong types, injection |
| Stale state | References to deleted data |
| Error state | Backend unreachable |
| Boundary | Max values, zero, single item |

Then skip to 3.9e (close browser + write results).

#### 3.9c: Execute Structured Scenarios

Create one task per scenario for tracking. Execute Critical first, then High, then Medium.

```
TaskCreate(subject="TS-NNN: [name]", description="[priority] | [preconditions]")
```

**For each scenario:**

1. `TaskUpdate → in_progress`
2. Execute each step exactly as written using `agent-browser --session "$AB_SESSION"`:
   - `open` / `goto` to navigate
   - `snapshot -i` after each interaction to see updated refs
   - `click`, `fill`, `press` per the step's action
   - Verify the expected result by reading the snapshot output
3. **PASS:** All steps match expected results → `TaskUpdate → completed`, note `TS-NNN: PASS`
4. **FAIL:** Step result doesn't match expected:
   - Analyze root cause, implement minimal fix, re-run relevant tests (stay in Phase B — no code changes that need re-review)
   - Re-execute the scenario (counts as fix attempt 1)
   - If still failing: implement second fix, re-execute (fix attempt 2)
   - After 2 failed fix attempts: `TaskUpdate → completed`, note `TS-NNN: KNOWN_ISSUE — [description]`
5. **Critical KNOWN_ISSUE** → set `Status: PENDING`, increment `Iterations`, register status change, invoke `Skill(skill='spec-implement', args='<plan-path>')` — do not proceed to VERIFIED
6. **High/Medium KNOWN_ISSUE** → document and continue (non-blocking)

#### 3.9d: Write E2E Results to Plan

After all scenarios are executed, append to the plan file:

```markdown
## E2E Results

| Scenario | Priority | Result | Fix Attempts | Notes |
|----------|----------|--------|--------------|-------|
| TS-001   | Critical | PASS   | 0            |       |
| TS-002   | High     | PASS   | 1            | Fixed: missing validation on empty submit |
| TS-003   | Medium   | KNOWN_ISSUE | 2       | Tooltip misaligned on narrow viewport |
```

#### 3.9e: Close Browser

```bash
agent-browser --session "$AB_SESSION" close
```

---

## Final

### Step 3.10: Final Regression Check

Re-run full test suite + type checker + build one final time. If code changed during Phase B this catches regressions. If no code changed, it confirms Phase A's green state — cheap insurance.

### Step 3.11: Worktree Sync (if worktree active)

1. Extract plan slug from path (strip date prefix and `.md`)

2. Check: `~/.pilot/bin/pilot worktree detect --json <plan_slug>`

3. **If no worktree:** Skip to Step 3.13.

4. **Save plan to project root** (only if gitignored):
   ```bash
   git -C <project_root> check-ignore -q docs/plans/<plan_filename>
   ```
   If exit 0 (ignored): `cp <worktree_plan_path> <project_root>/docs/plans/<plan_filename>`
   If exit 1 (tracked): skip — the squash merge will bring the updated plan.

5. **Show diff:** `~/.pilot/bin/pilot worktree diff --json <plan_slug>`

6. **Notify and ask:**
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Worktree Sync" "<plan_name> — approve merge" --plan-path "<plan_path>" 2>/dev/null || true
   ```
   AskUserQuestion: "Yes, squash merge" (Recommended) | "No, keep worktree" | "Discard all changes"

7. **Handle choice:**

   **Squash merge:**
   ```bash
   # ⛔ ALL THREE operations MUST be in ONE Bash call chained with &&
   # If sync fails, cleanup MUST NOT run — otherwise work is lost.
   ~/.pilot/bin/pilot worktree sync --json <plan_slug> && PROJECT_ROOT=$(~/.pilot/bin/pilot worktree cleanup --force --json <plan_slug> | jq -r '.project_root') && cd "$PROJECT_ROOT"
   ```
   ⛔ NEVER split sync, cleanup, or cd into separate Bash calls — compaction between them can cause work loss.
   ⛔ The `&&` chain ensures cleanup only runs after a successful sync.

   **Keep worktree:** Report path, user can sync later.
   **Discard:** `cleanup --discard` + `cd` in same bash call (no sync needed — `--discard` explicitly allows deleting unmerged work).

### Step 3.12: Post-Merge Verification (after squash merge only)

**Mandatory after successful worktree sync.** The squash merge can introduce breakage from base branch divergence.

1. Run full test suite
2. Run type checker / linter
3. Build verification
4. Program launch smoke test

If any fails: fix on base branch, re-run, commit fix separately (e.g., `fix: resolve post-merge regression from spec/<slug>`).

**⛔ Do NOT proceed to Step 3.13 until all post-merge checks pass.**

### Step 3.12b: Check for Code Review Feedback

**Run BEFORE marking VERIFIED.** Check if the user has left code review annotations in the Console's Changes tab. Annotations auto-save to the unified JSON — no "Send Feedback" button needed.

Derive the annotation file path: `docs/plans/.annotations/<plan-filename>.json` (same basename as the plan, `.json` extension).

Read the annotation file with the Read tool. If the file doesn't exist, treat as `NO_FEEDBACK`. If it exists, check whether `codeReviewAnnotations` has any entries (`FEEDBACK_EXISTS`) or is empty/missing (`NO_FEEDBACK`).

**If `FEEDBACK_EXISTS`:**
1. Each annotation in `codeReviewAnnotations` has `filePath`, `lineStart`, `lineEnd`, `side`, and `text` (user's annotation)
2. Fix all issues raised (each annotation = a required fix at the indicated file/line)
3. Clear code review annotations: `curl -s -X DELETE "http://localhost:41777/api/annotations/code-review?path=<encoded-plan-path>" > /dev/null 2>&1 || true`
4. Re-run tests and typecheck
5. Continue to Step 3.13

**If `NO_FEEDBACK`:** continue to Step 3.13.

### Step 3.13: Code Review Gate (User Confirmation)

**⛔ MANDATORY before marking VERIFIED.** All automated checks pass — but the user should review the actual code changes.

1. Notify:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Verification Complete — Review Changes" "<plan_name> — please review code in Changes tab" --plan-path "<plan_path>" 2>/dev/null || true
   ```

2. Tell the user:
   ```
   All automated checks passed. Please review the code changes in the Console's **Changes** tab.
   You can leave inline annotations on specific lines using the **Review** mode toggle — annotations save automatically.

   When done:
   - Say **"approve"** or **"lgtm"** to mark the spec as verified
   - Say **"fix"** to have me address your annotations (I'll read them directly from the Console)
   ```

3. Wait for user response:
   - "approve" / "lgtm" / "looks good" → proceed to Step 3.14
   - "fix" / any feedback → re-run Step 3.12b (check for code review annotations in JSON), fix issues, re-run tests, return to Step 3.13
   - If user skips ("continue", "proceed") → treat as approval, proceed to Step 3.14

### Step 3.14: Update Plan Status

**When ALL passes AND user approves:**

1. Set `Status: VERIFIED` in plan
2. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "VERIFIED" 2>/dev/null || true`
3. Report completion with summary:
   ```
   ## Verification Complete
   **Issues Found:** X
   ### Goal Achievement: N/M truths verified
   ### Must Fix (N) | Should Fix (N) | Suggestions (N)
   ### Not Verified: [list items from Step 3.8b, or "None"]
   ```

4. **Instruct the user:** Include in your completion message:
   ```
   Run /clear before starting new work — this resets context while keeping project rules loaded.
   ```

**When verification FAILS (missing features, serious bugs — before reaching Step 3.13):**

1. Add fix tasks to plan
2. Set `Status: PENDING`, increment `Iterations`
3. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`
4. Write `## Verification Gaps` table to plan (overwrite if exists):
   ```markdown
   | Gap | Type | Severity | Affected Files | Fix Description |
   ```
5. Invoke `Skill(skill='spec-implement', args='<plan-path>')`

ARGUMENTS: $ARGUMENTS
