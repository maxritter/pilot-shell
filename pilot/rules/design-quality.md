---
paths:
  - "**/*.{tsx,jsx,html,vue,svelte,astro,razor}"
  - "**/*.{css,scss,sass,less}"
  - "**/*.module.css"
  - "**/*.razor.css"
---

# UI Design Quality

Apply this rule when the request changes user-visible layout, styling, content hierarchy, theming, or interaction affordances. For a non-visual logic change in a matching file, preserve the current UI and do not broaden the task into a redesign.

## Start from the product

**Preserve the current visual language unless the user asks to change it.** Read the relevant components, tokens, theme, screenshots, brand guidance, and neighboring screens before making visual decisions. Exact project values outrank generic design advice.

- Keep the project’s component library, CSS methodology, icon set, typefaces, spacing scale, radii, shadows, and motion language.
- Reuse real product content and assets. Do not invent testimonials, statistics, features, destinations, or decorative copy to fill space.
- Treat an absent design system as a decision point, not permission to fall back to a generic template. Establish a small coherent direction tied to audience, purpose, and tone.

## Make the hierarchy legible

- A first-time user can identify the page purpose, primary information, and next action without hunting.
- Use size, weight, color, position, and density deliberately. Do not make every element equally loud or equally muted.
- Give each screen a clear primary action when the product flow has one. Dashboards and multi-tool workspaces may legitimately support several peer actions.
- Remove filler and duplicate explanation. Empty space is resolved through composition, not invented content.
- Use the project’s type, color, and spacing scales. New values become tokens or documented variants rather than isolated literals.

## Build a system, not a screenshot

- Prefer reusable components and variants over one-off page markup.
- Cover the states the interaction can actually enter: default, hover when applicable, active/selected, focus, disabled, loading, empty, success, and error.
- Keep current state and action feedback visible. Disabled controls explain unmet prerequisites when the reason is not otherwise clear.
- Motion communicates change or spatial relationship, remains brief, and respects `prefers-reduced-motion`.
- Responsive behavior is designed at content-driven widths, including long copy and narrow containers. Dark and light themes are checked independently when both exist.

## Avoid unearned template language

These are review prompts, not blanket bans. Keep a pattern when it comes from the product’s established system or has a clear semantic purpose.

- Gratuitous gradients, glass surfaces, emoji decoration, and ornamental SVG scenes
- Repeated icon-heading-paragraph card grids when a list, table, comparison, or prose structure communicates better
- Colored side borders used as decoration rather than callout, quote, status, or selection semantics
- Default-model house styles chosen without reference to the brief or product
- Arbitrary fonts, colors, spacing, and animation values that do not trace to a system
- Multiple variations that differ only cosmetically rather than in hierarchy, layout, interaction, density, or tone

## Completion check

- Existing design context was inspected and preserved or intentionally changed.
- Content is real, necessary, and concise.
- Hierarchy, component reuse, interaction states, responsive behavior, and supported themes are coherent.
- Accessibility and actual interaction are verified under `browser-automation.md` or the project’s named UI driver.
- Advisory detector findings were judged against product context rather than applied mechanically.
