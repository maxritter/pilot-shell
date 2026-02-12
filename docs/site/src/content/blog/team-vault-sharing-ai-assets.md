# Sharing AI Assets Across Your Team with Vault

Every team member configures Claude Code differently — different rules, different commands, different workflows. This creates inconsistency: one developer's Claude follows TDD, another's doesn't. Vault solves this by syncing AI assets through a shared Git repository.

## The Consistency Problem

Without shared configuration:

- New team members start from zero
- Best practices discovered by one developer stay local
- Rules drift between developers over time
- Onboarding means manually copying configuration files

## What Vault Shares

| Asset Type | Example | Shared Via |
|-----------|---------|-----------|
| **Rules** | Coding standards, testing requirements | `.claude/rules/*.md` |
| **Commands** | `/deploy`, `/review`, `/test` | `.claude/commands/*.md` |
| **Skills** | Learned workflows and patterns | `.claude/skills/*/` |
| **Agents** | Specialized review agents | `.claude/agents/*.md` |
| **Hooks** | Quality enforcement scripts | Hook configurations |

## Setup

Initialize a vault backed by a private Git repository:

```bash
sx init --type git --repo-url git@github.com:your-org/team-vault.git
```

This creates a shared store that all team members can push to and pull from.

## Publishing Assets

Share a rule with the team:

```bash
REPO=$(git remote get-url origin)
sx add .claude/rules/testing-standards.md \
  --yes --type rule --name "testing-standards" \
  --no-install --scope-repo $REPO
```

The `--scope-repo` flag ensures the rule only installs for this specific project. Use `--scope-global` for rules that apply to all repositories.

## Installing Assets

Team members pull shared assets:

```bash
sx install --repair
```

This fetches the latest versions and installs them to the correct locations. Run it after cloning a repo or when someone publishes updates.

## Scoping

| Scope | Installs To | Use When |
|-------|------------|----------|
| Project | `project/.claude/` | Rules specific to this codebase |
| Global | `~/.claude/` | Personal tools for all repos |
| Path | `project/path/.claude/` | Monorepo — different rules per service |

## Versioning

Every `sx add` creates a new version. The vault tracks version history:

```bash
sx vault list              # See all assets with versions
sx vault show my-rule      # See version history for an asset
```

Roll back by publishing a previous version.

## Practical Workflow

1. **Developer discovers pattern** — A debugging workflow that saves time
2. **Capture with /learn** — Pilot extracts it as a skill
3. **Share with /vault** — Push to the team vault
4. **Team installs** — `sx install --repair` on their machines
5. **Everyone benefits** — Claude knows the pattern in all sessions

This creates a flywheel: the more the team uses Claude, the smarter everyone's Claude gets.
