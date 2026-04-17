---
sidebar_position: 1
title: Extensions
description: Manage all Claude Code extensions — skills, rules, commands, and agents — from a unified interface with team sharing and plugin visibility
---

# Extensions

Extensions are the things that customize Claude Code behavior. Pilot Shell provides a unified view of all extensions across multiple scopes: **global** (your personal `~/.claude/` directory), **project** (the `.claude/` directory in each project), **plugin** (installed Claude Code plugins), and **remote** (a connected team git repository).

## Extension Categories

| Category     | What it does                                                | Location                         |
| ------------ | ----------------------------------------------------------- | -------------------------------- |
| **Skills**   | Reusable workflows that load automatically when relevant    | `.claude/skills/<name>/SKILL.md` |
| **Rules**    | Instructions Claude follows every session (or by file type) | `.claude/rules/<name>.md`        |
| **Commands** | Slash commands invoked on demand via `/<name>`              | `.claude/commands/<name>.md`     |
| **Agents**   | Sub-agent definitions for specialized tasks                 | `.claude/agents/<name>.md`       |

## Scope: Global vs Project

**Global extensions** live in `~/.claude/` and are available in every project. They're personal to you.

**Project extensions** live in `.claude/` inside a specific project directory. They're visible only when that project is active and can be committed to the repository so teammates get them automatically.

## Plugin Extensions

Installed Claude Code plugins are automatically discovered and their extensions appear on the Extensions page. Plugin extensions are **read-only** — they come from the marketplace and cannot be edited, renamed, or deleted.

- Plugins are tracked in `~/.claude/settings.json` under `enabledPlugins`
- Plugin assets live at `~/.claude/plugins/marketplaces/<marketplace>/plugins/<name>/`
- Each plugin extension shows its plugin name as a badge (e.g., "code-review", "feature-dev")
- Filter by the **Plugin** scope button to see only plugin extensions

Install plugins via the Claude Code CLI: `claude plugin install <name>`

## Team Sharing (Team and Enterprise)

Share extensions with your team through a connected git repository. This feature is available on the Team and Enterprise plans.

### How It Works

Team sharing uses `~/.claude/` as a git repository with a scoped `.gitignore` that tracks **only** the four extension directories (skills, rules, commands, agents). Everything else in `~/.claude/` is ignored by git.

### Connecting a Remote

1. On the Console Extensions page, find the **Team Remote** card
2. Enter a git remote URL (e.g., `https://github.com/org/team-extensions.git`)
3. Optionally specify a **subfolder** if your extensions live in a subdirectory (e.g., `plugins/myteam`)
4. Click **Connect** — Pilot initializes the git repo and verifies connectivity

Authentication uses your existing system git credentials (SSH keys or credential helpers).

### Browsing Remote Extensions

After connecting, a **Remote** scope filter button appears in the filter bar. Select it to see all extensions available in the team repository. Each remote extension shows its file path in the repository.

### Push, Pull, and Diff

- **Push to Remote** — From any local extension's detail modal, click **Push** to upload it to the team repository
- **Download from Remote** — Click any remote extension and choose **Download to Global** or **Download to Project**
- **Diff and sync** — When an extension exists both locally and remotely, click the **Remote** compare button in the detail modal. A side-by-side diff view opens with sync options: **Use Remote → Local** or **Use Local → Remote**
- **Conflict detection** — If a push would overwrite a differing remote version, Pilot shows the diff and lets you choose

### APM Format (Cross-Tool Compatibility)

