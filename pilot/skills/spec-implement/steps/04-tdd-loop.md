---

## Step 4: TDD Loop

**For EVERY task (generic flow — features use this as-is; bugfixes use it via the Bugfix Lane overrides below):**

1. **Read plan's implementation steps** — list files to create/modify/delete
2. **Call chain analysis (MANDATORY):** For each function being modified, run `trace_call_path(function_name, direction="both", depth=2)`. Discover exact names first with `search_graph(name_pattern="...")` if needed. This traces the actual call graph — Probe text search is not a substitute.
3. **Mark in_progress:** `TaskUpdate(taskId, status="in_progress")`
4. **TDD Flow:**
   - **RED:** Write failing test → verify it fails (feature missing, not syntax error)
   - **GREEN:** Implement minimal code to pass
   - **REFACTOR:** Improve while keeping tests green
   - Skip TDD for: docs, config, IaC, formatting-only changes (**features only** — the Bugfix Lane below removes this escape hatch)
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

---

### ⛔ Bugfix Lane — Overrides When `Type: Bugfix`

**If the plan header contains `Type: Bugfix`, the rules below OVERRIDE the generic flow above. No exceptions — not for "obvious" bugs, typos, or one-line fixes.**

**Global rules (apply to all three tasks):**

1. The plan has THREE tasks: `Write Reproducing Test (RED)` → `Implement Fix at Root Cause` → `Quality Gate`. Do not merge them. Do not skip Task 1 because "I already see the fix."
2. The "Skip TDD for docs, config, IaC, formatting-only" escape hatch (step 4 above) does **NOT** apply to bugfixes. Even config-driven bugs need a reproducing test at the end-to-end boundary.
3. Re-use the plan's `## Investigation` section instead of re-running codegraph. If the plan already documents callers/callees/impact for the root-cause function, read it from the plan — skip generic step 2. Re-run `codegraph_callers`/`codegraph_callees` only when the plan's breadcrumbs are missing or stale for a specific function you're about to modify.

**Per-task flows — run the flow matching the current task, not the generic 13-step loop:**

#### Task 1 — Write Reproducing Test (RED)

Minimal flow. No production code here, so most generic steps (call-chain analysis, performance audit, self-review) are inapplicable.

1. Read Task 1's `Entry point:` and the `## Behavior Contract` from the plan.
2. Write a test that encodes `Currently → Expected` via the entry point, named `test_<function>_<bug>_<expected>`.
3. Run it → **must FAIL** with an error matching the Behavior Contract's `Currently (bug)`.
4. If it passes on first run: the test is wrong or the bug is already fixed. STOP, re-investigate, do not proceed to Task 2.
5. Worktree mode: commit as its own commit (`test(spec): add reproducing test for <bug>`). This keeps the test file separable from the fix — it does not skip any verification step.
6. Update plan checkbox (`[ ]` → `[x]`), mark task completed.

#### Task 2 — Implement Fix at Root Cause (GREEN)

This is the only task that modifies production code. Full TDD discipline applies.

1. Call-chain analysis: use plan's Investigation if it covers the function; otherwise run `codegraph_callers` + `codegraph_callees` on the root-cause function only.
2. Make the minimal change at `Root Cause: file:line`. Fix at the source, not at the symptom.
3. Forbidden: new broad `try/except` around the failing call, `if value is None: return default` at the caller when the bug is upstream, swallowed exceptions, silently normalised bad inputs. Legitimate defense-in-depth requires an explicit entry in the plan's `Defense-in-depth:` field.
4. Re-run the reproducing test → **must PASS**.
5. Run the full test suite → zero failures. This is the anti-regression check for this task.
6. Diagnostics zero errors. Performance audit on the diff.
7. Re-read the plan's `## Behavior Contract` and confirm: (a) reproducing test passes, (b) `Anti-regression` behavior still works, (c) diff touches the root-cause file. If any is false, return to step 2 — do not rationalize forward.
8. Worktree mode: commit (`fix(spec): <bug>`). Update plan, mark task completed.

#### Task 3 — Quality Gate

Runner-only task. Code may change only via lint/type/formatter auto-fixes; if it does, the suite must still be green at task close.

1. Run lint, type check, build (if applicable) — the commands listed in Task 3's `Verify:` field.
2. Fix any findings inline.
3. **Re-run the full test suite.** Lint/type/formatter changes can break tests — a green checkbox on this task means the suite is green AFTER those fixes, not before.
4. If the suite failed from an auto-fix: revert the offending change or write a targeted correction, re-run lint/types/suite until all green.
5. Worktree mode: amend onto Task 2's commit or add a small `chore(spec): lint/types` commit. Update plan, mark task completed.

**Then hand off to `spec-bugfix-verify` (via Step 6 of this skill). Verify runs the suite once more as the authoritative final signal, plus a Behavior Contract audit and an always-on revert-test — quality insurance, not waste.**
