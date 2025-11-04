---
description: Use when partner provides a complete implementation plan to execute - loads plan, reviews critically, executes tasks in batches, reports for review between batches
model: sonnet
---

# Implementing Specification Plans

## Overview

Load plan, review critically, execute tasks in batches, report for review between batches.

**Core principle:** Batch execution with checkpoints for architect review.

**Workflow Position:** Step 2 of 3 in spec-driven development
- **Previous command (/plan):** Idea → Design → Implementation Plan
- **This command (/implement):** Implementation Plan → Working Code
- **Next command (/verify):** Working Code → Verified Implementation

**Input location:** `docs/plans/YYYY-MM-DD-<feature-name>.md`
**Output:** Working, tested code

## Session Context Awareness

**Session states:** Fresh start | After `/remember`+`/clear` | Ongoing session

**ALWAYS read plan first**, then:
- Check git status/diff for progress
- Query Cipher for stored learnings
- Search codebase with Claude Context
- Determine completed tasks from evidence
- Continue from next pending task

**After `/remember`+`/clear` preserved:** ✅ Plan, Code, Tests, Cipher, Codebase | ❌ Conversation

## MCP Tools for Implementation

1. **IDE Diagnostics** (FIRST & LAST): `getDiagnostics()` - Check errors before/after
2. **Cipher**: Query patterns, store discoveries - `ask_cipher("How did we implement X?")`
3. **Claude Context**: Search codebase - `search_code(path="/workspaces/...", query="patterns")`
4. **Ref/Context7**: API docs - `ref_search_documentation(query="...")`
5. **Database**: Schema/queries - `execute_sql("SELECT...")`
6. **FireCrawl** (if needed): External docs - Enable with `discover_tools_by_words`
7. **Playwright** (UI tests only): Browser automation - Enable when needed

## Standard Task Flow (EVERY Task)

1. **Diagnostics**: `getDiagnostics()`
2. **Knowledge**: Query Cipher for patterns
3. **Search**: Claude Context for similar code
4. **Research**: Ref/Context7 if needed
5. **Test**: Write failing test FIRST (MANDATORY)
6. **Implement**: Minimal code to pass
7. **Verify**: Diagnostics + run tests
8. **Execute**: Run actual code and verify output (MANDATORY)
9. **E2E** (APIs): Newman/Postman tests
10. **Store**: Save discoveries in Cipher

**CRITICAL - Execute Actual Code:** After tests pass, run the actual program/function to verify it works:
- ETL: `uv run python src/main.py` → Check logs/DB records
- API: `curl localhost:8000/endpoint` → Check response
- CLI: `uv run python src/cli.py --flag` → Check output
- Show actual output, don't claim "should work"

## API E2E Testing (Newman)

**For APIs:** Create Postman collection in `postman/collections/` with tests:
```json
{"info": {"name": "API Tests"},
 "item": [{
   "request": {"method": "POST", "url": "{{base_url}}/api/endpoint"},
   "event": [{"listen": "test", "script": {
     "exec": ["pm.test('Status 200', () => pm.response.to.have.status(200));"]
   }}]
 }]}
```
Run: `newman run postman/collections/feature.json -e postman/environments/dev.json`

## TDD Enforcement (NON-NEGOTIABLE)

**NO PRODUCTION CODE WITHOUT FAILING TEST FIRST**

**RED-GREEN-REFACTOR:** Write test → Verify fail → Minimal code → Verify pass → Refactor → Repeat

**Code before test = DELETE and restart with test**

## The Process

### Step 1: Load Plan and Assess Context

**FIRST:** Read plan file (from argument or ask for path)

**Determine session state:**
- Check git: `git status --short` and `git diff --name-only`
- If changes exist: Continuation - read files, query Cipher, search codebase
- Check plan file for `[x]` completed tasks - SKIP these, resume from first `[ ]` task
- If no changes: Fresh start from Task 1

**Prepare:**
1. Count total tasks
2. Review critically, raise concerns
3. Create TodoWrite (mark completed if continuation)
4. Run `getDiagnostics()` for clean state
5. Search codebase for relevant patterns

### Step 2: Execute Tasks Autonomously

