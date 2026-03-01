---
description: "Spec verification phase - tests, execution, rules audit, code review"
argument-hint: "<path/to/plan.md>"
user-invocable: false
model: opus
hooks:
  Stop:
    - command: uv run python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_verify_validator.py"
---

# /spec-verify - Verification Phase

**Phase 3 of the /spec workflow (features).** Runs comprehensive verification: tests, process compliance, code review, program execution, E2E tests, and edge case testing. For bugfix plans, use `spec-bugfix-verify` instead — it runs a lighter pipeline focused on Behavior Contract audit without sub-agents.

**Input:** Path to a plan file with `Status: COMPLETE`
**Output:** Plan status set to VERIFIED (success) or looped back to implementation (failure)
**On success:** Workflow complete
**On failure:** → `Skill(skill='spec-implement', args='<plan-path>')` to fix issues

---

## ⛔ KEY CONSTRAINTS (Rules Summary)

| #   | Rule                                                                                                                                                                                                                                                           |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **NEVER SKIP verification** - Code review (Step 3.0/3.7) launches `spec-reviewer` via the **Task tool** (`subagent_type="pilot:spec-reviewer"`). Mandatory. No exceptions. |
| 2   | **NO stopping** - Everything is automatic. Never ask "Should I fix these?"                                                                                                                                                                                     |
| 3   | **Fix ALL findings automatically** - must_fix AND should_fix. No permission needed.                                                                                                                                                                            |
| 4   | **Quality over speed** - Never rush due to context pressure                                                                                                                                                                                                    |
| 5   | **Plan file is source of truth** - Survives across auto-compaction cycles                                                                                                                                                                                      |
| 6   | **Code changes finish BEFORE runtime testing** - Code review and fixes happen before build/deploy/E2E                                                                                                                                                          |
| 7   | **Re-verification after fixes is MANDATORY** - Fixes can introduce new bugs. Always re-verify.                                                                                                                                                                 |

---

## The Process

The verification process is split into two phases. All code changes (from review findings) happen in Phase A. All runtime testing happens in Phase B against the finalized code.

```
Phase A — Finalize the code:
  Launch Reviewers (3 parallel) → Tests → Process Compliance → Plan Verify Commands → Artifact Existence Check → Feature Parity → Call Chain → Collect Review Results → Fix → Re-verify loop

Phase B — Verify the running program:
  Build → Deploy → Code Identity Check → Program Execution → Per-Task DoD Audit → E2E → Edge Cases

Final:
  Regression check → Worktree sync → Post-merge verification (if worktree) → Update plan status
```

**Why this order:** Code review findings change the code. If you run E2E before code review, you test unfixed code and must re-test after fixes. By finishing all code changes first, E2E tests the final product exactly once.

**All test levels are MANDATORY:** Unit tests alone are insufficient. You must run integration tests AND E2E tests AND execute the actual program with real data.

---

## Phase A: Finalize the Code

### Step 3.0: Launch Code Review Agent (Early Launch)

**⛔ CRITICAL: Launch the review agent IMMEDIATELY at the start of Phase A, before any other verification steps.**

This early-launch pattern maximizes efficiency: the agent begins reading the plan and reviewing code while the main session continues with automated checks (tests, lint, feature parity, call chain). By the time Step 3.7 collects results, the agent is done or nearly done.

#### 3.0a: Identify Changed Files

Get list of files changed in this implementation:

```bash
git status --short  # Shows staged and unstaged changes
```

#### 3.0b: Gather Context for the Reviewer

Collect information needed for actionable findings:

1. **Test framework constraints** — What can/can't the test framework test? (e.g., "SSR-only via renderToString — no client-side effects or state testing possible")
2. **Runtime environment** — How to start the program, what port, where artifacts are deployed
3. **Plan risks section** — Copy the Risks and Mitigations table from the plan (if present)

#### 3.0c: Resolve Session Path for Findings Persistence

**⛔ CRITICAL: The agent writes findings to a file so they survive agent lifecycle cleanup.**

Background agents' return values can be lost after completion. To guarantee findings are retrievable, the agent writes its JSON to a known file path.

