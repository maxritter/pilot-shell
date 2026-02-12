---
paths:
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/tests/**"
  - "**/conftest.py"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/__tests__/**"
  - "**/*_test.go"
---

## Testing Strategies and Coverage

**Core Rule:** Unit tests for logic, integration tests for interactions, E2E tests for workflows. Minimum 80% coverage required.

### Test Organization

Check existing structure before creating tests:

```
tests/
├── unit/              # Fast, isolated (< 1ms each)
├── integration/       # Real dependencies
└── e2e/              # Complete workflows
    └── postman/      # API collections (if applicable)
```

### Test Type Selection

**Unit Tests - Use When:**
- Testing pure functions and calculations
- Business logic without external dependencies
- Data transformations and parsing
- Input validation rules
- Utility functions

**Requirements:**
- Fast execution (< 1ms per test)
- Zero external dependencies (mock databases, APIs, filesystem)
- Test single behavior per test
- Use test markers (`@pytest.mark.unit`)

**Integration Tests - Use When:**
- Testing database queries and transactions
- External API calls
- Message queue operations
- File system operations
- Authentication flows

**Requirements:**
- Use real dependencies (test databases, not production)
- Setup/teardown fixtures for isolation
- Clean up data after each test
- Use test markers (`@pytest.mark.integration`)

**E2E Tests - Use When:**
- Testing complete user workflows
- API endpoint chains
- Data pipeline end-to-end flows

### Test Naming Convention

**Names must be self-documenting without reading code.**

**Python (pytest):** `test_<function>_<scenario>_<expected_result>`
- `test_process_payment_with_insufficient_funds_raises_error`
- `test_fetch_users_with_admin_role_returns_filtered_list`

**TypeScript/JS (Jest/Vitest):** `describe("<module>") + it("should <behavior> when <condition>")`
- `describe("processPayment") { it("should raise error with insufficient funds") }`
- `describe("fetchUsers") { it("should return filtered list for admin role") }`

### Running Tests

Identify framework first, then use minimal output:

```bash
# Python (pytest)
uv run pytest -q                              # Quiet mode (preferred)
uv run pytest -q -m unit                      # Unit only
uv run pytest tests/unit/test_auth.py -q      # Specific file

# TypeScript/JS (Jest/Vitest/Bun)
bun test                                      # Bun
npm test -- --silent                          # Jest/Vitest quiet
npx vitest run tests/unit/auth.test.ts        # Specific file
```

### Coverage Requirements

**Before marking work complete:**

1. Run coverage with the project's test runner:
   - Python: `uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80`
   - Jest/Vitest: `npx vitest run --coverage` or `npm test -- --coverage`
   - Bun: `bun test --coverage`
2. Verify ≥ 80% coverage on new code
3. Add tests for uncovered critical paths

**Must cover:**
- All business logic functions
- All API endpoints
- All data transformations
- All validation rules
- All error handling paths
- All conditional branches

**Exclude from coverage:**
- `if __name__ == "__main__"` blocks
- Generated code (migrations, protobuf)
- Configuration files
- Simple getters/setters with no logic

### Test Fixtures

Reuse setup code via fixtures:

```python
# Python (pytest)
@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.close()
```

```javascript
// JavaScript (Jest)
beforeEach(() => { /* Setup */ });
afterEach(() => { /* Cleanup */ });
```

Each test must start with clean, isolated state.

### AI Assistant Workflow

When implementing functionality:

1. Search codebase for similar test patterns
2. Determine test type (unit/integration/E2E) based on dependencies
3. Write failing test first (TDD)
4. Reuse existing fixtures
5. Follow naming convention
6. Run test to verify failure
7. Implement minimal code to pass
8. Run all tests to prevent regressions
9. Verify coverage ≥ 80%
10. Execute actual program

### E2E Testing Patterns

**For APIs:**

```bash
# Test with curl
curl -s http://localhost:8000/health | jq
curl -X POST http://localhost:8000/api/resource -H "Content-Type: application/json" -d '{"name": "test"}'
```

Test assertions:
- HTTP status codes (200, 201, 400, 401, 404, 500)
- Response time thresholds
- JSON schema validation
- State changes (database records)

**For Data Pipelines:**

Run actual pipeline, verify:
- Source extraction completes
- Transformations produce expected output
- Destination receives correct data
- Data quality checks pass
- Logs show expected flow

**For Frontend/UI (MANDATORY for web apps):**

Use `playwright-cli` to test actual UI rendering and user workflows:

```bash
playwright-cli open http://localhost:3000
playwright-cli snapshot                      # Get interactive elements with refs
playwright-cli fill e1 "test@example.com"    # Fill form
playwright-cli click e2                      # Submit
playwright-cli run-code "async page => { await page.waitForLoadState('networkidle'); }"
playwright-cli snapshot                      # Verify result
playwright-cli close
```

