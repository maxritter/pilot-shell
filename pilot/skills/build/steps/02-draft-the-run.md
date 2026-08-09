## Step 2: Draft the Tasks and Criteria

This is the artifact that matters. It is deliberately thin — `/build` exists because you do not want to plan the whole thing first.

### 2.1 Write 3–7 tasks

Each task is a **title and an objective**, and nothing else:

```markdown
### Task 2: Render the comparison table from the trial rows

**Objective:** Build the table that shows each system's pass rate side by side, generated
from the data rather than hand-written. It is the section a reader looks at first.
```

- **No `Files:`, no `Key Decisions:`, no per-task `Definition of Done:`.** Those are the upfront planning `/spec` charges for. Here you find the files while building.
- **Order them the way you would actually work.** Task order is the running order; there is no dependency syntax.
- **Cover the whole artifact, roughly.** Three to seven tasks that together produce something judgeable. Not a decomposition of every file you will touch.
- **They will change.** Adding, splitting, and dropping tasks mid-round is expected and logged (Step 4). Drafting them precisely now buys nothing.

If you cannot get the work under seven tasks without each one becoming vague, the goal is probably two goals. Say so and build the first.

### 2.2 Write 3–6 acceptance criteria

These are judged **once per round, at the end**, never worked one at a time. Each one:

- **Rules pass or fail, never a score.** Scores drift upward every round: "7/10" becomes "8/10" with no change to the work.
- **Is one sentence.** If it needs "and" three times, it is three criteria — split it.
- **Is decidable from the finished artifact**, by someone who did not build it.
- **Names the evidence that settles it**, so a lazy judge cannot pass it by default.
- **Can actually be settled during this run.** A criterion whose evidence depends on a process that will not finish in this session is not a criterion; it is a blocker. Rewrite it or drop it.

Include **at least one measurable criterion** when the goal has a measurable half — load time, bundle size, token cost, word count, pass rate, error rate. Taste plus a number beats taste alone.

| Weak | Strong |
|---|---|
| The hero section is compelling. | Our hero and Nike's, screenshotted at 1440px and shown unlabelled, and a viewer told nothing picks ours. |
| Good error handling. | Every failure mode the module documents has a test asserting the user-facing message, and the suite passes. |
| The writing is clear. | A reader new to the topic restates the core mechanism in one sentence after a single read. |
| ≥95% of rows carry a transcript, and the report discloses per-voice counts, and the table lists both architectures. | Three separate criteria. Split them. |

⛔ **Write these before building.** Criteria written after a first draft describe that draft — the standard quietly becomes whatever you happened to make.

### 2.3 Create the Buildout file

**Do this before any building** — the statusline and the Console pick it up immediately, and the stop guard starts holding the run open.

1. **Filename:** `docs/plans/YYYY-MM-DD-<slug>.md` — slug from the first 3–4 words of the goal (lowercase, hyphens). If this session is already running inside a worktree checkout, use the worktree path as the base directory. `/build` never creates a worktree itself.

2. **Author email** (best-effort, omit the line if it fails):

   ```bash
   ~/.pilot/bin/pilot status --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('email',''))" 2>/dev/null
   ```

<!-- CC-ONLY -->
3. **Agent:** `Claude Code` if `$CLAUDE_CODE_ENTRYPOINT` is set, otherwise `Codex`.
<!-- /CC-ONLY -->
<!-- CODEX-START
3. **Agent:** `Codex`.
CODEX-END -->

4. **Write the file:**

   ```markdown
   # [Name] Buildout

   Created: [Date]
   Author: [email if available]
   Agent: [Claude Code|Codex]
   Status: PENDING
   Approved: No
   Rounds: 0
   Worktree: [Yes|No]
   Type: Build

   ## Summary

   **Goal:** [one sentence — the end state]

   **Reference:** [named artifact] — re-obtain with `[exact command, URL, or path]`

   ## Acceptance Criteria

   - [ ] Criterion 1: [one sentence, decidable from the artifact, naming its evidence]
   - [ ] Criterion 2: ...
   - [ ] Criterion 3: ...

   ## Out of Scope

   - [anything the user named that this build is deliberately not doing, or omit the section]

   ## Progress Tracking

   - [ ] Task 1: [one-line summary]
   - [ ] Task 2: ...

   ## Implementation Tasks

   ### Task 1: [imperative title]

   **Objective:** [1–2 sentences — what this task produces and why.]

   ### Task 2: [imperative title]

   **Objective:** ...

   ## Round Log

   _No rounds yet._

   ## Changed Files

   _None yet._
   ```

   **Omit the `**Reference:**` line entirely when there is none** (Step 1.3). An empty or hand-waved reference is worse than no reference.

   `Type: Build` is what makes the statusline render the loop and the Console file it under **Buildouts**. `Status:` is a closed set — `PENDING` | `COMPLETE` | `VERIFIED`, bare keyword, no trailing prose. `Rounds:` starts at 0 and is incremented by the judge, never by hand.

   **The two checkbox lists have different jobs.** `## Progress Tracking` carries `- [ ] Task N:` lines — that is what the statusline and Console count. `## Acceptance Criteria` carries `- [ ] Criterion N:` lines — those are the judge's, and they stay unticked until a judge pass ticks them. Every task in `## Progress Tracking` has a matching `### Task N:` body under `## Implementation Tasks`.

   **`## Changed Files` starts empty.** Step 4 appends to it, Step 6 stages and diffs exactly it (see 4.3). It is absent from the Console's displayed-sections allowlist, so it stays off the rendered Buildout and any share link — leave it that way.

