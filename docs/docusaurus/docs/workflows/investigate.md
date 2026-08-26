---
sidebar_position: 1
title: /investigate
description: Read-only codebase investigation for Claude Code and Codex — trace current behavior end-to-end, challenge the conclusion, and answer with checkable evidence.
---

# /investigate

Answer one question about the code that exists now, with evidence you can check. `/investigate` reads the current worktree, traces the relevant behavior end-to-end, and challenges its own conclusion before reporting it. It does not edit project files or create a plan, task list, patch, or report file.

The workflow is manual: invoke it when an ordinary answer is not enough and you want an evidence-backed account of the current codebase.

```bash
# Claude Code
claude
> /investigate "How does a CLI flag become persisted configuration?"
> /investigate "Does another session's active plan satisfy this validator?"

# Codex CLI
codex
> $investigate "How does a CLI flag become persisted configuration?"
> $investigate "Does the installed Codex skill preserve this Claude behavior?"
```

## When to use it

Use `/investigate` to answer questions such as:

- Does the code actually work the way I think it does?
- Where does this value, decision, or side effect come from?
- How does a request, flag, event, or piece of data move through the system?
- Which configuration, default, feature gate, or generated artifact controls the result?
- Is a behavior demonstrated at runtime, covered by a test, or only possible from the static source?

Use [`/fix`](/docs/workflows/fix) when you already want a defect repaired. Use [`/spec`](/docs/workflows/spec) when you want an implementation plan and change. `/investigate` explains what exists and stops read-only, even when it uncovers a likely bug.

## How it works

```text
Frame the claim  →  Trace the active path  →  Challenge the conclusion  →  Report
```

### Frame the exact question

The workflow turns the prompt into one answerable question or falsifiable claim. It checks the repository, branch, uncommitted changes, and applicable project guidance first, so the answer describes the code in the current worktree rather than an assumed clean checkout.

It explores before asking questions. A clarification is reserved for a missing identifier, input, environment, or expected behavior that cannot be recovered safely and would materially change the answer.

### Trace behavior, not keywords

A matching symbol is only the entry point. `/investigate` follows the parts of the active path that can change the answer:

1. User-visible or programmatic entry point
2. Inputs, defaults, configuration, and feature gates
3. Decision branches and data or state transformations
4. Boundaries such as storage, subprocesses, network calls, installers, or generated files
5. Observable return value, side effect, persisted state, or rendered output

The trace stays proportional. A named symbol gets a targeted read and a nearby cross-check; an unfamiliar cross-layer flow gets a complete path. Search results and delegated summaries remain leads until their decisive source is reopened.

### Match evidence to the claim

Different evidence proves different things:

| Claim | Evidence `/investigate` looks for |
|---|---|
| Intended behavior | Repository contract, schema, ADR, or instruction |
| Static behavior | Current configuration, types, and implementation |
| Integration behavior | Callers, callees, and generated or installed artifacts |
| Covered behavior | The focused test and its actual assertions |
| Runtime or current-state behavior | A fresh, bounded, non-mutating command or user flow |
| Dependency behavior | Locked version plus version-matched primary documentation |

Static source is not presented as runtime proof, and the existence of a test is not presented as proof beyond the case it asserts. When sources conflict, the answer names the conflict and identifies which source controls current execution.

### Challenge the conclusion once

Before reporting, the workflow asks what concrete observation would make its provisional answer false and searches for that counterexample. A non-obvious or load-bearing conclusion gets one orthogonal cross-check, such as caller against callee, implementation against configuration, source against an installed artifact, or a static trace against a focused command.

Commands run only when they are safe, bounded, non-mutating, and materially stronger than reading. If runtime proof is blocked or disproportionate, `/investigate` keeps the static conclusion and names the missing check.

## What the answer contains

The answer stays in the conversation and starts with the conclusion. It then includes only the sections that help:

- **How it works** — the concise path from entry point to outcome, with real `file:line` evidence
- **Cross-check** — the independent evidence and what it does or does not prove
- **Confidence** — High, Medium, or Low, tied to the evidence gathered
- **Not verified** — only gaps material enough to change the conclusion

Observed facts and inferred implications are distinguished explicitly. Low confidence means multiple plausible paths or missing decisive evidence; it does not get rewritten as certainty.

## Read-only boundary

`/investigate` may read files and history and run bounded non-mutating checks. It does not edit, format, generate, migrate, install, commit, clean up, or perform external writes. Tests that create only ignored caches may be used when they materially strengthen the answer, with repository status checked before and after.

The conversation is the artifact. If you later want a fix, implementation plan, or persisted report, request that separately after the investigation.
