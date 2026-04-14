---
name: spec-plan
description: "Spec planning phase - explore codebase, design plan, get approval"
argument-hint: "<task description> or <path/to/plan.md>"
user-invocable: false
effort: high
model: opus
hooks:
  Stop:
    - command: uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_plan_validator.py"
---

# /spec-plan - Planning Phase

**Phase 1 of the /spec workflow.** Explores codebase, designs implementation plan, verifies it, gets user approval.

**Input:** Task description (new) or plan path (continue unapproved)
**Output:** Approved plan at `docs/plans/YYYY-MM-DD-<slug>.md`
**Next:** On approval → `Skill(skill='spec-implement', args='<plan-path>')`

---

## ⛔ Critical Constraints

- **NO sub-agents during planning** except Step 1.7 (spec-review, when enabled in settings)
- **Run spec-review when enabled** — it runs for every feature spec when `$PILOT_SPEC_REVIEW_ENABLED` is not `"false"`. Context level is NOT a valid reason to skip. To disable, use Console Settings → Reviewers → Spec Review toggle.
- **NEVER write code during planning** — planning and implementation are separate phases
- **NEVER assume — verify by reading files**
- **ONLY stopping point is plan approval** — everything else is automatic. Never ask "Should I fix these?"
- **Re-read plan after user edits** — before asking for approval again
- **Plan file is source of truth** — survives across auto-compaction cycles
- **Quality over speed** — never rush due to context pressure

---

## Step 0: Read Toggle Configuration

**⛔ Run FIRST, before any other step.** Read all toggle env vars in a single Bash call:

```bash
echo "QUESTIONS=$PILOT_PLAN_QUESTIONS_ENABLED REVIEWER=$PILOT_SPEC_REVIEW_ENABLED CODEX_SPEC=$PILOT_CODEX_SPEC_REVIEW_ENABLED APPROVAL=$PILOT_PLAN_APPROVAL_ENABLED"
```

Reference these values throughout: Steps 1.2/1.4 (questions), 1.7 (reviewer + Codex — Codex controlled by Console Settings), and 1.8 (approval).

---

## Asking User Questions

**⛔ If `PILOT_PLAN_QUESTIONS_ENABLED` is `"false"` (from Step 0),** skip ALL `AskUserQuestion` calls in Steps 1.2 and 1.4. Make reasonable default choices (including selecting the recommended approach in Step 1.4) and document them in the plan under an "Autonomous Decisions" sub-section. Continue to the next step immediately.

**⛔ ALWAYS use the `AskUserQuestion` tool** (when questions are enabled) — never list numbered questions in plain text. Each question gets its own entry with predefined options users can select. This provides a structured form UI that is much easier to answer than freeform numbered lists.

**⛔ Default is to ASK, not skip.** Every plan benefits from at least one round of user alignment. Only skip questions when the task is a single-file change with zero ambiguity.

**Questions batched into max 2 interactions:** Batch 1 (before exploration) clarifies task/scope/priorities. Batch 2 (after exploration) covers approach selection and design decisions. **Both batches are expected for most tasks** — skipping both is the exception, not the norm.

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

1. **Parse flags** from arguments: `--worktree=yes|no` or `--new-branch` (default: `Yes`). Strip the flag from task description.

