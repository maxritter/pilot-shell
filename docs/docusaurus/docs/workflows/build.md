---
sidebar_position: 5
title: /build
description: Autonomous goal-and-loop development — name an end state and walk away. /build drafts a short task list and a handful of acceptance criteria, then loops build → judge until every criterion passes, verifies the result on every layer, and hands back. No approval gate, no check-ins.
---

# /build

**Builds toward a goal without writing a spec first, and without checking in.** You name the end state, `/build` drafts 3–7 tasks and 3–6 acceptance criteria before writing a line, then works the whole task list and judges the result. Failing criteria become the next round's tasks.

The tasks are deliberately thin, and they are expected to change as the work teaches you something. That is the trade `/build` makes: less planning up front, more adapting as you go, with the judge holding the quality line at the end of each round.

It is the default path for *"make this, and make it good"* when a spec is neither required nor wanted.

## It runs on its own

`/build` asks the user for things in exactly one place — **before any work starts** — and then not again. After that it is autonomous to the hand-back: no approval of the drafted lists, no round-budget check-in, no sign-off before the Buildout is marked verified.

The front of the run is where the attention goes instead. A vague goal gets **grilled** until its acceptance criteria can actually be written; a sharp one passes through in silence. Paying there is what buys the quiet afterwards.

That is deliberately the shape of Claude Code's native [`/goal`](https://code.claude.com/docs/en/goal): a condition, a loop that keeps going until it holds, and a separate evaluator deciding when it does. `/build` is that idea with Pilot's quality machinery wrapped around it — the acceptance criteria are the condition, the judge pass is the evaluator, Pilot's stop guard is the hook that will not let the session end early, and a nine-layer verification pass stands between "the criteria passed" and "this is done".

:::tip Autonomy raises the bar, it does not lower it
Nobody inspects the work before it is called finished, so `VERIFIED` is earned by what the Buildout can show, never by a reply. Every criterion has to be ticked against evidence the judge could point at, and every verification layer has to be either evidenced or explicitly listed as not run. A criterion that will not close is reported unresolved — it is never quietly relaxed to reach a tidier ending.
:::

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

