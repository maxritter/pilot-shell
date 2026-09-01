---
sidebar_position: 5
title: /fix
description: Bugfix workflow — investigate root cause, write a RED reproducing test, fix at the source, then verify end-to-end against the running program. No ceremony.
---

# /fix

Bugfix workflow with TDD. Investigates the bug, writes a failing test, fixes at the root cause, **verifies end-to-end against the running program**, finishes. No plan file, no approval mid-flow, no separate verify phase.

Use `/fix` when you want a reported defect repaired. It keeps ownership even when investigation reveals a multi-component cause, structural change, substantial UI work, or a larger-than-expected diff. Scope changes how `/fix` organizes the work; it never causes a workflow handoff.

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

`/fix` starts with the smallest useful reproduction and scales as far as the defect requires. It can deepen the trace, decompose work across components, introduce a necessary test seam, make a coherent architectural repair, and broaden end-to-end verification without asking you to restart under another workflow.

## Workflow

```text
Investigate  →  RED  →  Fix  →  Verify End-to-End  →  Quality Gate  →  Done
```

### Investigate

When the report names a failing test, a CI failure, or a crashing command, `/fix` runs it locally **first** — before reading any code — and reads the complete output, not just the assertion: warning logs, stderr, and swallowed-exception notices often name the root cause directly. If the environment blocks the run (expired cloud auth, dependencies behind a private registry), `/fix` names the blocker and the exact unblock command and asks you to unblock it instead of speculating around the missing run.

Then trace the bug to `file:lineN — function() does X but should do Y` with **High** or **Medium** confidence. For UI / async / race / timing bugs that don't surface from a static read, add temporary `SPEC-DEBUG:`-marked logs at component boundaries before tracing. Low confidence means deeper investigation before production code—not a workflow redirect.

### RED — Write the Reproducing Test

Encode `Currently → Expected` via an existing public entry point. Run it; it must **fail** with an error matching the symptom. A test that passes against buggy code doesn't encode the bug.

### Fix at the Root Cause

Minimal change at the root cause. Symptom patches (`try/except` hiding the bug, swallowed returns, silently normalised inputs) are forbidden. Re-run the reproducing test → must pass. Run the targeted test module(s).

A diff sanity check follows: the root-cause file is in the diff, every file and hunk follows the causal chain, and no unrelated cleanup is bundled. A grep over the diff catches symptom-patching and leftover `print` / `console.log` / `SPEC-DEBUG:` markers — every match must be justified or reverted. There is no file-count or line-count ceiling on a necessary repair.

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

Lint + types + build (when applicable), then the full anti-regression suite, once. A far-from-the-fix failure is evidence of coupling: `/fix` traces whether the repair caused it, corrects the integration when it did, or records it as unrelated pre-existing evidence when it did not.

### Finalise

If the **Changes Review** or **Codex Companion Changes Review** toggle is on, the corresponding review audits the fix first — the same reviewers `/spec` runs after implementation (a single `changes-review` sub-agent on Claude Code, the native agent on Codex). Findings are auto-fixed by severity before the approval gate, so what you approve is the reviewed fix. Approval gate fires only if **Plan Approval** is enabled, and it comes **before** the commit and the merge — nothing has landed when you are asked, so "request changes" costs nothing to act on. Worktree mode: once approved, test + fix are bundled into one `fix:` commit and squash-merged back. The gate waits for you — Pilot disables Claude Code's 60-second idle auto-continue for unanswered questions (see the [approval gates note](/docs/workflows/spec) in `/spec`). The completion report includes a mandatory **E2E** line documenting what was actually run.

## How `/fix` scales

The workflow keeps going when the defect grows beyond its initial shape:

- **Several files or components:** decompose the causal chain into bounded work items and verify their integration.
- **Architectural root cause:** make the smallest coherent structural change that removes it, then cover the old failure boundary and the new contract.
- **Defense in depth:** repair every required boundary while keeping each change traceable to the same defect.
- **Low confidence or failed attempt:** revert unsupported edits, strengthen the reproduction and observability, then challenge the root-cause statement.
- **Non-trivial UI behavior:** capture the interaction states and verify the complete flow in the real browser or installed app.

`/fix` pauses only for a genuine external blocker: missing user-only information, credentials or authorization, an unavailable system, or a material product choice that cannot be inferred safely. It names the exact unblock action and resumes the same workflow afterward.

## Common issues

| Symptom | What it means | What to do |
| --- | --- | --- |
| Can't reproduce | Description too vague or environment-dependent | Ask for exact steps, env, stack trace. Don't write a speculative fix. |
| Repro blocked by environment | Expired cloud auth, private package registry, missing credentials | `/fix` names the blocker and the unblock command (e.g. `gcloud auth application-default login`) and waits for you — it never substitutes speculation for a run. |
| Test passes without the fix | Test doesn't encode the bug | Tighten the assertion or pick a more specific input. |
| Fix breaks far-away tests | The repair exposed coupling or the failure is pre-existing | Trace causality, correct in-scope integration, or report unrelated baseline evidence. |
| Reproducing test green but user still hits the bug | Test sits below the user's layer | Move the assertion up and re-run RED → Fix → Verify End-to-End. |
| An attempted fix fails | The current root-cause hypothesis is incomplete | Revert the unsupported edit, rerun the reproduction, and continue from the new evidence. |

## Configurable Toggles

`/fix` honours the same Console Settings as `/spec`:

| Toggle | Default | Effect when disabled |
| --- | --- | --- |
| **Ask Questions** | On | Investigation skips clarifying questions and uses defaults. |
| **Plan Approval** | On | The end-of-flow approval gate is skipped. |
| **Changes Review** | On | The changes review (sub-agent on Claude Code, native agent on Codex) does not audit the fix at finalise. |
| **Codex Companion Changes Review** | Off | No second-opinion Codex review of the fix (Claude Code only; needs the Codex plugin). |

When **Ask Questions** and **Plan Approval** are both off, `/fix` runs end-to-end with no user interaction.

`/fix` takes the same branch options `/spec` does — `--worktree=yes` for an isolated checkout squash-merged back at the end, or `--new-branch` for a `fix/<slug>` branch off the default branch. With **Branch Isolation** on and no flag given, it asks; with the toggle off it works on the current branch. The merge-back is `/fix`'s own: after you approve, it commits inside the worktree, syncs, and cleans up.

## Workflow ownership

`/fix` handles the full range from typos to multi-component and architectural defect repairs. `/spec` remains a separate, user-selected workflow for work measured against an ordered plan approved before implementation; `/build` remains a separate, user-selected workflow for a named outcome whose approach can emerge while building. `/fix` never selects either one on the user's behalf.
