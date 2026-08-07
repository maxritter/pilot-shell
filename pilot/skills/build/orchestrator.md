---
name: build
description: "Builds toward a named goal without writing a spec first — the goal-and-loop workflow. Use when the user types /build; asks for something to be made, written, designed, or implemented where the approach is better discovered while building than planned up front; asks to keep going until the result is genuinely good; or wants a migration, port, or rebuild judged on what comes out rather than against an approved task list. Not for a defect in behaviour that already worked — that is /fix. Not when the approach has to be written down and agreed before any code exists — that is /spec."
argument-hint: "<what to build, and optionally what it should measure up to>"
user-invocable: true
---

# /build — Goal-and-Loop Development

The path for **"make this, and make it good"** when there is no spec and you do not want one. You name the end state; `/build` turns it into a short task list plus a handful of acceptance criteria, builds the tasks, then judges the result against those criteria. What the tasks actually are is allowed to change as the work teaches you something — that flexibility is the point.

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
Goal → Draft tasks + criteria → Approve → Round(build every task → judge) → Hand back
```

Three things carry it:

1. **The goal** — one sentence naming the end state.
2. **The tasks** — 3–7 of them, a title and an objective each, expected to change as you learn.
3. **The judge** — a separate pass at the end of each round that rules the acceptance criteria from the finished artifact.

A **round** is one full pass over the task list plus **one** judge pass. Criteria that fail become the next round's tasks. Most runs converge in two or three rounds.

---

## Rules that keep it converging

```
1. TASKS ARE THE UNIT OF WORK. Criteria are judged at the end of a round, not
   worked one at a time. A criterion is never "the current gap".
2. CRITERIA BEFORE BUILDING. Criteria written after a draft describe that draft.
3. JUDGE ONLY WHEN EVERY TASK IS TICKED. Judging a half-built artifact spends a
   round to learn what you already knew.
4. PASS/FAIL, NEVER A SCORE. Scores drift upward every round; pass/fail does not.
5. CALIBRATED, NOT BRUTAL. Pass a criterion whose evidence meets what it asks.
   Raising the bar mid-judge is what makes this slower than /spec for no gain.
6. THREE JUDGE PASSES, THEN ASK. One more round is a one-time extension; four is
   the ceiling. Never a fifth.
7. WAITING IS NOT A ROUND. Work blocked on something that will not finish inside
   this session ends the run — it does not spend rounds.
```

---

## What Pilot adds

`/build` is not a conversation that remembers a goal. The goal, tasks, and criteria are a **file**, registered with the session, and the loop is held open by Pilot's stop guard.

- **Buildout file** at `docs/plans/YYYY-MM-DD-<slug>.md` with `Type: Build`. It survives compaction, shows up in the Console's **Buildouts** section, and can be shared with teammates for annotation like any other Pilot plan.
- **The statusline tracks tasks and rounds** — `Build: <name> build ▓▓▓░░ 3/5 r2`.
- **The stop guard holds the loop open.** While the Buildout is registered and not `VERIFIED`, the session cannot quietly end at "good enough". You do **not** need `/goal`; Pilot's Stop hook already does this, on both Claude Code and Codex. The user's escape hatch is stopping twice within 60s.
- **`Status:` is the same closed set** as every other Pilot plan — `PENDING` → `COMPLETE` → `VERIFIED`, bare keyword, no trailing prose.

| Buildout state | Statusline phase | What it means |
|---|---|---|
| `PENDING` + `Approved: No` | `goal` | Goal, tasks, and criteria being drafted |
| `PENDING` + `Approved: Yes` | `build` | Working the task list |
| `COMPLETE` | `judge` | Every task ticked; judge pass outstanding |
| `VERIFIED` | *(cleared)* | Handed back to the user |

A hand-back does not always mean `VERIFIED`: a run that stops at the round-four ceiling with criteria unresolved, or one blocked on something outside the session, stays `PENDING` so it can be resumed from the file. A one-shot sentinel lets the session stop in those two cases.

---

## Three user interaction points, and no more

1. **Goal and reference** — confirm the end state, and pick a reference only when the user did not name one and a real side-by-side comparison exists (Step 1).
2. **Approval** — one gate on the drafted tasks and criteria (Step 3), skipped when `PILOT_PLAN_APPROVAL_ENABLED` is `false`.
3. **Hand-back** — either every criterion passed, or the round budget was reached (Steps 5 and 6).

Everything else is automatic. **Never ask "should I keep going?"** — the criteria and the round budget answer that. A failing criterion is not a decision point; it is the next round's tasks.

⛔ **An auto-continued question is not an answer.** An `AskUserQuestion` result reading "No response after Ns — continued without an answer" means the user has not responded. Re-ask when they return; never infer approval.

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
| "I'll spin up a subagent to judge this properly." | It starts blind, re-derives what this thread already holds, and bills you for the round trip. Judge from the artifact instead. |
| "This is big, so it should have been `/spec`." | Scale is not what `/spec` is for; an approved task list is. Big work escalates *inside* this skill (Step 3), it does not get handed off. |
| "The data isn't in yet, so I'll do something else and call it a round." | Waiting is not a round. Hand back and say what is blocked. |

## Red flags — stop and go back

- About to build and the Buildout file has no tasks → Step 2.
- About to judge and a task is still unticked → finish the task first, Step 4.
- A criterion cannot be settled without asking the user what they meant → rewrite it, Step 2.
- A criterion's evidence depends on something that will not finish inside this run → rewrite or drop it, Step 2.
- You are reaching for a subagent inside the loop → Step 5, judge it yourself.
- You are about to suggest `/spec` because the work is large → Step 3, escalate here instead.
- You are patching a file with a `python3` heredoc instead of `Edit` → Step 4, tool discipline.
- The judge passed everything on round one and the work is thin → the criteria are decidable by feel, Step 2.
- A verdict contains "should", "probably", or "close enough" → rejudge from the artifact.

## When NOT to use

- **A defect in behaviour that already worked** → `/fix`.
- **The approach has to be written down and agreed before any code** → `/spec`. Size alone is not the trigger.
- **The idea is still vague about who it serves or what done means** → `/prd` first, then `/build` or `/spec`.
- **A one-line change, a rename, a config tweak** → just do it; a Buildout costs more than the edit.
- **The result cannot be judged without data that will not arrive during this session** → say so and build it straight, or come back when the data lands.
