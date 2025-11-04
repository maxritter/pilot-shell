---
description: Run comprehensive end-to-end verification after implementation - reads plan, checks all changes, runs all tests, verifies data integrity, ensures TDD compliance
model: sonnet
---

# Comprehensive Implementation Verification

**Purpose:** Thorough E2E verification after plan completion, ensuring all requirements met, tests pass, data integrity maintained.

**Workflow Position:** Step 3 of 3 in spec-driven development
- **Previous command (/plan):** Idea → Design → Implementation Plan
- **Previous command (/implement):** Implementation Plan → Working Code
- **This command (/verify):** Working Code → Verified Implementation

**Process:** Read plan → Understand changes → Run all tests → Verify data → Check standards → Generate report

## Process

### Step 1: Gather Context

**Understand what was built:**
1. Read plan: `Read(file_path="docs/plans/YYYY-MM-DD-*.md")` - Extract requirements, tasks, architecture
2. Check changes: `git status --short` and `git diff --stat` - See all modified files
3. Query Cipher: `ask_cipher("What was implemented for [feature]? Key patterns and decisions?")`
4. Search codebase: `search_code(path="/workspaces/...", query="new implementations from plan")`
5. Check diagnostics: `getDiagnostics()` - Must be zero errors/warnings

### Step 2: Execute Actual Program

**Run the actual code FIRST to verify functionality:**

```bash
# ETL Pipeline
uv run python src/main.py
# Verify: Logs show success, check DB records, inspect S3 files

# API Server
uv run python src/app.py &  # Start server
curl -X POST localhost:8000/api/endpoint -d '{"test": "data"}'
# Verify: Response correct, check DB records

# CLI Tool
uv run python src/cli.py --command test
# Verify: Expected output shown, files created

# Background Job
uv run python src/worker.py
# Verify: Job completes, side effects visible
```

**Show actual outputs (logs, responses, files) - NO "should work" claims**

### Step 3: Run Test Suites

**Execute ALL test types (MANDATORY):**

```bash
# Unit tests
uv run pytest -m unit -v --tb=short
# Expected: 100% pass

# Integration tests
uv run pytest -m integration -v --tb=short
# Expected: 100% pass

# All tests with coverage
uv run pytest --cov=. --cov-report=term-missing --cov-fail-under=80
# Expected: >80% coverage, all new code covered

# E2E API tests (if API changes)
newman run postman/collections/*.json -e postman/environments/dev.json
# Expected: All collections pass
```

### Step 4: Data Verification

**Verify source → target data integrity:**

1. **Database checks (if data pipeline):**
```sql
-- Count source records
SELECT COUNT(*) FROM source_table;
-- Count target records
SELECT COUNT(*) FROM target_table;
-- Verify data completeness
SELECT * FROM target WHERE source_id NOT IN (SELECT id FROM source);
```

2. **API verification (if REST/GraphQL):**
```bash
# Test all endpoints
for endpoint in $(grep -r "route\|endpoint" --include="*.py" | cut -d'"' -f2); do
  curl -X GET "localhost:8000$endpoint" -w "\n%{http_code}\n"
done
```

3. **UI verification (if frontend):**
```javascript
// Enable Playwright
discover_tools_by_words(words="playwright browser", enable=true)
// Navigate and verify
browser_navigate(url="http://localhost:3000")
browser_snapshot()
// Check key elements exist
browser_get_element_text(selector="[data-testid='feature']")
```

### Step 5: Code Quality Checks

**Standards compliance:**

```bash
# Python linting
uv run ruff check . --statistics
# Expected: 0 violations

# Format check
uv run ruff format . --check
# Expected: All files formatted

# Type checking
uv run mypy src --strict
# Expected: Success, no errors

# Security scan
uv run bandit -r src
# Expected: No high/medium issues

# Complexity check
uv run radon cc src -s -nb
# Expected: A or B ratings
```

### Step 6: TDD Compliance Verification

**Verify test-first development:**

1. Check test files exist for all source files:
```bash
for src in $(find src -name "*.py" -not -path "*/tests/*"); do
  test_file="tests/$(basename $src | sed 's/\.py$/_test.py/')"
  [[ -f "$test_file" ]] || echo "Missing test: $test_file"
done
```

2. Verify tests were written before code (git history):
```bash
for file in $(git diff --name-only HEAD~10 | grep -E "\.py$"); do
  git log --oneline --follow "$file" | tail -5
done
```

3. Check test quality:
- Tests have descriptive names
- Tests verify behavior, not implementation
- No test pollution or excessive mocking

### Step 7: Performance Verification

**If applicable, check performance:**

```bash
# Load testing for APIs
ab -n 1000 -c 10 http://localhost:8000/api/endpoint

# Memory profiling
uv run python -m memory_profiler src/main.py

# Query performance
EXPLAIN ANALYZE SELECT * FROM large_table;
```

### Step 8: Documentation Verification

**Ensure documentation matches implementation:**

1. API docs match actual endpoints
2. README instructions work
3. Docstrings present for public functions
4. Type hints complete

### Step 9: Generate Verification Report

```markdown
## ✅ Verification Report - [Feature Name]

**Date:** [YYYY-MM-DD]
**Plan:** docs/plans/[plan-file].md

### Test Results
- Unit Tests: X/X passed (100%)
- Integration Tests: X/X passed (100%)
- E2E Tests: X/X passed (100%)
- Coverage: XX% (target: 80%)

### Data Integrity
- Source Records: X
- Target Records: X
- Data Validation: ✅ Complete match

### Code Quality
- Linting: 0 violations
- Type Checking: ✅ Passed
- Security: No issues
- Complexity: A rating

### TDD Compliance
- All source files have tests: ✅
- Tests written first: ✅ Verified
- Test quality: ✅ High

### Performance (if tested)
- Response time: Xms avg
- Throughput: X req/s
- Memory usage: XMB

### Issues Found
[List any issues discovered]

### Recommendations
[Any improvements suggested]

**Conclusion:** Implementation verified successfully.
```

## MCP Tools for Verification

**Testing:** IDE (`getDiagnostics`)
**Memory:** Cipher (`ask_cipher`) | Claude Context (`search_code`)
**Data:** Database (`execute_sql`) | Playwright (`browser_*` for UI)
**Analysis:** FireCrawl (external API testing) | Newman (Postman collections)

## Verification Checklist

**Must Pass ALL:**
- [ ] Zero diagnostics errors
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Coverage > 80%
- [ ] Source/target data match
- [ ] Linting clean
- [ ] Type checking passes
- [ ] Security scan clean
- [ ] TDD compliance verified

## When to FAIL Verification

**Stop and report issues if:**
- Any test fails
- Coverage < 80% or new code uncovered
- Data integrity issues found
- Security vulnerabilities detected
- TDD not followed (code before tests)
- Performance degradation > 20%

## Store Results

After verification:
```
ask_cipher("Store: Verification of [feature] complete.
Tests: [results]
Coverage: [percentage]
Data integrity: [status]
Issues: [any found]
Performance: [metrics if tested]")
```

## Key Principles

**Be thorough** | **No assumptions** | **Evidence-based** | **Fail fast on issues** | **Document everything**

**Success = ALL checks pass. Partial success = FAILURE.**