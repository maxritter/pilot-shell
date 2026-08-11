---
title: "Claude Code Limits Doubled: 5x More With Smart Routing"
description: "Anthropic doubled Claude Code's 5-hour windows and removed peak throttling. The weekly cap is the real limit. How to absorb the new throughput."
slug: higher-usage-limits
date: 2026-05-06
authors:
  - max-ritter
tags:
  - guide
  - development
---

Anthropic doubled Claude Code's 5-hour windows and removed peak throttling. The weekly cap is the real limit. How to absorb the new throughput.

<!-- truncate -->

Anthropic [announced this morning](https://www.anthropic.com/news/higher-limits-spacex) that Claude Code's 5-hour rate limits are doubling for every Pro, Max, Team, and seat-based Enterprise account. Peak-hour throttling on Pro and Max is gone. Opus API rate limits went up. All effective today.

That's the headline. The amount of work you can push through Claude Code in a single 5-hour window just doubled.

The part most people will misread: today's change only touches the 5-hour rate-limit window and the peak-hour throttle. On the day this shipped, the weekly cap itself stayed exactly the size it was the day before. What's different is the size of the spigot draining out of that bucket during your actual work hours.

> **Correction (2026-07-25):** The paragraph above is still true about the size of the weekly bucket, but since July 20, 2026 it no longer tells you everything you need. [Claude Fable 5](/blog/claude-fable-5-mythos-5) does not get a bucket of its own. On Max plans and premium Team and seat-based Enterprise seats it draws on the **same** weekly allowance as every other model, capped at **50% of it**, and it weighs roughly double an Opus session against that allowance. On Pro plans and standard seats it runs on prepaid usage credits instead. So the practical failure mode is new even though the cap size is not: Fable can hit its half-of-the-bucket ceiling while [Opus 5](/blog/claude-opus-5) still has plenty of room, and the fix is to switch models rather than wait for a reset. See [how Fable 5 draws on your weekly allowance](/blog/fable-5-usage-credits) for the current terms.

That distinction matters, because it changes what "doubled limits" actually means in practice. It isn't more total capacity. It's more bandwidth to absorb the capacity you already had. Most users were leaving weekly headroom on the table because the per-window throttle and peak-hour clip stopped them from reaching it during the hours they were actually at the keyboard. Now they can.

This post covers what actually changed, what didn't, why bandwidth matters more than ceiling for most users, and the routing and efficiency patterns that turn the new headroom into shipped work.

## What Anthropic Actually Shipped Today

The [announcement post](https://www.anthropic.com/news/higher-limits-spacex) is short. Three concrete changes, all effective today:

1. **Claude Code's 5-hour rate limits are doubled.** Applies to Pro, Max, Team, and seat-based Enterprise. Whatever your old per-window cap was on Sonnet and Opus inside Claude Code, double it.
2. **Peak-hour throttling on Claude Code is removed for Pro and Max.** Anthropic had been quietly clipping limits during high-traffic windows. That clip is gone for the two tiers most likely to feel it.
3. **Opus API rate limits are raised considerably.** Higher per-minute and per-day ceilings for anyone hitting Opus through the API. The published table is in their post.

The why behind the change is short too. Anthropic is bringing on more compute. The headline partnership is a SpaceX/xAI deal that adds Colossus 1 -- 300 megawatts and 220,000+ NVIDIA GPUs -- to Claude infrastructure inside the next month. That sits on top of existing buildouts with AWS Trainium, Google TPUs, and NVIDIA GPU partners. More capacity, looser limits.

For context on how Pro and Max compare structurally, and what counts toward the 5-hour window in the first place, see our [Claude Code subscription guide](/blog/claude-code-subscription) and the usage optimization guide. The new limits don't change the OAuth versus API-key boundary. They only change the size of the spigot.

## What's Doubled, and What Isn't

Read the announcement carefully and the wording is precise. Anthropic doubled the **five-hour rate limits**. They removed the **peak-hour limit reduction**. They did not say anything about weekly caps.

Here's the practical decomposition:

| Limit type | Before today | After today |
| --- | --- | --- |
| Per 5-hour window | Baseline cap, throttled during peak | 2x baseline, no peak throttle (Pro/Max) |
| Weekly cap | Standing cap on weekly consumption across all models | Same standing cap |
| API Opus rate limit | Lower per-minute and per-day | Considerably higher |

Subscription allowances run on exactly two windows, a rolling five-hour one and a weekly one, and they are shared with Claude chat and Cowork rather than being Claude Code's alone. There is no monthly cap to reason about. The 5-hour window resets every five hours; the weekly cap is the absolute ceiling on what you can spend across a rolling seven-day period. Today's change widens the per-window pipe; it does not widen the weekly tank.

That sounds like a smaller win, and it is. But the working assumption that most users were maxing their weekly cap was already wrong. Most weren't. They were being clipped inside individual work sessions by the per-window throttle and the peak-hour cut, and walking away from a session with weekly headroom they couldn't actually consume during the hours they were at the keyboard.

What this announcement does, in effect, is unblock your weekly cap during the hours you actually want to use it.

## The Real Bottleneck Just Moved

If you've been bumping into the 5-hour ceiling, doubling it feels like the entire story. It isn't.

The real bottleneck for most Claude Code users isn't the size of any one bucket. It's the rate at which you spend, multiplied by where you're spending. Run Opus on every step of every task and you'll burn through the doubled per-window cap as fast as you used to burn through the old one, then crash into the unchanged weekly cap days earlier in the week. The ceilings move; your spend pattern moves to match; you hit the same wall in a different shape.

Here's what you actually want to do with the extra room: spend it on the steps that change the outcome of the run, and stop spending it on the steps that don't.

## The Opus-Sonnet-Opus Pipeline

**Stage 1: Planning. Run on Opus.** Master Orchestrator decomposes the request, picks specialists, writes the plan file. Deeper reasoning at this step changes the structure of every downstream task. This is the one place where pinching tokens is genuinely expensive.

**Stage 2: Execution. Run on Sonnet.** The specialist agents implement against the plan. This is the stage that absorbs the bulk of a session's tokens, because implementation reads and writes far more than planning does. It's also where Sonnet tracks Opus most closely on real coding work.

**Stage 3: Review and validation. Run on Opus.** frontend-specialist and debugger-detective stay on Opus. These are the agents catching subtle correctness issues before the work ships. Same logic as Stage 1: the cost of a missed defect is much higher than the cost of the deeper model.

Bookend on Opus, middle on Sonnet. Moving the heaviest stage down a tier is the whole trick, and the size of the win is worth stating accurately rather than optimistically. **On current API list prices, Opus 5 costs 1.67x Sonnet 5's standard $3/$15 rate, and 2.5x during Sonnet 5's introductory window through August 31, 2026.** Older guidance puts that ratio at 5x, which came from Opus 4.1 at $15/$75 against Sonnet at $3/$15; Opus 4.1 is deprecated and retires on August 5, 2026, so that number describes a model you should not be routing to anyway.

On a subscription you are not billed per token at all, and Anthropic does not publish the per-model weightings behind the usage bars, so treat the price ratio as the direction of the effect rather than its exact size on a plan. The one weighting Anthropic has published is Fable 5, which draws roughly double an Opus session against your weekly allowance. What holds either way: execution is the largest stage, Sonnet is materially cheaper per unit of it, and moving that stage down a tier is the highest-leverage routing change available. The model selection guide walks through the trade-offs across [Opus 5](/blog/claude-opus-5), [Sonnet 5](/blog/claude-sonnet-5), [Fable 5](/blog/claude-fable-5-mythos-5), and Haiku 4.5.

This bookend-Opus, middle-Sonnet split is the Fable orchestrator under an older name, built before Fable 5 existed to fill the top tier. For the current version of the pattern, with Fable 5 planning, Sonnet executing, and the cost benchmarks behind it, see the usage optimization guide. The same split is the advice behind our sub-agent guide too: [assign a cheaper model to the sub-agents doing the execution](/blog/sub-agent-best-practices). Not every job is worth splitting this way, though. Read [the tasks where this pipeline is not worth its coordination cost](/blog/multi-agent-orchestration-cost) before you wire it into a workflow by default.

## Efficiency Patterns That Compound With the New Throughput

The doubled 5-hour window is wasted on a session that burns tokens on bad context, redundant reads, or runaway loops. The patterns that turn raw throughput into shipped work are the same ones that mattered before today; they just matter more now that you actually have the bandwidth to feel them.

The four patterns that compound hardest with the new caps:

- **Context discipline.** Long, sloppy sessions with stale CLAUDE.md and bloated tool output spend tokens on noise. The context management guide covers compaction strategy and `/clear` discipline. The [context engineering walkthrough](/blog/context-engineering) goes deeper on what to load and what to leave out. For longer-running sessions, the [context buffer management](/blog/context-buffer-management) post covers the buffer hygiene that keeps quality from collapsing past the 70% mark.
- **Plan before you build.** Plan mode (press Shift+Tab to cycle into it) is the cheapest leverage point in Claude Code. Cheap because planning runs on Opus and produces a structure that Sonnet can execute against. Expensive when you skip it. The planning modes guide covers when to use it.
- **Speed and efficiency patterns.** Our efficiency patterns post covers the workflow-level moves that cut wasted iterations -- batching, fewer reads per turn, tighter tool calls. The speed optimization guide covers what to do when latency is the actual problem. [Fast mode](/blog/fast-mode) is the right default when you're doing high-volume Sonnet execution work.
- **Reach for deep thinking only where it pays.** Deep thinking techniques are expensive on the bucket. They're worth it on architectural decisions and ambiguous debugging; they're waste on routine implementation. Same logic as the Opus-Sonnet-Opus split, applied per-prompt.

None of these are new. They were already best practice. What's new is that the per-window cap no longer hides the cost of skipping them.

## How to Apply This Without Rebuilding Your Workflow

You don't need our framework to use any of this. The principle is portable.

**Default your shell to Sonnet.** `/model sonnet` at the start of every session. This is the single highest-leverage habit for stretching the new doubled cap.

**Reach for Opus only at the planning and review boundaries.** Architectural decisions, ambiguous requirements, post-implementation review of anything touching auth, payments, or migrations. Use `opusplan` if you want planning on Opus and execution on Sonnet automatically.

**Watch your absorption rate, not just your ceiling.** With the per-window cap doubled and peak throttling gone, the new constraint for heavy users is the weekly cap, not the per-session one. Track how much of your weekly budget you're actually using. If you're running well under 80% per week, the new throughput is pure upside -- absorb it. If you're already brushing 100%, the routing patterns above are how you stay productive without paying for an upgrade.

## What This Compounds To

Take a Max 20x account that used to cap around 900 messages per 5-hour window. The doubled per-window limit is now ~1,800. Run that on Opus end-to-end and you'll empty your weekly bucket faster than ever, because the weekly cap didn't move.

Run the same volume through the Opus-Sonnet-Opus pipeline and the bulk of those calls move to Sonnet, which costs less than half of Opus per token on current list prices. The blended draw on your weekly bucket drops well below the all-Opus baseline, and the new doubled per-window throughput lets you actually pull that work into the hours you're at the keyboard. How far it stretches depends on your mix, which is why the first instruction in this post is to run `/usage` and read your own breakdown rather than trust a multiplier from someone else's session.

The compute on the other end of this -- Colossus 1, AWS Trainium, the Google TPU build -- is finite. The new throughput will only feel like throughput if you spend it on the work that benefits from compounded capacity. Routing and context discipline are what turn a bandwidth bump into actual shipped output.

## Make the New Ceiling Count

Today's change is the largest single increase to Claude Code's per-window limits Anthropic has shipped. It also won't matter much for developers who route every task through Opus and run out of weekly room twice as fast as before. The pattern that does matter is the one underneath -- which model handles which step, what stays in context, and what gets compacted out.

Opus on the bookends. Sonnet in the middle. Tight context, plan first, fast mode for the volume work.

Either way, today is a good day to stop running Opus by default.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
