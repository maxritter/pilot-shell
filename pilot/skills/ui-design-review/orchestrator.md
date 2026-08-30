---
name: ui-design-review
description: Review or polish a product UI for accessibility, brand fidelity, hierarchy, rhythm, responsive behavior, themes, interaction states, and generic AI-template patterns. Use for visual audits, accessibility checks, UX polish, UI critique, or pre-ship design review. Do not use for generic code review, backend review, or API design.
user-invocable: true
license: MIT; adapted from Trystan Sarrade's claude-design-system-prompt
---

# UI Design Review

Judge the rendered product, not the source in isolation. A design review distinguishes standards failures, product-quality problems, and subjective preferences so the user can trust the verdict.

## Mutation boundary

**Review and audit requests are report-only.** Inspect, execute read-only checks, and return evidence-backed findings without editing files. **Change files only when the user asks to fix, polish, redesign, or implement**, or when a parent workflow explicitly carries that authorized fix scope.

## Establish the baseline

Read the affected UI, its tokens/components, supported themes, product context, and user-stated constraints. Capture the current rendered state before proposing a correction. Existing brand and system choices outrank generic taste; accessibility requirements do not.

## Select review lanes

Read only the relevant references, resolved relative to this skill:

| Lane | Required reference |
|---|---|
| Contrast, semantics, keyboard, forms, motion, target size, or WCAG review | `references/accessibility.md` |
| Brand fidelity, content discipline, hierarchy, rhythm, system consistency, or generic-template review | `references/visual-quality.md` |
| Interactive states, responsive/theme coverage, runtime verification, or final polish | `references/interaction-and-verification.md` |

A full pre-ship review uses all three. A focused contrast question reads only accessibility. Complete every applicable lane before aggregating findings so early fixes do not hide later issues.

Run lanes in the current agent by default. When the session exposes agent tools and multiple read-only lanes are genuinely independent, the active agent may delegate the minimum useful number with non-overlapping ownership, then integrates and verifies the result itself. Tool availability never changes the review contract.

## Findings contract

Deduplicate findings and classify them:

1. **Blocker** — standards failure or interaction/accessibility defect that prevents safe use or completion.
2. **Quality issue** — broken hierarchy, system inconsistency, missing state, misleading content, responsive/theme defect, or unearned template pattern with clear product impact.
3. **Advisory** — subjective refinement or deterministic detector signal that needs human judgment.

Every finding names the affected surface, evidence, user impact, and concrete correction. Do not report a preferred aesthetic as a standards failure.

## Fix and re-verify

When edits are authorized, fix blockers first, then in-scope quality issues. Preserve established tokens/components and avoid unrelated redesign. Re-run the actual interaction, affected viewport/theme/state matrix, exact contrast checks, and any focused automated check after edits. Detector output remains advisory even when a fix was requested.

## Completion

Return a verdict—ready, ready after named decisions, or needs iteration—plus counts by classification, evidence for each unresolved item, authorized fixes applied, and explicit unverified states. A clean source scan without rendered interaction is not a completed UI review.

## When not to use

- Generic code review, security review, backend/API review, or architecture critique
- Creating a new screen, flow, or visual direction; use `ui-design`
- Extracting tokens or component contracts; use `design-system`
- Logic-only UI changes that preserve the rendered interface
- Accessing a Claude Design project or preview; use `claude-design` for retrieval, then return here for the review
