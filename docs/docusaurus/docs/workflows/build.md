---
sidebar_position: 5
title: /build
description: Goal-and-loop development — name an end state, draft a short task list and a handful of acceptance criteria, then loop build → judge until every criterion passes. The default path for "make this, and make it good" when there is no spec.
---

# /build

**Builds toward a goal without writing a spec first.** You name the end state, `/build` drafts 3–7 tasks and 3–6 acceptance criteria before writing a line, then works the whole task list and judges the result. Failing criteria become the next round's tasks.

The tasks are deliberately thin, and they are expected to change as the work teaches you something. That is the trade `/build` makes: less planning up front, more adapting as you go, with the judge holding the quality line at the end of each round.

It is the default path for *"make this, and make it good"* when a spec is neither required nor wanted.

```bash
# Claude Code
claude
> /build "landing page for my running brand — should feel as alive as Nike's"
> /build "port the admin screens to React, better than what we have, not just ported"
> /build "2000-word explainer on vector databases for non-engineers"

# Codex CLI
codex
> $build "landing page for my running brand — should feel as alive as Nike's"
```

## `/build` and `/spec` are peers

Neither is the escalation path for the other, and **size does not decide** which one you want.

| What the work is measured against | Command |
| --- | --- |
| A defect in behaviour that already worked | [`/fix`](/docs/workflows/fix) |
| An ordered list of tasks, approved before any code | [`/spec`](/docs/workflows/spec) |
| A clear goal, with the approach found while building | **`/build`** |
| Still vague who it serves or what done means | [`/prd`](/docs/workflows/prd), then one of the above |

A 30-screen framework migration can be `/build`. A 40-line change can be `/build`. A modest feature whose execution order needs agreeing first is `/spec`. Ask what the work is *measured against*: an approved task list, or a defined end state.

