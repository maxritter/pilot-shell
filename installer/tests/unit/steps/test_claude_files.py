"""Tests for pilot files installation step."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch


class TestPatchClaudePaths:
    """Test the patch_claude_paths function."""

    def test_patch_claude_paths_leaves_plugin_path_unchanged(self):
        """patch_claude_paths does NOT expand ~/.claude/pilot (hooks use ${CLAUDE_PLUGIN_ROOT})."""
        from installer.steps.claude_files import patch_claude_paths

        content = '{"command": "~/.claude/pilot/scripts/worker.cjs"}'
        result = patch_claude_paths(content)

        assert content == result

    def test_patch_claude_paths_expands_tilde_bin_path(self):
        """patch_claude_paths expands ~/.pilot/bin/ to absolute path."""
        from pathlib import Path as P

        from installer.steps.claude_files import patch_claude_paths

        content = '{"command": "~/.pilot/bin/pilot statusline"}'
        result = patch_claude_paths(content)

        expected_bin = str(P.home() / ".pilot" / "bin") + "/"
        assert '"~/.pilot/bin/' not in result
        assert expected_bin in result

    def test_patch_claude_paths_only_expands_bin_path(self):
        """patch_claude_paths only expands ~/.pilot/bin/, not ~/.claude/pilot."""
        from pathlib import Path as P

        from installer.steps.claude_files import patch_claude_paths

        content = """{
            "command": "~/.claude/pilot/scripts/worker.cjs",
            "statusLine": {"command": "~/.pilot/bin/pilot statusline"}
        }"""
        result = patch_claude_paths(content)

        expected_bin = str(P.home() / ".pilot" / "bin") + "/"
        assert expected_bin in result
        assert "~/.claude/pilot" in result

    def test_patch_claude_paths_preserves_non_tilde_paths(self):
        """patch_claude_paths leaves non-tilde paths unchanged."""
        from installer.steps.claude_files import patch_claude_paths

        content = '{"path": "/usr/local/bin/something"}'
        result = patch_claude_paths(content)

        assert result == content


class TestProcessSettings:
    """Test the process_settings function."""

    def test_process_settings_round_trips_json(self):
        """process_settings parses and re-serializes JSON with consistent formatting."""
        from installer.steps.claude_files import process_settings

        settings = {"hooks": {"PostToolUse": [{"matcher": "Write", "hooks": []}]}, "model": "opus"}
        result = process_settings(json.dumps(settings))
        parsed = json.loads(result)

        assert parsed == settings
        assert result.endswith("\n")

    def test_process_settings_preserves_all_hooks(self):
        """process_settings preserves all language hooks without filtering."""
        from installer.steps.claude_files import process_settings

        python_hook = "uv run --no-project python ~/.claude/pilot/hooks/file_checker_python.py"
        ts_hook = "uv run --no-project python ~/.claude/pilot/hooks/file_checker_ts.py"
        go_hook = "uv run --no-project python ~/.claude/pilot/hooks/file_checker_go.py"
        settings = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Write|Edit|MultiEdit",
                        "hooks": [
                            {"type": "command", "command": python_hook},
                            {"type": "command", "command": ts_hook},
                            {"type": "command", "command": go_hook},
                        ],
                    }
                ]
            }
        }

        result = process_settings(json.dumps(settings))
        parsed = json.loads(result)

        hooks = parsed["hooks"]["PostToolUse"][0]["hooks"]
        assert len(hooks) == 3


class TestClaudeFilesStep:
    """Test ClaudeFilesStep class."""

    def test_claude_files_step_has_correct_name(self):
        """ClaudeFilesStep has name 'claude_files'."""
        from installer.steps.claude_files import ClaudeFilesStep

        step = ClaudeFilesStep()
        assert step.name == "claude_files"

    def test_claude_files_check_returns_false_when_empty(self):
        """ClaudeFilesStep.check returns False when no files installed."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = InstallContext(
                project_dir=Path(tmpdir),
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir),
            )
            assert step.check(ctx) is False

    def test_claude_files_run_installs_files(self):
        """ClaudeFilesStep.run installs pilot files."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            source_pilot = Path(tmpdir) / "source" / "pilot"
            source_pilot.mkdir(parents=True)
            (source_pilot / "test.md").write_text("test content")
            (source_pilot / "rules").mkdir()
            (source_pilot / "rules" / "rule.md").write_text("rule content")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir) / "source",
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            assert (home_dir / ".claude" / "rules" / "rule.md").exists()

    def test_claude_files_installs_settings(self):
        """ClaudeFilesStep installs settings to ~/.claude/settings.json."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            source_pilot = Path(tmpdir) / "source" / "pilot"
            source_pilot.mkdir(parents=True)
            (source_pilot / "settings.json").write_text('{"hooks": {}}')

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir) / "source",
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            assert (home_dir / ".claude" / "settings.json").exists()
            assert not (dest_dir / ".claude" / "settings.local.json").exists()


class TestClaudeFilesCustomRulesPreservation:
    """Test that standard rules from repo are installed and project rules preserved."""

    def test_standard_rules_installed_and_project_rules_preserved(self):
        """ClaudeFilesStep installs repo standard rules to ~/.claude and preserves project rules."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            source_pilot = Path(tmpdir) / "source" / "pilot"
            source_rules = source_pilot / "rules"
            source_rules.mkdir(parents=True)

            (source_rules / "python-rules.md").write_text("python rules from repo")
            (source_rules / "standard-rule.md").write_text("standard rule")

            dest_dir = Path(tmpdir) / "dest"
            dest_claude = dest_dir / ".claude"
            dest_rules = dest_claude / "rules"
            dest_rules.mkdir(parents=True)
            (dest_rules / "my-project-rules.md").write_text("USER PROJECT RULES - PRESERVED")

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir) / "source",
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            assert (dest_rules / "my-project-rules.md").exists()
            assert (dest_rules / "my-project-rules.md").read_text() == "USER PROJECT RULES - PRESERVED"

            global_rules = home_dir / ".claude" / "rules"
            assert (global_rules / "python-rules.md").exists()
            assert (global_rules / "python-rules.md").read_text() == "python rules from repo"
            assert (global_rules / "standard-rule.md").exists()

    def test_pycache_files_not_copied(self):
        """ClaudeFilesStep skips __pycache__ directories and .pyc files."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            source_pilot = Path(tmpdir) / "source" / "pilot"
            source_rules = source_pilot / "rules"
            source_pycache = source_rules / "__pycache__"
            source_pycache.mkdir(parents=True)
            (source_rules / "test-rule.md").write_text("# rule")
            (source_pycache / "something.cpython-312.pyc").write_text("bytecode")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir) / "source",
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            global_rules = home_dir / ".claude" / "rules"
            assert (global_rules / "test-rule.md").exists()
            assert not (global_rules / "__pycache__").exists()


