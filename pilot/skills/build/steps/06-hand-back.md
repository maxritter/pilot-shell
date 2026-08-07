## Step 6: Hand Back

You arrive here three ways: every criterion passed (Step 5.3), the round budget or ceiling was reached (Step 5.3/5.4), or the work is blocked on something outside this session (Step 4.4). The report differs; the closing mechanics do not.

### 6.1 Code quality pass — code artifacts only

<!-- CC-ONLY -->
For a build whose artifact is **code**, this is where Pilot's code-quality pass belongs, when the Console's Spec Workflow → Review Agents → Changes Review toggle is on: `git add` the build's own files, then launch the `changes-review` sub-agent with `run_in_background=true` and poll for its findings file. It rules on correctness and quality — axes the acceptance criteria mostly do not cover — so treat its `must_fix` and `should_fix` findings as work to close before hand-back, not as criteria. Skip it entirely for prose, design, and research artifacts, and skip it on a blocked hand-back (4.4) where the code is half-built by design.
<!-- /CC-ONLY -->
<!-- CODEX-START
For a build whose artifact is **code**, this is where the native `changes-review` custom agent belongs when its toggle is enabled: stage the build's own files, run the review, and close its `must_fix` / `should_fix` findings before hand-back. Skip it entirely for prose, design, and research artifacts, and skip it on a blocked hand-back (4.4) where the code is half-built by design.
CODEX-END -->

If closing a finding changes the artifact materially, re-run the affected criteria from Step 5.1 before continuing — a fix is a change, and the criteria rule on what shipped.

### 6.2 Close the Buildout

**Every criterion passed, or the user accepted an unresolved one:**

1. Set `Status: VERIFIED`.
2. Register it: `~/.pilot/bin/pilot register-plan "<buildout_path>" "VERIFIED" 2>/dev/null || true`

That clears the statusline and releases the stop guard.

**Round-four ceiling reached with criteria still failing (5.3):** leave `Status: PENDING` and leave it registered, with the failing criteria unticked and their reasons in `## Round Log`. Do NOT set `VERIFIED` — nothing verified them. The `build-handback-pending` sentinel touched in 5.3 is what lets the session stop.

**Blocked on something outside this session (4.4):** leave `Status: PENDING` and leave it registered. The run is not finished — it is waiting, and the Buildout is how it resumes. The `build-handback-pending` sentinel you touched in Step 4.4 is what lets the session pause here.

⛔ **Never tick a criterion you did not judge**, and never set `VERIFIED` to make the statusline look tidy. An unresolved criterion recorded honestly in `## Round Log` is a good outcome; a ticked one that nothing verified is the failure this workflow exists to prevent.

### 6.3 Report

Lead with what now works, then the evidence:

- **Every criterion, with the one line of evidence that settled it.** Not "all criteria pass" — the evidence *is* the report. Failing ones get the same treatment: what fails, and why it would not close.
- **Rounds it took**, and what each one closed.
- **How the task list changed** — what you added, split, or dropped once the work taught you something. This is often the most useful paragraph for the reader.
- **Any criterion that was relaxed mid-run**, with the before and after.
- **Anything deliberately left out**, and why.
- **Where the artifact is** and the command to see it.

Then hand it to the user for final review. The loop clears the criteria you set; it does not decide the work is finished.

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

**The Buildout is not showing in the statusline or Console.** It must live under `docs/plans/` (or `<worktree base>/<slug>/docs/plans/`) and be registered — `pilot register-plan` prints a warning when the path is outside the scanned directories. Check `Type: Build` is present and that `## Progress Tracking` uses top-level `- [ ] Task N:` lines.

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
