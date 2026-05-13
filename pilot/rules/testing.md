## Testing

### Default Posture: Parsimonious

**Default: reuse existing behavioural tests first; when a new public production class truly needs new tests, the ceiling is 1 unit test class + 1 functional test class (only when behaviour cannot be exercised through unit tests).** Multiply test classes only when the production class has genuinely independent behavioural axes that warrant separation. Avoid one-test-class-per-method, redundant assertions on the same path, and tests written purely to push a coverage number above a threshold.

The structure of tests should be **contra-variant** with the structure of code (Uncle Bob, *Test Contravariance*) — the one-unit-plus-one-functional ceiling is not a mandate to mirror every production class, and coupling test layout to code layout is what produces fragile, refactor-resistant suites. Kent Beck's *Test Desiderata* names the property explicitly: tests should be **structure-insensitive** — their pass/fail signal must respond to behaviour change, not to where you happened to put a method today.

**Local override.** A project that wants strict-TDD or blanket-coverage behaviour creates `.claude/rules/testing-project.md` in the repository — that file shadows this global rule. See the [Rules & Standards § Override the testing posture](https://pilot-shell.com/docs/features/rules#override-the-testing-posture) docs for a sample shadow rule and the full anti-patterns table.

> **Why this rule exists.** User feedback (paraphrased): *"90% of the time, the agent tries to test too much, doing redundant tests that just add to the maintenance cost of the codebase. It also tends to create one test class for each tiny part of the logic of a given class instead of 1 class = 1 unit test + 1 functional test (if needed)."* This default codifies that complaint as the rule.

### TDD — Default with Documented Escapes

**⛔ Default: have a failing test before you write production code.**

#### Red-Green-Refactor

1. **RED** — One minimal test for the desired behavior. Behavior, not implementation. Mocks for external deps only. Naming: Python `test_<function>_<scenario>_<expected>` | TS `it("should <behavior> when <condition>")`.
2. **VERIFY RED** — Run it; confirm it fails because the feature doesn't exist (not syntax). If it passes → rewrite.
3. **GREEN** — Simplest code that passes. No extras, no refactor. Hardcoding is fine.
4. **VERIFY GREEN** — Full suite passes. Check diagnostics.
5. **REFACTOR** — Improve quality; tests stay green; no new behavior.

**TDD applies to:** new functions, API endpoints, business logic, bug fixes (reproduce first), behavior changes.

**Skip RED when:**
- Docs, config, dep version bumps, formatting-only changes.
- The plan task carries a `Trivial:` justification naming the existing covering test or verification command (≤ 5 net new lines of production code, no new branch/loop/try with a non-trivial body, no new public symbol, no new error path). The reviewer agent (`pilot/agents/changes-review.md`) and the verify step (`pilot/skills/spec-verify/steps/02-automated-checks.md` § 2.1) audit the claim against the actual diff — the planner's claim is NOT authoritative.
- **Bugfixes never qualify for the `Trivial:` escape.** A bugfix without a reproducing test is a rubber-stamp fix; the reproducing test is the regression-prevention guarantee.

**Recovery (code before test):** don't revert — write the test now, verify it catches regressions. Goal is coverage of behaviour that matters, not ritual.

---

### Test Strategy & Coverage

**Unit for logic, integration for interactions, E2E for workflows.**

| Type | When | Requirements |
|------|------|--------------|
| **Unit** | Pure functions, business logic, validation | <1 ms each, mock ALL external deps, `@pytest.mark.unit` |
| **Integration** | DB, external APIs, file I/O, auth flows | Real test deps, fixtures, cleanup, `@pytest.mark.integration` |
| **E2E** | Complete user workflows, API chains | Test entire flow |

External deps? No → unit. Yes → integration. Complete user workflow? Yes → E2E.

**Coverage rule:** Coverage is a diagnostic, not a quota. Critical paths (business logic, security, data integrity, error handling) must have explicit behaviour coverage and no obvious coverage regressions. For glue code, configuration plumbing, simple CRUD, and trivial UI bindings, no numeric coverage gate — the parsimony audit (verify Step 5) and the reviewer agent replace the gate. Padding tests purely to push a coverage number above a threshold is a parsimony anti-pattern.

### Property-Based Testing (PBT)

Use when behavior depends on data shape, ranges, or combinations — not single known input.

| Lang | Tool | Example |
|------|------|---------|
| Python | `hypothesis` | `@given(st.lists(st.integers()))` |
| TypeScript | `fast-check` | `fc.assert(fc.property(fc.array(fc.integer()), ...))` |
| Go | `go test -fuzz` | `func FuzzFoo(f *testing.F) { f.Fuzz(...) }` |

**Use:** parsers, serializers, invariants, encode/decode roundtrips, bug-fix preservation. **Don't:** simple CRUD, UI, fixed-input validation, config. Supplements example-based tests, doesn't replace. Keep strategies simple. CI runs: `max_examples`/`numRuns` 100–200.

### Running Tests

```bash
uv run pytest -q                   # Python (quiet)
uv run pytest --cov=src            # Coverage report (gate is per-critical-path; see "Test Strategy & Coverage" above)
bun test                           # Bun
npm test -- --silent               # Jest/Vitest
```

### Mandatory Mocking in Unit Tests

| Call | MUST mock | Example |
|------|-----------|---------|
| HTTP/network | `httpx`, `requests` | `@patch("module.httpx.Client")` |
| Subprocess | `subprocess.run` | `@patch("module.subprocess.run")` |
| File I/O | `open`, `Path.read_text` | `@patch("builtins.open")` or `tmp_path` |
| Database | SQLite, PostgreSQL | Test fixtures |
| External APIs | Any third-party | Mock the client |

Mock at module level (where imported, not where defined). Test > 1 s = likely unmocked I/O.

### ⛔ E2E: Frontend/UI (MANDATORY for web apps)

Any change that affects what the user sees MUST be verified with browser automation — both `/spec` and quick mode. Unit tests don't catch layout bugs, stale bundles, or wiring issues. Tier priority and procedure: see `browser-automation.md` and `verification.md`.

### ⛔ Mock Audit on Dependency Changes

When a function gains a new dependency (subprocess, helper, I/O), update ALL existing tests for that function. Tests passing locally with real binaries fail in CI without them — the #1 cause of CI-only failures.

**Checklist:** (1) `Grep` the function name in `tests/`; (2) verify subprocess/I/O calls are mocked in each test; (3) run with `--tb=short` to surface unmocked calls fast.

### Anti-Patterns

- **Dependent tests** — each must work independently.
- **Testing implementation, not behavior** — assert outputs/state, not which mocks were called. `assert result == expected`, not `mock.assert_called_with(...)`. Behavior unchanged → tests still pass after refactor.
- **Incomplete mocks hiding structural assumptions** — mocks must mirror the complete real API, not just the fields you think you need. Partial mocks hide coupling and break against real data.
- **Unmocked environment dependencies** — locally-installed tools (semble, node) pass locally, fail CI. Mock every subprocess, PATH lookup, FS check for external tools.
- **Unnecessary mocks** — only for external deps.
- **Test-only methods in production** — never add methods/properties/flags purely for test access. Refactor so behavior is observable through public interfaces.
- **Mocking without understanding** — a mock that doesn't reflect real behavior is a lie. Tests pass against the lie, fail against reality.

### Test Parsimony — what NOT to do

- **One test class per method** — splitting a class's tests into per-method test classes (e.g. `DoSomethingTests`, `DoNothingTests` for class `Foo`). Anti-pattern. One test class per production class is the ceiling, not the floor.
- **Mirroring code structure in tests** — refactor moves a method, every test class follows. Tests should be contra-variant with code structure (Uncle Bob, *Test Contravariance*); a behaviour-preserving refactor must not break the suite.
- **Redundant assertions on the same path** — three tests asserting the same observable behaviour through three internal paths is one test, not three. The non-redundant ones are the ones that fail when behaviour changes; the rest are maintenance tax.
- **Test-per-trivial-helper** — a one-line getter or formatter does not need its own test class. If it has no branches, no I/O, and no public-API exposure, the test for the function that uses it is enough.
- **Coverage padding** — adding tests purely to push a coverage number above a threshold. Numbers are a side-effect of testing what matters, not the goal.

### ⛔ Zero Tolerance for Failing Tests

Every test failure MUST be fixed before work is done. Run the FULL suite, not just files you touched. "Pre-existing failure" is not an excuse — if you see it, you fix it.

### Completion Checklist

- [ ] Each new public class has at most 1 unit test class + at most 1 functional test class
- [ ] Tests assert observable behaviour, not internal structure
- [ ] No redundant tests on the same observable path
- [ ] Critical-path coverage adequate (no blanket %; reviewer judges)
- [ ] Tests follow naming convention
- [ ] Unit tests mock external dependencies
- [ ] Full test suite passes (0 failures) — not just your files
- [ ] Actual program executed and verified

### Assertion-Correctness Warning

Industry research (HumanEval across four LLMs) found > **62% of LLM-generated test assertions were incorrect** — passing tests asserting on the wrong field. False confidence is worse than no test.

Four mental checks before committing any assertion:

1. **One-character bug check** — would a one-char bug in the implementation still pass? `assert result` (truthy) ≠ `assert result == 42` (exact). If a tiny mistake survives, the assertion is too weak.
2. **Right field check** — `response.status` vs `response.body.error` is a common confusion. Confirm the assertion targets the field that carries meaning.
3. **Computed value check** — for hand-derived expected values, verify via a second path (different code, manual calculation, reference). Don't trust your own arithmetic.
4. **Spec-named behavior check** — assert the behavior the spec/contract names, not what you imagined. "User can perform X within rate limit" is named; "calls `_internal_fn` with `'QUEUED'`" is mechanics.

If you can't write a precise assertion because the spec is ambiguous, **STOP and ask** — don't pattern-match a plausible expected value.
