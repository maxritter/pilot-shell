---
title: "GLM 5.2 vs Claude: Opus 4.8 & Sonnet 5 Compared"
description: "GLM 5.2 vs Opus 4.8 vs Sonnet 5: the only clean benchmark comparisons, why cross-vendor numbers mislead, pricing, open weights, and which to use."
slug: glm-5-2-vs-opus-4-8-vs-sonnet-5
date: 2026-07-01
authors:
  - max-ritter
tags:
  - models
---

GLM 5.2 vs Opus 4.8 vs Sonnet 5: the only clean benchmark comparisons, why cross-vendor numbers mislead, pricing, open weights, and which to use.

<!-- truncate -->

GLM 5.2 vs Opus 4.8 vs Sonnet 5 is the comparison everyone wants after Z.ai shipped an open-weights model that benchmarks near the frontier at a fraction of the price. The honest version of this comparison starts with a warning: most of the cross-vendor numbers you will see floating around are not apples-to-apples, because [Z.ai](/blog/glm-5-2) and Anthropic measure benchmarks on different harnesses. This post separates the two clean comparisons that exist from the reference-only numbers that do not, then gives a straight decision: GLM 5.2 for cost, open weights, and math; [Sonnet 5](/blog/claude-sonnet-5) as your default daily driver; [Opus 4.8](/blog/claude-opus-4-8) as the ceiling for the hardest work.

## The Comparability Problem (Read This First)

Z.ai publishes a benchmark table that includes Claude Opus 4.8. It is tempting to read straight across it. Do not, for two reasons.

