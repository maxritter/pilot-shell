## Step 7: Hand Back

### 7.1 Check you are allowed to be here

Name which of the three arrivals applies before anything else: **Complete** (every criterion ticked by a judge pass), **Budget** (a real judge pass ran and `Rounds:` hit the budget at 5.4 or the ceiling at 5.3), or **Blocked** (4.6's external blocker, named).

⛔ **None of the three holds → you are not at hand-back.** An unticked task, an unjudged criterion, or a round that stopped early is Step 4. There is no fourth arrival and no partial one.

### 7.2 Close the Buildout

**Ceiling reached with criteria still failing (5.3):** leave `Status: PENDING`, registered, with the failing criteria unticked and their reasons in `## Round Log`. Do NOT set `VERIFIED` — nothing verified them. The `build-handback-pending` sentinel touched in 5.3 lets the session stop. Report (7.3) and finish; there is no gate to run.

**Blocked outside this session (4.6):** leave `Status: PENDING`, registered. The run is waiting, not finished, and the Buildout is how it resumes. The sentinel touched in 4.6 lets the session pause. Report and finish.

**Complete, or the user accepted an unresolved criterion at 5.4:** report (7.3), then run the gate (7.4). `VERIFIED` is written only after the user approves.

⛔ **Never tick a criterion you did not judge**, and never set `VERIFIED` to tidy the statusline. An unresolved criterion recorded honestly is a good outcome; a ticked one nothing verified is the failure this workflow exists to prevent.

### 7.3 Report

Lead with what now works, then the evidence:

- **Every criterion, with the one line of evidence that settled it.** Not "all criteria pass" — the evidence *is* the report. Failing ones get the same treatment: what fails, and why it would not close.
- **Rounds it took**, and what each one closed.
- **How the task list changed** — added, split, dropped. Often the most useful paragraph for the reader.
- **Any criterion relaxed mid-run**, with the before and after.
- **From Step 6:** the checks that ran, the live-target tier reached, the reviewer findings closed, docs touched or "no doc impact", and the `## Not Verified` list verbatim.
- **Where the artifact is** and the command to see it.

### 7.4 The approval gate

The loop clears the criteria you set; it does not decide the work is finished. Ask, and wait.

**State what was not verified in the question itself.** If Step 6 was skipped or left `## Not Verified` rows, name them there — approving a run whose evidence was switched off has to be a decision the user makes knowingly.

```
AskUserQuestion(
  question="<one-line summary>. <what was not verified, or 'everything checked'>. Approve?",
  options=["Approve — mark the Buildout verified", "Issues found — I'll describe them"]
)
```

**When you cannot render that form** — on Codex, or as a Claude Code subagent running this Buildout as an orchestration lane — read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/agent-gate-protocol.md` and follow it, supplying `GATE_NAME` = `Buildout hand-back`, `OPTIONS` = the two above, `SENTINEL_PATH` = `build-handback-pending`. Without that sentinel an approved `COMPLETE` Buildout blocks the stop and the gate is unreachable:

```bash
BUILD_SESS="${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
mkdir -p "$HOME/.pilot/sessions/$BUILD_SESS" && touch "$HOME/.pilot/sessions/$BUILD_SESS/build-handback-pending"
```

⛔ Never mark the Buildout verified yourself because the form was unavailable.

**Only these count as approval:** `Approve`, `approve`, `lgtm`, `looks good`. A bare `continue` or `proceed` is a resume nudge and does not qualify.

**Anything else is issues to fix** — a bug report, a screenshot, free text. Fix them, then ⛔ **go back through Step 6 before asking again.** The checks, review, doc pass, regression, and live target were all measured against the pre-fix build, so re-run what the profile calls for, re-judge any criterion the fix touched (5.1), refresh `## Verification Record`, and only then re-ask. Re-asking on stale evidence is how the gate becomes a rubber stamp.

**Already approved at 5.4?** *Accept and hand back* at the round-budget question **is** this gate's approval — record it as such and do not ask twice, or round three silently becomes a fourth interaction point.

Before writing `VERIFIED`, all three must be true:

1. `## Verification Record` exists in the Buildout (written by Step 6.9), or Step 6 was skipped and `## Not Verified` says why.
2. `## Not Verified` exists — "None" is a valid entry, an absent section is not.
3. The qualifying approval reply is recorded verbatim in the Buildout, with which gate produced it (7.4 or 5.4).

Any one missing → you are not finished.

⛔ **On a `Worktree: Yes` run, do 7.6 FIRST.** `VERIFIED` clears the statusline and releases the stop guard, so writing it before the merge lands means a failed sync or a post-merge regression leaves the Buildout claiming success with nothing holding the session open to fix it. Integration is part of being done, not a step after it.

Then:

1. Set `Status: VERIFIED`.
2. `~/.pilot/bin/pilot register-plan "<buildout_path>" "VERIFIED" $LANE_FLAG 2>/dev/null || true`

That clears the statusline and releases the stop guard.

### 7.6 Merge back — `Worktree: Yes` only (runs BEFORE 7.5's status write)

The run owns the checkout it created, so it owns putting the work back. Skip this entirely when the header says `Worktree: No`.

1. **If `docs/builds/` is gitignored, copy the Buildout to the project root first** — otherwise the squash lands the work with no record of the run that produced it.
2. Show the user what will merge (`~/.pilot/bin/pilot worktree diff --json <slug> $LANE_FLAG`) and ask: **Squash merge** · **Keep the worktree, merge later** · **Discard**. This rides along with the 7.4 approval — it is not a fourth interaction point.
3. On squash, one Bash call, chained, so a failed sync can never be followed by a cleanup that deletes the work:

```bash
~/.pilot/bin/pilot worktree sync --json <slug> $LANE_FLAG && \
  PROJECT_ROOT=$(~/.pilot/bin/pilot worktree cleanup --force --json <slug> $LANE_FLAG | jq -r '.project_root') && \
  cd "$PROJECT_ROOT"
```

⛔ Never split sync, cleanup, and `cd` across Bash calls — a compaction between them loses the thread mid-merge.

**Exit codes.** `0` clean · `1` nothing landed · **`2` the squash landed but the base checkout's own uncommitted work could not be restored** and is in `git stash list`. The chain stops on 2 by itself, leaving the worktree in place deliberately. Do NOT re-run cleanup: surface the JSON's `stash_warning` and the `git stash pop` recovery first. `success: true` is still correct — the merge landed; only the unrelated local work is stranded.

**Lane contention.** Sync serializes on a repo-wide lock. A failure naming lane contention means a sibling held it past the timeout and **nothing was changed** — retry once it finishes.

4. **After a successful merge, re-run Step 6's checks on the merged base branch.** The base may have moved since the worktree forked, and criteria that passed in isolation can fail on integration. A criterion that breaks here goes back to `- [ ]` and the run is not verified.

⛔ **Any failure in this step leaves the Buildout `PENDING` — never `VERIFIED`.** A sync that could not land, a `cleanup` refused for unmerged commits, a criterion that regressed on the merged base: in each case keep `Status: PENDING`, re-register it, say what failed and what it needs, and do NOT continue to 7.5. Registering `VERIFIED` releases the stop guard, so doing it on a failed integration ends the session with the work unmerged and the file claiming otherwise.

**Only once the merge has landed and the merged-base checks are green** do you continue to 7.5 and write `Status: VERIFIED`.

---

## Exporting the run

When the user wants this run in a fresh session, by a different agent, or on a machine without Pilot, hand back a portable brief instead of running it.

Without Pilot there is no Buildout file and no stop guard, so the goal condition has to move into the prompt.

<!-- CC-ONLY -->
**Paste first** (native Claude Code command — installs a session-scoped Stop hook, so the session cannot end while the condition reads false; `/goal clear` releases it early):

```
/goal Every acceptance criterion below passes a judge reading the finished artifact.
```

**Then paste:**
<!-- /CC-ONLY -->
<!-- CODEX-START
**Paste this brief.** Its first line is the goal condition — without Pilot's stop guard, that line is the only thing holding the run open:
CODEX-END -->

```
Build GOAL.

Work in rounds. A round is: do every open task, then judge.

Tasks to start from — add, split, or drop them as the work teaches you something:
1. ...
2. ...

Acceptance criteria, judged only at the end of a round, pass or fail, no scores:
1. ...
2. ...

Judge from the finished artifact, not from your reasoning about it or your memory of
what was hard. Rule each criterion with one line of evidence. Pass a criterion whose
evidence meets what it asks; do not raise the bar mid-judge. Any criterion that fails
becomes a task in the next round.

Do not judge until every task is done. Do not stop while a criterion is unjudged.
After three rounds, stop and tell me what will not close instead of starting a fourth.
```

Add the reference and its re-obtain command only if the run has one. The criteria block is the long part and earns it; keep the rest short. Leave out architecture, file layout, and stack unless the user demanded them — every extra instruction is one fewer decision the agent makes with the work actually in front of it.

## Common issues

**The session will not stop.** Pilot's stop guard is holding it because the Buildout is registered and not `VERIFIED`. That is the loop working. If a criterion genuinely will not close, take it to the user at Step 5.4 rather than lowering it quietly. The user's escape hatch is stopping twice within 60 seconds.

**The Buildout is not showing in the statusline or Console.** It must live under the project root's `docs/builds/` (`docs/plans/` still works for Buildouts written before the split) and be registered — `pilot register-plan` prints a warning when the path is outside the scanned directories. Check `Type: Build` is present and that `## Progress Tracking` uses top-level `- [ ] Task N:` lines. A Buildout written inside a worktree checkout is filtered out by design; move it to the project root and re-register.

**The judge keeps passing weak work.** The criteria are decidable by feel. Rewrite them to name the evidence that settles them (Step 2.2), then judge again from the round you are on.

**The run is on round 4 and nothing is converging.** It should already have stopped at Step 5.4. If it did not, stop now and report — the criteria were written against something this run cannot reach.

## Examples

### A visual goal

User: "landing page for my running brand, athletic, green and dark, has to feel alive."

Reference offered and picked: Nike's current running campaign page (a genuine A/B — both are landing pages, both screenshottable at 1440px).

Tasks (drafted): hero and motion · type scale and colour system · product section · responsive pass at 390px · accessibility pass.

Criteria (abridged): unlabelled hero A/B at 1440px and 390px, a viewer picks ours; motion still reads with `prefers-reduced-motion` set; LCP under 2.0s on a throttled 4G profile; every interactive element reachable by keyboard.

Round 1 built all five tasks and judged 2/4. Round 2 closed the motion and LCP criteria (splitting the responsive task once the hero turned out to need its own breakpoint) and judged 4/4. Two rounds, handed back.

### A writing goal

User: "a 2000-word explainer on vector databases for non-engineers."

Reference offered and picked: a named Julia Evans post.

Tasks: the opening · the core mechanism · the analogy set · the worked example · the ending.

Criteria (abridged): a reader new to the topic restates the core mechanism in one sentence after a single read; no undefined jargon; every analogy survives being pushed one step further; unlabelled A/B against three of her actual posts on which one a non-engineer finishes.

Mode: sequential. One artifact; the writer judges its own prose in a separate pass, from the page alone, with the Evans posts re-opened each round.

### A goal with no reference

User: "close the three measurement gaps in our eval — grade the cascade on speech, add an accent axis, make multi-turn a real measurement."

No reference: the nearest published benchmark is a paper, not something our report can sit beside and be picked over. Named none, said so in one line, and let the criteria carry the standard.

Criteria were written to be settleable **from data this run would actually produce** — the run's own results file, not a collection job scheduled to finish hours later. The gap that needed a long external run became a task with an explicit blocked hand-back (Step 4.4) rather than a criterion, so the run reported honestly at the point it ran out of things it could do, instead of spending rounds waiting.
