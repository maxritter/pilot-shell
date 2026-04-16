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
