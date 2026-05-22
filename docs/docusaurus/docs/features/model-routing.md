---
sidebar_position: 5
title: Model Routing
description: Plan with Opus, implement with Sonnet — without juggling config files.
---

# Model Routing

There's one switch: Claude Code's `/model`. Whatever you set there is what every Pilot workflow uses. No per-skill table, no Pilot-side override.

The interesting question is *when* to switch. Opus reasons better; Sonnet is faster and cheaper. The cost-saving move is to plan on Opus, then drop to Sonnet for the mechanical work that follows.

## The Default Flow With `/spec`

The Model Switching toggle (on by default) builds the swap into the spec workflow:

1. `/model opus[1m]` — Pilot refuses to start `/spec` on Sonnet.
2. `/spec <what you want>` — Pilot drafts the plan and asks for approval.
3. Approve. Pilot prints a short handoff message and stops.
4. Switch models — two paths below.

You only see the pause once per spec run. Implementation and verification then run on whatever you picked.

If your Claude plan already defaults to Opus, step 1 isn't strictly required — `/spec` will start on default Opus too. The explicit `/model opus[1m]` is for the 1M context window, which planning benefits from on larger codebases. Same for the Sonnet switch later: `sonnet` works, `sonnet[1m]` gives you the bigger context. You type whichever variant fits the session.

## Path A — Switch in Place

```text
/model sonnet[1m]
continue
```

Same session, planning context comes with you. Any prompt resumes (`continue`, `go`, anything).

Claude Code will ask to confirm the model switch — the planning context gets re-sent to Sonnet on the next turn, which costs Sonnet input tokens once. Small for short plans, noticeable for long ones.

Pick this when planning was short, or when you want Sonnet to be able to refer back to the discussion.

## Path B — Clean Start

```text
/clear
/model sonnet[1m]
/spec docs/plans/2026-05-21-your-plan.md
```

Fresh session, no context carry. Sonnet sees only the plan file. The dispatcher notices it's already approved and goes straight into implementation.

Pick this when planning was long, when you want lower first-turn cost, or when you're picking the plan back up later.

Both paths run the same `spec-implement` on Sonnet — they differ only in what's in context when it starts.

## Skip the Pause

Stay on one model end-to-end by turning off **Model Switching** in Console Settings → Automation. `/spec` then runs plan → implement → verify continuously. Also the right setting for headless / CI.
