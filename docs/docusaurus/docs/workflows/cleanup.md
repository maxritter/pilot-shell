---
sidebar_position: 2
title: Cleanup
description: Audit dead and unused code candidates with project-native analyzers, independent reference checks, and no automatic deletion.
---

# /cleanup — Corroborated Dead-Code Audit

`/cleanup` is an explicit, report-only workflow for finding code that may be removable. Use `/cleanup` in Claude Code or `$cleanup` in Codex, optionally followed by a path or subsystem.

```bash
# Claude Code
> /cleanup "src/auth"

# Codex CLI
> $cleanup "src/auth"
```

## Why report-only

Unused-code tools produce candidates, not proof. Dynamic imports, decorators, framework routes, callback registration, serialization, configuration, public exports, generated consumers, and tests can all make a zero-caller symbol live. LSP and graph indexes are bounded by their configured workspace and static model.

`/cleanup` therefore leaves the worktree unchanged. Removing reviewed candidates is a separate implementation request with focused tests and the repository's broader quality gates.

## Workflow

```text
Scope  →  Generate candidates  →  Corroborate independently  →  Report
```

1. **Scope** — records the requested paths, languages, dirty state, generated/vendor boundaries, public APIs, and available configured analyzers.
2. **Candidates** — runs repository-native tools already available in the project. Examples include Knip or compiler diagnostics for JavaScript/TypeScript and Vulture, deadcode, Ruff, or basedpyright for Python. It does not install or configure tools.
3. **Corroborate** — reads each definition, searches exact references, checks CodeGraph structure and Semble intent results when available, then challenges the candidate against exports, callbacks, registries, routes, decorators, reflection, configuration, tests, and generated consumers.
4. **Report** — separates likely removable candidates, uncertain/keep items, test-only code, excluded noise, and checks that could not run. Every conclusion includes its source commands and the next proof needed.

## Confidence contract

A candidate needs at least two independent supporting signals and no unresolved dynamic or public-entrypoint explanation before it can be labeled **likely removable**. The workflow never calls code “confirmed dead”; only deletion followed by focused and broader verification can establish that result.

Claude Code can add native LSP reference evidence when a matching language-server plugin is active. Codex uses repository analyzers, CodeGraph, Semble, and exact search. Neither agent treats one missing-reference result as a deletion decision.

## Output

The final response begins with a direct verdict and includes:

- candidate symbol and location;
- analyzer or graph source;
- literal and structural reference evidence;
- dynamic, framework, test, generated, and API risk;
- confidence and next proof;
- unavailable checks and exact command results;
- before/after worktree status confirming that no source files changed.

## When not to use

- Use `/investigate` for one behavioral question rather than a cleanup inventory.
- Use `/fix`, `/build`, or `/spec` when the request is to change code now.
- Use the repository's ordinary formatter or linter command for style-only cleanup.
