## Step 4: Build the Task List

Work every open task in `## Progress Tracking`, in order. When they are all ticked, go to Step 5 and judge. **Do not judge mid-pass** — judging a half-built artifact spends a round to learn what you already knew.

### 4.1 Work a task

For each `- [ ] Task N:`:

1. Read its `**Objective:**` under `## Implementation Tasks`.
2. Build it. Find the files now — that is the part `/build` deliberately did not plan.
3. Tick `- [x] Task N:` in `## Progress Tracking` the moment it is done, not at the end of the round.

Ordinary engineering discipline still applies inside the loop: the project's rules, TDD where there is code to test, and the least that works (`development-practices.md` → *Build the least that works*). The criteria raise the standard for the output; they do not license a mess behind it.

### 4.2 Tasks are allowed to change — that is the design

`/build` skips upfront planning precisely so the task list can absorb what you learn. When the work teaches you something:

- **Add a task** when you find real work the draft missed.
- **Split a task** that turned out to be two.
- **Drop a task** that turned out to be unnecessary, and say why.

Every change gets one line in `## Round Log`, and `## Progress Tracking` and `## Implementation Tasks` are updated in the same edit so they never disagree. A task list that ends the run looking nothing like the drafted one is a successful run, not a failed plan — as long as the criteria did not move.

⛔ **The criteria do not change here.** Only Step 5, and only out loud.

### 4.3 Tool discipline

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

### 4.4 When the work is blocked on something outside this session

If the only remaining work is waiting on a process that will not finish while you are here — a multi-hour data collection, a third-party review, a deploy queue, a credential someone else has to issue — **that is not a round.** Spinning up side work and calling it progress is how a three-round run becomes fourteen.

Stop and hand back:

1. Tick every task you genuinely finished.
2. Append one `## Round Log` line naming what is blocked and precisely what would unblock it.
3. Touch the hand-back sentinel so the stop guard lets the session pause:

   ```bash
   BUILD_SESS="${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
   mkdir -p "$HOME/.pilot/sessions/$BUILD_SESS" && touch "$HOME/.pilot/sessions/$BUILD_SESS/build-handback-pending"
   ```

4. Go to Step 6 and report — what is done, what is blocked, what unblocks it. Leave `Status: PENDING`; the run resumes when the user comes back with the thing it was waiting for.

### 4.5 Hand the round to the judge

Once every `- [ ] Task N:` is ticked, mark the round's build half done **before** judging:

1. Set `Status: COMPLETE` in the Buildout.
2. Register it:

   ```bash
   ~/.pilot/bin/pilot register-plan "<buildout_path>" "COMPLETE" 2>/dev/null || true
   ```

`COMPLETE` means *every task is ticked and the judge pass is outstanding* — the same meaning it carries in `/spec`, where it marks implementation done and verification pending. The statusline flips to `judge` for the duration of the pass, and the stop guard switches to demanding the judge run. Setting it only after judging succeeded would make the `judge` phase invisible and would tell the stop guard the opposite of the truth.

**Done when:** every task is ticked and `Status: COMPLETE` is registered — then Step 5. Or the run is blocked per 4.4 — then Step 6.
