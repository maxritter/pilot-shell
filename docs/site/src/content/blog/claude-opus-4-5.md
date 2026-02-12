---
slug: "claude-opus-4-5"
title: "Claude Opus 4.5: 67% Cheaper, 76% Fewer Tokens"
description: "Claude Opus 4.5 launched November 2025 with a 67% price cut to $5/$25 per million tokens and 76% fewer output tokens. The efficiency revolution for Claude Code."
date: "2025-11-24"
author: "Max Ritter"
tags: [Reference, Models]
readingTime: 4
keywords: "4, 45, 5, 67, 76, cheaper, claude, fewer, opus, tokens"
---

# Claude Opus 4.5: 67% Cheaper, 76% Fewer Tokens

Claude Opus 4.5 launched November 2025 with a 67% price cut to $5/$25 per million tokens and 76% fewer output tokens. The efficiency revolution for Claude Code.

Claude Opus 4.5 launched on November 24, 2025, and rewrote the economics of AI-assisted development. A 67% price cut to $5/$25 per million tokens, combined with 76% fewer output tokens for equivalent work, made premium-tier intelligence accessible for daily use.

## [Key Specs](#key-specs)

| Spec | Details |
| --- | --- |
| **API ID** | `claude-opus-4-5-20251101` |
| **Release Date** | November 24, 2025 |
| **Context Window** | 200K tokens (standard), 1M tokens (with beta header) |
| **Max Output** | 16,384 tokens |
| **Pricing (Input)** | $5 per million tokens |
| **Pricing (Output)** | $25 per million tokens |
| **Previous Opus Pricing** | $15/$75 per million tokens |
| **SWE-bench Verified** | 80.9% (new high at release) |
| **Status** | Active, superseded by Opus 4.6 for latest features |

## [What Opus 4.5 Brought to the Table](#what-opus-45-brought-to-the-table)

Three headline changes defined this release: pricing, token efficiency, and multi-agent orchestration.

**67% cheaper.** Opus 4 and 4.1 priced at $15 input / $75 output per million tokens. Opus 4.5 dropped to $5/$25. For teams running Opus through the API, this was an immediate and dramatic cost reduction.

**76% fewer output tokens.** Opus 4.5 produced the same quality work with dramatically less output. Where [Sonnet 4.5](/blog/models/claude-sonnet-4-5) might generate 500 tokens to complete a task, Opus 4.5 often accomplished the same result in roughly 120 tokens. Less verbose, more precise.

**50% fewer tool calls.** The model completed tasks with half the tool call overhead of previous generations. Fewer round trips meant faster task completion and lower cumulative costs.

**With Tool Search enabled, the efficiency gains compounded to 85% token reduction.** Tool Search let the model discover and select the right tools dynamically, eliminating wasted calls to irrelevant tools.

## [Multi-Agent Mastery](#multi-agent-mastery)

Anthropic explicitly trained Opus 4.5 for delegation and sub-agent orchestration. This was not a side effect of general capability improvement. It was a targeted training objective.

The result: Opus 4.5 writes better prompts for sub-agents, structures [task distribution](/blog/guide/agents/task-distribution) more effectively, and synthesizes results from parallel agents with less information loss. If you run multi-agent workflows in Claude Code, Opus 4.5 was the first model that made orchestration feel reliable rather than fragile.

GitHub reported that Opus 4.5 "surpasses internal coding benchmarks while cutting token usage in half." Replit confirmed similar results on their internal evaluations.

## [New Capabilities](#new-capabilities)

**Effort parameter.** A new API control for tuning the thinking depth per request. Low effort for quick tasks, high effort for complex reasoning. You control the budget without switching models.

**Auto-compaction.** When sessions hit 95% of the context window, the model automatically compacts earlier messages while preserving the full conversation thread. This created effectively unbounded session length for long engineering tasks.

**1M token context window.** Available with a beta header via the API, matching the extended context capability introduced with [Sonnet 4.5](/blog/models/claude-sonnet-4-5).

## [How It Compared to Sonnet 4.5](#how-it-compared-to-sonnet-45)

This was the first Opus model where cost-per-task approached Sonnet territory. The raw per-token price was still higher ($5/$25 vs $3/$15), but the 76% reduction in output tokens frequently made Opus 4.5 cheaper per completed task.

For complex work requiring deep reasoning, the math was clear: Opus 4.5 delivered better results at comparable or lower total cost. For routine tasks, [Sonnet 4.5](/blog/models/claude-sonnet-4-5) and [Haiku 4.5](/blog/models/claude-haiku-4-5) remained the more efficient choices.

## [The Detailed Guide](#the-detailed-guide)

This page covers the model profile and specs. For a comprehensive walkthrough of how to configure and use Opus 4.5 in Claude Code (including the effort parameter, auto-compaction, and multi-agent patterns), see the [Claude Opus 4.5 usage guide](/blog/models/claude-opus-4-5-guide).

## [Current Status](#current-status)

Opus 4.5 remains active and available through the API. It has been superseded by [Opus 4.6](/blog/models/claude-opus-4-6) for the latest features and capability improvements, but continues to serve as a reliable, well-understood model for production workflows.

## [Related Pages](#related-pages)

- [All Claude Models](/blog/models) for the complete model timeline
- [Haiku 4.5](/blog/models/claude-haiku-4-5) for the budget option in the same family
- [Opus 4.6](/blog/models/claude-opus-4-6) for the next generation
- [Opus 4.5 usage guide](/blog/models/claude-opus-4-5-guide) for hands-on configuration
- [Model selection guide](/blog/models/model-selection) for strategic model switching

Last updated on

[Previous

Claude Opus 4.6](/blog/models/claude-opus-4-6)[Next

Sonnet 4.5](/blog/models/claude-sonnet-4-5)
