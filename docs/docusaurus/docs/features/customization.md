---
sidebar_position: 10
title: Customization
description: Customize what Pilot Shell auto-installs — skills, rules, hooks, agents, MCP servers, LSP servers, and Claude settings
---

# Customization

Customize everything Pilot Shell auto-installs on your machine. Tweak the built-in `/spec` workflow, modify existing rules, register additional hooks on top of Pilot's defaults, change which MCP or LSP servers get configured, adjust the auto-applied `settings.json` and `claude.json` — all without forking Pilot or hand-editing `~/.claude/` after every update. Available on **Team** and **Enterprise** plans.

- **Team-wide (git URL):** publish your customization as a git repo; every developer runs `pilot customize install <git-url>` once, and `pilot customize update` pulls your team's latest.
- **Individual (local path):** drop the same files into a folder on your machine (e.g. `~/my-pilot-patch/`) and run `pilot customize install ~/my-pilot-patch`. `pilot customize update` re-applies directly from the same folder, so your edits take effect on the next update.

## What you can customize

| Target | What lives in the repo | How it composes |
|--------|------------------------|-----------------|
| **Skills** | `skills/<name>/...` + optional overlay ops in `customization.json` | Overlay ops (`insert_after`, `insert_before`, `replace`, `disable`) modify Pilot's built-in workflow skills (e.g. `/spec`, `/prd`); whole skill directories add new ones |
| **Rules** | `rules/*.md` | New rules are additive; same filename as a core rule → modifies the built-in rule |
| **Hooks** | `hooks/*.sh` + `hooks/hooks.json` | Scripts copied as-is; `hooks.json` registers additional hooks alongside Pilot's core hooks |
| **Agents** | `agents/*.md` | Add new agents alongside Pilot's built-ins (e.g. plug extra reviewers into the spec workflow) |
| **Top-level config** | `settings.json`, `claude.json`, `.mcp.json`, `.lsp.json` in the repo root | Modify the auto-applied Claude settings, app config, MCP server list, and LSP server list — see [Overriding top-level config](#overriding-top-level-config) below |

## File structure

The structure is the same whether you publish it as a git repo or keep it as a local folder. Directory names map 1:1 to `~/.claude/`:

```
my-customization/
├── customization.json          # Required: metadata + optional skill overlays
├── settings.json               # Optional: deep-merges into ~/.claude/settings.json
├── claude.json                 # Optional: deep-merges into ~/.claude.json
├── .mcp.json                   # Optional: replaces ~/.claude/pilot/.mcp.json
├── .lsp.json                   # Optional: replaces ~/.claude/pilot/.lsp.json
├── skills/                     # → ~/.claude/skills/
│   ├── spec-plan/steps/
│   │   └── security-review.md  # New step injected into spec-plan
│   └── team-deploy/            # Brand-new skill
│       ├── manifest.json
│       ├── orchestrator.md
│       └── steps/01-stage.md
├── rules/                      # → ~/.claude/rules/
│   ├── team-standards.md       # Additive
│   └── testing.md              # Overrides core (same filename)
├── hooks/                      # → ~/.claude/pilot/hooks/
│   ├── team-lint-check.sh
│   └── hooks.json              # Registers team-lint-check.sh (see below)
└── agents/                     # → ~/.claude/pilot/agents/
    └── team-reviewer.md
```

Only ship the files and directories you need. A repo with just `rules/` is a valid customization; so is one with just `.mcp.json`.

## Install and manage

```bash
pilot customize install <source>             # Install and apply
pilot customize update                       # Re-apply (pulls git source; reads local source in place)
pilot customize status                       # Active source, file counts, drift
pilot customize diff <skill>/<step-id>       # Unified diff vs upstream
pilot customize remove                       # Restore pristine state
```

`<source>` is either a git URL (`https://...`, `git@...`, `ssh://...`) or a local directory path (`/path/to/folder`, `~/my-patch`). Git sources are cloned into `~/.pilot/cache/customization/`; local sources are read in place on every apply — no cache, edits take effect immediately on `pilot customize update`.

`install` accepts `--branch <name>` (git only), `--subfolder <path>`, and `--json`. Every command is transactional: invalid overlay references fail fast before any file is written.

## Skill overlays

Each Pilot workflow skill ships as `orchestrator.md` + `manifest.json` + step fragments. Your `customization.json` declares how your fragments compose with upstream:

```json
{
  "name": "Acme Team",
  "version": "1.0.0",
  "schemaVersion": 2,
  "pilotVersionMin": "2.6.0",
  "overlays": {
    "<skill-name>": {
      "insert_after":  { "<anchor-id>": [{ "id": "my-step", "file": "steps/my-step.md" }] },
      "insert_before": { "<anchor-id>": [{ "id": "my-step", "file": "steps/my-step.md" }] },
      "replace":       { "<step-id>":   { "file": "steps/my-replacement.md" } },
      "disable":       [ "<step-id>" ]
    }
  }
}
```

Overlays run per skill in order: `disable` → `replace` → `insert_before` → `insert_after`. On install, Pilot applies them in memory and regenerates `SKILL.md` via atomic swap — upstream files are never mutated, and `pilot customize remove` restores byte-identical pristine state.

**Omit `overlays` entirely** if you're only shipping rules, hooks, or agents.

**Finding fragment IDs** to reference:

```bash
cat ~/.claude/skills/<skill-name>/manifest.json | jq '.steps[].id'
```

IDs are stable across Pilot versions — upstream can rename files or edit prose, the IDs stay constant.

## Registering hooks

A hook script at `hooks/team-lint-check.sh` is copied to `~/.claude/pilot/hooks/`, but Claude Code only runs it if it's registered in `hooks.json`. Pilot ships its own `hooks.json` with the core hooks; to add yours, ship a `hooks/hooks.json` in your repo that includes both.

1. Copy `~/.claude/pilot/hooks/hooks.json` into your repo at `hooks/hooks.json` — this is your baseline
2. Append your hook entries (under `PostToolUse`, `SessionStart`, etc.)
3. Keep the existing Pilot entries — your file replaces Pilot's, so anything you omit is lost

`pilot customize update` re-copies your `hooks.json` whenever you pull team changes, keeping your hooks registered.

## Drift detection (optional)

When you `replace` an upstream step, upstream may improve that same step later. Pilot will warn you if you opt in with a `pinned_hash`:

```json
"replace": {
  "step-1.6-write-plan": {
    "file": "steps/my-write-plan.md",
    "pinned_hash": "<hash from hashes.json>"
  }
}
```

Grab the hash from `~/.claude/skills/<skill>/hashes.json` — Pilot writes it on every install.

- `pilot customize status` compares your pinned hash to current upstream. Differs → warning.
- `pilot customize diff <skill>/<step-id>` shows what changed so you can port the improvement.
- Once you've updated (or chose to ignore), re-pin the hash and commit.

**Skip it** if you don't care about tracking upstream changes. `customize status` still flags overlay IDs that no longer exist upstream — those warnings appear regardless of `pinned_hash`.

## End-to-end example

```bash
mkdir -p my-customization/skills/<skill>/steps && cd my-customization
git init
```

Create `skills/<skill>/steps/security-review.md` with your step content, then `customization.json`:

```json
{
  "name": "Acme Team",
  "version": "0.1.0",
  "schemaVersion": 2,
  "overlays": {
    "<skill>": {
      "insert_after": {
        "<anchor-id>": [{ "id": "acme-security-review", "file": "steps/security-review.md" }]
      }
    }
  }
}
```

Install — either from a local folder (for yourself) or from a git repo (for your team):

```bash
# Option A: local path (personal use)
pilot customize install ~/my-customization

# Option B: git repo (team-wide)
git add -A && git commit -m "initial customization" && git push
pilot customize install https://github.com/your-org/my-customization.git
```

Your step now appears in `~/.claude/skills/<skill>/SKILL.md` right after the anchor.

## Overriding top-level config

Four Pilot config files can be overridden from your repo root. They use different strategies based on what each file contains:

| File in repo | Destination | Strategy | Notes |
|--------------|-------------|----------|-------|
| `settings.json` | `~/.claude/settings.json` | Deep-merge | Pack keys win; the launcher still re-injects the `model` field and env vars on every startup. |
| `claude.json`   | `~/.claude.json`          | Deep-merge | Preserves oauth account, project history, and caches — pack only overrides the keys it sets. |
| `.mcp.json`     | `~/.claude/pilot/.mcp.json` | Full copy | Pilot-owned; safe to replace. |
| `.lsp.json`     | `~/.claude/pilot/.lsp.json` | Full copy | Pilot-owned; safe to replace. |

**Deep-merge semantics:** nested objects merge recursively (pack values replace specific keys), arrays replace wholesale. If you want to add an entry to an array, your pack's file must include every item you want the final array to contain.

**When Pilot updates itself** (installer re-runs on version change, or you re-run `install.sh`): Pilot's baseline is re-applied, then your pack overlay re-applies on top. Pack values survive as "user customizations" through the three-way merge.

**On `pilot customize remove`:** `.mcp.json` and `.lsp.json` are deleted — re-run `install.sh` or the installer to restore Pilot defaults. `settings.json` and `claude.json` are left in place because they contain user state (oauth session, project history) — merged pack values stay until you edit them out manually. This is intentional safety — removing a pack should never wipe user data.

## See Also

- **[Extensions](/docs/features/extensions)** — per-project skills, rules, commands, and agents managed in the Console. Extensions are scoped to a single project; customization is a team-wide overlay that applies across every project via `pilot customize install`.
