# Prototype

Use this procedure for a clickable prototype, interaction demo, or new multi-state flow.

## Map the flow

Before building, list the entry state, screens or major states, primary transitions, success state, recoverable errors, and any deliberately simulated boundary. Keep this map in a concise source comment or nearby project documentation when it helps maintainers.

## Use the real medium

- Build in the project-native framework and component library.
- Use the target platform's actual window, viewport, navigation, and input conventions.
- Prefer real application routes and state when safe; isolate the prototype when the user wants disposable exploration.
- Use realistic supplied content. Clearly label mocked services, timeouts, uploads, or persistence.

## Interaction coverage

Wire the paths the prototype claims to demonstrate:

- Forward and back navigation with state behavior defined
- Form labels, validation, loading, success, and recoverable failure
- Selection, filtering, disclosure, modal, menu, and keyboard behavior where present
- Visible focus, current state, disabled reasons, and double-submit protection
- Reduced-motion behavior for non-essential animation

Persistence is a product decision, not a prototype default. Never persist passwords, authentication secrets, payment data, email/contact identifiers, verification inputs, or other sensitive data. Persist only non-sensitive navigation or demo state when reload continuity is part of the requested experience, and document the storage.

## Verification

Drive the prototype rather than inspecting source alone. Exercise the happy path and one representative failure, re-snapshot after each transition, use keyboard operation where relevant, and inspect the supported viewport/theme matrix. Report which services or outcomes remain simulated.

## Completion

The prototype is complete when every claimed transition can be exercised, feedback is visible, sensitive data is not retained, simulated behavior is disclosed, and runtime evidence covers both success and recovery.
