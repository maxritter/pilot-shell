---
description: Use when creating or planning anything - starts with discovery and clarification like design phase, then creates comprehensive implementation plan with exact file paths, complete code examples, and verification steps
model: opus
---

# Creating Comprehensive Implementation Plans

## Overview

Transform ideas into fully-formed implementation plans through structured discovery, questioning, and detailed task breakdown. This combines design exploration with concrete implementation planning.

**Core principle:** Understand deeply, explore alternatives, plan comprehensively with zero-context assumptions.

**Workflow Position:** Step 1 of 3 in spec-driven development
- **This command (/plan):** Idea → Design → Implementation Plan
- **Next command (/implement):** Implementation Plan → Working Code
- **Final command (/verify):** Working Code → Verified Implementation

**Output location:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Usage Modes

### Mode 1: Create New Plan (Default)
Use when starting fresh with a new feature or implementation.

### Mode 2: Extend Existing Plan
Use when adding tasks to an existing plan. User can provide:
- Path to existing plan: `/plan docs/plans/2024-11-04-auth-system.md`
- Or explicit instruction: "Add task to existing plan for user profile feature"

**When extending a plan:**
1. Load and parse the existing plan
2. Identify completed vs pending tasks
3. Add new tasks while preserving structure
4. Update total task count and progress tracking
5. Maintain original architecture decisions

## MCP Tools and Skills Available

### MCP Servers for Discovery & Planning

**Use these MCP servers during planning:**

1. **Cipher (START HERE)** - Query for past implementations, similar patterns, lessons learned
   ```
   ask_cipher("Have we implemented something similar to <feature>? What patterns worked?")
   ask_cipher("Store this implementation plan for <feature>")
   ```

2. **Claude Context** - Search codebase for existing patterns and exact file paths
   ```
   search_code(path="/workspaces/...", query="authentication patterns")
   ```

3. **Ref/Context7** - Research documentation for design decisions and API details
   ```
   ref_search_documentation(query="pytest fixtures documentation")
   resolve-library-id(libraryName="react")
   get-library-docs(context7CompatibleLibraryID="/facebook/react", topic="hooks")
   ```

4. **Database (if planning DB changes)** - Check current schema
   ```
   execute_sql("SELECT column_name FROM information_schema.columns WHERE table_name='users'")
   ```

5. **FireCrawl (optional)** - External research for best practices
   ```
   discover_tools_by_words(words="firecrawl", enable=true)
   ```

**NOT needed during planning:** IDE diagnostics (no code yet), Playwright (UI testing comes during implementation)

### Available Skills for Implementation

These skills will be automatically activated during `/implement` when referenced in your plan:

#### Testing Skills (Use in Implementation Tasks)
- **@testing-test-driven-development** - MANDATORY for all code tasks (enforces RED-GREEN-REFACTOR cycle)
- **@testing-test-writing** - For creating test files and test case structure
- **@testing-anti-patterns** - When using mocks, test doubles, or complex test setup
- **@testing-debugging** - For systematic debugging and troubleshooting
- **@testing-final-verification** - For final verification before marking complete
- **@testing-code-reviewer** - After completing significant features

#### Global Skills (Apply to All Code)
- **@global-coding-style** - Clean code, naming conventions, DRY principles
- **@global-commenting** - Minimal, self-documenting code approach
- **@global-conventions** - Project structure, dependency management
- **@global-error-handling** - Error handling, try-catch, exceptions
- **@global-validation** - Input validation, data sanitization

#### Backend Skills (Server-Side Tasks)
- **@backend-api** - REST/GraphQL endpoints, route handlers
- **@backend-models** - Database models, ORMs, entity definitions
- **@backend-queries** - Database queries, repository patterns
- **@backend-migrations** - Database schema changes, migration files

#### Frontend Skills (Client-Side Tasks)
**@frontend-components** - UI components (React/Vue/Svelte)
**@frontend-css** - Styling, CSS/SCSS/Tailwind
**@frontend-accessibility** - ARIA attributes, keyboard navigation
**@frontend-responsive** - Responsive layouts, mobile-first design

## The Process

**New Plan Checklist:**
```
- [ ] Phase 0: Research (Cipher, codebase, documentation)
- [ ] Phase 1: Understanding (purpose, constraints, criteria)
- [ ] Phase 2: Exploration (2-3 approaches proposed)
- [ ] Phase 3: Design Validation (confirmed in sections)
- [ ] Phase 4: Implementation Planning (detailed tasks)
- [ ] Phase 5: Documentation (save to docs/plans/)
- [ ] Phase 6: Implementation Handoff
```

**Extending Plan Checklist:**
```
- [ ] Phase 0: Load and analyze existing plan
- [ ] Phase 1: Review completed vs pending tasks
- [ ] Phase 2: Research new requirements
- [ ] Phase 3: Understand new feature scope
- [ ] Phase 4: Design integration with existing
- [ ] Phase 5: Create new tasks maintaining consistency
- [ ] Phase 6: Update plan with new tasks/counts
- [ ] Phase 7: Save updated plan
```

### Phase 0: Research and Discovery

**Always start with:**
1. Query Cipher: `ask_cipher("What do we know about <feature>? Past implementations?")`
2. Search codebase: `search_code(path="/workspaces/...", query="related features")`
3. Check CLAUDE.md for project conventions
4. Query relevant MCP servers for external systems

**Additional for extending plans:**
1. Load existing plan: `Read(file_path="docs/plans/YYYY-MM-DD-<feature>.md")`
2. Parse structure (architecture, progress tracking, task status)
3. Check git status for partially completed work
4. Query Cipher for implementation learnings

### Phase 1: Understanding

