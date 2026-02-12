---
paths:
  - "**/*.css"
  - "**/*.scss"
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.html"
  - "**/*.vue"
  - "**/*.svelte"
---

# Responsive Design Standards

**Rule:** Mobile-first development with consistent breakpoints, fluid layouts, relative units, and touch-friendly targets.

## Mobile-First Development - Mandatory

**Always start with mobile layout, then enhance for larger screens.**

```css
/* Mobile-first */
.container {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .container { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    grid-template-columns: repeat(4, 1fr);
  }
}
```

## Standard Breakpoints

**Use project breakpoints consistently:**

Tailwind: `sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`, `2xl: 1536px`

**Check existing codebase for breakpoint definitions before creating new ones. Never use arbitrary breakpoints like 850px.**

## Fluid Layouts

**Use flexible containers that adapt to screen size:**
- `width: 100%` + `max-width` instead of fixed widths
- Flexbox: `flex: 1`, `flex-grow`, `flex-shrink`
- Grid: `1fr`, `minmax()`, `auto-fit`, `auto-fill`
- Container queries (modern): `@container (min-width: 400px)`

## Relative Units Over Fixed Pixels

- `rem`: Font sizes, spacing, layout dimensions (scales with root font size)
- `em`: Component-relative sizing
- `%`: Widths, heights relative to parent
- `px`: Borders (1px), shadows, very small values
- `vw/vh`: Full viewport dimensions
- `ch`: Text-based widths (e.g., `max-width: 65ch`)

## Touch-Friendly Design

**Minimum touch target size: 44x44px (iOS) / 48x48px (Android)**

```css
.icon-button {
  width: 24px;
  height: 24px;
  padding: 12px; /* Total: 48x48px */
}
```

## Readable Typography

- Body text: 16px (1rem) minimum
- Small text: 14px (0.875rem) minimum
- Line height: 1.5 for body, 1.2 for headings
- Line length: 45-75 characters (`max-width: 65ch`)

Fluid typography with clamp:
```css
h1 { font-size: clamp(2rem, 5vw, 3rem); }
```

## Content Priority on Mobile

```jsx
<div className="flex flex-col lg:flex-row">
  <MainContent className="order-1" />
  <Sidebar className="order-2 hidden lg:block" />
</div>
```

## Image Optimization

```html
<img
  src="hero-800x600.jpg"
  srcset="hero-400x300.jpg 400w, hero-800x600.jpg 800w, hero-1600x1200.jpg 1600w"
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 800px"
  alt="Hero"
>
```

## Verification Checklist

Before completing responsive work:

- [ ] Started with mobile layout
- [ ] Used project's standard breakpoints
- [ ] Implemented fluid layouts (no fixed widths)
- [ ] Used relative units (rem/em) for sizing
- [ ] Touch targets minimum 44x44px
- [ ] Typography readable without zoom (16px+ body)
- [ ] No horizontal scrolling on mobile
- [ ] Tested at key breakpoints (375px, 768px, 1024px, 1440px)
