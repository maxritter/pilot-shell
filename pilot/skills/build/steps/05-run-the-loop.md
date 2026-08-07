## Step 5: Run the Loop

Each round is four moves. Do all four, in order, every round.

### 5.1 Build

Close **the single gap named last round**. One gap, not a list. On round 1 the gap is "nothing exists yet" — build the first honest attempt at the whole artifact, not a scaffold.

Ordinary engineering discipline still applies inside the loop: the project's rules, TDD where there is code to test, and the least that works (`development-practices.md` → *Build the least that works*). The rubric raises the standard for the output; it does not license a mess behind it.

### 5.2 Judge

**A separate pass, after the build is written out — never while writing it.**

1. **Re-obtain the bar** using the command recorded in the rubric. Recalling it is how the comparison drifts toward what you already made.
2. **Put both artifacts side by side with the labels stripped.** For visual work that means two screenshots at the same viewport; for prose, two passages of the same length; for code, both implementations against the same test or benchmark.
3. **Rule each criterion pass or fail** with one line of evidence you can point at right now. **Default to fail.**
4. **Judge from the artifact only.** Do not consult your build reasoning, your intentions, or your memory of what was hard. The judge must not know how hard the builder tried.

Judge harshly; praise is information-free. A verdict containing "should", "probably", or "close enough" is not a verdict — rejudge from the artifact.

⛔ **No subagents inside the loop.** The one research agent allowed in this workflow was Step 1's, and it is spent.

### 5.3 Update the rubric file

Every round, in the same edit:

- Tick `- [x] Criterion N:` for each criterion that now passes; untick any that regressed. A criterion that passed in round 2 and fails in round 4 goes back to `- [ ]` — the statusline must show the truth, not the high-water mark.
- Increment `Rounds:`.
- Append one line to `## Round Log`:

  ```markdown
  - Round 3: closed <gap>. Passing 5/7. Next gap: <one sentence>.
  ```

The file is the loop's memory. After a compaction you resume from it, not from the conversation.

### 5.4 Name the single biggest remaining gap

One sentence. Feed it into 5.1 and go again.

A list lets the next round cherry-pick the cheap ones and call it progress. If two gaps are genuinely tied, pick the one a viewer would notice first.

---

### Exiting

**Exit on the criteria, never on a round count.** When every criterion passes on a judge pass that re-obtained the bar:

1. Set `Status: COMPLETE` in the rubric.
2. Register it: `~/.pilot/bin/pilot register-plan "<rubric_path>" "COMPLETE" 2>/dev/null || true`
3. Go to Step 6 — a final blind judge pass, then hand back.

### When the loop is not converging

Three rounds where the same criterion fails and the gap description has not changed means the criterion is unreachable as written, not that the fourth attempt is the charm. Stop and say so plainly: name the criterion, what you tried, and why it will not close. Then ask the user to either relax that criterion or change the bar — **out loud, in the rubric**, never by quietly lowering it.

Lowering a criterion without saying so is the one failure mode this workflow exists to prevent.

### Runaway guard

Pilot's stop guard blocks a stop up to 30 consecutive times, then forces an `AskUserQuestion` about how to proceed. If you hit that escalation you are in the non-convergence case above — answer it honestly rather than starting another round.

**Done when:** every criterion is ticked, `Rounds:` reflects the real count, and `Status: COMPLETE` is registered.
