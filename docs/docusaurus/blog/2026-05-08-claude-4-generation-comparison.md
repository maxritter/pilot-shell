---
title: "Claude 4 Models Compared: 3.7 Sonnet, 4.5 Sonnet, Haiku"
description: "Compare Claude 3.7 Sonnet, Sonnet 4.5, and Haiku 4.5. Specs, benchmarks, smart model switching, and migration paths to current Claude models."
slug: claude-4-generation-comparison
date: 2026-05-08
authors:
  - max-ritter
tags:
  - models
---

Compare Claude 3.7 Sonnet, Sonnet 4.5, and Haiku 4.5. Specs, benchmarks, smart model switching, and migration paths to current Claude models.

<!-- truncate -->

The 4.x line is where Claude Code stopped feeling like a clever assistant and started feeling like infrastructure. Three models drove the transition: **Claude 3.7 Sonnet** (the last 3.x release that introduced extended thinking and set up the 4.x architecture), **Sonnet 4.5** (the workhorse that made $3/$15 daily-driver pricing the new default), and **Haiku 4.5** (the cheap, fast model whose smart switching changed how Claude Code spent your tokens).

All three have since been superseded by [Sonnet 4.6](/blog/claude-sonnet-4-6) and [Opus 4.7](/blog/claude-opus-4-7), but understanding what they shipped — and how they fit together — is still the cleanest way to think about which Claude model to reach for today.

## The Claude Lineup at a Glance

| Model | Released | Input/Output (per 1M) | Context | Status | Best For |
| --- | --- | --- | --- | --- | --- |
| **Opus 4.7** | Apr 2026 | $5 / $25 | 1M (GA) | Active | Heavy reasoning, agent teams, vision-heavy work |
| **Sonnet 4.6** | Feb 2026 | $3 / $15 | 1M (GA) | Active | Daily driver — replaces Sonnet 4.5 across the board |
| **Haiku 4.5** | Oct 2025 | Budget tier | 200K | Active | Routine tasks, smart-switching auto-target |
| **Sonnet 4.5** | Sep 2025 | $3 / $15 | 200K (1M β) | Superseded | Migrate to Sonnet 4.6 — same price, more capability |
| **Claude 3.7 Sonnet** | Feb 2025 | $3 / $15 | 200K | Superseded | Migrate to Sonnet 4.6 for newer codebases |

The short version: **on Claude Code today, you get the best return from running Sonnet 4.6 by default, letting smart model switching route to Haiku 4.5 when work is routine, and reaching for Opus 4.7 when reasoning depth genuinely matters.** The three models below explain how the lineup got there.

## Claude 3.7 Sonnet: The Bridge to Claude 4

Released February 25, 2025, Claude 3.7 Sonnet was the last model in the 3.x line and the one that made Claude usable for genuinely hard problems. It introduced two ideas that became permanent: **hybrid reasoning** and **extended thinking**.

### Key Specs

| Spec | Details |
| --- | --- |
| **API ID** | `claude-3-7-sonnet-20250225` |
| **Context window** | 200K tokens |
| **Input pricing** | $3 per 1M tokens |
| **Output pricing** | $15 per 1M tokens |
| **Thinking token pricing** | Included in output pricing |
| **Max output tokens** | 64,000 (with extended thinking) |
| **Release date** | February 25, 2025 |

### What 3.7 Sonnet Brought

**Extended thinking.** The defining feature. With extended thinking enabled, the model allocates a thinking budget to reason through a problem internally before generating its response. For math proofs, multi-step code logic, scientific analysis, and complex planning, the quality jump was substantial. API users got fine-grained control over the thinking budget. Set a low budget for quick tasks, high budget for problems that demand careful reasoning. The thinking tokens counted toward output pricing but the quality justified the cost on hard problems.

**Hybrid reasoning.** One model, two modes. Quick real-time responses for straightforward questions. Deep step-by-step reasoning for complex ones. You did not have to choose a "thinking model" versus a "fast model" — the same model handled both, switching based on the task.

**State-of-the-art agentic coding.** Claude 3.7 Sonnet set new highs on SWE-bench Verified, which tests real-world software engineering tasks (fixing actual GitHub issues). This was not a synthetic benchmark. The model could read a bug report, navigate a codebase, identify the root cause, and generate a working fix more reliably than any previous Claude.

**Instruction-following and multimodal improvements.** Building on the Claude 3.5 Sonnet v2 gains, 3.7 Sonnet further improved at following complex multi-constraint instructions and handling images, charts, and mixed media inputs.

### Why 3.7 Sonnet Still Matters

It was the last Claude built around explicit thinking-budget control. Every model since has folded that capability in more transparently — you no longer think about thinking tokens, you just ask for harder reasoning and the model routes appropriately. But the SWE-bench gains, agentic loop improvements, and extended-thinking pattern that landed in 3.7 Sonnet became the baseline expectations for Claude Code from that point forward.

