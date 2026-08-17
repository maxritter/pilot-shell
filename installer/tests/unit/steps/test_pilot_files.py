"""Tests for installer.steps.pilot_files — agent-neutral Pilot install step."""

from __future__ import annotations

import contextlib
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestPilotFilesStepBasics:
    def test_step_name_is_pilot_files(self) -> None:
        from installer.steps.pilot_files import PilotFilesStep

        assert PilotFilesStep().name == "pilot_files"

    def test_step_always_runs(self) -> None:
        """check() returns False so the install dispatcher always invokes run()."""
        from installer.context import InstallContext
        from installer.steps.pilot_files import PilotFilesStep
        from installer.ui import Console

        step = PilotFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = InstallContext(project_dir=Path(tmpdir), ui=Console(non_interactive=True, quiet=True))
            assert step.check(ctx) is False


class TestPilotFilesStepScope:
    """run() installs only agent-neutral categories: hooks, pilot_home, skills.

    Claude-targeted categories (rules, agents, settings) are left for the
    Claude step. Skills install regardless of whether Claude Code is installed,
    because Codex's adapter needs the decomposed skill source.
    """

    @staticmethod
    def _make_file_info(path: str):
        from installer.downloads import FileInfo

        return FileInfo(path=path, sha="abc")

    @staticmethod
    def _categories() -> dict[str, list]:
        mk = TestPilotFilesStepScope._make_file_info
        return {
            "skills": [mk("pilot/skills/spec/manifest.json")],
            "rules": [mk("pilot/rules/testing.md")],
            "agents": [mk("pilot/agents/changes-review.md")],
            "hooks": [mk("pilot/hooks/notify.py")],
            "pilot_home": [mk("pilot/scripts/worker.cjs")],
            "settings": [mk("pilot/settings.json")],
        }

    @contextlib.contextmanager
    def _patched_pilot_run(self, claude_installed: bool, cats: dict):
        """Enter every helper patch needed for PilotFilesStep.run() in one stack.

        Yields a dict ``{"install_cats": ..., "cleanup_stale": ...}`` of the
        mocks the test bodies assert against. Patches are constructed ONCE
        (vs the prior pattern of rebuilding a 10-element list per index
        lookup) so any side_effect ordering is preserved.
        """
        with contextlib.ExitStack() as stack:
            stack.enter_context(
                patch(
                    "installer.steps.pilot_files.get_repo_files",
                    return_value=[fi for files in cats.values() for fi in files],
                )
            )
            stack.enter_context(
                patch("installer.steps.claude_files.ClaudeFilesStep._categorize_files", return_value=cats)
            )
            stack.enter_context(patch("installer.steps.claude_files.ClaudeFilesStep._cleanup_old_directories"))
            install_cats = stack.enter_context(
                patch(
                    "installer.steps.claude_files.ClaudeFilesStep._install_categories",
                    return_value=(["/fake/installed"], 1, []),
                )
            )
            stack.enter_context(patch("installer.steps.claude_files.ClaudeFilesStep._make_scripts_executable"))
            stack.enter_context(patch("installer.steps.claude_files.ClaudeFilesStep._build_skill_md_files"))
            stack.enter_context(patch("installer.steps.pilot_files.download_files_parallel"))
            stack.enter_context(patch("installer.steps.claude_files.ClaudeFilesStep._save_pilot_manifest"))
            cleanup_stale = stack.enter_context(
                patch("installer.steps.claude_files.ClaudeFilesStep._cleanup_stale_managed_files")
            )
            stack.enter_context(patch("installer.steps.claude_files.ClaudeFilesStep._report_results"))
            stack.enter_context(patch("installer.steps.pilot_files.is_claude_installed", return_value=claude_installed))
            yield {"install_cats": install_cats, "cleanup_stale": cleanup_stale}

    @pytest.mark.parametrize("claude_installed", [True, False])
    def test_run_installs_only_pilot_categories(self, claude_installed: bool, tmp_path: Path) -> None:
        from installer.context import InstallContext
        from installer.steps.pilot_files import PilotFilesStep

        step = PilotFilesStep()
        ctx = InstallContext(project_dir=tmp_path, ui=None)
        cats = self._categories()

        with self._patched_pilot_run(claude_installed, cats) as mocks:
            step.run(ctx)
            passed_cats = mocks["install_cats"].call_args[0][0]
            assert set(passed_cats.keys()) == {"hooks", "pilot_home", "skills"}, (
                f"PilotFilesStep must only install agent-neutral + skills source; got {set(passed_cats.keys())}"
            )
            if claude_installed:
                mocks["cleanup_stale"].assert_not_called()
            else:
                mocks["cleanup_stale"].assert_called_once()

    def test_run_caches_categories_for_claude_step(self, tmp_path: Path) -> None:
        """ClaudeFilesStep reads from ctx.config to avoid a second download."""
        from installer.context import InstallContext
        from installer.steps.pilot_files import PilotFilesStep

        step = PilotFilesStep()
        ctx = InstallContext(project_dir=tmp_path, ui=None)
        cats = self._categories()

        with self._patched_pilot_run(True, cats):
            step.run(ctx)

        from installer.steps.pilot_files import PILOT_FILES_CACHE_CATEGORIES_KEY, PILOT_FILES_CACHE_CONFIG_KEY

        assert ctx.config.get(PILOT_FILES_CACHE_CATEGORIES_KEY) is cats
        assert ctx.config.get(PILOT_FILES_CACHE_CONFIG_KEY) is not None

    def test_stages_codex_sources_under_agent_neutral_pilot_home(self, tmp_path: Path) -> None:
        from installer.steps.pilot_files import PilotFilesStep

        step = PilotFilesStep()
        categories = self._categories()

        with (
            patch("installer.steps.pilot_files.Path.home", return_value=tmp_path),
            patch("installer.steps.pilot_files.download_files_parallel") as download,
        ):
            step._stage_raw_codex_sources(categories, MagicMock())

        destinations = [path for call in download.call_args_list for path in call.args[1]]
        assert tmp_path / ".pilot" / "rules" / "testing.md" in destinations
        assert tmp_path / ".pilot" / "skills" / "spec" / "manifest.json" in destinations
        assert tmp_path / ".pilot" / "agents" / "changes-review.md" in destinations


