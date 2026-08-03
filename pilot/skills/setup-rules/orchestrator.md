---
name: setup-rules
description: Gives a repository its own project rules and keeps them true as the codebase moves. Use when the user types /setup-rules, asks to set up, audit, refresh, or fix project rules, CLAUDE.md, or AGENTS.md, says the rules are stale or contradict the code, or wants the project's MCP servers documented for agents.
user-invocable: true
---
# /setup-rules - Set Up Project Rules

**Set up and audit project rules.** Reads your codebase, generates modular rules, and documents MCP servers.

**Flow:** Read existing → Migrate → Quality audit → Explore → Compare → Sync rules → Sync MCP → Discover rules → Cross-check → Sync AGENTS.md → Summary

**Skill creation:** Use `/create-skill` to create workflow skills — `/setup-rules` focuses exclusively on rules and MCP documentation.

<!-- CC-ONLY -->
**Use the `AskUserQuestion` tool for user questions** — it renders a structured form; don't fall back to plain-text numbered questions.
<!-- /CC-ONLY -->
<!-- CODEX-START
**Use plain-text numbered options for user questions** — the `AskUserQuestion` tool isn't callable in Codex. Present options with trade-offs and wait for the user's response.
CODEX-END -->
