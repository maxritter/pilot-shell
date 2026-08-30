# Token Extraction

Use this procedure to extract or normalize the atomic values that shape a product UI.

## Source precedence

Establish which sources control the result:

1. Published design tokens or theme primitives consumed by production
2. Shared component-library values
3. Repeated production usage
4. Brand documents and approved screenshots
5. Isolated page literals

Record disagreements between higher- and lower-precedence sources. A mismatch may be migration debt, not permission to choose the prettier value.

## Inventory

Capture only categories present in the sources:

- Brand, semantic, neutral, surface, border, and content colors across supported themes
- Font families and fallbacks, loaded weights, type sizes, line heights, and letter spacing
- Spacing, sizing, layout, and container scales
- Radii, borders, shadows, and elevation
- Motion durations, easings, reduced-motion behavior, and transitions
- Breakpoints, container queries, z-index, opacity, and other named primitives

For every item, record its source name, exact value, source location, observed usage, and theme or platform scope.

## Normalize without erasing evidence

- Keep exact values from authoritative sources.
- Group aliases only when the source already treats them as equivalent or the user approves consolidation.
- Flag near-duplicate colors, off-scale spacing, unused tokens, missing theme pairs, and overloaded semantic names.
- Distinguish raw primitives from semantic tokens and component-level tokens.
- Do not generate a generic ten-step palette, type scale, or spacing scale when the product does not define one.

## Output

Match the repository:

- CSS custom properties for a CSS-token system
- Typed exports for a TypeScript theme
- JSON for a platform-neutral token pipeline
- Tailwind theme extensions when Tailwind is already authoritative
- Platform-native resources for an established native UI system

Include a short provenance header and a findings note naming sources, gaps, inconsistencies, and explicit decisions. When editing production tokens, update consumers through the repository's normal migration path and verify both supported themes.

## Completion

Every output value maps to a source or approved decision, theme relationships are explicit, duplicates remain reviewable, and the repository's native validation plus a representative render passes.