2a. **Create new branch (if `--new-branch`):**

   **Step 1 — Stash any uncommitted work** (prevents checkout conflicts):
   ```bash
   STASH_MSG="pilot-spec-$(date +%s)"
   git stash push -m "$STASH_MSG" --include-untracked 2>/dev/null
   STASHED=$?  # 0 = stashed something, 1 = nothing to stash
   ```

   **Step 2 — Detect default branch** (local-only, no network dependency):
   ```bash
   git fetch origin 2>/dev/null
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
   DEFAULT_BRANCH=${DEFAULT_BRANCH:-main}
   ```

   **Step 3 — Create and checkout the branch** (handle name collisions):
   ```bash
   BRANCH_NAME="feat/<plan_slug>"
   # If branch already exists, append short timestamp
   if git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1; then
     BRANCH_NAME="feat/<plan_slug>-$(date +%m%d-%H%M)"
   fi
   git checkout -b "$BRANCH_NAME" "origin/$DEFAULT_BRANCH"
   ```

   **Step 4 — Restore stash on failure:**
   ```bash
   # If checkout failed and we stashed, restore the stash
   if [ $? -ne 0 ] && [ "$STASHED" -eq 0 ]; then
     git stash pop 2>/dev/null
   fi
   ```

   `<plan_slug>` is derived from the task description (same slug used for the plan filename). If checkout fails even after stashing (e.g. no origin remote), warn the user and fall back to current branch — the stash is restored automatically. After branch creation, continue with `Worktree: No` semantics (work directly on the new branch). Note: the stash remains in `git stash list` and can be recovered with `git stash pop` if needed.

2b. **Create worktree early (if `--worktree=yes`):**

   ```bash
   ~/.pilot/bin/pilot worktree detect --json <plan_slug>
   # If not found:
   ~/.pilot/bin/pilot worktree create --json <plan_slug>
   # Returns: {"path": "...", "branch": "spec/<slug>", "base_branch": "main"}
   ```

   All file writes use the worktree path as base. If creation fails (old git): continue without worktree, set to `No`.

3. **Generate filename:** (for both worktree and new-branch paths) `docs/plans/YYYY-MM-DD-<feature-slug>.md` — slug from first 3-4 words (lowercase, hyphens). If worktree active, use worktree path as base directory.

4. **Fetch author email** (best-effort, do not fail if unavailable):

   ```bash
   ~/.pilot/bin/pilot status --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('email',''))" 2>/dev/null
   ```

   If the command returns a non-empty email, include `Author: <email>` in the header. If empty or fails, omit the Author line entirely.

