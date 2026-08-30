---
sidebar_label: Claude Code vs Codex
description: Pilot Shell support for Codex CLI and the ChatGPT desktop app, including shared workflows and platform differences from Claude Code.
---

# Claude Code vs Codex

Pilot Shell supports both agents. **Claude Code is the preferred agent** and has full feature coverage; Codex works for all daily development workflows with fewer platform features. Pilot works with Codex CLI and with the Codex runtime bundled in the ChatGPT desktop app on macOS.

## Works on Both

All core and additional workflows run on both agents. Use `/` on Claude Code and `$` on Codex:

- **Core workflows:** `/prd`, `/spec`, `/build`, `/fix`
- **Additional workflows:** `/investigate`, `/cleanup`, `/ui-design`, `/design-system`, `/ui-design-review`, `/claude-design`, `/benchmark`, `/setup-rules`, `/create-skill`
- Console — all 11 views, persistent memory, sessions, and memories shared between agents
- Lifecycle hooks, compaction recovery, SessionEnd finalization, and workflow stop guards
- Workflow quality gates on both agents; Claude Code additionally keeps its edit-time lint, format, type, and TDD hooks
- MCP servers (CodeGraph, Semble, mem-search, web-search, and more)
- Rules, standards, context optimization, and team memories
- Spec-review and changes-review agents

The UI design skills use the same source for both agents. Claude Code loads their slash form; Pilot compiles the Codex dollar-invocation form and copies the same on-demand references into `~/.agents/skills/`. For the real Claude Design service, Claude Code prefers its native connector while current Codex uses the credential-safe `pilot design` CLI bridge described in [UI Design Expertise](../workflows/ui-design.md#claude-design-on-current-codex).

## Claude Code Only

- **Status line** — real-time session metrics below every response
- **Pilot Bot** — scheduled tasks and background automation
- **Remote control** — connect from the Claude app / browser, plus channels (Telegram, Discord, iMessage)
- **Language Server integration** — LSP-driven diagnostics, hover docs, and go-to-definition (Codex uses repository lint/type commands during verification rather than an edit-time file-checker hook)
- **Model switching** — `/model` command to change models mid-session (Codex sets model via `codex --model` or `config.toml`)
- **`/effort ultracode`** — Claude Code's additional whole-project orchestration mode
- **Permission modes** — `Shift+Tab` cycle and Auto Mode classifier (Codex uses `approval_policy` in `config.toml`)
- **Codex companion reviews** — OpenAI adversarial review launched from within Claude Code
- **Team-sharing of extensions** — push/pull of `~/.claude/` extensions through a git remote
- **Commands** — slash-command extensions in `.claude/commands/` (Codex has no command primitive)

Claude's native LSP can strengthen exact reference checks during `/cleanup`; Codex combines repository analyzers with CodeGraph, Semble, and exact search. Neither path treats a missing LSP or graph edge as proof that code is unreachable.
