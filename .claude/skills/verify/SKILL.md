---
name: verify
description: Run tests and fix issues end-to-end with Claude CodePro
---
# VERIFY MODE: Verification and Quality Assurance Process with Code Review

> **WARNING: DO NOT use the Task tool with any subagent_type (Explore, Plan, general-purpose).**
> Perform ALL verification yourself using direct tool calls (Read, Grep, Glob, Bash, MCP tools).
> Sub-agents lose context and make verification inconsistent.

**Available MCP Tools:**
- **Context7** - Library documentation lookup: `resolve-library-id(query, libraryName)` then `query-docs(libraryId, query)` - descriptive queries required (see `context7-docs.md`)
- **mcp-cli** - Custom MCP servers via `mcp-cli <server>/<tool> '<json>'` for servers in `mcp_servers.json`

## The Process

**Unit tests → Integration tests → Program execution (with log inspection) → Rules audit → Coverage → Quality → Code review → E2E tests → Final verification**

**All test levels are MANDATORY:** Unit tests alone are insufficient. You must run integration tests AND E2E tests AND execute the actual program with real data.

Active verification with comprehensive code review that immediately fixes issues as discovered, ensuring all tests pass, code quality is high, and system works end-to-end.

### Step 1: Run & Fix Unit Tests

Run unit tests and fix any failures immediately.

**If failures:** Identify → Read test → Fix implementation → Re-run → Continue until all pass

### Step 2: Run & Fix Integration Tests

Run integration tests and fix any failures immediately.

**Common issues:** Database connections, mock configuration, missing test data

### Step 3: Build and Execute the Actual Program (MANDATORY)

**⚠️ CRITICAL: Tests passing ≠ Program works**

Run the actual program and verify real output.

**Execution checklist:**
- [ ] Build/compile succeeds without warnings
- [ ] Program starts without errors
- [ ] **Inspect logs** - Check for errors, warnings, stack traces
- [ ] Verify expected output matches actual output
- [ ] Test with real/sample data, not just mocks

**If bugs are found:**

| Bug Type | Action |
|----------|--------|
| **Minor** (typo, off-by-one, missing import) | Fix immediately, re-run, continue verification |
| **Major** (logic error, missing function, architectural issue) | Add task to plan, set PENDING, exit verify → loop back |

**Rule of thumb:** If you can fix it in < 5 minutes without writing new tests, fix inline. Otherwise, add a task.

### Step 3a: Feature Parity Check (if applicable)

**For refactoring/migration tasks:** Verify ALL original functionality is preserved.

**Process:**
1. Compare old implementation with new implementation
2. Create checklist of features from old code
3. Verify each feature exists in new code
4. Run new code and verify same behavior as old code

**If features are MISSING:**

This is a serious issue - the implementation is incomplete.

1. **Add new tasks to the plan file:**
   - Read the existing plan
   - Add new tasks for each missing feature (follow existing task format)
   - Mark new tasks with `[MISSING]` prefix in task title
   - Update the Progress Tracking section with new task count
   - Add note: `> Extended [Date]: Tasks X-Y added for missing features found during verification`

2. **Set plan status to PENDING and increment Iterations:**
   ```
   Edit the plan file:
   Status: COMPLETE  →  Status: PENDING
   Iterations: N     →  Iterations: N+1
   ```

3. **Inform user:**
   ```
   🔄 Iteration N+1: Missing features detected, looping back to implement...

   Found [N] missing features that need implementation:
   - [Feature 1]
   - [Feature 2]

   The plan has been updated with [N] new tasks.
   ```

4. **EXIT verify process** - Do not continue to Step 4+. The /spec workflow will automatically loop back to /implement.

### Step 4: Rules Compliance Audit

**MANDATORY: Verify work complies with ALL project rules before proceeding.**

#### Process

1. **Discover all rules:**
   ```
   Glob(".claude/rules/standard/*.md") → Read each file
   Glob(".claude/rules/custom/*.md") → Read each file
   ```

2. **For each rule file:**
   - Read the entire file
   - Extract the key requirements and constraints
   - Check if each requirement was followed during implementation
   - Note any violations

3. **Classify violations:**
   - **Fixable Now:** Can be remediated immediately (run missing commands, apply fixes)
   - **Structural:** Cannot be fixed retroactively (missed TDD cycle, architectural issues)

4. **Remediate:** Execute fixes for all fixable violations before continuing

#### Output Format

