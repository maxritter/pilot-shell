---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.html"
  - "**/*.vue"
  - "**/*.svelte"
  - "**/*.css"
  - "**/*.scss"
  - "**/*.sass"
  - "**/*.less"
  - "**/*.module.css"
---

# Frontend Standards

## Components

**Small, focused components with single responsibility. Compose complex UIs from simple pieces.**

- **Single responsibility:** If you need "and" to describe it, split it
- **Minimal props:** Under 5-7. More = component doing too much. Always typed with defaults.
- **State:** Keep local — only lift when multiple components need it. Prop drilling 3+ levels → use composition or context.
- **Naming:** Components: PascalCase nouns. Props: camelCase, booleans `is*`/`has*`. Events: `on*` for props, `handle*` internal.
- **Split when:** >200-300 lines, multiple responsibilities, reusable elsewhere, testing becomes difficult.

## CSS

**Follow project methodology consistently. Identify first: Utility-first (Tailwind), CSS Modules, BEM, or CSS-in-JS. Never mix.**

- Use design tokens (`var(--color-primary)`) over hardcoded values
- Work with the framework — if you need `!important`, reconsider your approach
- Custom CSS only for: complex animations, unique effects, third-party integration, browser fixes

## Accessibility

- **Semantic HTML first:** `<button>` for actions, `<a>` for navigation, landmarks (`<nav>`/`<main>`/`<header>`)
- **Keyboard:** Tab navigates, Enter/Space activates, Escape closes. Visible focus indicators always.
- **Labels:** Every input needs a label. `aria-label` for icon-only buttons.
- **Images:** Informative: descriptive alt text. Decorative: `alt=""`
- **Color:** 4.5:1 contrast (normal text), 3:1 (large). Never convey info by color alone.
- **ARIA:** Semantic HTML first, ARIA second. `aria-live="polite"` for dynamic content.
- **Headings:** One `<h1>` per page. Don't skip levels.

## Responsive Design

**Mobile-first with `min-width` media queries.** Use project's standard breakpoints — never arbitrary values.

- **Fluid layouts:** `width: 100%` + `max-width`, grid with `1fr`/`minmax()`/`auto-fit`
- **Units:** `rem` for spacing/layout, `em` for component-relative, `px` only for borders/shadows, `ch` for text widths
- **Touch targets:** Min 44x44px (iOS) / 48x48px (Android)
- **Typography:** Body 16px min, line-height 1.5. Fluid: `clamp(2rem, 5vw, 3rem)`
- **Images:** Use `srcset` and `sizes`

## Design Direction

**Commit to a clear aesthetic. Every visual choice must be intentional.**

1. **Purpose** — What does this communicate? 2. **Audience** — Developers? Consumers? 3. **Tone** — Minimalist, editorial, playful, etc. 4. **Differentiator** — One memorable element.

- **Typography:** Display font for personality, body font for readability. Max 2 fonts. Avoid defaults (Inter, Roboto, Arial).
- **Color:** Clear hierarchy: Primary (CTAs) → Accent → Neutral → Semantic. Dark mode: design separately, not just invert.
- **Spacing:** Generous whitespace. Cramped = low quality.
- **Motion:** Every animation has purpose. Max 500ms. Always respect `prefers-reduced-motion`.
- **Avoid AI aesthetic:** Purple gradients on white, symmetric 3-column grids, rounded cards with shadow, gradient text everywhere.

## Checklist

- [ ] Components: single responsibility, typed props, local state
- [ ] CSS: project methodology, design tokens, no `!important`
- [ ] Accessible: keyboard, labels, contrast 4.5:1, alt text
- [ ] Responsive: mobile-first, fluid, touch targets ≥ 44px
- [ ] Design: intentional direction, no AI anti-patterns
