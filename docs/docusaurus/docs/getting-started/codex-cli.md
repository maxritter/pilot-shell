---
sidebar_label: Claude Code vs Codex
description: What works with both agents and what requires Claude Code.
---

# Claude Code vs Codex

Pilot Shell supports both agents. **Claude Code is the preferred agent** — it has full feature coverage. Codex works for all daily development workflows.

## Works on Both

All core and additional workflows run on both agents. Use `/` on Claude Code and `$` on Codex:

- `/spec`, `/build`, `/fix`, `/prd`, `/benchmark`, `/setup-rules`, `/create-skill`
- Console — all 10 views, persistent memory, sessions, and memories shared between agents
- Quality hooks and TDD enforcement
- MCP servers (CodeGraph, Semble, mem-search, web-search, and more)
- Rules, standards, and context optimization
- Spec-review and changes-review agents

## Claude Code Only

- **Status line** — real-time session metrics below every response
- **Pilot Bot** — scheduled tasks and background automation
- **Remote control** — connect from the Claude app / browser, plus channels (Telegram, Discord, iMessage)
- **Language Server integration** — LSP-driven diagnostics, hover docs, and go-to-definition (Codex still gets the same linting via the file-checker hook)
- **Model switching** — `/model` command to change models mid-session (Codex sets model via `codex --model` or `config.toml`)
- **`/effort ultracode`** — the parallel-surfaces escalation in [`/build`](/docs/workflows/build); Codex runs those surfaces sequentially instead. The rest of `$build` — Buildout file, stop-guard-held loop, statusline, Console — works identically.
- **Permission modes** — `Shift+Tab` cycle and Auto Mode classifier (Codex uses `approval_policy` in `config.toml`)
- **Codex companion reviews** — OpenAI adversarial review launched from within Claude Code
- **Team-sharing of extensions** — push/pull of `~/.claude/` extensions through a git remote
- **Commands** — slash-command extensions in `.claude/commands/` (Codex has no command primitive)
