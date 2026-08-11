---
title: "Claude Opus 5 vs Fable 5: Half Price, Who Wins"
description: "Claude Opus 5 vs Fable 5: Opus 5 wins nearly every eval at half the price. Where Fable 5 still leads, the retention gap, and which to pick."
slug: claude-opus-5-vs-fable-5
date: 2026-07-24
authors:
  - max-ritter
tags:
  - models
---

Claude Opus 5 vs Fable 5: Opus 5 wins nearly every eval at half the price. Where Fable 5 still leads, the retention gap, and which to pick.

<!-- truncate -->

**Claude Opus 5 vs Fable 5** came down to a single question within an hour of the [Opus 5 launch](/blog/claude-opus-5), and people asked it bluntly: if Opus 5 costs half of Fable 5 and beats it on almost everything, what is Fable 5 for? The honest answer is that **Fable 5's remaining case is narrow, and it is not a capability case**. Opus 5 wins seven of the eight quantified head-to-head evals, at $5/$25 against Fable 5's $10/$50. Fable 5 keeps a three-tenths-of-a-point edge on CursorBench 3.2, remains the model Anthropic points to for "the highest available capability," and is the one you already have provisioned if you are on a Max plan. Everything else in this comparison favors Opus 5, including two things that never show up on a benchmark chart: data retention and classifier false positives.

## TL;DR: Who Wins What

| Category | Winner | Margin |
| --- | --- | --- |
| Agentic coding (Frontier-Bench v0.1) | Opus 5 | 43.3 vs 33.7, at roughly half the cost |
| Agentic coding (CursorBench 3.2) | Fable 5 | 70.4 vs 70.1, at roughly twice the cost |
| Knowledge work (GDPval-AA v2, Elo) | Opus 5 | 1,862 vs 1,748 |
| Computer use (OSWorld 2.0) | Opus 5 | 70.5 vs 66.1, at about half the spend |
| Business workflows (AutomationBench) | Opus 5 | 25.8 vs 17.4 |
| Reasoning with tools (HLE) | Opus 5 | 64.8 vs 63.9 |
| Agentic search (DeepSearchQA) | Opus 5 | 95.0 vs 94.7, at $4.20 vs $7.30 |
| Coding index (Artificial Analysis) | Opus 5 | 66.7 vs 65.9, at $8.50 vs $13 |
| FrontierCode 1.1 | Unquantified | Cognition reports Opus 5 approaches Fable-level performance |
| Offensive cyber and autonomous biology | Fable 5 | Mythos-class ceiling Opus 5 does not reach |
| Price per token | Opus 5 | Exactly half on both input and output |
| Data retention terms | Opus 5 | No mandatory retention vs mandatory 30-day |
| Classifier false positives | Opus 5 | Intervenes ~85% less often |

Ten rows to Opus 5, two to Fable 5, one unquantified. The two Fable 5 rows are worth understanding precisely, because one of them is a rounding error and the other is a capability most readers cannot legally or practically use.

## Price: The Argument That Frames Everything Else

Fable 5 costs **$10 per million input tokens and $50 per million output**. Opus 5 costs **$5 and $25**. That is not a discount, it is a halving, on both sides of the meter, with the same 1M-token context window at the same flat rate and the same 90% prompt-caching discount on cached reads.

Put a working number on it. A job that sends 1M input tokens and generates 200K output runs about **$20 on Fable 5** ($10 + $10) and about **$10 on Opus 5** ($5 + $5). Across an agentic pipeline making thousands of those calls, that is a doubled line item for a model that loses seven of the eight quantified evals.

The cost story gets worse for Fable 5 once you look at how Anthropic charted the results. Every Opus 5 benchmark plots score against dollars spent across the effort ladder, and Opus 5's curve sits above and to the **left** of Fable 5's on nearly all of them. On OSWorld 2.0, Opus 5 hits 70.5 at roughly $25 per task while Fable 5 reaches only 66.1 at roughly $47. On DeepSearchQA the scores are within three tenths of a point and Opus 5 gets there for $4.20 against $7.30. You are not trading money for capability. On most of these curves you are paying more for less.

## Benchmarks: The Full Head-to-Head

