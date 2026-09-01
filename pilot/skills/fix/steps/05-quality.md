## Step 5: Quality Gate

Automated checks — the last green-bar gate before finalise.

### 5.1 Lint + types + build

```bash
# Python project example
ruff check . --fix && ruff format . && basedpyright <src> 2>&1 | tail -5
# TypeScript project example
bun run typecheck && bun run lint
```

Build only when the project has a build step that could surface fix-related errors (TS compile, native compile). Skip for plain Python or pure JS.

### 5.2 Full anti-regression suite

```bash
# Python
uv run pytest -q
# TypeScript
bun test
```

Zero failures. If anything broke that's not in the immediate neighbourhood of your fix:

- **Localised to the same module:** fix it inline, re-run.
- **Far from your fix:** treat it as evidence of unintended coupling. Trace whether the failure is caused by the repair; if it is, correct the integration inside this workflow and re-run. If it is unrelated and pre-existing, preserve the evidence and report it without altering unrelated code.

### 5.3 Auto-fix re-run

If lint/format/types auto-modified files in 5.1, re-run the suite to confirm those auto-fixes didn't break anything. (This is the only reason 5.2 might run twice.)

### 5.4 Least-that-works check

A bugfix should be the smallest change that resolves the root cause — run the ladder (`development-practices.md` → *Build the least that works*) over your diff and delete any abstraction, dependency, or boilerplate the fix didn't strictly need. If the fix ships a deliberate shortcut, it must carry a `SHORTCUT:` comment naming the ceiling and upgrade trigger; surface any such markers (and any pre-existing ones the fix touched: `git diff | grep -nE '(#|//) ?SHORTCUT:'`) in the finalise summary.
