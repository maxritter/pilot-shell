## Step 7: Implementation Planning

### 7.0: File Structure (when 4+ tasks expected, otherwise inline per task)

When the plan will have 4+ tasks, write a `## File Structure` section before tasks listing every file with one-line responsibility — decomposition decisions get locked in here. For 1–3 task plans skip this; the per-task `Files:` block already gives the same view.

```markdown
## File Structure

- `src/foo/bar.ts` (create) — pure function: `parseFoo(input) → Foo`. No I/O.
- `src/foo/loader.ts` (create) — fetches and caches Foo from API. Wraps `parseFoo`.
- `tests/foo/bar.test.ts` (create) — unit tests for `parseFoo`.
```

One responsibility per file. Files that change together live together. In existing codebases, follow established patterns — don't restructure unrelated code.

### 7.1: Task Granularity

**Task Granularity:** Each task: independently testable, focused (2-4 files max), verifiable. Split if multiple unrelated DoD criteria; merge if one can't be tested without the other. Don't create tasks for setup/boilerplate with no standalone value — fold into the first task that uses them. Task ORDER implies dependencies — no separate `Dependencies:` field needed.

**Task Structure (3 required fields — keep it tight):**

```markdown
### Task N: [Component Name — make the TITLE the objective. "Rename foo → bar in launcher" tells the reader everything; do not then write a 2-sentence Objective restating it.]

**Objective:** [OPTIONAL — include ONLY when the title cannot convey purpose. If the title is self-explanatory ("Rename X → Y", "Add /api/users endpoint", "Migrate v10 → v11"), OMIT this field entirely. When included, ≤2 sentences capturing why or cross-task implications the title can't. If covered by a specific E2E scenario, reference it inline: "verified by TS-002".]

**Files:**

- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py`
- Test: `tests/exact/path/to/test.py`

**Key Decisions / Notes:**

- [Technical approach, pattern to follow with file:line ref]
- `Trivial:` [Include this bullet ONLY for trivial changes — one-line justification: "≤ 5 net new lines, no new branch/loop/try with non-trivial body, no new public symbol, no new error path; covered by `<existing-test-or-verify-command>`". Otherwise omit entirely.]

**Definition of Done:**

- [ ] [Verifiable behavioral criterion — e.g., "GET /api/users?role=admin returns only admin users"]
- [ ] [Additional verifiable criterion if the task has multiple observable outcomes]
- [ ] Verify: `uv run pytest tests/path/to/test.py -q` (and any other command that proves the criteria above)
```

**Rules:**

- **DoD must be verifiable.** ✅ "GET /api/users?role=admin returns only admin users" ❌ "Feature works correctly".
- **Tests-pass and no-diagnostics are implicit** — every task must end with those. Do NOT add them as DoD bullets; only list task-specific behaviors.
- **The last DoD bullet IS the verify command.** No separate `Verify:` block.
- **`Trivial:` is a per-task annotation, not a section** — the reviewer agent and `spec-verify` Step 2.1 audit it against the diff regardless of where it sits, as long as it's the literal token `Trivial:` somewhere in the task body.
- **Key Decisions: aim for ≤5 bullets per task.** Prefer `file:line` refs over prose. Multi-paragraph explanations belong in a comment in the code, not in the plan — the plan should point the implementer at WHERE to look and WHAT pattern to follow, not re-explain the existing system.

#### Test plan parsimony

**Testing posture preference.** If there is no project-level testing rule/memory and this plan would introduce several test classes or force a choice between unit-only vs unit+functional coverage, ask one concise question about testing posture. Default to the parsimonious posture here if questions are disabled or the user does not specify a preference.

When listing files for a task, do not auto-create a new `tests/.../test_<file>.py` line for every modified production file. Apply these rules in order:

1. If an existing test class for this production class already exists, reuse it (modify, do not duplicate).
2. If the change is genuinely trivial (≤ 5 net new lines, no new branch/loop/try with non-trivial body, no new public symbol, no new error path), set the task's `Trivial:` field with the justification and the existing covering test/verification command — and omit the test file from `Files:`.
3. Otherwise, plan **at most 1 new unit test class + at most 1 new functional/integration test class** for this production class. More than that requires an explicit `Why >2 test classes:` note in `Key Decisions`.
4. Never plan a test file per method or per branch. The test class is the unit; methods inside it cover branches.

The reviewer agent (`pilot/agents/changes-review.md`) and `spec-verify` Step 2 audit these rules against the actual diff — they are not advisory.

**Performance considerations:** When a task processes data on a hot path (render loops, request handlers, polling callbacks), note it in Key Decisions. Flag: expensive computations that should be cached/memoized, heavy dependencies that have lighter alternatives, and repeated work that can be avoided when input hasn't changed.

**Zero-context assumption:** Assume implementer knows nothing. Provide exact file paths, explain domain concepts, reference similar patterns.

**Assumptions (conditional):** Only write a `## Assumptions` section when an assumption — if wrong — would silently invalidate a task. One bullet per real assumption: what you assume + which task numbers depend on it. Omit the section when there are none; do NOT include tautological assumptions ("config.json is the authoritative store") just to fill space.

#### Step 7.2: Goal Verification Criteria (skip step if no cross-task observable outcomes exist)

After creating tasks, ask: **is there a user-facing observable outcome that NO single E2E scenario captures AND NO single task DoD captures?** If no → skip this step entirely; the `## Goal Verification` section does not appear in the plan. spec-verify Step 10 audits via E2E and task-DoD source keys in that case.

If yes → write **at most 3 truths** for the `## Goal Verification > ### Truths` section. Each truth must be cross-task and not reducible to a single TS-NNN or task DoD reference. If you find yourself writing `[behavior] — TS-NNN passes`, that's not a truth — it's a redirect; delete it and rely on TS-NNN itself.

Do NOT list "supporting artifacts" — they duplicate the per-task `Files:` blocks. Do NOT paraphrase task titles as truths — the task list is the in-scope inventory.

#### Step 7.3: Completeness Probe

**⛔ Skip this step when task count ≤ 2** AND the plan does NOT touch security, authentication, data integrity, or destructive operations — the probe's ~2-min cost exceeds its value for 1–2 task changes whose error paths the implementer can audit by inspection. For 3+ task plans, OR any plan touching sensitive surfaces regardless of size, run the probe in full.

Before locking the truth list, work backward from the success state to find missing observable behaviors. For the chosen approach, walk these four prompts once:

1. **What could prevent the success state?** For each prerequisite the success path assumes, is there a truth covering what the system does when the prerequisite fails (missing input, invalid input, conflicting state, expired credential, rate-limit exceeded, downstream dependency unavailable, concurrent modification)?
2. **What are the cancellation / abort paths?** If the user can initiate the success path, can they cancel mid-flight? Is the observable state after cancel specified?
3. **What are the boundary inputs?** Empty, zero, negative, max length, unicode, whitespace-only, duplicate, exactly-at-limit.
4. **What are the concurrency edges?** If two callers exercise the path simultaneously, is the observable outcome specified, or is implicit serialization being assumed?

For each gap found, either add a truth covering it OR add an explicit `Out of Scope` entry under `## Scope`. Silence is the bug; explicit out-of-scope is the fix. Don't manufacture coverage — if a path is genuinely impossible in this codebase, say so in `## Assumptions` with the supporting finding.

This probe replaces ad-hoc "did I think of everything?" with a checklist. Cost: ~2 minutes of planning. Value: catches the unspecified error paths that are the single largest source of "passes test but breaks on edge case" bugs.