5. **Write initial header:**

   ```markdown
   # [Feature Name] Implementation Plan

   Created: [Date]
   Author: [email if available]
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
2. **Scope check:** Does this task describe multiple independent subsystems (e.g., "build chat, file storage, billing, and analytics")? If so, flag immediately — don't spend questions refining details of a task that needs decomposition first. Suggest splitting into separate plans, one per subsystem, each producing working software on its own. Proceed with the first sub-task.
3. Identify gray areas:

   | Domain      | Typical Gray Areas                                 |
   | ----------- | -------------------------------------------------- |
   | UI/frontend | Layout, interaction patterns, empty/loading states |
   | API/backend | Response shape, error codes, auth, pagination      |
   | CLI/scripts | Output format, flags, exit codes                   |
   | Data/config | Schema, migration, validation, defaults            |

3. **Ask Batch 1 questions** → notify, then use `AskUserQuestion` with each question as a separate entry with predefined options:

   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Input Needed" "<plan_name> — clarification questions" --plan-path "<plan_path>" 2>/dev/null || true
   ```

   Each question must have 2-4 concrete options. Use `multiSelect: true` when choices aren't mutually exclusive.

   Even when the task seems clear, ask about: scope boundaries (what's explicitly out), priority trade-offs (speed vs completeness), or behavioral expectations (error handling, edge cases). **Only skip if the task is a trivial single-file change.**

### Step 1.3: Exploration

**⛔ START WITH CODEGRAPH — before reading any files or running any searches.**

#### 1.3.1: Orient with CodeGraph (MANDATORY FIRST ACTION)

```
codegraph_context(task="<task description from user>")
```

This returns entry points, related symbols, and key code. Works best when the task maps to actual code symbols. If it returns irrelevant results (e.g., only tests or UI components), the task may be conceptual — supplement with Probe `probe search "how does X work"` for intent-based discovery.

#### 1.3.2: Deep dive with CodeGraph explore

After orienting, use `codegraph_search` to find specific symbol names, then:

```
codegraph_explore(query="SymbolA SymbolB relevant-file.ts")
```

This returns **full source code sections** from all relevant files in ONE call — replacing dozens of Read/Grep calls. Use specific symbol names (from search results), not natural language. Follow the call budget in the tool description.

#### 1.3.3: Systematic exploration

**Explore one area at a time (sequentially, not parallel).** Use CodeGraph and Probe as primary tools — Grep/Glob only for exact text patterns.

| Need                            | Tool                                                    |
| ------------------------------- | ------------------------------------------------------- |
| **Orient on the task**          | CodeGraph `codegraph_context(task=<description>)` — already done in 1.3.1 |
| **Deep understanding of code**  | CodeGraph `codegraph_search` → `codegraph_explore(query="<symbol names>")` |
| **Understand a feature by intent** | Probe `probe search "how does X work"`               |
| **Find symbols by name**        | CodeGraph `codegraph_search`                            |
| **Extract code by symbol/line** | Probe `probe extract file.ts#symbol`                    |
| **Project file structure**      | CodeGraph `codegraph_files`                             |
| **Call tracing**                | CodeGraph `codegraph_callers`/`codegraph_callees`       |
| **Library/framework docs**      | Context7                                                |
| **Real-world GitHub examples**  | grep-mcp                                                |
| **Exact text/regex**            | Grep/Glob (last resort)                                 |

**Areas (in order):** Architecture → Similar Features → Dependencies → Tests

#### 1.3.4: Dependency analysis (MANDATORY for 3+ file changes)

For every function you plan to modify: (1) `codegraph_callers` + `codegraph_callees` for the call graph, (2) `Grep` for the symbol name to catch callers the graph may miss, (3) `codegraph_impact` to assess blast radius. CodeGraph gives structure; Grep gives completeness — use both.

For each area: document hypotheses, note full file paths, track unanswered questions. After exploration: read identified files to verify hypotheses, build complete mental model, identify integration points, note reusable patterns.

### Step 1.4: Approach Selection & Design Decisions

**⛔ Do NOT skip this step.** After exploration, always propose competing approaches before committing to a design. Even when one approach seems obvious, stating alternatives with trade-offs validates the choice and surfaces blind spots.

**Two parts — both mandatory:**

#### Part A: Overall Approach

Propose 2-3 implementation approaches based on exploration findings. For each approach:

- **Name** — short label (e.g., "Extend existing handler" vs "New dedicated service")
- **How it works** — 2-3 sentences
- **Trade-offs** — frame as **"X at the cost of Y"** — never recommend without stating what it costs
- **Recommendation** — mark your preferred approach with reasoning

If exploration also revealed scope ambiguity (gaps, optional features, multiple directions), include scope items as part of this step. `AskUserQuestion(multiSelect: true)` for scope items; unselected items go to "Out of Scope" or "Deferred Ideas."

#### Part B: Design Decisions

Within the chosen approach, resolve remaining design choices. Each decision gets 2-3 concrete options with trade-offs and your recommendation.

**Notify, then ask (Batch 2):**

```bash
~/.pilot/bin/pilot notify plan_approval "Design Decisions" "<plan_name> — architecture choices" --plan-path "<plan_path>" 2>/dev/null || true
```

Use `AskUserQuestion` — Part A (approach selection) and Part B (design decisions) can be combined into a single Batch 2 interaction when the decisions are related.

**When questions are disabled (`PILOT_PLAN_QUESTIONS_ENABLED=false`):** Still evaluate approaches and design decisions internally. Select the recommended approach, resolve design decisions with reasonable defaults, and document all choices with reasoning in the plan's "Autonomous Decisions" section.

Incorporate choices into plan design, proceed to Step 1.5.

### Step 1.5: Implementation Planning

**Task Granularity:** Each task: independently testable, focused (2-4 files max), verifiable. Split if multiple unrelated DoD criteria; merge if one can't be tested without the other. Don't create tasks for setup/boilerplate with no standalone value — fold into the first task that uses them.

**Task Structure:**

```markdown
### Task N: [Component Name]

**Objective:** [1-2 sentences]
**Dependencies:** [None | Task X, Task Y]
**Mapped Scenarios:** [None | TS-001, TS-002]

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

**Performance considerations:** When a task processes data on a hot path (render loops, request handlers, polling callbacks), note it in Key Decisions. Flag: expensive computations that should be cached/memoized, heavy dependencies that have lighter alternatives, and repeated work that can be avoided when input hasn't changed.

**Zero-context assumption:** Assume implementer knows nothing. Provide exact file paths, explain domain concepts, reference similar patterns.

**Assumptions:** After creating tasks, write the `## Assumptions` section — one bullet per assumption: what you assume, which finding supports it, which task numbers depend on it. When implementation hits a surprise, this list tells the implementer which tasks are affected.

#### Step 1.5.1: Goal Verification Criteria

After creating tasks, derive for the `## Goal Verification` section:

1. State the goal
2. Derive 3-7 observable truths (falsifiable, user-perspective)
3. For each truth, identify supporting artifacts (files with real implementation, not stubs)

### Step 1.5.2: E2E Test Scenarios (Conditional)

**Skip when:** Runtime profile would be Minimal (no UI, no server, no user-facing entry points). Use the same classification logic as `spec-verify` Step 3.0 — if Phase B would be skipped entirely, skip this step too.

For features with UI or user-facing workflows, create structured E2E scenarios describing exactly how a user verifies the feature works. These become the verification contract for Phase B in `spec-verify` — the verifier executes them step by step rather than improvising.

**Format — add as `## E2E Test Scenarios` section in the plan:**

```markdown
### TS-001: [Scenario Name]
**Priority:** Critical | High | Medium
**Preconditions:** [Required state — e.g., "logged in as admin", "no existing items"]
**Mapped Tasks:** Task 1, Task 3

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | [Navigate / click / fill — concrete browser automation action] | [What user sees] |
| 2 | [Next action] | [Expected UI response] |
```

**Guidelines:**
- 3–8 scenarios typical — focus on user-visible workflows, not unit-level behavior
- **Critical** = must pass before deployment; **High** = essential UX; **Medium** = edge cases / error states
- Every task that changes UI or user-visible behavior must be covered by at least one scenario
- Steps must be executable via browser automation — Claude Code Chrome, playwright-cli, or agent-browser (concrete: navigate, click, fill, read page — no "observe manually")
- Test what users see, not internal implementation — same observable inputs and outputs

When scenarios are written, update Goal Verification truths to reference them (e.g., "TS-001 passes end-to-end").

---

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

## Approach

**Chosen:** [Name of selected approach]
**Why:** [1-2 sentences — what it gives us and what it costs]
**Alternatives considered:** [Brief list of other approaches with why they were rejected]

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

## Assumptions

- [What you assume] — supported by [finding/file:line] — Tasks N, M depend on this
- [What you assume] — supported by [finding/file:line] — Task N depends on this

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
⚠️ Mitigations are commitments — verification checks they're implemented.
✅ "Reset to null when project not in list" ❌ "Handle edge cases"

## Goal Verification

### Truths

### Artifacts

## E2E Test Scenarios (omit section for Minimal runtime profile)

[Scenarios from Step 1.5.2]

## Progress Tracking

- [ ] Task 1: [summary]
      **Total Tasks:** N | **Completed:** 0 | **Remaining:** N

## Implementation Tasks

[Tasks from Step 1.5]

## Open Questions (only if any remain)

### Deferred Ideas (only if any surfaced)
```

### Step 1.7: Plan Verification

**⛔ If `PILOT_SPEC_REVIEW_ENABLED` is `"false"` (from Step 0),** skip this step entirely and proceed to Step 1.8.

**When enabled:** Run spec-review for every feature spec. Small plans benefit from a second pair of eyes just as much as large ones — missing edge cases and unclear DoD criteria are size-independent.

```bash
SESS_ID=$(echo $PILOT_SESSION_ID)
```

**Derive plan slug** from the plan filename: strip the date prefix (`YYYY-MM-DD-`) and `.md` extension. Example: `2026-03-02-sku-builder-modal-cleanup.md` → `sku-builder-modal-cleanup`.

Output path: `~/.pilot/sessions/<SESS_ID>/findings-spec-review-<plan-slug>.json`

**⛔ Delete stale findings before launching** (previous run of the same plan may have left a file):

```bash
rm -f "$OUTPUT_PATH"
```

```
Task(
  subagent_type="pilot:spec-review",
  run_in_background=true,
  prompt="""
  **Plan file:** <plan-path>
  **User request:** <original task description>
  **Clarifications:** <any Q&A>
  **Output path:** <absolute path to findings JSON>

  Review for alignment with requirements AND adversarial risks.
  Write findings JSON to output_path using Write tool.
  IMPORTANT: Include the plan file path in your output JSON as the "plan_file" field.
  """
)
```

**⛔ NEVER use `TaskOutput`** to retrieve results — it dumps the full agent transcript into context, wasting thousands of tokens.

#### Codex Adversarial Review (Optional — launch immediately after Claude reviewer)

**If `PILOT_CODEX_SPEC_REVIEW_ENABLED` is `"true"` (from Step 0):**

Launch Codex review NOW — it runs in parallel with the Claude reviewer above.

1. Detect companion path, project root, and base branch:
```bash
CODEX_COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
# Use worktree base branch if in worktree, otherwise detect repo default branch
BASE_BRANCH=$(~/.pilot/bin/pilot worktree status --json 2>/dev/null | grep -o '"base_branch":"[^"]*"' | cut -d'"' -f4)
[ -z "$BASE_BRANCH" ] && BASE_BRANCH=$(cd "$PROJECT_ROOT" && git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")
```

2. Launch adversarial review in background. **⛔ Use `Bash(run_in_background=true)`** — the companion's `--background` flag is a no-op for reviews (only works for `task`), so we use Claude Code's background bash instead. The review runs synchronously inside the bash, and you'll be notified when it completes:
```bash
cd "$PROJECT_ROOT" && node "$CODEX_COMPANION" adversarial-review --base "$BASE_BRANCH" "Challenge this plan: <plan summary/goal>. Plan file: <plan-path>. Focus on: wrong assumptions, missing edge cases, scope gaps, and design choices that could fail under real-world conditions."
```
**Do NOT wait** — proceed to collect the Claude reviewer results first.

#### Collect Review Results

**Wait for Claude reviewer results (bash polling — NOT Read loop):**

```bash
OUTPUT_PATH="<findings-path>"
for i in $(seq 1 150); do [ -f "$OUTPUT_PATH" ] && echo "READY" && break; sleep 2; done
```

Then Read the file once. If not READY after 5 min, re-launch synchronously.

**⛔ Validate findings:** After reading the JSON, verify that the `plan_file` field matches the current plan path. If it doesn't match, the findings are stale from a previous `/spec` — delete the file, re-launch the reviewer, and wait again.

**Fix Claude reviewer findings immediately** — must_fix → should_fix. Suggestions if reasonable.

#### Collect Codex Results (if launched)

**⛔ MANDATORY — NEVER skip or defer the Codex review.** If Codex was launched above, you MUST collect and act on its results before proceeding. The Codex review runs as `Bash(run_in_background=true)` — you will be notified when it completes.

**⛔ If the notification hasn't arrived yet:** Wait. Do NOT proceed. Check the output file to see if `# Codex Adversarial Review` with a `Verdict:` line is present.

1. **When the notification arrives**, read the background bash output. **Filter out `[codex]` prefixed log lines** — use `ctx_execute_file` to extract only non-`[codex]` lines.

2. **Parse the output:** Look for the `# Codex Adversarial Review` section. Extract `Verdict:` and `Findings:` lines. Map severities: `[high]` / `[critical]` → must_fix, `[medium]` / `[low]` → should_fix. Fix all must_fix/should_fix.

3. **If the background bash timed out or failed** (exit code non-zero): Re-launch synchronously and wait. Only skip if the second attempt also fails.

**If Codex was NOT launched**, proceed after all Claude reviewer must_fix/should_fix resolved.

### Step 1.7b: Check for Console Annotation Feedback (Before Approval)

**⛔ Run this BEFORE Step 1.8 (approval).** Check if the user has annotated the plan in the Console's Specifications tab. Annotations auto-save to the unified JSON file — no "Send Feedback" button needed.

1. Derive the annotation file path from the plan path:
   - Plan: `docs/plans/2026-03-26-my-feature.md` → Annotations: `docs/plans/.annotations/2026-03-26-my-feature.json`

2. Read the annotation file with the Read tool. If the file doesn't exist, treat as `NO_FEEDBACK`. If it exists, check whether the `planAnnotations` array contains any entries (`FEEDBACK_EXISTS`) or is empty/missing (`NO_FEEDBACK`).

3. **If `FEEDBACK_EXISTS`:**
   - Each annotation in `planAnnotations` has `originalText` (selected text) and `text` (user's note)
   - Incorporate ALL annotations into the plan: treat each annotation's `text` as the user's instruction for that passage
   - After incorporating: delete the annotation file: `rm -f "<annotation-file-path>"` (e.g. `rm -f "docs/plans/.annotations/2026-03-26-my-feature.json"`). Direct file deletion is used instead of the DELETE API because curl is blocked in several hook environments.
   - Note: "Incorporated user annotations from Console — [N changes]"
   - Proceed to Step 1.8 with the updated plan

4. **If `NO_FEEDBACK`:** proceed directly to Step 1.8.

### Step 1.8: Get User Approval

**⛔ If `PILOT_PLAN_APPROVAL_ENABLED` is `"false"` (from Step 0),** skip this step: set `Approved: Yes` in the plan file automatically and immediately invoke `Skill(skill='spec-implement', args='<plan-path>')`. No AskUserQuestion, no notification.

**When `PILOT_PLAN_APPROVAL_ENABLED` is NOT `"false"` — MANDATORY APPROVAL GATE:**

0. Notify:

   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Plan Ready for Review" "<plan_name> — annotate in Console or approve here" --plan-path "<plan_path>" 2>/dev/null || true
   ```

1. Summarize: goal, key tasks, approach

2. AskUserQuestion:
   - "Yes, proceed with implementation" — I've reviewed and it looks good
   - "No, I need to make changes" — Let me edit the plan file first
   - "No, I'll annotate in the Console" — I'll use the Specifications tab to mark up the plan visually

   Note: `Worktree:` field was already set at creation time (Step 1.1). Do NOT ask again here.

3. **If "Yes":** Set `Approved: Yes`, invoke `Skill(skill='spec-implement', args='<plan-path>')`
   **If "No, I need to make changes":** Tell user to edit plan directly or annotate in the Console's Specifications tab (annotations auto-save — no button needed), then say "ready". Wait. Re-run Step 1.7b (check for annotation feedback), re-read plan, ask again
   **If "No, I'll annotate in the Console":** Tell user to annotate in the Console Specifications tab — annotations save automatically as they type. Say "ready" when done. Wait. Re-run Step 1.7b, re-read plan, ask again
   **If other feedback (config values, threshold changes, clarifications):** This is NOT approval — incorporate changes into plan, then re-ask with fresh AskUserQuestion.

ARGUMENTS: $ARGUMENTS
