## Step 2: Write the Reproducing Test (RED)

**No production code yet.** A bugfix without a failing test is a rubber-stamp fix. Keep this step focused, but do not skip it because the defect is complex.

### 2.1 Pick the entry point

Use an **existing public entry point** the bug is reachable through (function, endpoint, CLI command). Don't write a test that calls a helper you're about to create — those tests can't fail before the fix.

If no clean entry point exists, document the testability gap and use the closest stable public boundary. When a small test seam is necessary to reproduce the real defect, introduce it as part of the repair and keep it no broader than the failing behavior requires.

**Modify, don't duplicate.** If a test class already covers this entry point (e.g. you can `grep` for the function name in `tests/` and find one), add the new failing test as a method INSIDE that class. Do NOT create a new test class just because the bug is "different". Prefer one class per production class/public entry point, not one class per symptom.

### 2.2 Encode `Currently → Expected`

The test asserts the **correct** behaviour. Against the buggy code, the assertion must fail with an error matching the symptom you stated in Step 1.5.

Naming: `test_<function>_<bug>_<expected>` (Python) or `it("should <expected> when <condition>", ...)` (TS/JS). Keep it boring — this is regression insurance, not a showcase.

### 2.3 Run it — it MUST fail

```bash
<test command for ONLY this test, e.g. uv run pytest path/to/test.py::test_name -q>
```

**Outcome interpretation:**

- **Fails with the expected error** → RED proven, proceed to Step 3.
- **Passes** → the test does not encode the bug, OR the bug is already fixed. STOP. Re-read Step 1.5 — did you trace the actual root cause? Re-investigate. Do NOT write fix code.
- **Errors for an unrelated reason** (import error, missing fixture) → fix the test setup first, re-run. Don't proceed until RED is genuine.
- **Cannot run at all** (environment blocker: registry auth, missing services, broken install) → Step 1.1's environment blocker protocol applies: stop, ask the user to unblock, re-run after. Do NOT proceed to Step 3 without an observed RED.

### 2.4 No commit yet

Worktree mode: do not commit the test alone. `/fix` bundles the reproducing test, repair, and review-driven changes into one commit at finalise.