`/build` never hands large work off to `/spec` — it scales its execution graph internally instead (see [Execution and delegation](#execution-and-delegation)).

## Three things carry it

1. **The goal** — one sentence naming the end state.
2. **The tasks** — 3–7 of them, a title and an objective each, expected to change as you learn.
3. **The judge** — a separate pass at the end of each round that rules the acceptance criteria from the finished artifact.

## Workflow

```text
Goal  →  Draft tasks + criteria  →  Round (build every task → judge)  →  Verify  →  Hand back
                                          ↑                    ↓
                                          └─ gaps become the ──┘
                                             next round's tasks
```

A **round** is one full pass over the task list plus **one** judge pass. Most runs converge in two or three; four is the ceiling. When the rounds are done, a verification pass checks what the criteria do not cover, and the hand-back is a report — the Buildout is marked verified by the evidence in it, not by your approval.

### Name the goal

One sentence for what the finished thing is. A bounded research budget — typically 5–15 tool calls, widening to ~30 for an unfamiliar domain — goes on what already exists locally that the build should match, and what specifically "good" means here.

A **reference** to sit beside is optional. Use one only when a real side-by-side comparison exists: a competitor's live page, a named author's published piece, the pre-migration version of a screen. It must be **named**, **obtainable** (fetched once, up front, with the re-obtain command recorded), and **comparable**. Many goals have none, and forcing one is worse than having none — a reference nobody can obtain is a comparison the judge invents, and an invented comparison passes everything. `/build` picks the reference itself and tells you which it took; choosing a yardstick is not worth stopping a run for.

### Get grilled — the only place you are asked anything

Before anything is drafted or built, `/build` interrogates the goal. This is the one interaction in the workflow, and it is not a formality: everything downstream runs unsupervised against acceptance criteria written from your answers, so a vague goal here does not produce a vague result — it produces four rounds of confident work aimed slightly wrong.

**The stopping condition is objective** — three questions, and it keeps asking until all three have answers:

1. **The oracle** — the one observable signal that would show this outcome is actually true. A suite going green, a benchmark number, a walkthrough of the flow, a reader restating the mechanism. *No oracle, no serious build.*
2. **The evidence** — for every criterion it intends to write, what settles it pass or fail.
3. **The misfire** — how this run could pass every criterion and still be the wrong thing. It works that one out itself rather than asking, and then makes sure a criterion would catch it.

Then it stops and builds.

| The goal you give it | What happens |
| --- | --- |
| **Sharp** — "port these three screens to React, same behaviour, same tests green" | No questions. It says what it took the goal to mean and starts. |
| **One fork** — mostly clear, one branch point that changes what gets built | One targeted round on the fork. |
| **Weak** — "make the dashboard better", "modernise this", "clean it up" | A proper grilling: up to two rounds on the yardstick, the observable end state, the audience, and what must not change. |
| **Still vague about who it serves or what done means** | It says so and points you at [`/prd`](/docs/workflows/prd). A loop against an unsettled idea is worse than no loop. |

The five things it grills for are the five that decide whether a criterion can be written at all: **the oracle**, **the observable end state**, **the audience**, **what must not change**, and **where the work lands** when Branch Isolation is on.

A round of grilling reflects the goal back before it asks — *"I read this as X. One thing this could miss: Y. [question]"* — because a user corrects a wrong reading faster than they answer an abstract question, and naming a blind spot surfaces requirements a form would never have asked for. Up to three rounds, one or two questions each, each opened by the last one's answers.

What it will *not* ask about is how to build it — which library, which pattern, which file layout, whether the criteria look right, whether to keep going. That is the judgement the goal delegated.

This is the step where Pilot earns what `/goal` leaves to you. A native `/goal` condition is only as good as the sentence you typed; `/build` writes that condition itself, so it does the work of understanding first — and the answers land in the Buildout's `## Summary`, where the judge rules against them all run and the hand-back quotes them back.

:::note If you are not there
Turn **Ask Questions** off and `/build` asks nothing, states the assumption it took, and starts. If a question times out, it takes the recommended option, says which, and builds — then names the assumption again in the hand-back report. An autonomous run that stalls waiting on an absent user is the failure this shape exists to remove.
:::

### Draft tasks and criteria

**Tasks** are a title and a one-or-two-sentence objective. No file lists, no per-task definition of done — that is the upfront planning `/spec` charges for, and skipping it is the point.

**Criteria** are 3–6 one-sentence statements, judged once per round at the end. Each is decidable from the finished artifact by someone who did not build it, names the evidence that settles it, and can actually be settled during this run.

| Weak | Strong |
| --- | --- |
| The hero section is compelling. | Our hero and Nike's, screenshotted at 1440px and shown unlabelled, and a viewer told nothing picks ours. |
| Good error handling. | Every failure mode the module documents has a test asserting the user-facing message, and the suite passes. |
| ≥95% of rows carry a transcript, and the report discloses per-voice counts, and the table lists both architectures. | Three separate criteria. Split them. |

Two rules do most of the work: **pass/fail, never a score** (scores drift upward every round — "partial" and "mostly" are scores, and a criterion not fully met is a fail), and **one sentence each** (if it needs "and" three times, it is three criteria). At least one criterion is measurable whenever the goal has a measurable half — load time, bundle size, benchmark score, word count, pass rate.

**One of them is the oracle**, marked in the file: the observable that proves your outcome is real rather than that the work got done. Every other criterion can pass while that one fails — which is exactly the run building the wrong thing well — so it is judged last, from the signal itself and never a proxy, and it is the one criterion that can never be relaxed, waived, or rewritten mid-run. Rewriting an oracle is redefining the outcome, which is a new run.

**Tasks are sized as the largest slice that can be finished and verified in one go.** Small is not the goal, useful is: a working screen, a working endpoint, a real bug fixed, a section that reads end to end. Two tiny tasks in a row — a helper, a wrapper, a config file, a note — and the round has stopped moving criteria, which is the loop's most expensive way of looking busy.

A **Build Review** agent audits the tasks and criteria before the loop starts — a criterion you can decide by feel reads as perfectly clear to whoever wrote it. It runs on Claude Code and Codex, with an optional Codex companion for a second opinion, and is switchable in Console Settings. With no human approval gate, this reviewer is the only thing that reads the criteria before they become the contract, so its blocking findings are fixed rather than noted.

`/build` then prints the goal, the tasks and the criteria, names the Buildout file, and starts. It is a notification, not a gate — nothing waits for a reply.

:::note Steering a run without stopping it
The Buildout is annotatable in the Console like any other Pilot plan, and `/build` re-reads those annotations at the top of **every round**. That is how you redirect a run in flight: mark up a criterion and it is folded in — with the before and after recorded in the round log — at the next round boundary. It is the one path by which a criterion may legitimately change, because it comes from you rather than from the run finding it inconvenient.
:::

### Round

**Build** every open task, in order. Add, split, or drop tasks as the work teaches you something — each change gets one line in the round log. Code tasks are written test-first, and a task is never ticked while its tests fail. Then, once every task is ticked, **judge**:

1. Resolve a running artifact, if any criterion rules on runtime behaviour — reuse a live server, start the dev server, or attempt a preview deploy, in that order. A criterion about what a user sees is never ruled from source.
2. Re-obtain the reference, if the Buildout names one.
3. Rule each acceptance criterion pass or fail with one line of evidence, read off the finished artifact — not off your reasoning about it, and not off your memory of what was hard.
4. Tick or untick each criterion, increment `Rounds:`, append one line to the round log.

The judge is **calibrated, not brutal**: a criterion whose evidence meets what it asks passes. Raising the bar mid-judge is what makes a goal-and-loop run slower than `/spec` for no gain in quality. It is also strictly evidence-bound in the other direction — **insufficient evidence is a fail, not a pass.** If nothing can be pointed at right now, the criterion has not been settled, whatever the run believes about the work.

Failing criteria become the next round's tasks, at every round number. A failing criterion is never a question for you, and `/build` never asks whether to keep going: rounds one through three turn failures into tasks, round four is an automatic one-time extension, and there is no fifth.

:::note Waiting is not a round
If the only remaining work is blocked on something that will not finish inside the session — a multi-hour data collection, a third-party review, a credential someone else has to issue — `/build` stops and hands back with what is blocked and what unblocks it, rather than spending rounds on side work.
:::

#### When a criterion genuinely cannot be met

Borrowed from `/goal`'s `impossible` verdict, and guarded the same way: a run may declare a criterion unachievable and stop spending rounds on it — but only after **two genuinely different mechanisms** have been tried, the blocker is **named concretely** enough for someone else to check, it is not merely "not yet", and no other criterion is still closable. The run's own conviction that something is impossible is evidence, not proof.

That criterion is then reported unresolved with the two approaches that failed, and the run keeps working everything still live. It is an honest finish, not a pass.

### Verify

Once the rounds are done, a verification pass covers the axes acceptance criteria mostly do not. `VERIFIED` is measured against **nine layers**, and each must either carry evidence in the Buildout's `## Verification Record` or appear in `## Not Verified` saying what could not be run and why — there is no third state:

| Layer | Evidence that counts |
| --- | --- |
| Criteria | Every one ticked by a judge pass with evidence pointed at, the oracle from its own signal |
| Suite | Full test run, exit 0, counts recorded — the suite, not the touched files |
| Types · lint · build | Each command run, exit 0 |
| Runs at all | Artifact started, primary path exercised with real input, logs read |
| User-facing paths | Browser E2E — snapshot → click → re-snapshot, on a target proven current |
| Code review | **Changes Review** findings closed, `cannot_verify` items settled |
| Docs | Files updated, or "no doc impact" recorded |
| Regression | Suite, types and build re-run green after the last fix landed |
| Not verified | The section exists; "None" is valid, absent is not |

It is scaled to what was actually built. A prose, design, or research artifact runs only the documentation question and the not-verified list, so the pass costs almost nothing — but anything that produced code gets the checks, the review, and the regression in full, whether or not it has a UI. Findings are fixed on the spot and never spend a round; only a criterion the fix materially changed gets re-judged.

Every command lands in the record as the command plus `pass` or `fail`, never as prose. A verified run may list only passing commands — so a red one holds the run open until it is fixed, or is disclosed with the failure still visible as a failure. Softening it into a sentence ("mostly passing", "one unrelated flake") is the specific way an unsupervised loop launders a failure into a pass, and the structured pair is what makes the honest path the easy one.

:::warning Switching the verification pass off means unverified
With **Verification Pass** off in Console Settings there is no evidence to justify certifying an unsupervised run, so `/build` does not certify it. The run ends `COMPLETE` with `Verification: disabled` in `## Not Verified`, and the report leads with the fact that the criteria passed and nothing checked the code behind them. It never writes `VERIFIED` on that path.
:::

### Hand back

The hand-back is a report, not a gate. It names every criterion with the evidence that settled it, the rounds it took, how the task list changed along the way, any criterion that moved and why, **what `/build` assumed on your behalf** while you were away, and an explicit list of what was **not** verified. On a `--worktree=yes` run it also confirms the squash landed and what it carried — the flag asked for the merge, so the merge is not a second question.

`Status: VERIFIED` is then written by the run itself, and only when every criterion is ticked, `## Verification Record` exists, `## Not Verified` exists, and all nine layers above are either evidenced or disclosed. Any one missing and the run is not finished.

:::note There is no partial hand-back
Hand-back is reachable exactly four ways: every criterion passed, the four-round ceiling reached after a real judge pass, work blocked on something outside the session that is named, or every remaining criterion proven unachievable. An unticked task, an unjudged criterion, or a round cut short is not one of them — and running low on context is not a blocker, because the Buildout survives compaction and the run resumes from it.
:::

## The Buildout is a real file

`/build` writes `docs/builds/YYYY-MM-DD-<slug>.md` with `Type: Build` and registers it with the session — its own directory, beside `/spec`'s `docs/plans/` and `/prd`'s `docs/prd/`, running on the same machinery. The `Type:` header is what identifies a Buildout, not the directory, so one written to `docs/plans/` before the split keeps working. That buys four things:

- **It survives compaction.** After a context compaction the run resumes from the file, not from the conversation.
- **Claude Code's status line tracks tasks and rounds.** `Build: running-brand build ███░░ 3/5 r2`. Codex shows the same Buildout state in the Console.
- **The Console shows it.** Buildouts get their own **Buildouts** section, and can be shared with teammates for annotation like any other Pilot plan.
- **The stop guard holds the loop open.** While the Buildout is registered and not `VERIFIED`, the session cannot quietly end at "good enough" — on both Claude Code and Codex. On Claude Code, you never type [`/goal`](https://code.claude.com/docs/en/goal): Pilot's Stop hook is the same mechanism, with the acceptance criteria as its condition and the judge pass as its evaluator. The workflow escape hatch is stopping twice within 60 seconds.

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

The two checkbox lists have different jobs. `## Progress Tracking` carries the tasks, and that is what Claude Code's status line and the shared Console count. `## Acceptance Criteria` is the judge's list, and stays unticked until a judge pass ticks it.

### Statusline phases

| Buildout state | Phase shown | Meaning |
| --- | --- | --- |
| `PENDING` + `Approved: No` | `goal` | Goal, tasks, and criteria being drafted |
| `PENDING` + `Approved: Yes` | `build` | Contract locked, working the task list |
| `COMPLETE` | `judge` | Every task ticked; judge pass and verification outstanding |
| `VERIFIED` | *(cleared)* | Every criterion passed on evidence, and verification recorded it |

`Approved: Yes` on a Buildout means **the contract is locked and the loop is live** — `/build` writes it itself once the criteria stop moving. It is not a record of anyone signing off, and nothing in the workflow waits for one. (`/spec`'s **Plan Approval** toggle is not read by `/build`; there is no gate to switch off.)

A hand-back does not always mean `VERIFIED`: a run that stops at the four-round ceiling with criteria unresolved, one blocked on something outside the session, and one that proved its remaining criteria unachievable all stay `PENDING` so they can be resumed from the file. A run with the verification pass switched off ends `COMPLETE`. A one-shot sentinel lets the session stop in each case.

## Execution and delegation

Claude Code and Codex choose the useful execution graph themselves: direct, parallel, delegated, or nested where the current harness supports it. Pilot never pauses an autonomous build to ask permission to spawn subagents or to select an orchestration mode.

The agent still coordinates non-overlapping writes, task dependencies, and evidence returned by workers. Build Review and Changes Review remain configurable named review passes, but they do not limit additional delegation the active agent judges useful.

## Configurable toggles

| Toggle | Group | Default | Effect when disabled |
| --- | --- | --- | --- |
| **Ask Questions** | Automation | On | No grilling — `/build` takes the reading of the goal it would have recommended, records the assumption in the Buildout, and states it in one line. On a goal too weak to name any criterion's evidence it stops and points at `/prd` rather than inventing a yardstick and then judging against its own invention. |
| **Branch Isolation** | Automation | On | No question about where the work lands; the run works on the current branch unless a `--worktree` / `--new-branch` flag says otherwise. |
| **Build Review** | Reviews | On | The tasks and criteria go unreviewed into the loop — and with no approval gate, nothing else reads them first. |
| **Also review with Codex** (on Build Review) | Reviews | Off | No second-opinion Codex pass over the criteria. Needs the Claude Code Codex plugin. |
| **Verification Pass** | Automation | On | No checks, E2E, or regression — and the run **cannot reach `VERIFIED`**. It ends `COMPLETE` and the report says nothing checked the code. |
| **Changes Review** | Reviews | On | For code builds, the diff is not reviewed; the gap is disclosed in `## Not Verified`. |

**Plan Approval** is not in this table on purpose — it governs `/spec`'s plan gate, and `/build` does not read it. With **Ask Questions** off as well, `/build` runs goal → tasks and criteria → rounds → verify → hand back with no interaction from start to finish.

## Common issues

| Symptom | What it means | What to do |
| --- | --- | --- |
| The judge keeps passing weak work | The criteria are decidable by feel | Rewrite each to name the evidence that settles it. |
| The session will not stop | The stop guard is holding the loop, as designed | Let it run — an autonomous run is meant to be held to its criteria. Escape hatch: stop twice within 60s. |
| It never asked me anything | The goal was sharp enough to write criteria from | Check the Buildout's `## Summary` — the standard it inferred is written there. Annotate the file in the Console to steer it mid-run. |
| It grilled me harder than expected | The goal had no checkable yardstick | That is the design: those questions are the difference between a run judged against your standard and one judged against its own. |
| It handed back at four rounds with criteria failing | The round ceiling, working | Read the unresolved criteria and their reasons in the report, then start a new run at the gap. |
| It handed back saying a criterion was unachievable | The `impossible` exit, after two different approaches failed | The blocker is named in the round log — resolve it and re-run, or drop the criterion in the next run. |
| It handed back saying it was blocked | Remaining work needs something outside the session | Come back when the blocker clears; the Buildout stays `PENDING` and the run resumes from it. |
| It finished `COMPLETE`, not `VERIFIED` | The Verification Pass toggle is off | Nothing checked the code, so nothing certified it. Turn the toggle on and re-run the verification. |
| The Buildout is missing from the Console | It is outside the scanned directories | It must live in `docs/builds/` and be registered. On an ordinary run that means the project root. On a `--worktree=yes` run it lives in the run's own worktree, which the Console accepts because the Buildout slug matches that worktree's — a Buildout dropped into an *unrelated* worktree is still filtered out by design, so move it and re-register. |

## When not to use `/build`

- **Something that used to work is broken** → [`/fix`](/docs/workflows/fix).
- **You want the approach written down and approved before any code** → [`/spec`](/docs/workflows/spec).
- **The idea is still vague about who it serves** → [`/prd`](/docs/workflows/prd) first.
- **A one-line change, a rename, a config tweak** → just do it; a Buildout costs more than the edit.
- **The result cannot be judged without data that will not arrive this session** → build it straight, or come back when the data lands.

## Portability

The method survives outside Pilot. `/build` can export a portable brief instead of running: the goal condition moves into the prompt's first line, the tasks and criteria travel verbatim, and the judging protocol is stated inline. You lose the enforcement — the Buildout file, the stop guard, and Claude Code's status-line integration — not the method.