```
## Rules Compliance Audit

### Rules Checked
- `.claude/rules/standard/[filename].md` - [Brief description]
- `.claude/rules/custom/[filename].md` - [Brief description]
- ...

### ✅ Compliant
- [Rule file]: [Requirements that were followed]

### ⚠️ Violations Found (Fixable)
- [Rule file]: [Violation] → [Fix action to execute now]

### ❌ Violations Found (Structural)
- [Rule file]: [Violation] → [What should have been done differently]

### Remediation
[Execute each fix action listed above]
[Show output/evidence of fixes applied]
```

#### Completion Gate

**DO NOT proceed to Step 5 until:**
- All rule files have been read and checked
- All fixable violations have been remediated
- Structural violations have been documented

**If serious structural violations exist:** Consider whether to continue or restart implementation.

### Step 5: Call Chain Analysis

**Perform deep impact analysis for all changes:**

1. **Trace Upwards (Callers):**
   - Identify all code that calls modified functions
   - Verify they handle new return values/exceptions
   - Check for breaking changes in interfaces

2. **Trace Downwards (Callees):**
   - Identify all dependencies of modified code
   - Verify correct parameter passing
   - Check error handling from callees

3. **Side Effect Analysis:**
   - Database state changes
   - Cache invalidation needs
   - External system impacts
   - Global state modifications

### Step 6: Check Coverage

Verify test coverage meets requirements.

**If insufficient:** Identify uncovered lines → Write tests for critical paths → Verify improvement

### Step 7: Run Quality Checks

Run automated quality tools and fix any issues found.

### Step 8: Code Review Simulation

**Perform self-review using code review checklist:**

- [ ] **Logic Correctness:** Edge cases handled, algorithms correct
- [ ] **Architecture & Design:** SOLID principles, no unnecessary coupling
- [ ] **Performance:** No N+1 queries, efficient algorithms, no memory leaks
- [ ] **Security:** No SQL injection, XSS, proper auth/authz
- [ ] **Readability:** Clear naming, complex logic documented
- [ ] **Error Handling:** Graceful error handling, adequate logging
- [ ] **Convention Compliance:** Follows project standards

**If issues found:** Document and fix immediately

### Step 9: E2E Verification (MANDATORY for apps with UI/API)

**⚠️ Unit + Integration tests are NOT enough. You MUST also run E2E tests.**

Run end-to-end tests to verify the complete user workflow works.

#### For APIs: Manual or Automated API Testing

**When applicable:** REST APIs, GraphQL APIs, authentication systems, microservices

**Test with curl:**
```bash
# Health check
curl -s http://localhost:8000/health | jq

# CRUD operations
curl -X POST http://localhost:8000/api/resource -H "Content-Type: application/json" -d '{"name": "test"}'
curl -s http://localhost:8000/api/resource/1 | jq
curl -X PUT http://localhost:8000/api/resource/1 -H "Content-Type: application/json" -d '{"name": "updated"}'
curl -X DELETE http://localhost:8000/api/resource/1
```

**Verify:**
- All requests succeed with expected status codes
- Response times are acceptable
- Authentication flows work correctly
- CRUD operations complete successfully
- Error scenarios return proper error codes

**If failures:** Analyze failure → Check API endpoint → Fix implementation → Re-run → Continue until all pass

### Step 10: Final Verification

**Run everything one more time:**
- All tests
- Program build and execution
- Diagnostics
- Call chain validation

**Success criteria:**
- All tests passing
- No diagnostics errors
- Program builds and executes successfully with correct output
- Coverage ≥ 80%
- All Definition of Done criteria met
- Code review checklist complete
- No breaking changes in call chains

### Step 11: Update Plan Status

**Status Lifecycle:** `PENDING` → `COMPLETE` → `VERIFIED`

**When ALL verification passes (no missing features, no bugs, rules compliant):**

1. **MANDATORY: Update plan status to VERIFIED**
   ```
   Edit the plan file and change the Status line:
   Status: COMPLETE  →  Status: VERIFIED
   ```
2. Read the Iterations count from the plan file
3. Inform user: "✅ Iteration N: All checks passed - VERIFIED"

**When verification FAILS (missing features, serious bugs, or unfixed rule violations):**

1. Add new tasks to the plan for missing features/bugs
2. **Set status back to PENDING and increment Iterations:**
   ```
   Edit the plan file:
   Status: COMPLETE  →  Status: PENDING
   Iterations: N     →  Iterations: N+1
   ```
3. Inform user: "🔄 Iteration N+1: Issues found, fixing and re-verifying..."
4. **The /spec workflow handles this automatically** - do not tell user to run another command
5. /spec will re-read status, see PENDING, and run /implement again

**Fix immediately | Test after each fix | No "should work" - verify it works | Keep fixing until green**
