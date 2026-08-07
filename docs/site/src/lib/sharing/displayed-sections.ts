/**
 * Canonical render order + visibility allowlist for plan-spec sections.
 *
 * Single source of truth shared between the Console (`console/src/`) and the
 * pilot-shell.com SPA (`docs/site/src/`). The two files MUST stay byte-identical;
 * the website cannot import from `console/src/` so the docs/site mirror lives
 * at `docs/site/src/lib/sharing/displayed-sections.ts` and copies this file's
 * contents verbatim.
 *
 * Both renderers filter section H2 headings to this allowlist AND sort them by
 * the array index. Section headings not in the list (Progress Tracking,
 * File Structure, anything unknown) are hidden silently. Implementation Tasks
 * and the bugfix Tasks heading are NOT in this list — each surface renders
 * them as a special "always-last" section.
 *
 * "Acceptance Criteria" (a Buildout's pass/fail list, judged at the end of each
 * round) is allowlisted and rendered as an ordinary section on both surfaces.
 * Unlike a spec's task list it is NOT duplicated by the Console's header card,
 * which counts `- [ ] Task N:` progress lines — a Buildout's criteria are a
 * separate list from its tasks. "Criteria" is the pre-redesign heading and
 * stays allowlisted so `Build Rubric` files written before the rename keep
 * rendering.
 */

export const DISPLAYED_SECTIONS_ORDERED: readonly string[] = [
  "Summary",
  "Acceptance Criteria",
  "Criteria",
  "Out of Scope",
  "Investigation",
  "Behavior Contract",
  "Approach",
  "Fix Approach",
  "Scope",
  "Autonomous Decisions",
  "Context for Implementer",
  "Runtime Environment",
  "Feature Inventory",
  "Assumptions",
  "Risks and Mitigations",
  "Goal Verification",
  "E2E Test Scenarios",
  "E2E Results",
  "Verification Scenario",
  "Verification Scenarios",
  "Open Questions",
  "Deferred Ideas",
  "Round Log",
] as const;

export const IMPLEMENTATION_TASKS_HEADING = "Implementation Tasks";
export const TASKS_HEADING_BUGFIX = "Tasks";
