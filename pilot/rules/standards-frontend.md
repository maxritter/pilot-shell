---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.html"
  - "**/*.vue"
  - "**/*.svelte"
  - "**/*.razor"
  - "**/*.css"
  - "**/*.scss"
  - "**/*.sass"
  - "**/*.less"
  - "**/*.module.css"
  - "**/*.razor.css"
---

# Frontend Standards

## Components

**Small, focused components with single responsibility. Compose complex UIs from simple pieces.**

- **Single responsibility:** If you need "and" to describe it, split it
- **Minimal props:** Under 5-7. More = component doing too much. Always typed with defaults.
- **State:** Keep local — only lift when multiple components need it. Prop drilling 3+ levels → use composition or context.
- **Naming:** Components: PascalCase nouns. Props: camelCase, booleans `is*`/`has*`. Events: `on*` for props, `handle*` internal.
- **Split when:** >600-800 lines (deliberately stricter than the global 800/1000 in `development-practices.md` — JSX/component files grow unwieldy faster), multiple responsibilities, reusable elsewhere, testing becomes difficult.

## CSS

**Follow project methodology consistently. Identify first: Utility-first (Tailwind), CSS Modules, BEM, CSS-in-JS, or CSS isolation. Never mix.**

- Use design tokens (`var(--color-primary)`) over hardcoded values
- Work with the framework — if you need `!important`, reconsider your approach
- Custom CSS only for: complex animations, unique effects, third-party integration, browser fixes

## Accessibility

- **Semantic HTML first:** `<button>` for actions, `<a>` for navigation, landmarks (`<nav>`/`<main>`/`<header>`)
- **Keyboard:** Tab navigates, Enter/Space activates, Escape closes. Visible focus indicators always.
- **Labels:** Every input needs a label. `aria-label` for icon-only buttons.
- **Images:** Informative: descriptive alt text. Decorative: `alt=""`
- **Color contrast — verify, never eyeball:** Body/label text needs 4.5:1 against its *actual* background; large text (at least 18 point regular or 14 point bold) needs 3:1; meaningful non-text UI boundaries and states need 3:1. Re-check tokens on every surface and supported theme. Button-label text is measured against the button fill. Never convey information by color alone. (`impeccable detect` flags many candidates; compute exact ratios.)
- **ARIA:** Semantic HTML first, ARIA second. `aria-live="polite"` for dynamic content.
- **Headings:** Use a coherent hierarchy and do not skip levels merely for visual sizing. Give the page a clear primary heading; multiple sectioning roots are not automatically an accessibility failure.

## Responsive Design

**Follow the project's breakpoint strategy.** For a new layout with no established approach, start from the narrowest supported viewport and add content-driven `min-width` breakpoints.

- **Fluid layouts:** `width: 100%` + `max-width`, grid with `1fr`/`minmax()`/`auto-fit`
- **Units:** Prefer `rem` for scalable spacing and type, `em` for component-relative values, `ch` for readable text widths, and `px` where fixed device-independent CSS pixels are intentional.
- **Pointer targets:** Meet WCAG 2.2 AA's 24×24 CSS-pixel minimum or its spacing exception. On touch-first product surfaces, follow the platform's larger target guidance (commonly 44×44 on iOS and 48×48 on Android).
- **Typography:** Body 16px min, line-height 1.5. Fluid: `clamp(2rem, 5vw, 3rem)`
- **Images:** Use `srcset` and `sizes`

## Performance

- **Cache expensive work:** Parsing, transforming, or filtering data in a render/update path must be memoized. If input hasn't changed, output must not be recomputed.
- **Isolate re-renders:** List items should not re-render when unrelated parent state changes. Use framework memoization primitives on list item components.
- **Minimize dependency weight:** Import only what you use. Full library imports where tree-shaken alternatives exist waste bandwidth and parse time.
- **Polling-safe:** If the view refreshes on an interval, child components must not redo expensive work when the underlying data hasn't changed.

## Checklist

- [ ] Components: single responsibility, typed props, local state
- [ ] CSS: project methodology, design tokens, no `!important`
- [ ] Accessible: keyboard, labels, alt text, and applicable WCAG contrast ratios verified on every surface and theme
- [ ] Responsive: follows project breakpoints, remains fluid, and meets pointer-target requirements
- [ ] Performance: expensive work cached, re-renders isolated, deps tree-shaken, polling-safe
- [ ] Design: user-visible changes also satisfy `design-quality.md`
