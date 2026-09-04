---
description: Plan-spec section order and visibility come from one generated contract
paths:
  - "pilot/spec/plan-format.json"
  - "scripts/gen_plan_format.py"
  - "console/src/shared/displayed-sections.ts"
  - "console/src/ui/viewer/views/Spec/**"
  - "docs/site/src/lib/sharing/displayed-sections.ts"
  - "docs/site/src/components/feedback/**"
---

# Shared Spec Section Rendering

`console/src/shared/displayed-sections.ts` and
`docs/site/src/lib/sharing/displayed-sections.ts` are **generated files**. Do not
edit them. Both are produced from `pilot/spec/plan-format.json`, which is the
single place the section order, the hidden sections and the task headings live.

They are generated rather than imported because both consumers are Vite-rooted
(`console/vite.config.ts`, `docs/site/vite.config.ts`) and neither can resolve a
JSON file outside its own project root.

## Required Pattern

When changing the canonical section order or the hidden-section list:

1. Edit `pilot/spec/plan-format.json`.
2. Regenerate both files:

```bash
python scripts/gen_plan_format.py
```

3. Confirm nothing is stale:

```bash
python scripts/gen_plan_format.py --check
```

`--check` exits non-zero and prints a diff when a target does not match the
contract. `launcher/tests/unit/test_spec_format.py::TestGeneratedTypeScriptParity`
runs the same check, so a stale or hand-edited copy fails the suite rather than
silently shipping.

That parity test lives in the **Python** suite deliberately: `docs/site`'s vitest
is not invoked by `release.yml` or `release-dev.yml`, so a check placed there would
never run in CI.

## Why

The Console and the public `pilot-shell.com/s/<id>` review surface must render the
same plan sections in the same order. If only one copy changed, reviewers and
local agents would discuss different visible specs. This used to be a
"keep them byte-identical" convention enforced by `cmp`; it is now a generated
artifact with a failing test behind it.

## Unrecognised sections render

A `##` heading absent from `DISPLAYED_SECTIONS_ORDERED` is **not** dropped. It
renders after the recognised sections, in document order, so a plan written by a
skill outside Pilot can invent its own sections. Only `SECTIONS_HIDDEN` stays
invisible, and the two task headings are rendered by a dedicated task-card
component instead of as ordinary sections.

## Related Tests

```bash
uv run pytest launcher/tests/unit/test_spec_format.py -q
cd console && bun test tests/ui/spec-section-rendering.test.ts
cd docs/site && npx vitest run src/components/feedback/sectioned-block-helpers.test.ts
```
