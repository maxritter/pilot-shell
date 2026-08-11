---
title: "Claude Fable 5 Benchmarks: Specs, Release & Mythos 5"
description: "Claude Fable 5 benchmarks: state of the art on coding, finance, physics, and vision. Specs, the Mythos 5 split, safety, and release details."
slug: claude-fable-5-mythos-5
date: 2026-06-09
authors:
  - max-ritter
tags:
  - models
---

Claude Fable 5 benchmarks: state of the art on coding, finance, physics, and vision. Specs, the Mythos 5 split, safety, and release details.

<!-- truncate -->

**Claude Fable 5 posts state-of-the-art benchmark results across software engineering, knowledge work, scientific research, and vision**, with its lead over [Opus 4.8](/blog/claude-opus-4-8) widening the longer and more complex the task. Released **June 9, 2026**, it is the first [Mythos-class model](/blog/claude-mythos) Anthropic has made generally available, and the most powerful model the company has ever shipped to the public. This post covers what Fable 5 is, the benchmark numbers and the partners who reported them, the safety architecture that separates it from its uncapped sibling Mythos 5, and how to run it in Claude Code. For the full money story, the $10/$50 rates, and which plans include it since the July 20, 2026 split, see the dedicated [Fable 5 pricing and usage-credits guide](/blog/fable-5-usage-credits).

