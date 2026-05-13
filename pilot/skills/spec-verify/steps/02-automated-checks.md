## Step 2: Automated Checks

Run all mechanical checks in sequence. Fix any failures before proceeding.

1. **Full test suite** — `uv run pytest -q` / `bun test` / `npm test`. Fix failures immediately.
2. **Type checker** — `basedpyright` / `tsc --noEmit`. Zero errors required.
3. **Linter** — `ruff check` / `eslint`. Errors are blockers, warnings acceptable.
4. **Coverage** — If the project already has coverage tooling, or the task touches critical paths (business logic, security, data integrity, error handling), run the existing coverage command and inspect the report. **No blanket numeric gate.** If a critical path's coverage or explicit behaviour coverage dropped vs main, fix it. Glue/CRUD/UI-binding files are not gated, and do not add coverage tooling just to satisfy this step.
5. **Test Parsimony Audit** — For each task whose `Files:` block adds new test files, group new test classes by production class/entry point and count only classes added by this task. If any production class has more than 2 new test classes (1 unit + 1 functional/integration) AND the task does not declare a `Why >2 test classes:` note in Key Decisions, flag as **must_fix** and return to spec-implement. Also scan new test files for: (i) per-method test classes (e.g. `DoSomethingTests` for class `Foo` with method `DoSomething`) — flag as **must_fix**; (ii) two or more tests asserting the same observable behaviour through different internal paths — flag as **should_fix**. The `changes-review` reviewer does the same audit independently in Phase A; this step is the verifier's first pass.

   **2.1. `Trivial:` claim audit** — For every plan task that declares a `Trivial:` justification, run `git diff <base>..HEAD -- <task's Files: block>` and check the production-code diff against the four parsimony criteria. Flag **must_fix** if any of the following hold:
   - the `Trivial:` field does not name an existing covering test or verification command, OR
   - net added lines of production code > 5 (excluding pure import lines, blank lines, and comment-only lines), OR
   - the diff introduces a new control-flow construct with a non-trivial body — `if/elif/else`, `match`, `for`/`while` loop, `try/except` (a one-line guard like `if x is None: return None` is NOT non-trivial; a multi-line block is), OR
   - the diff adds a new public symbol (function name not starting with `_`, class name not starting with `_`, module-level constant exported via `__all__`), OR
   - the diff adds a new error path (raises a new exception type, returns a new error sentinel, calls `logger.error`/`logger.warning` that did not exist).

   When flagged, the implementer must: remove the `Trivial:` field from the task, write a real RED test, and re-implement the task per the standard TDD loop. This audit is the post-implementation guardrail against the `Trivial:` field being abused to skip TDD; the planner's pre-implementation claim is not authoritative.
6. **Build** — Clean build, zero errors.
7. **File length** — Changed production files (non-test): >800 lines consider splitting, >1000 flag for review.
8. **Plan verify commands** — For each task's `Verify:` section, run each command wrapped in `timeout 30 <cmd> || echo 'TIMEOUT'`. Defer server-dependent commands (containing `curl`, `localhost`, `http://`, browser automation) to Phase B.
9. **Performance audit** — For each changed file on a hot path (UI render, request handler, polling loop, CLI inner loop): is expensive work (parsing, serialization, I/O, dependency loading) cached/memoized? Are heavy dependencies imported fully when lighter alternatives exist? Does repeated invocation redo work when input hasn't changed? **This is a static code review — no running program needed.** Performance issues from missing caching are structural and visible in the source.
10. **Feature Parity Check (migration/refactoring only)** — Skip unless the plan has a `## Feature Inventory` section.
    1. Compare old vs new implementation
    2. Verify each feature exists in new code
    3. Run new code and verify same behavior

    **If features are MISSING:** Run the iteration-cap check from Step 11 first (read `Iterations:` from the plan header; if `>= 3` ask the user Continue / Pivot / Abandon before incrementing). On Continue: add tasks with `[MISSING]` prefix, set `Status: PENDING`, increment `Iterations`, register status change, invoke `Skill(skill='spec-implement', args='<plan-path>')`.
