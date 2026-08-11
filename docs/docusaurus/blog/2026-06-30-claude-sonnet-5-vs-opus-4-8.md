---
title: "Claude Sonnet 5 vs Opus 4.8: Benchmarks & Price"
description: "Sonnet 5 vs Opus 4.8 compared: Opus leads coding and reasoning by 0.5 to 6.6 points; Sonnet 5 ties knowledge work at ~40% less cost."
slug: claude-sonnet-5-vs-opus-4-8
date: 2026-06-30
authors:
  - max-ritter
tags:
  - models
---

Sonnet 5 vs Opus 4.8 compared: Opus leads coding and reasoning by 0.5 to 6.6 points; Sonnet 5 ties knowledge work at ~40% less cost.

<!-- truncate -->

Claude Sonnet 5 vs Opus 4.8 is the cost-versus-capability decision every Claude Code developer faces as of June 30, 2026. The honest answer from Anthropic's own benchmark chart: Opus 4.8 leads on coding, terminal use, computer use, and reasoning by margins of half a point to 6.6 points; the two effectively tie on knowledge work (GDPval-AA v2: Sonnet 5 1,618, Opus 4.8 1,615); and Sonnet 5 costs about 40% less per token at standard rates ($3/$15 vs $5/$25), less still during its introductory window. The practical takeaway is simple: make [Sonnet 5](/blog/claude-sonnet-5) your default daily driver and escalate to [Opus 4.8](/blog/claude-opus-4-8) for the hardest agentic-coding and max-accuracy work.

## TL;DR: Who Wins What

| Category | Winner | Margin |
| --- | --- | --- |
| Agentic coding (SWE-bench Pro) | Opus 4.8 | +6.0 points (69.2% vs 63.2%) |
| Terminal tasks (Terminal-Bench 2.1) | Opus 4.8 | +2.3 points (82.7% vs 80.4%) |
| Computer use (OSWorld-Verified) | Opus 4.8 | +2.2 points (83.4% vs 81.2%) |
| Reasoning, no tools (HLE) | Opus 4.8 | +6.6 points (49.8% vs 43.2%) |
| Reasoning, with tools (HLE) | Effective tie | +0.5 to Opus (57.9% vs 57.4%) |
| Knowledge work (GDPval-AA v2) | Sonnet 5 | +3 points (1,618 vs 1,615) |
| Price per token | Sonnet 5 | ~40% cheaper standard, ~60% during intro |

The short version: Opus 4.8 holds the capability lead on every coding, terminal, computer-use, and reasoning row, by margins that range from negligible to clear. Sonnet 5 ties it on knowledge work and wins decisively on price. Neither model dominates. The right choice depends entirely on whether a few accuracy points or a 40%-plus cost cut matters more for the workload in front of you.

## Release Context: Where Each Model Sits

Anthropic shipped [Opus 4.8](/blog/claude-opus-4-8) on May 28, 2026 as its reliable flagship for daily agentic work, holding the standard tier at $5/$25 with a Fast mode at $10/$50. [Sonnet 5](/blog/claude-sonnet-5) followed on June 30, 2026 as "the most agentic Sonnet model yet," superseding Sonnet 4.6 and launching as the default model on the Free and Pro plans.

Two facts frame the comparison. First, Opus 4.8 is not the top of Anthropic's lineup; [Fable 5](/blog/claude-fable-5-mythos-5), the first public Mythos-class model, sits above it at $10/$50. So this is a comparison of the daily workhorse against the reliable flagship, not against the frontier. Second, Anthropic explicitly frames the two as an effort dial rather than a hard line. Its own guidance: "Opus 4.8 ... is still the model of choice for higher accuracy on these tasks, but Sonnet 5 provides developers with lower-priced options," and "Between Sonnet 5 and Opus 4.8, users can adjust the effort level to find the right balance of cost and performance."

## Benchmarks: The Full Head-to-Head

Every number below comes from Anthropic's published Sonnet 5 benchmark chart, which carries an Opus 4.8 column for reference. It is the cleanest apples-to-apples source because both models were measured on the same harness for the same release.

