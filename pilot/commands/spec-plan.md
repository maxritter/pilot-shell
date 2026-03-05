---
description: "Spec planning phase - explore codebase, design plan, get approval"
argument-hint: "<task description> or <path/to/plan.md>"
user-invocable: false
model: opus
hooks:
  Stop:
    - command: uv run python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_plan_validator.py"
---

# /spec-plan - Planning Phase

**Phase 1 of the /spec workflow.** Explores codebase, designs implementation plan, verifies it, gets user approval.

**Input:** Task description (new) or plan path (continue unapproved)
**Output:** Approved plan at `docs/plans/YYYY-MM-DD-<slug>.md`
**Next:** On approval → `Skill(skill='spec-implement', args='<plan-path>')`

---

## ⛔ Critical Constraints

- **NO sub-agents during planning** except Step 1.7 (plan-reviewer)
- **NEVER skip plan-reviewer** when criteria are met (>3 tasks, migration, open questions) — context level is NOT a valid reason to skip
- **NEVER write code during planning** — planning and implementation are separate phases
- **NEVER assume — verify by reading files**
- **ONLY stopping point is plan approval** — everything else is automatic. Never ask "Should I fix these?"
- **Re-read plan after user edits** — before asking for approval again
- **Plan file is source of truth** — survives across auto-compaction cycles
- **Quality over speed** — never rush due to context pressure

---

## Asking User Questions

**⛔ ALWAYS use the `AskUserQuestion` tool** — never list numbered questions in plain text. Each question gets its own entry with predefined options users can select. This provides a structured form UI that is much easier to answer than freeform numbered lists.

**⛔ Default is to ASK, not skip.** Every plan benefits from at least one round of user alignment. Only skip questions when the task is a single-file change with zero ambiguity.

**Questions batched into max 2 interactions:** Batch 1 (before exploration) clarifies task/scope/priorities. Batch 2 (after exploration) resolves architecture/design decisions. **Both batches are expected for most tasks** — skipping both is the exception, not the norm.

**Principles:** Present options with trade-offs (not open-ended). Start open, narrow down. Challenge vagueness — make abstract concrete. 1-2 focused questions beat 4 vague ones. Questions clarify HOW to implement, not whether to expand scope.

## Extending Existing Plans

When adding tasks to an existing plan: load it, parse structure, verify compatibility, mark new tasks with `[NEW]`, update totals. If original + new > 12 tasks, suggest splitting.

## ⚠️ Migration/Refactoring Tasks

**When replacing existing code, complete a Feature Inventory BEFORE creating tasks:**

1. List ALL files being replaced with their functions/classes
2. Map EVERY function to a task — no row may be "Not mapped"
3. Every row needs a Task # or explicit "Out of Scope" with user confirmation

"Out of Scope: Changes to X" = X migrates AS-IS (still needs migration task). "Out of Scope: Feature X" = X intentionally REMOVED (needs user confirmation, no task needed).

---

## Creating New Plans

### Step 1.1: Create Plan File Header (FIRST)

1. **Parse worktree** from arguments: `--worktree=yes|no` (default: `Yes`). Strip flag from task description.

2. **Create worktree early (if yes):**
   ```bash
   ~/.pilot/bin/pilot worktree detect --json <plan_slug>
   # If not found:
   ~/.pilot/bin/pilot worktree create --json <plan_slug>
   # Returns: {"path": "...", "branch": "spec/<slug>", "base_branch": "main"}
   ```
   All file writes use the worktree path as base. If creation fails (old git): continue without worktree, set to `No`.

3. **Generate filename:** `docs/plans/YYYY-MM-DD-<feature-slug>.md` — slug from first 3-4 words (lowercase, hyphens). If worktree active, use worktree path as base directory.

4. `mkdir -p docs/plans`

5. **Write initial header:**

   ```markdown
   # [Feature Name] Implementation Plan

   Created: [Date]
   Status: PENDING
   Approved: No
   Iterations: 0
   Worktree: [Yes|No]
   Type: Feature

   > Planning in progress...

   ## Summary

   **Goal:** [Task description from user]

   ---

   _Exploring codebase and gathering requirements..._
   ```

