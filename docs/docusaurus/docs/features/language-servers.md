---
sidebar_position: 2
title: Language Servers
description: Real-time diagnostics, go-to-definition, and find-references via Claude Code LSP integrations for Python, TypeScript, Go, and opt-in C#.
---

# Language Servers

:::warning Claude Code only
Language Server integration requires Claude Code's LSP support. Codex does not have an equivalent Pilot LSP integration and does not run `file_checker.py`. On Codex, use CodeGraph for structural questions and Semble for intent-based discovery, then rely on the repository's lint, type-check, build, and test commands for diagnostics and verification.
:::

Real-time diagnostics and go-to-definition for Claude Code, auto-installed and configured.

Language servers give Claude Code real-time diagnostics, type information, and go-to-definition on every file edit. All three are auto-installed and configured via stdio transport — no manual setup. They work alongside Claude Code's `file_checker.py` hook: the hook catches formatting and linting errors, while LSP provides type-level intelligence.

## Python — basedpyright

- Strict type checking with inference
- Real-time diagnostics on every edit
- Go-to-definition and find-references
- Hover documentation for any symbol
- Auto-restart on crash (max 3 attempts)

> Works with uv virtual environments automatically.

## TypeScript — vtsls

- Full TypeScript and JavaScript support
- Type checking across the entire project
- Import auto-completion and refactoring
- Auto-restart on crash (max 3 attempts)

> Handles both `.ts` and `.tsx` files. Respects your `tsconfig.json` settings automatically.

## Go — gopls

- Official Go language server by Google
- Static analysis and vet diagnostics
- Go module-aware resolution
- Rename and code actions support
- Auto-restart on crash (max 3 attempts)

> Requires Go modules. Respects GOPATH and module proxy settings.

## C# — csharp-ls (opt-in)

Unlike the servers above, the C# language server is **not auto-installed** — it needs the .NET SDK, which Pilot does not ship. .NET developers enable it explicitly, so non-.NET users aren't burdened with a .NET toolchain.

[C# LSP](https://claude.com/plugins/csharp-lsp) is the Roslyn-based `csharp-ls` server recommended by Claude. It provides real-time diagnostics, go-to-definition, find-references, hover, and `.editorconfig`-aware formatting for `.cs` files across .NET Core/Framework and multi-project solutions.

**Enable it:**

1. Install the plugin from the [C# LSP plugin page](https://claude.com/plugins/csharp-lsp).
2. Install the server as a global .NET tool: `dotnet tool install --global csharp-ls`. Requires a compatible .NET SDK (see the [csharp-ls release notes](https://www.nuget.org/packages/csharp-ls) for the version your release needs).

> With the LSP active you get the real-time compile diagnostics that Claude Code's `file_checker.py` hook does not provide for C# — the hook runs a single-file `dotnet format` check only. Compile errors otherwise surface when you run `dotnet test`.

## Refactors and dead-code cleanup

LSP references and CodeGraph results are useful evidence, but neither proves that a symbol is safe to rename or delete. Public entry points, framework registration, reflection, configuration, generated code, and tests outside the language server's configured scope may not appear in a reference list. A symbol referenced only from tests may still define required behavior; test-only references are not evidence that it is dead.

Use a verification-first cleanup pass:

1. Generate candidates with the repository's configured compiler, linter, or dead-code analyzer.
2. Ask `codegraph_explore(query="symbolName callers and impact")` for structural context.
3. Run an exact repository search for the symbol, including tests, configuration, scripts, and generated entry-point metadata.
4. Make the smallest deletion and run focused tests, then the broader type-check, build, and test suite required by the repository.

Treat automated dead-code output as a report of candidates, not an instruction to delete code.

:::tip Add custom language servers
Add custom language servers via `.lsp.json` in your project root. Each language key maps to its server configuration:

```json
{
  "rust": {
    "command": "rust-analyzer",
    "args": [],
    "transport": "stdio",
    "maxRestarts": 3
  }
}
```
:::
