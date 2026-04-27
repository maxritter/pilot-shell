---
sidebar_position: 4
title: Open Source Tools
description: Open-source tools installed alongside Pilot Shell
---

# Open Source Tools

Pilot Shell installs the following open-source tools during setup. Each tool is installed only if not already present on your system. All tools retain their original licenses and are not modified or redistributed by Pilot Shell. **Claude Code** (proprietary, by Anthropic) is also installed automatically if missing — it is the foundation that Pilot Shell extends.

## System Prerequisites

*Installed via Homebrew (macOS) or system package manager (Linux)*

| Tool | Purpose | License |
|------|---------|---------|
| [Homebrew](https://github.com/Homebrew/brew) | Package manager (macOS/Linux) | BSD-2-Clause |
| [Git](https://github.com/git/git) | Version control | GPL-2.0 |
| [GitHub CLI](https://github.com/cli/cli) | GitHub operations from the terminal | MIT |
| [Python 3.12](https://github.com/python/cpython) | Programming language runtime | PSF-2.0 |
| [Node.js 22](https://github.com/nodejs/node) | JavaScript runtime | MIT |
| [NVM](https://github.com/nvm-sh/nvm) | Node.js version manager | MIT |
| [pnpm](https://github.com/pnpm/pnpm) | Fast Node.js package manager | MIT |
| [Bun](https://github.com/oven-sh/bun) | JavaScript runtime and toolkit | MIT |
| [uv](https://github.com/astral-sh/uv) | Python package manager | MIT / Apache-2.0 |
| [Go](https://github.com/golang/go) | Programming language runtime | BSD-3-Clause |
| [gopls](https://github.com/golang/tools) | Go language server | BSD-3-Clause |
| [jq](https://github.com/jqlang/jq) | JSON processor | MIT |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | Fast text search | Unlicense / MIT |

## Development Tools

*Linters, formatters, type checkers, and language servers*

| Tool | Purpose | License |
|------|---------|---------|
| [Ruff](https://github.com/astral-sh/ruff) | Python linter and formatter | MIT |
| [basedpyright](https://github.com/DetachHead/basedpyright) | Python type checker | MIT |
| [Prettier](https://github.com/prettier/prettier) | Code formatter (JS/TS/CSS/HTML) | MIT |
| [TypeScript](https://github.com/microsoft/TypeScript) | TypeScript compiler | Apache-2.0 |
| [golangci-lint](https://github.com/golangci/golangci-lint) | Go linter aggregator | GPL-3.0 |
| [vtsls](https://github.com/yioneko/vtsls) | TypeScript language server | MIT |

## Search & Utilities

*Code search, usage analytics, and skill management*

| Tool | Purpose | License |
|------|---------|---------|
| [Probe](https://github.com/probelabs/probe) | Semantic code search engine | ISC |
| [RTK](https://github.com/rtk-ai/rtk) | Token-optimized CLI proxy (60-90% savings) | MIT |
| [CodeGraph](https://github.com/colbymchenry/codegraph) | Code knowledge graph and structural analysis | MIT |

## Plugin Runtime Dependencies

*npm packages used by Pilot Shell's memory and processing features*

| Tool | Purpose | License |
|------|---------|---------|
| [Transformers.js](https://github.com/xenova/transformers.js) | Local ML model inference for embeddings | Apache-2.0 |
| [sharp](https://github.com/lovell/sharp) | High-performance image processing | Apache-2.0 |
| [better-sqlite3](https://github.com/WiseLibs/better-sqlite3) | SQLite bindings for context-mode FTS5 and session DB | MIT |
| [Turndown](https://github.com/mixmark-io/turndown) | HTML-to-markdown conversion for context-mode web fetching | MIT |

## Testing Tools

*Browser automation and property-based testing*

| Tool | Purpose | License |
|------|---------|---------|
| [Chrome DevTools MCP](https://github.com/anthropics/chrome-devtools-mcp) | Browser automation via Chrome DevTools Protocol — Lighthouse, performance tracing, device emulation | Apache-2.0 |
| [playwright-cli](https://github.com/microsoft/playwright-cli) | Browser automation — persistent sessions, tracing, network mocking | Apache-2.0 |
| [agent-browser](https://github.com/vercel-labs/agent-browser) | Browser automation — lightweight, fast startup | Apache-2.0 |
| [Chrome for Testing](https://developer.chrome.com/blog/chrome-for-testing/) | Headless browser engine (via playwright-cli / agent-browser) | BSD-3-Clause |
| [hypothesis](https://github.com/HypothesisWorks/hypothesis) | Property-based testing (Python) | MPL-2.0 |
| [fast-check](https://github.com/dubzzz/fast-check) | Property-based testing (TypeScript) | MIT |

## MCP Servers

*Model Context Protocol servers pre-cached during install*

| Tool | Purpose | License |
|------|---------|---------|
| [context-mode](https://github.com/mksglu/context-mode) | Sandbox execution + FTS5 knowledge base — keeps large outputs out of context | ELv2 |
| [Context7](https://github.com/upstash/context7) | Library documentation lookup | MIT |
| [open-websearch](https://github.com/Aas-ee/open-webSearch) | Web search (multi-engine, no API key) | MIT |
| [fetcher-mcp](https://github.com/jae-jae/fetcher-mcp) | Web page fetching via Playwright | MIT |
