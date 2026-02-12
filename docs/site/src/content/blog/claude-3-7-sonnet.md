---
slug: "claude-3-7-sonnet"
title: "Claude 3.7 Sonnet: Hybrid Reasoning and Extended Thinking"
description: "Claude 3.7 Sonnet introduced hybrid reasoning in February 2025. Extended thinking mode lets Claude pause and think step-by-step before responding."
date: "2025-02-25"
author: "Max Ritter"
tags: [Reference, Models]
readingTime: 4
keywords: "3, 37, 7, claude, extended, hybrid, reasoning, sonnet, thinking"
---

# Claude 3.7 Sonnet: Hybrid Reasoning and Extended Thinking

Claude 3.7 Sonnet introduced hybrid reasoning in February 2025. Extended thinking mode lets Claude pause and think step-by-step before responding.

Claude 3.7 Sonnet was the model that gave Claude the ability to think before it speaks. Released February 25, 2025, it introduced hybrid reasoning, a mode where Claude can pause, work through a problem step-by-step internally, and then deliver a more accurate response. This was the last model in the Claude 3.x generation, and it set the foundation for everything that followed in the Claude 4 line.

## [Key Specs](#key-specs)

| Spec | Details |
| --- | --- |
| **API ID** | `claude-3-7-sonnet-20250225` |
| **Context window** | 200K tokens |
| **Input pricing** | $3 / 1M tokens |
| **Output pricing** | $15 / 1M tokens |
| **Thinking token pricing** | Included in output pricing |
| **Max output tokens** | 64,000 (with extended thinking) |
| **Release date** | February 25, 2025 |

## [What Claude 3.7 Sonnet Brought to the Table](#what-claude-37-sonnet-brought-to-the-table)

**Extended thinking.** The defining feature. When enabled, Claude can "think out loud" internally before generating a response. Instead of immediately producing output token by token, the model allocates a thinking budget to reason through the problem first. For math proofs, multi-step code logic, scientific analysis, and complex planning tasks, extended thinking produced dramatically better results.

API users got fine-grained control over the thinking budget. Set a low budget for quick tasks, high budget for problems that demand careful reasoning. The thinking tokens counted toward output pricing but the quality improvement justified the cost for hard problems.

**Hybrid reasoning.** Claude 3.7 Sonnet could operate in two modes within the same conversation. Quick, real-time responses for straightforward questions. Deep, step-by-step reasoning for complex ones. You did not have to choose a "thinking model" versus a "fast model." One model handled both, switching based on the task.

**State-of-the-art agentic coding.** The model set new highs on SWE-bench Verified, which tests real-world software engineering tasks (fixing actual GitHub issues). This was not a synthetic benchmark. Claude 3.7 Sonnet could read a bug report, navigate a codebase, identify the root cause, and generate a working fix more reliably than any previous Claude model.

**Instruction-following and multimodal improvements.** Building on the [3.5 Sonnet v2](/blog/models/claude-3-5-sonnet-v2) gains, 3.7 Sonnet further improved at following complex, multi-constraint instructions. It also handled images, charts, and mixed media inputs with higher accuracy.

## [Extended Thinking in Practice](#extended-thinking-in-practice)

Extended thinking transformed how developers approached hard problems with Claude. The pattern was straightforward:

1. Send a complex prompt (code review, mathematical proof, architectural decision)
2. Claude allocates thinking budget to reason through it internally
3. The response arrives with higher accuracy and fewer logical errors

The biggest gains showed up in math, science, and multi-file code changes. Tasks that previously required multiple back-and-forth corrections often resolved correctly on the first attempt with extended thinking enabled.

For a deeper look at how to use this effectively, see the [deep thinking techniques guide](/blog/guide/performance/deep-thinking-techniques).

## [How It Compared to Claude 3.5 Sonnet v2](#how-it-compared-to-claude-35-sonnet-v2)

Same pricing ($3/$15 per million tokens). Same 200K context window. But meaningfully better at reasoning, coding, and following instructions. The max output token limit jumped to 64,000 when using extended thinking (up from 8,192), making it viable for generating long-form code, documentation, or analysis in a single response.

The most important difference was qualitative: Claude 3.7 Sonnet made fewer reasoning errors on complex tasks. The extended thinking mode gave it a way to "show its work" internally, catching mistakes before they reached the output.

## [Current Status](#current-status)

| Model | Status |
| --- | --- |
| Claude 3.7 Sonnet | Superseded by Claude 4 generation |

Claude 3.7 Sonnet was the bridge between the 3.x and 4.x generations. The hybrid reasoning and extended thinking capabilities it pioneered became standard features in [Claude 4](/blog/models/claude-4) and every model that followed. If you are still running 3.7 Sonnet in production, the upgrade path to Claude 4 models is straightforward and the pricing remains competitive.

## [Navigation](#navigation)

- [All Claude Models](/blog/models) for the complete model index
- [Claude 3.5 Sonnet v2](/blog/models/claude-3-5-sonnet-v2), the October 2024 predecessor
- [Claude 4](/blog/models/claude-4), the next generation
- [Deep thinking techniques](/blog/guide/performance/deep-thinking-techniques) for getting the most out of extended thinking
- [Model selection strategies](/blog/models/model-selection) for choosing between Claude models

Last updated on

[Previous

Claude 4](/blog/models/claude-4)[Next

Claude 3.5 Sonnet v2](/blog/models/claude-3-5-sonnet-v2)
