"""Pilot Files installation step — agent-neutral Pilot Shell-managed assets.

This step always runs and installs:

- ``hooks`` → ``~/.pilot/hooks/`` — Python hook scripts + ``hooks.json``
  (referenced from both Claude and Codex agent configs)
- ``pilot_home`` → ``~/.pilot/`` — Console scripts, UI assets, ``.mcp.json``,
  shared app config, package metadata
- ``skills`` → ``~/.claude/skills/`` for Claude plus a raw, agent-neutral
  source under ``~/.pilot/skills/`` for Codex materialization.
- ``rules`` and ``agents`` are likewise staged under ``~/.pilot/`` so a
  Codex-only installation never depends on a Claude profile.

Categories that target ``~/.claude/`` *exclusively* (``rules``, ``agents``,
``settings``) are owned by :class:`installer.steps.claude_files.ClaudeFilesStep`
and gated on ``is_claude_installed()``. ``PilotFilesStep`` caches the
download metadata in two named keys on ``ctx.config`` (see
``PILOT_FILES_CACHE_CATEGORIES_KEY`` / ``PILOT_FILES_CACHE_CONFIG_KEY``
below) so the Claude step can reuse it without a second GitHub round-trip.
"""

from __future__ import annotations

from pathlib import Path

from installer.context import InstallContext
from installer.downloads import DownloadConfig, FileInfo, download_files_parallel, get_repo_files
from installer.platform_utils import is_claude_installed
from installer.steps.base import BaseStep
from installer.steps.claude_files import ClaudeFilesStep

# Inter-step cache keys on ``ctx.config``. ``PilotFilesStep`` writes both;
# ``ClaudeFilesStep`` reads both. Keep these names in sync with the reader
# (claude_files.py imports them). The leading underscore marks them as
# inter-step cache (not user-facing config) — separate from the public
# ``installed_files`` key which both steps append to.
PILOT_FILES_CACHE_CATEGORIES_KEY = "_pilot_files_categories"
PILOT_FILES_CACHE_CONFIG_KEY = "_pilot_files_config"


class PilotFilesStep(BaseStep):
    """Installs Pilot Shell-managed agent-neutral assets.

    Uses ``ClaudeFilesStep`` *by composition* (not inheritance) to reuse the
    shared download/categorize/install/cleanup helpers without inheriting
    Claude-only methods like ``_install_settings`` / ``_merge_hooks_into_settings``
    / ``_merge_app_config`` / ``_merge_mcp_servers_into_claude_json`` /
    ``_reapply_customization``. This avoids the LSP violation of
    "PilotFilesStep IS-A ClaudeFilesStep" — Pilot is a separate concept that
    happens to share the file-install plumbing.

    When Claude Code is not installed on this system, ``ClaudeFilesStep``
    will skip — so this step also runs ``_cleanup_stale_managed_files`` to
    remove any leftover Pilot-managed files from a previous Claude install.
    When Claude *is* installed, that cleanup is deferred to
    ``ClaudeFilesStep`` so the union of pilot + Claude installed files is
    used to decide what's stale (avoids temporarily removing live Claude
    rules/agents between the two steps).
    """

    name = "pilot_files"

    _PILOT_CATEGORIES = ("hooks", "pilot_home", "skills")

    def __init__(self) -> None:
        # Composition target — used purely as a bag of file-install helpers.
        # Its public run() and Claude-specific methods are NEVER invoked from
        # this step.
        self._installer = ClaudeFilesStep()

    def check(self, ctx: InstallContext) -> bool:
        """Always run — Pilot runtime is required for both agents."""
        return False

    def run(self, ctx: InstallContext) -> None:
        ui = ctx.ui
        config = self._installer._create_download_config(ctx)

        if ui:
            ui.status("Installing Pilot Shell-managed assets...")

        pilot_files = get_repo_files("pilot", config)
        if not pilot_files:
            self._installer._handle_no_files(ui, config)
            return

        categories = self._installer._categorize_files(pilot_files, ctx)

        ctx.config[PILOT_FILES_CACHE_CATEGORIES_KEY] = categories
        ctx.config[PILOT_FILES_CACHE_CONFIG_KEY] = config

        self._installer._cleanup_old_directories(ctx, config, ui)

        pilot_categories = {cat: files for cat, files in categories.items() if cat in self._PILOT_CATEGORIES and files}
        installed_files, file_count, failed_files = self._installer._install_categories(
            pilot_categories, ctx, config, ui
        )
        existing_installed = list(ctx.config.get("installed_files", []))
        ctx.config["installed_files"] = existing_installed + installed_files

        self._stage_raw_codex_sources(categories, config)
        self._installer._make_scripts_executable(Path.home() / ".pilot" / "scripts")
        self._installer._build_skill_md_files(ctx, ui)

        # When Claude Code is NOT installed, ClaudeFilesStep will skip — we own
        # the cleanup/manifest tail here. cleanup_stale MUST run before
        # save_pilot_manifest, otherwise we'd read the freshly-saved manifest
        # and find nothing stale. When Claude Code IS installed, both calls are
        # deferred to ClaudeFilesStep so they see the union of pilot + Claude
        # installed files.
        if not is_claude_installed():
            self._installer._cleanup_stale_managed_files(ctx)
            self._installer._save_pilot_manifest(ctx)

        self._installer._report_results(ui, file_count, failed_files)

    def _stage_raw_codex_sources(
        self,
        categories: dict[str, list[FileInfo]],
        config: DownloadConfig,
    ) -> None:
        """Stage raw Codex inputs below ``~/.pilot``.

        Claude still receives its native skill/rule/agent layout. Codex reads
        these neutral copies first, which keeps app-only and CLI-only installs
        independent of ``CLAUDE_CONFIG_DIR``.
        """
        pilot_home = Path.home() / ".pilot"
        for category, prefix in (("rules", "pilot/rules/"), ("skills", "pilot/skills/"), ("agents", "pilot/agents/")):
            files = categories.get(category, [])
            if not files:
                continue
            destinations = [pilot_home / category / fi.path.removeprefix(prefix) for fi in files]
            for destination in destinations:
                destination.parent.mkdir(parents=True, exist_ok=True)
            download_files_parallel(files, destinations, config)