6. **Register plan:** `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`

**Do this FIRST** — before any exploration or questions. Status bar shows progress immediately.

---

### Step 1.2: Task Understanding, Discuss & Clarify

1. Restate the task in your own words — core problem, assumptions
2. Identify gray areas:

   | Domain | Typical Gray Areas |
   |--------|-------------------|
   | UI/frontend | Layout, interaction patterns, empty/loading states |
   | API/backend | Response shape, error codes, auth, pagination |
   | CLI/scripts | Output format, flags, exit codes |
   | Data/config | Schema, migration, validation, defaults |

3. **Ask Batch 1 questions** → notify, then use `AskUserQuestion` with each question as a separate entry with predefined options:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Input Needed" "<plan_name> — clarification questions" --plan-path "<plan_path>" 2>/dev/null || true
   ```
   Each question must have 2-4 concrete options. Use `multiSelect: true` when choices aren't mutually exclusive.

   Even when the task seems clear, ask about: scope boundaries (what's explicitly out), priority trade-offs (speed vs completeness), or behavioral expectations (error handling, edge cases). **Only skip if the task is a trivial single-file change.**

### Step 1.3: Exploration

**Explore systematically, one area at a time (sequentially, not parallel).**

| Tool | When |
|------|------|
| **Context7** | Library/framework docs |
| **Vexor** | Semantic code search |
| **grep-mcp** | Real-world GitHub examples |
| **Read/Grep/Glob** | Direct file exploration |

**Areas (in order):** Architecture → Similar Features → Dependencies → Tests

For each: document hypotheses, note full file paths, track unanswered questions. After exploration: read identified files to verify hypotheses, build complete mental model, identify integration points, note reusable patterns.

### Step 1.3b: Present Findings & Scope Selection — CONDITIONAL

**Only when exploration revealed multiple possible directions or scope is ambiguous.** Skip for straightforward tasks.

1. Notify user, list discovered gaps/opportunities with brief assessments
2. `AskUserQuestion(multiSelect: true)` — let user pick which items to include
3. Unselected items go to "Out of Scope" or "Deferred Ideas"

### Step 1.4: Design Decisions

**⛔ Do NOT skip this step.** After exploration, there are always design choices to validate — even confirming the "obvious" approach ensures alignment. Summarize findings, notify, then use `AskUserQuestion` (Batch 2) — each decision as a separate question with concrete options:

```bash
~/.pilot/bin/pilot notify plan_approval "Design Decisions" "<plan_name> — architecture choices" --plan-path "<plan_path>" 2>/dev/null || true
```

Incorporate user choices into plan design, proceed to Step 1.5.

### Step 1.5: Implementation Planning

**Task Granularity:** Each task: independently testable, focused (2-4 files max), verifiable. Split if multiple unrelated DoD criteria; merge if one can't be tested without the other. Don't create tasks for setup/boilerplate with no standalone value — fold into the first task that uses them.

**Task Structure:**

```markdown
### Task N: [Component Name]

**Objective:** [1-2 sentences]
**Dependencies:** [None | Task X, Task Y]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py`
- Test: `tests/exact/path/to/test.py`

**Key Decisions / Notes:**
- [Technical approach, pattern to follow with file:line ref]

**Definition of Done:**
- [ ] All tests pass
- [ ] No diagnostics errors
- [ ] [Verifiable criterion — e.g., "API returns 404 for nonexistent resources"]

**Verify:**
- `uv run pytest tests/path/to/test.py -q`
```

**DoD must be verifiable.** ✅ "GET /api/users?role=admin returns only admin users" ❌ "Feature works correctly"

**Zero-context assumption:** Assume implementer knows nothing. Provide exact file paths, explain domain concepts, reference similar patterns.

#### Step 1.5.1: Goal Verification Criteria

After creating tasks, derive for the `## Goal Verification` section:
1. State the goal
2. Derive 3-7 observable truths (falsifiable, user-perspective)
3. For each truth, identify supporting artifacts (files with real implementation)
4. Identify 2-5 key links (critical component connections)

