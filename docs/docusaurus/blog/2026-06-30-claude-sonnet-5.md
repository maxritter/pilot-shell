---
title: "Claude Sonnet 5: Near-Opus Coding, Sonnet Price"
description: "Claude Sonnet 5 scores 63.2% agentic coding at $2/$10 per million tokens (intro), closing the gap with Opus 4.8. Specs, benchmarks, pricing."
slug: claude-sonnet-5
date: 2026-06-30
authors:
  - max-ritter
tags:
  - models
---

Claude Sonnet 5 scores 63.2% agentic coding at $2/$10 per million tokens (intro), closing the gap with Opus 4.8. Specs, benchmarks, pricing.

<!-- truncate -->

**Claude Sonnet 5 costs $2 per million input tokens and $10 per million output tokens** through August 31, 2026, then moves to the standard Sonnet rate of $3/$15. It is the **default model on the Free and Pro plans** and available to Max, Team, and Enterprise. On Anthropic's headline agentic coding benchmark (SWE-bench Pro) it scores **63.2%**, against **69.2% for [Opus 4.8](/blog/claude-opus-4-8)** and **58.1% for the [Sonnet 4.6](/blog/claude-sonnet-4-6) it replaces**, and it edges past Opus 4.8 on knowledge work. The API model ID is `claude-sonnet-5`, and it shipped **June 30, 2026**. Every number on this page is grounded in Anthropic's [official Sonnet 5 announcement](https://www.anthropic.com/news/claude-sonnet-5) and [system card](https://www.anthropic.com/claude-sonnet-5-system-card).

Anthropic calls Sonnet 5 "the most agentic Sonnet model yet." The pitch is specific: it can make plans, drive browsers and terminals, and run autonomously through long, multi-step tasks at a level that, in Anthropic's framing, previously required larger and more expensive models. That makes Sonnet 5 the new workhorse for daily agentic coding, the model you leave running by default and only escalate to [Opus 4.8](/blog/claude-opus-4-8) when a task genuinely needs the extra accuracy. It supersedes [Sonnet 4.6](/blog/claude-sonnet-4-6) as the recommended Sonnet across every plan.

## Quick Answers: Pricing, Free Access, and Specs

If you came here for one number, here it is. These are the facts most people search for, answered directly and grounded in Anthropic's release.

- **How much does Sonnet 5 cost?** $2 per million input tokens and $10 per million output tokens during the introductory window through August 31, 2026, then $3 input / $15 output per million from September 1, 2026.
- **Is Claude Sonnet 5 free?** Yes, in the everyday sense. It is the default model on the claude.ai free tier and on Pro, and it is available on Max, Team, and Enterprise. API access is paid at the rates above.
- **What is the context window?** 1 million tokens, with a 128,000-token max output (up to 300,000 via the Batch API extended-output beta).
- **When was it released?** June 30, 2026. The API ID is `claude-sonnet-5`.
- **How does it compare to Opus 4.8?** On SWE-bench Pro it trails Opus 4.8 by 6 points (63.2% vs 69.2%), it slightly outperforms Opus 4.8 on knowledge work, and it costs roughly half as much per token. Full table below.

For the model that still sits above it on raw accuracy, see [Opus 4.8](/blog/claude-opus-4-8). For the full lineup, see every Claude model.

## Key Specs

| Spec | Details |
| --- | --- |
| **API ID** | `claude-sonnet-5` |
| **Release Date** | June 30, 2026 |
| **Context Window** | 1M tokens |
| **Max Output** | 128,000 tokens (up to 300,000 via Batch API extended-output beta) |
| **Knowledge Cutoff** | January 2026 |
| **Tokenizer** | Updated tokenizer (same input maps to ~1.0 to 1.35x more tokens than prior gens) |
| **Intro Pricing** | $2 input / $10 output per 1M tokens (through Aug 31, 2026) |
| **Standard Pricing** | $3 input / $15 output per 1M tokens (from Sep 1, 2026) |
| **Availability** | claude.ai (default Free and Pro), Claude Code, Messages API, Bedrock, Vertex AI |
| **Status** | Active, current recommended Sonnet |

## What Changed: The Most Agentic Sonnet Yet

Sonnet 4.6 was a coding-quality release. Sonnet 5 is an autonomy release. The headline is not a single benchmark, it is how far the model will carry a task on its own before it stalls or asks for help.

**It finishes multi-step jobs end to end.** The behavior partners describe most often is sustained execution. Zapier's Daniel Shepard put it plainly: "We handed Claude Sonnet 5 a two-part job and it finished end to end. That used to stall halfway." Sualeh Asif at Cursor reported that "agents stay on plan, follow our conventions, and ship clean multi-step changes." That is the practical difference between a model you babysit and a model you delegate to.

**It debugs like an engineer, not a patcher.** Several teams flagged root-cause behavior over symptom-patching. Dominic Elm described Sonnet 5 tracing "a failure to its actual root cause" and shipping "a durable fix instead of patching the symptom," while Neel Chotai noted it "wrote a reproducing test, implemented the fix, then stashed it" unprompted. For agentic coding loops, that test-first instinct is what keeps an autonomous session from drifting.

**It knows when to say no.** Lovable's Fabian Hedin framed the safety gains as a capability, not a tax: "A model that knows when to say no is just as important as one that knows how to build." That matters more as Sonnet 5 takes on browser and terminal work where a wrong action has real consequences.

**The tokenizer changed.** Sonnet 5 ships an updated tokenizer that processes text differently to improve performance. The tradeoff is that the same input can map to roughly 1.0 to 1.35x more tokens depending on content type. Anthropic set the introductory pricing specifically to keep the transition "roughly cost-neutral" while the per-token math shifts, which is the real reason the cheap window exists.

## Benchmark Results

Sonnet 5 beats Sonnet 4.6 across the board and closes most of the distance to Opus 4.8. The numbers below come from Anthropic's published benchmark table (rendered as the chart on the announcement page and reported by [TechCrunch](https://techcrunch.com/2026/06/30/anthropic-launches-claude-sonnet-5-as-a-cheaper-way-to-run-agents/) and [The Decoder](https://the-decoder.com/anthropics-new-claude-sonnet-5-closes-the-gap-to-the-pricier-opus-model-series/)).

| Benchmark | Sonnet 5 | Sonnet 4.6 | Opus 4.8 |
| --- | --- | --- | --- |
| **SWE-bench Pro (agentic coding)** | 63.2% | 58.1% | 69.2% |
| **Terminal-Bench 2.1 (agentic coding)** | 80.4% | 67.0% | 82.7% |
| **Humanity's Last Exam (no tools)** | 43.2% | 34.6% | 49.8% |
| **Humanity's Last Exam (with tools)** | 57.4% | 46.8% | 57.9% |
| **OSWorld-Verified (computer use)** | 81.2% | 78.5% | 83.4% |
| **GDPval-AA v2 (knowledge work)** | 1,618 | 1,395 | 1,615 |

Read the table honestly and the hierarchy is intact: Opus 4.8 leads Sonnet 5 on coding, terminal, computer use, and reasoning, by margins from half a point (Humanity's Last Exam with tools, 57.9% vs 57.4%) to six-plus points (SWE-bench Pro, 69.2% vs 63.2%, and Humanity's Last Exam without tools, 49.8% vs 43.2%). The single exception is knowledge work, where Sonnet 5 edges ahead on GDPval-AA v2 (1,618 vs 1,615). The real headline is the jump over Sonnet 4.6: Terminal-Bench 2.1 climbs more than 13 points (80.4% vs 67.0%) and GDPval-AA v2 rises about 16% (1,395 to 1,618). That generational gain, not any claim of Opus parity, is what "most agentic Sonnet yet" buys you.

The shape of the comparison is the value prop: Sonnet 5 lands a few points behind Opus 4.8 on coding, terminal, and computer use, ties it on knowledge work, and costs 40% less at standard rates (and less than half its price during the introductory window). For most daily work, that gap is small enough that price, not capability, becomes the deciding factor.

## Safety Profile

Anthropic reports that Sonnet 5 has a lower overall rate of undesirable behaviors than Sonnet 4.6. It is better at refusing malicious requests and more resistant to prompt-injection attacks, and it shows lower hallucination and sycophancy rates than its predecessor. For teams running computer use or processing untrusted documents, the prompt-injection improvement is the one that matters most day to day.

There are two honest caveats. First, Sonnet 5's rate of misaligned behavior is higher than [Opus 4.8](/blog/claude-opus-4-8) and Claude Mythos Preview, so the most safety-critical workloads still belong on the higher-aligned models. Second, on cybersecurity, Anthropic notes Sonnet 5 has "much lower ability to perform dangerous cybersecurity tasks than our current Opus models." It cannot develop a working Firefox exploit (0.0% success), and cyber safeguards are enabled by default. The full evaluation set, including detailed alignment metrics and prompt-injection numbers, is in the [Claude Sonnet 5 system card](https://www.anthropic.com/claude-sonnet-5-system-card). Read it before deploying in a regulated or high-risk environment.

## Pricing: $2/$10 Intro, $3/$15 Standard

| Tier | Input (per 1M) | Output (per 1M) |
| --- | --- | --- |
| **Introductory (through Aug 31, 2026)** | $2 | $10 |
| **Standard (from Sep 1, 2026)** | $3 | $15 |

The standard $3/$15 rate is exactly where Sonnet has sat since the 4.5 generation, so the long-run price is unchanged. The introductory window is a real discount, not a gimmick: it offsets the new tokenizer's higher token counts so the move to Sonnet 5 stays roughly cost-neutral through the end of August. If you run high-volume agentic workloads, the two months before September 1 are the cheapest this model will ever be.

For context on where Sonnet 5 sits in the price ladder, the standard $3/$15 is 40% less than [Opus 4.8](/blog/claude-opus-4-8) at $5/$25 and less than a third the cost of [Fable 5](/blog/claude-fable-5-mythos-5) at $10/$50. TechCrunch notes Sonnet 5 also lands cheaper than OpenAI's GPT-5.5 and Google's Gemini 3.1 Pro and pricier than Gemini 3.5 Flash; Anthropic's own announcement makes no cross-vendor comparison. Prompt caching and the Batch API discount carry forward. If you are managing spend across a team, the usage optimization guide covers how to route cheap tasks here and reserve Opus for the work that needs it.

### Is Claude Sonnet 5 Free?

**Yes.** Sonnet 5 is the default model on the claude.ai free tier and on Pro, which is the most generous free access any agentic Claude model has launched with. "Free" here means included in a plan, including the no-cost tier, rather than free API calls. If you want Sonnet 5 without a subscription, you pay per token through the API at the rates above. There is no free API tier. For a side-by-side of what each plan includes, see the model selection guide.

## How to Use Sonnet 5 in Claude Code

Set Sonnet 5 as your default model:

```
claude config set model claude-sonnet-5
```

For a per-session override without changing your default:

```
claude --model claude-sonnet-5
```

Inside an interactive session, switch models on the fly with the slash command:

```
/model claude-sonnet-5
```

## Sonnet 5 vs Sonnet 4.6: What Changed

| Feature | Sonnet 4.6 | Sonnet 5 |
| --- | --- | --- |
| **SWE-bench Pro** | 58.1% | 63.2% |
| **Terminal-Bench 2.1** | 67.0% | 80.4% |
| **OSWorld-Verified** | 78.5% | 81.2% |
| **Humanity's Last Exam (tools)** | 46.8% | 57.4% |
| **GDPval-AA v2 (knowledge work)** | 1,395 | 1,618 |
| **Autonomy** | Strong coding, asks often | Plans, uses browsers/terminals, finishes end to end |
| **Safety** | Strong, on par with Opus 4.6 | Lower undesirable behaviors, better prompt-injection resistance |
| **Tokenizer** | Prior generation | Updated (~1.0 to 1.35x token counts) |
| **Max output** | 16,384 tokens | 128,000 tokens |
| **Standard pricing** | $3/$15 per 1M | $3/$15 per 1M ($2/$10 intro through Aug 31) |

Everything Sonnet 4.6 did well carries forward at the same long-run price. The upgrade is autonomy and reach: longer tasks completed without hand-holding, meaningfully stronger terminal and computer use, and a higher output ceiling. If you run Sonnet 4.6 today, switch to `claude-sonnet-5`. Existing prompts and Claude Code configs carry over.

## Sonnet 5 vs Opus 4.8: Which Should You Use?

This is the decision most developers actually face, and Anthropic frames it as an effort dial rather than a hard line. Its guidance: "Opus 4.8 ... is still the model of choice for higher accuracy on these tasks, but Sonnet 5 provides developers with lower-priced options." It adds: "Between Sonnet 5 and Opus 4.8, users can adjust the effort level to find the right balance of cost and performance."

| Use Sonnet 5 when... | Use Opus 4.8 when... |
| --- | --- |
| Daily coding, fast iteration, most agentic loops | Correctness-critical refactors and architecture calls |
| Cost matters and volume is high | The 6-point SWE-bench Pro accuracy gap pays for itself |
| Browser, terminal, and computer-use automation | Long-horizon work where a small error rate compounds |
| Knowledge work, where it ties Opus 4.8 | The most safety-sensitive or regulated workloads |

The practical rule: make Sonnet 5 your default and escalate to Opus 4.8 only when a specific task justifies the premium. For the full head-to-head on benchmarks, price, and specs, see [Sonnet 5 vs Opus 4.8](/blog/claude-sonnet-5-vs-opus-4-8). Above Opus 4.8 sits [Fable 5](/blog/claude-fable-5-mythos-5), the frontier model, for the rare long-horizon job where even Opus is not enough. For tactical switching during a session, see the model selection guide.

## Also Launched: Claude Science

Sonnet 5 did not ship alone. Anthropic announced **Claude Science**, a customizable app that integrates the tools and packages researchers use most, produces auditable artifacts, and provides flexible access to compute. It is aimed at research workflows rather than coding, but it underlines the direction: the same agentic reliability that makes Sonnet 5 a good daily driver is being packaged for science teams who need reproducible, auditable runs.

## Frequently Asked Questions

**Is Claude Sonnet 5 free?** Yes. It is the default model on the claude.ai free tier and on Pro, and it is available on Max, Team, and Enterprise. API access is paid at $2/$10 per million tokens through August 31, 2026, then $3/$15.

**What is the Sonnet 5 context window?** 1 million tokens, with a 128,000-token max output per response (up to 300,000 tokens through the Batch API extended-output beta).

**How does Sonnet 5 compare to Opus 4.8?** Sonnet 5 scores 63.2% on SWE-bench Pro versus Opus 4.8's 69.2%, slightly outperforms it on knowledge work (GDPval-AA v2), and nearly matches it on Humanity's Last Exam. Opus 4.8 keeps a clear edge only on pure agentic coding accuracy, at roughly double the price.

**Why is Sonnet 5 cheaper until August?** The introductory $2/$10 rate offsets the new tokenizer, which maps the same input to slightly more tokens. Anthropic set it to keep the upgrade roughly cost-neutral through August 31, 2026, after which standard $3/$15 pricing applies.

**Does Sonnet 5 break existing Sonnet 4.6 code?** No. Switch the model ID to `claude-sonnet-5` and existing prompts and Claude Code configurations carry forward. Budget for the tokenizer change if you track per-call token costs closely.

**What is the Sonnet 5 API model ID?** `claude-sonnet-5` on the Claude API and Google Vertex AI, and `anthropic.claude-sonnet-5` on Amazon Bedrock.

## Related Pages

- Every Claude Model for the complete timeline from Claude 3 to Opus 5
- [Opus 4.8](/blog/claude-opus-4-8) for the higher-accuracy flagship Sonnet 5 escalates to
- [Sonnet 4.6](/blog/claude-sonnet-4-6) for the predecessor Sonnet 5 replaces
- Model selection guide for switching models tactically mid-session
- [GPT-5.6 Sol](/blog/gpt-5-6) for how the competitive landscape stacks up
- [GLM 5.2 vs Opus 4.8 vs Sonnet 5](/blog/glm-5-2-vs-opus-4-8-vs-sonnet-5) for how Claude compares to the leading open-weights model
- Usage optimization for managing costs across models
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** handles model routing in one config file: Opus for `/spec` planning, Sonnet for everyday iteration, Haiku for trivial calls. You set the policy; Pilot Shell picks per request.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
