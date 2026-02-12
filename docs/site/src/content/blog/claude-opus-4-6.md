---
slug: "claude-opus-4-6"
title: "Claude Opus 4.6: Anthropic's Smartest Model Gets a Major Coding Upgrade"
description: "Claude Opus 4.6 leads Terminal-Bench 2.0, Humanity's Last Exam, and GDPval-AA. Better coding, 1M context beta, 128K output, and same $5/$25 pricing."
date: "2026-02-05"
author: "Max Ritter"
tags: [Reference, Models]
readingTime: 8
keywords: "4, 46, 6, anthropics, claude, coding, gets, major, model, opus, smartest, upgrade"
---

# Claude Opus 4.6: Anthropic's Smartest Model Gets a Major Coding Upgrade

Claude Opus 4.6 leads Terminal-Bench 2.0, Humanity's Last Exam, and GDPval-AA. Better coding, 1M context beta, 128K output, and same $5/$25 pricing.

Claude Opus 4.6 is Anthropic's smartest model, upgraded. It plans more carefully, sustains agentic tasks for longer, operates more reliably in larger codebases, and has better code review and debugging skills to catch its own mistakes. In a first for Opus-class models, it also features a 1M token context window in beta and supports up to 128K output tokens.

The model is state-of-the-art across several evaluations. It tops Terminal-Bench 2.0 for agentic coding, leads all frontier models on Humanity's Last Exam (a complex multidisciplinary reasoning test), and outperforms GPT-5.2 on GDPval-AA by around 144 Elo points and its own predecessor Opus 4.5 by 190 points. Pricing stays identical at $5/$25 per million tokens.

## [Key Specs](#key-specs)

| Spec | Details |
| --- | --- |
| **API ID** | `claude-opus-4-6` |
| **Release Date** | February 5, 2026 |
| **Context Window** | 200K tokens (standard), 1M tokens (beta) |
| **Max Output** | 128,000 tokens |
| **Pricing (Standard)** | $5 input / $25 output per 1M tokens |
| **Pricing (Extended 200K+)** | $10 input / $37.50 output per 1M tokens |
| **Status** | Active, current recommended Opus |

## [What Changed: The Coding Improvements](#what-changed-the-coding-improvements)

Anthropic builds Claude with Claude. Their engineers use Claude Code every day, and every new model gets tested on their own work first. With Opus 4.6, the improvements are specific and practical:

**More careful planning.** The model thinks more deeply before settling on an approach. It revisits its reasoning, catches logical errors earlier, and produces more reliable first-pass results on complex tasks.

**Longer agentic sessions.** Opus 4.6 sustains focus over longer sessions without the performance drift that affected earlier models. Multi-step workflows that span dozens of tool calls complete more reliably.

**Better in large codebases.** Navigation, understanding, and modification of large projects improved. The model maintains better awareness of project structure and conventions across long sessions.

**Stronger code review and debugging.** The model catches its own mistakes more effectively, writes more thorough reviews, and traces bugs through dependency chains with less hand-holding.

**Faster on straightforward work.** Opus 4.6 focuses its deeper reasoning on the hardest parts of a task and moves quickly through the more straightforward parts. If the model overthinks a simpler task, dial effort down from its default (high) to medium with `/effort`.

## [Benchmark Results](#benchmark-results)

Opus 4.6 set new records across multiple categories:

| Benchmark | Score | Notable Comparison |
| --- | --- | --- |
| **Terminal-Bench 2.0** | 65.4% | GPT-5.2: 64.7% |
| **GDPval-AA Elo** | 1,606 | 144 Elo above GPT-5.2, 190 above Opus 4.5 |
| **Humanity's Last Exam** | Leading | Highest among all frontier models |
| **BrowseComp** | Leading | Best at finding hard-to-locate information online |
| **OSWorld** | 72.7% | State-of-the-art for computer use |
| **MRCR v2 (8-needle)** | 76% | Sonnet 4.5: 18.5% |

Terminal-Bench 2.0 is the one that matters most for Claude Code users. It measures real-world terminal task completion across coding, system administration, and file manipulation. Opus 4.6 taking the top spot means it is the strongest model available for the work developers actually do in their terminals.

GDPval-AA measures performance on economically valuable knowledge work across finance, legal, and other professional domains. Opus 4.6 outperforms the industry's next-best model by a wide margin.

The MRCR v2 score of 76% reflects a qualitative shift in how much context the model can actually use. A common complaint about AI models is "context rot" where performance degrades as conversations get longer. Opus 4.6 holds and tracks information over hundreds of thousands of tokens with less drift, and picks up buried details that even Opus 4.5 would miss.

## [1M Token Context Window and 128K Output](#1m-token-context-window-and-128k-output)

