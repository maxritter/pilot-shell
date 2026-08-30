# Visual Quality Review

Review the interface against its product intent and established system before applying generic aesthetic heuristics.

## Brand and context fidelity

- Compare colors, type, density, spacing, radii, shadows, iconography, imagery, motion, and copy voice with authoritative product sources.
- Flag invented values and one-off patterns that do not trace to tokens or approved variants.
- Keep an established choice even when it is a commonly overused pattern; consistency is better than an unrequested rebrand.
- When no system exists, judge against the documented direction from the UI design work rather than an imagined universal style.

## Content discipline

Every visible element answers a real user question, advances the task, or supplies necessary structure. Flag:

- Placeholder content presented as fact
- Repeated headings/body copy that say the same thing
- Unconnected actions and “learn more” destinations
- Decorative sections, statistics, testimonials, or features with no source
- Empty layouts filled with content instead of improved composition

## Hierarchy

For each major state, identify what a user should notice first, second, and third. Evaluate the combined signals of size, weight, color, position, density, and whitespace.

Flag flat hierarchy, reversed emphasis, competing primary actions in a single-path flow, de-emphasized critical feedback, and important content buried behind decorative elements. Dashboards and workspaces may intentionally have several peer actions.

## Rhythm and system consistency

- Infer the actual spacing and type scales from tokens or repeated usage, then flag accidental outliers.
- Check repeated components for consistent anatomy, alignment, padding, state treatment, and theme behavior.
- Distinguish deliberate variation from almost-identical drift.
- Check palette roles and surface relationships rather than enforcing an arbitrary color count.
- Look for overflow and awkward wrapping with real long content, not only ideal demo strings.

## Generic-template review

Question patterns that appear without product or semantic justification:

- Gratuitous gradients, glass surfaces, emoji decoration, or ornamental SVG scenes
- Repeated icon-heading-paragraph card grids where another structure communicates better
- Decorative colored side borders, gradient text, or numbered section scaffolding
- A default-model house style unrelated to audience or product
- Arbitrary font swaps, color literals, spacing, or motion
- Variations that differ only cosmetically

These are quality prompts, not automatic failures. A quotation border, status accent, established font, brand gradient, or repeated product component may be correct. State why the pattern harms this product before recommending replacement.

## Evidence

Each quality finding names the violated product goal or system rule, points to the rendered state and source token/component, and describes the user-visible impact. “Looks generic” without a concrete pattern and correction is not a finding.
