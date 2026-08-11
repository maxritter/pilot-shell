---
name: build
description: "Builds toward a named goal without writing a spec first — the goal-and-loop workflow. Use when the user types /build; asks for something to be made, written, designed, or implemented where the approach is better discovered while building than planned up front; asks to keep going until the result is genuinely good; or wants a migration, port, or rebuild judged on what comes out rather than against an approved task list. Not for a defect in behaviour that already worked — that is /fix. Not when the approach has to be written down and agreed before any code exists — that is /spec."
argument-hint: "<what to build, and optionally what it should measure up to>"
user-invocable: true
hooks:
  Stop:
    - command: uv run --no-project --python python3 python "$HOME/.pilot/hooks/spec_plan_validator.py" docs/builds Buildout
---

# /build — Goal-and-Loop Development

The path for **"make this, and make it good"** when there is no spec and you do not want one. You name the end state; `/build` turns it into a short task list plus a handful of acceptance criteria, builds the tasks, then judges the result against those criteria. What the tasks actually are is allowed to change as the work teaches you something — that flexibility is the point.

**It runs autonomously from the goal to the hand-back.** The goal *is* the directive: once it is clear enough to build against, start and keep going until every criterion passes. There is no approval gate, no round-budget check-in, and no sign-off at the end.

**All the asking happens before any work starts**, and it is not a formality: Step 1.5 grills a weak goal until its acceptance criteria can actually be written — the yardstick, the end state, what must not change. A sharp goal passes through in silence. Spending a user's attention *there* is what buys the silence afterwards.

**Autonomy raises the evidence bar; it does not lower it.** Nobody inspects this work before it is called done, so `VERIFIED` is earned only by what the Buildout can show: every criterion ticked against evidence a judge pointed at, and every verification layer either evidenced or explicitly disclosed as not run (Step 6.10). A criterion that will not close is reported unresolved — it is never quietly relaxed, and no round is ever skipped to reach a tidier ending.

```bash
> /build "landing page for my running brand — should feel as alive as Nike's"
> /build "port the admin screens to React, better than what we have, not just ported"
> /build "2000-word explainer on vector databases for non-engineers"
```

`/build` and `/spec` are **peers, not tiers**. Neither is the escalation path for the other.

| The request | Command |
|---|---|
| Something that already worked is broken | `/fix` |
| The approach should be written down and approved before any code | `/spec` |
| The idea is still vague about who it serves or what done means | `/prd` |
| A clear goal, and the approach can be found while building | **`/build`** |

Size is **not** the discriminator. A 30-screen migration can be `/build`; a 40-line change can be `/build`; a small feature whose execution order matters can be `/spec`. Pick on **what the work is measured against**: an approved task list (`/spec`) or a defined end state (`/build`).

---

## The shape of a run

```
Goal → Draft tasks + criteria → Round(build every task → judge) → Verify → Hand back
```

Three things carry it:

1. **The goal** — one sentence naming the end state.
2. **The tasks** — 3–7 of them, a title and an objective each, expected to change as you learn.
3. **The judge** — a separate pass at the end of each round that rules the acceptance criteria from the finished artifact.

A **round** is one full pass over the task list plus **one** judge pass. Criteria that fail become the next round's tasks. Most runs converge in two or three rounds.

Once the rounds are done, **Step 6 verifies** what the criteria do not cover and **Step 7 hands back** — a report, not a gate. `VERIFIED` is earned by evidence in the file, never by a sign-off.

---

## Rules that keep it converging

```
0. NO ORACLE, NO BUILD. One criterion is the observable that proves the user's
   outcome is actually true. Every other criterion can pass while it fails —
   that is the run building the wrong thing well. It is never relaxed, never
   waived, and never ruled from a proxy.
1. TASKS ARE THE UNIT OF WORK. Criteria are judged at the end of a round, not
   worked one at a time. A criterion is never "the current gap".
2. CRITERIA BEFORE BUILDING. Criteria written after a draft describe that draft.
3. JUDGE ONLY WHEN EVERY TASK IS TICKED. Judging a half-built artifact spends a
   round to learn what you already knew.
4. PASS/FAIL, NEVER A SCORE. Scores drift upward every round; pass/fail does not.
   "Partial" and "mostly" are scores. Not fully met is fail.
5. CALIBRATED, NOT BRUTAL. Pass a criterion whose evidence meets what it asks.
   Raising the bar mid-judge is what makes this slower than /spec for no gain.
6. NO EVIDENCE YOU CAN POINT AT RIGHT NOW IS A FAIL. Not a pass on the balance of
   probability, not "it must work by now". Insufficient evidence is a failing
   criterion, and its gap is next round's tasks.
7. FOUR JUDGE PASSES IS THE CEILING, AND NOBODY IS ASKED FOR MORE. Rounds 1-3
   turn failures into tasks; round 4 is the automatic one-time extension; a fifth
   never happens. What will not close is reported unresolved, never lowered.
8. WAITING IS NOT A ROUND. Work blocked on something that will not finish inside
   this session ends the run — it does not spend rounds. Context pressure is not
   such a blocker: the Buildout survives compaction, so re-read it and continue.
9. HAND-BACK HAS FOUR DOORS. Every criterion passed, the round ceiling reached
   after a real judge pass, a named external blocker, or a criterion proven
   unachievable in this session. Nothing else is one.
```