Opus 4.6 is the first Opus-class model with a 1M token context window, available in beta. Premium pricing applies for prompts exceeding 200K tokens ($10/$37.50 per million input/output tokens).

The model also supports outputs of up to 128K tokens, up from the previous 16K limit. This lets Claude complete larger-output tasks, generate entire modules, or produce comprehensive analyses without breaking them into multiple requests.

In Claude Code, the standard 200K context window still applies. The 1M window is currently available through the API with a beta header. Your existing [context preservation strategies](/blog/guide/performance/context-preservation) remain relevant for day-to-day Claude Code work.

## [Safety Profile](#safety-profile)

These intelligence gains do not come at the cost of safety. On Anthropic's automated behavioral audit, Opus 4.6 showed a low rate of misaligned behaviors including deception, sycophancy, encouragement of user delusions, and cooperation with misuse. It is just as well-aligned as Opus 4.5, which was the most-aligned frontier model to date.

Opus 4.6 also shows the **lowest rate of over-refusals** of any recent Claude model, meaning fewer false blocks on legitimate requests.

On the cybersecurity front, the model discovered **500+ previously unknown high-severity zero-day flaws** in open-source libraries. Anthropic is accelerating cyberdefensive uses, applying the model to help find and patch vulnerabilities in open-source software. For security-conscious teams, Opus 4.6 serves as a strong first-pass vulnerability scanner during code reviews.

## [New API and Product Features](#new-api-and-product-features)

Alongside the model upgrade, Anthropic shipped several features:

**Adaptive thinking.** Previously, extended thinking was binary (on or off). Now Claude decides when deeper reasoning would be helpful. At the default effort level (high), the model uses extended thinking when useful. Developers can adjust this with four effort levels: low, medium, high (default), and max.

**Context compaction (beta).** Long-running conversations that approach the context window now get automatically summarized and compacted, letting Claude perform longer tasks without hitting limits.

**Agent teams (Claude Code research preview).** Multiple Claude instances can now work in parallel as a coordinated team. Best for tasks that split into independent, read-heavy work like codebase reviews. See the full [agent teams guide](/blog/guide/agents/agent-teams) for details.

**Claude in PowerPoint (research preview).** Claude reads your layouts, fonts, and slide masters to stay on brand, whether building from a template or generating a full deck from a description. Available for Max, Team, and Enterprise plans.

## [Pricing](#pricing)

No price increase. Opus 4.6 costs the same as Opus 4.5:

| Tier | Cost |
| --- | --- |
| **Standard context** (up to 200K) | $5 input / $25 output per 1M tokens |
| **Extended context** (200K+, beta) | $10 input / $37.50 output per 1M tokens |
| **Pro plan** | $20/month |
| **Max plan** | $100/month |

If you have been running Opus 4.5 and managing your [usage and costs](/blog/guide/development/usage-optimization), the upgrade is pure upside at the same price.

## [How to Use Opus 4.6 in Claude Code](#how-to-use-opus-46-in-claude-code)

Switch your default model with one command:

```p-4
claude config set model claude-opus-4-6
```

For per-session overrides without changing your default:

```p-4
claude --model claude-opus-4-6
```

The model is available across all platforms: claude.ai, the Messages API, AWS Bedrock, and Google Vertex AI. The API model identifier is `claude-opus-4-6`.

## [Opus 4.6 vs Opus 4.5: What Changed](#opus-46-vs-opus-45-what-changed)

| Feature | Opus 4.5 | Opus 4.6 |
| --- | --- | --- |
| **Context window** | 200K (standard), 1M (API beta) | 200K (standard), 1M (API beta) |
| **Max output tokens** | 16,384 | 128,000 |
| **Terminal-Bench 2.0** | Not tested on v2.0 | 65.4% (highest) |
| **GDPval-AA Elo** | 1,416 | 1,606 (+190 points) |
| **MRCR v2** | Not tested | 76% |
| **Over-refusals** | Low | Lowest of any recent model |
| **Adaptive thinking** | Not available | Built in |
| **Context compaction** | Auto at 95% | Configurable threshold (beta) |
| **Standard pricing** | $5/$25 per 1M | $5/$25 per 1M (unchanged) |

The core improvements are in coding quality and sustained agentic performance. Everything Opus 4.5 did well (token efficiency, multi-agent delegation, the effort parameter) carries forward. The 128K output limit and adaptive thinking are practical upgrades for everyday Claude Code use.

For [model selection](/blog/models/model-selection), the calculus is simple. Use Opus 4.6 for complex work where reasoning depth matters. Use Sonnet for fast iteration on smaller tasks where speed trumps depth. The pricing parity means there is no cost reason to stay on the older model.

Last updated on

[Previous

Claude Opus 4.5 Guide](/blog/models/claude-opus-4-5-guide)[Next

Opus 4.5](/blog/models/claude-opus-4-5)