Pilot Shell supports pushing extensions in [APM (Agent Package Manager)](https://microsoft.github.io/apm/introduction/key-concepts/) format, making your team remote directly installable by anyone using `apm install owner/repo` — regardless of whether they use Copilot, Claude, Cursor, or other AI coding tools.

When **APM format** is enabled, extensions are converted on push:

| Pilot Shell (local)             | APM (remote)                                |
| ------------------------------- | ------------------------------------------- |
| `rules/my-rule.md`             | `instructions/my-rule.instructions.md`      |
| `commands/my-cmd.md`           | `prompts/my-cmd.prompt.md`                  |
| `agents/my-agent.md`           | `agents/my-agent.agent.md`                  |
| `skills/my-skill/SKILL.md`    | `skills/my-skill/SKILL.md` (unchanged)      |

APM-compatible [frontmatter](https://microsoft.github.io/apm/introduction/key-concepts/#instructions-instructionsmd) is automatically injected (e.g., `applyTo: "**"` for instructions, `description` for prompts and agents). An `apm.yml` manifest is generated in the remote.

**Enabling APM format:**
1. Click the edit (pencil) button next to your connected remote
2. Check the **APM format** checkbox
3. Click **Update** — Pilot migrates all existing extensions in a single commit

**Migrating back:** Uncheck APM format and update. Extensions are renamed back to native format. Content (including any frontmatter) is preserved.

**Mixed-format resilience:** During migration or partial updates, Pilot reads both formats from the remote, so no extensions become invisible.

Learn more about APM: [Getting Started](https://microsoft.github.io/apm/getting-started/first-package/), [Team Sharing](https://microsoft.github.io/apm/enterprise/teams/), [Key Concepts](https://microsoft.github.io/apm/introduction/key-concepts/).

### Subfolder Support

Some teams organize their extensions repository with subfolder paths (e.g., `plugins/myteam/rules/`, `plugins/myteam/skills/`). When you specify a subfolder during connection, all browse/push/pull operations automatically translate between the subfolder-prefixed remote paths and your local `~/.claude/` paths.

## Console Extensions Page

The [Pilot Console](/docs/features/console) provides a full management interface at `http://localhost:41777/#/extensions`.

### Viewing Extensions

- All extensions from all scopes appear in a unified two-column grid
- Each category has a distinct color: Skills (violet), Rules (amber), Commands (green), Agents (blue)
- Filter by **scope** (All / Global / Project / Plugin / Remote) and **category** (Skills, Rules, Commands, Agents)
- Search by name in the top-right search bar
- Extensions that exist in both scopes show an "also in global/project" indicator so you can spot duplicates at a glance
- Plugin extensions display the plugin name as a badge
- Click any extension to see its full content

### Editing Extensions

Extensions support:

- **View** — rendered preview or raw source toggle
- **Edit** — in-place markdown editor, saved directly to disk
- **Rename** — rename the file/directory
- **Delete** — with confirmation prompt
- **Move** — transfer between project and global scope (physically moves the file, not a copy)
- **Compare** — diff between project and global versions, or between local and remote versions
- **Push** — upload a local extension to the connected team remote
- **Download** — pull a remote extension to local global or project scope

Plugin extensions are read-only — edit, rename, delete, and move are not available.

### Moving Between Scopes

Clicking "→ Global" on a project extension physically moves the file from `.claude/` to `~/.claude/`. Clicking "→ Project" moves it back. This is a move, not a copy — the original is removed.

## Creating Extensions

Create extensions manually or via Claude Code commands:

- **Rules:** `/setup-rules` — explores your codebase and generates project-specific rules
- **Skills:** `/create-skill` — builds a reusable skill interactively from any topic
- **Commands:** Create `.claude/commands/<name>.md` manually
- **Agents:** Create `.claude/agents/<name>.md` manually

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

### Plugin Extensions (read-only)

```
~/.claude/plugins/marketplaces/<marketplace>/plugins/<name>/
├── .claude-plugin/plugin.json   ← plugin manifest
├── skills/                      ← plugin skills
├── rules/                       ← plugin rules
├── commands/                    ← plugin commands
└── agents/                      ← plugin agents
```

## See Also

- **[Customization](/docs/features/customization)** — for team-wide workflow modification. Extensions are project-scoped; customization is a git-hosted overlay that applies across every project via `pilot customize install`. It composes custom steps into core workflow skills and adds team rules, hooks, and agents. Available on Team and Enterprise plans.
