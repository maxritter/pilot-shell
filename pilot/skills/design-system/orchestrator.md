---
name: design-system
description: Extract, document, or normalize a product UI design system from code, screenshots, or brand sources. Use for visual tokens, theme variables, typography, spacing, colors, radii, shadows, component inventories, variants, states, or building a reusable UI library. Do not use for software architecture, database schemas, or generic system design.
user-invocable: true
license: MIT; adapted from Trystan Sarrade's claude-design-system-prompt
---

# Design System

Turn an existing visual language into authoritative tokens and reusable component contracts. Extraction is evidence work: the source may be inconsistent, but the result must not silently invent consistency.

## Important boundaries

- Inspect the user's code, brand material, screenshots, or named reference before defining values.
- Preserve source names and exact values when they are authoritative. Record near-duplicates and conflicts rather than merging them without a decision.
- Match the project's existing token and component format. Do not introduce a second CSS/JSON/TypeScript/Tailwind representation by default.
- A design-system request concerns product UI. Software architecture, distributed systems, schemas, and API design are outside this skill.

## Select the relevant procedure

Read only the required references, resolved relative to this skill:

| Request | Required reference |
|---|---|
| Colors, type, spacing, radii, shadows, motion, breakpoints, or theme tokens | `references/tokens.md` |
| Reusable UI components, variants, states, composition, or a component inventory | `references/components.md` |

Use both when the user wants a complete system or component library. Token extraction precedes component documentation because component contracts should name real tokens.

## Execution contract

1. Identify authoritative sources and their precedence.
2. Extract observed values, usage, variants, and states with source locations.
3. Separate observed facts, inferred groupings, missing decisions, and recommended consolidation.
4. Emit or update the format already used by the project when the user requested implementation; otherwise produce a reviewable inventory.
5. Verify that every emitted token/component traces to a source or an explicit user decision and that consuming code still builds or renders when files changed.

## Completion

The system is complete when sources and precedence are named, every recorded value is traceable, inconsistencies and gaps remain visible, output matches the repository's native format, and a maintainer can use the result without reverse-engineering the extraction.

## When not to use

- General system design, software architecture, data modeling, or API contracts
- Creating a new screen or flow; use `ui-design`
- Auditing a finished UI without extracting reusable structure; use `ui-design-review`
- Inventing a brand from scratch when there is no source; establish direction through `ui-design`
- Reading or changing a design system stored in Claude Design; use `claude-design` for access, then return here for extraction