class TestDirectoryClearing:
    """Test directory clearing behavior in local and normal mode."""

    def test_clears_managed_files_preserves_user_files(self):
        """Pilot-managed rules are removed on update; user-created files are preserved."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            old_global_rules = home_dir / ".claude" / "rules"
            old_global_rules.mkdir(parents=True)
            (old_global_rules / "old-rule.md").write_text("old Pilot rule to be removed")
            (old_global_rules / "my-custom-rule.md").write_text("user-created rule")

            manifest_path = home_dir / ".claude" / ".pilot-manifest.json"
            manifest_path.write_text(json.dumps({"files": ["rules/old-rule.md"]}, indent=2))

            source_dir = Path(tmpdir) / "source"
            source_pilot = source_dir / "pilot"
            source_rules = source_pilot / "rules"
            source_rules.mkdir(parents=True)
            (source_rules / "new-rule.md").write_text("new rule content")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=source_dir,
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            global_rules = home_dir / ".claude" / "rules"
            assert (global_rules / "new-rule.md").exists()
            assert (global_rules / "new-rule.md").read_text() == "new rule content"
            assert not (global_rules / "old-rule.md").exists()
            assert (global_rules / "my-custom-rule.md").exists()
            assert (global_rules / "my-custom-rule.md").read_text() == "user-created rule"

    def test_legacy_upgrade_seeds_manifest_and_cleans_old_files(self):
        """Pre-manifest upgrade: old Pilot files are seeded into manifest and cleaned up."""
        from installer.context import InstallContext
        from installer.steps.claude_files import PILOT_MANIFEST_FILE, ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            old_global_rules = home_dir / ".claude" / "rules"
            old_global_rules.mkdir(parents=True)
            (old_global_rules / "old-pilot-rule.md").write_text("old Pilot rule")
            (old_global_rules / "another-old-rule.md").write_text("another old rule")

            old_global_cmds = home_dir / ".claude" / "commands"
            old_global_cmds.mkdir(parents=True)
            (old_global_cmds / "old-cmd.md").write_text("old Pilot command")

            manifest_path = home_dir / ".claude" / PILOT_MANIFEST_FILE
            assert not manifest_path.exists()

            source_dir = Path(tmpdir) / "source"
            source_pilot = source_dir / "pilot"
            source_rules = source_pilot / "rules"
            source_rules.mkdir(parents=True)
            (source_rules / "new-rule.md").write_text("new rule content")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=source_dir,
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            global_rules = home_dir / ".claude" / "rules"
            assert (global_rules / "new-rule.md").exists()
            assert not (global_rules / "old-pilot-rule.md").exists()
            assert not (global_rules / "another-old-rule.md").exists()
            assert not (old_global_cmds / "old-cmd.md").exists()
            assert manifest_path.exists()

    def test_deprecated_pilot_skills_cleaned_from_home(self):
        """Regression for Sweep-Manifest: skills Pilot historically shipped but
        no longer ships (e.g., `notify`, `skill-build`) are removed from
        ~/.claude/skills/ by the explicit deprecated-name cleanup. User
        skills with non-deprecated names are preserved untouched."""
        from installer.steps.claude_files import ClaudeFilesStep

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_claude = home_dir / ".claude"

            skills_dir = home_claude / "skills"
            skills_dir.mkdir(parents=True)
            # Deprecated Pilot skills — must be removed.
            (skills_dir / "notify").mkdir()
            (skills_dir / "notify" / "SKILL.md").write_text("legacy notify")
            (skills_dir / "skill-build").mkdir()
            (skills_dir / "skill-build" / "SKILL.md").write_text("legacy skill-build")
            # User skill — must survive.
            (skills_dir / "my-custom-skill").mkdir()
            (skills_dir / "my-custom-skill" / "SKILL.md").write_text("user custom")

            step._cleanup_deprecated_pilot_skills_in_home(home_claude)  # type: ignore[attr-defined]

            assert not (skills_dir / "notify").exists()
            assert not (skills_dir / "skill-build").exists()
            assert (skills_dir / "my-custom-skill" / "SKILL.md").read_text() == "user custom"

    def test_deprecated_cleanup_idempotent_when_dirs_missing(self):
        """No-op when ~/.claude/skills/ does not exist (fresh install path)."""
        from installer.steps.claude_files import ClaudeFilesStep

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_claude = home_dir / ".claude"
            home_claude.mkdir(parents=True)
            # Should not raise; nothing to clean.
            step._cleanup_deprecated_pilot_skills_in_home(home_claude)  # type: ignore[attr-defined]

    def test_skips_clearing_when_source_equals_destination(self):
        """Directories are NOT cleared when source == destination (same dir)."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            pilot_dir = Path(tmpdir) / "pilot"
            rules_dir = pilot_dir / "rules"
            rules_dir.mkdir(parents=True)
            (rules_dir / "existing-rule.md").write_text("existing rule content")

            ctx = InstallContext(
                project_dir=Path(tmpdir),
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir),
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            assert (home_dir / ".claude" / "rules" / "existing-rule.md").exists()

    def test_stale_managed_rules_removed_when_source_equals_destination(self):
        """Stale Pilot-managed rules are removed even when source == destination."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            global_rules = home_dir / ".claude" / "rules"
            global_rules.mkdir(parents=True)
            (global_rules / "old-deleted-rule.md").write_text("stale rule from previous install")

            manifest_path = home_dir / ".claude" / ".pilot-manifest.json"
            manifest_path.write_text(json.dumps({"files": ["rules/old-deleted-rule.md"]}, indent=2))

            pilot_dir = Path(tmpdir) / "pilot"
            rules_dir = pilot_dir / "rules"
            rules_dir.mkdir(parents=True)
            (rules_dir / "current-rule.md").write_text("current rule content")

            ctx = InstallContext(
                project_dir=Path(tmpdir),
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir),
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            assert (global_rules / "current-rule.md").exists()
            assert not (global_rules / "old-deleted-rule.md").exists()

    def test_project_rules_never_cleared(self):
        """Project rules directory is NEVER cleared, only global standard rules."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            source_dir = Path(tmpdir) / "source"
            source_pilot = source_dir / "pilot"
            source_rules = source_pilot / "rules"
            source_rules.mkdir(parents=True)
            (source_rules / "new-rule.md").write_text("new standard rule")

            dest_dir = Path(tmpdir) / "dest"
            dest_claude = dest_dir / ".claude"
            dest_project_rules = dest_claude / "rules"
            dest_project_rules.mkdir(parents=True)
            (dest_project_rules / "my-project.md").write_text("USER PROJECT RULE")

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=source_dir,
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            assert (dest_project_rules / "my-project.md").exists()
            assert (dest_project_rules / "my-project.md").read_text() == "USER PROJECT RULE"

            global_rules = home_dir / ".claude" / "rules"
            assert (global_rules / "new-rule.md").exists()

    def test_skills_installed_to_root_level(self):
        """Skills from pilot/skills/ are installed to ~/.claude/skills/."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            source_dir = Path(tmpdir) / "source"
            source_pilot = source_dir / "pilot"
            spec_dir = source_pilot / "skills" / "spec"
            spec_dir.mkdir(parents=True)
            (spec_dir / "SKILL.md").write_text("new spec skill")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=source_dir,
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            global_skills = home_dir / ".claude" / "skills"
            assert (global_skills / "spec" / "SKILL.md").exists()
            assert (global_skills / "spec" / "SKILL.md").read_text() == "new spec skill"

    def test_pilot_plugin_folder_is_installed(self):
        """ClaudeFilesStep installs pilot plugin folder to ~/.claude/pilot/ (global)."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            source_dir = Path(tmpdir) / "source"
            source_pilot = source_dir / "pilot"
            source_pilot.mkdir(parents=True)
            (source_pilot / "package.json").write_text('{"name": "pilot"}')
            (source_pilot / "plugin.json").write_text('{"version": "1.0"}')
            (source_pilot / ".mcp.json").write_text('{"servers": []}')
            (source_pilot / ".lsp.json").write_text('{"python": {}}')
            (source_pilot / "scripts").mkdir()
            (source_pilot / "scripts" / "mcp-server.cjs").write_text("// mcp server")
            (source_pilot / "hooks").mkdir()
            (source_pilot / "hooks" / "hook.py").write_text("# hook")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=source_dir,
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            global_pilot = home_dir / ".claude" / "pilot"
            assert (global_pilot / "package.json").exists()
            # plugin.json and .lsp.json are SKIPPED by the installer post-migration:
            # Pilot is no longer registered as a Claude Code plugin; LSP moved to
            # the Piebald-AI/claude-code-lsps marketplace. See plan Task 3.
            assert not (global_pilot / "plugin.json").exists()
            assert (global_pilot / ".mcp.json").exists()
            assert not (global_pilot / ".lsp.json").exists()
            assert (global_pilot / "scripts" / "mcp-server.cjs").exists()
            assert (global_pilot / "hooks" / "hook.py").exists()