| Benchmark | Sonnet 5 | Opus 4.8 | Edge |
| --- | --- | --- | --- |
| **SWE-bench Pro (agentic coding)** | 63.2% | 69.2% | Opus +6.0 |
| **Terminal-Bench 2.1 (agentic coding)** | 80.4% | 82.7% | Opus +2.3 |
| **Humanity's Last Exam (no tools)** | 43.2% | 49.8% | Opus +6.6 |
| **Humanity's Last Exam (with tools)** | 57.4% | 57.9% | Tie (+0.5) |
| **OSWorld-Verified (computer use)** | 81.2% | 83.4% | Opus +2.2 |
| **GDPval-AA v2 (knowledge work)** | 1,618 | 1,615 | Sonnet 5 +3 |

Read the table honestly and the picture is consistent. Opus 4.8 wins the two agentic-coding rows, computer use, and both reasoning rows. The margins matter as much as the direction: the SWE-bench Pro gap (6.0 points) and the no-tools reasoning gap (6.6 points) are the two places Opus 4.8 earns its premium, while Terminal-Bench (2.3), OSWorld (2.2), and with-tools reasoning (0.5) are close enough that most workloads would not feel the difference. The single row where Sonnet 5 noses ahead is knowledge work, and at 1,618 vs 1,615 that is a statistical tie, not a Sonnet win you would build a decision on.

The way to read this: Sonnet 5 does not match Opus 4.8 on raw capability, and Anthropic does not claim it does. What it does is land within a few points across the board while costing far less, which is exactly what makes it the better default for high-volume work where the accuracy delta does not justify the price delta.

## Pricing: The Real Reason to Choose Sonnet 5

| Tier | Sonnet 5 | Opus 4.8 |
| --- | --- | --- |
| **Standard input (per 1M)** | $3 | $5 |
| **Standard output (per 1M)** | $15 | $25 |
| **Introductory (through Aug 31, 2026)** | $2 / $10 | not offered |
| **Fast / high-throughput tier** | not offered | $10 / $50 |

At standard rates, Sonnet 5 costs 40% less per token than Opus 4.8 on both input and output. To make that concrete, a job that sends 1M input tokens and generates 200K output tokens runs about **$10 on Opus 4.8** ($5 + $5), **$6 on Sonnet 5 standard** ($3 + $3), and **$4 on Sonnet 5 during the introductory window** ($2 + $2). Across a high-volume agentic pipeline making thousands of those calls, that is the difference between a hobby budget and a production line item.

One honest caveat keeps the gap from being quite as wide as the sticker price suggests. Sonnet 5 ships an updated tokenizer that maps the same text to roughly 1.0 to 1.35x more tokens than prior generations, so a like-for-like task sends more tokens on Sonnet 5 than on Opus 4.8. The introductory pricing exists partly to absorb that during the transition. If your spend is sensitive, run a token count on representative traffic before assuming the full 40% saving. Prompt caching (up to 90%) and the Batch API discount (50%) apply on both models and narrow the absolute cost either way.

The broader principle behind this table is to run the expensive model only where it changes the answer, which our usage optimization guide covers in full.

## Specs: Nearly Identical Where It Counts

| Spec | Sonnet 5 | Opus 4.8 |
| --- | --- | --- |
| **API ID** | `claude-sonnet-5` | `claude-opus-4-8` |
| **Released** | June 30, 2026 | May 28, 2026 |
| **Context window** | 1M tokens | 1M tokens |
| **Max output** | 128K (up to 300K via Batch beta) | 128K (up to 300K via Batch beta) |
| **Knowledge cutoff** | January 2026 | January 2026 |
| **Standard pricing** | $3/$15 ($2/$10 intro) | $5/$25 ($10/$50 Fast mode) |
| **Default plans** | Free and Pro (and up) | Pro, Max, Team, Enterprise |

The specs tell their own story: on the things that usually differentiate a tier, Sonnet 5 and Opus 4.8 are the same. Both carry a 1M-token context window at standard pricing with no long-context premium, both cap output at 128K tokens per response (up to 300K via the Batch API beta), and both share a January 2026 knowledge cutoff. The meaningful spec difference is availability: Sonnet 5 is the default on the no-cost Free tier, while Opus 4.8 starts at Pro. If you want frontier-adjacent agentic coding without a subscription, Sonnet 5 is the only one of the two you can run for free.

## Which Should You Use?

The decision matrix below maps workloads to the model that wins them. Pick on your dominant use case, not the average.