---

## What Pilot adds

`/build` is not a conversation that remembers a goal. The goal, tasks, and criteria are a **file**, registered with the session, and the loop is held open by Pilot's stop guard.

- **Buildout file** at `docs/builds/YYYY-MM-DD-<slug>.md` with `Type: Build` — its own directory, next to `/spec`'s `docs/plans/` and `/prd`'s `docs/prd/`. It survives compaction, shows up in the Console's **Buildouts** section, and can be shared and annotated like any other Pilot plan — annotations are picked up at the start of every round, so the file stays the way to steer a run without stopping it.
- **Two reviewers, outside the loop, switchable** in Console → Settings → Workflows: **Build Review** on the criteria before round one, **Changes Review** on the diff at the end. Each has an optional Codex companion.
- **A verification pass** (Step 6) before hand-back — suite, types, lint, build, live-target E2E, the code review, doc sync, regression — scaled to the artifact, so a prose build pays almost nothing. Its nine layers (6.10) are what `VERIFIED` is measured against: each is either evidenced in the file or disclosed as not run. **Switch the pass off and the run does not reach `VERIFIED`** — it hands back `COMPLETE` and says nothing checked the code.
- **The statusline tracks tasks and rounds** — `Build: <name> build ▓▓▓░░ 3/5 r2`.
- **The stop guard holds the loop open.** While the Buildout is registered and not `VERIFIED`, the session cannot quietly end at "good enough". You do **not** need `/goal` — Pilot's Stop hook is the same mechanism, on both Claude Code and Codex, with the acceptance criteria as its condition and the judge pass as its evaluator. The user's escape hatch is stopping twice within 60s.
- **`Status:` is the same closed set** as every other Pilot plan — `PENDING` → `COMPLETE` → `VERIFIED`, bare keyword, no trailing prose.

| Buildout state | Statusline phase | What it means |
|---|---|---|
| `PENDING` + `Approved: No` | `goal` | Goal, tasks, and criteria being drafted |
| `PENDING` + `Approved: Yes` | `build` | Contract locked, working the task list |
| `COMPLETE` | `judge` | Every task ticked; judge pass and verification outstanding |
| `VERIFIED` | *(cleared)* | Every criterion passed on evidence, and Step 6 recorded it |

`Approved: Yes` on a Buildout means **the contract is locked and the loop is live** — Step 3 writes it itself the moment the criteria stop moving. It is not a record of anyone signing off, and nothing in this workflow waits for one.

A hand-back does not always mean `VERIFIED`: a run that stops at the round-four ceiling with criteria unresolved, one blocked on something outside the session, and one that proved a criterion unachievable all stay `PENDING` so they can be resumed from the file. A one-shot sentinel lets the session stop in those cases.

---

## All the interaction is at the front

**Step 1.5 is the one place a user is asked anything, and it is a real interrogation** — sized to the goal you were handed. A sharp goal gets no questions at all. A weak one ("make the dashboard better") gets grilled properly: the yardstick, the observable end state, the audience, what must not change, and where the work lands, over up to two rounds.

The stopping condition is objective, not social: **you keep asking until you can name, for every criterion you intend to write, the evidence that would settle it.** Then you stop and build. That is the work `/goal` leaves to whoever types the condition — `/build` writes the condition itself, so it has to understand first.

Everything after that is automatic:

- **Never ask "should I keep going?"** — the criteria and the round ceiling answer that.
- **Never ask for approval of the tasks or criteria.** Step 3 locks them itself.
- **Never ask whether to accept a failing criterion.** It is next round's tasks, and at the ceiling it is a line in the report.
- **Never ask for sign-off at hand-back.** Evidence in the file decides `VERIFIED`, not a reply.

The single exception is **Step 3.3's ultracode escalation**, and only because it is not a check-in: `/effort ultracode` is session-scoped and the user has to type it, so there is no version of that step you can do on their behalf. It never generalises to anything else.

⛔ **`PILOT_PLAN_APPROVAL_ENABLED` is not read by `/build`.** That toggle governs `/spec`'s plan gate. A Buildout has no gate to switch off.

⛔ **A question that auto-continues does not stall this run.** An `AskUserQuestion` result reading "No response after Ns — continued without an answer" means the user is not there. `/spec` re-asks; `/build` does not, because Step 1.5 is the only question it has and waiting is the failure mode this workflow was rebuilt to remove. Take the recommended option, say in one line which you took and why, and build — then name the assumption again in the hand-back report, where they will actually read it.

**Stop guard:** when it blocks a stop mid-run, don't acknowledge it, output resume instructions, or say goodbye. Your very next action is a tool call — re-read the Buildout and build or judge. Same after any user interruption.

---

## Excuse → Reality

