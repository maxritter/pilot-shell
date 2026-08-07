## Testing

### Default Posture: Parsimonious

**Reuse existing behavioural tests first.** When a new public production class genuinely needs new tests, the ceiling is 1 unit test class + 1 functional test class (the latter only when the behaviour can't be exercised through unit tests). Multiply test classes only when the production class has genuinely independent behavioural axes.

Tests should be **structure-insensitive**: the signal responds to behaviour change, not to where a method happens to live today. A behaviour-preserving refactor must not break the suite.

**Local override:** a project that wants strict-TDD or blanket-coverage behaviour ships `.claude/rules/testing-project.md`, which shadows this rule.

### TDD — default, with documented escapes

**⛔ Default: have a failing test before you write production code.**

RED (one minimal test for the desired *behaviour*) → verify it fails for the right reason, not a syntax error → GREEN (simplest thing that passes) → verify the full suite → refactor with tests green.

Applies to new functions, endpoints, business logic, behaviour changes, and bug fixes (reproduce first).

**Skip RED for:** docs, config, dependency bumps, formatting. Also for a plan task carrying a `Trivial:` justification that names the existing covering test (≤5 net new lines, no new branch/loop/try with a real body, no new public symbol, no new error path) — the changes review audits that claim against the diff, so the planner's word is not authoritative.

**⛔ Bugfixes never qualify for `Trivial:`.** A bugfix without a reproducing test is a rubber stamp.

If you wrote code before the test, don't revert — write the test now and confirm it catches the regression.

### Strategy and coverage

External deps? No → unit. Yes → integration. Complete user workflow? → E2E.

Unit tests must mock every external dependency — HTTP, subprocess, file I/O, database, third-party clients — at the point of *import*, not definition. A unit test taking >1s is a sign of unmocked I/O. Locally-installed tools are the classic CI-only failure: they pass on your machine and vanish in CI.

**When a function gains a new dependency, update every existing test for it.** Grep the function name across the test tree and check each call site mocks the new subprocess or I/O. This is the most common cause of CI-only failures.

Coverage is a diagnostic, not a quota. Critical paths — business logic, security, data integrity, error handling — need explicit behavioural coverage. Glue code, config plumbing, and trivial bindings get no numeric gate.

### ⛔ Frontend changes require browser verification

Any change to what the user sees must be verified with browser automation, in `/spec`, in `/build`, and in quick mode alike. Unit tests don't catch stale bundles, layout breakage, or wiring. Procedure and tool tiers: `browser-automation.md`.

### ⛔ Zero tolerance for failing tests

Run the full suite, not just the files you touched. "Pre-existing failure" is not an excuse — if you see it, you fix it, in a clearly-labelled separate commit when practical, or report it explicitly if the fix warrants its own change. This is the one sanctioned exception to the lineage rule.

### Assertions are where tests go wrong

Industry research across four LLMs found **>62% of generated test assertions were incorrect** — passing tests asserting the wrong field. False confidence is worse than no test. Before committing an assertion, check that a one-character bug in the implementation would actually fail it, that it targets the field carrying the meaning, that any hand-derived expected value came from an independent source, and that it asserts the behaviour the spec names rather than internal mechanics.

**Name the break first.** Before writing the test body, name the production change that would make this test fail. Can't name one → redesign around an observable behaviour. Only *intentional* decisions could fail it → it's a change detector; test the behaviour that depends on the decision instead.

**Then run the mutation check** before you finish: mentally mutate the implementation — wrong constant or argument, wrong branch taken, missing state change or side effect, empty/default return, missing validation for zero, empty, nil, unauthorized, or malformed input — and confirm at least one test fails for each. A mutation nothing catches marks the behaviour as unprotected, or the test as tautological.

If the spec is too ambiguous to write a precise assertion, **stop and ask** — don't pattern-match a plausible value.

### Anti-patterns

- **Tautological tests** — the expectation recomputes the value the way the implementation does, so it passes by construction. Expected values come from a known-good literal, a worked example, or the spec. (A spec-named invariant asserted property-style is fine; deriving the expectation from the implementation's own logic is not.)
- **Testing implementation, not behaviour** — asserting which mocks were called rather than the observable result. `assert result == expected`, not `mock.assert_called_with(...)`.
- **String-presence tests on source files** — asserting that a script, skill, prompt, or config file *contains* a line proves only that the source is the source, and it fails on every harmless rewording. Run the artifact and assert its effects: outputs, side effects, exit codes. Documents that instruct agents are tested by the consuming agent's behaviour; prose written for humans earns no test. (Asserting on text your test just *produced* — the output of a build, render, or transform it ran — is the correct form, not this trap.)
- **Change detectors** — `assert MAX_RETRIES == 5` can only fail when someone deliberately changes the constant, so it fires on redesign and sleeps through bugs. Assert the behaviour that depends on the decision: a failing call is retried 5 times and the 6th attempt never happens.
- **Asserting on the mock itself** — a `*-mock` test id or "the double was installed" assertion passes when the mock is present and fails when it is absent; it says nothing about the component. Assert the real component's behaviour, or unmock it.
- **Partial mocks** — a mock mirroring only the fields you think you need hides coupling and breaks against real data.
- **One test class per method**, or mirroring code structure in tests. One test class per production class is the ceiling, not the floor.
- **Redundant assertions on the same path** — three tests covering one observable behaviour through three internal routes is one test plus maintenance tax.
- **Coverage padding** — tests written to move a number rather than to catch a behaviour change.
- **Test-only production code** — never add a method, property, or flag purely for test access; refactor so the behaviour is observable through the public interface.
- **Dependent tests** — each must pass on its own, in any order.
