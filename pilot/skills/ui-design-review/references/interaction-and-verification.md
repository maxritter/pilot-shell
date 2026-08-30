# Interaction and Verification

Review the states users can actually enter and prove the interface through its real driver.

## Interactive inventory

Inventory buttons, links, inputs, toggles, tabs, menus, dialogs, disclosures, selectable rows/cards, filters, sorting, pagination, and custom widgets. For each applicable element check:

- Resting affordance and accessible name
- Hover when pointer interaction exists
- Pressed, active, selected, or current state
- Visible keyboard focus
- Disabled behavior and explanation when needed
- Loading and double-submit protection for asynchronous work
- Success, error, empty, and recovery feedback

Do not add decorative transforms or animation merely to satisfy a state checklist. The state must be visible, consistent with the product, and usable under reduced motion.

## Runtime matrix

Use the driver named by the repository. If none exists, follow `browser-automation.md` for browser pages or `mobile-development.md` for installed/mobile UI.

For every affected user path:

1. Capture the starting state.
2. Perform the primary interaction.
3. Capture and inspect the resulting state.
4. Exercise one relevant failure or recovery path.
5. Repeat at representative narrow and wide viewports.
6. Check each supported theme and the states materially changed by the request.
7. Verify keyboard operation, focus, console/runtime errors, and actual content overflow.

A source read, static server response, passing unit test, or screenshot without interaction is not runtime proof.

## Render gate and fresh eyes

Run a mechanical gate before judging design quality. A blank mount, console error, failed subresources, validator failure, or obviously stale render makes visual judgment meaningless; fix it and render again first. Do not switch verification paths when a gate fails—diagnose the same rendered surface.

After the gate is clean, perform a fresh-eyes pass against the user's request verbatim: first check whether the requested changes actually landed, then inspect layout, spacing, typography, hierarchy, and states. Use an independent reviewer when the current runtime and delegation policy make that appropriate; otherwise re-read the screenshot with the acceptance points written out. A reviewer is evidence, not authority—the active agent owns the verdict and re-verification.

The screenshot is the visual ground truth. DOM measurements and computed styles diagnose why clipping, overflow, or spacing is wrong; they do not overrule visible evidence. When repeated tweaks do not converge, measure the affected element and parent, state the root cause, and make one structural correction rather than accumulating cosmetic offsets.

## Deterministic detector

After runtime interaction and visual checks pass, run the bounded `impeccable detect` contract from `browser-automation.md` when the executable and a concrete UI target are available.

- Scan explicit changed UI files, narrow rendered output, or a saved live DOM—not the repository root.
- Parse JSON. Exit codes 0 and 2 both indicate a completed detector run.
- Treat findings as advisory candidates and judge them against the product system.
- A missing binary, unsupported target, timeout, invalid output, or third-party-only finding is recorded as a skip or out-of-scope note rather than a fabricated pass.

## Fix verification

After an authorized fix, repeat the exact failing interaction and state first, then the affected matrix. Re-check contrast numerically where color changed and inspect whether focus, wrapping, or theme fixes created a new regression.

## Completion

Verification is complete when the primary interaction and recovery path were driven, result states were re-captured, relevant viewport/theme/state coverage is recorded, and every skipped check or simulated boundary is explicit.
