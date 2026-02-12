---
paths:
  - "**/*.css"
  - "**/*.scss"
  - "**/*.sass"
  - "**/*.less"
  - "**/*.module.css"
---

# CSS Standards

**Rule:** Follow project CSS methodology consistently, leverage framework patterns, maintain design system tokens.

## Identify Project Methodology First

Before writing any styles, check existing codebase for:

**Utility-first (Tailwind/UnoCSS):**
```jsx
<div className="flex items-center gap-4 p-6 bg-white rounded-lg shadow-md">
```

**CSS Modules:**
```jsx
import styles from './Component.module.css'
<div className={styles.container}>
```

**BEM (Block Element Modifier):**
```css
.card { }
.card__header { }
.card__header--highlighted { }
```

**CSS-in-JS (styled-components/emotion):**
```jsx
const Button = styled.button`
  padding: 1rem;
  background: ${props => props.theme.primary};
`
```

**Once identified, use that methodology exclusively. Never mix methodologies.**

## Design System Tokens

**Always use design tokens instead of hardcoded values:**

Bad:
```css
color: #3b82f6;
padding: 16px;
font-size: 14px;
```

Good (CSS variables):
```css
color: var(--color-primary);
padding: var(--spacing-4);
font-size: var(--text-sm);
```

**Check for existing tokens before creating new ones.**

## Framework Patterns Over Overrides

**Work with framework, not against it:**

Bad (fighting Tailwind):
```jsx
<div className="flex items-center" style={{gap: '17px', padding: '13px'}}>
```

Good (using framework values):
```jsx
<div className="flex items-center gap-4 p-3">
```

**If you need `!important` or deep style overrides, reconsider your approach.**

## Minimize Custom CSS

**Only write custom CSS for:**
- Complex animations
- Unique visual effects not in framework
- Third-party library integration
- Browser-specific fixes

## Organization Patterns

**Structure CSS logically:** Layout → Box model → Typography → Visual → Misc

**Group related styles, separate concerns with comments.**

## Performance Optimization

**Avoid:**
- Importing entire CSS frameworks when using few components
- Duplicate style definitions across files
- Overly specific selectors (`.a .b .c .d .e`)
- Large inline styles that could be extracted

## Verification Checklist

Before completing CSS work:

- [ ] Identified and followed project CSS methodology
- [ ] Used design tokens instead of hardcoded values
- [ ] Leveraged framework utilities where possible
- [ ] Avoided `!important` and deep overrides
- [ ] Followed project naming conventions
- [ ] Verified no unused styles in production build

## Quick Reference

| Situation                      | Action                                |
| ------------------------------ | ------------------------------------- |
| New component styling          | Check existing patterns first         |
| Need specific color            | Use design token, not hex code        |
| Framework doesn't have utility | Write minimal custom CSS              |
| Styles not applying            | Check specificity, avoid `!important` |
| Large CSS file                 | Extract to utilities or components    |
| Production bundle large        | Enable CSS purging/tree-shaking       |
