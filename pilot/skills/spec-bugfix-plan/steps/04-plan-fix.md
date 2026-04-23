---

## Step 4: Plan the Fix

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

### Behavior Contract (MANDATORY — write it before task structure)

**Every bugfix plan must pin down the contract as an explicit before/after invariant.** This is what the reproducing test will encode and what verification will audit against. Without this, "the fix works" has no meaning.

Write it in the plan like this:

```markdown
## Behavior Contract

**Given:** [precondition / state / input that triggers the bug]
**When:** [the action or call that exercises the code path]
**Currently (bug):** [actual, incorrect behavior — the symptom]
**Expected (fix):** [correct behavior the fix must produce]
**Anti-regression:** [what must still work — behavior the fix must NOT break]
```

The reproducing test encodes the `Currently → Expected` transition. Verification audits that the fix produced it without breaking `Anti-regression`.

**Write `Anti-regression:` specifically** — name the test(s), user flow, or API contract that must still pass. "Existing functionality" or "nothing else breaks" is not auditable. Example: `Anti-regression: test_search_with_filters_returns_200, test_search_pagination` — not `Anti-regression: existing search tests`.

### Task structure — ONE uniform shape for every bugfix

**⛔ Do NOT collapse these into fewer tasks. Do NOT merge test + fix into a single task.** Separate checkboxes = separate proof. Combining them is exactly where the process falls apart.

**Task 1: Write Reproducing Test (RED)**
- Write a test that encodes the Behavior Contract's `Currently → Expected` transition.
- Test must exercise an existing public entry point (not helpers you plan to create).
- Run it → **must FAIL** with an assertion or error that matches the documented symptom.
- Commit the failing test BEFORE writing any fix code (worktree mode only).
- Definition of Done: test exists, is named `test_<function>_<bug>_<expected>`, runs, fails with the expected error.

**Task 2: Implement Fix at Root Cause**
- Make the minimal change at `Root Cause: file:line` from the plan.
- Fix at the source, not where the error appears. No catching/hiding/patching around the symptom.
- Re-run the reproducing test → **must PASS**.
- Run the full test suite → zero failures (no `Anti-regression` breakage). This is the anti-regression gate for the fix itself.
- Definition of Done: reproducing test green, full suite green, diff touches root cause file.

**Task 3: Quality Gate**
- Lint, type check, build (if applicable), performance audit.
- Re-run the full test suite at the END of this task. Lint/type auto-fixes can silently modify code — the suite must be green **after** those fixes, not before. A task checkbox goes green only when the suite is green for the code as it stands at that moment.
- For UI-facing bugs: the `Verification Scenario` (TS-001) is executed in the verify phase (step 6), not here.
- Definition of Done: lint clean, types clean, build green, full suite green, no performance regressions in the diff.

**Scope scaling:** Lean bugs have short tasks (one-line test, one-line fix). Complex bugs have longer tasks (multiple assertions, defense-in-depth fix). The **number** of tasks is always three. The **content** of each task scales with the bug.

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
