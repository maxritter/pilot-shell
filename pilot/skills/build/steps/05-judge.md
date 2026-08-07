## Step 5: Judge the Criteria

**One judge pass per round, after every task is ticked.** This is the whole quality mechanism; the rest of the workflow exists to make it possible.

### 5.1 Judge

1. **Re-obtain the reference**, if the Buildout names one, using the command recorded there. Recalling it is how the comparison drifts toward what you already made. If there is no reference, skip this — the criteria stand on their own.
2. **Look at the finished artifact.** For visual work, screenshot it at the viewport the criterion names; for prose, read the passage; for code, run the tests or the benchmark the criterion names. Where a reference exists, put both side by side with the labels stripped.
3. **Rule each criterion pass or fail** with one line of evidence you can point at right now.
4. **Judge from the artifact only.** Not from your build reasoning, not from your intentions, not from your memory of what was hard. The judge must not know how hard the builder tried.

**Calibrated, not brutal.** Pass a criterion whose evidence meets what it asks. Raising the bar mid-judge — deciding that what the criterion said is not quite enough after all — is what turns `/build` into something slower than `/spec` for no gain in quality. If a criterion was written too loosely, that is a lesson for the next run, not a licence to fail work that met it.

A verdict containing "should", "probably", or "close enough" is not a verdict — look again at the artifact and rule it.

⛔ **Rule every criterion, every pass.** A criterion that passed in round 1 and regresses in round 2 goes back to `- [ ]`. The file must show the truth, not the high-water mark.

### 5.2 Record the round

In one edit:

- Tick `- [x] Criterion N:` for each criterion that now passes; untick any that regressed.
- Increment `Rounds:`.
- Append one entry to `## Round Log`:

  ```markdown
  - Round 2: closed the accent axis and the interval table (added task 8, dropped task 5 — the
    loader already handled it). Judge: 4/5 pass. Failing: Criterion 3 — the comparison table
    still prints bare rates in two cells.
  ```

The file is the run's memory. After a compaction you resume from it, not from the conversation.

### 5.3 Decide what happens next

You arrive here with `Status: COMPLETE` (set at the end of Step 4). Each branch below owns the transition out of it — a judge pass that does not move the status leaves the file claiming the judge never ran.

**Every criterion passes** → go to Step 6, which sets `Status: VERIFIED`. Leave `COMPLETE` in place until then.

**Some criterion fails, and `Rounds:` is 1 or 2** → turn each failure into one or more tasks:

- Append them to `## Progress Tracking` as `- [ ] Task N:` and to `## Implementation Tasks` with an objective.
- Set `Status: PENDING` and register it — the next round has open tasks again, so `COMPLETE` would be a lie and the stop guard would demand a judge pass instead of the build:

  ```bash
  ~/.pilot/bin/pilot register-plan "<buildout_path>" "PENDING" 2>/dev/null || true
  ```

- Go back to Step 4 and work them.

A failing criterion is never a question for the user. It is the next round's tasks.

**Some criterion fails, and `Rounds:` is 3** → the budget is reached. Go to 5.4.

**Some criterion fails, and `Rounds:` is 4** → the ceiling. Do **not** ask again. Leave the failing criteria unticked and append a `## Round Log` line recording each one as unresolved with the reason it would not close. Then make the hand-back actually reachable — the run ends with the Buildout still unfinished, so it stays `PENDING`, and only the one-shot sentinel lets the session stop:

```bash
BUILD_SESS="${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
mkdir -p "$HOME/.pilot/sessions/$BUILD_SESS" && touch "$HOME/.pilot/sessions/$BUILD_SESS/build-handback-pending"
~/.pilot/bin/pilot register-plan "<buildout_path>" "PENDING" 2>/dev/null || true
```

Then go to Step 6 to hand back. ⛔ Without that sentinel the stop guard blocks the stop and reinjects the loop, which defeats the ceiling entirely — the one failure this budget exists to prevent.

### 5.4 The round budget — ask once, at three

Three judge passes is where a converging run has converged and a stuck run has revealed why. Stop and ask.

⛔ **Touch the hand-back sentinel first.** On Codex, `AskUserQuestion` is rewritten to plain-text numbered options, which means you have to end your turn to receive an answer — and for an approved `PENDING` Buildout the stop guard blocks exactly that, reinjecting you into the loop instead. Writing the sentinel is what makes this question reachable at all. On Claude Code it is a harmless no-op, so write it unconditionally rather than branching:

```bash
BUILD_SESS="${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
mkdir -p "$HOME/.pilot/sessions/$BUILD_SESS" && touch "$HOME/.pilot/sessions/$BUILD_SESS/build-handback-pending"
```

Then name the failing criteria, what you tried, and why each will not close — plainly, no hedging. Offer three options:

<!-- CC-ONLY -->
Ask with `AskUserQuestion`:
<!-- /CC-ONLY -->
<!-- CODEX-START
Ask with plain-text numbered options, then end your turn; the sentinel above lets the stop through. Treat the user's next message as their answer.
CODEX-END -->

| Option | What you do |
|---|---|
| **One more round** | Turn the failures into tasks, set `Status: PENDING` and register it, then go back to Step 4. This is a **one-time** extension. |
| **Relax a criterion** | Rewrite it in `## Acceptance Criteria` with the user's wording, note the change and its reason in `## Round Log`, then judge against the new wording. `Status:` stays `COMPLETE` — no tasks reopened. |
| **Accept and hand back** | Leave the failing criteria unticked, record the waiver and its reason in `## Round Log`, go to Step 6 (which sets `VERIFIED` on the user's acceptance). |

**"One more round" never repeats.** If the fourth judge pass still fails, 5.3's ceiling applies: hand back automatically, no second ask. A recurring question would rebuild the many-rounds-with-checkpoints shape this workflow exists to remove. Four judge passes is the ceiling; a user who wants more starts a new run.

⛔ **Lowering a criterion without saying so is the one failure mode this workflow exists to prevent.** Relaxing one is fine — in the file, with the user's agreement, and recorded.

### Status at a glance

Every path out of this step names its status, so the file never claims a state the run is not in:

| Situation | `Status:` | Sentinel | Next |
|---|---|---|---|
| Arrived from Step 4 | `COMPLETE` | — | judge |
| All criteria pass | `COMPLETE` → Step 6 sets `VERIFIED` | — | Step 6 |
| Fails, rounds 1–2 | `PENDING` (registered) | — | Step 4 |
| Fails, round 3 → one more round | `PENDING` (registered) | touched for the ask | Step 4 |
| Fails, round 3 → relax | `COMPLETE` | touched for the ask | re-judge |
| Fails, round 3 → accept | `COMPLETE` → Step 6 sets `VERIFIED` | touched for the ask | Step 6 |
| Fails, round 4 (ceiling) | `PENDING` (registered) | **touched** | Step 6 |

**Done when:** the status above matches the branch taken, and the run is either heading to Step 6 or back to Step 4.
