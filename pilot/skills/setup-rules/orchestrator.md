---
name: setup-rules
description: Gives a repository shared Claude Code and Codex guidance and keeps it true as the codebase moves. Use when the user types /setup-rules, asks to set up, audit, refresh, or fix project rules, CLAUDE.md, AGENTS.md, or repository skills, says agent assets drifted or contradict the code, or wants the project's MCP servers documented for agents.
user-invocable: true
---
# /setup-rules - Set Up Project Rules

**Set up and audit project guidance.** Reads your codebase, keeps the shared agent core and scoped rules concise, documents MCP servers, and installs automatic Claude Code/Codex asset synchronization with a deterministic checker.

**Flow:** Read existing → Migrate → Quality audit → Explore → Compare → Sync scoped rules → Sync MCP → Discover rules → Cross-check → Sync shared agent assets → Prove parity → Summary

**Skill creation:** Use `/create-skill` to author workflow skills. `/setup-rules` establishes their canonical/mirror layout and drift check but does not invent skill content.

<!-- CC-ONLY -->
**Use the `AskUserQuestion` tool for user questions** — it renders a structured form; don't fall back to plain-text numbered questions.
<!-- /CC-ONLY -->
<!-- CODEX-START
**Use plain-text numbered options for user questions** — the `AskUserQuestion` tool isn't callable in Codex. Present options with trade-offs and wait for the user's response.
CODEX-END -->
