## Step 3: Quality Checks + Residual Plan Verifies

1. **Type checker** — zero new errors
2. **Linter** — errors are blockers, fix immediately
3. **Build** (if applicable) — must succeed
4. **Residual `Verify:` commands.** The uniform 3-task plan structure means Task 1's verify (RED) was run by `spec-implement`, Task 2's verify (PASS) was run in Step 2.2, and Task 3's verify (lint/types/build) is covered by 1–3 above. Skip those. Run only **residual** commands a human author added (e.g. `uv run python -c "import foo; foo.smoke()"`, an endpoint smoke test) — usually nothing.

   For server-dependent residuals (containing `curl`, `localhost`, `http://`): start the service → run the command → stop the service → fix failures. Skip this branch entirely if no residuals exist.
