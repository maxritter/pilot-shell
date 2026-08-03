---
name: prd
description: "Turns a rough idea into a written, approved Product Requirements Document, with optional market and technical research. Use when the user types /prd, has a feature idea that is still vague about who it serves or what counts as done, wants a thought partner to pressure-test a concept before building, or asks for a PRD, product spec, or requirements doc. Not for work already scoped enough to plan — that is /spec."
argument-hint: "<idea or feature description>"
user-invocable: true
---

# /prd - Generate Product Requirements Documents

<HARD-GATE>
Do NOT invoke `/spec`, `/spec-plan`, `/spec-implement`, write any code, scaffold any project, or take any implementation action until you have written a PRD and the user has approved it. This applies to EVERY idea regardless of perceived simplicity.

`/prd`'s output is a written PRD at the path determined in Step 7 (write-prd). The terminal state is offering hand-off to `/spec` and waiting for the user. The skill does not invoke implementation skills directly — Step 8 prints the `/spec` command for the user to run.
</HARD-GATE>

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
- **Divergent (Ideate):** free-form prose, the agent pitches directions, user reacts. Used when the idea is vague.
- **Convergent (Clarify → Converge):** structured `AskUserQuestion` forms with predefined options. Used once the shape is known.

The phase boundary is a default, not a wall — Clarify can drop back into 1-2 prose turns when a question opens a genuinely new unknown, then return to structured forms.

The entire flow is conversational. One question at a time. No rushing to solutions.

## Principles

- **Understand before solving.** The PRD describes WHAT and WHY; `/spec` handles HOW. Resist over-specifying technically.
- **Be a thought partner, not an order-taker.** Challenge assumptions, surface trade-offs, name red flags and scope-creep risks while they're still cheap to fix.
- **YAGNI ruthlessly.** Apply rung 1 of the ladder (`development-practices.md` → *Build the least that works*) to every proposed feature: does this need to exist at all? The cheapest scope to cut is the scope never specified.
- **Write for handoff.** The PRD is the contract between requirements and specification — a reader running `/spec` should need nothing else.

## Interaction budget

Questions are the expensive part of this skill, and every avoidable one costs the user a round-trip.

**Target: 2–4 user interactions total**, from first message to hand-off. A typical concrete idea spends one Clarify batch and one combined approach+scope confirmation. Ideation rounds (Step 3) are conversation, not interactions — they don't count against this, but they have their own 1–3 round ceiling.

Spend an interaction only when the answer would **change what gets built**. Before every question, ask in order:

1. Can the codebase answer this? → read it (Step 1's scan, `codegraph_explore`, Semble). Never ask the user about facts the code already encodes.
2. Was it answered by the original idea or an earlier answer? → don't re-ask.
3. Is the decision reversible and low-cost? → pick the sensible default, record it under Key Decisions, move on.

Combine related decisions into one call rather than serialising them — approach selection (Step 5) and scope confirmation (Step 6) belong in one interaction whenever the scope follows from the approach.

<!-- CC-ONLY -->
**Use the `AskUserQuestion` tool for user questions during convergent phases (Steps 4-8)** — it renders a structured form; don't fall back to plain-text numbered questions.
<!-- /CC-ONLY -->
<!-- CODEX-START
**Use plain-text numbered options for user questions** — the Claude question tool isn't callable in Codex. Present 2-4 concrete options with trade-offs, and wait for the user's response.

### Codex PRD Pacing Contract

For Codex, PRD quality means enough product clarity to hand off to `$spec`, not exhaustive discovery.

- Reach a first complete PRD draft before context reaches 40% unless the user explicitly asks for deep research or brainstorming.
- Use one bounded project-context pass: at most one CodeGraph orientation call when existing runtime-code structure is unknown, plus at most one Semble search, then targeted reads. Skip CodeGraph for docs, rules, markdown, config, UI copy, or named paths.
- Default to Quick research for repo-local ideas. Ask about Standard or Deep research only when the user requests market/current external context or the idea depends on external facts.
- Ask at most two decision prompts before the PRD draft: one scope/requirements prompt and one approach/scope confirmation prompt. If the answer is reversible, document the assumption and draft.
- Do not keep ideating after a viable direction exists. Capture alternatives as deferred ideas and move to the PRD.
CODEX-END -->