If you're still running 3.7 Sonnet in production, the upgrade to [Sonnet 4.6](/blog/claude-sonnet-4-6) is straightforward and the pricing is identical. There is no reason to stay on 3.7 in 2026.

## Haiku 4.5: Smart Switching Becomes the Default

Released October 15, 2025, Haiku 4.5 was the smallest and cheapest model in the 4.5 family. Its real impact came from Claude Code's **smart model switching**, which automatically routed simple tasks to Haiku while reserving Sonnet and Opus for heavier work.

### Key Specs

| Spec | Details |
| --- | --- |
| **API ID** | `claude-haiku-4-5-20251001` |
| **Release Date** | October 15, 2025 |
| **Context Window** | 200K tokens |
| **Max Output** | 8,192 tokens |
| **Pricing** | Budget tier (significantly cheaper than Sonnet) |
| **Status** | Active |

### What Haiku 4.5 Brought

Haiku 4.5 was not built to replace Sonnet or Opus. It was built to handle the 30 to 40% of Claude Code tasks that do not require heavy reasoning, and to handle them fast and cheap.

**Smart model switching.** This was the headline. Claude Code began automatically routing simpler tasks to Haiku 4.5: file reads, quick edits, simple questions, boilerplate generation, and straightforward refactors. Users did not have to manually switch. The system made the call.

**Pro plan availability.** Haiku 4.5 was added for Claude Code Pro plan users, making intelligent routing available without API billing. This made the Pro subscription meaningfully more useful.

**Speed.** Haiku models are fast. Responses that took 3 to 5 seconds on Sonnet came back in under 2 seconds on Haiku. For tight feedback loops, the latency drop matters.

**Cost reduction.** For teams paying per token through the API, routing routine operations to Haiku cut daily costs substantially. Across a team running Claude Code all day, the savings compounded fast.

### What Haiku 4.5 Is Good At

- **File reading and summarization** — scanning a file and answering questions about its contents
- **Quick edits** — small targeted changes to existing code
- **Simple questions** — "what does this function do", "what's the correct import path"
- **Boilerplate generation** — standard patterns, test scaffolding, config files
- **Commit messages and documentation** — clear conventional commit messages and inline docs

### Where Haiku 4.5 Falls Short

Do not rely on Haiku for:

- **Complex architecture decisions.** Multi-system design needs Sonnet 4.6 or Opus 4.7 reasoning depth.
- **Multi-file refactoring.** Large changes across many files need a model that can hold more in working memory.
- **Deep debugging.** Tracing subtle bugs through dependency chains demands stronger reasoning.
- **Nuanced code review.** Catching security issues, performance bottlenecks, and architectural anti-patterns requires more capability.

Smart model switching handles this routing automatically in most cases. If you're explicitly choosing a model for a complex task, reach for Sonnet 4.6 or [Opus 4.7](/blog/claude-opus-4-7).

## Sonnet 4.5: The Workhorse Generation

Released September 29, 2025, Claude Sonnet 4.5 became the default model most Claude Code users set and rarely changed. The combination of speed, intelligence, and $3/$15 pricing made it the obvious daily driver for most of late 2025 and early 2026.

### Key Specs

| Spec | Details |
| --- | --- |
| **API ID** | `claude-sonnet-4-5-20250929` |
| **Alias** | `claude-sonnet-4-5` |
| **Release Date** | September 29, 2025 |
| **Context Window** | 200K tokens (standard), 1M tokens (beta) |
| **Max Output** | 16,384 tokens |
| **Pricing (Input)** | $3 per 1M tokens |
| **Pricing (Output)** | $15 per 1M tokens |
| **Extended Context** | Different pricing tier for 200K+ token windows |
| **Status** | Superseded by Sonnet 4.6 |

### What Sonnet 4.5 Brought

**Top-tier intelligence at Sonnet pricing.** At launch, Sonnet 4.5 scored highest across most evaluation tasks in its tier. Complex reasoning, nuanced code generation, and multi-step problem solving all showed measurable improvement over previous Sonnet models.

**Best-in-class agent performance.** Agentic workflows became significantly more reliable. Fewer abandoned chains, better error recovery, and smarter decisions about when to ask for clarification versus proceed.

**1M token context window (beta).** For long sessions or large codebases, the beta 1M context window meant working through entire features without hitting context compaction. This required a beta header via the API or Console access.

**Coding benchmark leadership.** SWE-bench scores, HumanEval pass rates, and real-world coding task completion all placed Sonnet 4.5 at or near the top of its class. The gap between Sonnet and Opus narrowed significantly.

### How Sonnet 4.5 Stacked Up

Relative to Sonnet 4, the jump was substantial. Sonnet 4.5 handled ambiguity better, produced more idiomatic code across more languages, and maintained coherence over longer conversations.

Relative to Opus 4.1, the comparison got interesting. Sonnet 4.5 matched or exceeded Opus 4.1 on many coding tasks while running faster and costing less. For most Claude Code workflows, Sonnet 4.5 became the better choice.