| Benchmark | Opus 5 | Fable 5 | Edge |
| --- | --- | --- | --- |
| **Frontier-Bench v0.1** (agentic coding) | 43.3, 44.3 peak | 33.7 | Opus 5, +9.6 and cheaper |
| **CursorBench 3.2** (agentic coding) | 70.1 (~$8) | 70.4 (~$17) | Fable 5, +0.3 |
| **GDPval-AA v2** (knowledge work, Elo) | 1,862 | 1,748 | Opus 5, +114 |
| **OSWorld 2.0** (computer use) | 70.5 (~$25) | 66.1 (~$47) | Opus 5, +4.4 |
| **AutomationBench** (business workflows) | 25.8 | 17.4 | Opus 5, +8.4 |
| **Humanity's Last Exam** (with tools) | 64.8 | 63.9 | Opus 5, +0.9 |
| **DeepSearchQA** (agentic search) | 95.0 (~$4.20) | 94.7 (~$7.30) | Opus 5, +0.3 and cheaper |
| **AA Coding Agent Index** | 66.7 (~$8.50) | 65.9 (~$13) | Opus 5, +0.8 and cheaper |
| **FrontierCode 1.1** | "approaches Fable-level" | not published | Not quantified |

The same caveat applies to every row that applies to any frontier launch. Anthropic configures its own harness, and the Frontier-Bench chart footnote is explicit that its numbers come from an internal run on the mini-SWE-agent harness with Opus 4.8 serving as fallback on classifier refusals for both models. Directionally these results are real. Treat the exact margins as indicative, not as a scoreboard, and measure your own workload before you move a pipeline.

## Where Fable 5 Still Wins

**CursorBench 3.2, by three tenths of a point.** Fable 5 scores 70.4 to Opus 5's 70.1, and needs roughly twice the money to do it. Cursor Co-Founder Sualeh Asif said as much on launch day: "Claude Opus 5 delivers near Fable 5 intelligence at Opus speed and cost. On CursorBench 3.2 it's just under Fable 5 and has many of the same behaviors." If the workload Cursor's benchmark models is your workload, Fable 5 is the marginally better model. Whether 0.3 points is worth a doubled bill is a question that answers itself for most teams.

**The Mythos-class ceiling on offensive cyber and autonomous biology.** Anthropic is explicit that Opus 5 does not advance the frontier in dual-use capability, and stays behind [Mythos 5](/blog/claude-fable-5-mythos-5) on both. The OSS-Fuzz split is the cleanest illustration: Opus 5 **identifies** vulnerabilities at 79.4% pass@1 against Mythos 5's 80.0%, effectively a tie, but on **exploiting** them Mythos 5 solves 13 challenges at grade 1.0 against Opus 5's 4.

 For autonomous biological research, Mythos 5 remains stronger. Note carefully that this is a Mythos 5 advantage, not a Fable 5 one: Fable 5 is the safeguarded build, and its classifiers block exactly the workloads where the uncapped model leads.

**Long-horizon partner evals from its own launch.** Fable 5 shipped in June with state-of-the-art results on Cognition's FrontierBench, Hex's core analytics suite, Physical Superintelligence's frontier physics eval, and Hebbia's finance benchmark. Anthropic has not re-run those against Opus 5, so the June claims stand unchallenged rather than overturned. If your workload resembles one of them, benchmark both rather than assuming the July numbers transfer.

That is the complete list. It is short.

## The Differences That Do Not Show Up on a Chart

Two operational differences separate these models more decisively than any benchmark gap, and both cut toward Opus 5.

### Data Retention

Fable 5 carries **mandatory 30-day retention on all Mythos-class traffic**, first-party and third-party, and it overrides enterprise agreements that were previously zero-retention. The data is explicitly not used for training and Anthropic deletes after 30 days in nearly all cases, but the term is not negotiable and it supersedes contracts your legal team already signed.

**Opus 5 has no mandatory retention for general access.** For any organization operating under a zero-retention agreement, that single line decides the comparison before anyone opens a benchmark chart. It is the difference between a model your compliance team has to review and a model that inherits the terms you already have.

### Classifier False Positives

Fable 5's safeguard architecture routes flagged cybersecurity, biology, chemistry, and distillation requests to [Opus 4.8](/blog/claude-opus-4-8) and tells the user it did, which Anthropic reports happens in fewer than 5% of sessions on average. That average hides the distribution. If you do legitimate security research, audit code for vulnerabilities, or work in life sciences, you are not in the average, and the classifiers Anthropic openly called "narrower than ideal" on biology and chemistry drop you to a weaker model mid-task on exactly the work that justified paying double.

