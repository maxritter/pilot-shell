---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.html"
  - "**/*.vue"
  - "**/*.svelte"
---

# Accessibility Standards

**Core Rule:** Build accessible interfaces that work for all users, including those using assistive technologies.

## Semantic HTML First

Use native HTML elements that convey meaning to assistive technologies.

```html
<!-- Navigation -->
<nav><a href="/about">About</a></nav>

<!-- Buttons that perform actions -->
<button onClick="{handleSubmit}">Submit</button>

<!-- Links that navigate -->
<a href="/profile">View Profile</a>

<!-- Main content area -->
<main><article>...</article></main>

<!-- Form structure -->
<form>
  <label for="email">Email</label>
  <input id="email" type="email" />
</form>
```

**When to use each element:**

- `<button>`: Actions (submit, open modal, toggle)
- `<a>`: Navigation to different pages/sections
- `<nav>`: Navigation landmarks
- `<main>`: Primary page content
- `<header>`, `<footer>`, `<aside>`: Page structure

## Keyboard Navigation

All interactive elements must be keyboard accessible.

**Requirements:**
- Tab key moves focus through interactive elements
- Enter/Space activates buttons and links
- Escape closes modals and dialogs
- Arrow keys navigate menus and lists (when appropriate)
- Focus indicators are clearly visible

**Never:**
- Remove focus outlines without providing alternative indicators
- Use `tabIndex` values other than 0 or -1
- Create keyboard traps (user can't escape with keyboard)

## Form Labels and Inputs

Every form input must have an associated label.

```html
<!-- Explicit label association -->
<label for="username">Username</label>
<input id="username" type="text" />

<!-- aria-label for icon-only buttons -->
<button aria-label="Close dialog">
  <CloseIcon />
</button>

<!-- aria-describedby for help text -->
<label for="password">Password</label>
<input id="password" type="password" aria-describedby="password-help" />
<span id="password-help">Must be at least 8 characters</span>
```

## Alternative Text for Images

```jsx
<!-- Informative images -->
<img src="chart.png" alt="Sales increased 40% in Q4 2024" />

<!-- Decorative images -->
<img src="decoration.png" alt="" />

<!-- Complex images need longer descriptions -->
<img src="architecture.png" alt="System architecture diagram" aria-describedby="arch-description" />
```

**Alt text rules:**
- Describe the content and function, not "image of"
- Keep concise (under 150 characters when possible)
- Use empty alt (`alt=""`) for purely decorative images

## Color Contrast

**WCAG Requirements:**
- Normal text (< 18pt): 4.5:1 contrast ratio
- Large text (>= 18pt or >= 14pt bold): 3:1 contrast ratio
- UI components and graphics: 3:1 contrast ratio

**Don't rely on color alone:**
```jsx
// BAD - color only
<span style={{color: 'red'}}>Error</span>

// GOOD - color + icon + text
<span style={{color: 'red'}}>
  <ErrorIcon aria-hidden="true" />
  Error: Invalid email format
</span>
```

## ARIA Attributes

Use ARIA to enhance semantics when HTML alone isn't sufficient.

```jsx
// Roles for custom components
<div role="dialog" aria-modal="true">...</div>

// States and properties
<button aria-expanded={isOpen} aria-controls="menu">Menu</button>
<ul id="menu" hidden={!isOpen}>...</ul>

// Live regions for dynamic content
<div aria-live="polite" aria-atomic="true">{statusMessage}</div>

// Hide decorative elements
<span aria-hidden="true">→</span>
```

**ARIA rules:**
1. Use semantic HTML first, ARIA second
2. Don't override native semantics (`<button role="link">` is wrong)
3. All interactive ARIA roles need keyboard support

## Heading Hierarchy

Use heading levels (h1-h6) in logical order to create document structure.

**Rules:**
- One `<h1>` per page (page title)
- Don't skip levels (h2 → h4 is wrong)
- Don't choose headings based on visual size (use CSS for styling)

## Verification Checklist

Before marking UI work complete:

- [ ] All interactive elements are keyboard accessible
- [ ] Focus indicators are visible on all focusable elements
- [ ] All images have appropriate alt text
- [ ] All form inputs have associated labels
- [ ] Color contrast meets WCAG standards (4.5:1 for text)
- [ ] Heading hierarchy is logical (no skipped levels)
- [ ] ARIA attributes are used correctly (if needed)
- [ ] No information conveyed by color alone
- [ ] Tested with keyboard navigation (Tab, Enter, Escape)
