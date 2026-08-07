---
sidebar_position: 5
title: /build
description: Goal-and-loop development — set a named bar, write pass/fail criteria before building, then loop build → judge until every criterion clears. The default path for "make this, and make it good".
---

# /build

**Builds to a standard instead of to completion.** You name something real for the work to beat, `/build` turns that into 5–9 pass/fail criteria before writing a line, and then loops — build, judge, close one gap, judge again — until every criterion passes a blind comparison against the bar.

It is the default path for *"make this, and make it good"* when there is no spec.

```bash
# Claude Code
claude
> /build "landing page for my running brand — has to feel as alive as Nike's"
> /build "port the admin screens to React, better than what we have, not just ported"
> /build "2000-word explainer on vector databases for non-engineers"

# Codex CLI
codex
> $build "landing page for my running brand — has to feel as alive as Nike's"
```

## `/build` and `/spec` are peers

Neither is the escalation path for the other, and **size does not decide** which one you want.

| What the work is measured against | Command |
| --- | --- |
| A defect in behaviour that already worked | [`/fix`](/docs/workflows/fix) |
| An ordered list of tasks, approved before any code | [`/spec`](/docs/workflows/spec) |
| A standard — a named bar the result has to clear | **`/build`** |
| Still vague who it serves or what done means | [`/prd`](/docs/workflows/prd), then one of the above |

A 30-screen framework migration can be `/build`. A 40-line change with an exacting bar can be `/build`. A modest feature whose execution order needs agreeing first is `/spec`. Ask what the work is *measured against*: a task list, or a standard.

