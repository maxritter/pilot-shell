---
sidebar_position: 10
title: Customization Packs
description: Override and extend Pilot Shell workflows with team-specific customization packs
---

# Customization Packs

Override core Pilot Shell workflows, skills, rules, hooks, and agents with your own team-specific versions via a git repository. Available on **Team** and **Enterprise** plans.

:::info Extensions vs Customizations
[Extensions](/docs/features/extensions) are **additive** — they add new skills, rules, and agents alongside core Pilot files via the Console UI. **Customization Packs** are **override-capable** — they can replace core files (like the spec dispatcher) and are managed via the CLI. Use extensions for sharing team content; use customizations for deep workflow modification.
:::

## Pack Structure

A customization pack is a git repository with a `customization.json` manifest and directories that mirror Pilot's file structure:

```
team-customization/
├── customization.json          # Required: pack metadata
├── skills/                     # Maps to ~/.claude/skills/
│   ├── spec/SKILL.md           # Overrides core spec dispatcher
│   ├── spec-plan/SKILL.md      # Overrides core planning phase
│   └── team-review/SKILL.md    # Adds new skill
├── rules/                      # Maps to ~/.claude/rules/
│   └── team-standards.md       # Adds team rule
├── hooks/                      # Maps to ~/.claude/pilot/hooks/
│   └── team-lint-check.sh      # Adds new hook
└── agents/                     # Maps to ~/.claude/pilot/agents/
    └── team-reviewer/AGENT.md  # Adds new agent
```

### `customization.json`

```json
{
  "name": "Acme Team Customization",
  "version": "1.0.0",
  "description": "Custom spec workflow with security review phase",
  "pilotVersionMin": "2.4.0",
  "pilotVersionMax": null
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name for the pack |
| `version` | Yes | Semantic version of the pack |
| `description` | No | Short description |
| `pilotVersionMin` | No | Minimum compatible Pilot version |
| `pilotVersionMax` | No | Maximum compatible Pilot version |

### File Mapping

| Pack Directory | Destination | Can Override Core? |
|---------------|-------------|-------------------|
| `skills/` | `~/.claude/skills/` | Yes |
| `rules/` | `~/.claude/rules/` | Yes |
| `hooks/` | `~/.claude/pilot/hooks/` | Yes |
| `agents/` | `~/.claude/pilot/agents/` | Yes |

:::warning settings.json Not Supported
Customization packs cannot override `settings.json`. The Pilot launcher rewrites parts of `settings.json` on every startup, which would cause the pack version to drift immediately. Configure settings via Console Settings instead.
:::

## CLI Commands

### Install

```bash
pilot customize install https://github.com/your-org/pilot-customizations.git
```

Options:
- `--branch <branch>` — Git branch (default: `main`)
- `--subfolder <path>` — Subfolder within the repo for monorepos
- `--json` — Output as JSON

### Update

Pull the latest changes from the remote and re-apply:

```bash
pilot customize update
```

This also runs automatically when `pilot update` installs a new Pilot version.

### Status

```bash
pilot customize status
pilot customize status --json
```

Shows: pack name, version, source URL, branch, commit SHA, last applied timestamp, and file counts (overrides vs additions).

### Remove

```bash
pilot customize remove
```

Removes all customization files and clears the configuration. Run `pilot update` or the installer afterward to restore core Pilot files that were overridden.

## Team Workflow

### Setting Up (Team Lead)

1. Create a git repository for your team's customizations
2. Add `customization.json` with your pack metadata
3. Add custom skills, rules, hooks, or agents in the appropriate directories
4. Push to your team's git hosting (GitHub, Bitbucket, GitLab)

### Onboarding (Team Members)

1. Install Pilot Shell normally: `curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash`
2. Install the customization pack: `pilot customize install https://your-org/repo.git`
3. Done — customizations persist across `pilot update`

### Keeping Up to Date

- Team lead pushes changes to the customization repo
- Team members run `pilot customize update` to pull latest
- `pilot update` automatically re-applies customizations after updating core Pilot

## How It Works

1. **Install** clones the pack repo to `~/.pilot/cache/customization/`
2. Files are copied to `~/.claude/` — overriding core files where they overlap
3. A separate manifest (`~/.pilot/.customization-manifest.json`) tracks which files came from the pack
4. The source URL is persisted in `~/.pilot/config.json` under the `customization` key
5. On `pilot update`, the installer calls `pilot customize update` after core files are installed
6. **Customization always wins** — no merge conflicts, your pack's version takes precedence

## Common Customizations

### Custom Spec Workflow

Override `skills/spec/SKILL.md` to add phases, change routing, or modify the dispatcher:

```markdown
# /spec - Custom Spec Workflow

## Workflow
/spec → Detect type → Feature: Skill('spec-plan') → Plan → Skill('team-security-review') → Implement → Verify
```

### Team Coding Standards

Add `rules/team-standards.md` with your team's coding conventions — automatically loaded into every Claude session.

### Custom Review Agent

Add `agents/team-reviewer/AGENT.md` to define a specialized code review agent for your team's domain.

### Custom Plan Statuses

The default spec workflow uses three statuses: `PENDING`, `COMPLETE`, `VERIFIED`. If your custom workflow writes additional statuses to the plan `Status:` header (e.g., `DEPLOYED`, `QA_REVIEW`), both the Console dashboard and the status line display them as-is with neutral styling. No configuration needed — any `Status:` value is supported.

## Tier Availability

| Capability | Solo | Team | Enterprise |
|-----------|------|------|-----------|
| Extensions (additive, via Console) | Cross-machine sync | Team sharing via git | Team sharing via git |
| **Customization Packs (override, via CLI)** | — | **Yes** | **Yes** |
| Full source code (launcher, console) | — | — | Yes |
