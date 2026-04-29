---

## Step 4: Plan the Fix

### Gate — before writing the plan

Answer YES to all:

1. Root cause stated as `file:lineN — function() does X but should do Y`?
2. WHY it causes the symptom is explained?
3. Confidence is High or Medium?

If any NO → return to Step 3.

### Fix approach selection

**Default: pick the obvious fix.** For most bugs the source-level change at the root cause is the only reasonable fix. Document it in one or two sentences and move on. Don't manufacture fake alternatives.

**Propose 2–3 approaches only when there is a genuine architectural choice** (patch at call site vs. fix at source vs. add validation layer, with materially different scope/regression/maintenance trade-offs). For each: name, what it fixes, trade-offs, recommendation.

When a genuine choice exists AND `PILOT_PLAN_QUESTIONS_ENABLED` is not `"false"`: use `AskUserQuestion` to pick.

```bash
~/.pilot/bin/pilot notify plan_approval "Fix Approach" "<plan-slug> — fix strategy" --plan-path "<plan_path>" 2>/dev/null || true
```

### Behavior Contract (MANDATORY)

```markdown
## Behavior Contract

**Given:** [precondition / state / input that triggers the bug]
**When:** [the action or call that exercises the code path]
**Currently (bug):** [actual, incorrect behavior — the symptom]
**Expected (fix):** [correct behavior the fix must produce]
**Anti-regression:** [named tests / flows / API contracts that must still pass]
```

`Anti-regression:` must name specific tests or flows — `test_search_with_filters_returns_200, test_search_pagination` not "existing search tests".

### Task structure — three tasks, no exceptions

⛔ Do NOT merge tasks. Separate checkboxes = separate proof.

**Task 1 — Write Reproducing Test (RED)**
Encode `Currently → Expected` via an existing public entry point. Run → must FAIL with the documented symptom. Worktree mode: commit alone before any fix code. Naming: `test_<function>_<bug>_<expected>`.

**Task 2 — Implement Fix at Root Cause**
Minimal change at `Root Cause: file:line`. Fix at source, not symptom. Re-run reproducing test → must PASS. Run targeted test module(s), not full suite — full suite runs at Task 3. Diff must touch the root-cause file.

**Task 3 — Quality Gate**
Lint, type check, build (if applicable). Re-run full suite at the END (lint/type auto-fixes can break tests). UI-facing bugs: the Verification Scenario runs in verify phase, not here.

**Scope scaling:** simple bugs get short tasks, complex bugs get longer tasks — but always three tasks.

**Defense-in-depth:** when the bug propagated through multiple layers, plan validation at each layer (entry point, business logic, environment guards). Document as `Defense-in-depth:` in the Fix Approach section.

### Verification Scenario (UI-facing bugs only)

```markdown
### TS-001: [Bug Trigger / Fix Confirmation]
**Preconditions:** [State that triggers the bug]

| Step | Action | Expected Result (after fix) |
|------|--------|-----------------------------|
| 1 | [User action that triggered bug] | [Correct behavior now shown] |
| 2 | [Follow-up verification] | [No regression] |
```

Tool-agnostic — Claude Code Chrome, Chrome DevTools MCP, playwright-cli, or agent-browser per `browser-automation.md`.
