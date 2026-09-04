# Pilot Shell repository instructions

## Project

Pilot Shell is an engineering harness for Claude Code and Codex. The installer
ships agent-specific skills, rules, hooks, MCP configuration, the Console, and
the `pilot` CLI while preserving user-owned configuration.

## Commands

- Launcher: `rtk uv run pytest launcher/tests/unit/ -q`
- Installer: `rtk uv run pytest installer/tests/unit/ -q`
- Hooks: `rtk uv run pytest pilot/hooks/tests/ -q`
- Benchmark skill: `rtk uv run pytest pilot/skills/benchmark/tests/ -q`
- Console: `cd console && rtk bun test`
- Full Python: `rtk uv run pytest installer/tests/unit/ launcher/tests/unit/ pilot/hooks/tests/ pilot/skills/benchmark/tests/ -q`
- Build binary: `rtk uv run python -m launcher.build`
- Agent-asset parity: `rtk node scripts/sync-agent-assets.mjs --check`

## Repository rules

- Preserve unrelated work in the dirty worktree. Do not reset, restore, or
  overwrite concurrent changes.
- Use `rtk` for shell commands, `apply_patch` for source edits, Semble for intent
  search, CodeGraph for callers or non-local runtime blast radius, and ast-grep
  for syntax-aware structural search or controlled codemods.
- Keep `launcher/` and `installer/` independent. They ship as separate packages
  and must never import one another.
- Edit generated contracts at their canonical source, regenerate them, and
  verify the installed/generated artifact rather than assuming source parity.
- Day-to-day prerelease work normally uses `dev`; production releases use
  `main`. Never switch branches, commit, push, rebase, or force-update history
  without the corresponding user authorization.

## Cross-agent assets

- `AGENTS.md` is the shared repository core; `CLAUDE.md` must remain exactly
  `@AGENTS.md` plus a trailing newline.
- `.agents/skills/` is canonical. `.claude/skills/` is generated and must not be
  edited directly.
- `scripts/sync-agent-assets.mjs --check` must pass. Use `--write` only to
  recover drift after fixing the canonical source.
- Ignored skills outside the explicitly tracked canonical/mirror set remain
  private local extensions and are never copied or deleted automatically.

## Matching detailed rules

- `.claude/rules/pilot-shell-codex-skill-sync.md` — `installer/steps/codex_files.py`, `installer/skill_builder.py`, their tests, `pilot/hooks/{codex_skill_sync.py,cc_skill_sync.py,_lib/util.py}`, hook tests, and `pilot/skills/**` — read before changing skill build, adaptation, or license gating.
- `.claude/rules/pilot-shell-installer-patterns.md` — `installer/**` — read before changing installer merge, ownership, or file-placement behavior.
- `.claude/rules/pilot-shell-package-boundaries.md` — `installer/**`, `launcher/**` — read before moving logic across package boundaries.
- `.claude/rules/pilot-shell-shared-display-sections.md` — `pilot/spec/plan-format.json`, `scripts/gen_plan_format.py`, Console Spec rendering, and website feedback rendering — read before changing plan section order or visibility.