- Ask ONE question at a time to refine requirements
- Use **AskUserQuestion tool** for structured choices
- Gather: Purpose, constraints, success criteria, integration points
- **For extending:** Verify compatibility with original architecture

**Example AskUserQuestion:**
```
Question: "Where should data be stored?"
Options: ["Session storage" (secure), "Local storage" (persistent), "Cookies" (SSR-compatible)]
```

### Phase 2: Exploration

- Propose 2-3 architectural approaches with trade-offs
- Use **AskUserQuestion tool** to present options
- **For extending:** Consider impact on existing components

### Phase 3: Design Validation

- Present design in 200-300 word sections
- Cover: Architecture, components, data flow, error handling, testing
- Ask: "Does this approach work for your needs?"
- Adjust based on feedback

### Phase 4: Implementation Planning

**Required Plan Header:**
```markdown
# [Feature Name] Implementation Plan

> **IMPORTANT:** Start with fresh context. Run `/clear` before `/implement`.
> If context limits reached: `/remember` → `/clear` → `/implement` again

**Goal:** [One sentence describing what this builds]
**Architecture:** [2-3 sentences about approach]
**Tech Stack:** [Key technologies/libraries]

## Progress Tracking
- [ ] Task 1: [Brief summary]
- [ ] Task 2: [Brief summary]
- [ ] Task N: [Brief summary]

**Total Tasks:** [Number]
```

**For Extending Plans:**
1. Preserve original header/architecture
2. Mark new tasks with `[NEW]` prefix
3. Update total count: `Total Tasks: X (Originally: Y)`
4. Add extension history: `> Extended [Date]: Tasks X-Y for [feature]`
5. Insert tasks in logical order (after related, before dependent)

## Task Structure

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**TDD Steps (MANDATORY):**
1. Write failing test with expected behavior
2. Run: `uv run pytest tests/path/test.py::test_name -v` → FAIL
3. Write minimal implementation to pass
4. Run test again → PASS
5. **Execute actual code:** Run the program/function and verify output
6. (IF API) Create Postman collection and run with Newman

**Execution Verification:**
- Include exact command to run actual code: `uv run python src/main.py` or similar
- Show expected output/behavior (not just "should work")
- Verify logs, files created, database records, or API responses

**Include:** Complete code (no placeholders), exact commands, expected outputs

## Skills to Reference in Tasks

**Mandatory:** `@testing-test-driven-development` for all code tasks

**Context-specific:**
`@backend-api` (endpoints), `@backend-models` (database), `@backend-queries` (SQL),
`@global-error-handling`, `@global-validation`, `@testing-final-verification` (last task)

## Coding Standards

✅ **TDD Mandatory** - Test first, fail, implement, pass
✅ **DRY/YAGNI** - No repetition or speculative features
✅ **Exact paths** - Complete file paths, no ambiguity
✅ **Complete code** - No placeholders like "add validation here"
✅ **Exact commands** - With expected output
✅ **Clean code** - One-line docstrings, no inline comments, imports at top

### Phase 5: Plan Documentation

**New Plans:** Save to `docs/plans/YYYY-MM-DD-<feature-name>.md` with:
- Complete header with context management
- All tasks with exact code (no placeholders)
- Referenced skills using @ syntax

**Extended Plans:** Update existing file with:
- Preserved completed work [x] checkboxes
- New tasks marked with `[NEW]`
- Extension metadata: `> Extended [Date]: Tasks X-Y for [feature]`
- Updated counts and Cipher storage of decisions

### Phase 6: Implementation Handoff

1. Announce: "Plan saved to `docs/plans/YYYY-MM-DD-<feature-name>.md`"
2. Guide: "Has [N] tasks. To implement: `/clear` → `/implement [plan-path]`"
3. If context limits: "`/remember` → `/clear` → `/implement` again"
4. Ask: "Ready to clear context and start implementation?"

## Extension Examples

**Pattern 1: Insert Related Tasks**
```markdown
- [x] Task 1: Auth service setup
- [x] Task 2: JWT generation
- [ ] Task 3: [NEW] Error handler
- [ ] Task 4: [NEW] Rate limiting
- [ ] Task 5: User profile (was Task 3)
Total: 5 (Originally: 3)
```

**Pattern 2: Add Tests to Existing**
```markdown
- [x] Task 1: Payment gateway
- [ ] Task 2: [NEW] Unit tests for gateway
- [x] Task 3: Transaction model
- [ ] Task 4: [NEW] Unit tests for model
Total: 4 (Originally: 2)
```

**Pattern 3: Enhancement Section**
```markdown
### Original (Complete)
- [x] Tasks 1-5: Core feature
### Enhancement
- [ ] Task 6-8: [NEW] Additional feature
Total: 8 (Originally: 5, Completed: 5)
```

## When to Revisit Earlier Phases

Go backward when: New constraints revealed, validation gaps found, approach questioned, critical patterns discovered. Don't force forward progress.

## Key Principles

| Principle                | Application                              |
| ------------------------ | ---------------------------------------- |
| **Research first**       | Always Cipher + codebase before planning |
| **One question/time**    | Single question per message              |
| **Structured choices**   | AskUserQuestion for 2-4 options          |
| **YAGNI/DRY**            | No speculation or repetition             |
| **Explore alternatives** | Always 2-3 approaches                    |
| **Complete code**        | No placeholders ever                     |
| **Fresh context**        | Start with /clear                        |

**For Extensions:** Preserve history, mark [NEW], group logically, update metadata, store in Cipher

## Remember

**All plans:** Research → Question → Explore → Validate → Task → Document → Handoff

**New:** Save to `docs/plans/YYYY-MM-DD-<feature>.md`
**Extend:** Update existing file, preserve completed work, mark additions [NEW]

Always include: Exact paths, complete code, test commands, @ skills, E2E tests for APIs