```bash
echo $PILOT_SESSION_ID
```

**⚠️ Validate the session ID is set.** If `$PILOT_SESSION_ID` is empty, fall back to `"default"` to avoid writing to `~/.pilot/sessions//`.

Define output path (replace `<session-id>` with the resolved value):

- **Reviewer findings:** `~/.pilot/sessions/<session-id>/findings-spec-reviewer.json`

#### 3.0d: Launch the Reviewer

The agent has `background: true` in its definition, so it runs in the background automatically. As a fallback, also set `run_in_background=true`.

```
Task(
  subagent_type="pilot:spec-reviewer",
  run_in_background=true,
  prompt="""
  **Plan file:** <plan-path>
  **Changed files:** [file list from git status]
  **Output path:** <absolute path to findings-spec-reviewer.json>

  **Runtime environment:** [how to start, port, deploy path, etc.]
  **Test framework constraints:** [what the test framework can/cannot test]

  Review this implementation in three phases:
  1. Compliance: verify implementation matches plan, DoD criteria met, risk mitigations implemented
  2. Quality: read all quality-relevant rules, then check code quality, security, testing, performance, error handling
  3. Goal: verify goal achievement, artifact completeness (exists/substantive/wired), stub detection, anti-patterns

  The plan may contain a `## Goal Verification` section with explicit `### Truths`,
  `### Artifacts`, and `### Key Links` subsections — use those as your starting point
  if present.

  **IMPORTANT:** Write your final findings JSON to the output_path using the Write tool.
  """
)
```

The agent reads the plan and changed files once and performs all three review phases, persisting a single findings JSON to the session directory.

#### 3.0e: Continue with Automated Checks

**Do NOT wait for agent results.** Proceed immediately to Step 3.1. The agent works in the background while you run tests, linters, verify commands, artifact checks, feature parity, and call chain analysis.

### Step 3.1: Run & Fix Tests

Run the full test suite (unit + integration) and fix any failures immediately.

**If failures:** Identify → Read test → Fix implementation → Re-run → Continue until all pass

### Step 3.2: Process Compliance Check

Run mechanical verification tools. These check process adherence that the code review agent cannot assess.

**Run each tool and show output:**

1. **Type checker** — `tsc --noEmit` / `basedpyright` / equivalent
2. **Linter** — `eslint` / `ruff check` / equivalent
3. **Coverage** — Run with coverage flag, verify ≥ 80%
4. **Build** — Clean build with no errors

5. **File length** — Check all changed production files (non-test). Any file >300 lines must be refactored (split into focused modules using TDD: write tests first, then extract). Files >500 lines are a hard blocker.

**Fix all errors before proceeding.** Warnings are acceptable; errors are blockers.

**Note:** The review agents (launched in Step 3.0) handle code quality, spec compliance, rules enforcement, and goal achievement. This step only covers mechanical tool checks that produce binary pass/fail results.

### Step 3.3: Run Plan Verify Commands

**Re-run each task's verification commands to catch regressions.**

For each task in the plan, read its `Verify:` section and run each command:

1. **Wrap each command in a timeout:** `timeout 30 <cmd> || echo 'TIMEOUT'`
2. **If a command fails** → fix immediately (same as Step 3.1 test failure handling)
3. **If a command times out** (30s) → log `TIMEOUT: <command> — deferred to Phase B` and continue

**Skip heuristic for server-dependent commands:** If the command contains `curl`, `wget`, `http://`, `localhost`, `integration`, or `playwright-cli`, defer to Phase B. Log: `DEFERRED to Phase B: <command>`

This re-validates task-specific acceptance criteria that were checked during implementation but might have regressed due to later tasks.

### Step 3.4: Artifact Existence & Quick Wiring Scan

**Verify all planned files exist and are connected.**

1. **Artifact existence:** Read the plan's task `Files:` sections. For each `Create:` file, verify it exists:
   ```bash
   test -f <path> && echo "OK: <path>" || echo "MISSING: <path>"
   ```

2. **Quick wiring scan:** For each changed file, check it's imported by at least one other file:
   ```bash
   grep -r "import.*<filename-without-ext>" --include="*.ts" --include="*.tsx" --include="*.py" | grep -v "<the-file-itself>"
   ```

3. **Entry points are exempt from import checks:** route files, main files, test files, CLI entry points, hook scripts, config files.

4. **If any file is MISSING** → this is a serious issue. Check if the file was accidentally deleted or never created. Fix immediately.

5. **If any file appears orphaned** (no imports) → note it for cross-reference with the spec-reviewer's deeper wiring analysis in Step 3.7.

This is a fast sanity check (~30 seconds) that catches obvious issues before the spec-reviewer's deeper analysis arrives.

### Step 3.5: Feature Parity Check (if applicable)

**For refactoring/migration tasks only:** Verify ALL original functionality is preserved.

**Process:**

1. Compare old implementation with new implementation
2. Create checklist of features from old code
3. Verify each feature exists in new code
4. Run new code and verify same behavior as old code

**If features are MISSING:**

This is a serious issue - the implementation is incomplete.

1. **Add new tasks to the plan file:**
   - Read the existing plan
   - Add new tasks for each missing feature (follow existing task format)
   - Mark new tasks with `[MISSING]` prefix in task title
   - Update the Progress Tracking section with new task count
   - Add note: `> Extended [Date]: Tasks X-Y added for missing features found during verification`

2. **Set plan status to PENDING and increment Iterations:**

   ```
   Edit the plan file:
   Status: COMPLETE  →  Status: PENDING
   Iterations: N     →  Iterations: N+1
   ```

3. **Register status change:** `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`

4. **Inform user:**

   ```
   🔄 Iteration N+1: Missing features detected, looping back to implement...

   Found [N] missing features that need implementation:
   - [Feature 1]
   - [Feature 2]

   The plan has been updated with [N] new tasks.
   ```

5. **Invoke implementation phase:** `Skill(skill='spec-implement', args='<plan-path>')`

### Step 3.6: Call Chain Analysis

**Perform deep impact analysis for all changes:**

1. **Trace Upwards (Callers):**
   - Identify all code that calls modified functions
   - Verify they handle new return values/exceptions
   - Check for breaking changes in interfaces

2. **Trace Downwards (Callees):**
   - Identify all dependencies of modified code
   - Verify correct parameter passing
   - Check error handling from callees

3. **Side Effect Analysis:**
   - Database state changes
   - Cache invalidation needs
   - External system impacts
   - Global state modifications

### Step 3.7: Collect Review Results

**⛔ THIS STEP IS NON-NEGOTIABLE. You MUST collect and process review findings.**

**⚠️ SKIPPING THIS STEP IS FORBIDDEN.** Even if:

- You're confident the code is correct
- Context is getting high (finish verification first — auto-compact handles context automatically)
- Tests pass (tests don't catch everything)
- The implementation seems simple

**None of these are valid reasons to skip. ALWAYS COLLECT AND PROCESS RESULTS.**

#### 3.7a: Retrieve and Fix Findings

The review agent (launched in Step 3.0) should be done or nearly done by now. Its findings are persisted to a file in the session directory.

**⛔ NEVER use `TaskOutput` to retrieve agent results.** TaskOutput dumps the full verbose agent transcript (all JSON messages, hook progress, tool calls) into context, wasting thousands of tokens. Instead, poll the output file with the Read tool.

**⚠️ IMPORTANT: Wait between polling attempts.** Run `sleep 10` via Bash before each Read attempt. The agent typically takes 3-7 minutes. Rapid-fire Read calls waste context and produce dozens of "file not found" errors.

1. **Wait 10 seconds, then attempt to read the findings file** using the Read tool on the path defined in Step 3.0c:
   - `~/.pilot/sessions/<session-id>/findings-spec-reviewer.json`
2. **If the file doesn't exist yet** → run `sleep 10` and retry. Repeat up to 50 times before considering the agent failed.
3. **When the file is ready**, fix findings by severity: must_fix → should_fix → suggestion

**If the findings file is still missing after 50 retries** (agent failed to write):

1. Re-launch the agent synchronously (without `run_in_background`) with the same prompt
2. If the synchronous re-launch also fails, log the failure and continue

**The `truths` array** in the findings JSON captures goal verification status. Include it in the report.

**Expected timeline:**

- Agent was launched before Step 3.1 (tests, lint, verify commands, artifact checks, feature parity, call chain)
- Steps 3.1-3.6 typically take 3-7 minutes
- Agent typically completes in 3-7 minutes
- Net result: Agent finishes around the same time as Step 3.6, minimal or zero wait time

#### 3.7b: Report Findings

As you collect and fix findings, present them briefly:

```
## Code Verification Complete

**Issues Found:** X

### Goal Achievement: N/M truths verified
### Must Fix (N) | Should Fix (N) | Suggestions (N)

Implementing fixes automatically...
```

#### 3.7c: Fix Severity Order

**⛔ DO NOT ask user for permission. Fix everything automatically.**

This is part of the automated /spec workflow. The user approved the plan - verification fixes are part of that approval. Never stop to ask "Should I fix these?" or "Want me to address these findings?"

**Implementation order (by severity):**

1. **must_fix issues** - Fix immediately (security, crashes, TDD violations)
2. **should_fix issues** - Fix immediately (spec deviations, missing tests, error handling)
3. **suggestions** - Implement if reasonable and quick

**For each fix:**

1. Implement the fix
2. Run relevant tests to verify
3. Log: "✅ Fixed: [issue title]"

### Step 3.8: Re-verification (Only When Looping Back to Implementation)

Re-verification is **only required when fixes are structural enough to warrant looping back to the implementation phase** (e.g., adding new plan tasks, architectural changes, major logic rewrites).

**Skip re-verification when:** Fixes were localized (terminology cleanup, error handling improvements, test updates, docstring fixes, minor bug fixes). Run tests + lint to confirm fixes don't break anything, then proceed to Phase B.

**Re-verify when:** Fixes required new functionality, changed APIs, modified hook behavior, or added significant new code paths. In this case:

1. Re-run the spec-reviewer agent (same as Step 3.0d)
2. Fix any new must_fix or should_fix findings
3. Maximum 2 iterations before adding remaining issues to plan

If issues require going back to implementation, add tasks to plan. Then invoke `Skill(skill='spec-implement', args='<plan-path>')`

---

## Phase B: Verify the Running Program

All code is now finalized. No more code changes should happen in this phase (except critical bugs found during execution).

### Step 3.9: Build, Deploy, and Verify Code Identity

**⚠️ CRITICAL: Tests passing ≠ Program works. And building ≠ running your build.**

#### 3.9a: Build

Build/compile the project. Verify zero errors.

#### 3.9b: Deploy (if applicable)

If the project builds artifacts that are deployed separately from source (e.g., bundled JS, compiled binaries, Docker images):

1. Identify where built artifacts are installed (e.g., `~/.claude/pilot/scripts/`)
2. Copy new builds to the installed location
3. Restart any running services that use the old artifacts

**⚠️ Parallel spec warning:** Deploy paths are shared OS resources. If another `/spec` session deploys to the same path, Code Identity Verification (3.9c) becomes unreliable. Check `ps aux | grep <service>` before restarting shared services.

**If no separate deployment is needed, skip to 3.9c.**

#### 3.9c: Code Identity Verification (MANDATORY)

**Before testing ANY endpoint or behavior, prove the running instance uses your newly built code.**

1. Identify a behavioral change unique to this implementation (new query parameter, changed response field, new endpoint, different behavior for specific input)
2. Craft a request that ONLY the new code would handle correctly (e.g., filter by nonexistent value should return 0 results; old code returns unfiltered results)
3. Execute the request against the running program
4. **If the response matches OLD behavior** → you are testing stale code
   - Redeploy artifacts
   - Restart the service
   - Re-verify until the response matches NEW behavior
5. **If the response matches NEW behavior** → proceed

**Example:** You added `?project=` filtering. Query `?project=nonexistent-xyz`. New code returns 0 results. Old code ignores the parameter and returns all results. If you see all results, you're testing old code.

**⛔ DO NOT proceed to program execution testing until code identity is confirmed.**

### Step 3.10: Program Execution Verification

Run the actual program and verify real output.

**⚠️ Parallel spec warning:** Before starting a server, check if the port is already in use: `lsof -i :<port>`. If another `/spec` session occupies it, wait for it to finish Phase B or use a different port.

**Execution checklist:**

- [ ] Program starts without errors
- [ ] **Inspect logs** - Check for errors, warnings, stack traces
- [ ] **Verify output correctness** - Fetch source data independently, compare against program output
- [ ] Test with real/sample data, not just mocks

**⛔ Output Correctness - MANDATORY:**
If code processes external data, ALWAYS verify by fetching source data independently and comparing:

```bash
# Fetch actual source data (database query, API call, file contents)
# Compare counts/content with what your code returned
# If mismatch → BUG (don't trust program output alone)
```

**If bugs are found:**

| Bug Type                                                       | Action                                                                                                                      |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Minor** (typo, off-by-one, missing import)                   | Fix immediately, re-run, continue verification                                                                              |
| **Major** (logic error, missing function, architectural issue) | Add task to plan, set PENDING, then `Skill(skill='spec-implement', args='<plan-path>')` |

### Step 3.11: Per-Task DoD Audit

**Task completion ≠ Goal achievement.** The `spec-reviewer` agent (Step 3.0) already performed static goal-backward verification (truths → artifacts → wiring) in Phase A. Its `truths` array provides evidence of structural completeness. This step focuses on **runtime DoD verification** — checking each task's acceptance criteria against the running program.

**For EACH task in the plan**, read its Definition of Done criteria and verify each criterion is met with evidence from the running program.

```markdown
### Task N: [title]

- [ ] DoD criterion 1 → [evidence: command output / API response / screenshot]
- [ ] DoD criterion 2 → [evidence]
      ...
```

**If any criterion is unmet (at either goal or task level):**

- If fixable inline → fix immediately
- If structural → add task to plan and loop back to implementation

### Step 3.12: E2E Verification (MANDATORY for apps with UI/API)

**⚠️ Unit + Integration tests are NOT enough. You MUST also run E2E tests.**

#### 3.12.0: Resolve Playwright Session (MANDATORY before any playwright-cli usage)

**⛔ Parallel `/spec` sessions WILL interfere if you use bare `playwright-cli` commands.** Always use a session-scoped browser instance.

```bash
PW_SESSION="${PILOT_SESSION_ID:-default}"
```

**ALL `playwright-cli` commands in this phase MUST use `-s="$PW_SESSION"`:**

```bash
playwright-cli -s="$PW_SESSION" open <url>
playwright-cli -s="$PW_SESSION" snapshot
playwright-cli -s="$PW_SESSION" click e1
# ... etc
```

**Cleanup at the end of E2E testing (after Step 3.12b):**

```bash
playwright-cli -s="$PW_SESSION" close
```

#### 3.12a: Happy Path Testing

Test the primary user workflow end-to-end.

**For APIs:** Test endpoints with curl. Verify status codes, response content, and state changes.

**For Frontend/UI:** Use `playwright-cli -s="$PW_SESSION"` to verify UI renders and workflows complete. See `~/.claude/rules/playwright-cli.md`.

Walk through the main user scenario described in the plan. Every view, every interaction, every state transition.

#### 3.12b: Edge Case and Negative Testing

After the happy path passes, test failure modes. **This is not optional.**

| Category          | What to test                                    | Example                                                          |
| ----------------- | ----------------------------------------------- | ---------------------------------------------------------------- |
| **Empty state**   | No data, no items, no results                   | Empty database, no projects, search returns nothing              |
| **Invalid input** | Bad parameters, wrong types                     | SQL injection in query params, empty strings, special characters |
| **Stale state**   | Cached/stored data references something deleted | localStorage has project name that no longer exists              |
| **Error state**   | Backend unreachable, API returns error          | What does the UI show when fetch fails?                          |
| **Boundary**      | Maximum values, zero values, single item        | Exactly 1 project, 0 observations, 100-char project name         |

For each edge case:

1. Set up the condition
2. Exercise the UI/API
3. Verify the result is reasonable (not blank, not broken, not stuck, no unhandled errors)

**After all E2E testing completes, close the playwright session:**

```bash
playwright-cli -s="$PW_SESSION" close
```

### Step 3.13: Final Regression Check

Run the test suite and type checker one final time to catch any regressions from Phase B fixes (if any code changed during execution/E2E testing):

1. Run full test suite — all pass
2. Run type checker — zero errors
3. Verify build still succeeds

**If no code changed during Phase B** (no bugs found during execution/E2E), this confirms the same green state from Phase A. Still run it — it's cheap insurance.

### Step 3.13b: Worktree Sync (if worktree is active)

**After all verification passes, sync worktree changes back to the original branch with user approval.**

This is the THIRD user interaction point in the `/spec` workflow (first is worktree choice, second is plan approval).

1. **Extract plan slug** from the plan file path:
   - `docs/plans/2026-02-09-add-auth.md` → plan_slug = `add-auth` (strip date prefix and `.md`)

2. **Check for active worktree:**

   ```bash
   ~/.pilot/bin/pilot worktree detect --json <plan_slug>
   # Returns: {"found": true, "path": "...", "branch": "...", "base_branch": "..."} or {"found": false}
   ```

3. **If no worktree is active** (`"found": false`): Skip to Step 3.14 (this is a non-worktree spec run or worktree was already synced).

4. **Pre-sync: Check working tree is clean (MANDATORY)**

   The sync requires a clean working tree on the base branch. Check now and stop if dirty:

   ```bash
   git -C <project_root> status --porcelain
   ```

   **If output is non-empty (dirty working tree):**
   - Report to user: "Cannot sync: the main branch has uncommitted changes. Please commit or `git stash` them first, then re-run `/spec <plan_path>` to resume verification."
   - Do NOT proceed with sync. Step 3.14 will loop back to implementation.

5. **Save plan file to project root (MANDATORY)**

   Plan files are gitignored and live only in the worktree. Copy the plan to the project root before deleting the worktree so it persists locally for reference.

   ```bash
   # plan_path is the worktree-relative path, e.g. .worktrees/spec-slug-hash/docs/plans/2026-02-09-slug.md
   # Compute the destination in the project root:
   mkdir -p <project_root>/docs/plans
   cp <worktree_plan_path> <project_root>/docs/plans/<plan_filename>
   ```

   This file is gitignored and will NOT be committed. It stays on disk for local reference only.

6. **Show diff summary:**

   ```bash
   ~/.pilot/bin/pilot worktree diff --json <plan_slug>
   # Returns JSON with changed files list
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
   # Returns: {"success": true, "files_changed": N, "commit_hash": "..."} or {"success": false, "error": "..."}
   ```

   If sync fails (e.g. merge conflict), report the error and ask user to resolve manually.

   If sync succeeds, clean up **and immediately cd back** in the SAME bash invocation. The shell CWD will be invalid after the worktree is deleted — combining them prevents the broken-shell issue:

   ```bash
   PROJECT_ROOT=$(~/.pilot/bin/pilot worktree cleanup --force --json <plan_slug> | python3 -c "import sys,json; print(json.load(sys.stdin)['project_root'])") && cd "$PROJECT_ROOT"
   ```

   **⛔ NEVER call cleanup and cd in separate Bash tool calls.** Deleting the worktree invalidates the shell's CWD. Every subsequent Bash call will fail with exit code 1 until the session restarts.

   Report: "Changes synced to `<base_branch>` — N files changed, commit `<hash>`"

   **If "No, keep worktree":**
   Report: "Worktree preserved at `<worktree_path>`. You can sync later via `pilot worktree sync <plan-slug>` or discard via `pilot worktree cleanup <plan-slug>`."

   **If "Discard all changes":**

   Combine cleanup + cd in a SINGLE bash call (same reason as above):

   ```bash
   PROJECT_ROOT=$(~/.pilot/bin/pilot worktree cleanup --force --json <plan_slug> | python3 -c "import sys,json; print(json.load(sys.stdin)['project_root'])") && cd "$PROJECT_ROOT"
   ```

   Report: "Worktree and branch discarded."

### Step 3.13c: Post-Merge Verification (worktree sync only)

**After a successful worktree sync, verify the merged code on the base branch before marking VERIFIED.**

Verification in the worktree confirmed the code works in isolation. But the squash merge onto the base branch can introduce breakage:

- **Other worktrees merged first** — the base branch diverged, and the squash merge produced semantic conflicts (code merges cleanly but logic is broken)
- **Merge conflict resolution** — if conflicts were resolved (manually or automatically), the resolution itself may introduce bugs
- **Interface drift** — dependencies, shared utilities, or APIs changed on the base branch since the worktree branched off

**⛔ This step is MANDATORY after a successful "Yes, squash merge" in Step 3.13b.** Skip only if:

- No worktree was active (non-worktree spec run)
- User chose "No, keep worktree" or "Discard all changes"

**Post-merge checks (run on base branch after sync + cleanup):**

1. **Run full test suite** — All tests must pass. This is the single most important check — tests written in the worktree now run against the merged codebase which includes all other changes.

2. **Run type checker / linter** — Zero errors. Type mismatches from interface drift are common after merges.

3. **Build verification** — Clean build with no errors.

4. **Program launch smoke test** — Start the program and verify it launches without errors. Check logs for stack traces, panics, or unhandled exceptions. If the program exposes an API or UI, verify at least one endpoint/page responds correctly. This catches runtime issues that static analysis and unit tests miss (missing config, broken imports from renamed modules, incompatible state migrations, etc.).

**If any check fails:**

The merge introduced a regression. Fix it on the base branch directly:

1. Report the specific failure clearly
2. Fix the issue immediately (you are now on the base branch, not in a worktree)
3. Re-run the failing check to confirm the fix
4. Re-run the full test suite to catch cascading failures
5. Commit the fix separately (with a descriptive message referencing the merge, e.g. `fix: resolve post-merge regression from spec/<slug>`)

**⛔ Do NOT proceed to Step 3.14 (VERIFIED) until all post-merge checks pass.**

### Step 3.14: Update Plan Status

**Status Lifecycle:** `PENDING` → `COMPLETE` → `VERIFIED`

**When ALL verification passes (no missing features, no bugs, rules compliant):**

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
   - [Brief summary of what was implemented]
   - [Key files created/modified]
   - [Test results]

   💡 Run /clear to free context before starting new work.
   ```

**When verification FAILS (missing features, serious bugs, or unfixed rule violations):**

1. Add new tasks to the plan for missing features/bugs
2. **Set status back to PENDING and increment Iterations:**
   ```
   Edit the plan file:
   Status: COMPLETE  →  Status: PENDING
   Iterations: N     →  Iterations: N+1
   ```
3. **Register status change (auto-notifies dashboard):** `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`
4. **Write structured gap table** to the plan file under a `## Verification Gaps` section. If the section already exists, overwrite it entirely (to avoid accumulating stale gaps across iterations):

   ```markdown
   ## Verification Gaps

   | Gap | Type | Severity | Affected Files | Fix Description |
   |-----|------|----------|---------------|-----------------|
   | [truth that failed] | goal_gap | must_fix | [files] | [what needs to happen] |
   | [stub found] | stub | should_fix | [file:line] | [implement real logic] |
   | [orphaned module] | wiring | should_fix | [file] | [wire into consumer] |
   ```

   This supplements the new tasks — tasks describe what to build, the gap table provides diagnostic context.

5. Inform user: "🔄 Iteration N+1: Issues found, fixing and re-verifying..."
6. **Invoke implementation phase:** `Skill(skill='spec-implement', args='<plan-path>')`

---

## Context Management

Context is managed automatically by auto-compaction. No agent action needed — just keep working.

ARGUMENTS: $ARGUMENTS
