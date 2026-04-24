---
name: prd
description: "Generate Product Requirements Documents with optional research — brainstorm, challenge assumptions, define scope"
argument-hint: "<idea or feature description>"
user-invocable: true
model: opus
---

# /prd - Generate Product Requirements Documents

**Strategic thought partner and brainstorming surface** — turns vague ideas into concrete Product Requirements Documents (PRDs) through one-on-one conversation, with optional research. Produces a PRD that can be handed off directly to `/spec` for implementation.

**Use `/prd` when:**
- You have an idea but aren't ready to spec it
- Requirements are unclear or you only have a problem statement, not a solution
- You want to **brainstorm back-and-forth** before locking anything down — pitch ideas, react, refine, then converge
- You need to explore trade-offs, challenge assumptions, or define scope before committing to a plan

**Use `/spec` instead when:** Requirements are well-defined. You know what to build and roughly how. Skip straight to technical planning.

`/prd` and `/spec` are designed to chain: `/prd` produces the requirements doc, then offers to hand off to `/spec` for implementation.

---

## Workflow

```
Understand → Research (optional) → Ideate (if vague) → Clarify → Propose → Converge → Write PRD → Hand off to /spec
```

**Two modes inside one flow:**
- **Divergent (Ideate):** free-form prose, Claude pitches directions, user reacts. Used when the idea is vague.
- **Convergent (Clarify → Converge):** structured `AskUserQuestion` forms with predefined options. Used once the shape is known.

The phase boundary is a default, not a wall — Clarify can drop back into 1-2 prose turns when a question opens a genuinely new unknown, then return to structured forms.

The entire flow is conversational. One question at a time. No rushing to solutions.
