## Testing

### TDD — Mandatory Workflow

**⛔ STOP: Do you have a failing test? If not, write the test FIRST.**

#### The Red-Green-Refactor Cycle

1. **RED** — Write one minimal test for the desired behavior. Focus on behavior, not implementation. Mocks only for external deps.
   - **Naming:** Python: `test_<function>_<scenario>_<expected>` | TS: `it("should <behavior> when <condition>")`
2. **VERIFY RED** — Run the test, confirm it fails because the feature doesn't exist (not syntax errors). If it passes → rewrite.
3. **GREEN** — Write the simplest code that passes. No extras, no refactoring. Hardcoding is fine.
4. **VERIFY GREEN** — Run all tests, confirm they pass. Check diagnostics.
5. **REFACTOR** — Improve code quality (tests must stay green). No new behavior.

**When TDD applies:** New functions, API endpoints, business logic, bug fixes (reproduce first), behavior changes.

**Skip:** Documentation, config updates, dependency versions, formatting-only.

**Recovery (code written before test):** Don't revert — write the test immediately, verify it catches regressions. Goal is coverage, not ritual.

---

### Test Strategy & Coverage

**Unit tests for logic, integration tests for interactions, E2E tests for workflows. Minimum 80% coverage.**

| Type | Use When | Requirements |
|------|----------|--------------|
| **Unit** | Pure functions, business logic, validation, utilities | < 1ms each, mock ALL external deps, `@pytest.mark.unit` |
| **Integration** | DB queries, external APIs, file I/O, auth flows | Real test deps, fixtures, cleanup, `@pytest.mark.integration` |
| **E2E** | Complete user workflows, API chains, data pipelines | Test entire flow |

```
External dependencies? NO → Unit test | YES → Integration test
Complete user workflow? YES → E2E test | NO → Unit or integration
```

### Property-Based Testing (PBT)

**Use PBT when behavior depends on data shape, ranges, or combinations — not a single known input.**

| Language | Tool | Example |
|----------|------|---------|
| Python | `hypothesis` | `@given(st.lists(st.integers()))` |
| TypeScript | `fast-check` | `fc.assert(fc.property(fc.array(fc.integer()), ...))` |
| Go | `go test -fuzz` | `func FuzzFoo(f *testing.F) { f.Fuzz(...) }` |

**When to use:** Parsers, serializers, data structure invariants, encode/decode roundtrips, bugfix preservation properties.

**When NOT to use:** Simple CRUD, UI interactions, fixed-input validation, config changes.

**Rules:** PBT supplements example-based tests — don't replace them. Keep strategies simple (avoid deeply nested custom strategies). Set `max_examples` / `numRuns` low enough for CI (100–200).

### Running Tests

```bash
uv run pytest -q                              # Python (quiet)
uv run pytest --cov=src --cov-fail-under=80  # Coverage
bun test                                      # Bun
npm test -- --silent                          # Jest/Vitest
```

### Mandatory Mocking in Unit Tests

| Call Type | MUST Mock | Example |
|-----------|-----------|---------|
| HTTP/Network | `httpx`, `requests` | `@patch("module.httpx.Client")` |
| Subprocess | `subprocess.run` | `@patch("module.subprocess.run")` |
| File I/O | `open`, `Path.read_text` | `@patch("builtins.open")` or `tmp_path` |
| Database | SQLite, PostgreSQL | Use test fixtures |
| External APIs | Any third-party | Mock the client |

Mock at module level (where imported, not where defined). Test > 1s = likely unmocked I/O.

### ⛔ E2E: Frontend/UI (MANDATORY for web apps)

**Any change that affects what the user sees MUST be verified with browser automation** — in both `/spec` and quick mode. Unit tests do not catch layout bugs, stale bundles, or wiring issues.

**Tool priority:** Claude Code Chrome (preferred) → Chrome DevTools MCP (enterprise fallback) → playwright-cli (thorough) → agent-browser (lightweight). See `browser-automation.md` for detection and workflow. See `verification.md` for the quick-mode procedure.

### ⛔ Mock Audit on Dependency Changes

**When adding a new dependency to an existing function (new subprocess call, new helper function, new I/O), you MUST update ALL existing tests for that function.** Search for the function name in test files and add mocks for the new dependency to every test. Tests that pass locally with real binaries/files will fail in CI where those binaries don't exist. This is the #1 cause of CI-only test failures.

**Checklist when modifying a function's dependencies:**
1. `Grep` for the function name in `tests/` directories
2. For each test: verify all subprocess/I/O calls are mocked
3. Run tests with `--tb=short` to catch unmocked calls fast

### Anti-Patterns

- **Dependent tests** — each test must work independently
- **Testing implementation, not behavior** — assert outputs and state changes, not that specific mocks were called. `assert result == expected` not `mock.assert_called_with(...)`. If the implementation changes but behavior stays the same, tests should still pass.
- **Incomplete mocks hiding structural assumptions** — mocks must mirror the complete real API structure, not just the fields you think you need. Partial mocks hide coupling to downstream fields and break when the real API returns additional or different data.
- **Unmocked environment dependencies** — tests that rely on locally-installed tools (probe, node, etc.) pass locally but fail in CI. Every subprocess call, PATH lookup, and filesystem check for external tools must be mocked in unit tests.
- **Unnecessary mocks** — only for external deps
- **Test-only methods in production** — never add methods, properties, or flags to production classes purely for test access. If you need internal state for testing, refactor the design so the behavior is observable through public interfaces.
- **Mocking without understanding** — before mocking a dependency, understand what it actually does. A mock that doesn't reflect real behavior is a lie — tests pass against the lie, then fail against reality.

### ⛔ Zero Tolerance for Failing Tests

**Every test failure MUST be fixed before work is done.** Run the FULL suite, not just files you touched. "Pre-existing failure" is not an excuse — if you see it, you fix it. A green suite is a prerequisite, not a nice-to-have.

### Completion Checklist

- [ ] All new functions have tests
- [ ] Tests follow naming convention
- [ ] Unit tests mock external dependencies
- [ ] **Full test suite passes (0 failures)** — not just your files
- [ ] Coverage ≥ 80% verified
- [ ] Actual program executed and verified

### Assertion-Correctness Warning

Industry research (HumanEval evaluation across four LLMs) found over **62% of LLM-generated test assertions were incorrect**. This is the single most likely failure mode in LLM-driven TDD: the test passes, but it's testing the wrong thing. A test asserted on the wrong field is worse than no test — it provides false confidence.

Before committing any assertion, run these four mental checks:

1. **One-character bug check** — would a one-character bug in the implementation still let this assertion pass? `assert result` (truthy) and `assert result == 42` (exact) catch very different things. If a tiny mistake survives the check, the assertion is too weak.
2. **Right field check** — `response.status` vs `response.body.error` is a common confusion. Confirm the assertion targets the field that actually carries the meaning, not an adjacent field that happens to be set.
3. **Computed value check** — for any expected value derived by hand, verify it via a second path (different code, manual calculation, reference doc). Don't trust your own arithmetic.
4. **Spec-named behavior check** — assert on the behavior the spec/contract names, not the behavior you imagined. "User can perform X within rate limit" is named; "calls `_internal_fn` with status `'QUEUED'`" is mechanics.

If you can't write a precise assertion because the spec is ambiguous, **STOP and ask** — don't pattern-match a plausible expected value. See also the existing RED step (above) for *why* a test must fail before you write code that makes it pass.
