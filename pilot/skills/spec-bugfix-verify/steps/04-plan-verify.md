## Step 4: Plan Verify Commands (conditional — usually a no-op)

**For plans following the uniform 3-task structure (Reproducing Test → Fix → Quality Gate), this step is typically redundant:**

- Task 1's `Verify:` (reproducing test must FAIL): already run as RED by `spec-implement`; running it now expecting FAIL is wrong state.
- Task 2's `Verify:` (reproducing test must PASS): already run in Step 2.2 of this phase.
- Task 3's `Verify:` (lint, type check, build): already run in Step 3 of this phase.

**Decision:**

1. Read each task's `Verify:` command.
2. Skip any command that matches what Steps 1, 2, or 3 already ran (full suite, reproducing test, lint, type check, build).
3. Run only **residual** commands — typically ad-hoc shell checks a human author added (e.g., `uv run python -c "import foo; foo.smoke()"`, a specific endpoint smoke test).
4. Defer server-dependent commands (containing `curl`, `localhost`, `http://`) to Step 5.

If nothing residual remains: this step is a no-op. Do not re-run covered commands.