First, **Z.ai ran the comparisons on its own harness.** When it lists Opus 4.8 at 85.0 on Terminal-Bench, that is Z.ai's re-run, not Anthropic's number ([Anthropic's official Opus 4.8 Terminal-Bench is 82.7](/blog/claude-opus-4-8)). Cross-harness scores drift, so reading GLM's Z.ai-harness number against Claude's Anthropic-harness number is comparing two different tests.

Second, **Sonnet 5 is not in Z.ai's table at all.** Every GLM-5.2-vs-Sonnet-5 number you might construct is built from two separate harnesses. There is no head-to-head data for that pairing, full stop.

There are exactly **two clean GLM-5.2-vs-Opus-4.8 comparisons**, and they are clean only because Z.ai used Anthropic's own published figures for Opus on those rows. Everything else is reference-only.

## The Only Clean Comparison: GLM 5.2 vs Opus 4.8

On these two benchmarks, the Opus 4.8 number in Z.ai's table matches Anthropic's official figure, so the comparison holds.

| Benchmark (closest to apples-to-apples) | GLM 5.2 | Opus 4.8 | Gap |
| --- | --- | --- | --- |
| **SWE-bench Pro (agentic coding)** | 62.1 | 69.2 | Opus +7.1 |
| **HLE (with tools)** | 54.7 | 57.9 | Opus +3.2 |

The read is consistent: GLM 5.2 lands within striking distance but a clear step behind Opus 4.8 on the two evals where a fair comparison is possible. A 7-point SWE-bench Pro gap is the difference you are paying the Opus premium for, and it widens on the harder long-horizon coding tasks below.

## Reference Numbers (Separate Harnesses, Not Head-to-Head)

The table below puts GLM 5.2 (Z.ai's harness) next to the Anthropic-official numbers for Opus 4.8 and Sonnet 5. **These columns are measured on different harnesses. Read each column on its own; do not read across the rows as a verdict.** It is here so you can see roughly where each model lands, not to declare per-row winners.

| Benchmark | GLM 5.2 (Z.ai harness) | Opus 4.8 (Anthropic) | Sonnet 5 (Anthropic) |
| --- | --- | --- | --- |
| **SWE-bench Pro** | 62.1 | 69.2 | 63.2 |
| **Terminal-Bench 2.1** | 81.0 (Terminus-2) | 82.7 | 80.4 |
| **HLE (with tools)** | 54.7 | 57.9 | 57.4 |
| **OSWorld-Verified (computer use)** | none (text-only) | 83.4 | 81.2 |
| **GDPval-AA v2 (knowledge work)** | AA index only | 1,615 | 1,618 |

A specific trap to flag: GLM 5.2's own best-reported Terminal-Bench figure is **82.7**, the exact digits of Anthropic's official Opus 4.8 Terminal-Bench number. They are different measurements on different harnesses that happen to share three digits. Do not read that coincidence as a tie.

Two rows resolve cleanly on capability, not harness. GLM 5.2 is **text-only**, so it scores nothing on OSWorld-Verified computer use, where Opus 4.8 (83.4) and Sonnet 5 (81.2) operate normally. And on Z.ai's own long-horizon coding evals (its harness, both models), GLM trails badly: NL2Repo 48.9 vs Opus 4.8's 69.7, SWE-Marathon 13.0 vs 26.0. Synthesizing code across a whole repo is GLM 5.2's weakest area regardless of how you slice the harness question.

Where GLM 5.2 genuinely leads is competition math (AIME 2026 99.2 on Z.ai's harness, ahead of every model in its set) and price.

## Pricing: GLM Undercuts Both, With an Asterisk

| Model | Input (per 1M) | Output (per 1M) | Notes |
| --- | --- | --- | --- |
| **GLM 5.2** | $1.40 | $4.40 | Open weights (MIT); token-hungry |
| **Sonnet 5** | $3 ($2 intro) | $15 ($10 intro) | Default on Free and Pro; intro thru Aug 31 |
| **Opus 4.8** | $5 | $25 | Reliable flagship; $10/$50 Fast mode |

On sticker price, GLM 5.2 is the cheapest by a wide margin, roughly 3.6x to 5.7x cheaper per token than Opus 4.8, roughly half of Sonnet 5's input rate and about a third of its output rate. The asterisk is real, though: independent testing (Artificial Analysis) clocks GLM 5.2 at roughly 43K output tokens per task, so a token-hungry run narrows the gap that the per-token price implies. Sonnet 5 sits in the middle and, unlike GLM, is the default model on Claude's free tier. Opus 4.8 is the most expensive and the most capable on the hardest tasks. For a deeper Claude-side cost breakdown, see [Sonnet 5 vs Opus 4.8](/blog/claude-sonnet-5-vs-opus-4-8).

## Open Weights, Vision, and Ecosystem

This is where the three diverge most, and where benchmarks miss the point.

**GLM 5.2 is open (MIT) and self-hostable, in theory.** The weights are on Hugging Face under a permissive license that cannot be switched off or geofenced, which matters for data control and provider competition. The catch is hardware: 1.51 TB in BF16, roughly 744 to 890 GB of VRAM even in FP8. Open, with a serious hardware asterisk. Claude is closed and API-only; you cannot self-host it.

**Only Claude does vision.** Opus 4.8 and Sonnet 5 handle images and computer-use; GLM 5.2 is text-only and breaks any harness that sends it a screenshot. If your agent reads dashboards or drives a browser, GLM is out by definition.

**Claude is the managed frontier.** Opus 4.8 and Sonnet 5 ship inside a generally available ecosystem with effort controls, Dynamic Workflows, and first-party Claude Code support. GLM 5.2 reaches Claude Code through Z.ai's Anthropic-compatible endpoint, and as documented today its default mapping still points to GLM-4.7, so you have to select GLM 5.2 explicitly.

## Which Should You Use?

This is a three-way split where the right answer depends on what you are optimizing for, not on a single leaderboard.

| Pick this | When... |
| --- | --- |
| **GLM 5.2** | Cost is the hard constraint, you want open weights or self-host for data control, or the work is math and reasoning heavy. A cheap second engine for bulk, well-scoped tasks. |
| **Sonnet 5** | You want the best balance of speed, intelligence, and price as your everyday default, including free-tier access. The model you leave running for most agentic coding. |
| **Opus 4.8** | The task is the hardest long-horizon software engineering, needs vision or computer-use, or demands maximum accuracy in a managed, generally available stack. |

The pattern most teams will settle on: make Sonnet 5 your default, keep Opus 4.8 as the escalation ceiling, and add GLM 5.2 as a low-cost lane for high-volume or math-heavy work where its weaknesses (long-horizon synthesis, no vision) do not bite. The frontier-vs-frontier question between the Claude models is covered in depth in [Sonnet 5 vs Opus 4.8](/blog/claude-sonnet-5-vs-opus-4-8); for the full Claude lineup see the model selection guide.

## Running Each in Claude Code

Claude models are native to [Claude Code](/blog/claude-sonnet-5): set the model and go.

```
claude config set model claude-sonnet-5   # default daily driver
claude --model claude-opus-4-8            # escalate for the hardest tasks
```

GLM 5.2 runs through Z.ai's Anthropic-compatible endpoint, so the same harness works against it:

```
// ~/.claude/settings.json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "your_zai_api_key"
  }
}
```

## Frequently Asked Questions

**Is GLM 5.2 better than Claude Opus 4.8?** On the only two clean comparisons, no: Opus 4.8 leads SWE-bench Pro 69.2 to 62.1 and HLE-with-tools 57.9 to 54.7, and it stretches further ahead on long-horizon coding (NL2Repo, SWE-Marathon). GLM 5.2 wins on price, open weights, and competition math.

**Is GLM 5.2 better than Sonnet 5?** There is no head-to-head benchmark data, because Sonnet 5 is absent from Z.ai's table and the two are measured on different harnesses. On the numbers that exist, they are close on coding (GLM 62.1 vs Sonnet 5 63.2 on SWE-bench Pro, separate harnesses) while GLM is cheaper per token and Sonnet 5 adds vision, free-tier access, and native Claude Code support.

**Why can't I just compare the benchmark tables directly?** Because Z.ai and Anthropic run different harnesses. Z.ai's table even lists Opus 4.8 at a Terminal-Bench number (85.0) that differs from Anthropic's official 82.7. Only SWE-bench Pro and HLE-with-tools line up, because Z.ai used Anthropic's own figures there.

**Which is cheapest?** GLM 5.2 at $1.40/$4.40 per million tokens, well under Sonnet 5 ($3/$15) and Opus 4.8 ($5/$25). Factor in GLM's high token usage per task before assuming the full savings.

**Can I run all three in Claude Code?** Claude models are native. GLM 5.2 works through Z.ai's Anthropic-compatible endpoint, with the caveat that you must select GLM 5.2 explicitly (the default maps to GLM-4.7) and disable vision steps.

## Related Pages

- [GLM 5.2](/blog/glm-5-2) for the full dedicated breakdown: specs, benchmarks, open weights, and pricing
- [Claude Sonnet 5](/blog/claude-sonnet-5) for the recommended daily-driver Claude model
- [Claude Opus 4.8](/blog/claude-opus-4-8) for the frontier ceiling
- [Sonnet 5 vs Opus 4.8](/blog/claude-sonnet-5-vs-opus-4-8) for the Claude-internal comparison
- [GPT-5.6 Sol](/blog/gpt-5-6) for the other major non-Anthropic release this cycle
- Every Claude Model and the model selection guide
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** handles model routing in one config file: Opus for `/spec` planning, Sonnet for everyday iteration, Haiku for trivial calls. You set the policy; Pilot Shell picks per request.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
