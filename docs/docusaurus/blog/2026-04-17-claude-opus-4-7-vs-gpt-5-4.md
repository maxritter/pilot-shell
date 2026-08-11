---
title: "Claude Opus 4.7 vs GPT-5.4: Coding, Tools, Vision"
description: "Opus 4.7 beats GPT-5.4 on SWE-bench Pro by 6.6 points. Full comparison: coding, tools, vision, pricing, agentic reliability."
slug: claude-opus-4-7-vs-gpt-5-4
date: 2026-04-17
authors:
  - max-ritter
tags:
  - models
---

Opus 4.7 beats GPT-5.4 on SWE-bench Pro by 6.6 points. Full comparison: coding, tools, vision, pricing, agentic reliability.

<!-- truncate -->

Claude Opus 4.7 vs GPT-5.4 is the comparison that matters for anyone wiring agents into production code in April 2026. On SWE-bench Pro, the benchmark that best predicts real-world agentic coding performance, Opus 4.7 scores 64.3% to GPT-5.4's 57.7%. That 6.6-point gap translates into measurably fewer failed PRs, fewer tool errors, and fewer agents that quit halfway through a multi-file refactor. GPT-5.4 still wins a few categories, particularly agentic web research. Everything else tilts toward Opus 4.7.

## TL;DR: Who Wins What

| Category | Winner | Margin |
| --- | --- | --- |
| Agentic coding | Opus 4.7 | +6.6 points on SWE-bench Pro |
| Tool use at scale | Opus 4.7 | +9.2 points on MCP-Atlas |
| Computer use | Opus 4.7 | +3.0 points on OSWorld-Verified |
| Vision resolution | Opus 4.7 | 2,576px vs lower GPT-5.4 defaults |
| Raw reasoning | Opus 4.7 | +4.2 points on HLE (no tools) |
| Pricing transparency | Opus 4.7 | Flat $5/$25 vs tiered GPT-5.4 |
| Agentic web research | GPT-5.4 Pro | +10 points on BrowseComp |
| Tool-assisted search | GPT-5.4 Pro | +4.0 points on HLE (with tools) |
| Graduate reasoning | Effective tie | 94.2% vs 94.4% on GPQA Diamond |

The short version: if your workload is agentic coding, multi-tool orchestration, or computer use, Opus 4.7 is the correct default. If you are building a research agent that lives inside a browser, GPT-5.4 Pro still has the edge.

## Release Context and the Mythos Caveat

Anthropic released [Claude Opus 4.7](/blog/claude-opus-4-7) on April 16, 2026, positioning it as the most capable generally available model in their lineup. There is a caveat worth stating upfront. Opus 4.7 is not Anthropic's most capable model internally. That is Mythos Preview, which Anthropic is holding back for further alignment work and using as a testing ground for stricter safety frameworks. Mythos Preview posts a 93.9% on SWE-bench Verified and 77.8% on SWE-bench Pro per Anthropic's system card. Those numbers are not competing in the market yet.

GPT-5.4 shipped earlier in the year as OpenAI's frontier coding and reasoning model. VentureBeat framed the Opus 4.7 launch as "narrowly retaking the lead for most powerful generally available LLM," which matches what the benchmarks show. Opus 4.7 does not dominate. It wins more categories than it loses, and it wins them by meaningful margins in the workloads most developers care about.

Both models target different audiences in practice. Opus 4.7 is the default in Claude Code, Cursor, and a long list of developer tooling. GPT-5.4 anchors OpenAI's agent stack and the Microsoft ecosystem through Azure and Copilot products. The comparison below reflects how each model performs when you put them side by side on the same tasks.

## Agentic Coding: SWE-bench Pro and Friends

Agentic coding is the workload that separates frontier models from lab curiosities. It tests whether a model can plan, execute, self-correct, and ship working code across multi-file codebases.

Opus 4.7 leads the field on every coding benchmark where direct comparison is possible:

| Benchmark | Opus 4.7 | GPT-5.4 | Gemini 3.1 Pro | Opus 4.6 |
| --- | --- | --- | --- | --- |
| SWE-bench Pro | 64.3% | 57.7% | 54.2% | 53.4% |
| SWE-bench Verified | 87.6% | N/A published | 80.6% | 80.8% |
| Terminal-Bench 2.0 | 69.4% | 75.1%\* | 68.5% | 65.4% |
| CursorBench (per Cursor) | 70% | not disclosed | -- | 58% |

All scores from Anthropic's Opus 4.7 system card unless noted. The Terminal-Bench 2.0 asterisk matters: GPT-5.4's 75.1% uses OpenAI's self-reported harness, which Vellum's benchmark breakdown flags as "not directly comparable" to Anthropic's Terminus-2 harness. That makes Terminal-Bench a directional signal, not a definitive one.

SWE-bench Pro is the number that matters most. It uses held-out repositories and memorization screens to catch models that have seen the test cases during training. Opus 4.7's 64.3% is the highest score any generally available model has posted on it. The +10.9-point jump from Opus 4.6 is the largest single-release coding gain in Anthropic's history.

The customer data backs this up. Cursor measured CursorBench moving from 58% on Opus 4.6 to 70% on Opus 4.7. Linear reported a 13% resolution lift on a 93-task internal coding benchmark. Factory saw "10% to 15% lift in task success" with fewer tool errors. Cognition, which builds Devin, described the model as working "coherently for hours, pushes through hard problems." Rakuten reported 3x more production tasks resolved compared to Opus 4.6 with double-digit gains in both code quality and test quality.

What these numbers translate to operationally: fewer aborted sessions, fewer PRs that fail review, fewer instances of agents giving up halfway through complex refactors. If your workload involves multi-file code changes, Opus 4.7 is the correct choice.

For GPT-5.4, the honest read is that it is a strong coding model that Opus 4.7 is now clearly ahead of on the hardest benchmarks. OpenAI's own Terminal-Bench score suggests GPT-5.4 still has advantages in command-line tasks, but the harness caveat prevents a clean head-to-head.

## Tool Use: MCP-Atlas and Real Agent Work

Tool use is where agents live or die. Every production agent makes dozens of tool calls per task, and a model that picks the wrong tool or formats arguments badly burns tokens on recovery attempts.

| Benchmark | Opus 4.7 | GPT-5.4 | Opus 4.6 |
| --- | --- | --- | --- |
| MCP-Atlas | 77.3% | 68.1% | 62.7% |
| Finance Agent v1.1 | 64.4% | 61.5% | 60.1% |

The MCP-Atlas margin is the single largest gap in the entire Opus 4.7 vs GPT-5.4 comparison. 9.2 points on a benchmark built to stress multi-tool orchestration across MCP servers means Opus 4.7 picks the right tool more often, formats arguments more reliably, and recovers from tool errors with less churn.

Notion confirmed this pattern on their own infrastructure, reporting that Opus 4.7 achieved "+14% over Opus 4.6 at fewer tokens and a third of the tool errors." A third the tool errors is not a small improvement. In a 50-step agentic loop, reducing tool errors by two-thirds compounds dramatically, which is why customers running long agentic traces see outsized gains.

The behavior change under the hood is that Opus 4.7 makes fewer tool calls by default, relying on reasoning instead. Raising the effort level increases tool usage. This is the opposite of the Opus 4.6 default, which leaned tool-heavy. For developers migrating prompts, the fix is usually to push effort to `xhigh` for tool-heavy workloads and let the model reason before acting.

GPT-5.4 remains strong at tool use but is a full 9.2 points behind on the benchmark built specifically to measure it. For teams wiring MCP servers into production agents, this gap is the single most important number to evaluate.

## Computer Use: Vision Meets Action

Computer use is where the 2,576px vision upgrade translates into measurable task success.

| Benchmark | Opus 4.7 | GPT-5.4 | Opus 4.6 |
| --- | --- | --- | --- |
| OSWorld-Verified | 78.0% | 75.0% | 72.7% |

