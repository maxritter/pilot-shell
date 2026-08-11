---
title: "Claude Sonnet 4.5: The Best Coding Model Gets Better"
description: "Claude Sonnet 4.5 launched September 2025 with top intelligence across most tasks, 1M beta context, and best-in-class coding performance."
slug: claude-sonnet-4-5
date: 2025-09-29
authors:
  - max-ritter
tags:
  - models
---

Claude Sonnet 4.5 launched September 2025 with top intelligence across most tasks, 1M beta context, and best-in-class coding performance.

<!-- truncate -->

Claude Sonnet 4.5 launched on September 29, 2025, as the highest-intelligence Sonnet model at its price point. It delivered best-in-class coding and agent performance while maintaining the speed that made Sonnet the default choice for Claude Code daily use.

## Key Specs

| Spec | Details |
| --- | --- |
| **API ID** | `claude-sonnet-4-5-20250929` |
| **Alias** | `claude-sonnet-4-5` |
| **Release Date** | September 29, 2025 |
| **Context Window** | 200K tokens (standard), 1M tokens (beta) |
| **Max Output** | 16,384 tokens |
| **Pricing (Input)** | $3 per million tokens |
| **Pricing (Output)** | $15 per million tokens |
| **Extended Context** | Different pricing tier for 200K+ token windows |
| **Status** | Superseded by Sonnet 4.6 |

## What Sonnet 4.5 Brought to the Table

This release hit the sweet spot that Claude Code users care about most: high intelligence at a price that supports all-day use.

**Top-tier intelligence.** At launch, Sonnet 4.5 scored highest across most evaluation tasks in its tier. Complex reasoning, nuanced code generation, and multi-step problem solving all showed measurable improvement over previous Sonnet models.

**Best-in-class agent performance.** Agentic workflows (where Claude chains multiple tool calls together to accomplish a goal) became significantly more reliable. Fewer abandoned chains, better error recovery, and smarter decision-making about when to ask for clarification versus proceeding.

**1M token context window (beta).** For users with long sessions or large codebases, the beta 1M context window meant working through entire features without hitting context compaction. This required a beta header via the API or Console access, but it was a meaningful capability for extended engineering sessions.

**Coding benchmark leadership.** SWE-bench scores, HumanEval pass rates, and real-world coding task completion all placed Sonnet 4.5 at or near the top of its class. The gap between Sonnet and Opus narrowed significantly with this release.

## How It Compared to Previous Models

Relative to Sonnet 4, the jump was substantial. Sonnet 4.5 handled ambiguity better, produced more idiomatic code across a wider range of languages, and maintained coherence over longer conversations.

Relative to Opus 4.1, the comparison got interesting. Sonnet 4.5 matched or exceeded Opus 4.1 on many coding tasks while running faster and costing less. For most Claude Code workflows, Sonnet 4.5 became the better choice.

The $3/$15 pricing (input/output per million tokens) kept it accessible for teams running Claude Code throughout the workday. At roughly one-fifth the cost of Opus models, Sonnet 4.5 delivered 90% or more of the capability.

## The Workhorse Model

Sonnet 4.5 became the model that most Claude Code users set as their default and rarely changed. The combination of speed, intelligence, and cost made it the obvious daily driver.

For tasks requiring deeper reasoning, users would switch to Opus. For simple, quick tasks, [Haiku 4.5](/blog/claude-haiku-4-5) handled the job at a fraction of the cost. But Sonnet 4.5 covered the middle 90% of work without compromise.

## Current Status

Sonnet 4.5 has been superseded by [Sonnet 4.6](/blog/claude-sonnet-4-6), which delivers Opus-level intelligence at the same $3/$15 pricing. Sonnet 4.5 remains available through the API using its full model ID, but Sonnet 4.6 is now the recommended Sonnet for all workloads.

## Related Pages

- All Claude Models for the complete model timeline
- Opus 4.1 for the previous generation's top model
- [Haiku 4.5](/blog/claude-haiku-4-5) for the budget-friendly option in the same family
- Model selection guide for strategic model switching
- Usage optimization for managing costs across models
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** handles model routing in one config file: Opus for `/spec` planning, Sonnet for everyday iteration, Haiku for trivial calls. You set the policy; Pilot Shell picks per request.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