Test assertions:
- UI renders correctly after operations
- Forms submit and show success/error states
- Navigation works between pages
- Data displays correctly after CRUD

**Why:** API tests verify backend works. playwright-cli verifies **what the user sees**. See `playwright-cli.md` for full command reference.

### ⛔ CRITICAL: Mandatory Mocking in Unit Tests

**Unit tests MUST mock ALL external calls. No exceptions.**

| Call Type | MUST Mock | Example |
|-----------|-----------|---------|
| HTTP/Network | `httpx`, `urllib`, `requests` | `@patch("module.httpx.Client")` |
| Subprocess | `subprocess.run`, `subprocess.Popen` | `@patch("module.subprocess.run")` |
| File I/O | `open`, `Path.read_text` | `@patch("builtins.open")` or use `tmp_path` |
| Database | SQLite, PostgreSQL connections | Use test fixtures |
| External APIs | Any third-party service | Mock the client |

**Why this is non-negotiable:**
- Real network calls make tests slow (5+ seconds vs milliseconds)
- Real calls cause flaky tests (network failures, rate limits)
- Tests must work offline and in CI without credentials
- Hanging tests waste developer time and CI resources

**Pattern - Mock at module level:**
```python
# GOOD - mock where imported, not where defined
@patch("mymodule.httpx.Client")
def test_fetch_data(mock_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_client.return_value.__enter__.return_value.get.return_value = mock_response

    result = fetch_data()  # Uses mocked httpx
    assert result == {"data": "test"}

# BAD - no mock, makes real network call
def test_fetch_data():
    result = fetch_data()  # HANGS or fails without network
```

**Detecting unmocked calls:**
- Test takes > 1 second → likely unmocked I/O
- Test fails with "Connection refused" → unmocked network
- Test hangs indefinitely → unmocked blocking call

### Common Mistakes

**Dependent tests:**
```python
# BAD - test2 depends on test1 running first
def test1_create_user():
    create_user("test")

def test2_update_user():
    get_user("test")  # Assumes test1 ran
```

**Testing implementation instead of behavior:**
```python
# BAD - tests internal variable
def test_internal_counter_increments():
    obj._counter += 1
    assert obj._counter == 1

# GOOD - tests behavior
def test_process_increments_total():
    obj.process()
    assert obj.get_total() == 1
```

**Other mistakes to avoid:**
- Ignoring failing tests (fix or remove immediately)
- Committing commented-out tests
- Time-dependent assertions (causes flakiness)
- Relying on external services in unit tests
- Missing cleanup between tests
- **Making real network/subprocess calls in unit tests (NEVER)**

### ⛔ MANDATORY: Fix ALL Errors (Tests, Types, Lint)

**Fix ALL verification errors before marking work complete — no exceptions.** See `verification-before-completion.md` for the full policy, invalid excuses table, and auto-fix rules in /spec workflows.

### Test Markers

Organize tests by type for selective execution:

```python
# Python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.slow
```

```javascript
// JavaScript
describe.skip('integration tests', () => {});
```

Use to run fast tests during development, full suite in CI/CD.

### Decision Tree

```
Does function use external dependencies?
├─ NO → Unit test (mock all external calls)
└─ YES → Integration test (use real dependencies)

Is this a complete user workflow?
├─ YES → E2E test (test entire flow)
└─ NO → Unit or integration test
```

### Testing Anti-Patterns

**Anti-Pattern: Asserting on Mock Existence**

Don't verify mocks are present; test real behavior.

```typescript
// BAD: Testing mock exists
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});

// GOOD: Test real behavior
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});
```

**Detection:** If assertion contains `*-mock` or only checks `toHaveBeenCalled` without verifying behavior, delete or rewrite.

**Anti-Pattern: Test-Only Methods in Production Code**

Never add methods to production classes that are only called from tests.

```typescript
// BAD: Production method only used in tests
class Session {
  async destroy() { /* only called in afterEach */ }
}

// GOOD: Test utility function
// test-utils.ts
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) await workspaceManager.destroyWorkspace(workspace.id);
}
```

**Detection:** Before adding a method to a production class, search: is it only called from test files? If yes, create a test utility instead.

**Anti-Pattern: Incomplete Mock Data**

Mock data must match real API/response structure completely.

```typescript
// BAD: Missing fields — code accessing response.metadata.requestId silently fails
const mockResponse = { status: 'success', data: { userId: '123' } };

// GOOD: Complete structure
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 }
};
```

**Before creating mock data:** Check real API response, include ALL fields, use realistic values.

### Completion Checklist

Before marking testing complete:

- [ ] All new functions have tests
- [ ] Tests follow naming convention
- [ ] Unit tests mock external dependencies
- [ ] Integration tests use real dependencies
- [ ] All tests pass
- [ ] Coverage ≥ 80% verified
- [ ] No flaky or dependent tests
- [ ] Actual program executed and verified

**If any checkbox unchecked, testing is incomplete.**