| Use case | Recommended model | Why |
| --- | --- | --- |
| Daily coding and fast iteration | Sonnet 5 | Within 6 points of Opus on SWE-bench Pro at 40% less |
| High-volume agentic pipelines | Sonnet 5 | Cost compounds across thousands of calls |
| Free-tier or no-subscription use | Sonnet 5 | The only one of the two on the Free plan |
| Knowledge work and analysis | Sonnet 5 | Ties Opus 4.8 on GDPval-AA v2 (1,618 vs 1,615) |
| Correctness-critical agentic coding | Opus 4.8 | +6.0 SWE-bench Pro is the accuracy you pay for |
| Hard multi-step reasoning without tools | Opus 4.8 | +6.6 on Humanity's Last Exam (no tools) |
| Long-horizon work where small errors compound | Opus 4.8 | A 2 to 6 point edge per step adds up over a session |
| The most safety-sensitive or regulated workloads | Opus 4.8 | Lower misaligned-behavior rate than Sonnet 5 |

The practical rule mirrors Anthropic's own effort-dial framing: default to Sonnet 5, and escalate to Opus 4.8 only when a specific task justifies the premium. For the rare long-horizon job where even Opus 4.8 is not enough, [Fable 5](/blog/claude-fable-5-mythos-5) sits above it. For tactical switching across the whole lineup, see the model selection guide. Wiring this choice into a multi-agent setup instead of picking per-prompt is the same tradeoff one level down: [pair a strong planner with cheaper workers](/blog/sub-agent-best-practices).

## How to Switch Between Them in Claude Code

Set Sonnet 5 as your default for everyday work:

```
claude config set model claude-sonnet-5
```

When a task needs Opus 4.8's accuracy, escalate for that session or that turn:

```
claude --model claude-opus-4-8
```

Or switch on the fly inside an interactive session:

```
/model claude-opus-4-8
```

## Frequently Asked Questions

**Is Opus 4.8 better than Sonnet 5?** On raw capability, yes, narrowly. Opus 4.8 leads Sonnet 5 on coding (SWE-bench Pro 69.2% vs 63.2%), terminal use (82.7% vs 80.4%), computer use (83.4% vs 81.2%), and reasoning (Humanity's Last Exam no-tools 49.8% vs 43.2%). The two tie on knowledge work. Sonnet 5 wins on price, costing about 40% less per token.

**How much cheaper is Sonnet 5 than Opus 4.8?** About 40% per token at standard rates ($3/$15 vs $5/$25), and roughly 60% cheaper during the introductory window ($2/$10 through August 31, 2026). A 1M-input, 200K-output job is about $6 on Sonnet 5 standard versus $10 on Opus 4.8.

**Which model should I use as my default in Claude Code?** Sonnet 5, for most developers. It lands within a few points of Opus 4.8 across the board at significantly lower cost, which is the right tradeoff for daily, high-volume work. Reserve Opus 4.8 for correctness-critical agentic coding and the hardest reasoning.

**Do Sonnet 5 and Opus 4.8 have the same context window?** Yes. Both offer a 1M-token context window at standard pricing with no long-context premium, and both cap output at 128K tokens per response (Sonnet 5 supports up to 300K via the Batch API extended-output beta).

**Is Sonnet 5 available on the free plan and Opus 4.8 isn't?** Correct. Sonnet 5 is the default model on the claude.ai Free tier and on Pro. Opus 4.8 is included starting at Pro and is not on the Free tier.

**Should I switch my whole pipeline from Opus 4.8 to Sonnet 5?** Not wholesale. Pilot Sonnet 5 on your top workloads and measure accuracy and cost on your real data, accounting for the tokenizer change that maps the same input to slightly more tokens. Keep Opus 4.8 in the loop for the tasks where the accuracy gap actually shows up.

## Related Pages

- [Claude Sonnet 5](/blog/claude-sonnet-5) for the full Sonnet 5 release: specs, benchmarks, and pricing
- [Claude Opus 4.8](/blog/claude-opus-4-8) for the full Opus 4.8 release and why it is the reliable flagship
- [GLM 5.2 vs Opus 4.8 vs Sonnet 5](/blog/glm-5-2-vs-opus-4-8-vs-sonnet-5) to add the leading open-weights model to this comparison
- Every Claude Model for the complete timeline from Claude 3 to Opus 5
- Model selection guide for switching models tactically mid-session
- Usage optimization for routing cheap work to Sonnet and reserving Opus
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** handles model routing in one config file: Opus for `/spec` planning, Sonnet for everyday iteration, Haiku for trivial calls. You set the policy; Pilot Shell picks per request.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
