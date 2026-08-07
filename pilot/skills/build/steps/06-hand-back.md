## Step 6: Final Judge and Hand Back

### 6.1 One last blind pass

`Status: COMPLETE` means every criterion was ticked during a round. Before handing back, judge the **whole artifact** once more, cold:

- Re-obtain the bar one final time.
- Rule every criterion again, from the finished artifact only — not from the round log, and not from your memory of ticking them.
- A criterion that fails here goes back to `- [ ]`, `Status:` returns to `PENDING`, re-register it, and the loop resumes at Step 5. That is the system working, not a setback.

<!-- CC-ONLY -->
For a build whose artifact is **code**, this is also where Pilot's code-quality pass belongs, when the Console's Spec Workflow → Review Agents → Changes Review toggle is on: `git add` the build's own files, then launch the `changes-review` sub-agent with `run_in_background=true` and poll for its findings file. It rules on correctness and quality — axes your criteria mostly do not cover — so treat its `must_fix` and `should_fix` findings as gaps to close before hand-back, not as criteria. Skip it entirely for prose, design, and research artifacts.
<!-- /CC-ONLY -->
<!-- CODEX-START
For a build whose artifact is **code**, this is also where the native `changes-review` custom agent belongs when its toggle is enabled: stage the build's own files, run the review, and close its `must_fix` / `should_fix` findings before hand-back. Skip it entirely for prose, design, and research artifacts.
CODEX-END -->

### 6.2 Close the rubric

1. Set `Status: VERIFIED`.
2. Register it: `~/.pilot/bin/pilot register-plan "<rubric_path>" "VERIFIED" 2>/dev/null || true`

That clears the statusline and releases the stop guard. Do not set `VERIFIED` while any criterion is unticked.

### 6.3 Report

Lead with what now works, then the evidence:

- **Every criterion, with the one line of evidence that passed it.** Not "all criteria pass" — the evidence is the report.
- **Rounds it took**, and the gap each one closed.
- **Anything deliberately left out**, and why.
- **Any criterion that was renegotiated mid-loop**, with the before and after.
- **Where the artifact is** and the command to see it.

Then hand it to the user for final review. The loop clears the bar you set; it does not decide the work is finished.

---

## Exporting the brief

When the user wants this run in a fresh session, by a different agent, or on a machine without Pilot, hand back a portable brief instead of running it.

Without Pilot there is no rubric file and no stop guard, so the goal condition has to move into the prompt.

<!-- CC-ONLY -->
**Paste first** (native Claude Code command — installs a session-scoped Stop hook, so the session cannot end while the condition reads false; `/goal clear` releases it early):

```
/goal Every criterion below passes a blind judge, and the judge picks ours over BAR.
```

**Then paste:**
<!-- /CC-ONLY -->
<!-- CODEX-START
**Paste this brief.** Its first line is the goal condition — without Pilot's stop guard, that line is the only thing holding the loop open:
CODEX-END -->

```
Build GOAL.

Do not end your turn until every criterion below passes a blind judge.

The bar is BAR. Obtain the real thing first — HOW — and compare against it
directly, not against a description of it.

Judge every round against these, pass or fail, no scores:
1. ...
2. ...

Each round: build, then judge. The judge inspects the actual output rather than
a description of it, puts ours next to the bar with the labels stripped, rules
each criterion pass or fail with one line of evidence, and names the single
biggest remaining gap. That gap is the next round's only job.

Judge harshly. Praise is not useful. A criterion is failed until the evidence
passes it.

Do not stop on a round count. Stop when every criterion passes, then hand it
back for review.
```

The criteria block is the long part and earns it; keep the rest short. Leave out architecture, file layout, stack, and round counts unless the user demanded them — every extra instruction is one fewer decision the agent makes with the work actually in front of it.

## Common issues

**The session will not stop.** Pilot's stop guard is holding it because the rubric is registered and not `VERIFIED`. That is the loop working. If the criteria are genuinely unreachable, renegotiate them openly with the user (Step 5, non-convergence) rather than lowering them quietly. The user's escape hatch is stopping twice within 60 seconds.

**The rubric is not showing in the statusline or Console.** It must live under `docs/plans/` (or `<worktree base>/<slug>/docs/plans/`) and be registered — `pilot register-plan` prints a warning when the path is outside the scanned directories. Check `Type: Build` is present and each criterion is a top-level `- [ ] Criterion N:` line.

**The judge keeps passing weak work.** The criteria are decidable by feel. Rewrite each to name the evidence that settles it, then re-run the loop from the round you are on.

**The judge passed everything on round one.** The bar is too soft. Go back to Step 2 and pick a harder one; a bar that is cleared without building is not a bar.

## Examples

### A visual goal

User: "landing page for my running brand, athletic, green and dark, has to feel alive."

Bars offered: Nike's current running campaign page / On Running's homepage / Gymshark's product landing. User picks Nike.

Criteria (abridged): unlabelled hero A/B at 1440px and 390px; motion that still reads with `prefers-reduced-motion` set; type legible at arm's length on mobile; LCP under 2.0s on a throttled 4G profile; every interactive element reachable by keyboard.

Mode: sequential. Six sections of one page is one artifact, not six surfaces — the Step 4.3 threshold is not met, so parallelism never comes up.

### A writing goal

User: "a 2000-word explainer on vector databases for non-engineers."

Bars offered: a named Stripe engineering explainer / a named Julia Evans post / the Wikipedia article plus a comprehension test. User picks the Evans post.

Criteria (abridged): a reader new to the topic restates the core mechanism in one sentence after a single read; no undefined jargon; every analogy survives being pushed one step further; unlabelled A/B against three of her actual posts on which one a non-engineer finishes.

Mode: sequential. One artifact; the writer judges its own prose in a separate pass, from the page alone, with the Evans posts re-opened each round.

### A goal that clears the escalation bar

User: "we're moving the whole admin app off Angular to React — 30-odd screens, and I want them better than what we have, not just ported."

Bar: the existing Angular screens, screenshotted before any edit, plus the two competitor screens the user rates highest.

Threshold check: 30 screens, each needing its own build-judge loop; they do not block each other; sequential would run for hours. All three hold, so Step 4.3 applies.

Note what this example is **not**: a reason to hand the work to `/spec`. Thirty screens measured against a standard is `/build` at its largest, not `/spec` in disguise.
