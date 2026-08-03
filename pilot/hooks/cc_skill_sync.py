"""SessionStart hook: gate Pilot Shell Claude Code skills on license validity.

Pilot-managed CC skills live at ``~/.claude/skills/<name>/`` as a built
``SKILL.md`` (the artifact Claude Code loads) plus its source (``manifest.json``
+ ``orchestrator.md`` + ``steps/``). This hook gates only the built ``SKILL.md``:

  * License valid   → rebuild any MISSING ``SKILL.md`` from its source
                      (self-heal after a prior deactivation). A ``SKILL.md`` that
                      is already present is left untouched so installer /
                      customization output is never clobbered.
  * License invalid → delete ``SKILL.md`` for Pilot-managed skills so they can no
                      longer be invoked. The source survives, so reactivating the
                      license and restarting restores them.

Scope is restricted to skills tracked in ``~/.claude/.pilot-manifest.json`` —
user-created skills are never listed there, so they are NEVER touched. If the
manifest is missing or unreadable the hook does nothing (treats "unknown
ownership" as "touch nothing").

The build logic is self-contained (no launcher/installer imports) to respect the
package boundary, replicating ``installer.skill_builder.build_skill_md``. Keep it
in sync — see ``.claude/rules/pilot-shell-codex-skill-sync.md``.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.util import claude_config_dir, pilot_owned_skill_names  # noqa: E402


def _check_license() -> bool:
    pilot_bin = Path.home() / ".pilot" / "bin" / "pilot"
    if not pilot_bin.is_file():
        return True
    try:
        result = subprocess.run(
            [str(pilot_bin), "verify", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        data = json.loads(result.stdout)
        return data.get("valid", False)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
        return False


def _canonicalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _build_skill(skill_dir: Path) -> str | None:
    """Concatenate orchestrator + ordered steps into the CC SKILL.md body.

    Mirrors installer.skill_builder.build_skill_md (orchestrator + steps joined
    by a blank line, then canonicalized). Returns None if the source is absent
    or unreadable.
    """
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    orch_path = skill_dir / manifest.get("orchestrator", "orchestrator.md")
    if not orch_path.is_file():
        return None

    parts = [orch_path.read_text(encoding="utf-8")]
    for step in manifest.get("steps", []):
        step_path = skill_dir / step["file"]
        if not step_path.is_file():
            return None
        parts.append(step_path.read_text(encoding="utf-8"))

    return _canonicalize("\n\n".join(parts))


def _remove_cc_skills(skills_dir: Path, names: set[str]) -> int:
    """Delete SKILL.md for the named (Pilot-owned) skills. Source is preserved."""
    removed = 0
    for name in names:
        skill_md = skills_dir / name / "SKILL.md"
        if skill_md.is_file():
            skill_md.unlink()
            removed += 1
    return removed


def _rebuild_cc_skills(skills_dir: Path, names: set[str]) -> int:
    """Rebuild SKILL.md for named skills whose SKILL.md is missing.

    Present SKILL.md files are left untouched so we never clobber installer or
    customization output.
    """
    rebuilt = 0
    for name in names:
        skill_dir = skills_dir / name
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            continue
        content = _build_skill(skill_dir)
        if content is None:
            continue
        tmp = skill_dir / "SKILL.md.tmp"
        tmp.write_text(content, encoding="utf-8")
        os.replace(str(tmp), str(skill_md))
        rebuilt += 1
    return rebuilt


def main() -> None:
    claude_dir = claude_config_dir()
    if claude_dir is None:
        # CLAUDE_CONFIG_DIR set but invalid. This hook deletes and rebuilds
        # SKILL.md files, so falling back to ~/.claude would mutate the profile
        # the user was trying to protect. Do nothing.
        print(json.dumps({"continue": True}))
        return

    skills_dir = claude_dir / "skills"
    if not skills_dir.is_dir():
        print(json.dumps({"continue": True}))
        return

    names = pilot_owned_skill_names(claude_dir)
    if not names:
        # No manifest / nothing provably Pilot-owned → touch nothing.
        print(json.dumps({"continue": True}))
        return

    if _check_license():
        rebuilt = _rebuild_cc_skills(skills_dir, names)
        msg = f"Pilot skills restored: {rebuilt}" if rebuilt else ""
    else:
        removed = _remove_cc_skills(skills_dir, names)
        msg = f"License invalid — removed {removed} Pilot Shell skill(s)" if removed else ""

    print(json.dumps({"continue": True, "systemMessage": msg} if msg else {"continue": True}))


if __name__ == "__main__":
    main()
