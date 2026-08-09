## Step 4: Build the Task List

Work every open task in `## Progress Tracking`, in order. When they are all ticked, go to Step 5 and judge. **Do not judge mid-pass** — judging a half-built artifact spends a round to learn what you already knew.

### 4.1 Work a task

For each `- [ ] Task N:`:

1. Read its `**Objective:**` under `## Implementation Tasks`.
2. Build it. Find the files now — that is the part `/build` deliberately did not plan.
3. Append every path you created or modified to `## Changed Files` (4.2).
4. Tick `- [x] Task N:` in `## Progress Tracking` the moment it is done, not at the end of the round.

The project's rules apply in full inside the loop, and so does the least that works (`development-practices.md`). The criteria raise the standard for the output; they do not license a mess behind it.

**A task is not done while it is red.** Never tick a task whose tests fail or whose files carry open diagnostics.

### 4.2 Code tasks: test first

`testing.md` is the contract; the short form:

- **RED** — one minimal test for the behaviour the objective names, failing for that reason and not on a typo.
- **GREEN** — the simplest thing that passes. **REFACTOR** — with tests green.

Name the production change that would make the test fail before writing the assertion; if you cannot, it is a change detector — test the observable behaviour instead. Then run the mutation check: wrong constant, wrong branch, missing side effect, empty return, missing validation — each must fail something.

**Parsimony:** reuse the existing test class before adding one; ceiling is 1 unit + 1 functional class per production class; never one per method.

**Exempt:** prose, design, research, docs, config — say so in one line rather than inventing a test.

⛔ **No `Trivial:` escape here.** `/spec`'s version is auditable against a named covering test; a Buildout has no per-task DoD, so the claim would be unfalsifiable. Write the test.

### 4.3 Keep the Changed Files ledger current

Append every path you create or modify to `## Changed Files`, in the same edit that ticks the task. A path enters only when this run wrote to it, and Step 6 stages nothing outside it — so a file the user already had dirty can never be swept into the review or a commit. The conversation is not an inventory; compaction erases it.

### 4.4 Tasks are allowed to change — that is the design

`/build` skips upfront planning precisely so the task list can absorb what you learn. When the work teaches you something:

- **Add a task** when you find real work the draft missed.
- **Split a task** that turned out to be two.
- **Drop a task** that turned out to be unnecessary, and say why.

Every change gets one line in `## Round Log`, and `## Progress Tracking` and `## Implementation Tasks` are updated in the same edit so they never disagree. A task list that ends the run looking nothing like the drafted one is a successful run, not a failed plan — as long as the criteria did not move.

⛔ **The criteria do not change here.** Only Step 5, and only out loud.

⛔ **Dropping a task a criterion depends on is a criterion change.** Before dropping, ask whether any criterion's evidence needs that task. If so, removing it quietly lowers the bar — take it to Step 5.4 and let the user relax the criterion or keep the task.

### 4.5 Tool discipline

Loop pressure pushes toward batching everything into one giant call. It produces unreadable diffs, corrupted files, and orphaned processes. Inside the loop:

- **Use `Edit` / `Write` for every file change** — including the Buildout file itself. ⛔ Never patch a file with a `python3 - <<'PY' ... s.replace(...)` heredoc, `sed -i`, or any other string surgery. If `Edit` feels awkward, read the file first; that is the fix.
- **One purpose per `Bash` call.** Do not chain an edit, a formatter, a linter, a test run, and a render into a single command — when it fails you cannot tell which half broke.
- **Clean up what you start.** A background process you launched is yours to kill before the round ends.
- **One line of narration per task.** The round log is the record; the conversation is not the report. Save the writing for Step 6.

<!-- CC-ONLY -->
⛔ **No subagents inside the loop.** The one research agent allowed in this workflow was Step 1's, and it is spent.
<!-- /CC-ONLY -->
<!-- CODEX-START
⛔ **No delegated agents inside the loop.** The one research pass allowed in this workflow was Step 1's, and it is spent.
CODEX-END -->

### 4.6 When the work is blocked on something outside this session

If the only remaining work is waiting on a process that will not finish while you are here — a multi-hour data collection, a third-party review, a deploy queue, a credential someone else has to issue — **that is not a round.** Spinning up side work and calling it progress is how a three-round run becomes fourteen.

⛔ **Context pressure is not one of these.** The test is what the run waits on: something in the world (legitimate) or its own context window (not). Everything needed is in the Buildout and compaction is expected — re-read it and keep working. Never tick a task, pass a criterion, or reach Step 7 because the window is filling up.

Stop and hand back:

1. Tick every task you genuinely finished.
2. Append one `## Round Log` line naming what is blocked and precisely what would unblock it.
3. Touch the hand-back sentinel so the stop guard lets the session pause:

   ```bash
   BUILD_SESS="${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
   mkdir -p "$HOME/.pilot/sessions/$BUILD_SESS" && touch "$HOME/.pilot/sessions/$BUILD_SESS/build-handback-pending"
   ```

4. Go to **Step 7** and report — what is done, what is blocked, what unblocks it. Skip Step 6: the artifact is half-built by design, so there is nothing coherent to verify. Leave `Status: PENDING`; the run resumes when the user comes back with the thing it was waiting for.

### 4.7 Hand the round to the judge

Once every `- [ ] Task N:` is ticked, mark the round's build half done **before** judging:

1. Set `Status: COMPLETE` in the Buildout.
2. Register it:

   ```bash
   ~/.pilot/bin/pilot register-plan "<buildout_path>" "COMPLETE" 2>/dev/null || true
   ```

`COMPLETE` means *every task is ticked and the judge pass is outstanding* — the same meaning it carries in `/spec`, where it marks implementation done and verification pending. The statusline flips to `judge` for the duration of the pass, and the stop guard switches to demanding the judge run. Setting it only after judging succeeded would make the `judge` phase invisible and would tell the stop guard the opposite of the truth.

**Done when:** every task is ticked and `Status: COMPLETE` is registered — then Step 5. Or the run is blocked per 4.6 — then Step 7.
