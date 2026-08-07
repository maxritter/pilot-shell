---
name: build
description: "Builds to a standard instead of to completion — the goal-and-loop workflow for when there is no spec. Use when the user types /build; asks for something to be made, written, designed, or implemented and cares that it is good, not just done; names something to match or beat (\"as good as Stripe's docs\", \"better than our dashboard\"); asks to keep iterating until the work clears a bar; or wants a migration, port, or rebuild where each piece has to come out better than what it replaces. Not for a defect in behaviour that already worked — that is /fix."
argument-hint: "<what to build, and optionally what it has to beat>"
user-invocable: true
---

# /build — Goal-and-Loop Development

The default path for **"make this, and make it good"** when there is no spec. It replaces build-once-and-hand-over with a loop that cannot exit until the work clears a bar set before any building started.

```bash
> /build "landing page for my running brand — has to feel as alive as Nike's"
> /build "port the admin screens to React, better than what we have, not just ported"
> /build "2000-word explainer on vector databases for non-engineers"
```

`/build` and `/spec` are **peers, not tiers**. Neither is the escalation path for the other.

| The request | Command |
|---|---|
| Something that already worked is broken | `/fix` |
| You want an approved plan file and a task list before any code | `/spec` |
| The idea is still vague about who it serves or what done means | `/prd` |
| Make this, and make it good — the standard is the deliverable | **`/build`** |

Size is **not** the discriminator. A 30-screen migration can be `/build`; a 40-line change with an exacting bar can be `/build`; a small feature with an unclear execution order can be `/spec`. Pick on **what the work is measured against**: a task list (`/spec`) or a standard (`/build`).

---

## Three things carry this workflow

1. **The bar** — a real, named, obtainable artifact the work is compared against.
2. **The criteria** — 5–9 pass/fail statements, written before any building.
3. **The blind judge** — fresh eyes ruling on each criterion without knowing which artifact is ours.

Everything else is scaffolding for those three. When you are short on time, cut the scaffolding, never these.

---

## Iron Laws

```
1. CRITERIA BEFORE BUILDING — criteria written after a draft describe that draft.
2. THE BAR MUST BE OBTAINABLE — open it, run it, screenshot it. A bar you cannot
   fetch is a bar the judge hallucinates, and a hallucinated comparison passes
   everything.
3. PASS/FAIL, NEVER A SCORE — scores drift upward every round; pass/fail does not.
4. DEFAULT TO FAIL — a criterion is failed until evidence passes it.
5. EXIT ON THE CRITERIA, NEVER ON A ROUND COUNT — "three rounds is probably
   enough" is how this degrades into an ordinary build.
6. ONE GAP PER ROUND — a list lets the next round cherry-pick the cheap ones and
   call it progress.
```

---

## What Pilot adds

`/build` is not a conversation that remembers a rubric. The rubric is a **file**, registered with the session, and the loop is enforced by Pilot's stop guard.

- **Rubric file** at `docs/plans/YYYY-MM-DD-<slug>.md` with `Type: Build`. It survives compaction, shows up in the Console's **Specifications** tab with a `Build` badge, and can be shared with teammates for annotation like any other Pilot plan.
- **The statusline is the loop counter** — `Build: <name> build [loop] ▓▓▓░░ 4/7 r2` — criteria passed, current round, current gap.
- **The stop guard is the goal condition.** While the rubric is registered and not `VERIFIED`, the session cannot quietly end at "good enough". You do **not** need `/goal`; Pilot's Stop hook already holds the loop open, on both Claude Code and Codex. Escape hatch: the user stops twice within 60s.
- **`Status:` is the same closed set** as every other Pilot plan — `PENDING` → `COMPLETE` → `VERIFIED`, bare keyword, no trailing prose.

| Rubric state | Statusline phase | What it means |
|---|---|---|
| `PENDING` + `Approved: No` | `rubric` | Bar and criteria being written |
| `PENDING` + `Approved: Yes` | `loop` | Build → judge rounds running |
| `COMPLETE` | `judge` | Every criterion checked; final blind judge pass outstanding |
| `VERIFIED` | *(cleared)* | Handed back to the user |

---

## Workflow

```
Scope & research → Set the bar → Write criteria → Approve → Loop (build → judge → one gap) → Hand back
```

**Three user interaction points, and no more:**

1. **Bar selection** — only when the user did not name one (Step 2).
2. **Criteria approval** — the one gate (Step 4), skipped when `PILOT_PLAN_APPROVAL_ENABLED` is `false`.
3. **Hand-back** — the loop clears the bar you set; it does not decide the work is finished (Step 6).

Everything else is automatic. **Never ask "should I keep going?"** — the criteria answer that. A failing criterion is not a decision point; it is the next round's job.

⛔ **An auto-continued question is not an answer.** An `AskUserQuestion` result reading "No response after Ns — continued without an answer" means the user has not responded. Re-ask when they return; never infer approval.

**Stop guard:** when it blocks a stop mid-loop, don't acknowledge it, output resume instructions, or say goodbye. Your very next action is a tool call — re-read the rubric and judge or build. Same after any user interruption.

---

## Excuse → Reality

| What you will be tempted to think | What is true |
|---|---|
| "The bar is basically best-in-class SaaS sites." | A category cannot be fetched, so the judge invents the comparison and passes everything. |
| "I'll write the criteria once I see a first draft." | Criteria written after the build describe the build. |
| "8/10 — good enough to move on." | Scores drift up every round. Pass/fail does not. |
| "Three rounds is enough." | The exit is the criteria. A round count is a way to stop while still failing. |
| "I built it, so I can tell it's good." | You know how hard it was to make. The judge must not. |
| "I'll spin up a subagent to judge this properly." | It starts blind, re-derives what this thread already holds, and bills you for the round trip. Rejudge from the artifact instead. |
| "This is big, so it warrants fanning out." | Big is not the trigger. 5+ independent surfaces is. A long grind is still one thread. |
| "This is big, so it should have been `/spec`." | Scale is not what `/spec` is for; an approved task list is. Big work escalates *inside* this skill (Step 4), it does not get handed off. |
| "One criterion still fails but it's minor — I'll flag it." | Stopping on a failing criterion is the exact outcome this workflow exists to prevent. Close it, or renegotiate it with the user out loud. |

## Red flags — stop and go back

- About to build and the rubric file has no numbered criteria → Step 3.
- A criterion cannot be settled without asking you what you meant → rewrite it, Step 3.
- A criterion would pass on a tie with the bar → rewrite it so ours has to win, Step 3.
- You are reaching for a subagent inside the loop → Step 5, judge it yourself.
- You are about to suggest `/spec` because the work is large → Step 4, escalate here instead.
- The judge passed everything on round one → the bar is too soft, Step 2.
- You are counting rounds → Step 5.
- A verdict contains "should", "probably", or "close enough" → rejudge from the artifact.

## When NOT to use

- **A defect in behaviour that already worked** → `/fix`.
- **The user wants an approved plan file and an ordered task list before any code** → `/spec`. Size alone is not the trigger.
- **The idea is still vague about who it serves or what done means** → `/prd` first, then `/build` or `/spec`.
- **A one-line change, a rename, a config tweak** → just do it; a rubric costs more than the edit.
- **Work with no comparable reference and no measurable half** → there is nothing to loop against. Say so and build it straight.
