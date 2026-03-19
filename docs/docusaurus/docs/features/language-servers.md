---
sidebar_position: 2
title: Language Servers
description: Real-time diagnostics and go-to-definition, auto-installed and configured
---

# Language Servers

Real-time diagnostics and go-to-definition, auto-installed and configured.

Language servers (LSP) give Claude real-time diagnostics, type information, and go-to-definition on every file edit. All three are auto-installed and configured via stdio transport — no manual setup. They work alongside the `file_checker.py` hook: hooks catch formatting and linting errors, LSP provides type-level intelligence.

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