5. **Register it:**

   ```bash
   ~/.pilot/bin/pilot register-plan "<buildout_path>" "PENDING" 2>/dev/null || true
   ```

### 2.4 Have the criteria reviewed before they become the contract

You wrote these criteria, so you are the last one who can tell they are undecidable. This is the one pre-loop round-trip worth paying for.

**Gate the two reviewers independently** — the Console exposes them separately, so neither may depend on the other. Skip 2.4 only when `PILOT_BUILD_REVIEW_ENABLED` is `"false"` **and** `PILOT_CODEX_BUILD_REVIEW_ENABLED` is not `"true"`.

**Slug** = the Buildout filename minus the `YYYY-MM-DD-` prefix and `.md`.

<!-- CC-ONLY -->
> **Reviewer-launch protocol** (Step 6.5 reuses this; only its inputs differ)
>
> ```bash
> SESS_DIR="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
> mkdir -p "$SESS_DIR"; OUTPUT_PATH="$SESS_DIR/findings-<agent>-<slug>.json"; rm -f "$OUTPUT_PATH"
> ```
>
> Launch with `Agent(subagent_type=..., run_in_background=true, ...)`, passing the Buildout path, the agent's inputs, and `**Output path:** $OUTPUT_PATH`. Tell it to `Write` findings JSON there and to include the Buildout path as the `plan_file` field.
>
> ⛔ **Never `TaskOutput`** — poll:
> ```bash
> for i in $(seq 1 90); do [ -f "$OUTPUT_PATH" ] && echo "READY" && break; sleep 2; done
> ```
> Read once. `plan_file` must match this Buildout — a mismatch is another run's findings, so delete and relaunch. Not READY → relaunch once, synchronously.

**Native reviewer** — when `PILOT_BUILD_REVIEW_ENABLED` is not `"false"`: run the protocol with `subagent_type="build-review"`, inputs = the goal as the user stated it and the reference choice if one was made.

**Codex companion** — when `PILOT_CODEX_BUILD_REVIEW_ENABLED` is `"true"`, whether or not the native reviewer ran. Skip if `$SESS_DIR/codex-build-review-ran-<slug>.flag` exists (codex-once). Otherwise follow `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/codex-companion-protocol.md` with `PROMPT_TEMPLATE` = `build-review-codex.md`, `{{PLAN_PATH}}` = the Buildout, `{{PLAN_GOAL}}` = the goal sentence, `{{CONTEXT_FILES}}` = whatever the goal names as a reference or pattern.

⛔ **`task --prompt-file`, never `adversarial-review --base`.** A Buildout is gitignored, so a diff-scoped launch reviews an empty diff.

Launch Codex first so it overlaps, then collect the native reviewer. If the companion returns nothing after its one retry, continue without it and say so in 2.5.
<!-- /CC-ONLY -->
<!-- CODEX-START
Spawn the managed reviewer and wait:

```python
review = multi_agent_v1.spawn_agent(agent_type="build-review", message="""
    Plan file: <buildout-path>
    User request: <the goal as the user stated it>
    Clarifications: <the reference choice, if one was made>

    Audit the tasks and acceptance criteria before the build-judge loop starts.
    Return ONLY valid JSON matching the build-review schema.
    Include the Buildout path in the `plan_file` field.
""")
result = multi_agent_v1.wait_agent(targets=[review.agent_id], timeout_ms=600000)
```

Parse the final message as JSON; on a parse failure treat it as one `suggestion` and continue — do not relaunch. `plan_file` must match this Buildout; discard a mismatch and self-review instead.
CODEX-END -->

**Fix every `must_fix` and `should_fix` before 2.5**, using each finding's `suggested_fix` as the replacement wording; `suggestion` if quick. The user should see reviewed criteria, not the first draft.

### 2.5 Show the user what you drafted

Print the goal, the numbered tasks, and the numbered criteria in the conversation. It is the one thing worth twenty seconds of their attention before the loop starts. If a reviewer changed anything, say so in one line — which criteria moved, and why.

**Done when:** the Buildout file exists, is registered, every criterion states its pass condition, every task has an objective, the reviewers' blocking findings are closed, and the user has seen both lists.
