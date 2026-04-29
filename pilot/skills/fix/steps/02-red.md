## Step 2: Write the Reproducing Test (RED)

**No production code yet.** A bugfix without a failing test is a rubber-stamp fix. The quick lane keeps this step minimal — but it does not skip it.

### 2.1 Pick the entry point

Use an **existing public entry point** the bug is reachable through (function, endpoint, CLI command). Don't write a test that calls a helper you're about to create — those tests can't fail before the fix.

If no clean entry point exists: that's a design smell. Document it briefly and use the closest stable one. Don't refactor "to make it testable" in the quick lane — bail out (tell the user to re-invoke with `/spec`) if the smell is large.

### 2.2 Encode `Currently → Expected`

The test asserts the **correct** behaviour. Against the buggy code, the assertion must fail with an error matching the symptom you stated in Step 1.4.

Naming: `test_<function>_<bug>_<expected>` (Python) or `it("should <expected> when <condition>", ...)` (TS/JS). Keep it boring — this is regression insurance, not a showcase.

### 2.3 Run it — it MUST fail

```bash
<test command for ONLY this test, e.g. uv run pytest path/to/test.py::test_name -q>
```

**Outcome interpretation:**

- **Fails with the expected error** → RED proven, proceed to Step 3.
- **Passes** → the test does not encode the bug, OR the bug is already fixed. STOP. Re-read Step 1.5 — did you trace the actual root cause? Re-investigate. Do NOT write fix code.
- **Errors for an unrelated reason** (import error, missing fixture) → fix the test setup first, re-run. Don't proceed until RED is genuine.

### 2.4 No commit yet

Worktree mode: do not commit the test alone. The quick lane bundles test + fix into one commit at finalise. (Full lane uses separate commits because the cp+trap RED proof in verify needs them — quick lane skips that proof, so commit-bundling is fine.)
