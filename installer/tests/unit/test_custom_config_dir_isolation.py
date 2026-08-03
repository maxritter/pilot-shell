"""End-to-end proof that a custom CLAUDE_CONFIG_DIR install leaves ~/.claude alone.

This is the acceptance test for the reported problem: installing Pilot Shell must
not modify the personal Claude profile when the user has pointed
``CLAUDE_CONFIG_DIR`` at a different one.

⛔ Lives under ``tests/unit/`` deliberately. CI invokes pytest with an explicit
path list (``.github/workflows/release.yml`` / ``release-dev.yml``:
``installer/tests/unit/ launcher/tests/unit/ pilot/hooks/tests/ ...``), so a new
sibling ``tests/integration/`` directory would be collected locally via
``pyproject.toml`` testpaths but would NEVER run in CI.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from installer.context import InstallContext
from installer.ui import Console


@pytest.fixture(autouse=True)
def _allow_claude_config_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    """Neutralise the repo-wide autouse fixture that deletes CLAUDE_CONFIG_DIR.

    ``installer/tests/conftest.py`` unsets the variable for every installer test.
    Without opting out, the custom-dir cases below would silently exercise the
    default path and pass for the wrong reason.
    """
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)


def _snapshot(root: Path) -> dict[str, str]:
    """Content hash of every file under root, keyed by relative path."""
    if not root.exists():
        return {}
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def _hash_file(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def _seed_source(tmpdir: Path) -> Path:
    """Minimal pilot/ source tree the install steps read from."""
    source_pilot = tmpdir / "source" / "pilot"
    (source_pilot / "rules").mkdir(parents=True)
    (source_pilot / "agents").mkdir(parents=True)
    (source_pilot / "hooks").mkdir(parents=True)

    (source_pilot / "settings.json").write_text(
        json.dumps({"env": {"X": "1"}, "permissions": {"defaultMode": "bypassPermissions"}}, indent=2)
    )
    (source_pilot / "claude.json").write_text(json.dumps({"theme": "dark"}, indent=2))
    (source_pilot / ".mcp.json").write_text(json.dumps({"mcpServers": {"context7": {"command": "npx"}}}, indent=2))
    (source_pilot / "rules" / "testing.md").write_text("# Testing rule\n")
    (source_pilot / "agents" / "spec-review.md").write_text("# Spec review agent\n")
    (source_pilot / "hooks" / "noop.py").write_text("print('noop')\n")
    return tmpdir / "source"


def _install(tmpdir: Path, home_dir: Path) -> None:
    from installer.steps.claude_files import ClaudeFilesStep
    from installer.steps.pilot_files import PilotFilesStep

    dest = tmpdir / "dest"
    dest.mkdir(exist_ok=True)
    ctx = InstallContext(
        project_dir=dest,
        ui=Console(non_interactive=True, quiet=True),
        local_mode=True,
        local_repo_dir=tmpdir / "source",
    )
    with contextlib.ExitStack() as stack:
        stack.enter_context(patch("installer.steps.pilot_files.is_claude_installed", return_value=True))
        stack.enter_context(patch("installer.steps.claude_files.is_claude_installed", return_value=True))
        stack.enter_context(patch("installer.steps.pilot_files.Path.home", return_value=home_dir))
        stack.enter_context(patch("installer.steps.claude_files.Path.home", return_value=home_dir))
        PilotFilesStep().run(ctx)
        ClaudeFilesStep().run(ctx)


class TestCustomConfigDirIsolation:
    def test_personal_profile_is_untouched(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        home = tmp_path / "home"
        home.mkdir()
        _seed_source(tmp_path)

        # A populated personal profile that must survive byte-identical.
        personal = home / ".claude"
        (personal / "rules").mkdir(parents=True)
        (personal / "rules" / "my-own-rule.md").write_text("personal rule\n")
        (personal / "settings.json").write_text(json.dumps({"model": "opus"}, indent=2))
        personal_app_config = home / ".claude.json"
        personal_app_config.write_text(json.dumps({"oauthAccount": "personal"}, indent=2))

        before_tree = _snapshot(personal)
        before_app = _hash_file(personal_app_config)

        work = home / ".claude_work"
        work.mkdir()
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(work))

        _install(tmp_path, home)

        assert _snapshot(personal) == before_tree, "personal ~/.claude tree changed"
        assert _hash_file(personal_app_config) == before_app, "personal ~/.claude.json changed"

    def test_custom_profile_is_populated(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Guards against the isolation test passing by installing nothing at all."""
        home = tmp_path / "home"
        home.mkdir()
        _seed_source(tmp_path)
        work = home / ".claude_work"
        work.mkdir()
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(work))

        _install(tmp_path, home)

        assert (work / "settings.json").exists()
        assert (work / "rules" / "testing.md").exists()
        assert (work / "agents" / "spec-review.md").exists()
        assert (work / ".pilot-manifest.json").exists()

        # The app config must exist INSIDE the custom profile, never at the home
        # root. Only the mcpServers block is asserted here: a later install step
        # rewrites this file with Claude Code's own app defaults, so exact
        # contents are not stable end-to-end. The full three-way merge (including
        # the pilot/claude.json template keys) is covered by the unit tests in
        # test_claude_files.py::TestMergeAppConfig.
        app_config = work / ".claude.json"
        assert app_config.exists(), "app config did not land in the custom profile"
        assert not (home / ".claude.json").exists(), "app config leaked to the home root"
        merged = json.loads(app_config.read_text())
        assert merged["mcpServers"]["context7"]["command"] == "npx"

    def test_default_profile_unchanged_when_env_unset(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """The whole change must be a strict no-op for existing users."""
        home = tmp_path / "home"
        home.mkdir()
        _seed_source(tmp_path)
        monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)

        _install(tmp_path, home)

        claude = home / ".claude"
        assert (claude / "settings.json").exists()
        assert (claude / "rules" / "testing.md").exists()
        # App config stays at the home root, NOT ~/.claude/.claude.json.
        assert (home / ".claude.json").exists()
        assert not (claude / ".claude.json").exists()

    def test_symlinked_config_dir_resolves_to_target(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        home = tmp_path / "home"
        home.mkdir()
        _seed_source(tmp_path)

        real = tmp_path / "real_profile"
        real.mkdir()
        link = home / ".claude_link"
        link.symlink_to(real, target_is_directory=True)
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(link))

        _install(tmp_path, home)

        assert (real / "settings.json").exists(), "assets did not land in the symlink target"
        assert not (home / ".claude").exists(), "personal profile was created"

    def test_relative_config_dir_installs_nothing_anywhere(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fail closed end-to-end: neither ~/.claude nor the relative path is written."""
        home = tmp_path / "home"
        home.mkdir()
        _seed_source(tmp_path)
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", "relative/path")

        with pytest.raises(ValueError, match="CLAUDE_CONFIG_DIR"):
            _install(tmp_path, home)

        assert not (home / ".claude" / "settings.json").exists()
        assert not (home / ".claude.json").exists()