class TestMergeAppConfig:
    """Test merging pilot/claude.json app preferences into ~/.claude.json."""

    def test_merge_sets_new_keys(self):
        """Keys in source that don't exist in target are added."""
        from installer.steps.settings_merge import merge_app_config

        target = {"numStartups": 500, "oauthAccount": {"email": "x"}}
        source = {"autoCompactEnabled": True, "theme": "dark"}

        result = merge_app_config(target, source)

        assert result is not None
        assert result["autoCompactEnabled"] is True
        assert result["theme"] == "dark"
        assert result["numStartups"] == 500
        assert result["oauthAccount"] == {"email": "x"}

    def test_merge_updates_existing_keys(self):
        """Keys in source that exist in target are updated to source value."""
        from installer.steps.settings_merge import merge_app_config

        target = {"autoCompactEnabled": False, "verbose": False}
        source = {"autoCompactEnabled": True, "verbose": True}

        result = merge_app_config(target, source)

        assert result is not None
        assert result["autoCompactEnabled"] is True
        assert result["verbose"] is True

    def test_merge_preserves_all_other_keys(self):
        """Keys not in source are never touched."""
        from installer.steps.settings_merge import merge_app_config

        target = {
            "numStartups": 500,
            "oauthAccount": {"email": "x"},
            "projects": {"path": {}},
            "skillUsage": {"spec": 10},
            "cachedGrowthBookFeatures": {"flag": True},
        }
        source = {"theme": "dark"}

        result = merge_app_config(target, source)

        assert result is not None
        assert result["numStartups"] == 500
        assert result["oauthAccount"] == {"email": "x"}
        assert result["projects"] == {"path": {}}
        assert result["skillUsage"] == {"spec": 10}
        assert result["cachedGrowthBookFeatures"] == {"flag": True}

    def test_merge_returns_none_when_no_changes(self):
        """Returns None when all source keys already match target values."""
        from installer.steps.settings_merge import merge_app_config

        target = {"autoCompactEnabled": True, "theme": "dark", "numStartups": 500}
        source = {"autoCompactEnabled": True, "theme": "dark"}

        result = merge_app_config(target, source)

        assert result is None

    def test_integration_merges_claude_json(self):
        """Installer merges pilot/claude.json preferences into ~/.claude.json."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()
            (home_dir / ".claude").mkdir(parents=True)

            claude_json_path = home_dir / ".claude.json"
            claude_json_path.write_text(
                json.dumps(
                    {
                        "numStartups": 500,
                        "autoCompactEnabled": False,
                        "oauthAccount": {"email": "user@test.com"},
                        "projects": {},
                    },
                    indent=2,
                )
                + "\n"
            )

            source_pilot = Path(tmpdir) / "source" / "pilot"
            source_pilot.mkdir(parents=True)
            (source_pilot / "settings.json").write_text(
                json.dumps({"env": {"X": "1"}, "permissions": {"defaultMode": "bypassPermissions"}}, indent=2)
            )
            (source_pilot / "claude.json").write_text(
                json.dumps(
                    {
                        "autoCompactEnabled": True,
                        "theme": "dark",
                        "verbose": True,
                    },
                    indent=2,
                )
            )

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir) / "source",
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            patched = json.loads(claude_json_path.read_text())

            assert patched["autoCompactEnabled"] is True
            assert patched["theme"] == "dark"
            assert patched["verbose"] is True
            assert patched["numStartups"] == 500
            assert patched["oauthAccount"] == {"email": "user@test.com"}
            assert patched["projects"] == {}

    def test_creates_claude_json_if_missing(self):
        """Installer creates ~/.claude.json if it doesn't exist."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()
            (home_dir / ".claude").mkdir(parents=True)

            source_pilot = Path(tmpdir) / "source" / "pilot"
            source_pilot.mkdir(parents=True)
            (source_pilot / "settings.json").write_text(
                json.dumps({"env": {"X": "1"}, "permissions": {"defaultMode": "bypassPermissions"}}, indent=2)
            )
            (source_pilot / "claude.json").write_text(
                json.dumps({"autoCompactEnabled": True, "theme": "dark"}, indent=2)
            )

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir) / "source",
            )

            claude_json_path = home_dir / ".claude.json"
            assert not claude_json_path.exists()

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            assert claude_json_path.exists()
            patched = json.loads(claude_json_path.read_text())
            assert patched["autoCompactEnabled"] is True
            assert patched["theme"] == "dark"

    def test_no_crash_when_claude_json_template_missing(self):
        """Installer skips merge when pilot/claude.json was not installed."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()
            (home_dir / ".claude").mkdir(parents=True)

            source_pilot = Path(tmpdir) / "source" / "pilot"
            source_pilot.mkdir(parents=True)
            (source_pilot / "settings.json").write_text(
                json.dumps({"env": {"X": "1"}, "permissions": {"defaultMode": "bypassPermissions"}}, indent=2)
            )

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path(tmpdir) / "source",
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            assert not (home_dir / ".claude.json").exists()


class TestMergeSettings:
    """Tests for three-way settings merge."""

    def test_first_install_uses_incoming(self):
        """Without baseline or current, incoming settings are used as-is."""
        from installer.steps.settings_merge import merge_settings

        incoming = {
            "env": {"A": "1", "B": "2"},
            "permissions": {"defaultMode": "bypassPermissions"},
            "spinnerTipsEnabled": False,
        }
        result = merge_settings(None, {}, incoming)

        assert result["env"] == {"A": "1", "B": "2"}
        assert result["permissions"]["defaultMode"] == "bypassPermissions"
        assert result["spinnerTipsEnabled"] is False

    def test_preserves_user_changed_env_var(self):
        """If user changed an env var value, Pilot doesn't overwrite it."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"env": {"DISABLE_TELEMETRY": "true", "ENABLE_LSP_TOOL": "true"}}
        current = {"env": {"DISABLE_TELEMETRY": "false", "ENABLE_LSP_TOOL": "true"}}
        incoming = {"env": {"DISABLE_TELEMETRY": "true", "ENABLE_LSP_TOOL": "true", "NEW_VAR": "1"}}

        result = merge_settings(baseline, current, incoming)

        assert result["env"]["DISABLE_TELEMETRY"] == "false"
        assert result["env"]["NEW_VAR"] == "1"
        assert result["env"]["ENABLE_LSP_TOOL"] == "true"

    def test_preserves_user_only_keys(self):
        """Keys the user added that Pilot doesn't manage are preserved."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"spinnerTipsEnabled": False}
        current = {"spinnerTipsEnabled": False, "myCustomKey": "hello"}
        incoming = {"spinnerTipsEnabled": False}

        result = merge_settings(baseline, current, incoming)

        assert result["myCustomKey"] == "hello"

    def test_adds_new_pilot_keys(self):
        """New keys from Pilot are added on update."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"env": {"A": "1"}}
        current = {"env": {"A": "1"}}
        incoming = {"env": {"A": "1", "B": "2"}, "newFeature": True}

        result = merge_settings(baseline, current, incoming)

        assert result["env"]["B"] == "2"
        assert result["newFeature"] is True

    def test_updates_unchanged_scalars(self):
        """Scalar values the user didn't touch get updated to new Pilot values."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"alwaysThinkingEnabled": False}
        current = {"alwaysThinkingEnabled": False}
        incoming = {"alwaysThinkingEnabled": True}

        result = merge_settings(baseline, current, incoming)

        assert result["alwaysThinkingEnabled"] is True

    def test_preserves_user_changed_scalar(self):
        """Scalar values the user changed from baseline are kept."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"alwaysThinkingEnabled": True}
        current = {"alwaysThinkingEnabled": False}
        incoming = {"alwaysThinkingEnabled": True}

        result = merge_settings(baseline, current, incoming)

        assert result["alwaysThinkingEnabled"] is False

    def test_preserves_user_added_env_vars(self):
        """User-added env vars not in Pilot's set are preserved."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"env": {"A": "1"}}
        current = {"env": {"A": "1", "MY_CUSTOM_VAR": "yes"}}
        incoming = {"env": {"A": "1"}}

        result = merge_settings(baseline, current, incoming)

        assert result["env"]["MY_CUSTOM_VAR"] == "yes"

    def test_pilot_removed_key_dropped_when_user_unchanged(self):
        """Key Pilot previously managed and user didn't change is removed when Pilot drops it."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"spinnerTipsEnabled": False, "model": "sonnet"}
        current = {"spinnerTipsEnabled": False, "model": "sonnet"}
        incoming = {"spinnerTipsOverride": {"tips": ["tip1"], "excludeDefault": True}, "model": "sonnet"}

        result = merge_settings(baseline, current, incoming)

        assert "spinnerTipsEnabled" not in result
        assert result["spinnerTipsOverride"] == {"tips": ["tip1"], "excludeDefault": True}

    def test_pilot_removed_key_preserved_when_user_changed(self):
        """Key Pilot managed but user changed is preserved even when Pilot removes it."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"spinnerTipsEnabled": False}
        current = {"spinnerTipsEnabled": True}
        incoming = {"spinnerTipsOverride": {"tips": ["tip1"], "excludeDefault": True}}

        result = merge_settings(baseline, current, incoming)

        assert result["spinnerTipsEnabled"] is True
        assert result["spinnerTipsOverride"] == {"tips": ["tip1"], "excludeDefault": True}

    def test_user_added_key_not_in_baseline_preserved_when_not_in_incoming(self):
        """User-added keys (never in Pilot baseline) are always preserved."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"model": "sonnet"}
        current = {"model": "sonnet", "myCustomKey": "hello"}
        incoming = {"model": "opus"}

        result = merge_settings(baseline, current, incoming)

        assert result["myCustomKey"] == "hello"
        assert result["model"] == "opus"


