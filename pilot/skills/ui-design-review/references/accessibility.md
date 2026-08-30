# Accessibility Review

Use WCAG 2.2 as the default web conformance baseline when the product does not specify another applicable standard. Keep normative requirements separate from design recommendations.

Primary references:

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Target Size Minimum, Level AA: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- Target Size Enhanced, Level AAA: https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html

## Contrast and color

- Normal text and images of text need at least 4.5:1 contrast under WCAG 2.2 SC 1.4.3.
- Large-scale text needs at least 3:1. The WCAG definition uses at least 18 point regular or 14 point bold, evaluated from the user agent and font metrics.
- Meaningful non-text UI components, boundaries, focus indicators, and states need 3:1 where SC 1.4.11 applies.
- Resolve actual foreground/background pairs on every surface and supported theme. Compute ratios; do not eyeball.
- Information and state need a non-color cue. Brand logotypes and inactive controls have specific contrast exceptions; do not misreport them.
- Pure white/black, muted gray, or a particular palette is a design preference unless it causes a measurable failure.

## Structure and names

- Use semantic elements and landmarks appropriate to the role; add ARIA only where native semantics cannot express the behavior.
- Controls need accessible names, inputs need programmatic labels, errors need field association, and meaningful images need purpose-specific alternatives.
- Heading levels describe document structure rather than visual size. A clear primary heading is good practice; “exactly one h1” is not itself a WCAG success criterion.
- Dynamic status and error messages are exposed without unexpectedly moving focus.

## Keyboard and focus

- Every interactive function is reachable and operable from the keyboard with a logical order.
- Focus remains visible and is not obscured by sticky content or overlays.
- Custom widgets follow their expected keyboard pattern. Dialogs manage entry, containment where appropriate, Escape behavior, and focus restoration.
- Avoid positive tabindex values and mouse-only or hover-only functionality.

## Forms, motion, and reflow

- Instructions and errors are specific, programmatically associated, and not conveyed by color alone.
- Input purpose, type, and autocomplete are correct where the field represents a known purpose.
- Content reflows and remains usable under supported zoom/text scaling without clipping, overlap, or two-dimensional scrolling except where essential.
- Non-essential motion respects reduced-motion preferences. Flashing content stays within applicable thresholds and user-controlled animation can be paused where required.

## Pointer targets

WCAG 2.2 SC 2.5.8 Level AA uses a target size of 24 by 24 CSS pixels with defined spacing, inline, equivalent-control, user-agent, and essential exceptions. WCAG SC 2.5.5 Level AAA uses 44 by 44 CSS pixels with its exceptions. Report the actual conformance level; do not call 44 by 44 the AA minimum.

Product and platform guidelines may set larger targets, such as touch-first 44 or 48 CSS-pixel conventions. Treat those as product/platform requirements when adopted, not as a mislabeled WCAG AA rule.

## Evidence

For each failure, record the criterion or product requirement, measured state, expected threshold/behavior, and user impact. Automated accessibility tooling nominates issues; keyboard use, focus behavior, dynamic state, and product semantics still require direct verification.
