# Component Extraction

Use this procedure to turn repeated product patterns into a reusable component inventory or library contract.

## Walk the real surfaces

Inspect the requested page, flow, or application breadth. A component candidate exists when a pattern repeats, plausibly recurs, has variants, owns interaction states, or provides a stable semantic role.

Organize candidates by the project's own taxonomy when it has one. Otherwise use:

- Foundations and primitives
- Controls and inputs
- Composed patterns such as form fields, cards, alerts, menus, and dialogs
- Navigation and page structures
- Templates only when multiple screens share the structure

## Component contract

For each component record:

- Name and user-facing purpose
- Anatomy and composition
- Variants and sizes that actually exist
- Default, hover where applicable, active/selected, focus, disabled, loading, empty, success, and error states that the component can enter
- Tokens and assets it consumes
- Responsive and theme behavior
- Keyboard, semantic, labeling, and contrast requirements
- Usage guidance and a concrete misuse to avoid
- Source locations and known consumers

Keep public APIs small and semantic. Do not expose visual implementation details as props when composition or a named variant expresses the intent.

## Find system gaps

Report:

- Near-duplicate components that should converge
- Missing states or variants needed by existing product behavior
- One-off values that should become tokens
- Accessibility differences between otherwise similar patterns
- Components whose responsibilities are too broad to reuse safely
- Patterns that look similar but serve different semantics and should remain separate

## Output

When the user requests an inventory, write a maintainable document with source links and decisions. When the user requests implementation, follow the repository's component structure, story/example convention, and test strategy; migrate a representative consumer before broad replacement.

## Completion

Each component traces to real product evidence, variants and states are explicit, gaps are separated from observed behavior, and implemented contracts render correctly in representative consumers and themes.