`/build` never hands large work off to `/spec` — it escalates internally instead (see [Parallel surfaces](#parallel-surfaces)).

## Three things carry it

1. **The bar** — a real, named, obtainable artifact the work is compared against. Not a category. "Stripe's pricing page" works; "award-winning SaaS sites" does not, because a category cannot be fetched, so the judge invents the comparison and passes everything.
2. **The criteria** — 5–9 pass/fail statements, written *before* any building. Criteria written after a first draft describe that draft.
3. **The blind judge** — each round re-obtains the bar, strips the labels, and rules every criterion against evidence, defaulting to fail.

## Workflow

```text
Scope & research  →  Set the bar  →  Write criteria  →  Approve  →  Loop  →  Hand back
```

### Scope & research

A bounded budget — typically 5–15 tool calls, widening to ~30 for an unfamiliar domain — spent on exactly three things: confirming the bar is obtainable (open it, run it, screenshot it), learning what *specifically* makes it good, and reading what already exists locally that the build should match. Research that does not change a criterion is waste.

### Set the bar

If you named a reference, `/build` uses it. If not, it offers 2–3 candidates and waits for your pick — it never proceeds on a bar it chose alone. The bar must be **named**, **obtainable**, and **comparable** (you can picture the A/B). For a rewrite, the "before" is captured *before* any edit, because once you start editing the old version stops being obtainable.

The re-obtain command is written into the rubric so later rounds cannot drift toward "whatever we already made".

### Write criteria

5–9 statements, each shaped as **what is compared → how the judge obtains it → what passing looks like**.

| Weak | Strong |
| --- | --- |
| The hero section is compelling. | Our hero and Nike's, both screenshotted at 1440px and shown unlabelled: a viewer told nothing picks ours. |
| Good error handling. | Every failure mode the module documents has a test asserting the user-facing message, and the suite passes. |
| The writing is clear. | A reader new to the topic restates the core mechanism in one sentence after a single read. |

Two rules do most of the work: **pass/fail, never a score** (scores drift upward every round — "7/10" becomes "8/10" with no change to the work), and **resolve to "ours wins", never to "you cannot tell"** (a criterion phrased as *indistinguishable from the bar* passes on a tie, and a tie is the most common place the loop stops early).

At least one criterion is measurable whenever the goal has a measurable half — load time, bundle size, benchmark score, word count, pass rate.

### Approve

One gate. `/build` shows the numbered criteria and waits, unless **Plan Approval** is off in Console Settings. That is the only mid-flow question — a failing criterion is never a decision point, it is the next round's job.

### Loop

Four moves per round:

1. **Build** — close the single gap named last round. One gap, not a list.
2. **Judge** — a separate pass, after the build is written out. Re-obtain the bar, put both artifacts side by side with the labels stripped, and rule each criterion pass or fail with one line of evidence. **Default to fail.**
3. **Record** — tick or untick each criterion, increment `Rounds:`, append one line to the round log. A criterion that passed in round 2 and regressed in round 4 goes back to unticked; the statusline shows the truth, not the high-water mark.
4. **Name the single biggest remaining gap** in one sentence, and feed it into the next round.

The exit is the criteria, never a round count. "Three rounds is probably enough" is how this degrades into an ordinary build.

### Hand back

One final blind pass over the finished artifact, then a report: every criterion with the evidence that passed it, how many rounds it took, anything deliberately left out, and any criterion renegotiated mid-loop with its before and after. The loop clears the bar you set; it does not decide the work is finished.

## The rubric is a real file

`/build` writes `docs/plans/YYYY-MM-DD-<slug>.md` with `Type: Build` and registers it with the session — the same machinery `/spec` plans use. That buys four things:

- **It survives compaction.** After a context compaction the loop resumes from the file, not from the conversation.
- **The statusline is the loop counter.** `Build: running-brand build [loop] ███░░ 3/5 r2` — criteria passed, total, and round.
- **The Console shows it.** It appears in **Specifications** with a `Build` badge, criteria as the progress checklist, and the round log as a section. It can be shared with teammates for annotation like any other Pilot plan.
- **The stop guard is the goal condition.** While the rubric is registered and not `VERIFIED`, the session cannot quietly end at "good enough" — on both Claude Code and Codex. You never type `/goal`; the enforcement is built in. The escape hatch is stopping twice within 60 seconds.

```markdown
# Running Brand Landing Build Rubric

Created: 2026-08-07
Status: PENDING
Approved: Yes
Rounds: 2
Type: Build

## Summary

**Goal:** landing page that feels as alive as Nike's running campaign

**Bar:** nike.com/running campaign page

**Re-obtain the bar:** screenshot https://www.nike.com/running at 1440px

## Criteria

- [x] Criterion 1: our hero and Nike's, both at 1440px, unlabelled — a viewer picks ours
- [x] Criterion 2: motion still reads with `prefers-reduced-motion` set
- [ ] Criterion 3: LCP under 2.0s on a throttled 4G profile

## Round Log

- Round 2: closed flat hero typography. Passing 2/3. Next gap: hero image is 1.4MB unoptimised.
```

### Statusline phases

| Rubric state | Phase shown | Meaning |
| --- | --- | --- |
| `PENDING` + `Approved: No` | `rubric` | Bar and criteria being written |
| `PENDING` + `Approved: Yes` | `loop` | Build → judge rounds running |
| `COMPLETE` | `judge` | Every criterion ticked; final blind pass outstanding |
| `VERIFIED` | *(cleared)* | Handed back |

## Sequential by default

One thread, no subagents. Build, judge, close the gap, judge again — all in the same conversation.

A subagent starts blind: it re-reads the files, re-derives context the thread already holds, reports a summary, and the summary gets read back. For judging work you just built, that is routinely several times the tokens of judging it yourself, spent to buy separation you can mostly recreate by judging from the artifact in a distinct pass. The loop's quality comes from the criteria, not from the org chart running it.

One exception: a single research agent during scope & research, when the sweep is genuinely wide. One, at the start only, never inside the loop.

### Parallel surfaces

`/build` proposes parallel execution only when **all three** hold:

1. The work splits into **5+ distinct surfaces that each need their own build-judge loop** — not five sections of one artifact.
2. Those surfaces can progress without waiting on each other.
3. Running them one after another would take hours, not minutes.

That is whole-project scale: a framework migration, an app rebuilt surface by surface. A landing page with six sections is one artifact. A long grind is still one thread.

On Claude Code, clearing that bar prompts for `/effort ultracode` — session-scoped, typed by you, requiring dynamic workflows in `/config`, and substantially more expensive than the sequential default. Declining is a first-class answer: sequential is the design, not the fallback. Codex has no ultracode equivalent and runs the surfaces one at a time, closing each surface's criteria before opening the next.

## Configurable toggles

`/build` honours the Console Settings `/spec` uses:

| Toggle | Default | Effect when disabled |
| --- | --- | --- |
| **Ask Questions** | On | The bar is chosen for you — `/build` takes the hardest candidate it can reach and says which. |
| **Plan Approval** | On | The criteria approval gate is skipped; the loop starts immediately. |
| **Changes Review** | On | For code builds, the changes review does not audit the artifact at hand-back. |

With both question toggles off, `/build` runs bar → criteria → loop → hand back with no interaction at all.

## Common issues

| Symptom | What it means | What to do |
| --- | --- | --- |
| Everything passed on round one | The bar is too soft | Pick a harder one. A bar cleared without building is not a bar. |
| The judge keeps passing weak work | The criteria are decidable by feel | Rewrite each to name the evidence that settles it. |
| The session will not stop | The stop guard is holding the loop, as designed | Let it run, or renegotiate the criteria out loud. Escape hatch: stop twice within 60s. |
| Same criterion fails three rounds running | Unreachable as written, not a fourth-attempt problem | `/build` says so and asks you to relax the criterion or change the bar — never lowers it quietly. |
| The rubric is missing from the Console | It is outside the scanned directories | It must live under `docs/plans/` (or a worktree's `docs/plans/`) and be registered. |

## When not to use `/build`

- **Something that used to work is broken** → [`/fix`](/docs/workflows/fix).
- **You want the approach written down and approved before any code** → [`/spec`](/docs/workflows/spec).
- **The idea is still vague about who it serves** → [`/prd`](/docs/workflows/prd) first.
- **A one-line change, a rename, a config tweak** → just do it; a rubric costs more than the edit.
- **No comparable reference and no measurable half** → there is nothing to loop against.

## Portability

The method survives outside Pilot. `/build` can export a portable brief instead of running: the goal condition moves into the prompt's first line, the criteria block travels verbatim, and the judging protocol is stated inline. You lose the enforcement — the rubric file, the statusline, the stop guard — not the method.