| What you will be tempted to think | What is true |
|---|---|
| "I'll write the criteria once I see a first draft." | Criteria written after the build describe the build. |
| "8/10 — good enough to move on." | Scores drift up every round. Pass/fail does not. |
| "I'll judge this task now while it's fresh." | The judge runs once per round, on the whole artifact, after every task is ticked. Judging per task is how a 3-round run becomes a 14-round one. |
| "This criterion is close — one more thing and it'd pass." | Then it fails, and that thing is a task. |
| "I built it, so I can tell it's good." | You know how hard it was to make. The judge must not. |
| "The task list has changed a lot; I should have planned harder." | Tasks changing as you learn is the design. Log it and keep going. |
| "I'll spin up a subagent to judge this properly." | It starts blind, re-derives what this thread already holds, and bills you for the round trip. Judge from the artifact instead. Reviewers are the exception, and they run outside the loop. |
| "Four pass, three partial — I'll report that." | "Partial" is a score. Not fully met is fail, and the gap is next round's tasks. |
| "Context is nearly gone; I'll hand back what I have." | The Buildout survives compaction. Re-read it and finish the round. |
| "I'll just check the criteria with the user before I start." | Step 1.5 is where you ask, and it is generous — grill there until you can name every criterion's settling evidence. After it, asking is the run refusing to run. |
| "The goal is thin, but I'll work it out as I build." | You will work out *a* standard, then judge against your own invention. A thin goal is exactly what 1.5 exists to fix, and it is the cheapest fix available all session. |
| "They said 'make it better' — I know what they mean." | Name the evidence that settles it. If you cannot, you do not know what they mean; you know what you would build. |
| "Every criterion passed, so the goal is met." | Check the oracle. Criteria can all be true while the thing the user wanted is not — that is the misfire you named at 1.5, arriving on schedule. |
| "I'll add a small helper task to keep the round moving." | Two tiny tasks in a row and the round has stopped moving criteria. Name which criterion the next task closes; if none, it is busywork with a checkbox. |
| "The suite is mostly green — one unrelated flake." | Then it is `fail`, recorded as `fail`. A red command turned into a sentence is how an unsupervised loop launders a failure into a pass. |
| "This criterion can't be met, so I'll stop here." | Say it out loud and prove it (Step 5.5). Your own belief that it is impossible is evidence, not proof — a criterion you have not attacked from a second angle is failing, not unachievable. |
| "I'll ask whether they want a fourth round." | Round four is automatic and is the last. There is nothing to ask; there is a report to write. |
| "The criteria passed, so the code is fine." | The criteria rule the artifact. Step 6 rules the code behind it — they are different axes. |
| "This is big, so it should have been `/spec`." | Scale is not what `/spec` is for; an approved task list is. Big work escalates *inside* this skill (Step 3), it does not get handed off. |
| "The data isn't in yet, so I'll do something else and call it a round." | Waiting is not a round. Hand back and say what is blocked. |
| "One more selector and this tap will land." | Three failures with the same driver means the driver is wrong. Check what the project says to use — `browser-automation.md`. |

## Red flags — stop and go back

- About to build and the Buildout file has no tasks → Step 2.
- About to skip Step 6 on a code build with verification enabled → run it.
- About to judge and a task is still unticked → finish the task first, Step 4.
- A criterion cannot be settled without asking the user what they meant → rewrite it, Step 2.
- A criterion's evidence depends on something that will not finish inside this run → rewrite or drop it, Step 2.
- You are reaching for a subagent inside the loop → Step 5, judge it yourself.
- You are about to suggest `/spec` because the work is large → Step 3, escalate here instead.
- You are patching a file with a `python3` heredoc instead of `Edit` → Step 4, tool discipline.
- The judge passed everything on round one and the work is thin → the criteria are decidable by feel, Step 2.
- A verdict contains "should", "probably", "close enough", "partial", or "mostly" → rejudge from the artifact.
- About to hand back with an unticked task or an unjudged criterion → Step 4, not Step 7.
- About to write `VERIFIED` without `## Verification Record` and `## Not Verified` in the file → Step 7.4.
- About to ask the user anything after Step 1.5 → you are not at an interaction point. Re-read the run's four doors (rule 9) and take the one that applies.
- About to draft criteria and you cannot name what evidence settles one of them → Step 1.5, not Step 2. That is the grilling's stopping condition, unmet.
- About to rule a UI criterion from source instead of a running artifact → Step 5.1a.
- Three interactions in a row failed with the same UI driver → the driver is wrong, not the selector. `browser-automation.md`, hard rule 3.
- About to call a live target unavailable because the artifact is installed rather than served → Step 5.1a, Tier 2b.

## When NOT to use

- **A defect in behaviour that already worked** → `/fix`.
- **The approach has to be written down and agreed before any code** → `/spec`. Size alone is not the trigger.
- **The idea is still vague about who it serves or what done means** → `/prd` first, then `/build` or `/spec`.
- **A one-line change, a rename, a config tweak** → just do it; a Buildout costs more than the edit.
- **The result cannot be judged without data that will not arrive during this session** → say so and build it straight, or come back when the data lands.