A 3-point lead on OSWorld-Verified is meaningful because the benchmark combines vision, planning, and tool execution in ways that mirror real desktop automation. The reason Opus 4.7 pulls ahead is mechanical. The model now accepts images at 2,576 pixels on the long edge (roughly 3.75 megapixels), more than three times what prior Claude models supported. Coordinates map 1:1 to pixels, so there is no scale-factor math required when directing clicks.

What this means in practice: a screenshot of a dense dashboard now renders with enough fidelity that the model can read small labels and dropdown values it would have hallucinated on Opus 4.6. XBOW's visual-acuity benchmark, which tests fine detail reading, jumped from 54.5% on Opus 4.6 to 98.5% on Opus 4.7. That is not incremental. That is the first Claude model where computer-use agents can reliably read what they are looking at.

GPT-5.4 supports image inputs but does not publish directly comparable resolution limits in the same format. For teams building browser automation, UI testing harnesses, or any agent that needs to read dense visual content, Opus 4.7 is the model to start with.

## Reasoning: The Benchmark That's Nearly Tied

Graduate-level reasoning is effectively a wash at the frontier.

| Benchmark | Opus 4.7 | GPT-5.4 Pro | Gemini 3.1 Pro | Mythos Preview |
| --- | --- | --- | --- | --- |
| GPQA Diamond | 94.2% | 94.4% | 94.3% | 94.6% |
| HLE (no tools) | 46.9% | 42.7% | 44.4% | 56.8% |
| HLE (with tools) | 54.7% | 58.7% | 51.4% | 64.7% |

On GPQA Diamond, all three models sit within 0.4 percentage points. Vellum's analysis calls differences at this level "within noise." The story gets more interesting on HLE, Humanity's Last Exam. Without tools, Opus 4.7 leads GPT-5.4 Pro by 4.2 points, indicating stronger internal knowledge and reasoning before any tool access. With tools enabled, GPT-5.4 Pro takes the lead by 4.0 points, suggesting OpenAI's tool integration currently routes research queries more effectively.

The practical read: for pure reasoning tasks where the model works from context, Opus 4.7 has a small edge. For research workloads where tool access is standard, GPT-5.4 Pro currently executes the tool choreography better. The gap is small enough that either model works for most reasoning tasks. The shape of your agent architecture matters more than the model choice here.

Opus 4.7 also ships with adaptive thinking as the only thinking-on mode. Fixed thinking budgets are gone. The model decides how long to reason based on task complexity. This is closer to how GPT-5.4 Pro has handled reasoning for a while, so migrating prompts across models has become marginally easier.

## Agentic Search and Browsing: Where GPT-5.4 Wins

| Benchmark | Opus 4.7 | GPT-5.4 Pro | Opus 4.6 |
| --- | --- | --- | --- |
| BrowseComp | 79.3% | 89.3% | 83.7% |

This is the one benchmark where Opus 4.7 not only loses but regresses from the prior Claude generation. BrowseComp tests agentic web research: the model has to navigate, read, cross-reference, and synthesize information across multiple pages. GPT-5.4 Pro's 89.3% is a 10-point lead over Opus 4.7 and a meaningful gap over every other model in the comparison.

If your workload is deep web research, competitor monitoring, or any agent that spends most of its time reading and synthesizing pages, GPT-5.4 Pro is currently the stronger choice. Anthropic has not publicly commented on why Opus 4.7 regressed on BrowseComp specifically. Possibilities include the stricter instruction-following behavior reducing exploratory browsing, or the updated tokenizer changing how long pages get processed. Either way, the measured gap is real.

For everything else that involves tool use and synthesis, Opus 4.7 pulls ahead. The BrowseComp result is the main data point that prevents the comparison from being a clean sweep.

## Vision: The Generational Leap

Opus 4.7's vision upgrade is the most pronounced single-release capability jump in the comparison.

| Vision Spec | Opus 4.7 | Opus 4.6 |
| --- | --- | --- |
| Max resolution | 2,576px long edge | 1,568px long edge |
| Max megapixels | 3.75 MP | 1.15 MP |
| XBOW Visual Acuity | 98.5% | 54.5% |
| CharXiv (with tools) | 91.0% | 84.7% (Opus 4.6) |
| Coordinate mapping | 1:1 with pixels | scale-factor math |