### Step 1.6: Write Full Plan

**Save to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

**Required sections:**

```markdown
# [Feature Name] Implementation Plan

Created: [Date]
Status: PENDING
Approved: No
Iterations: 0
Worktree: [Yes|No]
Type: Feature

## Summary
**Goal:** [One sentence]
**Architecture:** [2-3 sentences]
**Tech Stack:** [Key technologies]

## Scope
### In Scope
### Out of Scope

## Context for Implementer
> Write for an implementer who has never seen the codebase.
- **Patterns to follow:** [file:line references]
- **Conventions:** [naming, organization, error handling]
- **Key files:** [important files with descriptions]
- **Gotchas:** [non-obvious dependencies]
- **Domain context:** [business logic needed to understand task]

## Runtime Environment (only if project has a running service)
- **Start command / Port / Deploy path / Health check / Restart procedure**

## Feature Inventory (only for migration/refactoring — see Migration section)

## Progress Tracking
- [ ] Task 1: [summary]
**Total Tasks:** N | **Completed:** 0 | **Remaining:** N

## Implementation Tasks
[Tasks from Step 1.5]

## Testing Strategy
- Unit / Integration / Manual verification

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
⚠️ Mitigations are commitments — verification checks they're implemented.
✅ "Reset to null when project not in list" ❌ "Handle edge cases"

## Goal Verification
### Truths
### Artifacts
### Key Links

## Open Questions (only if any remain)
### Deferred Ideas (only if any surfaced)
```

### Step 1.7: Plan Verification — CONDITIONAL

**Run plan-reviewer when:** plan has >3 tasks, OR includes a Feature Inventory (migration), OR has unresolved open questions.

**Skip when:** plan has ≤3 tasks with clear scope and no migration — proceed directly to Step 1.8.

**When running:**

```bash
SESS_ID=$(echo $PILOT_SESSION_ID)
```

Output path: `~/.pilot/sessions/<SESS_ID>/findings-plan-reviewer.json`

**⛔ Delete stale findings before launching** (same path may exist from a previous `/spec` in this session):

```bash
rm -f "$OUTPUT_PATH"
```

```
Task(
  subagent_type="pilot:plan-reviewer",
  run_in_background=true,
  prompt="""
  **Plan file:** <plan-path>
  **User request:** <original task description>
  **Clarifications:** <any Q&A>
  **Output path:** <absolute path to findings JSON>

  Review for alignment with requirements AND adversarial risks.
  Write findings JSON to output_path using Write tool.
  """
)
```

**⛔ NEVER use `TaskOutput`** to retrieve results — it dumps the full agent transcript into context, wasting thousands of tokens.

**Wait for results (bash polling — NOT Read loop):**

```bash
OUTPUT_PATH="<findings-path>"
for i in $(seq 1 30); do [ -f "$OUTPUT_PATH" ] && echo "READY" && break; sleep 10; done
```

Then Read the file once. If not READY after 5 min, re-launch synchronously.

**Fix findings:** must_fix → should_fix immediately. Suggestions if reasonable. Proceed after all must_fix/should_fix resolved.

### Step 1.8: Get User Approval

**⛔ MANDATORY APPROVAL GATE**

0. Notify:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Plan Ready for Review" "<plan_name> — approval needed" --plan-path "<plan_path>" 2>/dev/null || true
   ```

1. Summarize: goal, key tasks, approach

2. AskUserQuestion:
   - "Yes, proceed with implementation" — I've reviewed and it looks good
   - "No, I need to make changes" — Let me edit first

   Note: `Worktree:` field was already set at creation time (Step 1.1). Do NOT ask again here.

3. **If "Yes":** Set `Approved: Yes`, invoke `Skill(skill='spec-implement', args='<plan-path>')`
   **If "No":** Tell user to edit plan, wait for "ready", re-read, ask again
   **If other feedback (config values, threshold changes, clarifications):** This is NOT approval — incorporate changes into plan, then re-ask with fresh AskUserQuestion.

ARGUMENTS: $ARGUMENTS
