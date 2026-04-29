## Step 5: Quality Gate (Once, At The End)

This is the only place the full anti-regression suite runs. Don't run it earlier — Step 3.4 already covered the immediate scope.

### 5.1 Lint + types + build

Run the project's standard checks. Fix any inline.

```bash
# Python project example
ruff check . --fix && ruff format . && basedpyright <src> 2>&1 | tail -5
# TypeScript project example
bun run typecheck && bun run lint
```

Build only when the project has a build step that could surface fix-related errors (TS compile, native compile). Skip for plain Python or pure JS.

### 5.2 Full suite — once

```bash
# Python
uv run pytest -q
# TypeScript
bun test
```

Zero failures. If anything broke that's not in the immediate neighbourhood of your fix:

- Localised to the same module → fix it inline, re-run.
- Far from your fix → your fix has unintended cross-coupling. **Stop and tell the user to re-invoke with `/spec`** — the bug is bigger than you thought.

### 5.3 Auto-fix re-run check

If lint/format/types auto-modified files in 5.1, re-run the suite to confirm those auto-fixes didn't break anything. (This is the only reason 5.2 might run twice.)