Reading dense technical diagrams, chemical structures, architectural blueprints, or high-resolution code screenshots is now reliable. Solve Intelligence confirmed Opus 4.7 reads chemical structures correctly that prior models garbled. Databricks reported 21% fewer errors than Opus 4.6 on OfficeQA Pro, which benchmarks document understanding.

GPT-5.4 supports images, and OpenAI has not published resolution specs in a directly comparable format. For vision-heavy workloads, particularly computer use and document extraction, Opus 4.7 is the stronger default. The 1:1 coordinate mapping also removes a common failure mode where models with scale-factor conversion point their clicks at the wrong pixel.

The practical caveat: higher-resolution images consume more tokens. If fine detail is not necessary for your use case, downsample before sending. For workloads where detail matters (medical images, engineering diagrams, dense dashboards), the token cost is worth it.

## Pricing and Availability

Pricing is where the comparison gets structurally different. Anthropic keeps it simple:

| Tier | Opus 4.7 |
| --- | --- |
| Input | $5 per 1M tokens |
| Output | $25 per 1M tokens |
| Prompt caching | Up to 90% savings |
| Batch processing | 50% savings |
| US-only inference | 1.1x standard |

Pricing is flat across all Opus 4.7 deployments. The 1M token context is available at standard API pricing with no long-context premium.

GPT-5.4 Pro pricing is tiered with structural variation depending on tier and deployment. Anthropic publishes one price sheet. OpenAI publishes several. For procurement, this means you can estimate Opus 4.7 costs directly from token counts. GPT-5.4 estimates require cross-referencing tier documentation. Teams doing serious cost modeling tend to benchmark both on their actual workloads before committing.

**The tokenizer asterisk.** Opus 4.7 uses a new tokenizer that may map identical input to roughly 1.0 to 1.35x more tokens than Opus 4.6. For most content types the overhead is small. For multilingual content and heavily structured text, it can approach the 1.35x upper bound. If you are cost-sensitive, run `/v1/messages/count_tokens` on representative traffic before switching model defaults. This is the main reason existing Opus 4.6 users see higher bills on Opus 4.7 even though the per-token price is unchanged.

Platform availability favors Opus 4.7 for teams that want to standardize on a single deployment story:

| Platform | Opus 4.7 | GPT-5.4 |
| --- | --- | --- |
| Native API | Yes | Yes |
| Amazon Bedrock | Yes | Limited |
| Google Vertex AI | Yes | No |
| Microsoft Foundry | Yes | Yes |
| GitHub Copilot | Yes (7.5x premium multiplier promo, April 30) | Yes |
| Claude Code | Default | No |
| Cursor | Default | Yes |

Opus 4.7's cross-cloud availability on Bedrock, Vertex, and Foundry on day one is meaningful for enterprise procurement. GitHub Copilot's 7.5x premium multiplier promo on Opus 4.7 runs until April 30, 2026, which makes it a cheap way to test the model inside existing Copilot subscriptions before committing to API spend.

## Which Should You Use?

The decision matrix below reflects what each model does best. Pick based on your dominant workload.

| Use Case | Recommended Model | Why |
| --- | --- | --- |
| Agentic coding in Claude Code or Cursor | Opus 4.7 | +6.6 SWE-bench Pro, +12 CursorBench lift |
| Multi-tool agents (MCP, function calling) | Opus 4.7 | +9.2 MCP-Atlas, 1/3 the tool errors of 4.6 |
| Computer use and UI automation | Opus 4.7 | +3.0 OSWorld, 2,576px vision, 1:1 coordinates |
| Document extraction and OCR-heavy pipelines | Opus 4.7 | 98.5% visual acuity, 3.75MP image support |
| Legal and financial document review | Opus 4.7 | 90.9% BigLaw Bench, 64.4% Finance Agent v1.1 |
| Long-running autonomous sessions | Opus 4.7 | Works "coherently for hours" per Cognition |
| Agentic web research with heavy browsing | GPT-5.4 Pro | +10 points BrowseComp, material lead |
| Tool-assisted analyst or research queries | GPT-5.4 Pro | +4.0 HLE with tools, narrow but real |
| Graduate-level reasoning from context | Either | GPQA Diamond tied at 94.2-94.4% |
| Cost-sensitive high-volume generation | Neither (use Haiku or smaller tier) | Opus pricing doesn't fit |

