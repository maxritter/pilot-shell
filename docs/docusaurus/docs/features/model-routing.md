---
sidebar_position: 5
title: Model Routing
description: Opus where reasoning matters, Sonnet where speed and cost matter
---

# Model Routing

Opus where reasoning matters, Sonnet where speed and cost matter.

Pilot automatically routes each phase to the right model. Rather than always using the most powerful (and most expensive) model, it applies reasoning where reasoning has the highest impact — and uses fast, cost-effective execution where a clear spec makes quality predictable.

## Routing Table

| Phase | Model | Rationale |
|-------|-------|-----------|
| **Planning** | Opus | Exploring your codebase, designing architecture, and writing the spec requires deep reasoning. A good plan is the foundation — invest here. |
| **Spec Review** | Sonnet | The spec-review sub-agent validates completeness and challenges assumptions on every feature spec. Optional Codex adversarial review provides an independent second opinion. *(enabled by default — disable in Console Settings → Reviewers)* |
| **Implementation** | Sonnet | With a solid plan, writing code is straightforward. Sonnet is fast, cost-effective, and produces high-quality code when guided by a clear spec and strong hooks. |
| **Changes Review** | Sonnet | The unified changes-review agent handles deep code review (compliance + quality + goal). The orchestrator runs mechanical checks and applies fixes efficiently. Optional Codex adversarial review for additional coverage. *(enabled by default — disable in Console Settings → Reviewers)* |

## The Insight

- Implementation is the easy part when the plan is good and verification is thorough
- Pilot invests reasoning power (Opus) where it has the highest impact: planning
- Sonnet handles implementation and verification — guided by a solid plan and structured review agents
- The result: better output at lower cost than running Opus everywhere

:::tip Fully configurable
Configure via the Pilot Shell Console Settings tab (`localhost:41777/#/settings`). Choose between Sonnet 4.6 and Opus 4.7 for the main session, each command, and each sub-agent independently. Context window size (200K or 1M) is configurable via the Extended Context toggle. API subscribers (Team, Enterprise) get 1M at no additional cost with all models. Max plan users must set all models to Opus — Sonnet 1M is not included in Max.
:::

## Pinning a Legacy or Specific Model Version

The model dropdown in Console Settings includes a **Custom…** option that lets you enter an explicit Anthropic model ID instead of a Claude Code alias. This is useful when:

- You want to pin a specific historical version (e.g. `claude-opus-4-6`, `claude-opus-4-5`, `claude-sonnet-4-5-20250929`) for reproducibility.
- A newer release trips content filters on code that previous releases handled, and you need a reliable fallback while the issue is reported.
- You are standardizing across a team and want every machine on the exact same model ID.

Accepted values:

- Any alias supported by Claude Code — currently `sonnet` and `opus`.
- Any explicit Anthropic model ID matching `claude-<suffix>` (e.g. `claude-opus-4-6`, `claude-haiku-4-5`).

The Extended Context (`1M`) toggle only applies to the `sonnet` and `opus` aliases — explicit model IDs are passed through to Claude Code exactly as entered, so pick the concrete ID for the context window you want.