The $3/$15 pricing kept it accessible for teams running Claude Code throughout the workday. At roughly one-fifth the cost of Opus models at the time, Sonnet 4.5 delivered 90% or more of the capability.

## Smart Model Routing Across the Lineup

The 4.5 generation made a single strategy obvious: **don't pick one model, route between them.** Claude Code's smart model switching codified this pattern. Here's how it shakes out today across the active and superseded lineup.

| Task Class | Model in 4.5 era | Model today (mid-2026) |
| --- | --- | --- |
| File reads, single-line edits | Haiku 4.5 | Haiku 4.5 |
| Boilerplate, scaffolding, commit msgs | Haiku 4.5 | Haiku 4.5 |
| Routine refactors, normal coding | Sonnet 4.5 | Sonnet 4.6 |
| Multi-file refactor, hard debugging | Sonnet 4.5 (extended) | Sonnet 4.6 or Opus 4.7 |
| Architecture decisions, agent teams | Opus 4.1 / Opus 4.5 | Opus 4.7 |
| Vision-heavy tasks (screenshots, diagrams) | Sonnet 4.5 | Opus 4.7 (3x resolution) |

The pattern is the same. The names shifted up by a generation. If you wired smart model switching during the 4.5 era, the routing logic still works — you just want the labels updated to point at Sonnet 4.6 and Opus 4.7 where they used to say Sonnet 4.5 and Opus 4.5.

For tactical model switching during specific sessions, the model selection guide covers when to override defaults manually.

## Migration Guide

If you're still running any of these three in production, here's the path forward.

### From Claude 3.7 Sonnet → Sonnet 4.6

Direct upgrade. Same $3/$15 pricing. Substantially better at coding, instruction-following, and agentic workflows. The 1M context window is now generally available, not gated behind a beta header. Replace `claude-3-7-sonnet-20250225` with `claude-sonnet-4-6` in your API calls and you're done.

The one thing to retest: any prompts that explicitly tuned the extended-thinking budget on 3.7 Sonnet. Sonnet 4.6 handles that more transparently, and your old budget settings may be over- or under-allocated relative to the new defaults. Sample 5 to 10 representative prompts before flipping the switch in production.

### From Sonnet 4.5 → Sonnet 4.6

Same pricing. Same 200K base context (1M now generally available). Stronger coding scores, better computer-use accuracy (94% on insurance benchmarks), and Opus-level performance on most tasks. Drop-in upgrade for nearly all workloads. The few cases that benefit from staying on 4.5 are rare enough that you can default to migrating everything and roll back the exceptions if any surface.

### From Haiku 4.5 → Stay

Haiku 4.5 is still the active Haiku and the smart-switching auto-target. No migration needed. The next generation of Haiku will likely arrive in late 2026; until then, Haiku 4.5 is the budget tier.

## Cost Optimization Patterns That Survived the Generation

The cost playbook the 4.5 generation made obvious is still the right playbook on 4.6 and 4.7.

**Default to Sonnet 4.6, route routine work to Haiku 4.5.** In Claude Code, smart model switching does this automatically. On the API, set Sonnet 4.6 as your default model and explicitly call Haiku 4.5 for jobs you know are routine (commit message generation, log summarization, simple classifications, boilerplate scaffolding).

**Reserve Opus 4.7 for genuinely hard problems.** At $5/$25, Opus is roughly 5x the input cost and 1.7x the output cost of Sonnet. The capability gap is real but only worth paying for on architecture decisions, multi-system design, complex debugging, and vision-heavy work where Opus 4.7's 3x resolution actually matters.

**Use agent fundamentals to push routing into your tooling.** Cheap subagents on Haiku for parallel research and file reads. Mid-tier orchestrators on Sonnet 4.6 for synthesis. Heavy specialists on Opus 4.7 only for the work that needs it. The same pattern that worked with Sonnet 4.5 + Haiku 4.5 in late 2025 still works — the model labels just shifted.

## Where to Go Next

- [Sonnet 4.6](/blog/claude-sonnet-4-6) — current daily driver, what most readers should be on
- [Opus 4.7](/blog/claude-opus-4-7) — current heavy-lifting model with 3x vision and self-verification
- All Claude Models — the full timeline from Claude 3 forward
- Model selection guide — strategic switching during sessions
- Usage optimization — cost management across the lineup
- Deep thinking techniques — getting the most out of extended-thinking-style reasoning on current models

The 4.5 generation made smart model switching a default rather than a power-user trick. Sonnet 4.6 and Opus 4.7 inherited that infrastructure. Knowing how it got built — what 3.7 Sonnet introduced, what Haiku 4.5 made automatic, what Sonnet 4.5 made affordable — is the cleanest way to understand why the current Claude lineup looks the way it does.

[Opus 4.5](/blog/claude-opus-4-5)

Opus 4.1
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** handles model routing in one config file: Opus for `/spec` planning, Sonnet for everyday iteration, Haiku for trivial calls. You set the policy; Pilot Shell picks per request.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
