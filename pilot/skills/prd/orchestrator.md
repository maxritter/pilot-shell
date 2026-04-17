---
name: prd
description: "Generate Product Requirements Documents with optional research — brainstorm, challenge assumptions, define scope"
argument-hint: "<idea or feature description>"
user-invocable: true
effort: high
model: opus
---

# /prd - Generate Product Requirements Documents

**Strategic thought partner** — turns vague ideas into concrete Product Requirements Documents (PRDs) through one-on-one conversation, with optional research. Produces a PRD that can be handed off directly to `/spec` for implementation.

**Use `/prd` when:** You have an idea but aren't ready to spec it. Requirements are unclear. You need to explore trade-offs, challenge assumptions, or define scope before committing to a plan.

**Use `/spec` instead when:** Requirements are well-defined. You know what to build and roughly how. Skip straight to technical planning.

---

## Workflow

```
Understand → Research (optional) → Clarify → Propose → Converge → Write PRD → Hand off to /spec
```

The entire flow is conversational. One question at a time. No rushing to solutions.