`/build` never hands large work off to `/spec` — it escalates internally instead (see [Parallel surfaces](#parallel-surfaces)).

## Three things carry it

1. **The goal** — one sentence naming the end state.
2. **The tasks** — 3–7 of them, a title and an objective each, expected to change as you learn.
3. **The judge** — a separate pass at the end of each round that rules the acceptance criteria from the finished artifact.

## Workflow

```text
Goal  →  Draft tasks + criteria  →  Approve  →  Round (build every task → judge)  →  Verify  →  Hand back
```

A **round** is one full pass over the task list plus **one** judge pass. Most runs converge in two or three. When the rounds are done, a verification pass checks what the criteria do not cover, and hand-back asks you to approve before anything is marked verified.

### Name the goal

One sentence for what the finished thing is. A bounded research budget — typically 5–15 tool calls, widening to ~30 for an unfamiliar domain — goes on what already exists locally that the build should match, and what specifically "good" means here.

A **reference** to sit beside is optional. Use one only when a real side-by-side comparison exists: a competitor's live page, a named author's published piece, the pre-migration version of a screen. It must be **named**, **obtainable** (fetched once, up front, with the re-obtain command recorded), and **comparable**. Many goals have none, and forcing one is worse than having none — a reference nobody can obtain is a comparison the judge invents, and an invented comparison passes everything.

### Draft tasks and criteria

**Tasks** are a title and a one-or-two-sentence objective. No file lists, no per-task definition of done — that is the upfront planning `/spec` charges for, and skipping it is the point.

**Criteria** are 3–6 one-sentence statements, judged once per round at the end. Each is decidable from the finished artifact by someone who did not build it, names the evidence that settles it, and can actually be settled during this run.

| Weak | Strong |
| --- | --- |
| The hero section is compelling. | Our hero and Nike's, screenshotted at 1440px and shown unlabelled, and a viewer told nothing picks ours. |
| Good error handling. | Every failure mode the module documents has a test asserting the user-facing message, and the suite passes. |
| ≥95% of rows carry a transcript, and the report discloses per-voice counts, and the table lists both architectures. | Three separate criteria. Split them. |

Two rules do most of the work: **pass/fail, never a score** (scores drift upward every round — "partial" and "mostly" are scores, and a criterion not fully met is a fail), and **one sentence each** (if it needs "and" three times, it is three criteria). At least one criterion is measurable whenever the goal has a measurable half — load time, bundle size, benchmark score, word count, pass rate.

A **Build Review** agent audits the tasks and criteria before the loop starts — a criterion you can decide by feel reads as perfectly clear to whoever wrote it. It runs on Claude Code and Codex, with an optional Codex companion for a second opinion, and is switchable in Console Settings.

### Approve

One gate. `/build` shows the tasks and criteria and waits, unless **Plan Approval** is off in Console Settings. The criteria are the contract; the tasks will change and everyone knows it.

### Round

**Build** every open task, in order. Add, split, or drop tasks as the work teaches you something — each change gets one line in the round log. Code tasks are written test-first, and a task is never ticked while its tests fail. Then, once every task is ticked, **judge**:

1. Resolve a running artifact, if any criterion rules on runtime behaviour — reuse a live server, start the dev server, or attempt a preview deploy, in that order. A criterion about what a user sees is never ruled from source.
2. Re-obtain the reference, if the Buildout names one.
3. Rule each acceptance criterion pass or fail with one line of evidence, read off the finished artifact — not off your reasoning about it, and not off your memory of what was hard.
4. Tick or untick each criterion, increment `Rounds:`, append one line to the round log.

The judge is **calibrated, not brutal**: a criterion whose evidence meets what it asks passes. Raising the bar mid-judge is what makes a goal-and-loop run slower than `/spec` for no gain in quality.

Failing criteria become the next round's tasks. A failing criterion is never a question for you.

:::note Waiting is not a round
If the only remaining work is blocked on something that will not finish inside the session — a multi-hour data collection, a third-party review, a credential someone else has to issue — `/build` stops and hands back with what is blocked and what unblocks it, rather than spending rounds on side work.
:::

### Verify

Once the rounds are done, a verification pass covers the axes acceptance criteria mostly do not: the full test suite, type checker, linter and build; a running artifact proven to be the current one; browser E2E over the user-facing paths; an independent **Changes Review** of the diff (with an optional Codex companion); documentation sync; and a final regression run.

It is scaled to what was actually built. A prose, design, or research artifact runs only the documentation question and the not-verified list, so the pass costs almost nothing — but anything that produced code gets the checks, the review, and the regression in full, whether or not it has a UI. Findings are fixed on the spot and never spend a round; only a criterion the fix materially changed gets re-judged.

The evidence is written into the Buildout as a `## Verification Record`, and hand-back refuses to mark anything verified without it.

### Hand back

After **three** judge passes with criteria still failing, `/build` stops and asks: one more round, relax the named criterion, or accept as-is. "One more round" is a **one-time** extension — four judge passes is the ceiling, after which the run hands back automatically with the unresolved criteria recorded.

The report names every criterion with the evidence that settled it, the rounds it took, how the task list changed along the way, anything deliberately left out, any criterion relaxed mid-run with its before and after, and an explicit list of what was **not** verified. Then it asks you to approve — `Status: VERIFIED` is written only on an explicit approval, never by the loop itself.

:::note There is no partial hand-back
Hand-back is reachable exactly three ways: every criterion passed, the round budget reached after a real judge pass, or work blocked on something outside the session that is named. An unticked task, an unjudged criterion, or a round cut short is not one of them — and running low on context is not a blocker, because the Buildout survives compaction and the run resumes from it.
:::

## The Buildout is a real file

`/build` writes `docs/plans/YYYY-MM-DD-<slug>.md` with `Type: Build` and registers it with the session — the same machinery `/spec` plans use. That buys four things:

- **It survives compaction.** After a context compaction the run resumes from the file, not from the conversation.
- **The statusline tracks tasks and rounds.** `Build: running-brand build ███░░ 3/5 r2`.
- **The Console shows it.** Buildouts get their own **Buildouts** section, and can be shared with teammates for annotation like any other Pilot plan.
- **The stop guard holds the loop open.** While the Buildout is registered and not `VERIFIED`, the session cannot quietly end at "good enough" — on both Claude Code and Codex. You never type `/goal`. The escape hatch is stopping twice within 60 seconds.

```markdown
# Running Brand Landing Buildout

Created: 2026-08-07
Status: PENDING
Approved: Yes
Rounds: 2
Type: Build

## Summary

**Goal:** a landing page that feels as alive as Nike's running campaign

**Reference:** nike.com/running campaign page — screenshot at 1440px

## Acceptance Criteria

- [x] Criterion 1: our hero and Nike's at 1440px, unlabelled, and a viewer picks ours
- [ ] Criterion 2: LCP under 2.0s on a throttled 4G profile

## Progress Tracking

- [x] Task 1: hero and motion
- [x] Task 2: type scale and colour system
- [ ] Task 3: responsive pass at 390px

## Implementation Tasks

### Task 1: Hero and motion

**Objective:** Build the hero with the motion treatment that carries the page.

## Round Log

- Round 2: closed flat hero typography (added task 3 once the phone layout broke). Judge: 1/2 pass.
```

The two checkbox lists have different jobs. `## Progress Tracking` carries the tasks, and that is what the statusline and Console count. `## Acceptance Criteria` is the judge's list, and stays unticked until a judge pass ticks it.

### Statusline phases

| Buildout state | Phase shown | Meaning |
| --- | --- | --- |
| `PENDING` + `Approved: No` | `goal` | Goal, tasks, and criteria being drafted |
| `PENDING` + `Approved: Yes` | `build` | Working the task list |
| `COMPLETE` | `judge` | Every task ticked; judge pass outstanding |
| `VERIFIED` | *(cleared)* | Handed back |

A hand-back does not always mean `VERIFIED`: a run that stops at the round-four ceiling with criteria unresolved, or one blocked on something outside the session, stays `PENDING` so it can be resumed from the file. A one-shot sentinel lets the session stop in those two cases.

## Sequential by default

One thread. No subagents for building or judging — those stay in the same conversation.

A subagent starts blind: it re-reads the files, re-derives context the thread already holds, reports a summary, and the summary gets read back. For judging work you just built, that is routinely several times the tokens of judging it yourself, spent to buy separation you can mostly recreate by judging from the artifact in a distinct pass. The loop's quality comes from the criteria, not from the org chart running it.

**Reviewers are the exception, and both run outside the loop:** Build Review before the first round, Changes Review after the last. Each looks at something the loop structurally cannot see — whether the criteria are decidable at all, and whether the code behind the artifact is sound. A single research agent while scoping is also allowed, once, at the start.

### Parallel surfaces

`/build` proposes parallel execution only when **all three** hold:

1. The work splits into **5+ distinct surfaces that each need their own build-judge loop** — not five tasks against one artifact.
2. Those surfaces can progress without waiting on each other.
3. Running them one after another would take hours, not minutes.

That is whole-project scale: a framework migration, an app rebuilt surface by surface. A landing page with six sections is one artifact. A long grind is still one thread.

On Claude Code, clearing that bar prompts for `/effort ultracode` — session-scoped, typed by you, requiring dynamic workflows in `/config`, and substantially more expensive than the sequential default. Declining is a first-class answer: sequential is the design, not the fallback. Codex has no ultracode equivalent and runs the surfaces one at a time, closing each surface's criteria before opening the next.

## Configurable toggles

`/build` honours the Console Settings `/spec` uses:

| Toggle | Group | Default | Effect when disabled |
| --- | --- | --- | --- |
| **Ask Questions** | Automation | On | The reference is chosen for you — `/build` takes the most useful candidate it can reach and says which. |
| **Plan Approval** | Automation | On | The approval gate on the drafted tasks and criteria is skipped; the loop starts immediately. |
| **Build Review** | Reviews | On | The tasks and criteria go unreviewed into the loop. |
| **Also review with Codex** (on Build Review) | Reviews | Off | No second-opinion Codex pass over the criteria. Needs the Claude Code Codex plugin. |
| **Verification Pass** | Automation | On | No checks, E2E, or regression before hand-back — the run is judged on its criteria alone, and the hand-back says so. |
| **Changes Review** | Reviews | On | For code builds, the diff is not reviewed at hand-back. |

With Ask Questions and Plan Approval off, `/build` runs goal → tasks and criteria → rounds → verify with no interaction until the final approval gate.

## Common issues

| Symptom | What it means | What to do |
| --- | --- | --- |
| The judge keeps passing weak work | The criteria are decidable by feel | Rewrite each to name the evidence that settles it. |
| The session will not stop | The stop guard is holding the loop, as designed | Let it run, or take a criterion to the round-budget question. Escape hatch: stop twice within 60s. |
| It stopped at three rounds with criteria failing | The round budget, working | Answer the question: one more round, relax the criterion, or accept as-is. |
| It handed back saying it was blocked | Remaining work needs something outside the session | Come back when the blocker clears; the Buildout stays `PENDING` and the run resumes from it. |
| The Buildout is missing from the Console | It is outside the scanned directories | It must live under `docs/plans/` (or a worktree's `docs/plans/`) and be registered. |

## When not to use `/build`

- **Something that used to work is broken** → [`/fix`](/docs/workflows/fix).
- **You want the approach written down and approved before any code** → [`/spec`](/docs/workflows/spec).
- **The idea is still vague about who it serves** → [`/prd`](/docs/workflows/prd) first.
- **A one-line change, a rename, a config tweak** → just do it; a Buildout costs more than the edit.
- **The result cannot be judged without data that will not arrive this session** → build it straight, or come back when the data lands.

## Portability

The method survives outside Pilot. `/build` can export a portable brief instead of running: the goal condition moves into the prompt's first line, the tasks and criteria travel verbatim, and the judging protocol is stated inline. You lose the enforcement — the Buildout file, the statusline, the stop guard — not the method.
