---
sidebar_position: 1
title: Extensions
description: Manage all Claude Code extensions — skills, rules, commands, and agents — from a unified interface
---

# Extensions

Extensions are the things that customize Claude Code behavior. Pilot Shell provides a unified view of all extensions across two scopes: **global** (your personal `~/.claude/` directory) and **project** (the `.claude/` directory in each project).

## Extension Categories

| Category | What it does | Location |
|----------|--------------|----------|
| **Skills** | Reusable workflows that load automatically when relevant | `.claude/skills/<name>/SKILL.md` |
| **Rules** | Instructions Claude follows every session (or by file type) | `.claude/rules/<name>.md` |
| **Commands** | Slash commands invoked on demand via `/<name>` | `.claude/commands/<name>.md` |
| **Agents** | Sub-agent definitions for specialized tasks | `.claude/agents/<name>.md` |

## Scope: Global vs Project

**Global extensions** live in `~/.claude/` and are available in every project. They're personal to you.

**Project extensions** live in `.claude/` inside a specific project directory. They're visible only when that project is active and can be committed to the repository so teammates get them automatically.

## Console Extensions Page

The [Pilot Console](/docs/features/console) provides a full management interface at `http://localhost:41777/#/extensions`.

### Viewing Extensions

- All extensions from both scopes appear in a unified two-column grid
- Each category has a distinct color: Skills (violet), Rules (amber), Commands (green), Agents (blue)
- Filter by **scope** (Global / Project / All) and **category** (Skills, Rules, Commands, Agents)
- Search by name in the top-right search bar
- Extensions that exist in both scopes show an "also in global/project" indicator so you can spot duplicates at a glance
- Click any extension to see its full content

### Editing Extensions

Extensions support:

- **View** — rendered preview or raw source toggle
- **Edit** — in-place markdown editor, saved directly to disk
- **Rename** — rename the file/directory
- **Delete** — with confirmation prompt
- **Move** — transfer between project and global scope (physically moves the file, not a copy)

### Moving Between Scopes

Clicking "→ Global" on a project extension physically moves the file from `.claude/` to `~/.claude/`. Clicking "→ Project" moves it back. This is a move, not a copy — the original is removed.

## Creating Extensions

Create extensions manually or via Claude Code commands:

- **Rules:** `/setup-rules` — explores your codebase and generates project-specific rules
- **Skills:** `/create-skill` — builds a reusable skill interactively from any topic
- **Commands:** Create `.claude/commands/<name>.md` manually
- **Agents:** Create `.claude/agents/<name>.md` manually

## Distributing Extensions

Share extensions across teams and organizations:

- **[Claude Code Plugin Registry](https://github.com/anthropics/claude-code/blob/main/docs/plugin-marketplaces.md)** — publish and discover extensions via the official registry
- **[Skillshare](https://github.com/runkids/skillshare)** — sync extensions org-wide via git remotes, with collect/sync workflow for keeping teams in sync

## File Locations Reference

### Global Extensions

```
~/.claude/
├── skills/         ← global skills
├── rules/          ← global rules
├── commands/       ← global commands
└── agents/         ← global agents
```

### Project Extensions

```
<project>/
├── .claude/
│   ├── skills/          ← project skills
│   ├── rules/           ← project rules (committed to repo)
│   ├── commands/        ← project commands
│   └── agents/          ← project agents
```