class TestMergeAppConfigWithBaseline:
    """Tests for merge_app_config with baseline parameter."""

    def test_baseline_preserves_user_changes(self):
        """User changes to ~/.claude.json are preserved when baseline exists."""
        from installer.steps.settings_merge import merge_app_config

        target = {"autoCompactEnabled": False, "verbose": True}
        source = {"autoCompactEnabled": True, "verbose": True, "newKey": "value"}
        baseline = {"autoCompactEnabled": True, "verbose": True}

        result = merge_app_config(target, source, baseline)

        assert result is not None
        assert result["autoCompactEnabled"] is False
        assert result["newKey"] == "value"
        assert result["verbose"] is True

    def test_no_baseline_overwrites_like_before(self):
        """Without baseline (first install), all source keys are applied."""
        from installer.steps.settings_merge import merge_app_config

        target = {"autoCompactEnabled": False}
        source = {"autoCompactEnabled": True}

        result = merge_app_config(target, source, None)

        assert result is not None
        assert result["autoCompactEnabled"] is True


class TestMergePermissions:
    """Tests for permissions dict merge (scalar keys only, no allow/deny/ask lists)."""

    def test_user_default_mode_preserved_through_update(self):
        """User's defaultMode: bypassPermissions survives a Pilot update."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"permissions": {"defaultMode": "bypassPermissions"}}
        current = {"permissions": {"defaultMode": "bypassPermissions"}}
        incoming = {"permissions": {"defaultMode": "bypassPermissions"}}

        result = merge_settings(baseline, current, incoming)

        assert result["permissions"]["defaultMode"] == "bypassPermissions"

    def test_default_mode_in_incoming_is_applied(self):
        """defaultMode from Pilot's incoming settings is applied on first install."""
        from installer.steps.settings_merge import merge_settings

        incoming = {"permissions": {"defaultMode": "bypassPermissions"}}
        result = merge_settings(None, {}, incoming)

        assert result["permissions"]["defaultMode"] == "bypassPermissions"

    def test_user_changed_default_mode_preserved(self):
        """User's manually changed defaultMode is preserved even if Pilot updates it."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"permissions": {"defaultMode": "bypassPermissions"}}
        current = {"permissions": {"defaultMode": "default"}}
        incoming = {"permissions": {"defaultMode": "bypassPermissions"}}

        result = merge_settings(baseline, current, incoming)

        assert result["permissions"]["defaultMode"] == "default"

    def test_user_added_custom_key_preserved(self):
        """User-added keys in permissions survive a Pilot update."""
        from installer.steps.settings_merge import merge_settings

        baseline = {"permissions": {"defaultMode": "bypassPermissions"}}
        current = {"permissions": {"defaultMode": "bypassPermissions", "customKey": "userValue"}}
        incoming = {"permissions": {"defaultMode": "bypassPermissions"}}

        result = merge_settings(baseline, current, incoming)

        assert result["permissions"]["defaultMode"] == "bypassPermissions"
        assert result["permissions"]["customKey"] == "userValue"


class TestResolveRepoUrl:
    """Tests for _resolve_repo_url method."""

    def test_resolve_repo_url_returns_correct_url(self):
        """_resolve_repo_url returns the repository URL."""
        from installer.steps.claude_files import ClaudeFilesStep

        step = ClaudeFilesStep()
        result = step._resolve_repo_url("v5.0.0")

        assert result == "https://github.com/maxritter/pilot-shell"


class TestSkillsDeployment:
    """Test that skills from pilot/skills/ are deployed to ~/.claude/pilot/skills/ via pilot_plugin."""

    def test_all_skills_categorized_as_skills(self):
        """All files in pilot/skills/ are categorized as 'skills' for root-level installation."""
        from installer.steps.claude_files import _categorize_file

        assert _categorize_file("pilot/skills/spec/SKILL.md") == "skills"
        assert _categorize_file("pilot/skills/setup-rules/SKILL.md") == "skills"
        assert _categorize_file("pilot/skills/mcp-servers/skill.md") == "skills"

    def test_benchmark_skill_nested_files_categorized_as_skills(self):
        """The benchmark skill ships scripts/ and agents/ subdirs.

        Regression guard: ensure the categorizer treats these as skill content, not
        as project-level Python source or rules.
        """
        from installer.steps.claude_files import _categorize_file

        assert _categorize_file("pilot/skills/benchmark/SKILL.md") == "skills"
        assert _categorize_file("pilot/skills/benchmark/manifest.json") == "skills"
        assert _categorize_file("pilot/skills/benchmark/orchestrator.md") == "skills"
        assert _categorize_file("pilot/skills/benchmark/steps/01-intake.md") == "skills"
        assert _categorize_file("pilot/skills/benchmark/scripts/runner.py") == "skills"
        assert _categorize_file("pilot/skills/benchmark/scripts/utils.py") == "skills"
        assert _categorize_file("pilot/skills/benchmark/agents/grader.md") == "skills"

    def test_skills_deployed_to_root_skills_dir(self):
        """Skills are installed to ~/.claude/skills/<name>/ (root level, not plugin)."""
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            source_dir = Path(tmpdir) / "source"
            source_pilot = source_dir / "pilot"
            skill_dir = source_pilot / "skills" / "mcp-servers"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: mcp-servers\n---\n# MCP Servers")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=source_dir,
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            expected_path = home_dir / ".claude" / "skills" / "mcp-servers" / "SKILL.md"
            assert expected_path.exists(), f"Skill not at {expected_path}"
            assert "MCP Servers" in expected_path.read_text()


class TestCommandsToSkillsMigration:
    """Test migration from legacy commands/ to skills/ format."""

    def test_old_commands_cleaned_up_during_migration(self):
        """Legacy commands in manifest are removed when upgrading to skills format."""
        from installer.context import InstallContext
        from installer.steps.claude_files import PILOT_MANIFEST_FILE, ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            # Old commands exist from previous install
            old_commands = home_dir / ".claude" / "commands"
            old_commands.mkdir(parents=True)
            (old_commands / "spec.md").write_text("old spec command")
            (old_commands / "setup-rules.md").write_text("old setup-rules command")

            # Old manifest tracks commands
            manifest_path = home_dir / ".claude" / PILOT_MANIFEST_FILE
            manifest_path.write_text(json.dumps({"files": ["commands/spec.md", "commands/setup-rules.md"]}, indent=2))

            # Source now has skill folders
            source_dir = Path(tmpdir) / "source"
            spec_skill = source_dir / "pilot" / "skills" / "spec"
            spec_skill.mkdir(parents=True)
            (spec_skill / "SKILL.md").write_text("new spec skill")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=source_dir,
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            # Old commands removed
            assert not (old_commands / "spec.md").exists()
            assert not (old_commands / "setup-rules.md").exists()

            # New skill installed
            global_skills = home_dir / ".claude" / "skills"
            assert (global_skills / "spec" / "SKILL.md").exists()
            assert (global_skills / "spec" / "SKILL.md").read_text() == "new spec skill"

            # Manifest updated with skills entries
            manifest = json.loads(manifest_path.read_text())
            assert "skills/spec/SKILL.md" in manifest["files"]
            assert "commands/spec.md" not in manifest["files"]

    def test_user_commands_preserved_during_migration(self):
        """User-created commands not in manifest are preserved during migration."""
        from installer.context import InstallContext
        from installer.steps.claude_files import PILOT_MANIFEST_FILE, ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            # Old Pilot command + user command
            old_commands = home_dir / ".claude" / "commands"
            old_commands.mkdir(parents=True)
            (old_commands / "spec.md").write_text("old spec command")
            (old_commands / "my-custom-cmd.md").write_text("user custom command")

            # Manifest only tracks Pilot files
            manifest_path = home_dir / ".claude" / PILOT_MANIFEST_FILE
            manifest_path.write_text(json.dumps({"files": ["commands/spec.md"]}, indent=2))

            source_dir = Path(tmpdir) / "source"
            spec_skill = source_dir / "pilot" / "skills" / "spec"
            spec_skill.mkdir(parents=True)
            (spec_skill / "SKILL.md").write_text("new spec skill")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=source_dir,
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            # User command preserved
            assert (old_commands / "my-custom-cmd.md").exists()
            assert (old_commands / "my-custom-cmd.md").read_text() == "user custom command"

            # Pilot command removed
            assert not (old_commands / "spec.md").exists()

    def test_user_skills_not_seeded_into_manifest_on_legacy_upgrade(self):
        """User-owned global skills are NOT seeded into manifest during legacy upgrade."""
        from installer.context import InstallContext
        from installer.steps.claude_files import PILOT_MANIFEST_FILE, ClaudeFilesStep
        from installer.ui import Console

        step = ClaudeFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir) / "home"
            home_dir.mkdir()

            # Pre-existing user skill + Pilot skill (no manifest = legacy)
            skills_dir = home_dir / ".claude" / "skills"
            user_skill = skills_dir / "my-custom-skill"
            user_skill.mkdir(parents=True)
            (user_skill / "SKILL.md").write_text("user custom skill")

            pilot_skill = skills_dir / "spec"
            pilot_skill.mkdir(parents=True)
            (pilot_skill / "SKILL.md").write_text("old pilot spec skill")

            manifest_path = home_dir / ".claude" / PILOT_MANIFEST_FILE
            assert not manifest_path.exists()

            # Source has new spec skill
            source_dir = Path(tmpdir) / "source"
            spec_src = source_dir / "pilot" / "skills" / "spec"
            spec_src.mkdir(parents=True)
            (spec_src / "SKILL.md").write_text("new spec skill")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()

            ctx = InstallContext(
                project_dir=dest_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=source_dir,
            )

            with patch("installer.steps.claude_files.Path.home", return_value=home_dir):
                step.run(ctx)

            # User skill preserved — not seeded, not deleted
            assert (user_skill / "SKILL.md").exists()
            assert (user_skill / "SKILL.md").read_text() == "user custom skill"

            # Manifest does NOT contain user skill
            manifest = json.loads(manifest_path.read_text())
            assert not any("my-custom-skill" in f for f in manifest["files"])


class TestBotSkillsCategory:
    """Test that bot skills are categorized correctly."""

    def test_bot_skills_categorized_as_skills(self):
        from installer.steps.claude_files import _categorize_file

        assert _categorize_file("pilot/skills/bot-boot/SKILL.md") == "skills"
        assert _categorize_file("pilot/skills/bot-heartbeat/SKILL.md") == "skills"
        assert _categorize_file("pilot/skills/bot-jobs/SKILL.md") == "skills"
        assert _categorize_file("pilot/skills/bot-channel-task/SKILL.md") == "skills"
        assert _categorize_file("pilot/skills/bot-defaults/SKILL.md") == "skills"


class TestReapplyCustomization:
    """Tests for _reapply_customization in ClaudeFilesStep."""

    def test_calls_pilot_binary_when_customization_configured(self, tmp_path):
        import json
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        config_path = tmp_path / ".pilot" / "config.json"
        config_path.parent.mkdir(parents=True)
        config_path.write_text(
            json.dumps({"customization": {"source": "https://github.com/org/repo.git", "branch": "main"}})
        )

        pilot_bin = tmp_path / ".pilot" / "bin" / "pilot"
        pilot_bin.parent.mkdir(parents=True)
        pilot_bin.touch()

        step = ClaudeFilesStep()
        ui = MagicMock()

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch("installer.steps.claude_files.subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=0)
            step._reapply_customization(ui)

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "customize" in call_args
        assert "update" in call_args
        assert "--quiet" in call_args

    def test_skips_silently_when_no_customization(self, tmp_path):
        import json
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        config_path = tmp_path / ".pilot" / "config.json"
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps({"model": "opus"}))

        step = ClaudeFilesStep()
        ui = MagicMock()

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch("installer.steps.claude_files.subprocess.run") as mock_run,
        ):
            step._reapply_customization(ui)

        mock_run.assert_not_called()

    def test_warns_on_failure(self, tmp_path):
        import json
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        config_path = tmp_path / ".pilot" / "config.json"
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps({"customization": {"source": "https://github.com/org/repo.git"}}))

        pilot_bin = tmp_path / ".pilot" / "bin" / "pilot"
        pilot_bin.parent.mkdir(parents=True)
        pilot_bin.touch()

        step = ClaudeFilesStep()
        ui = MagicMock()

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch("installer.steps.claude_files.subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=1)
            step._reapply_customization(ui)

        # Customization reapply failures now surface as visible errors, not silent warnings
        ui.error.assert_called_once()
        assert "FAILED" in ui.error.call_args.args[0]


class TestBuildSkillMdFiles:
    """Tests for the _build_skill_md_files method (Task 3: installer integration)."""

    def _make_skill(self, skills_dir: Path, skill_name: str) -> Path:
        """Create a skill directory with manifest.json, orchestrator, and one step."""
        skill_dir = skills_dir / skill_name
        skill_dir.mkdir(parents=True)
        (skill_dir / "orchestrator.md").write_text("# Skill")
        (skill_dir / "steps").mkdir()
        (skill_dir / "steps" / "01.md").write_text("## Step 1\n\nContent.")
        (skill_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "orchestrator": "orchestrator.md",
                    "steps": [{"id": "step-1", "file": "steps/01.md"}],
                }
            )
        )
        return skill_dir

    def _make_ctx(self, tmp_path: Path):
        """Build a minimal InstallContext for _build_skill_md_files tests."""
        from installer.context import InstallContext

        return InstallContext(project_dir=tmp_path)

    def test_builds_skill_md_for_each_skill(self, tmp_path):
        """Each decomposed skill gets a SKILL.md materialized in-process."""
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        skills_dir = tmp_path / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        skill_a = self._make_skill(skills_dir, "skill-a")
        skill_b = self._make_skill(skills_dir, "skill-b")

        step = ClaudeFilesStep()
        ui = MagicMock()

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch(
                "installer.steps.claude_files.get_claude_config_dir",
                return_value=tmp_path / ".claude",
            ),
        ):
            step._build_skill_md_files(self._make_ctx(tmp_path), ui)

        for skill_dir in (skill_a, skill_b):
            built = skill_dir / "SKILL.md"
            assert built.is_file()
            text = built.read_text()
            assert "# Skill" in text
            assert "## Step 1" in text

    def test_skips_skills_without_manifest(self, tmp_path):
        """Skills without manifest.json (legacy monolithic) are skipped."""
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        skills_dir = tmp_path / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        new_skill = self._make_skill(skills_dir, "new-skill")
        # Legacy monolithic (no manifest.json) — pre-built SKILL.md is left alone
        legacy = skills_dir / "legacy"
        legacy.mkdir()
        (legacy / "SKILL.md").write_text("# Legacy")

        step = ClaudeFilesStep()
        ui = MagicMock()

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch(
                "installer.steps.claude_files.get_claude_config_dir",
                return_value=tmp_path / ".claude",
            ),
        ):
            step._build_skill_md_files(self._make_ctx(tmp_path), ui)

        assert (new_skill / "SKILL.md").is_file()
        assert (legacy / "SKILL.md").read_text() == "# Legacy"

    def test_reports_failures_as_visible_errors(self, tmp_path):
        """A persistent BuildError surfaces via ui.error AND raises to abort the install."""
        from unittest.mock import MagicMock, patch

        import pytest

        from installer.steps.claude_files import ClaudeFilesStep

        skills_dir = tmp_path / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        skill_dir = self._make_skill(skills_dir, "broken")
        # Corrupt the manifest so build fails and recovery cannot help
        (skill_dir / "manifest.json").write_text("{not valid json")

        step = ClaudeFilesStep()
        ui = MagicMock()

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch(
                "installer.steps.claude_files.get_claude_config_dir",
                return_value=tmp_path / ".claude",
            ),
        ):
            with pytest.raises(RuntimeError, match="skill-build failed"):
                step._build_skill_md_files(self._make_ctx(tmp_path), ui)

        ui.error.assert_called_once()
        assert "broken" in ui.error.call_args.args[0]
        assert "FAILED" in ui.error.call_args.args[0]

    def test_missing_fragment_triggers_lazy_recovery_and_retry(self, tmp_path):
        """Missing fragment causes BuildError → recovery downloads it → retry succeeds."""
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        skills_dir = tmp_path / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        skill_dir = self._make_skill(skills_dir, "prd")
        missing = skill_dir / "steps" / "01.md"
        missing.unlink()
        assert not missing.exists()

        step = ClaudeFilesStep()
        ui = MagicMock()
        ctx = self._make_ctx(tmp_path)

        def fake_download(_repo_path: str, dest: Path, _config) -> bool:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("## Step 1\n\nRecovered.")
            return True

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch(
                "installer.steps.claude_files.get_claude_config_dir",
                return_value=tmp_path / ".claude",
            ),
            patch("installer.steps.claude_files.download_file", side_effect=fake_download) as mock_dl,
        ):
            step._build_skill_md_files(ctx, ui)

        assert missing.exists()
        assert (skill_dir / "SKILL.md").is_file()
        assert "Recovered." in (skill_dir / "SKILL.md").read_text()
        mock_dl.assert_called_once()
        repo_path_arg = mock_dl.call_args.args[0]
        assert repo_path_arg == "pilot/skills/prd/steps/01.md"
        assert str(missing) in ctx.config.get("installed_files", [])

    def test_urllib_fallback_recovers_when_download_file_fails(self, tmp_path):
        """If download_file returns False, the single-threaded urllib fallback takes over."""
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        skills_dir = tmp_path / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        skill_dir = self._make_skill(skills_dir, "prd")
        missing = skill_dir / "steps" / "01.md"
        missing.unlink()

        step = ClaudeFilesStep()
        ui = MagicMock()
        ctx = self._make_ctx(tmp_path)

        response_mock = MagicMock()
        response_mock.__enter__ = MagicMock(return_value=response_mock)
        response_mock.__exit__ = MagicMock(return_value=False)
        response_mock.status = 200
        response_mock.read.return_value = b"## Step 1\n\nFallback content."

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch(
                "installer.steps.claude_files.get_claude_config_dir",
                return_value=tmp_path / ".claude",
            ),
            patch("installer.steps.claude_files.download_file", return_value=False) as mock_dl,
            patch("urllib.request.urlopen", return_value=response_mock) as mock_urlopen,
        ):
            step._build_skill_md_files(ctx, ui)

        mock_dl.assert_called_once()
        mock_urlopen.assert_called_once()
        called_request = mock_urlopen.call_args.args[0]
        assert "pilot/skills/prd/steps/01.md" in called_request.full_url
        assert missing.is_file()
        assert missing.read_bytes() == b"## Step 1\n\nFallback content."
        assert (skill_dir / "SKILL.md").is_file()
        assert str(missing) in ctx.config.get("installed_files", [])

    def test_diagnostics_emitted_when_skill_build_fails(self, tmp_path):
        """After recovery cannot fix the skill, diagnostics print on-disk state and URLs."""
        from unittest.mock import MagicMock, patch

        import pytest

        from installer.steps.claude_files import ClaudeFilesStep

        skills_dir = tmp_path / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        skill_dir = self._make_skill(skills_dir, "prd")
        # Drop a fragment AND make recovery fail, so BuildError persists
        (skill_dir / "steps" / "01.md").unlink()

        step = ClaudeFilesStep()
        ui = MagicMock()

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch(
                "installer.steps.claude_files.get_claude_config_dir",
                return_value=tmp_path / ".claude",
            ),
            patch("installer.steps.claude_files.download_file", return_value=False),
            patch.object(ClaudeFilesStep, "_direct_download_with_diagnostics", return_value=False),
        ):
            with pytest.raises(RuntimeError):
                step._build_skill_md_files(self._make_ctx(tmp_path), ui)

        printed = "\n".join(call.args[0] for call in ui.print.call_args_list if call.args)
        assert str(skill_dir) in printed
        assert "manifest.json" in printed
        assert "steps/01.md" in printed
        assert "pilot/skills/prd/steps/01.md" in printed

    def test_no_skills_dir_returns_silently(self, tmp_path):
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        # No skills dir at all
        step = ClaudeFilesStep()
        ui = MagicMock()

        with (
            patch("installer.steps.claude_files.Path.home", return_value=tmp_path),
            patch(
                "installer.steps.claude_files.get_claude_config_dir",
                return_value=tmp_path / ".claude",
            ),
        ):
            step._build_skill_md_files(self._make_ctx(tmp_path), ui)

        ui.warning.assert_not_called()
        ui.error.assert_not_called()


class TestPatchPluginRoot:
    """patch_plugin_root expands ${CLAUDE_PLUGIN_ROOT} to the absolute asset path."""

    def test_substitutes_plugin_root_with_absolute_path(self):
        from installer.steps.claude_files import get_claude_config_dir, patch_plugin_root

        content = '{"command": "uv run python \\"${CLAUDE_PLUGIN_ROOT}/hooks/foo.py\\""}'
        result = patch_plugin_root(content)

        expected_root = str(get_claude_config_dir() / "pilot")
        assert "${CLAUDE_PLUGIN_ROOT}" not in result
        assert expected_root in result

    def test_leaves_unrelated_text_unchanged(self):
        from installer.steps.claude_files import patch_plugin_root

        content = '{"command": "echo hello"}'
        result = patch_plugin_root(content)
        assert result == content

    def test_handles_multiple_occurrences(self):
        from installer.steps.claude_files import patch_plugin_root

        content = "${CLAUDE_PLUGIN_ROOT}/a ${CLAUDE_PLUGIN_ROOT}/b"
        result = patch_plugin_root(content)
        assert "${CLAUDE_PLUGIN_ROOT}" not in result
        assert result.count("/a") == 1
        assert result.count("/b") == 1


class TestMergePilotHooks:
    """Tests for the Pilot-owned-entry-aware hooks merge.

    See docs/plans/2026-05-12-drop-plugin-system-native-install.md Task 1.
    """

    @staticmethod
    def _entry(matcher, command):
        return {"matcher": matcher, "hooks": [{"type": "command", "command": command}]}

    def test_first_install_no_baseline_no_current(self):
        """No baseline, empty current → incoming installed as-is."""
        from installer.steps.settings_merge import merge_pilot_hooks

        incoming = {"PostToolUse": [self._entry("Write|Edit", "py /a/file_checker.py")]}

        result = merge_pilot_hooks({}, incoming, None)

        assert result == incoming

    def test_first_install_user_added_event_preserved(self):
        """User defined a hook under a key Pilot doesn't ship → preserved alongside Pilot's."""
        from installer.steps.settings_merge import merge_pilot_hooks

        current = {"UserPromptSubmit": [self._entry("", "echo user")]}
        incoming = {"PostToolUse": [self._entry("Write", "py /a/file_checker.py")]}

        result = merge_pilot_hooks(current, incoming, None)

        assert result["UserPromptSubmit"] == [self._entry("", "echo user")]
        assert result["PostToolUse"] == [self._entry("Write", "py /a/file_checker.py")]

    def test_upgrade_baseline_matches_current_incoming_replaces(self):
        """Baseline == current Pilot entries → upgrade to incoming."""
        from installer.steps.settings_merge import merge_pilot_hooks

        baseline = {"PostToolUse": [self._entry("Write", "py /old/file_checker.py")]}
        current = {"PostToolUse": [self._entry("Write", "py /old/file_checker.py")]}
        incoming = {"PostToolUse": [self._entry("Write", "py /new/file_checker.py")]}

        result = merge_pilot_hooks(current, incoming, baseline)

        assert result["PostToolUse"] == [self._entry("Write", "py /new/file_checker.py")]

    def test_user_added_entry_under_pilot_event_preserved(self):
        """User added an entry to a Pilot event key → kept alongside Pilot's new entry."""
        from installer.steps.settings_merge import merge_pilot_hooks

        baseline = {"Stop": [self._entry("", "py /old/stop.py")]}
        current = {
            "Stop": [
                self._entry("", "py /old/stop.py"),
                self._entry("", "echo my-user-stop"),
            ]
        }
        incoming = {"Stop": [self._entry("", "py /new/stop.py")]}

        result = merge_pilot_hooks(current, incoming, baseline)

        # User's entry should remain; Pilot's entry should be the new one
        commands = [h["command"] for entry in result["Stop"] for h in entry["hooks"]]
        assert "echo my-user-stop" in commands
        assert "py /new/stop.py" in commands
        assert "py /old/stop.py" not in commands

    def test_signature_collision_raises_value_error(self):
        """Incoming with two entries sharing (matcher, sorted-commands) is a programmer error."""
        import pytest

        from installer.steps.settings_merge import merge_pilot_hooks

        incoming = {
            "PostToolUse": [
                self._entry("Write", "py /a/file_checker.py"),
                self._entry("Write", "py /a/file_checker.py"),  # exact duplicate
            ]
        }
        with pytest.raises(ValueError):
            merge_pilot_hooks({}, incoming, None)

    def test_pilot_event_removed_when_user_unchanged(self):
        """Pilot drops an event entirely; user hadn't touched it → dropped."""
        from installer.steps.settings_merge import merge_pilot_hooks

        baseline = {"PreCompact": [self._entry("", "py /old/pre_compact.py")]}
        current = {"PreCompact": [self._entry("", "py /old/pre_compact.py")]}
        incoming = {}

        result = merge_pilot_hooks(current, incoming, baseline)

        assert "PreCompact" not in result


