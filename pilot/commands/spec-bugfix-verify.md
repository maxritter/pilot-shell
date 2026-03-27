---
description: "Bugfix verification phase - tests, quality checks, fix confirmation"
argument-hint: "<path/to/plan.md>"
user-invocable: false
effort: high
model: sonnet
hooks:
  Stop:
    - command: uv run python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_verify_validator.py"
---

# /spec-bugfix-verify - Bugfix Verification Phase

**Phase 3 (bugfix).** Lightweight verification: run tests, quality checks, confirm fix works.

**Input:** Bugfix plan with `Status: COMPLETE`
**Output:** Plan → VERIFIED (success) or loop back to implementation (failure)

**Why no sub-agents:** The regression test proves the fix works. The full test suite proves nothing else broke. Sub-agents would re-verify what tests already prove.

---

## Critical Constraints

- **NO review sub-agents** — tests prove correctness for bugfixes
- **NO stopping** — everything automatic. Never ask "Should I fix these?"
- **Fix ALL issues automatically** — no permission needed
- **Plan file is source of truth** — re-read after auto-compaction

---

## Step 3.1: Run Full Test Suite

Run all tests. Fix any failures immediately. Re-run until green.

## Step 3.2: Verify the Fix

1. **Read the plan's regression test** (from Task 1)
2. **Run it specifically:** `uv run pytest <test-path>::<test-name> -q`
3. Must PASS — if not, fix is incomplete, fix immediately
4. **Scope check:** Read changed files, confirm changes match plan scope. Flag unplanned changes.

## Step 3.3: Quality Checks

1. **Type checker** — zero new errors
2. **Linter** — errors are blockers, fix immediately
3. **Build** (if applicable) — must succeed
4. **Performance audit** — For changed files on hot paths: expensive uncached work? Heavy dependency imports with lighter alternatives? Repeated invocations redoing work when input hasn't changed? Structural issues — visible in source, no running program needed.

## Step 3.4: Plan Verify Commands

Run each task's `Verify:` commands. Defer server-dependent commands (containing `curl`, `localhost`, `http://`) to Step 3.5.

## Step 3.5: Runtime Verification (only if deferred commands exist)

If no server-dependent commands were deferred: skip to Step 3.5b.

Otherwise: start service → run deferred commands → stop service → fix failures.

## Step 3.5b: Verification Scenario (if exists in plan)

Check whether the plan has a `## Verification Scenario` section (only present for UI-facing bugs).

**If no Verification Scenario:** proceed to Final.

**If Verification Scenario exists:**

```bash
AB_SESSION="${PILOT_SESSION_ID:-default}"
```

1. Execute each step from the scenario using `agent-browser --session "$AB_SESSION"`
2. Verify the expected result for each step (snapshot after each interaction)
3. **PASS:** Scenario confirms fix works — close browser, proceed to Final
4. **FAIL (attempt 1):** Analyze root cause, implement fix, re-run tests, re-execute scenario
5. **FAIL (attempt 2):** Implement second fix, re-run tests, re-execute scenario
6. **FAIL after 2 attempts:** The bug is not fully fixed — set `Status: PENDING`, increment `Iterations`, invoke `Skill(skill='spec-implement', args='<plan-path>')`. Do not proceed to VERIFIED.

```bash
agent-browser --session "$AB_SESSION" close
```

---

## Final

### Step 3.6: Worktree Sync (if worktree active)

1. Detect: `~/.pilot/bin/pilot worktree detect --json <plan_slug>`
2. If no worktree: skip to Step 3.8.
3. Save plan to project root (only if gitignored):
   `git -C <project_root> check-ignore -q docs/plans/<plan_filename>` — if exit 0: `cp <worktree_plan> <project_root>/docs/plans/`; if exit 1 (tracked): skip — squash merge brings the updated plan.
5. Show diff: `~/.pilot/bin/pilot worktree diff --json <plan_slug>`
6. Notify + AskUserQuestion: "Yes, squash merge" | "No, keep" | "Discard"
7. Handle:
   - **Squash:** `worktree sync && cleanup --force + cd` — ALL in ONE Bash call chained with `&&`. Cleanup MUST NOT run if sync fails.
   - **Keep:** Report path
   - **Discard:** `cleanup --discard` + `cd` in SAME bash call (no sync needed — `--discard` explicitly allows deleting unmerged work)

   ⛔ NEVER split sync, cleanup, or cd into separate Bash calls — compaction between them can cause work loss.

### Step 3.7: Post-Merge Verification (after squash merge only)

Full test suite + type checker + build. If any fails: fix on base branch, re-run.

### Step 3.7b: Check for Code Review Feedback

**Run BEFORE marking VERIFIED.** Check if the user left code review annotations in the Console's Changes tab. Annotations auto-save — no "Send Feedback" button needed.

Derive the annotation file path: `docs/plans/.annotations/<plan-filename>.json` (same basename as the plan, `.json` extension).

Read the annotation file with the Read tool. If the file doesn't exist, treat as `NO_FEEDBACK`. If it exists, check whether `codeReviewAnnotations` has any entries (`FEEDBACK_EXISTS`) or is empty/missing (`NO_FEEDBACK`).

**If `FEEDBACK_EXISTS`:** Each annotation in `codeReviewAnnotations` has `filePath`, `lineStart`, `text`. Fix all issues, clear annotations via `curl -s -X DELETE "http://localhost:41777/api/annotations/code-review?path=<encoded-plan-path>" > /dev/null 2>&1 || true`, re-run tests, continue to Step 3.8.
**If `NO_FEEDBACK`:** continue to Step 3.8.

### Step 3.8: Code Review Gate (User Confirmation)

**⛔ MANDATORY before marking VERIFIED.**

1. Notify:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Bugfix Verification Complete" "<plan-slug> — please review changes" --plan-path "<plan_path>" 2>/dev/null || true
   ```

2. Tell the user:
   ```
   All automated checks passed. Please review the code changes in the Console's **Changes** tab.
   You can leave inline annotations using the **Review** mode toggle — annotations save automatically.

   Say **"approve"** to mark verified, or **"fix"** to have me address your annotations (I'll read them directly from the Console).
   ```

3. Wait for user response:
   - "approve" / "lgtm" → proceed to Step 3.9
   - "fix" / feedback → re-run Step 3.7b (check for code review annotations in JSON), fix issues, re-run tests, return to Step 3.8
   - "continue" / "proceed" → treat as approval

### Step 3.9: Update Plan Status

**All passes and user approves:** Set `Status: VERIFIED`, register:
```bash
~/.pilot/bin/pilot register-plan "<plan_path>" "VERIFIED" 2>/dev/null || true
```
Report:
```
Bugfix verified — regression test passes, full suite green.
Run /clear before starting new work — this resets context while keeping project rules loaded.
```

**Fails:** Add fix tasks, set `Status: PENDING`, increment `Iterations`, invoke `Skill(skill='spec-implement', args='<plan-path>')`.

ARGUMENTS: $ARGUMENTS
