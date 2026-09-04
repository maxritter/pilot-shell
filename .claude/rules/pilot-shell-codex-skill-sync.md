---
description: Keep skill build/sync + license-gating logic in sync across installer and session hooks
paths:
  - "installer/steps/codex_files.py"
  - "installer/skill_builder.py"
  - "installer/tests/unit/steps/test_codex_files.py"
  - "pilot/hooks/codex_skill_sync.py"
  - "pilot/hooks/cc_skill_sync.py"
  - "pilot/hooks/_lib/util.py"
  - "pilot/hooks/tests/test_codex_skill_sync.py"
  - "pilot/hooks/tests/test_cc_skill_sync.py"
  - "pilot/skills/**"
---

# Skill Sync Parity

`installer/steps/codex_files.py` builds Codex `SKILL.md` files during install.
`pilot/hooks/codex_skill_sync.py` rebuilds them on session start. Keep their
adaptation behavior equivalent.

## Required Parity

When changing Codex skill adaptation, update both implementations unless the
change is intentionally install-only or hook-only and the reason is documented.

Keep these behaviors aligned:

- Supported skill allowlists.
- Manifest v2 metadata, invocation policy, and bundled/progressive delivery.
- `<!-- CC-ONLY -->` stripping.
- `<!-- CODEX-START ... CODEX-END -->` unwrapping.
- `Skill(...)` call adaptation.
- `/skill-name` to `$skill-name` conversion.
- `AskUserQuestion` adaptation to a structured-question-neutral fallback without rewriting plain-text guidance into contradictions.
- Codex YAML frontmatter generation.
- Platform-adapted progressive step files and all runtime resources, including stale-resource cleanup.

## License Gating (both agents)

When the license is invalid, both session-start hooks remove Pilot-managed
`SKILL.md` artifacts so the skills cannot be invoked; when valid they are
restored. Keep these behaviors aligned:

- **Claude Code** (`cc_skill_sync.py`): deletes `~/.claude/skills/<name>/SKILL.md`
  on invalid; rebuilds *missing* ones on valid (never clobbers a present file).
  Its `_build_skill` mirrors `installer/skill_builder.py:build_skill_md`
  (orchestrator + steps joined by a blank line, then canonicalized).
- **Codex** (`codex_skill_sync.py`): deletes `~/.agents/skills/<name>/SKILL.md`
  + managed review-agent TOMLs on invalid; rebuilds the main file, metadata, and
  runtime-resource tree on valid.

**Scope is manifest-driven, not name-only.** Both hooks restrict removal to
skills tracked in `~/.claude/.pilot-manifest.json` via
`_lib/util.py:pilot_owned_skill_names`. User-created skills are never listed, so
they are never removed. A missing/unreadable manifest means "touch nothing" for
CC; Codex falls back to its static allowlist for legacy installs. If you change
the manifest path or shape, update `pilot_owned_skill_names` and
`installer/steps/claude_files.py:PILOT_MANIFEST_FILE` together.

## Tests

Run focused tests after any change:

```bash
uv run pytest installer/tests/unit/steps/test_codex_files.py pilot/hooks/tests/test_codex_skill_sync.py pilot/hooks/tests/test_cc_skill_sync.py launcher/tests/unit/test_skill_builder.py installer/tests/unit/test_skill_builder.py -q
```

If the change touches source skill content under `pilot/skills/**`, include at
least one test that builds the affected skill through the Codex path.
