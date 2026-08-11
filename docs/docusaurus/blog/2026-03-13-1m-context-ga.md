---
title: "Claude Code 1M Context Window: What It Means for You"
description: "Claude Code's 1M context window is live at no extra cost. Load entire codebases, run agents for hours, and stop managing tokens."
slug: 1m-context-ga
date: 2026-03-13
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Claude Code's 1M context window is live at no extra cost. Load entire codebases, run agents for hours, and stop managing tokens.

<!-- truncate -->

Claude Code users have been fighting context limits since day one. Today, that fight got a lot smaller. Anthropic just expanded the **Claude Code context window** to 1 million tokens -- generally available for [Opus 4.6](/blog/claude-opus-4-6) and [Sonnet 4.6](/blog/claude-sonnet-4-6), no beta headers, no long-context surcharge, no waiting list. If you're on Max, Team, or Enterprise, you already have it.

This isn't a version bump. It's a 5x expansion of the working memory your agent uses to understand your codebase, hold tool call traces, and maintain reasoning chains across long sessions. And the pricing stays flat -- a 900K-token request costs exactly the same per token as a 9K one.

## Before and After: 200K vs 1M

| Metric | Before (200K) | After (1M) |
| --- | --- | --- |
| Usable tokens | ~167K | ~830K |
| Compaction frequency | Every 20-30 min on complex tasks | 15% fewer events |
| Files loadable | Small project | Entire monorepo |
| Media items per request | 100 | 600 |
| Long-context pricing | Premium ($10/$37.50 for Opus) | Same rate as short requests |
| Beta header required | Yes (over 200K) | No |

## What Changed in the 1M Context Window

The 1M context window existed in beta for months. What's different at GA is that Anthropic removed every friction point that made the beta feel like a second-class experience.

**Unified pricing across the full window.** No long-context premium. [Opus 4.6](/blog/claude-opus-4-6) bills at $5/$25 per million tokens (input/output). [Sonnet 4.6](/blog/claude-sonnet-4-6) bills at $3/$15. Whether your request uses 10K tokens or 950K tokens, the per-token rate is identical.

**Full rate limits at every context length.** During beta, longer requests sometimes hit lower rate limits. That restriction is gone. A 1M-token request gets the same throughput as a short one.

**600 media items per request.** The previous limit was 100 images or PDF pages. That's now 6x higher at 600. If you work with design systems, documentation sets, or contract review, this matters.

**No beta header required.** Requests over 200K tokens previously needed a special `anthropic-beta` header. Existing headers are silently ignored now. The API just works.

**Multi-cloud availability.** The 1M window is live on Claude Platform, Microsoft Azure Foundry, and Google Cloud Vertex AI.

## How the 1M Context Window Changes Claude Code

For API users, this is a pricing and convenience improvement. For Claude Code users, it's structural.

### Fewer Auto-Compaction Events

If you've used Claude Code on any serious project, you know the compaction problem. You load a codebase, run a chain of tool calls, build up reasoning context -- and then auto-compaction triggers. Claude summarizes your conversation to free space, and in the process loses nuance, forgets edge cases, and drops the thread on complex multi-step tasks.

Jon Bell, Anthropic's CPO, put a number on the improvement: **a 15% decrease in compaction events** since the 1M window shipped. That's not a benchmark -- that's measured across real Claude Code usage. Agents now hold their full context and run for hours without forgetting what they read on page one.

For context on how compaction works and what triggers it, see the [context buffer management guide](/blog/context-buffer-management). The short version: Claude Code reserves a buffer (currently ~33K tokens) and compacts when usage hits about 83.5%. With a 1M window, you have roughly 5x the usable space before that threshold arrives.

### Entire Codebases in One Window

A 200K context window holds roughly 150K tokens of usable space after the compaction buffer. That's enough for a small project but forces constant file selection on anything substantial.

At 1M tokens, you're looking at ~830K usable tokens. That's thousands of source files. Entire monorepos. Full documentation sets alongside the code they describe. The practical difference: Claude can see both your API layer and the frontend consuming it, both the migration and the schema it modifies, both the test suite and the code under test -- simultaneously, without needing you to manually manage which files are loaded.

### Long-Running Agent Traces

This is the change that matters most for [agent teams](/blog/agent-teams) and complex orchestration workflows. Every tool call, every intermediate reasoning step, every file read -- these accumulate as context. In a 200K window, a multi-agent session doing real work can burn through context in 20-30 minutes.

