---
description: Spec-driven development - plan, implement, verify workflow
argument-hint: "<task description>" or "<path/to/plan.md>"
model: opus
---
# /spec - Unified Spec-Driven Development

**For new features, major changes, and complex work.** Creates a spec, gets your approval, implements with TDD, and verifies completion - all in one continuous flow.

---

## 📋 TABLE OF CONTENTS

| Section | What Happens |
|---------|--------------|
| [PHASE 0: WORKFLOW CONTROL](#phase-0-workflow-control) | Dispatcher, context handoff, rules summary |
| [PHASE 1: PLANNING](#phase-1-planning) (1.1–1.8) | Explore → Design → Write plan → Verify → Approve |
| [PHASE 2: IMPLEMENTATION](#phase-2-implementation) (2.1–2.4) | TDD loop for each task |
| [PHASE 3: VERIFICATION](#phase-3-verification) (3.1–3.11) | Tests → Execution → Rules → Code Review → E2E |

### Quick Step Reference

**Phase 0 (Workflow Control):**
- 0.1 Parse arguments, determine current state
- 0.2 Dispatch to appropriate phase
- 0.3 Context handoff (when >= 90%)
- 0.4 Rules reference (12 rules)

**Phase 1 (Planning):**
- 1.1 Create plan file header
- 1.2 Clarify requirements (Question Batch 1)
- 1.3 Explore codebase
- 1.4 Design decisions (Question Batch 2)
- 1.5 Write implementation tasks
- 1.6 Write full plan
- 1.7 Plan verification
- 1.8 Get user approval → PHASE 2

**Phase 2 (Implementation):**
- 2.1 Read plan, gather context
- 2.2 Per-task TDD loop (RED→GREEN→REFACTOR)
- 2.3 Update plan checkboxes after EACH task
- 2.4 All tasks done → set COMPLETE → PHASE 3

**Phase 3 (Verification):**
- 3.1 Unit tests
- 3.2 Integration tests
- 3.3 Execute actual program
- 3.4 Rules compliance audit
- 3.5 Call chain analysis
- 3.6 Coverage check
- 3.7 Quality checks
- 3.8 Code review verification
- 3.9 E2E tests
- 3.10 Final verification
- 3.11 Update plan status → VERIFIED or loop back

---

# PHASE 0: WORKFLOW CONTROL

This phase handles argument parsing, state dispatch, context management, and enforces workflow rules.

**⛔ KEY CONSTRAINTS (see 0.4 for full rules):**
- NO sub-agents during Phase 1/2 (except verification steps 1.7 and 3.8)
- NO stopping between phases - flow continuously
- NO built-in plan mode (EnterPlanMode/ExitPlanMode)
- Quality over speed - never rush

---

## 0.1 Parse Arguments

```
/spec <task-description>           # Start new workflow from task
/spec <path/to/plan.md>            # Continue existing plan
/spec --continue <path/to/plan.md> # Resume after session clear
```

Parse the arguments: $ARGUMENTS

### Determine Current State

```
IF arguments start with "--continue":
    plan_path = extract path after "--continue"
    1. Read /tmp/claude-continuation.md if it exists
    2. Delete the continuation file after reading
    3. Read plan file, check Status AND Approved fields
    → Jump to appropriate phase based on status

ELIF arguments end with ".md" AND file exists:
    plan_path = arguments
    → Read plan file, check Status AND Approved fields
    → Jump to appropriate phase based on status

ELSE:
    task_description = arguments
    → Go to PHASE 1: PLANNING
```

## 0.2 Status-Based Dispatch

| Status | Approved | Action |
|--------|----------|--------|
| PENDING | No | PHASE 1: Get user approval |
| PENDING | Yes | PHASE 2: IMPLEMENTATION |
| COMPLETE | * | PHASE 3: VERIFICATION |
| VERIFIED | * | Report completion, workflow done |

### The Feedback Loop

```
LOOP until VERIFIED or context >= 90%:
  1. Read plan file status
  2. Execute appropriate phase (table above)
  3. After phase completes, go back to step 1
  4. EXIT only when: Status == VERIFIED OR context >= 90%
```

**Report iteration progress:**
```
🔄 Starting Iteration 1 implementation...  (after first verify failure)
✅ Iteration 1: All checks passed - VERIFIED
```

---

## 0.3 Context Management (90% Handoff)

After each major operation, check context:

```bash
~/.pilot/bin/pilot check-context --json
```

**Between iterations:**
1. If context >= 90%: hand off cleanly (don't rush!)
2. If context 80-89%: continue but wrap up current task with quality
3. If context < 80%: continue the loop freely

If response shows `"status": "CLEAR_NEEDED"` (context >= 90%):

**⚠️ CRITICAL: Execute ALL steps below in a SINGLE turn. DO NOT stop or wait for user response between steps.**

**Step 1: Write continuation file (GUARANTEED BACKUP)**

Write to `/tmp/claude-continuation.md`:

```markdown
# Session Continuation (/spec)

**Plan:** <plan-path>
**Phase:** [planning|implementation|verification]
**Current Task:** Task N - [description]

**Completed This Session:**
- [x] [What was finished]

**Next Steps:**
1. [What to do immediately when resuming]

**Context:**
- [Key decisions or blockers]
```

**Step 2: Trigger session clear**

```bash
~/.pilot/bin/pilot send-clear <plan-path>
```

Pilot will restart with `/spec --continue <plan-path>`

### Error Handling

**No Active Session:** If `send-clear` fails, tell user: "Context at X%. Please run `/clear` manually, then `/spec --continue <plan-path>`"

**Plan File Not Found:** Tell user: "Plan file not found: <path>" and ask if they want to create a new plan.

---

## 0.4 Rules Summary (Quick Reference)

| # | Rule |
|---|------|
| 1 | **NO sub-agents during planning/implementation** - Phase 1 and 2 use direct tools only. Verification steps (Step 1.7, Step 3.8) each use a single verifier sub-agent. |
| 2 | **NEVER SKIP verification** - Plan verification (Step 1.7) and Code verification (Step 3.8) are mandatory. No exceptions. |
| 3 | **ONLY stopping point is plan approval** - Everything else is automatic. Never ask "Should I fix these?" |
| 4 | **Batch questions together** - Don't interrupt user flow |
| 5 | **Run explorations sequentially** - One at a time, never in parallel |
| 6 | **NEVER write code during planning** - Separate phases |
| 7 | **NEVER assume - verify by reading files** |
| 8 | **Re-read plan after user edits** - Before asking for approval again |
| 9 | **TDD is MANDATORY** - No production code without failing test first |
| 10 | **Update plan checkboxes after EACH task** - Not at the end |
| 11 | **Quality over speed** - Never rush due to context pressure |
| 12 | **Plan file is source of truth** - Survives session clears |

---

# PHASE 1: PLANNING

> **WARNING: DO NOT use the built-in `ExitPlanMode` or `EnterPlanMode` tools.**

## Using AskUserQuestion - Core Planning Tool

**Questions are grouped into batches for smooth user experience:**

| Batch | When | Purpose |
|-------|------|---------|
| **Batch 1** | Phase 0 (before exploration) | Clarify task, scope, priorities |
| **Batch 2** | Phase 2 (after exploration) | Architecture choices, design decisions |

**When to Use AskUserQuestion:**

| Situation | Example Question |
|-----------|------------------|
| **Unclear requirements** | "Should this feature support batch processing or single items only?" |
| **Multiple valid approaches** | Present 2-3 options with trade-offs for user to choose |
| **Ambiguous scope** | "Should we include error recovery, or fail fast?" |
| **Technology choices** | "Prefer async/await or callbacks for this integration?" |
| **Priority decisions** | "Performance or simplicity - which matters more here?" |
| **Missing domain knowledge** | "How does the existing auth flow work in production?" |

**Key principles:**
- Present options, not open-ended questions when possible
- Include trade-offs for each option
- **Batch related questions together** - don't interrupt user flow
- Don't proceed with assumptions - ASK

## Extending Existing Plans

**When adding tasks to existing plan:**

1. Load existing plan: `Read(file_path="docs/plans/...")`
2. Parse structure (architecture, completed tasks, pending tasks)
3. Check git status for partially completed work
4. Verify new tasks are compatible with existing architecture
5. Check total: If original + new > 12 tasks, suggest splitting
6. Mark new tasks with `[NEW]` prefix
7. Update total count: `Total Tasks: X (Originally: Y)`
8. Add extension history: `> Extended [Date]: Tasks X-Y for [feature]`

## ⚠️ CRITICAL: Migration/Refactoring Tasks

**When the task involves migrating, refactoring, or replacing existing code, you MUST complete these additional steps to prevent missing features.**

### Mandatory Feature Inventory (Phase 1.5)

**After exploration but BEFORE creating tasks:**

1. **List ALL files being replaced:**
   ```markdown
   ## Feature Inventory - Files Being Replaced

   | Old File | Functions/Classes | Status |
   |----------|-------------------|--------|
   | `old/module1.py` | `func_a()`, `func_b()`, `ClassX` | ⬜ Not mapped |
   | `old/module2.py` | `func_c()`, `func_d()` | ⬜ Not mapped |
   ```

2. **Map EVERY function/feature to a new task:**
   ```markdown
   ## Feature Mapping - Old → New

   | Old Feature | New Location | Task # |
   |-------------|--------------|--------|
   | `module1.func_a()` | `new/step1.py` | Task 3 |
   | `module1.func_b()` | `new/step1.py` | Task 3 |
   | `module2.func_c()` | `new/step2.py` | Task 5 |
   | `module2.func_d()` | ❌ MISSING | ⚠️ NEEDS TASK |
   ```

3. **Verify 100% coverage before proceeding:**
   - Every row must have a Task # or explicit "Out of Scope" justification
   - "Out of Scope" means the feature is INTENTIONALLY REMOVED (with user confirmation)
   - "Out of Scope" does NOT mean "migrate as-is" - that still needs a task!

### "Out of Scope" Clarification

**CRITICAL: "Out of Scope" has a precise meaning:**

| Phrase | Meaning | Requires Task? |
|--------|---------|----------------|
| "Out of Scope: Changes to X" | X will be migrated AS-IS, no modifications | ✅ YES - migration task |
| "Out of Scope: Feature X" | X is intentionally REMOVED/not included | ❌ NO - but needs user confirmation |
| "Out of Scope: New features for X" | X migrates as-is, no NEW features added | ✅ YES - migration task |

### Pre-Task Verification Gate

**Before finalizing tasks, verify:**

- [ ] All old files listed in Feature Inventory
- [ ] All functions/classes from old files identified
- [ ] Every feature mapped to a task OR explicitly marked "REMOVED" with user confirmation
- [ ] No row in Feature Mapping has "⬜ Not mapped" status
- [ ] User has confirmed any features marked for removal

**If any checkbox is unchecked, DO NOT proceed to implementation.**

---

## Creating New Plans

### Step 1.1: Create Plan File Header (FIRST)

**Immediately upon starting planning, create the plan file header for status bar detection.**

1. **Generate filename:** `docs/plans/YYYY-MM-DD-<feature-slug>.md`
   - Use current date
   - Create slug from first 3-4 words of task description (lowercase, hyphens)
   - Example: "add user authentication" → `2026-01-24-add-user-authentication.md`

2. **Create directory if needed:** `mkdir -p docs/plans`

3. **Write initial header immediately:**
   ```markdown
   # [Feature Name] Implementation Plan

   Created: [Date]
   Status: PENDING
   Approved: No
   Iterations: 0

   > Planning in progress...

   ## Summary
   **Goal:** [Task description from user]

   ---
   *Exploring codebase and gathering requirements...*
   ```

4. **Why this matters:**
   - Status bar shows "Spec: <name> [/plan]" immediately
   - User sees progress even during exploration phase
   - Plan file exists for continuation if session clears

**CRITICAL:** Do this FIRST, before any exploration or questions.

---

### Step 1.2: Task Understanding & Clarification

**First, clearly state your understanding of the task.**

Before any exploration:
1. Restate what the user is asking for in your own words
2. Identify the core problem being solved
3. List any assumptions you're making

**Then gather all clarifications needed (Question Batch 1):**

Use AskUserQuestion to ask everything upfront in a single interaction.

**Don't proceed to exploration until clarifications are complete.**

### Step 1.3: Exploration

**Explore the codebase systematically.** Run explorations **one at a time** (sequentially, not in parallel).

#### 🔧 Tools for Exploration

| Tool | When to Use | Example |
|------|-------------|---------|
| **Context7** | Library/framework docs | `resolve-library-id(query="your question", libraryName="lib")` then `query-docs(libraryId, query)` |
| **Vexor** | Semantic code search | `vexor search "query" --mode code` |
| **grep-mcp** | Real-world GitHub examples | `searchGitHub(query="FastMCP", language=["Python"])` |
| **Read/Grep/Glob** | Direct file exploration | Use directly, no sub-agents |

**Exploration areas (in order):**

1. **Architecture** - Project structure, entry points, how components connect
2. **Similar Features** - Existing patterns that relate to the task, what can be reused
3. **Dependencies** - Imports, modules, what will be impacted
4. **Tests** - Test infrastructure, existing patterns, available fixtures

**For each area:**
- Document hypotheses (not conclusions)
- Note full file paths for relevant code
- Track questions that remain unanswered

**After explorations complete:**
1. Read each identified file to verify hypotheses
2. Build a complete mental model of current architecture
3. Identify integration points and potential risks
4. Note reusable patterns

### Step 1.4: Design Decisions

**Present findings and gather all design decisions (Question Batch 2).**

Summarize what you found, then use AskUserQuestion with all decisions at once.

**After user answers:**
- Summarize the chosen design approach
- Confirm: "Does this design work for your needs?"
- Don't proceed until design is validated

### Step 1.5: Implementation Planning

**Task Count Guidance**
- Avoid bloating plans with unnecessary or overly granular tasks
- If the work genuinely requires more tasks, that's fine - the workflow handles multi-session execution
- Focus on keeping tasks meaningful and necessary

**Task Structure:**
```markdown
### Task N: [Component Name]

**Objective:** [1-2 sentences describing what to build]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py`
- Test: `tests/exact/path/to/test.py`

**Implementation Steps:**
1. Write failing test - Define expected behavior
2. Implement minimal code - Make test pass
3. Verify execution - Run actual program
4. Integration test - Test with other components

**Definition of Done:**
- [ ] All tests pass (unit, integration if applicable)
- [ ] No diagnostics errors (linting, type checking)
- [ ] Code functions correctly with real data
- [ ] Edge cases handled appropriately
- [ ] Error messages are clear and actionable
```

**Zero-context assumption:**
- Assume implementer knows nothing about codebase
- Provide exact file paths
- Explain domain concepts
- List integration points
- Reference similar patterns in codebase

### Step 1.6: Write Full Plan

**Save plan to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

**Required plan template:**

```markdown
# [Feature Name] Implementation Plan

Created: [Date]
Status: PENDING
Approved: No
Iterations: 0

> **Status Lifecycle:** PENDING → COMPLETE → VERIFIED
> **Iterations:** Tracks implement→verify cycles (incremented by verify phase)
> - PENDING: Initial state, awaiting implementation
> - COMPLETE: All tasks implemented
> - VERIFIED: All checks passed
>
> **Approval Gate:** Implementation CANNOT proceed until `Approved: Yes`

## Summary
**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about chosen approach]

**Tech Stack:** [Key technologies/libraries]

## Scope

### In Scope
- [What WILL be changed/built]
- [Specific components affected]

### Out of Scope
- [What will NOT be changed]
- [Explicit boundaries]

## Prerequisites
- [Any requirements before starting]
- [Dependencies that must exist]
- [Environment setup needed]

## Context for Implementer
- [Key codebase convention or pattern]
- [Domain knowledge needed]
- [Integration points or dependencies]

## Feature Inventory (FOR MIGRATION/REFACTORING ONLY)

> **Include this section when replacing existing code. Delete if not applicable.**

### Files Being Replaced

| Old File | Functions/Classes | Mapped to Task |
|----------|-------------------|----------------|
| `old/file1.py` | `func_a()`, `func_b()` | Task 3 |
| `old/file2.py` | `ClassX`, `func_c()` | Task 4, Task 5 |

### Feature Mapping Verification

- [ ] All old files listed above
- [ ] All functions/classes identified
- [ ] Every feature has a task number
- [ ] No features accidentally omitted

**⚠️ If any feature shows "❌ MISSING", add a task before implementation!**

## Progress Tracking

**MANDATORY: Update this checklist as tasks complete. Change `[ ]` to `[x]`.**

- [ ] Task 1: [Brief summary]
- [ ] Task 2: [Brief summary]
- [ ] ...

**Total Tasks:** [Number] | **Completed:** 0 | **Remaining:** [Number]

## Implementation Tasks

### Task 1: [Component Name]
[Full task structure]

### Task 2: [Component Name]
[Full task structure]

## Testing Strategy
- Unit tests: [What to test in isolation]
- Integration tests: [What to test together]
- Manual verification: [Steps to verify manually]

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [How to mitigate] |

## Open Questions
- [Any remaining questions for the user]
- [Decisions deferred to implementation]
```

### Step 1.7: Plan Verification

**⛔ THIS STEP IS NON-NEGOTIABLE. You MUST run plan verification before asking for approval.**

Before presenting the plan to the user, verify it with a dedicated verifier agent. This catches missing requirements, scope issues, and misalignments BEFORE the user sees the plan.

#### Launch Plan Verification

Spawn 1 `plan-verifier` agent using the Task tool:

```
Task(
  subagent_type="pilot:plan-verifier",
  prompt="""
  **Plan file:** <plan-path>
  **User request:** <original task description from user>
  **Clarifications:** <any Q&A that clarified requirements>

  Verify this plan correctly captures the user's requirements.
  Check for missing features, scope issues, and ambiguities.
  """
)
```

The verifier:
- Reviews plan against original user request
- Checks if clarification answers are incorporated
- Identifies missing requirements or scope issues
- Returns structured JSON findings

#### Fix All Findings

After verification completes, fix all issues by severity:

| Severity | Action |
|----------|--------|
| **must_fix** | Fix immediately - update plan before proceeding |
| **should_fix** | Fix immediately - update plan before proceeding |
| **suggestion** | Incorporate if reasonable, or note in Open Questions |

**Only proceed to Step 1.8 after all must_fix and should_fix issues are resolved.**

### Step 1.8: Get User Approval

**⛔ MANDATORY APPROVAL GATE - This is NON-NEGOTIABLE**

**After saving plan:**

1. **Summarize the plan** - Provide a brief overview of:
   - What will be built (goal)
   - Key tasks (numbered list)
   - Tech stack / approach

2. **Use AskUserQuestion to request approval:**
   ```
   Question: "Do you approve this plan for implementation?"
   Header: "Plan Review"
   Options:
   - "Yes, proceed with implementation" - I've reviewed the plan and it looks good
   - "No, I need to make changes" - I want to edit the plan first
   ```

3. **Based on user response:**

   **If user selects "Yes, proceed with implementation":**
   - Edit the plan file to change `Approved: No` to `Approved: Yes`
   - **Continue immediately to PHASE 2: IMPLEMENTATION**

   **If user selects "No, I need to make changes":**
   - Tell user: "Please edit the plan file at `<plan-path>`, then say 'ready' when done"
   - Wait for user to confirm they're done editing
   - Re-read the plan file to see their changes
   - Ask for approval again using AskUserQuestion

   **If user provides OTHER feedback (corrections, config values, clarifications):**
   - This is NOT approval - they're giving you changes to incorporate
   - Update the plan with their feedback
   - Ask for approval AGAIN with a fresh AskUserQuestion

4. **DO NOT proceed to implementation until user explicitly selects "Yes, proceed"**

**⚠️ CRITICAL: Any response other than selecting "Yes, proceed with implementation" is NOT approval. Config feedback, threshold changes, clarifications = update plan, then re-ask.**

**⚠️ CRITICAL: Claude handles the `Approved:` field update - user never edits it manually**

---

# PHASE 2: IMPLEMENTATION

## Quality Over Speed - CRITICAL

**NEVER rush or compromise quality due to context pressure.**

- Context warnings are informational, not emergencies
- Work spans sessions seamlessly via plan file and continuation mechanisms
- Finish the CURRENT task with full quality, then hand off cleanly
- Do NOT skip tests, compress code, or cut corners to "beat" context limits
- **Quality is the #1 metric** - a well-done task split across sessions beats rushed work

## Feedback Loop Awareness

**This phase may be called multiple times in a feedback loop:**

```
PHASE 2 → PHASE 3 → issues found → PHASE 2 → PHASE 3 → ... → VERIFIED
```

**When called after verification found issues:**
1. Read the plan - verification will have added fix tasks (marked with `[MISSING]` or similar)
2. Check the `Iterations` field in the plan header
3. **Report iteration start:** "🔄 Starting Iteration N implementation..."
4. Focus on uncompleted tasks `[ ]` - these are the fixes needed
5. Complete all fix tasks, then set status to COMPLETE as normal

---

### Step 2.1: Read Plan & Gather Context

**Before ANY implementation, you MUST:**

1. **Read the COMPLETE plan** - Understanding overall architecture and design
2. **Verify comprehension** - Summarize what you learned to demonstrate understanding
3. **Identify dependencies** - List files, functions, classes that need modification
4. **Check current state:**
   - Git status: `git status --short` and `git diff --name-only`
   - Plan progress: Check for `[x]` completed tasks

#### 🔧 Tools for Implementation

| Tool | When to Use | Example |
|------|-------------|---------|
| **Context7** | Library API lookup | `resolve-library-id(query="how to use fixtures", libraryName="pytest")` then `query-docs(libraryId, query)` |
| **Vexor** | Find similar patterns | `vexor search "query" --mode code` |
| **grep-mcp** | Production code examples | `searchGitHub(query="useEffect cleanup", language=["TypeScript"])` |

---

### Step 2.2: Per-Task TDD Loop

**TDD is MANDATORY. No production code without a failing test first.**

| Requires TDD | Skip TDD |
|--------------|----------|
| New functions/methods | Documentation changes |
| API endpoints | Config file updates |
| Business logic | IaC code (CDK, Terraform, Pulumi) |
| Bug fixes | Formatting/style changes |

**For EVERY task, follow this exact sequence:**

1. **READ PLAN'S IMPLEMENTATION STEPS** - List all files to create/modify/delete
2. **Perform Call Chain Analysis:**
   - **Trace Upwards (Callers):** Identify what calls the code you're modifying
   - **Trace Downwards (Callees):** Identify what the modified code calls
   - **Side Effects:** Check for database, cache, external system impacts
3. **Mark task as in_progress** in TodoWrite
4. **Execute TDD Flow (RED → GREEN → REFACTOR):**
   - Write failing test first, **verify it fails**
   - Implement minimal code to pass
   - Refactor if needed (keep tests green)
5. **Verify tests pass** - `uv run pytest tests/path/to/test.py -q`
6. **Run actual program** - Show real output with sample data
7. **Check diagnostics** - Must be zero errors
8. **Validate Definition of Done** - Check all criteria from plan
9. **Mark task completed** in TodoWrite
10. **UPDATE PLAN FILE IMMEDIATELY** (see Step 2.3)
11. **Check context usage** - Run `~/.pilot/bin/pilot check-context --json`

**⚠️ NEVER SKIP TASKS:**
- EVERY task MUST be fully implemented
- NO exceptions for "MVP scope" or complexity
- If blocked: STOP and report specific blockers
- NEVER mark complete without doing the work

---

### Step 2.3: Update Plan After EACH Task

**⛔ CRITICAL: Task Completion Tracking is MANDATORY**

**After completing EACH task, you MUST:**

1. **IMMEDIATELY edit the plan file** to change `[ ]` to `[x]` for that task
2. **Update the Progress Tracking counts** (Completed/Remaining)
3. **DO NOT proceed to next task** until the checkbox is updated

**This is NON-NEGOTIABLE.**

**Example - After completing Task 5:**
```
Edit the plan file:
- [ ] Task 5: Implement X  →  - [x] Task 5: Implement X
Update counts:
**Completed:** 4 | **Remaining:** 8  →  **Completed:** 5 | **Remaining:** 7
```

---

### Step 2.4: All Tasks Complete → PHASE 3

**⚠️ CRITICAL: Follow these steps exactly:**

1. Quick verification: Check diagnostics and run `uv run pytest -q`
2. **FOR MIGRATIONS ONLY - Feature Parity Check:**
   - Run the NEW code and verify it produces expected output
   - Compare behavior with OLD code (if still available)
   - Check Feature Inventory - every feature should now be implemented
   - If ANY feature is missing: **DO NOT mark complete** - add tasks for missing features
3. **MANDATORY: Update plan status to COMPLETE**
   ```
   Edit the plan file and change the Status line:
   Status: PENDING  →  Status: COMPLETE
   ```
4. **Continue immediately to PHASE 3: VERIFICATION**

---

## ⚠️ Migration/Refactoring Tasks (Phase 2 Additions)

**When the plan involves replacing existing code, perform these ADDITIONAL checks:**

### Before Starting Implementation

1. **Locate the Feature Inventory section** in the plan
2. **If Feature Inventory is MISSING** - STOP and inform user
3. **Verify ALL features are mapped** - Every row must have a Task #
4. **Read the OLD code completely** - Don't rely on the plan alone

### During Implementation

For EACH task that migrates old functionality:

1. **Read the corresponding old file(s)** listed in Feature Inventory
2. **Create a checklist** of functions/behaviors from old code
3. **Verify each function/behavior exists** in new code after implementation
4. **Test with same inputs** - Old and new code should produce same outputs

### Before Marking Task Complete

**For migration tasks, add this to Definition of Done:**

- [ ] All functions from old code have equivalents in new code
- [ ] Behavior matches old code (same inputs → same outputs)
- [ ] No features accidentally omitted

### Red Flags - STOP Implementation

If you notice ANY of these, STOP and report to user:

- Feature Inventory section missing from plan
- Old file has functions not mentioned in any task
- "Out of Scope" items that should actually be migrated
- Tests pass but functionality is missing compared to old code

---

# PHASE 3: VERIFICATION

## The Process

**Unit tests → Integration tests → Program execution (with log inspection) → Rules audit → Coverage → Quality → Code review → E2E tests → Final verification**

**All test levels are MANDATORY:** Unit tests alone are insufficient. You must run integration tests AND E2E tests AND execute the actual program with real data.

### Step 3.1: Run & Fix Unit Tests

Run unit tests and fix any failures immediately.

**If failures:** Identify → Read test → Fix implementation → Re-run → Continue until all pass

### Step 3.2: Run & Fix Integration Tests

Run integration tests and fix any failures immediately.

**Common issues:** Database connections, mock configuration, missing test data

### Step 3.3: Build and Execute the Actual Program (MANDATORY)

**⚠️ CRITICAL: Tests passing ≠ Program works**

Run the actual program and verify real output.

**Execution checklist:**
- [ ] Build/compile succeeds without warnings
- [ ] Program starts without errors
- [ ] **Inspect logs** - Check for errors, warnings, stack traces
- [ ] **Verify output correctness** - Fetch source data independently, compare against program output
- [ ] Test with real/sample data, not just mocks

**⛔ Output Correctness - MANDATORY:**
If code processes external data, ALWAYS verify by fetching source data and comparing:
```bash
# Fetch actual source data
aws <service> get-<resource> --output json

# Compare counts/content with what your code logged
# If mismatch → BUG (don't trust logs alone)
```

**If bugs are found:**

| Bug Type | Action |
|----------|--------|
| **Minor** (typo, off-by-one, missing import) | Fix immediately, re-run, continue verification |
| **Major** (logic error, missing function, architectural issue) | Add task to plan, set PENDING, loop back to PHASE 2 |

**Rule of thumb:** If you can fix it in < 5 minutes without writing new tests, fix inline. Otherwise, add a task.

### Step 3.3a: Feature Parity Check (if applicable)

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

4. **Go back to PHASE 2** - Continue the loop

### Step 3.4: Rules Compliance Audit

**⚠️ MANDATORY: Actually READ every rule file and verify compliance. Don't skip this.**

This step exists because we often forget our own rules. By re-reading each rule file and explicitly checking compliance, we catch mistakes before they ship.

#### Process

**Step 3.4a: Discover and read ALL rules (BOTH standard AND custom)**

**⛔ CRITICAL: You MUST check BOTH directories. Checking only custom rules is NOT sufficient.**

```bash
# List ALL rule files - BOTH directories are MANDATORY
ls -la ~/.claude/rules/*.md    # Standard rules (global) - REQUIRED
ls -la .claude/rules/*.md      # Custom rules (project) - REQUIRED
```

Then use `Read` tool to read EACH file completely from BOTH directories:

| Directory | What It Contains | Required? |
|-----------|------------------|-----------|
| `~/.claude/rules/*.md` | Core development standards (TDD, testing, execution, Python/TS/Go rules, etc.) | **YES - MANDATORY** |
| `.claude/rules/*.md` | Project-specific rules (git commits, project conventions) | **YES - MANDATORY** |

**DO NOT skip standard rules. They contain critical requirements like TDD enforcement, execution verification, and testing standards.**

**Step 3.4b: For EACH rule file, create a compliance checklist**

After reading each rule file, extract the key requirements and check each one:

```markdown
## Rules Compliance Report

### [rule-filename.md]
- [ ] Requirement 1: [description] → ✅ Compliant / ❌ Violation
- [ ] Requirement 2: [description] → ✅ Compliant / ❌ Violation
...

### [next-rule-filename.md]
...
```

#### Common Rules to Check (examples)

| Rule File | Key Requirements to Verify |
|-----------|---------------------------|
| `execution-verification.md` | Did you RUN the actual program (not just tests)? Show output. |
| `tdd-enforcement.md` | Did each test FAIL before you wrote the code? |
| `verification-before-completion.md` | Did you show actual command output as evidence? |
| `testing-strategies-coverage.md` | Is coverage ≥ 80%? Did you mock external calls in unit tests? |
| `python-rules.md` | Did you use `uv` (not pip)? Did you run `ruff` and `basedpyright`? |
| `typescript-rules.md` | Did you detect the package manager? Run `tsc --noEmit`? |
| `git-commits.md` | Using `fix:` prefix? No AI attribution footers? |

**Step 3.4c: Fix ALL violations immediately**

For each violation found:

1. **Fixable Now** (missing command, missing test, formatting):
   - Execute the fix immediately
   - Show the fix output
   - Re-verify the requirement passes

2. **Structural** (missed TDD cycle, wrong architecture):
   - Document the violation
   - If critical, add fix task to plan and loop back

**Step 3.4d: Output brief compliance report**

```
## Rules Compliance Audit
- Standard rules (~/.claude/rules/): [N] checked ✅
- Custom rules (.claude/rules/): [N] checked ✅
- Violations found: [N] | Fixed: [N]
```

**⛔ DO NOT proceed until BOTH directories are checked and all fixable violations are fixed.**

### Step 3.5: Call Chain Analysis

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

### Step 3.6: Check Coverage

Verify test coverage meets requirements.

**If insufficient:** Identify uncovered lines → Write tests for critical paths → Verify improvement

### Step 3.7: Run Quality Checks

Run automated quality tools and fix any issues found.

### Step 3.8: Code Review Verification

**⛔ THIS STEP IS NON-NEGOTIABLE. You MUST run code verification.**

**⚠️ SKIPPING THIS STEP IS FORBIDDEN.** Even if:
- You're confident the code is correct
- Context is getting high (do handoff AFTER verification, not instead of it)
- Tests pass (tests don't catch everything)
- The implementation seems simple

**None of these are valid reasons to skip. ALWAYS VERIFY.**

#### 3.8a: Identify Changed Files

Get list of files changed in this implementation:
```bash
git status --short  # Shows staged and unstaged changes
```

#### 3.8b: Launch Code Verification

Spawn 1 `spec-verifier` agent using the Task tool:

```
Task(
  subagent_type="pilot:spec-verifier",
  prompt="""
  **Plan file:** <plan-path>
  **Changed files:** [file list from git status]

  Review the implementation against the plan. Read the plan file first to understand
  the requirements, then verify the changed files implement them correctly.
  You may read related files for context as needed.
  """
)
```

The verifier:
- Receives the plan file path as source of truth
- Reviews changed files against plan requirements
- Can read related files for context (imports, dependencies, etc.)
- Runs with fresh context (no anchoring bias)
- Returns structured JSON findings

#### 3.8c: Report Findings

Present findings briefly:

```
## Code Verification Complete

**Issues Found:** X

### Must Fix (N) | Should Fix (N) | Suggestions (N)

Implementing fixes automatically...
```

#### 3.8d: Automatically Implement ALL Findings

**⛔ DO NOT ask user for permission. Fix everything automatically.**

This is part of the automated /spec workflow. The user approved the plan - verification fixes are part of that approval. Never stop to ask "Should I fix these?" or "Want me to address these findings?"

**Implementation order (by severity):**

1. **must_fix issues** - Fix immediately (security, crashes, TDD violations)
2. **should_fix issues** - Fix immediately (spec deviations, missing tests, error handling)
3. **suggestions** - Implement if reasonable and quick (< 5 min each)

**For each fix:**
1. Implement the fix
2. Run relevant tests to verify
3. Log: "✅ Fixed: [issue title]"

**After all fixes:**
1. Re-run verification (spawn new verifier) to catch any regressions
2. Repeat until no must_fix or should_fix issues remain (max 3 iterations)
3. If iterations exhausted with remaining issues, add them to plan and loop back to Phase 2

**The only stopping point in /spec is plan approval. Everything else is automatic.**

### Step 3.9: E2E Verification (MANDATORY for apps with UI/API)

**⚠️ Unit + Integration tests are NOT enough. You MUST also run E2E tests.**

Run end-to-end tests to verify the complete user workflow works.

#### For APIs
Test endpoints with curl. Verify status codes, response content, and error handling.

#### For Frontend/UI
Use `agent-browser` to verify UI renders and workflows complete. See `~/.claude/rules/agent-browser.md`.

### Step 3.10: Final Verification

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

### Step 3.11: Update Plan Status

**Status Lifecycle:** `PENDING` → `COMPLETE` → `VERIFIED`

**When ALL verification passes (no missing features, no bugs, rules compliant):**

1. **MANDATORY: Update plan status to VERIFIED**
   ```
   Edit the plan file and change the Status line:
   Status: COMPLETE  →  Status: VERIFIED
   ```
2. Read the Iterations count from the plan file
3. Report completion:
   ```
   ✅ Workflow complete! Plan status: VERIFIED

   Summary:
   - [Brief summary of what was implemented]
   - [Key files created/modified]
   - [Test results]

   Is there anything else you'd like me to help with?
   ```

**When verification FAILS (missing features, serious bugs, or unfixed rule violations):**

1. Add new tasks to the plan for missing features/bugs
2. **Set status back to PENDING and increment Iterations:**
   ```
   Edit the plan file:
   Status: COMPLETE  →  Status: PENDING
   Iterations: N     →  Iterations: N+1
   ```
3. Inform user: "🔄 Iteration N+1: Issues found, fixing and re-verifying..."
4. **Go back to PHASE 2** - Continue the loop

ARGUMENTS: $ARGUMENTS
