---
sidebar_position: 5
title: /fix
description: Bugfix workflow — investigate, RED test, fix, audit, done.
---

# /fix

Bugfix workflow with RED-before-GREEN discipline. Investigates the bug, writes a failing test, fixes at the root cause, audits, finishes. No plan file, no approval mid-flow, no separate verify phase.

Use `/fix` for bugs. Use [`/spec`](/docs/workflows/spec) for features and architectural changes — including bugfixes that warrant a full plan with approval and code review.

```bash
$ pilot
> /fix "annotation persistence drops fields between save and reload"
> /fix "off-by-one in pagination at boundary"
> /fix "wrong default for max_retries"
```

`/fix` is **always quick**. If investigation reveals the bug is multi-component, architectural, or otherwise larger than a quick fix, `/fix` stops cleanly and tells you to re-invoke with `/spec`. It does not silently switch lanes — `/fix` means quick, `/spec` means the full workflow.

## Workflow

```
Investigate  →  RED  →  Fix  →  Audit  →  Quality Gate  →  Done
```

### Investigate

Trace the bug to `file:lineN — function() does X but should do Y` with **High** or **Medium** confidence.

- Reproduce the bug. Restate symptom, trigger, expected behaviour.
- Skim recent changes (`git log --oneline -10`).
- Start with `codegraph_context(task=…)` for orientation. For local bugs, one or two targeted reads is enough — no full call-graph traversal.
- For UI / async / race / timing bugs that don't surface from a static read: add temporary `SPEC-DEBUG:`-marked logs at component boundaries, trigger the bug, read the output, then proceed. Step 4 audit greps the marker — leftover diagnostics fail the audit.
- State the root cause out loud before writing any test. If confidence stays Low: bail out.

### RED — Write the Reproducing Test

Encode `Currently → Expected` via an existing public entry point. Run it; it must **fail** with an error matching the symptom.

A test that passes against buggy code doesn't encode the bug — re-investigate. A test that errors for unrelated reasons (import error, missing fixture) is not a valid signal.

### Fix at the Root Cause

Make the **minimal** change at the root cause. One change, one variable, one logical fix. No "while I'm here" cleanups. No bundled refactoring.

Forbidden: broad new `try/except`, `if value is None: return default` at the caller when the bug is upstream, swallowed exceptions, silently normalised bad inputs.

Re-run the reproducing test → must **pass**. Then run the test module(s) covering the fix file (fast, scoped). The full anti-regression suite runs once at the Quality Gate, not after every fix iteration.

### Audit

Single pass — replaces the eight-substep audit of the full lane:

- **Scope sanity** — root-cause file IS in the diff, no unplanned files appear, diff is small.
- **Symptom-patching grep** — `git diff | grep` for new `try/except`, swallowed returns, leftover `print`/`console.log` and `SPEC-DEBUG:` markers. Justify each match or revert.
- **End-to-end verification — MANDATORY** — re-run the user's actual repro and capture concrete evidence. **A passing unit test does NOT prove the bug is fixed.** Skip is not an option, no exceptions.
  - **UI bugs:** browser automation against the running app. 4-tier resolution: **Claude Code Chrome** → **Chrome DevTools MCP** → **playwright-cli** → **agent-browser**. Walk the user's repro steps, read the page, confirm correct behaviour.
  - **CLI:** run the exact command the user ran, capture output + exit code.
  - **API:** `curl` / HTTP client, capture status + the field that proves the fix.
  - **Library / SDK:** `python -c '…'`, `node -e '…'`, or scratch script with the user's args, capture the returned value.
  - **Background job:** trigger manually, read logs.

Bare assertions ("looks fixed", "behaves correctly") are insufficient — the finalise step requires evidence in the report. If the symptom persists, the unit test is at the wrong layer: move the assertion up to the user's actual entry point and re-run RED → fix → audit.

### Quality Gate

Lint + types + build (when applicable), then the full test suite. If a far-from-the-fix test breaks, the bug has unintended cross-coupling — bail out.

### Finalise

- Worktree mode: bundle test + fix into one commit (`fix: <one-line>`).
- Approval gate fires only if **Plan Approval** is enabled in Console Settings.
- The completion report includes a mandatory **E2E** line documenting what was actually run and observed — not just "tests pass". Without it, the workflow is incomplete.
- Console notification + report.

## When to bail out — use `/spec` instead

`/fix` stops and tells you to re-invoke with `/spec` when:

- Bug spans 3+ files or 2+ components.
- Root cause is architectural, not a single line.
- Fix needs defense-in-depth at multiple layers.
- Confidence stays Low — root cause can't be pinned to file:line.
- Two quick-lane fix attempts have already failed.
- Fix has non-trivial UI implications that warrant a recorded Verification Scenario.

The full lane (`/spec`) adds: Behavior Contract, three-task structure, plan file with approval gate, Console annotation cycle, `cp`+`trap` revert-test proof in verify, iteration cap at 3.

## Common issues

| Symptom | What it means | What to do |
| ------- | ------------- | ---------- |
| Can't reproduce | Description is too vague or environment-dependent | Ask for exact steps, env, stack trace. Do not write a speculative fix. |
| Test passes without the fix | Test doesn't encode the bug | Tighten the assertion or pick a more specific input. |
| Fix breaks far-away tests | Cross-coupling beyond the quick lane | Bail out. Re-invoke with `/spec`. |
| Reproducing test green but user still hits the bug | Test sits below the user's layer | Move the assertion to the user's actual entry point (API, browser, CLI). |
| Three failed fix attempts | Architectural problem, not a fix problem | Bail out. The pattern needs reconsidering, not another patch. |

## Configurable Toggles

`/fix` honours the same Console Settings as `/spec`:

| Toggle | Default | Effect when disabled |
| ------ | ------- | -------------------- |
| **Ask Questions** | On | Investigation skips clarifying questions and uses defaults. |
| **Plan Approval** | On | The end-of-flow approval gate is skipped — fix is finalised immediately. |

When both are off, `/fix` runs end-to-end with no user interaction. Worktree isolation is not honoured — use `/spec` if you want a worktree.

## When to use `/spec` vs `/fix`

| Use `/fix` | Use `/spec` |
| ---------- | ----------- |
| Something is broken | Building new functionality |
| Bug fits in 1–2 files | Architecture decisions matter |
| Root cause is locatable to a line/function | Multiple sub-systems involved |
| Fix is small and contained | Work warrants a written plan + approval |