If you are already running a GPT-5.4 pipeline, do not flip traffic wholesale. Run a structured pilot on your top three workloads and measure on your real data. Public benchmarks are directional. Your specific prompt shape and tool chain may weight the differences up or down.

If you are running Opus 4.6, the upgrade to 4.7 is straightforward for coding and agentic work. Plan for the tokenizer change by running a cost baseline on representative traffic, then update your default. For model selection strategy across Claude's full lineup, the same rules apply: Sonnet for daily coding, Opus for complex work, switch models mid-session when the task demands it.

## FAQ

**Is Opus 4.7 better than GPT-5.4 for coding?**

Yes, on the benchmarks that measure real-world coding. Opus 4.7 leads SWE-bench Pro by 6.6 points (64.3% to 57.7%) and posts strong customer wins across Cursor, Linear, Factory, and Cognition. GPT-5.4 still wins Terminal-Bench by a reported 5.7 points, but that benchmark uses OpenAI's self-reported harness, which is not directly comparable to Anthropic's. For agentic coding workloads inside Claude Code, Cursor, or custom pipelines, Opus 4.7 is the correct default.

**How does Opus 4.7 pricing compare to GPT-5.4?**

Opus 4.7 runs $5 per million input tokens and $25 per million output tokens, flat, with 50% batch discounts and up to 90% prompt caching savings. GPT-5.4 Pro pricing is tiered and varies by deployment. The updated tokenizer in Opus 4.7 may produce up to 35% more tokens than Opus 4.6 on identical input, so real costs can creep up even though the per-token rate is unchanged. Run token counts on your actual traffic before committing to budgets.

**What is the xhigh effort level?**

Opus 4.7 introduced a new effort tier called `xhigh` that sits between `high` and `max`. Claude Code defaults to `xhigh` across all plans. It gives most of the reasoning depth of `max` without the full token cost. The effort ladder is now low, medium, high, xhigh, max.

**Does GPT-5.4 beat Opus 4.7 on anything important?**

Yes. GPT-5.4 Pro leads BrowseComp (agentic web research) by 10 points, 89.3% to 79.3%. It also has a narrow 4-point lead on HLE with tools enabled. For browsing-heavy research agents, GPT-5.4 is the stronger default. Everything else in the developer stack (coding, multi-tool use, computer use, vision) tilts to Opus 4.7.

**How is Opus 4.7 vs Gemini 3.1 Pro for coding?**

Opus 4.7 wins SWE-bench Pro by 10.1 points (64.3% to 54.2%) and SWE-bench Verified by 7.0 points (87.6% to 80.6%). Gemini 3.1 Pro offers a 2M token context window versus Opus 4.7's 1M, and undercuts on pricing at $2 input and $12 output per million tokens. For coding workloads, Opus 4.7 is ahead. For long-context retrieval or cost-sensitive classification, Gemini 3.1 Pro deserves evaluation.

**What breaking changes ship with Opus 4.7?**

Three API changes require migration on the Messages API (Claude Managed Agents users are unaffected). Sampling parameters (`temperature`, `top_p`, `top_k`) return a 400 error if set to non-default values. Extended thinking budgets (`thinking.budget_tokens`) return 400; adaptive thinking is the only thinking-on mode. Thinking display defaults to `omitted`, so thinking content is not returned unless you set `display: "summarized"`. Task budgets are available in public beta via the `task-budgets-2026-03-13` beta header, with a 20k token minimum.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** handles model routing in one config file: Opus for `/spec` planning, Sonnet for everyday iteration, Haiku for trivial calls. You set the policy; Pilot Shell picks per request.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
