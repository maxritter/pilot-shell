---
description: Installer Patterns
paths:
  - "installer/**"
---

# Installer Non-Destructive Patterns

Preserve user customizations across Pilot Shell updates. Settings, skills, and rules merge intelligently without losing user changes.

## Three-Way Merge for Settings

Updates to `settings.local.json` or `~/.claude.json` use three-way merge:

```python
from installer.steps.settings_merge import merge_settings

# baseline = what Pilot Shell installed last time (.pilot-baseline.json)
# current  = what's on disk now (may include user changes)
# incoming = what Pilot Shell wants to install this time
merged = merge_settings(baseline, current, incoming)
```

| Field type | Behavior |
|------------|----------|
| Scalar (str, num) | User change wins. `current != baseline` → keep `current`; else use `incoming`. |
| Dict (`env`, `permissions`, `attribution`) | Merge keys individually using the scalar rule. |

**First install:** no baseline → incoming wins.

**Permissions** use `bypassPermissions` mode (no allow/deny/ask lists). The `permissions` dict is merged like any other dict.

## Manifest-Based File Tracking

Shared dirs (`<claude-config-dir>/skills/`, `<claude-config-dir>/rules/`) hold both Pilot Shell-managed and user files. The manifest at `<claude-config-dir>/.pilot-manifest.json` tracks Pilot Shell-owned paths.

The Claude config dir is `$CLAUDE_CONFIG_DIR` when set, else `~/.claude` — resolve it via `installer/claude_paths.py:get_claude_config_dir()`, never by hardcoding. The app config (`.claude.json`) has its own rule: `get_claude_app_config_path()`, whose base is `$HOME` when the variable is unset but the config dir when it is set.

```json
{
  "skills": ["skills/spec/SKILL.md", "skills/setup-rules/SKILL.md"],
  "rules":  ["rules/testing.md", "rules/skill-sharing.md"]
}
```

| File status | Action |
|-------------|--------|
| In manifest, exists | Update |
| In manifest, missing | Re-create (user deleted, restore) |
| **Not in manifest** | **PRESERVE** (user-created) |
| In manifest, not in incoming | Remove (Pilot Shell deprecated it) |

```python
from installer.steps.settings_merge import cleanup_managed_files
cleanup_managed_files(directory=home_claude / "rules", manifest_path=manifest_path, prefix="rules")
```

### Legacy Upgrade

Pre-manifest installs have files but no manifest. Seed it from existing files before cleanup so deprecated files can be safely removed:

```python
from installer.steps.settings_merge import save_manifest
if not manifest_path.exists():
    existing = {"rules/old-rule.md", "skills/old-skill/SKILL.md"}
    save_manifest(manifest_path, existing)
```

## When to Use

- **Three-way merge** — `settings.local.json` in project `.claude/`, `~/.claude.json`, any file where user customizations must be preserved.
- **Manifest tracking** — installs to shared dirs (`skills/`, `rules/`); upgrades from older versions; removing deprecated Pilot Shell files without touching user files.

## References

`installer/steps/settings_merge.py` (impl) · `installer/tests/unit/steps/test_pilot_files.py` + `test_claude_files.py` (tests) · `installer/steps/pilot_files.py` (agent-neutral usage) + `installer/steps/claude_files.py` (Claude-only usage) + `installer/steps/codex_files.py` (Codex-only usage).

## Step Split: Pilot / Claude / Codex

Three sibling step classes own the file installation, with clear destinations and gating:

| Step class | File | When it runs | Destinations |
|---|---|---|---|
| `PilotFilesStep` | `installer/steps/pilot_files.py` | Always | `~/.pilot/*` (hooks, scripts, ui, mcp config) + `<claude-config-dir>/skills/` (canonical skill source — Claude reads natively, Codex adapts) + `~/.pilot/rules/` (RAW rule sources staged for `CodexFilesStep._install_codex_rules` — keeps Codex's AGENTS.md fed with un-adapted content even on Codex-only systems where Claude's adaptation pass never runs) |
| `ClaudeFilesStep` | `installer/steps/claude_files.py` | Only when `is_claude_installed()` | `<claude-config-dir>/{rules,agents}` + `<claude-config-dir>/settings.json` (three-way merge) + Claude post-install merges (app-config MCP block, app config, model config migration, customization reapply). Inherits download/install helpers used by `PilotFilesStep`. |
| `CodexFilesStep` | `installer/steps/codex_files.py` | Only when `is_codex_installed()` | `~/.agents/skills/` (adapted from `<claude-config-dir>/skills/`; `~/.agents` is NOT relocatable — Codex derives it from `$HOME`) + `~/.codex/{agents,AGENTS.md,config.toml,hooks.json}`. Emits per-category counts mirroring the Claude section. Dispatched as a top-level step `[4/9]` from `cli.py`'s `get_all_steps()` — the `codex@openai-codex` Claude marketplace plugin is installed separately inside `DependenciesStep` (different concern: Codex CLI integration writes Codex's own config tree; the marketplace plugin enables Codex tooling from inside Claude Code). |

`PilotFilesStep` caches the categorized download in `ctx.config["_pilot_files_categories"]` so `ClaudeFilesStep` reuses it without a second GitHub round-trip. The manifest save + `_cleanup_stale_managed_files` tail runs in whichever step is the *last* to install files, so the stale-removal pass sees the union of pilot + Claude installed files (avoids temporarily removing live Claude entries between steps).
