---
sidebar_position: 5
title: /fix
description: Bugfix workflow — investigate root cause, write a RED reproducing test, fix at the source, then verify end-to-end against the running program. No ceremony.
---

# /fix

Bugfix workflow with TDD. Investigates the bug, writes a failing test, fixes at the root cause, **verifies end-to-end against the running program**, finishes. No plan file, no approval mid-flow, no separate verify phase.

Use `/fix` for bugs. Use [`/spec`](/docs/workflows/spec) for features and architectural changes — including bugfixes that warrant a full plan with approval and code review.

```bash
# Claude Code
claude
> /fix "annotation persistence drops fields between save and reload"
> /fix "off-by-one in pagination at boundary"
> /fix "wrong default for max_retries"

# Codex CLI
codex
> $fix "annotation persistence drops fields between save and reload"
> $fix "off-by-one in pagination at boundary"
> $fix "wrong default for max_retries"
```

`/fix` is **always quick**. If investigation reveals the bug is multi-component, architectural, or otherwise larger than a quick fix, `/fix` stops cleanly and tells you to re-invoke with `/spec`. It does not silently switch lanes.

## Workflow

```text
Investigate  →  RED  →  Fix  →  Verify End-to-End  →  Quality Gate  →  Done
```

### Investigate

When the report names a failing test, a CI failure, or a crashing command, `/fix` runs it locally **first** — before reading any code — and reads the complete output, not just the assertion: warning logs, stderr, and swallowed-exception notices often name the root cause directly. If the environment blocks the run (expired cloud auth, dependencies behind a private registry), `/fix` names the blocker and the exact unblock command and asks you to unblock it instead of speculating around the missing run.

Then trace the bug to `file:lineN — function() does X but should do Y` with **High** or **Medium** confidence. For UI / async / race / timing bugs that don't surface from a static read, add temporary `SPEC-DEBUG:`-marked logs at component boundaries before tracing. Low confidence bails out.

### RED — Write the Reproducing Test

Encode `Currently → Expected` via an existing public entry point. Run it; it must **fail** with an error matching the symptom. A test that passes against buggy code doesn't encode the bug.

### Fix at the Root Cause

Minimal change at the root cause. Symptom patches (`try/except` hiding the bug, swallowed returns, silently normalised inputs) are forbidden. Re-run the reproducing test → must pass. Run the targeted test module(s).

A diff sanity check follows: root-cause file IS in the diff, no unplanned files, < 20 lines typically. A grep over the diff catches symptom-patching and leftover `print` / `console.log` / `SPEC-DEBUG:` markers — every match must be justified or reverted.

### Verify End-to-End

The primary correctness signal. Run the actual program with the original input and observe the symptom is gone — a passing unit test alone is never accepted. This step is mandatory.

| Bug surface | Tool | Evidence |
| --- | --- | --- |
| **UI / web** | Browser automation — Claude Code prefers its Chrome extension; Codex uses Chrome DevTools MCP. Both fall back to playwright-cli / agent-browser. | Page state, element values |
| **CLI** | The exact command the user ran | Stdout, exit code |
| **HTTP API** | `curl` / HTTP client with the user's body | Status code, response field |
| **Library / SDK / function** | `python -c '…'`, `node -e '…'`, REPL, scratch script | Returned value |
| **Background job** | Trigger manually with the failing input | Logs |

The completion report must include concrete evidence — bare assertions ("looks fixed", "tests pass") are insufficient. If the symptom persists, the unit test is at the wrong layer: move the assertion up to the user's actual entry point and re-run RED → Fix → Verify End-to-End.

### Quality Gate

Lint + types + build (when applicable), then the full anti-regression suite, once. If a far-from-the-fix test breaks, the bug has unintended cross-coupling — bail out to `/spec`.

### Finalise

If the **Changes Review** or **Codex Companion Changes Review** toggle is on, the corresponding review audits the fix first — the same reviewers `/spec` runs after implementation (a single `changes-review` sub-agent on Claude Code, the native agent on Codex). Findings are auto-fixed by severity before the commit and the approval gate, so review-driven changes land in the single bundled commit. Worktree mode: bundle test + fix into one `fix:` commit. Approval gate fires only if **Plan Approval** is enabled. The gate waits for you — Pilot disables Claude Code's 60-second idle auto-continue for unanswered questions (see the [approval gates note](/docs/workflows/spec) in `/spec`). The completion report includes a mandatory **E2E** line documenting what was actually run.

## When to bail out — use `/spec` instead

`/fix` stops and tells you to re-invoke with `/spec` when:

- Bug spans 3+ files or 2+ components.
- Root cause is architectural, not a single line.
- Fix needs defense-in-depth at multiple layers.
- Confidence stays Low — root cause can't be pinned to file:line.
- Two failed fix attempts.
- Fix has non-trivial UI implications that warrant a recorded Verification Scenario.

The full lane (`/spec`) adds: Behavior Contract, three-task structure, plan file with approval gate, Console annotation cycle, `cp`+`trap` revert-test proof in verify, iteration cap at 3.

## Common issues

| Symptom | What it means | What to do |
| --- | --- | --- |
| Can't reproduce | Description too vague or environment-dependent | Ask for exact steps, env, stack trace. Don't write a speculative fix. |
| Repro blocked by environment | Expired cloud auth, private package registry, missing credentials | `/fix` names the blocker and the unblock command (e.g. `gcloud auth application-default login`) and waits for you — it never substitutes speculation for a run. |
| Test passes without the fix | Test doesn't encode the bug | Tighten the assertion or pick a more specific input. |
| Fix breaks far-away tests | Cross-coupling beyond the quick lane | Bail out. Re-invoke with `/spec`. |
| Reproducing test green but user still hits the bug | Test sits below the user's layer | Move the assertion up and re-run RED → Fix → Verify End-to-End. |
| Two failed fix attempts | Architectural problem, not a fix problem | Bail out. The pattern needs reconsidering, not another patch. |

## Configurable Toggles

`/fix` honours the same Console Settings as `/spec`:

| Toggle | Default | Effect when disabled |
| --- | --- | --- |
| **Ask Questions** | On | Investigation skips clarifying questions and uses defaults. |
| **Plan Approval** | On | The end-of-flow approval gate is skipped. |
| **Changes Review** | On | The changes review (sub-agent on Claude Code, native agent on Codex) does not audit the fix at finalise. |
| **Codex Companion Changes Review** | Off | No second-opinion Codex review of the fix (Claude Code only; needs the Codex plugin). |

When **Ask Questions** and **Plan Approval** are both off, `/fix` runs end-to-end with no user interaction. Worktree isolation is not honoured — use `/spec` if you want a worktree.

## When to use `/spec` vs `/fix`

| Use `/fix` | Use `/spec` |
| --- | --- |
| Something is broken | Building new functionality |
| You want a fix without ceremony | Architecture or design decision matters |
| You want it done now | Work warrants a written plan + approval |

`/fix` handles the full range — from typos to multi-step debugging. It bails out and points to `/spec` only when complexity is truly architectural (multiple components, defense-in-depth at multiple layers, repeated failed attempts).
