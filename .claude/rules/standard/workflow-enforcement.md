# Workflow Enforcement Rules

**Rule:** Follow the /plan → /implement → /verify workflow exactly. No shortcuts. No sub-agents.

## No Sub-Agents Policy

**DO NOT use the Task tool with any subagent_type during project workflows.**

### Prohibited

| Subagent Type | Why Prohibited |
|---------------|----------------|
| `Explore` | Loses conversation context, use direct tools instead |
| `Plan` | Use `/plan` command, not Task tool |
| `general-purpose` | Maintain context yourself with direct tool calls |

### Use Instead

| Instead of Sub-Agent | Use These Directly |
|----------------------|---------------------|
| `Task(subagent_type="Explore")` | `Read`, `Grep`, `Glob` |
| `Task(subagent_type="Plan")` | `/plan` slash command |
| `Task(subagent_type="general-purpose")` | Direct tool calls (Read, Grep, Bash, etc.) |

### Allowed Task Tool Usage

The Task tool IS allowed for:
- **Skills:** Invoking project skills via `Skill` tool
- **Background shells:** Using `run_in_background` for long-running commands

## Plan-Implement-Verify Lifecycle

The project uses a three-phase workflow that must be followed strictly:

| Phase | Command | Status | Next Action |
|-------|---------|--------|-------------|
| Planning | `/plan` | Creates plan with `Status: PENDING` | User reviews, then `/implement` |
| Implementation | `/implement` | Updates to `Status: COMPLETE` | Run `/verify` |
| Verification | `/verify` | Updates to `Status: VERIFIED` | Done |

**Status values in plan files:**
- `PENDING` - Tasks remain to be implemented
- `COMPLETE` - All tasks implemented (set by /implement)
- `VERIFIED` - Verification passed (set by /verify)

## Mandatory Task Completion Tracking

**After completing EACH task during /implement, you MUST:**

1. **Edit the plan file immediately** - Change `[ ]` to `[x]` for the completed task
2. **Update Progress Tracking counts** - Increment Completed, decrement Remaining
3. **Do NOT proceed to next task** until checkbox is updated

**This applies to EVERY task, not just at the end of implementation.**

### Valid Plan Progress Tracking

```markdown
## Progress Tracking

- [x] Task 1: Create package structure
- [x] Task 2: Implement UI layer
- [ ] Task 3: Implement context module  ← Currently implementing
- [ ] Task 4: Add error handling

**Total Tasks:** 4 | **Completed:** 2 | **Remaining:** 2
```

### Invalid (What NOT to Do)

```markdown
## Progress Tracking

- [ ] Task 1: Create package structure  ← WRONG: Task done but not checked
- [ ] Task 2: Implement UI layer        ← WRONG: Task done but not checked
- [x] Task 3: Implement context module
- [ ] Task 4: Add error handling

**Total Tasks:** 4 | **Completed:** 1 | **Remaining:** 3  ← WRONG: Counts don't match
```

## Verification Red Flags

The following indicate workflow violations:

### During /implement

- Proceeding to next task without updating checkbox
- Completing all tasks without any checkboxes marked
- Counts don't match number of checked boxes
- `Status: PENDING` at end of implementation (should be `COMPLETE`)

### During /verify

- Plan shows `Status: PENDING` (should have been set to `COMPLETE` by /implement)
- Tasks are incomplete (`[ ]`) but claimed as done
- Completed count doesn't match checked boxes
- Missing features found that have no corresponding tasks

## Migration/Refactoring Rules

When the plan involves replacing existing code:

1. **Feature Inventory is REQUIRED** - List every file, function, class being replaced
2. **Every feature must map to a task** - No unmapped features allowed
3. **"Out of Scope" requires user confirmation** - Only use for intentional removals
4. **Feature parity check during /verify** - Compare old vs new functionality

### Feature Inventory Format

```markdown
## Feature Inventory

| Old File | Functions/Classes | Mapped to Task |
|----------|-------------------|----------------|
| `old/file.py` | `func_a()`, `func_b()` | Task 3 |
| `old/other.py` | `ClassX` | Task 4 |

**Verification:**
- [x] All old files listed
- [x] All functions/classes identified
- [x] Every feature has a task number
```

## What the Rules Supervisor Checks

When a plan reaches `Status: COMPLETE`, the supervisor verifies:

1. **Checkbox Consistency:**
   - All tasks have checkboxes
   - Completed count = number of `[x]` checkboxes
   - Remaining count = number of `[ ]` checkboxes (should be 0)

2. **Progress Tracking:**
   - Total = Completed + Remaining
   - All tasks should be `[x]` when status is COMPLETE

3. **For Migrations:**
   - Feature Inventory section exists
   - All features mapped to tasks
   - No "❌ MISSING" or "⬜ Not mapped" entries

4. **Status Progression:**
   - PENDING → COMPLETE → VERIFIED
   - Never skip states

## Common Violations and Fixes

| Violation | Symptom | Fix |
|-----------|---------|-----|
| Forgot to update checkbox | `[ ]` on completed task | Edit plan, change to `[x]` |
| Wrong counts | Completed + Remaining ≠ Total | Recount and update |
| Missing feature inventory | Migration without inventory | Add Feature Inventory section |
| Status not updated | `PENDING` after all tasks done | Change to `COMPLETE` |
| Tasks implemented but not tracked | Tests pass but checkboxes empty | Update all checkboxes retroactively |

## Enforcement Protocol

**If workflow violations detected:**

1. **STOP** - Do not proceed
2. **Report** - List all violations found
3. **Fix** - Update plan file with correct checkboxes, counts, status
4. **Re-verify** - Run verification again

**Violations are blocking** - The workflow cannot proceed until fixed.

## Quick Reference

| When | Action | Verify |
|------|--------|--------|
| Complete a task | Edit plan: `[ ]` → `[x]`, update counts | Checkbox changed, counts match |
| Finish /implement | Set `Status: COMPLETE` | All `[x]`, counts show 0 remaining |
| Pass /verify | Set `Status: VERIFIED` | All checks passed |
| Find missing feature | Add task with `[MISSING]` prefix | Set `Status: PENDING` |