class TestClaudeFilesStepGated:
    """ClaudeFilesStep emits a clear skip and does no work when Claude is absent."""

    def test_run_skips_when_claude_not_installed(self, tmp_path: Path) -> None:
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep

        ui = MagicMock()
        step = ClaudeFilesStep()
        ctx = InstallContext(project_dir=tmp_path, ui=ui)

        with (
            patch("installer.steps.claude_files.is_claude_installed", return_value=False),
            patch("installer.steps.claude_files.ClaudeFilesStep._install_categories") as install_cats,
            patch("installer.steps.claude_files.ClaudeFilesStep._merge_hooks_into_settings") as merge_hooks,
        ):
            step.run(ctx)

        install_cats.assert_not_called()
        merge_hooks.assert_not_called()
        assert any("Claude Code" in str(c) for c in ui.info.call_args_list), (
            "Expected an info-level skip message naming Claude Code"
        )

    def test_run_installs_only_claude_categories(self, tmp_path: Path) -> None:
        from installer.context import InstallContext
        from installer.steps.claude_files import ClaudeFilesStep
        from installer.steps.pilot_files import PILOT_FILES_CACHE_CATEGORIES_KEY, PILOT_FILES_CACHE_CONFIG_KEY

        step = ClaudeFilesStep()
        ctx = InstallContext(project_dir=tmp_path, ui=None)
        cats = TestPilotFilesStepScope._categories()
        ctx.config[PILOT_FILES_CACHE_CATEGORIES_KEY] = cats
        ctx.config[PILOT_FILES_CACHE_CONFIG_KEY] = MagicMock()

        with (
            patch("installer.steps.claude_files.is_claude_installed", return_value=True),
            patch(
                "installer.steps.claude_files.ClaudeFilesStep._install_categories",
                return_value=([], 0, []),
            ) as install_cats,
            patch("installer.steps.claude_files.ClaudeFilesStep._merge_hooks_into_settings"),
            patch("installer.steps.claude_files.ClaudeFilesStep._merge_app_config"),
            patch("installer.steps.claude_files.ClaudeFilesStep._merge_mcp_servers_into_claude_json"),
            patch("installer.steps.claude_files.migrate_model_config"),
            patch("installer.steps.claude_files.ClaudeFilesStep._save_pilot_manifest"),
            patch("installer.steps.claude_files.ClaudeFilesStep._cleanup_stale_managed_files"),
            patch("installer.steps.claude_files.ClaudeFilesStep._reapply_customization"),
            patch("installer.steps.claude_files.ClaudeFilesStep._report_results"),
        ):
            step.run(ctx)

        passed_cats = install_cats.call_args[0][0]
        assert set(passed_cats.keys()) == {"rules", "agents", "settings"}, (
            f"ClaudeFilesStep must only install Claude-targeted categories; got {set(passed_cats.keys())}"
        )
