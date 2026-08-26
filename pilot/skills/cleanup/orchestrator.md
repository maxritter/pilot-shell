---
name: cleanup
description: Report-only dead-code and unused-code cleanup audit for an existing repository. Runs only when the user explicitly types /cleanup. Uses project-configured analyzers to generate candidates, then corroborates them with exact search and available CodeGraph, Semble, or LSP evidence. Never installs tools, edits files, deletes code, or treats a graph/reference result as proof of safe removal.
argument-hint: "optional repository-relative scope"
user-invocable: true
disable-model-invocation: true
---

# /cleanup — Verification-First Dead-Code Audit

Produce a bounded report of unused-code candidates. This workflow is deliberately report-only: the user can make a separate implementation request after reviewing the evidence.

## Safety Contract

1. **Leave the repository unchanged.** Do not edit, delete, format, generate, migrate, install, initialize, synchronize, or clean caches. Do not run a tool's fix/write mode. Existing read-only checks that create only ignored runtime caches are acceptable, but the final worktree snapshot must equal the initial snapshot.
2. **Project-native analyzers nominate candidates.** Use only analyzers, compiler flags, or package scripts already configured and locally available in the repository. Never use CodeGraph, Semble, `rg`, LSP, or model judgment as the primary candidate generator.
3. **Navigation is not deletion proof.** CodeGraph traces structure, Semble searches intent, exact search checks literal occurrences, and Claude LSP can find semantic references. Each can miss dynamic or external consumers. Their absence of results never independently proves safe deletion.
4. **Require independent evidence.** Label a production symbol **likely removable** only when at least two independent signals agree, one is a project-native analyzer, and no public, dynamic, framework, configuration, generated, reflection, serialization, plugin, CLI, or external-consumer boundary remains unresolved.
5. **Keep tests distinct.** A production symbol referenced only by tests is not dead; report it as **test-supported production code**. Symbols defined inside test/fixture/example code belong in a separate **test-only candidates** section and never inflate the production result.
6. **Report facts, not implied actions.** Do not provide a deletion patch. Record the exact command and result behind every analyzer claim, including failures, skipped tools, selected scope, and candidate limits.

## Required Result Contract

Use only these status labels, exactly as written: **Likely removable**, **Needs boundary review**, **Test-supported production code**, **Test-only candidate**, **Referenced / false positive**, and **Unresolved**. Do not strengthen or paraphrase them into “confirmed,” “safe,” “ready,” “dead,” or another synonym.

Every final response includes `### Commands and results`, `### Worktree`, and `### Not verified`, even when the prompt supplies an evidence packet and asks only for classification. Attribute supplied results to the packet rather than claiming to have executed them. The Worktree section records initial state, final state, and whether they match; Not verified names every material evidence gap.

## Signal Independence

Use this minimum standard:

| Evidence | Role | Independence rule |
|---|---|---|
| Configured compiler/linter/dead-code analyzer | Candidate generator | Required for `likely removable` |
| Exact whole-repository symbol search | Corroboration | Counts when it includes tests, config, scripts, and entry-point metadata |
| CodeGraph callers/impact or bundled helper | Structural corroboration | Heuristic; graph absence alone is insufficient |
| Claude LSP references | Semantic corroboration | Optional; do not combine with CodeGraph absence as the only two signals |
| Semble intent search | Dynamic/boundary discovery | Useful for registration patterns and indirect consumers, not exhaustive |
| Source/config/package metadata read | Boundary resolution | Required whenever export, framework, plugin, CLI, or generated use is plausible |

Two tools derived from the same reference graph are one structural signal, not two independent signals. If independence is doubtful, classify conservatively.

## Allowed CodeGraph Helper

When an existing `.codegraph/codegraph.db` is present and the globally installed CodeGraph SDK is available, `scripts/codegraph-candidates.mjs` can obtain a deterministic, scoped snapshot of CodeGraph's unreferenced-symbol heuristic. Resolve the script relative to this skill's loaded `SKILL.md`, then run it from the target repository:

```bash
node --disable-warning=ExperimentalWarning <cleanup-skill-dir>/scripts/codegraph-candidates.mjs --root . --scope src --exclude src/generated --limit 100
```

The helper opens the existing graph read-only with synchronization disabled. It never initializes, indexes, syncs, or writes. Treat its JSON as one structural corroboration only. If CodeGraph or its index is absent, skip it without installing or initializing anything.

Complete Steps 1–4 in order.

## When Not to Use

- The user did not explicitly invoke `/cleanup`.
- The user asked to implement deletions or refactor code; handle that as a separate change request.
- The request is a general quality review, formatter pass, dependency update, or security audit.
- The target is not an existing repository or there is no meaningful source scope to audit.
