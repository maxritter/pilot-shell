---
name: spec-bugfix-plan
description: "Bugfix spec planning phase - investigate root cause, design fix, get approval"
argument-hint: "<bug description> or <path/to/plan.md>"
user-invocable: false
effort: high
model: opus
hooks:
  Stop:
    - command: uv run python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_plan_validator.py"
---

# /spec-bugfix-plan - Bugfix Planning Phase

**Phase 1 (bugfix).** Investigates root cause, creates lean fix plan, gets approval.

**Input:** Bug description (new) or plan path (continue unapproved)
**Output:** Approved bugfix plan at `docs/plans/YYYY-MM-DD-<slug>.md` with `Type: Bugfix`
**Next:** On approval → `Skill(skill='spec-implement', args='<plan-path>')`

---

## Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Step 1.2, you cannot propose fixes. Symptom fixes are failure.

---

## Critical Constraints

- **NEVER write code during planning** — planning and implementation are separate phases
- **NEVER assume — verify by reading files.** Trace the bug to actual file:line.
- **Right-size the plan** — small bugs get lean plans. Don't over-engineer.
- **Plan file is source of truth** — survives across auto-compaction cycles
- **ALWAYS use `AskUserQuestion` tool** for clarifications — never list numbered questions in plain text
- **⛔ If `PILOT_PLAN_QUESTIONS_ENABLED` is `"false"` (from Step 0),** skip all `AskUserQuestion` calls (Steps 1.2.1, 1.2.5 escalation, 1.3 approach selection). Make reasonable default assumptions (including selecting the recommended fix approach) and document them in the plan. Continue autonomously.

> **NOTE: During `/spec`, use the structured workflow below — not CC's native plan mode.**

---

## Step 0: Read Toggle Configuration

**⛔ Run FIRST, before any other step.** Read all toggle env vars in a single Bash call:

```bash
echo "QUESTIONS=$PILOT_PLAN_QUESTIONS_ENABLED CODEX_SPEC=$PILOT_CODEX_SPEC_REVIEW_ENABLED APPROVAL=$PILOT_PLAN_APPROVAL_ENABLED"
```

Reference these values throughout: Steps 1.2.1/1.2.5 (questions), 1.4c (Codex — controlled by Console Settings), and 1.5 (approval).

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking any of these, STOP. Return to Step 1.2.

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)
- Each fix reveals a new problem in a different place

---

## Step 1.1: Create Plan File Header (FIRST)

1. **Parse flags** from arguments: `--worktree=yes|no` (default: `No`). Strip the flag.
2. **Create worktree early (if yes):** Same pattern as spec-plan Step 1.1.
3. **Generate filename:** `docs/plans/YYYY-MM-DD-<bug-slug>.md`
4. **Fetch author email** (best-effort): same as spec-plan Step 1.1 step 4. If non-empty, include `Author: <email>` in header. If empty/fails, omit.
5. **Write header:**

   ```markdown
   # [Bug Description] Fix Plan

   Created: [Date]
   Author: [email if available]
   Status: PENDING
   Approved: No
   Iterations: 0
   Worktree: [Yes|No]
   Type: Bugfix

   > Investigating bug...

   ## Summary

   **Symptom:** [Bug description from user]

   ---

   _Tracing root cause..._
   ```

6. **Register:** `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`

---

## Step 1.2: Root Cause Investigation

**Complete each sub-step before the next. No shortcuts.**

### 1.2.1: Reproduce & Understand

1. Restate: **symptom** (what user observes), **trigger** (when/how), **expected behavior**
2. If too vague: `AskUserQuestion` with ONE focused question
3. Can you trigger it reliably? What are the exact steps?
4. If not reproducible: gather more data, don't guess

### 1.2.2: Check Recent Changes

- What changed that could cause this? `git log --oneline -10 -- <file>`, `git diff`
- New dependencies, config changes, environmental differences?

### 1.2.3: Trace the Root Cause

**⛔ START WITH CODEGRAPH — before reading any files.**

**Step 1: Orient with CodeGraph (MANDATORY FIRST ACTION):**
```
codegraph_context(task="<bug description and symptoms>")
```
This reveals entry points, related symbols, and code context for the bug area. Read the output carefully before diving deeper.