class TestAgentsCategoryAndSkips:
    """Task 3: agents go to ~/.claude/agents/; plugin.json + .lsp.json skipped."""

    def test_categorize_agents_routes_to_agents_category(self):
        from installer.steps.claude_files import _categorize_file

        assert _categorize_file("pilot/agents/spec-review.md") == "agents"
        assert _categorize_file("pilot/agents/changes-review-codex.md") == "agents"

    def test_skip_plugin_json(self):
        from installer.steps.claude_files import _should_skip_file

        assert _should_skip_file("pilot/plugin.json") is True

    def test_skip_lsp_json(self):
        from installer.steps.claude_files import _should_skip_file

        assert _should_skip_file("pilot/.lsp.json") is True

    def test_get_dest_path_agents_goes_to_claude_agents_dir(self, tmp_path):
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        step = ClaudeFilesStep()
        claude_dir = tmp_path / ".claude"
        with patch("installer.steps.claude_files.get_claude_config_dir", return_value=claude_dir):
            ctx = MagicMock()
            dest = step._get_dest_path("agents", "pilot/agents/spec-review.md", ctx)
        assert dest == claude_dir / "agents" / "spec-review.md"

    def test_remove_legacy_plugin_marker_deletes_file(self, tmp_path):
        from unittest.mock import patch

        from installer.steps.claude_files import ClaudeFilesStep

        claude_dir = tmp_path / ".claude"
        plugin_dir = claude_dir / "pilot"
        plugin_dir.mkdir(parents=True)
        marker = plugin_dir / "plugin.json"
        marker.write_text('{"name": "pilot"}')

        step = ClaudeFilesStep()
        with patch("installer.steps.claude_files.get_claude_config_dir", return_value=claude_dir):
            step._remove_legacy_plugin_marker()

        assert not marker.exists()

    def test_remove_legacy_plugin_marker_silent_if_missing(self, tmp_path):
        from unittest.mock import patch

        from installer.steps.claude_files import ClaudeFilesStep

        claude_dir = tmp_path / ".claude"
        step = ClaudeFilesStep()
        with patch("installer.steps.claude_files.get_claude_config_dir", return_value=claude_dir):
            # Should not raise even if marker doesn't exist.
            step._remove_legacy_plugin_marker()

    def test_upgrade_idempotency_two_runs_no_double_fire(self, tmp_path):
        """Run install twice in a row. plugin.json stays gone; hooks aren't doubled.

        Plan Risk-table mitigation: 'Add an integration test that runs install
        twice with a stale plugin.json from the first run and asserts it's gone
        on the second.' This exercises the full _post_install_processing path
        (minus heavy sub-steps) two times.
        """
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        claude_dir = tmp_path / ".claude"
        plugin_dir = claude_dir / "pilot"
        plugin_dir.mkdir(parents=True)
        # Seed first-run state: stale plugin.json from a prior install
        marker = plugin_dir / "plugin.json"
        marker.write_text('{"name": "pilot"}')
        # Minimal hooks.json so _merge_hooks_into_settings has input
        hooks_dir = plugin_dir / "hooks"
        hooks_dir.mkdir()
        hooks_dir_content = {
            "hooks": {"Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "py /a/stop.py"}]}]}
        }
        (hooks_dir / "hooks.json").write_text(json.dumps(hooks_dir_content) + "\n")
        # Pre-existing user settings.json
        (claude_dir / "settings.json").write_text(json.dumps({"model": "sonnet"}) + "\n")

        ctx = MagicMock()
        ctx.local_mode = True
        ui = MagicMock()
        step = ClaudeFilesStep()

        with (
            patch("installer.steps.claude_files.get_claude_config_dir", return_value=claude_dir),
            patch.object(step, "_make_scripts_executable"),
            patch.object(step, "_merge_app_config"),
            patch.object(step, "_merge_mcp_servers_into_claude_json"),
            patch("installer.steps.claude_files.migrate_model_config"),
            patch.object(step, "_cleanup_stale_managed_files"),
            patch.object(step, "_build_skill_md_files"),
            patch.object(step, "_save_pilot_manifest"),
            patch.object(step, "_reapply_customization"),
        ):
            # First run — plugin marker gone, hooks merged once
            step._post_install_processing(ctx, ui)
            assert not marker.exists()
            settings_after_first = json.loads((claude_dir / "settings.json").read_text())
            first_stop = settings_after_first["hooks"]["Stop"]
            assert len(first_stop) == 1

            # Second run — re-seed marker (simulates downstream tooling
            # recreating it; we still want it gone after a re-install) and
            # confirm idempotency
            marker.write_text('{"name": "pilot"}')
            step._post_install_processing(ctx, ui)
            assert not marker.exists()

            # Hooks must NOT have doubled — second-run is a no-op for the same
            # incoming entries (baseline matches → identity-aware merge replaces
            # in place rather than appending).
            settings_after_second = json.loads((claude_dir / "settings.json").read_text())
            second_stop = settings_after_second["hooks"]["Stop"]
            assert len(second_stop) == 1, f"Hooks doubled: {second_stop}"
            assert second_stop == first_stop

    def test_post_install_processing_removes_marker_first(self, tmp_path):
        """Order-of-operations: plugin.json deletion must happen before any merge writes."""
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        claude_dir = tmp_path / ".claude"
        plugin_dir = claude_dir / "pilot"
        plugin_dir.mkdir(parents=True)
        marker = plugin_dir / "plugin.json"
        marker.write_text('{"name": "pilot"}')

        call_log: list[str] = []

        def _log_remove():
            call_log.append("remove_marker")
            (plugin_dir / "plugin.json").unlink(missing_ok=True)

        def _log_merge_hooks():
            call_log.append("merge_hooks")

        ctx = MagicMock()
        ctx.local_mode = True  # short-circuit _update_hooks_config
        ui = MagicMock()

        step = ClaudeFilesStep()
        with (
            patch.object(step, "_remove_legacy_plugin_marker", side_effect=_log_remove),
            patch.object(step, "_make_scripts_executable"),
            patch.object(step, "_merge_hooks_into_settings", side_effect=_log_merge_hooks),
            patch.object(step, "_merge_app_config"),
            patch.object(step, "_merge_mcp_servers_into_claude_json"),
            patch("installer.steps.claude_files.migrate_model_config"),
            patch.object(step, "_cleanup_stale_managed_files"),
            patch.object(step, "_build_skill_md_files"),
            patch.object(step, "_save_pilot_manifest"),
            patch.object(step, "_reapply_customization"),
            patch(
                "installer.steps.claude_files.get_claude_config_dir",
                return_value=claude_dir,
            ),
        ):
            step._post_install_processing(ctx, ui)

        assert call_log.index("remove_marker") < call_log.index("merge_hooks")


class TestMergePilotMcpServers:
    """Value-aware MCP server merge — preserves user-added AND user-modified servers."""

    def test_first_install_no_collision_installs_all(self):
        from installer.steps.settings_merge import merge_pilot_mcp_servers

        current = {}
        incoming = {"context7": {"command": "npx", "args": ["-y", "context7"]}}
        result, warnings = merge_pilot_mcp_servers(current, incoming, None)

        assert result == incoming
        assert warnings == []

    def test_first_install_name_collision_preserves_user(self):
        from installer.steps.settings_merge import merge_pilot_mcp_servers

        current = {"context7": {"command": "user-custom"}}
        incoming = {"context7": {"command": "npx"}}
        result, warnings = merge_pilot_mcp_servers(current, incoming, None)

        assert result["context7"]["command"] == "user-custom"
        assert any("context7" in w for w in warnings)

    def test_upgrade_user_untouched_pilot_server_updated(self):
        from installer.steps.settings_merge import merge_pilot_mcp_servers

        baseline = {"context7": {"command": "npx-old"}}
        current = {"context7": {"command": "npx-old"}}
        incoming = {"context7": {"command": "npx-new"}}
        result, warnings = merge_pilot_mcp_servers(current, incoming, baseline)

        assert result["context7"]["command"] == "npx-new"
        assert warnings == []

    def test_upgrade_user_modified_pilot_server_preserved_with_warning(self):
        """Codex finding #2 — value-aware preservation."""
        from installer.steps.settings_merge import merge_pilot_mcp_servers

        baseline = {"context7": {"command": "npx", "args": ["-y"]}}
        current = {"context7": {"command": "node", "args": ["-y"]}}  # user changed command
        incoming = {"context7": {"command": "npx-new", "args": ["-y"]}}
        result, warnings = merge_pilot_mcp_servers(current, incoming, baseline)

        assert result["context7"]["command"] == "node"
        assert any("context7" in w for w in warnings)

    def test_upgrade_pilot_ships_server_user_already_added(self):
        """Pilot newly ships a server with a name the user already created."""
        from installer.steps.settings_merge import merge_pilot_mcp_servers

        baseline = {"context7": {"command": "npx"}}  # only original Pilot server
        current = {
            "context7": {"command": "npx"},
            "super-tool": {"command": "user-added"},  # not in baseline
        }
        incoming = {
            "context7": {"command": "npx"},
            "super-tool": {"command": "pilot-version"},  # Pilot now adds this
        }
        result, warnings = merge_pilot_mcp_servers(current, incoming, baseline)

        assert result["super-tool"]["command"] == "user-added"
        assert any("super-tool" in w for w in warnings)

    def test_deprecated_pilot_server_removed_when_user_untouched(self):
        from installer.steps.settings_merge import merge_pilot_mcp_servers

        baseline = {"old-server": {"command": "npx-old"}, "context7": {"command": "npx"}}
        current = {"old-server": {"command": "npx-old"}, "context7": {"command": "npx"}}
        incoming = {"context7": {"command": "npx"}}  # old-server deprecated
        result, _ = merge_pilot_mcp_servers(current, incoming, baseline)

        assert "old-server" not in result
        assert "context7" in result

    def test_deprecated_pilot_server_preserved_when_user_customized(self):
        from installer.steps.settings_merge import merge_pilot_mcp_servers

        baseline = {"old-server": {"command": "npx-old"}}
        current = {"old-server": {"command": "user-custom"}}  # user modified
        incoming = {}  # Pilot deprecates
        result, warnings = merge_pilot_mcp_servers(current, incoming, baseline)

        assert result["old-server"]["command"] == "user-custom"
        assert any("old-server" in w for w in warnings)

    def test_user_added_non_pilot_server_always_preserved(self):
        from installer.steps.settings_merge import merge_pilot_mcp_servers

        baseline = {"context7": {"command": "npx"}}
        current = {
            "context7": {"command": "npx"},
            "my-server": {"command": "user-thing"},
        }
        incoming = {"context7": {"command": "npx"}}
        result, _ = merge_pilot_mcp_servers(current, incoming, baseline)

        assert result["my-server"]["command"] == "user-thing"


class TestMergeMcpServersIntoClaudeJson:
    """Integration tests for ClaudeFilesStep._merge_mcp_servers_into_claude_json."""

    def test_installs_pilot_servers_into_claude_json(self, tmp_path):
        from unittest.mock import patch

        from installer.steps.claude_files import ClaudeFilesStep

        claude_dir = tmp_path / ".claude"
        plugin_dir = claude_dir / "pilot"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / ".mcp.json").write_text(json.dumps({"mcpServers": {"context7": {"command": "npx"}}}, indent=2))
        home = tmp_path
        # Pre-existing ~/.claude.json with non-MCP keys
        (home / ".claude.json").write_text(json.dumps({"oauthAccount": "x"}, indent=2))

        step = ClaudeFilesStep()
        with (
            patch("installer.steps.claude_files.get_claude_config_dir", return_value=claude_dir),
            patch("installer.steps.claude_files.Path.home", return_value=home),
        ):
            step._merge_mcp_servers_into_claude_json(ui=None)

        merged = json.loads((home / ".claude.json").read_text())
        assert merged["mcpServers"]["context7"]["command"] == "npx"
        assert merged["oauthAccount"] == "x"  # preserved
        # Dedicated MCP baseline (NOT .pilot-claude-baseline.json — that one is
        # owned by _merge_app_config and would clobber us on subsequent installs).
        baseline = json.loads((claude_dir / ".pilot-mcp-baseline.json").read_text())
        assert baseline["context7"]["command"] == "npx"

    def test_preserves_user_modified_pilot_server(self, tmp_path):
        """Second install: user modified context7; merge preserves it and warns."""
        from unittest.mock import MagicMock, patch

        from installer.steps.claude_files import ClaudeFilesStep

        claude_dir = tmp_path / ".claude"
        plugin_dir = claude_dir / "pilot"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / ".mcp.json").write_text(
            json.dumps({"mcpServers": {"context7": {"command": "npx-new"}}}, indent=2)
        )
        home = tmp_path
        # ~/.claude.json: user modified context7
        (home / ".claude.json").write_text(
            json.dumps({"mcpServers": {"context7": {"command": "node-custom"}}}, indent=2)
        )
        # baseline (from prior install) records what Pilot installed
        (claude_dir / ".pilot-mcp-baseline.json").write_text(json.dumps({"context7": {"command": "npx-old"}}, indent=2))

        step = ClaudeFilesStep()
        ui = MagicMock()
        with (
            patch("installer.steps.claude_files.get_claude_config_dir", return_value=claude_dir),
            patch("installer.steps.claude_files.Path.home", return_value=home),
        ):
            step._merge_mcp_servers_into_claude_json(ui=ui)

        merged = json.loads((home / ".claude.json").read_text())
        assert merged["mcpServers"]["context7"]["command"] == "node-custom"
        # UI got a warning
        ui.warning.assert_called()