**Opus 5's cyber classifiers are expected to intervene roughly 85% less often than Fable 5's.** They permit vulnerability identification in source code while blocking binary scanning, penetration testing, and exploit generation. On top of that, biology-related requests that Fable 5 blocks now route to Opus 5 rather than Opus 4.8, so the fallback itself got stronger. For the users who felt Fable 5's false-positive tax most, this is a larger practical upgrade than any score in the tables above.

## Access and Plan Availability

Both models are live as of July 24, 2026, but they reach you through different doors, and Fable 5's door has been eventful.

Fable 5 was **disabled worldwide on June 12, 2026** under a US export-control directive that required blocking all foreign nationals, which Anthropic could not verify in real time. Access was **restored on July 1, 2026** after the US government lifted the controls, with a new classifier that blocks the flagged jailbreak in over 99% of cases and reroutes those requests to Opus 4.8.

Plan access changed again on **July 20, 2026**, the day after the promotional window closed at 11:59:59 PM PT on July 19:

| Plan | Fable 5 | Opus 5 |
| --- | --- | --- |
| **Claude Max** | Standard, up to 50% of weekly limits | Default model |
| **Claude Pro** | Usage credits only | Strongest model available |
| **Team, premium seats** | Standard, up to 50% of weekly limits | Available |
| **Team, standard seats** | Usage credits only | Available |
| **Seat-based Enterprise, premium seats** | Standard, up to 50% of weekly limits | Available |
| **Seat-based Enterprise, standard seats** | Usage credits only | Available |
| **Usage-based Enterprise** | $10 / $50 per 1M | $5 / $25 per 1M |
| **Claude API** | $10 / $50 per 1M | $5 / $25 per 1M |

Read the Pro row twice, because it is the sharpest practical split in this whole comparison. On Claude Pro, Fable 5 requires prepaid usage credits billed at API rates, while Opus 5 is simply the best model in your picker at no extra cost. Anthropic granted eligible Pro and Team standard seats a one-time credit to soften the July 20 change, but the structural answer for Pro subscribers is that Opus 5 is the model your plan actually includes. For the mechanics of enabling and funding credits, see the [Fable 5 pricing and usage-credits guide](/blog/fable-5-usage-credits).

## Specs Side by Side

| Spec | Opus 5 | Fable 5 |
| --- | --- | --- |
| **API ID** | `claude-opus-5` | `claude-fable-5` |
| **Released** | July 24, 2026 | June 9, 2026 |
| **Standard pricing** | $5 / $25 per 1M | $10 / $50 per 1M |
| **Context window** | 1M tokens, default and maximum | 1M tokens |
| **Max output** | 128K tokens | 128K tokens |
| **Knowledge cutoff** | May 2026 | January 2026 |
| **Thinking** | Adaptive, on by default | Adaptive, always on |
| **Effort ladder** | low to max, default `high` | low to max, default `high` |
| **Fast mode** | $10 / $50, Claude API only | Not offered |
| **Prompt cache minimum** | 512 tokens | Not documented |
| **Data retention** | No mandatory retention | Mandatory 30-day on Mythos-class traffic |
| **Safety mechanism** | Cyber classifiers, ~85% fewer hits | Classifier fallback to Opus 4.8 |

The four-month gap in knowledge cutoff is easy to overlook and matters for anyone working against fast-moving libraries: Opus 5 knows the world through **May 2026**, Fable 5 through **January 2026**.

## Which Should You Use?

| Situation | Use | Why |
| --- | --- | --- |
| Default for agentic coding and daily work | Opus 5 | Wins Frontier-Bench outright at half the price |
| Long-horizon autonomous runs | Opus 5 | Leads OSWorld 2.0 and AutomationBench, costs less per task |
| Cost-sensitive high-volume pipelines | Opus 5 | The curve sits left of Fable 5 on nearly every chart |
| Security research, code auditing, life sciences | Opus 5 | Classifiers fire ~85% less often |
| Zero-retention or regulated environments | Opus 5 | No mandatory retention to take to legal |
| Anything on a Claude Pro plan | Opus 5 | Included, where Fable 5 needs prepaid credits |
| Cursor-shaped agentic coding where 0.3 points decides | Fable 5 | The only benchmark row it still holds |
| Workloads matching Fable 5's June partner evals | Test both | Those evals have not been re-run against Opus 5 |
| Offensive cyber or autonomous biology at the ceiling | Neither | That capability lives in Mythos 5, behind Project Glasswing |