**Step 2: Deep dive if needed:** Use `codegraph_search` to find the specific symbol, then `codegraph_explore(query="<symbol names>")` to get full source code from all relevant files in one call.

**Step 3: Trace and investigate.** Use Probe for intent-based search (`probe search`), CodeGraph for structural tracing. Fall back to Grep/Glob only for exact patterns.

Read as many files as needed. For each: read completely, trace execution path from user action to symptom, note specific lines where behavior diverges.

**Backward tracing technique (from symptom to source):**

1. Find where the error/wrong behavior appears — note file:line
2. Use `codegraph_callers` to trace what called this with the wrong value/state
3. Keep tracing until you find the **source** — where the bad data originates
4. **Fix at the source, not where the error appears**

**Multi-component systems:** Before concluding, instrument at component boundaries:

- What data enters each component? What exits?
- WHERE does it break? Run once to gather evidence, THEN investigate the failing component.

**⛔ Structural tracing (MANDATORY):** Run `codegraph_callers` and `codegraph_callees` on the function where the bug manifests AND the function at the root cause. Then run `codegraph_impact` to see the full blast radius — essential for understanding how bad data flows through the system.

Tools: CodeGraph (`codegraph_context`, `codegraph_explore`, `codegraph_callers`/`codegraph_callees`, `codegraph_impact`, `codegraph_search`), Probe CLI (`probe search` for intent, `probe extract` for symbols), Read/Grep/Glob for exact patterns.

### 1.2.4: Pattern Analysis

1. Find **working examples** — similar code in the codebase that works correctly
2. Compare: what's different between working and broken?
3. List every difference, however small — don't assume "that can't matter"

### 1.2.5: Root Cause Statement

State clearly:

- **Root cause:** `file/path.py:lineN` — `function_name()` does X but should do Y
- **Why:** Explain WHY it causes the symptom (not just what's wrong)
- **Confidence:** High (traced fully) / Medium (strong hypothesis) / Low (needs more data)

If confidence is Low: gather more evidence. Don't guess.

**Escalation:** If 3+ hypotheses have failed, STOP — this is likely an architectural problem, not a simple bug. `AskUserQuestion` to discuss with user before continuing.

---

## Step 1.3: Plan the Fix

### Gate Function — Before Planning

```
BEFORE writing the plan:
  1. Can I state the root cause with file:line? If NO → back to 1.2
  2. Can I explain WHY it causes the symptom? If NO → back to 1.2
  3. Is my confidence High or Medium? If LOW → back to 1.2
```

### Fix Approach Selection

**After confirming root cause, evaluate fix strategies before committing to one.** Even simple bugs often have multiple valid fixes (patch at symptom vs fix at source vs structural prevention). Making the choice explicit improves plan quality.

Propose 2-3 fix approaches. For each:

- **Name** — short label (e.g., "Patch at call site" vs "Fix at source" vs "Add validation layer")
- **What it fixes** — which symptoms/failure modes it addresses
- **Trade-offs** — scope of change, risk of regression, maintenance burden
- **Recommendation** — mark your preferred approach with reasoning

**When questions are enabled (`PILOT_PLAN_QUESTIONS_ENABLED` is not `"false"`):** Use `AskUserQuestion` to let the user pick the approach. Each approach is an option.

```bash
~/.pilot/bin/pilot notify plan_approval "Fix Approach" "<plan-slug> — fix strategy" --plan-path "<plan_path>" 2>/dev/null || true
```

**When questions are disabled:** Select the recommended approach and document the reasoning in the plan.

**Skip for trivial bugs:** If there is genuinely only one reasonable fix (e.g., typo, wrong variable name, missing import), note the approach briefly and proceed — don't manufacture fake alternatives.

### Size the task structure

| Size                  | Criteria                         | Tasks                         |
| --------------------- | -------------------------------- | ----------------------------- |
| **Compact** (default) | ≤3 files, clear root cause       | 2: Fix (test + code) → Verify |
| **Full**              | 4+ files, multiple failure modes | 3: Tests → Fix → Verify       |

### Compact (most bugs)

**Task 1: Fix** — Write regression test → verify FAILS → implement fix → verify all PASS.
**Task 2: Verify** — Full test suite, lint, type check.

### Full (complex bugs)

**Task 1: Write Tests** — regression + preservation tests (if fix touches shared code paths).
**Task 2: Implement Fix** — minimal fix at root cause.
**Task 3: Verify** — full suite, lint, type check.

**Regression tests must exercise existing public entry points** (not internal helpers you plan to create). The test answers: "Under the bug condition, does the system produce the correct result?"

**Defense-in-depth:** When the bug was caused by invalid data flowing through multiple layers, plan validation at every layer the data passes through — not just the source. Entry point validation, business logic validation, environment guards where appropriate.

**Verification Scenario (if UI-facing bug):** If the bug manifests in the UI or through user-visible behavior, add a single structured scenario to the plan describing the user steps that reproduce the bug and confirm the fix. Same format as feature E2E scenarios — concrete browser automation steps with expected results (tool-agnostic: Claude Code Chrome, playwright-cli, or agent-browser). This serves as the acceptance test beyond the regression unit test.

```markdown
### TS-001: [Bug Trigger / Fix Confirmation]
**Preconditions:** [State that triggers the bug]

| Step | Action | Expected Result (after fix) |
|------|--------|-----------------------------|
| 1 | [User action that triggered bug] | [Correct behavior now shown] |
| 2 | [Follow-up verification] | [No regression] |
```

---

## Step 1.4: Write the Bugfix Plan

**Save to:** `docs/plans/YYYY-MM-DD-<bug-name>.md`

```markdown
# [Bug Description] Fix Plan

Created: [Date]
Status: PENDING
Approved: No
Iterations: 0
Worktree: [Yes|No]
Type: Bugfix

## Summary

**Symptom:** [What user observes]
**Trigger:** [When/how it happens]
**Root Cause:** `file/path.py:lineN` — [what's wrong and why]

## Investigation

- [Key findings from tracing — breadcrumb trail so implementer understands the bug]
- [Working example for comparison, if relevant]
- [Recent changes that may have caused it, if relevant]

## Fix Approach

**Chosen:** [Name of selected approach]
**Why:** [1-2 sentences — what it fixes and what it costs]
**Alternatives considered:** [Brief list of other approaches with why they were rejected — omit for trivial bugs]

**Files:** [files to modify]
**Strategy:** [how to fix — reference pattern from working code if applicable]
**Tests:** [test files to create/modify]
**Defense-in-depth:** [additional validation layers, if applicable — skip for isolated fixes]

## Verification Scenario (only for UI-facing bugs — omit otherwise)

### TS-001: [Bug Trigger / Fix Confirmation]
**Preconditions:** [State that triggers the bug]

| Step | Action | Expected Result (after fix) |
|------|--------|-----------------------------|
| 1 | [User action that triggered bug] | [Correct behavior] |
| 2 | [Follow-up verification] | [No regression] |

## Progress

- [ ] Task 1: [title]
- [ ] Task 2: [title]
      **Tasks:** N | **Done:** 0

## Tasks

### Task 1: [Title]

**Objective:** [what]
**Files:** [list]
**TDD:** Write regression test → verify FAILS → implement fix → verify all PASS
**Verify:** `[command]`

### Task 2: Verify

**Objective:** Full suite + quality checks
**Verify:** `uv run pytest -q && ruff check . && basedpyright launcher`
```

**Do NOT include:** "Goal Verification" sections, "Risks and Mitigations" table, "Assumptions" section, per-task "Definition of Done" checklists, per-task "Dependencies" field.

**Include `## Verification Scenario` only for UI-facing bugs** (from the Verification Scenario guidance in Step 1.3). Omit entirely for backend/non-UI bugs.

---

## Step 1.4b: Check for Console Annotation Feedback (Before Approval)

**⛔ Run this BEFORE Step 1.5 (approval).** Check if the user has annotated the plan in the Console's Specifications tab. Annotations auto-save to JSON — no "Send Feedback" button needed.

1. Derive annotation file: `docs/plans/.annotations/<plan-filename>.json`
2. Read the annotation file with the Read tool. If the file doesn't exist, treat as `NO_FEEDBACK`. If it exists, check whether `planAnnotations` has any entries (`FEEDBACK_EXISTS`) or is empty/missing (`NO_FEEDBACK`).
3. **If `FEEDBACK_EXISTS`:** Each annotation in `planAnnotations` has `originalText` (selected passage) and `text` (user's note). Incorporate into plan, clear annotations via `curl -s -X DELETE "http://localhost:41777/api/annotations/plan?path=<encoded-plan-path>" > /dev/null 2>&1 || true`, note changes. Proceed to Step 1.5.
4. **If `NO_FEEDBACK`:** proceed directly to Step 1.5.

## Step 1.4c: Codex Adversarial Review (Optional)

**If `PILOT_CODEX_SPEC_REVIEW_ENABLED` is `"true"` (from Step 0):**

1. Detect companion path, project root, and base branch:
```bash
CODEX_COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
# Use worktree base branch if in worktree, otherwise detect repo default branch
BASE_BRANCH=$(~/.pilot/bin/pilot worktree status --json 2>/dev/null | grep -o '"base_branch":"[^"]*"' | cut -d'"' -f4)
[ -z "$BASE_BRANCH" ] && BASE_BRANCH=$(cd "$PROJECT_ROOT" && git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")
```

2. Launch adversarial review with specific focus text from the project root. **⛔ Use synchronous Bash (NOT `run_in_background`)** — the companion's `--background` flag already makes it non-blocking and returns the job ID immediately to stdout:
```bash
cd "$PROJECT_ROOT" && node "$CODEX_COMPANION" adversarial-review --background --base "$BASE_BRANCH" "Challenge this bugfix plan: <plan summary/root cause>. Plan: <plan-path>. Focus on: wrong root cause, incomplete fix, missing edge cases, regression risk, and whether the fix addresses symptoms vs cause."
```
Parse the job ID from stdout (format: `review-XXXXXXXX-YYYYYY`).

**⛔ Use the companion's built-in wait — do NOT use `sleep` loops or poll output files manually.**

3. Wait for completion (this blocks until Codex finishes or times out — no sleep needed):
```bash
node "$CODEX_COMPANION" status <jobId> --wait --timeout-ms 300000 --json
```

4. **Handle status:**
   - `waitTimedOut: true` → Log "Codex review timed out — skipping" and continue.
   - `job.status` is `"cancelled"` or exit code non-zero → Log "Codex review failed: <failureMessage>" and continue.
   - `job.status` is `"completed"` → fetch full result:

5. Get review findings:
```bash
node "$CODEX_COMPANION" result <jobId> --json
```

6. Parse the result JSON — look for `verdict`, `findings`, `details`. Map severities: critical/high → must_fix, medium/low → should_fix. Fix all must_fix/should_fix in the plan.

---

## Step 1.5: Get User Approval

**⛔ If `PILOT_PLAN_APPROVAL_ENABLED` is `"false"` (from Step 0),** skip this step: set `Approved: Yes` in the plan file automatically and immediately invoke `Skill(skill='spec-implement', args='<plan-path>')`. No AskUserQuestion, no notification.

**When `PILOT_PLAN_APPROVAL_ENABLED` is NOT `"false"`:**

0. Notify:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Bugfix Plan Ready" "<plan-slug> — annotate in Console or approve here" --plan-path "<plan_path>" 2>/dev/null || true
   ```
1. Summarize: symptom → root cause → fix approach → task structure
2. AskUserQuestion: "Yes, proceed" | "No, let me edit" | "No, I'll annotate in the Console"
3. **Yes:** Set `Approved: Yes`, invoke `Skill(skill='spec-implement', args='<plan-path>')`
   **No (edit or annotate):** Tell user to edit the plan or annotate in the Console Specifications tab — annotations auto-save. Say "ready" when done. Re-run Step 1.4b (check for annotation feedback), re-read plan, ask again. **Other:** Incorporate, re-ask.

---

## Continuing Unapproved Bugfix Plans

When arguments end with `.md`: read plan, check Status/Approved. Resume from wherever planning left off: no investigation yet → Step 1.2. Has investigation, no tasks → Step 1.3. Complete but unapproved → Step 1.5.

ARGUMENTS: $ARGUMENTS
