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
