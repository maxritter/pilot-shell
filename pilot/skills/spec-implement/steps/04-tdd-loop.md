---

## Step 4: TDD Loop

**For EVERY task:**

1. **Read plan's implementation steps** — list files to create/modify/delete
2. **Call chain analysis (MANDATORY):** For each function being modified, run `trace_call_path(function_name, direction="both", depth=2)`. Discover exact names first with `search_graph(name_pattern="...")` if needed. This traces the actual call graph — Probe text search is not a substitute.
3. **Mark in_progress:** `TaskUpdate(taskId, status="in_progress")`
4. **TDD Flow:**
   - **RED:** Write failing test → verify it fails (feature missing, not syntax error)
   - **GREEN:** Implement minimal code to pass
   - **REFACTOR:** Improve while keeping tests green
   - Skip TDD for: docs, config, IaC, formatting-only changes
   - **Surprise discovery:** If something contradicts how you expected it to work, check plan's `## Assumptions` section — identify which task numbers are affected and note the invalidated assumption in the plan before continuing.
5. **Verify tests pass** — run test suite
6. **Run actual program** — use plan's Runtime Environment. Check port: `lsof -i :<port>`. For browser verification: prefer Claude Code Chrome if available, then Chrome DevTools MCP, then playwright-cli, then agent-browser (see `browser-automation.md` for 4-tier selection)
7. **Check diagnostics** — zero errors
8. **Validate Definition of Done** — all criteria from plan
9. **Self-review:** Completeness? Names clear? YAGNI? Tests verify behavior not implementation?
10. **Performance:** Is any expensive work (parsing, transforming, I/O) running on a hot path without caching or memoization? Are heavy dependencies imported fully when a lighter/tree-shaken alternative exists? Does repeated invocation (polling, re-render, request loop) redo work when input hasn't changed?
11. **Per-task commit (worktree only):** `git add <files> && git commit -m "{type}(spec): {task-name}"`
12. **Mark completed:** `TaskUpdate(taskId, status="completed")`
13. **Update plan file immediately** (Step 5)