The recommendation is unusually clean for a model comparison: **make Opus 5 your default and treat Fable 5 as a workload-specific exception you have measured, not a general-purpose upgrade path.** Six weeks ago Fable 5 was the model you escalated to when Opus could not finish the job. Opus 5 absorbed most of that role and kept the Opus price.

## Switching Between Them in Claude Code

```
claude config set model claude-opus-5
```

Per-session override, or a mid-session switch:

```
claude --model claude-fable-5
```

```
/model claude-opus-5
```

If you are moving prompts from Fable 5 to Opus 5, two Opus 5 behaviors need attention rather than a straight copy. Thinking is on by default and shares `max_tokens` with your response text, and `thinking: {"type": "disabled"}` now returns a **400 error** at `xhigh` or `max` effort. Anthropic also recommends stripping verification instructions such as "include a final verification step" or "use a subagent to verify," because Opus 5 verifies its own work unprompted and those lines produce over-verification. The full migration checklist is in the [Opus 5 launch breakdown](/blog/claude-opus-5).

## Frequently Asked Questions

**Is Opus 5 better than Fable 5?** On the published evidence, yes, on nearly everything, and at half the price. Opus 5 leads on Frontier-Bench, GDPval-AA v2, OSWorld 2.0, AutomationBench, Humanity's Last Exam with tools, DeepSearchQA, and the Artificial Analysis Coding Agent Index. Fable 5 holds CursorBench 3.2 by 0.3 points.

**Why would anyone still pay for Fable 5?** Three reasons: a marginal CursorBench 3.2 edge, long-horizon partner evals from Fable 5's June launch that Anthropic has not re-run against Opus 5, and the fact that it is standard on Max plans, so heavy Max users already have it provisioned. Outside those cases the economics do not support it.

**How much cheaper is Opus 5 than Fable 5?** Exactly half on both meters: $5/$25 per million tokens against $10/$50. A 1M-input, 200K-output job runs about $10 on Opus 5 and about $20 on Fable 5, before prompt caching or batch discounts, which apply to both.

**Can I use Fable 5 right now?** Yes. Access was restored on July 1, 2026, after the June 12 export-control suspension was lifted, with an added classifier that blocks the flagged jailbreak in over 99% of cases. On plans, Fable 5 is included on Max and on premium Team and seat-based Enterprise seats; Pro and standard seats need usage credits.

**Which model is safer to use in a regulated environment?** Opus 5. It carries no mandatory data retention for general access, while Fable 5 imposes 30-day retention on all Mythos-class traffic and overrides pre-existing zero-retention agreements. Opus 5 also posts the lowest misaligned-behavior score of any recent Claude model at 2.30, against 2.85 for Opus 4.8 and 3.35 for [Sonnet 5](/blog/claude-sonnet-5).

**Does Opus 5 replace Fable 5 as Anthropic's top model?** Not formally. Anthropic still points to Fable 5 for workloads needing the highest available capability, and Mythos 5 remains the uncapped build behind Project Glasswing. What changed is that the practical gap between the top tier and the Opus tier narrowed to almost nothing on published evals, while the price gap stayed at 2x.

## Related Pages

- [Claude Opus 5](/blog/claude-opus-5) for the full launch breakdown, all nine benchmark charts, and the prompt migration
- [Claude Fable 5 and Mythos 5](/blog/claude-fable-5-mythos-5) for Fable 5's specs, safety architecture, and the Mythos split
- [Claude Opus 4.8](/blog/claude-opus-4-8) for the model both of these supersede, still the classifier fallback
- [Fable 5 pricing and usage credits](/blog/fable-5-usage-credits) for how prepaid credits work on subscription plans
- Every Claude Model for the complete timeline from Claude 3 to Opus 5
- Model selection guide for routing work across the full lineup
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** handles model routing in one config file: Opus for `/spec` planning, Sonnet for everyday iteration, Haiku for trivial calls. You set the policy; Pilot Shell picks per request.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
