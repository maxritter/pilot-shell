---
paths:
  - "**/*.css"
  - "**/*.scss"
  - "**/*.sass"
  - "**/*.less"
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.html"
  - "**/*.vue"
  - "**/*.svelte"
---

# Design Standards

**Rule:** Commit to a clear aesthetic direction and execute it with precision. Every visual choice must be intentional, not default.

## Design Direction Before Code

Before writing any styles, establish a clear aesthetic direction.

**Ask these questions:**
1. **Purpose** - What does this interface communicate? Professional trust? Creative energy? Technical precision?
2. **Audience** - Who uses this? Developers? Consumers? Enterprise buyers?
3. **Tone** - Pick a specific direction: minimalist, editorial, brutalist, playful, luxurious, industrial, organic, retro-futuristic, geometric, soft
4. **Differentiator** - What single visual element will make this memorable?

**Then commit.** A bold minimalist design and a rich maximalist design are both good. A directionless design that hedges is always bad.

## Typography

### Font Selection

Choose fonts that match the aesthetic direction and have character.

**Bad - Generic defaults:**
```css
font-family: Arial, sans-serif;
font-family: 'Inter', sans-serif;
font-family: 'Roboto', sans-serif;
font-family: system-ui, sans-serif;
```

**Good - Intentional choices:**
```css
/* Editorial / Magazine */
font-family: 'Playfair Display', serif;      /* Display */
font-family: 'Source Serif 4', serif;         /* Body */

/* Technical / Developer */
font-family: 'JetBrains Mono', monospace;     /* Display */
font-family: 'IBM Plex Sans', sans-serif;     /* Body */

/* Modern / Clean */
font-family: 'Outfit', sans-serif;            /* Display */
font-family: 'DM Sans', sans-serif;           /* Body */

/* Bold / Statement */
font-family: 'Cabinet Grotesk', sans-serif;   /* Display */
font-family: 'General Sans', sans-serif;      /* Body */
```

### Font Pairing

Pair a distinctive display font with a readable body font. Contrast in style, unite in tone.

**Principles:**
- Display fonts carry personality (headings, hero text, callouts)
- Body fonts prioritize readability (paragraphs, UI labels, form text)
- Limit to 2 fonts per project (3 maximum with a monospace)
- Use weight variation within a family before adding another font

### Font Anti-Patterns

Never default to these without a specific reason:
- Inter, Roboto, Arial, Helvetica (overused, signals no design thought)
- Space Grotesk (AI-generated UI cliche)
- Using the same font for display and body without weight contrast

## Color

### Palette Construction

Build a cohesive palette with clear hierarchy. Avoid distributing colors evenly.

**Structure:**
```
Primary   - Brand color, CTAs, key actions (1 color)
Accent    - Highlights, badges, secondary emphasis (1-2 colors)
Neutral   - Text, borders, backgrounds (gray scale)
Semantic  - Success, warning, error, info (functional only)
```

**Good - Clear hierarchy:**
```css
--primary: #0f172a;        /* Dominant: dark navy */
--accent: #f59e0b;         /* Sharp contrast: amber */
--text: #334155;           /* Readable body text */
--text-muted: #94a3b8;     /* Secondary text */
--surface: #f8fafc;        /* Background */
--border: #e2e8f0;         /* Subtle borders */
```

### Color Anti-Patterns

- Purple-to-blue gradients on white (the quintessential AI look)
- Rainbow or multi-color schemes without hierarchy
- Low-contrast text that fails WCAG AA (4.5:1 minimum)
- Using brand color for everything instead of as an accent

### Dark Mode

If implementing dark mode, design it separately. Don't just invert colors.

```css
/* Good: designed for dark */
--bg: #0f172a;           /* Deep navy, not pure black */
--surface: #1e293b;       /* Elevated surfaces slightly lighter */
--text: #e2e8f0;          /* Off-white, not pure white */
--text-muted: #64748b;    /* Muted but readable */
--border: #334155;        /* Subtle, not stark */
```

## Spacing and Composition

### Whitespace

Use generous whitespace to create focus. Cramped layouts signal low quality.

```css
.section { padding: 4rem 2rem; }       /* Generous section spacing */
.card { margin-bottom: 2rem; }         /* Room to breathe */

@media (min-width: 1024px) {
  .section { padding: 6rem 4rem; }     /* Even more space on desktop */
}
```

### Layout Composition

Not every layout needs to be a symmetric grid. Consider:
- **Asymmetric splits** (60/40, 70/30) for visual interest
- **Overlapping elements** for depth
- **Varied column widths** instead of equal divisions
- **Full-bleed sections** breaking the container for emphasis
- **Negative space** as a deliberate design element

## Motion and Interaction

### Purposeful Animation

Every animation should serve a purpose: guide attention, provide feedback, or create continuity.

```css
/* Staggered entrance reveals content hierarchy */
.card {
  opacity: 0;
  transform: translateY(1rem);
  animation: reveal 0.5s ease-out forwards;
}

.card:nth-child(1) { animation-delay: 0ms; }
.card:nth-child(2) { animation-delay: 100ms; }
.card:nth-child(3) { animation-delay: 200ms; }

@keyframes reveal {
  to { opacity: 1; transform: translateY(0); }
}
```

### Motion Anti-Patterns

- Animations longer than 500ms for UI elements (feels sluggish)
- Infinite animations on static content (distracting)
- Animating layout properties (width, height) instead of transform/opacity (poor performance)
- Motion without `prefers-reduced-motion` respect:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Visual Atmosphere

### Shadows and Elevation

Use shadows to create depth hierarchy, not just borders.

```css
/* Subtle elevation */
box-shadow:
  0 1px 2px rgba(0, 0, 0, 0.04),
  0 4px 8px rgba(0, 0, 0, 0.04);

/* Higher elevation (modals, dropdowns) */
box-shadow:
  0 4px 6px rgba(0, 0, 0, 0.04),
  0 12px 24px rgba(0, 0, 0, 0.08);
```

## AI Aesthetic Anti-Patterns

These patterns signal "AI-generated" and should be avoided:

| Anti-Pattern | Why It's Bad | Alternative |
|-------------|-------------|-------------|
| Purple gradient on white | Most common AI cliche | Choose palette matching purpose |
| Inter/Roboto/Space Grotesk | Default AI font choices | Select fonts matching tone |
| Symmetric 3-column grid | Predictable, no visual interest | Asymmetric or varied layouts |
| Rounded cards with light shadow | Every AI UI looks like this | Match card style to aesthetic |
| Blue CTA buttons | Safe but forgettable | Brand-aligned accent color |
| Gradient text on everything | Overused effect | Reserve for one focal element |

## Verification Checklist

Before completing design work:

- [ ] Established clear aesthetic direction before coding
- [ ] Typography uses intentional font choices (not defaults)
- [ ] Color palette has clear hierarchy (not evenly distributed)
- [ ] Spacing is generous with clear visual hierarchy
- [ ] Animations serve a purpose (feedback, attention, continuity)
- [ ] `prefers-reduced-motion` is respected
- [ ] Does not match common AI aesthetic anti-patterns
- [ ] Consistent tone across all elements
- [ ] Color contrast meets WCAG AA (4.5:1)