class TestMergeHooksIntoSettings:
    """Integration tests for ClaudeFilesStep._merge_hooks_into_settings."""

    def test_writes_hooks_into_settings_with_absolute_paths(self, tmp_path):
        """After merge, ~/.claude/settings.json `hooks` contains absolute paths,
        no ${CLAUDE_PLUGIN_ROOT} substrings, and a dedicated baseline file exists.
        """
        from unittest.mock import patch

        from installer.steps.claude_files import ClaudeFilesStep

        claude_dir = tmp_path / ".claude"
        plugin_dir = claude_dir / "pilot"
        hooks_dir = plugin_dir / "hooks"
        hooks_dir.mkdir(parents=True)
        # Minimal hooks.json with one ${CLAUDE_PLUGIN_ROOT} reference
        hooks_json = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Write|Edit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": 'uv run python "${CLAUDE_PLUGIN_ROOT}/hooks/file_checker.py"',
                            }
                        ],
                    }
                ]
            }
        }
        (hooks_dir / "hooks.json").write_text(json.dumps(hooks_json, indent=2) + "\n")
        # Pre-existing settings.json with no hooks key
        claude_dir.mkdir(parents=True, exist_ok=True)
        (claude_dir / "settings.json").write_text(json.dumps({"model": "sonnet"}, indent=2) + "\n")

        step = ClaudeFilesStep()
        with patch(
            "installer.steps.claude_files.get_claude_config_dir",
            return_value=claude_dir,
        ):
            step._merge_hooks_into_settings()

        merged = json.loads((claude_dir / "settings.json").read_text())
        assert "hooks" in merged
        assert merged["model"] == "sonnet"
        # Verify absolute path substitution happened
        cmd = merged["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
        assert "${CLAUDE_PLUGIN_ROOT}" not in cmd
        assert str(claude_dir / "pilot") in cmd

        # Dedicated baseline file exists with the new hooks
        baseline_path = claude_dir / ".pilot-hooks-baseline.json"
        assert baseline_path.exists()
        baseline = json.loads(baseline_path.read_text())
        assert "PostToolUse" in baseline
        # settings baseline (legacy) must NOT contain hooks
        settings_baseline = claude_dir / ".pilot-settings-baseline.json"
        if settings_baseline.exists():
            assert "hooks" not in json.loads(settings_baseline.read_text())

    def test_preserves_user_added_hook_on_re_install(self, tmp_path):
        """User added a Stop hook → preserved alongside Pilot's incoming hooks."""
        from unittest.mock import patch

        from installer.steps.claude_files import ClaudeFilesStep

        claude_dir = tmp_path / ".claude"
        plugin_dir = claude_dir / "pilot"
        hooks_dir = plugin_dir / "hooks"
        hooks_dir.mkdir(parents=True)

        # Incoming hooks.json from the new install
        hooks_json = {
            "hooks": {"Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "py NEW_PILOT_STOP"}]}]}
        }
        (hooks_dir / "hooks.json").write_text(json.dumps(hooks_json, indent=2) + "\n")

        # Previous Pilot baseline (what was installed before)
        claude_dir.mkdir(parents=True, exist_ok=True)
        (claude_dir / ".pilot-hooks-baseline.json").write_text(
            json.dumps(
                {"Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "py OLD_PILOT_STOP"}]}]},
                indent=2,
            )
            + "\n"
        )
        # Current settings.json has Pilot's old Stop + a user-added Stop entry
        (claude_dir / "settings.json").write_text(
            json.dumps(
                {
                    "model": "sonnet",
                    "hooks": {
                        "Stop": [
                            {"matcher": "", "hooks": [{"type": "command", "command": "py OLD_PILOT_STOP"}]},
                            {"matcher": "", "hooks": [{"type": "command", "command": "echo MY_USER_STOP"}]},
                        ]
                    },
                },
                indent=2,
            )
            + "\n"
        )

        step = ClaudeFilesStep()
        with patch(
            "installer.steps.claude_files.get_claude_config_dir",
            return_value=claude_dir,
        ):
            step._merge_hooks_into_settings()

        merged = json.loads((claude_dir / "settings.json").read_text())
        commands = [h["command"] for entry in merged["hooks"]["Stop"] for h in entry["hooks"]]
        assert "echo MY_USER_STOP" in commands  # preserved
        assert "py NEW_PILOT_STOP" in commands  # installed
        assert "py OLD_PILOT_STOP" not in commands  # replaced
