## Team Sharing

Share AI assets (rules, skills, commands, agents, hooks, MCP configs) across your team using `sx` and a private Git repository.

### Primary Interface

**Use the Teams page in the Pilot Shell Console dashboard** (`http://localhost:41777/#/teams`) — browse assets, push local assets, configure the repository. Teams features require a **Team plan** license.

### When to Use

| Situation                              | Action                                                 |
| -------------------------------------- | ------------------------------------------------------ |
| User says "share", "push", "team"      | Direct to Teams page in Console                        |
| After `/sync` creates new rules/skills | Suggest pushing via Teams page                         |
| User wants team consistency            | Set up repository via Teams page configuration section |
| New team member onboarding             | `sx install --repair --target .`                       |

### sx CLI Quick Reference

For power users or CI/CD. The Console Teams page wraps these commands in a UI.

```bash
# Status
sx config                              # Show config, repository URL, installed assets
sx vault list                          # List all vault assets with versions

# Pull team assets
sx install --repair --target .         # Fetch and install to current project

# Push assets (project-scoped — recommended)
REPO=$(git remote get-url origin)
sx add .claude/skills/my-skill --yes --type skill --name "my-skill" --scope-repo $REPO

# Browse & remove
sx vault show <asset-name>             # Show asset details and versions
sx remove <asset-name> --yes           # Remove from lock file
```

### Asset Types

| Type      | Flag             | Source Path                  |
| --------- | ---------------- | ---------------------------- |
| `skill`   | `--type skill`   | `.claude/skills/<name>/`     |
| `rule`    | `--type rule`    | `.claude/rules/<name>.md`    |
| `command` | `--type command` | `.claude/commands/<name>.md` |
| `agent`   | `--type agent`   | `.claude/agents/<name>.md`   |

### Scoping

| Scope                     | Installs to        | Use When                                       |
| ------------------------- | ------------------ | ---------------------------------------------- |
| Project (`--scope-repo`)  | `project/.claude/` | **Recommended.** Assets stay with the project. |
| Global (`--scope-global`) | `~/.claude/`       | Personal tools needed in all repos.            |

### Setup (First Time)

Use the **configuration section** in the Console Teams page, or via CLI:

```bash
sx init --type git --repo-url git@github.com:org/team-repo.git
sx init --type path --repo-url /path/to/repo
```

### Tips

- Always use `sx install --repair --target .` to install assets
- Multiple profiles supported via `--profile` flag or `SX_PROFILE` env var