Anton Biryukov, a software engineer at Ramp, described the old reality: "Claude Code can burn 100K+ tokens searching Datadog, Braintrust, databases, and source code. Then compaction kicks in." With 1M context, he searches, re-searches, aggregates edge cases, and proposes fixes -- all in one window without losing any intermediate findings.

## Can Claude Actually Use 1M Tokens? Benchmark Results

Raw context size is useless if the model can't actually recall and reason over what's in there. Anthropic published two benchmarks that test exactly that at the 1M token mark.

**Opus 4.6 scores 78.3% on MRCR v2 at 1M tokens.** MRCR (Multi-Round Coreference Resolution) tests whether the model can track entities and relationships across an enormous context. Nearly 80% accuracy across a million tokens means the model isn't just holding the text -- it's maintaining meaningful connections between distant parts of it.

**Sonnet 4.6 scores 68.4% on GraphWalks BFS at 1M tokens.** This benchmark tests the model's ability to traverse graph structures embedded in long contexts -- essentially, can it follow chains of references across hundreds of thousands of tokens? Both scores are reported as the highest among frontier models at these context lengths.

For practical Claude Code work, this translates to: the model can still find that utility function defined 500K tokens ago and understand how it connects to the component you're currently modifying.

## Practical Implications for Your Workflow

### What You Should Do Differently

**Stop micro-managing file inclusion.** With 200K, every `@file` directive was a tradeoff. At 1M, load the files you need and stop worrying about the budget. Include the test file alongside the implementation. Load the types alongside the component. Let Claude see the full picture.

**Run longer sessions.** The instinct to start fresh every 30 minutes came from necessity, not preference. With 5x the context, sessions can run for hours on complex tasks. Save restarts for genuine shifts in focus, not buffer anxiety. For strategies on when to compact versus continue, see the context management guide.

**Trust multi-step agent workflows.** The biggest unlock isn't for simple edits -- it's for the kind of work where Claude needs to research, plan, implement, and verify across many files. That workflow used to fall apart when compaction hit mid-process. Now the entire chain fits comfortably.

**Rethink [context engineering](/blog/context-engineering) strategy.** Your strategies for loading and preserving context still matter -- they just have more room to breathe. The fundamentals from our context management guide still apply, but the urgency shifts from "survive within 200K" to "use 1M effectively."

### What Stays the Same

Context discipline still matters. A 1M window is not an invitation to dump everything in and hope for the best. Loading irrelevant files wastes tokens and dilutes the signal Claude uses to prioritize its attention.

[CLAUDE.md files](/blog/claude-md-mastery), skills-first loading, and structured session management remain best practices. They just operate with more headroom. If you're already following usage optimization patterns, you'll get even more out of the expanded window.

## Which Plans Get the 1M Context Window

**Claude Code users on Max, Team, and Enterprise plans** get the 1M context window automatically with Opus 4.6. No configuration needed. The previously required extra usage allocation for long-context requests is gone.

**API users** get it at the standard per-token rates. Opus 4.6 at $5/$25 per million tokens. Sonnet 4.6 at $3/$15. No premium tier for long context.

**The 200K window still exists** as the default for standard API requests and lower-tier plans. The 1M window is specifically available on Opus 4.6 and Sonnet 4.6.

## What This Signals

Anthropic isn't just making context windows bigger. They're removing the tradeoffs that made large context windows impractical. Unified pricing means you don't have to budget differently for long requests. Full rate limits mean you don't sacrifice throughput. Removing the beta header means existing code just works.

The direction is clear: context management is moving from a user problem to an infrastructure problem. The models get better at using long context. The pricing makes it accessible. The tooling adapts automatically.

For Claude Code users, the immediate takeaway is simple: your agents can now think longer and remember more. Build your workflows around that capability, and you'll find that tasks that previously required careful session management and manual context curation just work -- end to end, in a single window.

## Related Resources

- [Context Buffer Management](/blog/context-buffer-management) -- How auto-compaction works and the 33K token buffer
- [Context Engineering](/blog/context-engineering) -- The six pillars framework for loading context strategically
- Context Management -- Strategies for keeping critical context intact across sessions
- Model Selection Guide -- Choosing between Opus 4.6 and Sonnet 4.6 for different tasks
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