**Execute ALL tasks continuously. NO stopping unless context > 75%.**

**Per task (CRITICAL - follow exactly):**
1. Mark task as `in_progress` in TodoWrite
2. Run `getDiagnostics()` to check for pre-existing errors
3. Execute Standard Task Flow (see above)
4. Write failing test FIRST (TDD mandatory - NO exceptions)
5. Implement minimal code to pass test
6. Run `getDiagnostics()` again to verify no errors
7. **Execute actual code** to verify functionality (MANDATORY - show output)
8. Mark task as `completed` in TodoWrite ONLY if tests pass AND code executes successfully
9. **UPDATE PLAN FILE:** Change `[ ]` to `[x]` for this task
10. Check context usage (see below)

**Context Check After EVERY Task (CRITICAL):**
```
IMPORTANT: System warnings only show MESSAGE tokens, NOT total context!
Total context = MESSAGE tokens + OVERHEAD (~35-40k for system + tools + memory)

To check ACTUAL context usage:
1. Look for LATEST <system_warning> containing "Token usage: X/200000"
2. Add 35k overhead: TOTAL = X + 35000
3. Calculate percentage: (TOTAL / 200000) * 100
4. Alternative: Ask user to run /context command for exact total

If ≥ 80% (160k total tokens):
  - Run `/remember` immediately to store learnings
  - STOP execution - NO new features above 80%
  - Tell user: "Context at 80% (Xk/200k). Running /remember to preserve learnings. Please run /clear then /implement <plan> to continue."
If < 80%: Continue to next task without asking
```

**Flow:** Task → Check → Continue (if <80%) | Remember+Stop (if ≥80%)

**Why 80% limit:** Above 80%, overhead and new tool calls can quickly consume remaining space, causing context overflow mid-task.

**Standards:** TDD | `uv` not pip | One-line docstrings | No inline comments | Imports at top | DRY/YAGNI | Check diagnostics | Edit > Create

**Active Skills:**

**Testing (EVERY task):** @testing-test-driven-development (MANDATORY), @testing-test-writing, @testing-anti-patterns, @testing-debugging, @testing-final-verification, @testing-code-reviewer

**Global (all code):** @global-coding-style, @global-commenting, @global-conventions, @global-error-handling, @global-validation

**Backend:** @backend-api, @backend-models, @backend-queries, @backend-migrations

**Frontend:** @frontend-accessibility, @frontend-components, @frontend-css, @frontend-responsive

### Step 3: Automatic Context Management

**After EVERY task:** Check context usage (MESSAGE tokens + 35k overhead)

**If ≥ 80% (160k total):** `/remember` → STOP → Tell user to `/clear` then continue
**If < 80%:** Continue immediately

**CRITICAL**: System warnings show MESSAGE tokens only. Add ~35k for system/tools/memory overhead to get TOTAL context usage.

**Preserved after /clear:** ✅ Plan, Code, Tests, Cipher, Codebase | ❌ Conversation
**On restart:** Read plan → Check git → Query Cipher → Resume from pending task

### Step 4: Complete Development

**When ALL tasks are `[x]` complete:**
1. Run quick verification: `getDiagnostics()` and `uv run pytest`
2. Store learnings: `ask_cipher("Store: Completed <feature>. Key learnings: <insights>")`
3. **INFORM USER:** "✅ All tasks complete. Run `/verify` for comprehensive verification"
4. DO NOT run /verify yourself - let user initiate

**Evidence required:** Test output, diagnostics clean

**NO completion claims without showing actual test output.**

## When to Stop

**STOP when:** Blocker hit | Plan has gaps | Instruction unclear | Verification fails repeatedly
**Ask, don't guess.**

## Git Operations - READ ONLY

✅ **Allowed:** `git status`, `git diff`, `git log`, `git show`, `git branch`
❌ **FORBIDDEN:** `git add`, `git commit`, `git push`, `git pull`, `git merge`, `git rebase`, `git checkout`, `git reset`, `git stash`

## Remember

- Review plan critically → Raise concerns
- Standard Task Flow → TDD always
- Check diagnostics before/after
- Work autonomously until 80% context
- Auto /remember at 80%
- Stop when blocked
- Evidence required for completion
