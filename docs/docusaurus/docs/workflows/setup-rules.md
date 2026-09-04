---
sidebar_position: 1
title: /setup-rules
description: Keep repository rules and skills synchronized across Claude Code and Codex while auditing project guidance and MCP documentation.
---

# /setup-rules

Generate project guidance once and keep Claude Code and Codex synchronized.

Run `/setup-rules` (or `$setup-rules` on Codex) to explore your project structure, discover conventions and undocumented patterns, audit stale guidance, and document custom MCP servers. It also prepares the repository for Pilot's shared synchronization hook and installs a checker that prevents the shared root guidance and tracked project skills from drifting between Claude Code and Codex.

Pilot uses one ownership model in every prepared repository:

| Asset | Role |
|-------|------|
| `AGENTS.md` | Shared, user-editable repository core for both agents |
| `CLAUDE.md` | One-line `@AGENTS.md` import for Claude Code |
| `.claude/rules/*.md` | Detailed, path-scoped guidance; indexed from `AGENTS.md` for Codex |
| `.agents/skills/` | Codex project skills and durable source for tracked skills |
| `.claude/skills/` | Claude Code project skills; changes synchronize safely in either direction |
| Pilot shared hook | Synchronizes on SessionStart, supported edits, and Stop as a Code Mode backstop |
| `scripts/sync-agent-assets.mjs` | Standalone recovery writer and CI drift checker committed with the project |

Existing repositories may keep an exact in-repository compatibility alias between `AGENTS.md` and `CLAUDE.md`, or between the two skill roots. Pilot recognizes that both agents already read the same physical source and leaves the alias intact. Links to any other target remain blocked.

```bash
# Claude Code         # Codex CLI
claude                codex
> /setup-rules        > $setup-rules
```

## What /setup-rules Does

12 phases:

| Phase | Action |
|-------|--------|
| 1 | Load ownership, writing, scoping, and error-handling guidelines |
| 2 | Inventory `AGENTS.md`, `CLAUDE.md`, scoped rules, both skill trees, the checker, and CI integration |
| 3 | Offer migration of unscoped legacy assets |
| 4 | Audit size, specificity, conflicts, stale references, imports, path scopes, and cross-agent drift |
| 5 | Explore the codebase with available search tools |
| 6 | Compare discovered and documented patterns |
| 7 | Put shared guidance in `AGENTS.md`, file-specific detail in scoped rules, and preserve existing content |
| 8 | Sync custom MCP server documentation |
| 9 | Discover missing rules and place them at the narrowest scope |
| 10 | Cross-check source fidelity, user-content coverage, rule routing, and skill migration safety |
| 11 | Install `scripts/sync-agent-assets.mjs`, confirm shared-hook coverage for both agents, and add `--check` to an existing CI job |
| 12 | Report exact parity evidence and all changes made |

## The synchronization contract

`AGENTS.md` is the shared core. Claude Code gets the same core because root `CLAUDE.md` contains only:

```text
@AGENTS.md
```

Detailed `.claude/rules/` files keep their `paths` frontmatter, so they load only for relevant Claude Code work. `AGENTS.md` carries a compact index telling Codex which matching rule to read; it does not duplicate the detailed content.

Pilot synchronizes complete project-skill trees between `.agents/skills/` and `.claude/skills/`, including `scripts/`, `references/`, and `assets/`. It runs on SessionStart and supported edits made through either Claude Code or Codex. A Stop hook covers Code Mode when no edit event fired.

Tracked skills retain `.agents/skills/` as their durable source, but a Claude-side edit synchronizes back when the Codex copy still matches the last trusted baseline. Untracked and gitignored skills use the same conflict-safe two-way rule with a baseline under `.git/pilot`. One-sided skills are copied automatically; when both sides changed independently, Pilot preserves both and reports the conflict.

Gitignored `.claude/rules/` remain one physical source. Pilot adds a bounded path index to the agent-only SessionStart context so Codex can load the relevant rule on demand without copying its contents into every prompt or printing hook status in the user-facing session.

The shared hook executes only Pilot's installed, trusted checker and automatically detects repositories containing agent assets. The repository copy is the command used by CI and manual recovery; hooks update it when present but never execute repository-controlled code. Successful synchronization is silent in both clients; only actionable conflicts or unsafe layouts surface to the user.

When an established repository uses exact shared aliases, edits to the physical instruction file remain allowed from either agent and Stop verifies the layout without trying to create a second copy.

The standalone commands remain available as recovery and verification:

```bash
node scripts/sync-agent-assets.mjs --write
node scripts/sync-agent-assets.mjs --check
```

Normal work does not require `--write`. Use it only to recover if the hook was unavailable; `--check` remains the local and CI backstop.

`/setup-rules` installs the script from Pilot's bundled copy. Existing user-authored root instructions and one-sided skills are migrated without dropping content; ambiguous two-sided conflicts still go through the workflow's review gate. Gitignored skill parity is recorded locally and therefore stays outside shared CI state.

For CI, add `node scripts/sync-agent-assets.mjs --check` to an existing required validation, lint, or documentation job. The check is fast and does not need a separate workflow or job.

## When to Run /setup-rules

- After installing Pilot in a new project
- After making significant architectural changes
- When `AGENTS.md`, `CLAUDE.md`, `.claude/rules/`, or either skill directory has drifted
- When adding new MCP servers to `.mcp.json`
- Before starting a complex `/spec` task on an unfamiliar codebase
- After onboarding to a project you didn't write

:::tip Creating skills
Use `/create-skill` to author project skills; Pilot's shared hook keeps the Claude Code and Codex trees synchronized automatically. `/setup-rules` owns the repository-wide synchronization contract, rules, and MCP documentation.
:::
