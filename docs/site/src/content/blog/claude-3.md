---
slug: "claude-3"
title: "Claude 3: The Model Family That Started It All"
description: "Claude 3 introduced Opus, Sonnet, and Haiku in March 2024. Vision capabilities, 200K context, and three performance tiers that defined modern AI pricing."
date: "2024-03-04"
author: "Max Ritter"
tags: [Reference, Models]
readingTime: 3
keywords: "3, all, claude, family, model, started, that"
---

# Claude 3: The Model Family That Started It All

Claude 3 introduced Opus, Sonnet, and Haiku in March 2024. Vision capabilities, 200K context, and three performance tiers that defined modern AI pricing.

Claude 3 was the release that turned Anthropic from a safety research lab into a serious competitor. Launched March 4, 2024, it introduced three models at three price points, each purpose-built for different workloads. This was the first time any AI company shipped a coherent family with clear tradeoffs between speed, cost, and capability.

## [Key Specs](#key-specs)

| Spec | Opus | Sonnet | Haiku |
| --- | --- | --- | --- |
| **API ID** | `claude-3-opus-20240229` | `claude-3-sonnet-20240229` | `claude-3-haiku-20240307` |
| **Context window** | 200K tokens | 200K tokens | 200K tokens |
| **Input pricing** | $15 / 1M tokens | $3 / 1M tokens | $0.25 / 1M tokens |
| **Output pricing** | $75 / 1M tokens | $15 / 1M tokens | $1.25 / 1M tokens |
| **Release date** | March 4, 2024 | March 4, 2024 | March 7, 2024 |

## [What Claude 3 Brought to the Table](#what-claude-3-brought-to-the-table)

**Three-tier model family.** Before Claude 3, you picked one model and lived with its tradeoffs. Anthropic gave developers a clear hierarchy: Haiku for speed and cost, Sonnet for the daily workhorse, Opus for the hardest problems. This pricing structure became the template every AI lab copied.

**Vision capabilities.** Claude could see for the first time. Photos, charts, diagrams, handwritten notes, screenshots. You could drop an image into the conversation and get analysis back. This opened up use cases that pure text models simply could not handle.

**200K token context window.** At launch, this was among the largest context windows commercially available. Developers could feed entire codebases, legal documents, or research papers into a single prompt without chunking.

**Benchmark performance.** Opus topped the charts on MMLU (86.8%), GPQA (50.4%), and GSM8K (95.0%), outperforming GPT-4 and Gemini 1.0 Ultra across most academic benchmarks. It was the first Claude model that could credibly claim "best in class."

**Haiku's speed.** The smallest model could read and process a 10,000-token research paper with charts and graphs in under 3 seconds. For high-volume, latency-sensitive applications, nothing else came close at the price point.

## [How It Compared to Predecessors](#how-it-compared-to-predecessors)

Claude 2 was a single model with a single personality. Claude 3 replaced that with a full product line. The jump in reasoning, multilingual support, and accuracy was substantial. Claude 2 had a tendency to refuse tasks unnecessarily. Claude 3 was more willing to engage with complex requests while maintaining safety guardrails. The addition of vision alone made it a fundamentally different product.

## [Current Status](#current-status)

| Model | Status |
| --- | --- |
| Claude 3 Opus | Retired (January 2026) |
| Claude 3 Sonnet | Retired (July 2025) |
| Claude 3 Haiku | Still available |

Claude 3 Haiku remains accessible for lightweight, cost-sensitive workloads. Opus and Sonnet have been fully superseded by the 3.5 and 4.x generations.

## [Navigation](#navigation)

- [All Claude Models](/blog/models) for the complete model index
- [Claude 3.5 Sonnet](/blog/models/claude-3-5-sonnet), the next release that surpassed Opus at a fraction of the cost
- [Model selection strategies](/blog/models/model-selection) for choosing the right model for your workload

Last updated on

[Previous

Claude 3.5 Sonnet](/blog/models/claude-3-5-sonnet)