Fable 5 is Mythos made safe. A separate classifier system watches every session for high-risk cybersecurity, biology, chemistry, and distillation requests and, when one fires, re-runs the request on a fallback model chosen by category, cybersecurity to Opus 4.8 and biology to Opus 5, telling the user when it does. That fallback triggers in under 5% of sessions on average. Its sibling, **Claude Mythos 5**, is the same underlying model with those safeguards lifted, and it stays restricted to [Project Glasswing](https://www.anthropic.com/glasswing) partners. The API model ID is `claude-fable-5`, available today on the Claude API, Claude Code, consumption-based Enterprise plans, AWS, Google Cloud, and Microsoft Foundry.

## Key Specs

| Spec | Details |
| --- | --- |
| **API ID** | `claude-fable-5` |
| **Release Date** | June 9, 2026 |
| **Model Class** | Mythos-class (safeguarded for general release) |
| **Fallback Model** | Cybersecurity flags to Opus 4.8, biology flags to Opus 5 (< 5% of sessions) |
| **Context Window** | Full 1M tokens, included at standard pricing |
| **Pricing** | $10 input / $50 output per 1M tokens |
| **Prompt Caching** | Up to 90% off cached input |
| **Inference Region** | US-only inference available at a 1.1x multiplier |
| **Data Retention** | Mandatory 30-day retention on all Mythos-class traffic, not used for training |
| **Availability** | Claude API, Claude Code, consumption Enterprise, AWS, Google Cloud, MS Foundry |
| **Status** | Active, most capable generally available model |

## What Fable 5 Is: Mythos, Made Safe

In April, Anthropic announced [Claude Mythos Preview](/blog/claude-mythos) and refused to release it. The stated reason was offensive cybersecurity capability that ran ahead of the company's safeguard stack. Mythos found thousands of zero-day vulnerabilities autonomously, produced 181 working Firefox exploits on a harness where Opus 4.6 produced two, and stayed locked behind Project Glasswing at $25/$125 per million tokens. For two months, [Opus 4.8](/blog/claude-opus-4-8) was the public ceiling.

Fable 5 changes that by splitting one model into two products. The two share the same weights. What separates them is a classifier layer. As Anthropic puts it in a footnote, "Fable is from the Latin fabula, 'that which is told,' akin to the Greek mythos. The safeguards are what distinguish the two models."

The safeguard mechanism is worth understanding precisely, because it changes how the model behaves in practice. Fable 5 does not refuse flagged requests. Instead, a separate set of AI classifiers watches for potential misuse and jailbreak attempts across three categories. When one triggers, the request re-runs on a fallback model and the user is told the handoff happened. Which model depends on the category: biology-flagged requests re-run on **Opus 5**, cybersecurity-flagged requests re-run on **Claude Opus 4.8**. That category split is current behavior as of Claude Code v2.1.219; earlier versions fell back to Opus 4.8 for every flagged category regardless of which one fired. Anthropic reports this fallback occurs in **fewer than 5% of sessions on average**.

That design has a real cost most launch coverage glosses over. The classifiers are deliberately conservative, and Anthropic admits the biology and chemistry coverage is "narrower than ideal" because the company prioritized shipping speed over precision. A conservative classifier produces false positives. If you do legitimate security research or run agentic recon against your own infrastructure, expect Fable 5 to occasionally drop you to Opus 4.8 mid-task and tell you it did. If you work in a wet lab, the same conservative classifiers can drop you to Opus 5 instead. For most developers that 5% is invisible. For a minority of technical users it is a recurring tax on the exact workloads that justify paying double.

## Benchmark Results

Anthropic frames Fable 5 as a capability release, not a reliability release. Where [Opus 4.8 was about doing the same work with fewer mistakes](/blog/claude-opus-4-8), Fable 5 is about doing work that earlier models could not finish at all. The pattern across partner evals is consistent: the lead over Opus 4.8 widens the longer and more complex the task gets.

| Benchmark / Eval | Fable 5 result | Source |
| --- | --- | --- |
| **Cognition FrontierBench** | Highest-scoring model, excels at long-horizon reasoning | Scott Wu, Cognition |
| **CursorBench** | State of the art, opens up long-horizon problems | Michael Truell, Cursor |
| **Hebbia Finance Benchmark** | Highest score of any model on senior-level reasoning | Anthropic announcement |
| **Finance-first reasoning** | Strongest finance-first model tested, a notable step up | Damian Miraglia, Balyasny |
| **Hex core analytics** | First model to break 90%, a 10-point jump over Opus | Izzy Miller, Hex |
| **Shortcut spreadsheet suite** | Beats Opus 4.8 at every effort level, 25-30% faster | Peter Wang, Shortcut |
| **Frontier physics research** | Strongest tested, using a third of the reasoning tokens | Matthew Pines, Physical Superintelligence |
| **Legal redlines** | Matched or beat the current model in every blind review | Aveek Duttagupta, Crosby Legal |
| **Replit ViBench** | Highest-performing model tested on vibe coding | Michele Catasta, Replit |
| **Stripe codebase migration** | Codebase-wide migration in one day in a 50M-line Ruby repo | Stripe |
| **Slay the Spire (memory)** | File-based memory helped 3x more than it did Opus 4.8 | Anthropic internal |
| **Pokémon FireRed (vision)** | Completed using only raw screenshots, no maps or aids | Anthropic internal |

A few results deserve weight beyond a single row. On Hex's core analytics benchmark, AI Research Lead Izzy Miller reported Fable 5 was the "first to break 90% on our core analytics benchmark," which he framed as "a 10-point jump over Opus." Ten points at the top of a saturating benchmark is unusual. On frontier physics, Physical Superintelligence CEO Matthew Pines called it the "strongest model we've tested on frontier physics research while using a third of the reasoning tokens," which is the more interesting half of the claim: better answers for less compute, not better answers at any cost.

The coding partners converge on the same theme. Cursor CEO Michael Truell said Fable 5 is a "state of the art model on CursorBench." Cognition CEO Scott Wu reported it as the highest scorer on FrontierBench, singling out long-horizon reasoning. GitHub CPO Mario Rodriguez described "complex, long-horizon coding tasks with a level of autonomy and reliability that exceeded previous benchmarks." Walleye CTO Luke Anderson cited "more capable engineering in fewer turns." Lovable CTO and Co-founder Fabian Hedin offered the most concrete line: "Apps that took a hundred prompts a year ago, it now one-shots." Outside code, Crosby Legal's Aveek Duttagupta reported that "in blind review, our lawyers found its redlines matched or beat our current model every time."

One caveat, the same one that applies to every frontier launch. Anthropic configures its own benchmark harness, typically at maximum effort and averaged across trials, while competitor numbers come from their own setups. The direction of these results is real and the partner quotes are independent, but the exact margins are not an apples-to-apples scoreboard. Benchmark on your own workload before you commit a production pipeline to the higher rate.

## Pricing and Access in Brief

The short version, with the full breakdown in our [Fable 5 pricing and usage-credits guide](/blog/fable-5-usage-credits): on the API, Fable 5 costs **$10 per million input tokens and $50 per million output**, exactly double Opus 4.8's $5/$25 and less than half Mythos Preview's $25/$125, with the full 1M-token context window at standard pricing. On subscriptions the arrangement settled on **July 20, 2026**: Fable 5 is included at no extra cost on **Max plans and premium seats** on Team and seat-based Enterprise, capped at 50% of your weekly usage limits, while **Pro plans and standard seats** run it on prepaid [usage credits](/blog/fable-5-usage-credits) billed at API rates.

Access is settled too. On **June 12, 2026**, a US government export-control directive forced Anthropic to disable Fable 5 and Mythos 5 for all customers, on subscriptions and on the API alike. Those controls were lifted on June 30 and **access was restored on July 1, 2026** across the Claude Platform, claude.ai, Claude Code, and Claude Cowork, with cloud providers following. Anthropic shipped a new classifier alongside the restoration that blocks the reported jailbreak in over 99% of cases and reroutes those requests to [Opus 4.8](/blog/claude-opus-4-8). For how credits are purchased, how auto-reload works, and the full access timeline, the [pricing guide](/blog/fable-5-usage-credits) is the place to go.

## Safety Profile

Fable 5's safety story is the classifier system plus a new data policy, and both are sharper than anything Anthropic has shipped to general customers before.

**The three classifier categories** are cybersecurity (exploitation, offensive cyber tasks, agentic hacking such as reconnaissance, discovery, and lateral movement), biology and chemistry (broad dual-use research coverage, which Anthropic openly calls narrower than ideal), and distillation (large-scale attempts to extract Claude's capabilities to train competing models). When a classifier fires, the request re-runs on a fallback model chosen by category: cybersecurity-flagged requests on Opus 4.8, biology-flagged requests on Opus 5. Anthropic reports the fallback rate stays under 5% of sessions on average.

The hardening numbers are meaningful. An external bug bounty found **no universal jailbreaks in over 1,000 hours** of testing. One external partner found Fable 5's cyber safeguards the strongest of any model they tested, with zero compliance on harmful single-turn requests across 30 public jailbreak techniques. With safeguards in blocking mode, Fable 5 made no measurable progress on offensive cyber evaluations.

**The new data retention policy is the part with industry implications.** Anthropic now mandates **30-day retention for all traffic on Mythos-class models**, first-party and third-party, including on enterprise agreements that were previously zero-retention. The data is explicitly not used to train new Claude models or for any non-safety purpose, and Anthropic logs all human access and deletes after 30 days in nearly all cases. The stated purpose is defending against novel attacks and reducing classifier false positives. If your organization signed a zero-retention deal, this is a change you need to take to legal before you route production traffic to Fable 5, because it overrides that term for this model class.

On alignment, the assessment is reassuring in a way the cyber capability is not. Anthropic's automated alignment evaluation rated Mythos 5's level of misaligned behavior, things like deception or cooperation with misuse, as **low and similar to Opus 4.8**. The risk that gates Mythos 5 is raw offensive capability, not the model's disposition.

## Mythos 5 and Project Glasswing

Mythos 5 is the uncapped version of Fable 5. Same weights, safeguards lifted, and Anthropic describes it as having "the strongest cybersecurity capabilities of any model in the world." That is precisely why it is not on a public endpoint.

Access runs through [Project Glasswing](https://www.anthropic.com/glasswing), the invitation-only defensive cybersecurity program Anthropic launched in April for critical-infrastructure operators, run in collaboration with the US government. Every current Glasswing and Mythos Preview partner can upgrade to Mythos 5 today with cyber safeguards lifted. Anthropic plans to expand access steadily and stand up a formal trusted access program for cybersecurity organizations.

Biology is a separate track. A **biology trusted access program** opens in the coming weeks, offering Fable 5 with bio and chemistry safeguards removed (cyber safeguards stay on) to a small group of vetted life sciences researchers. The case for it is in the research results: with protein-design tooling and no human assistance, Mythos-class models matched or beat skilled human operators, and on 9 of 14 protein targets produced strong drug-design candidates now under investigation. In a week of largely autonomous genomics work, the model trained a custom ML model that outperformed a recent Science-published model while being 100x smaller.

The structure mirrors the original Glasswing logic. The most capable version goes first to the people defending against, or researching with, that capability, while the general public gets the safeguarded version. If you are an individual developer or a general enterprise, Mythos 5 is not an access path. Fable 5 is your ceiling, and for almost everyone that is the correct ceiling.

## How to Use Fable 5 in Claude Code

Switch your default model:

```
claude config set model claude-fable-5
```

For a per-session override without changing your default:

```
claude --model claude-fable-5
```

The model API identifier is `claude-fable-5`, available across the Claude API, Claude Code, consumption-based Enterprise plans, AWS, Google Cloud, and Microsoft Foundry from launch day. If you run Claude Code on a subscription, the plan tier decides the billing. On Max and premium Team or seat-based Enterprise seats, Fable 5 sessions draw on your included weekly allowance up to a 50% cap and weigh roughly double an Opus session against it. On Pro and standard seats, they draw on prepaid [usage credits](/blog/fable-5-usage-credits) at API rates.

## Fable 5 vs Opus 4.8

| Feature | Opus 4.8 | Fable 5 |
| --- | --- | --- |
| **Model class** | Opus-class, generally available | Mythos-class, safeguarded for general release |
| **API ID** | `claude-opus-4-8` | `claude-fable-5` |
| **Standard pricing** | $5 / $25 per 1M | $10 / $50 per 1M (double) |
| **Subscription inclusion** | Included on Pro, Max, Team, Enterprise | Max and premium seats, 50% cap; credits on Pro and standard seats |
| **Subscription usage weight** | Baseline | Roughly 2x an Opus session |
| **Long-horizon capability** | Strong, reliable | State of the art, lead widens with task length |
| **Safety mechanism** | Standard refusals | Classifier fallback: cyber to Opus 4.8, biology to Opus 5 |
| **Data retention** | Standard policy / zero-retention deals | Mandatory 30-day retention, not used for training |
| **Best for** | Daily agentic work, most coding tasks | Long-horizon, high-complexity work where finishing wins |

The honest recommendation has changed since this table was written. [Opus 5](/blog/claude-opus-5), released July 24, 2026, supersedes Opus 4.8 at the same $5/$25 and now wins seven of the eight quantified head-to-head evals against Fable 5, so it is the default for daily [agentic coding](/blog/agent-teams) and for most of the long-horizon work Fable 5 was built for. Reach for Fable 5 when your own benchmarks show it winning on your specific workload, which on published evidence means CursorBench 3.2-shaped coding and the long-horizon partner evals from its June launch that Anthropic has not re-run. The [Opus 5 vs Fable 5 comparison](/blog/claude-opus-5-vs-fable-5) works through the decision, the model selection guide covers tactical switching, and the complete Claude model timeline shows where this lands in Anthropic's release history.

## Frequently Asked Questions

**Is Claude Fable 5 free?** It depends on your plan. Since July 20, 2026 it is included at no extra cost on Max plans and premium seats on Team and seat-based Enterprise, capped at 50% of weekly usage limits. Pro plans and standard seats need [usage credits](/blog/fable-5-usage-credits). On the API it is paid from day one at $10/$50 per million tokens, and the claude.ai free tier never included it.

**Can I use Fable 5 right now?** Yes. The June 12, 2026 export-control suspension ended on July 1, 2026, and Fable 5 has been generally available since across the Claude Platform, claude.ai, Claude Code, and Claude Cowork, with cloud providers restored after. Whether it costs extra depends on your plan tier.

**Fable 5 vs Mythos 5: what's the difference?** They are the same underlying model. Fable 5 ships with classifier safeguards that catch high-risk cybersecurity, biology, chemistry, and distillation requests and re-run them on a fallback model, cybersecurity to Opus 4.8 and biology to Opus 5. Mythos 5 has those safeguards lifted and is restricted to Project Glasswing partners and select biology researchers. The public gets Fable 5.

**Fable 5 vs Opus 4.8: which should I use?** Use Opus 4.8 as your default for daily agentic and coding work at $5/$25. Reach for Fable 5 on long-horizon, high-complexity tasks where its widening capability lead justifies double the price. Its advantage grows the longer and harder the task.

**How much does Fable 5 cost?** $10 per million input tokens and $50 per million output tokens, double Opus 4.8 and less than half of Mythos Preview's $25/$125. Prompt caching saves up to 90% on cached input, and US-only inference is available at a 1.1x multiplier.

**What is the Fable 5 context window?** Fable 5 includes the full 1M-token context window at standard pricing, the same flat per-token rate whether a request is 9K tokens or 900K. There is no long-context surcharge.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** handles model routing in one config file: Opus for `/spec` planning, Sonnet for everyday iteration, Haiku for trivial calls. You set the policy; Pilot Shell picks per request.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
