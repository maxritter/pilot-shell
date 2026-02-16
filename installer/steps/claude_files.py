"""Claude files installation step - installs pilot directory files."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from installer.context import InstallContext
from installer.downloads import (
    DownloadConfig,
    FileInfo,
    download_file,
    download_files_parallel,
    get_repo_files,
)
from installer.steps.base import BaseStep

SETTINGS_FILE = "settings.local.json"

REPO_URL = "https://github.com/maxritter/claude-pilot"

SKIP_PATTERNS = (
    "__pycache__",
    ".pyc",
    "/node_modules/",
    "/dist/",
    "/.vite/",
    "/coverage/",
    "/.turbo/",
    ".lock",
    "-lock.yaml",
    ".install-version",
)

SKIP_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def patch_claude_paths(content: str) -> str:
    """Expand ~/.pilot/bin/ paths to absolute paths."""
    home = Path.home()
    abs_bin_path = str(home / ".pilot" / "bin") + "/"
    return content.replace('"~/.pilot/bin/', '"' + abs_bin_path)


def process_settings(settings_content: str) -> str:
    """Process settings JSON - parse and re-serialize with consistent formatting."""
    config: dict[str, Any] = json.loads(settings_content)
    return json.dumps(config, indent=2) + "\n"


def patch_global_settings(
    global_settings: dict[str, Any],
    local_settings: dict[str, Any],
) -> dict[str, Any] | None:
    """Remove Pilot-managed keys from global settings that exist in settings.local.json.

    Returns patched dict if changes were made, None if no changes needed.
    Never touches 'permissions' — only env vars and other top-level keys.
    """
    modified = False

    if "env" in global_settings and "env" in local_settings:
        for key in local_settings["env"]:
            if key in global_settings["env"]:
                del global_settings["env"][key]
                modified = True
        if not global_settings["env"]:
            del global_settings["env"]

    skip_keys = {"permissions", "env"}
    for key in list(local_settings.keys()):
        if key in skip_keys:
            continue
        if key in global_settings:
            del global_settings[key]
            modified = True

    return global_settings if modified else None


def merge_app_config(
    target: dict[str, Any],
    source: dict[str, Any],
) -> dict[str, Any] | None:
    """Merge app-level preferences from source into target (~/.claude.json).

    Sets each key from source in target. Returns patched dict if changes were made,
    None if all keys already match.
    """
    modified = False
    for key, value in source.items():
        if key not in target or target[key] != value:
            target[key] = value
            modified = True
    return target if modified else None


def _should_skip_file(file_path: str) -> bool:
    """Check if a file should be skipped during installation."""
    if not file_path:
        return True

    if any(pattern in file_path for pattern in SKIP_PATTERNS):
        return True

    if file_path.endswith(SKIP_EXTENSIONS):
        return True
    if Path(file_path).name == ".gitignore":
        return True

    return False


def _categorize_file(file_path: str) -> str:
    """Determine which category a file belongs to."""
    if file_path == "pilot/settings.json" or file_path.endswith("/settings.json"):
        return "settings"
    elif "/commands/" in file_path:
        return "commands"
    elif "/rules/" in file_path:
        return "rules"
    else:
        return "pilot_plugin"


def _clear_directory_safe(path: Path, ui: Any = None, error_msg: str = "") -> None:
    """Safely remove a directory with error handling."""
    if not path.exists():
        return
    try:
        shutil.rmtree(path)
    except (OSError, IOError) as e:
        if ui and error_msg:
            ui.warning(f"{error_msg}: {e}")


def _clear_directory_contents(path: Path) -> None:
    """Remove contents of a directory but keep the directory."""
    if not path.exists():
        return
    for item in path.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        except (OSError, IOError):
            pass


class ClaudeFilesStep(BaseStep):
    """Step that installs pilot directory files from the repository."""

    name = "claude_files"

    def check(self, ctx: InstallContext) -> bool:
        """Check if pilot files are already installed."""
        return False

    def run(self, ctx: InstallContext) -> None:
        """Install all pilot files from repository."""
        ui = ctx.ui
        config = self._create_download_config(ctx)

        if ui:
            ui.status("Installing pilot files...")

        pilot_files = get_repo_files("pilot", config)
        if not pilot_files:
            self._handle_no_files(ui, config)
            return

        categories = self._categorize_files(pilot_files, ctx)

        self._cleanup_old_directories(ctx, config, ui)

        installed_files, file_count, failed_files = self._install_categories(categories, ctx, config, ui)

        ctx.config["installed_files"] = installed_files

        self._post_install_processing(ctx, ui)

        self._report_results(ui, file_count, failed_files)

    def _create_download_config(self, ctx: InstallContext) -> DownloadConfig:
        """Create download configuration based on context."""
        repo_branch = "main"
        if ctx.target_version:
            if ctx.target_version.startswith("dev-"):
                repo_branch = ctx.target_version
            else:
                repo_branch = f"v{ctx.target_version}"

        repo_url = self._resolve_repo_url(repo_branch)

        return DownloadConfig(
            repo_url=repo_url,
            repo_branch=repo_branch,
            local_mode=ctx.local_mode,
            local_repo_dir=ctx.local_repo_dir,
        )

    def _resolve_repo_url(self, branch: str) -> str:
        """Return the repository URL."""
        return REPO_URL

    def _handle_no_files(self, ui: Any, config: DownloadConfig) -> None:
        """Handle case when no pilot files are found."""
        if ui:
            ui.warning("No pilot files found in repository")
            if not config.local_mode:
                ui.print("  This may be due to GitHub API rate limiting.")
                ui.print("  Try running with --local flag if you have the repo cloned.")

    def _categorize_files(self, pilot_files: list[FileInfo], ctx: InstallContext) -> dict[str, list[FileInfo]]:
        """Categorize files and filter out ones to skip."""
        categories: dict[str, list[FileInfo]] = {
            "commands": [],
            "rules": [],
            "pilot_plugin": [],
            "settings": [],
        }

        for file_info in pilot_files:
            file_path = file_info.path
            if _should_skip_file(file_path):
                continue

            category = _categorize_file(file_path)
            categories[category].append(file_info)

        return categories

    def _cleanup_old_directories(
        self,
        ctx: InstallContext,
        config: DownloadConfig,
        ui: Any,
    ) -> None:
        """Clean up old installation directories.

        Always cleans all directories when called - cleanup is decoupled from
        which file categories were found. This ensures stale files are removed
        even if specific categories are empty due to filtering or API issues.
        """
        home_claude_dir = Path.home() / ".claude"
        home_pilot_plugin_dir = home_claude_dir / "pilot"

        self._cleanup_legacy_standards_skills(home_pilot_plugin_dir)

        source_is_destination = (
            config.local_mode and config.local_repo_dir and config.local_repo_dir.resolve() == ctx.project_dir.resolve()
        )
        if source_is_destination:
            return

        _clear_directory_safe(
            home_claude_dir / "commands",
            ui,
            "Failed to clear global commands directory",
        )

        _clear_directory_safe(
            home_claude_dir / "rules",
            ui,
            "Failed to clear global rules directory",
        )

        _clear_directory_contents(home_pilot_plugin_dir)

        self._cleanup_legacy_project_dirs(ctx)

    def _cleanup_legacy_standards_skills(self, plugin_dir: Path) -> None:
        """Remove old standards-* skill directories from plugin skills folder.

        Standards were migrated from pilot/skills/ to pilot/rules/ with frontmatter.
        Runs unconditionally (before source_is_destination check) to clean up stale installs.
        """
        skills_dir = plugin_dir / "skills"
        if not skills_dir.exists():
            return

        for item in skills_dir.iterdir():
            if item.is_dir() and item.name.startswith("standards-"):
                _clear_directory_safe(item)

        if skills_dir.exists() and not any(skills_dir.iterdir()):
            try:
                skills_dir.rmdir()
            except (OSError, IOError):
                pass

    def _cleanup_legacy_project_dirs(self, ctx: InstallContext) -> None:
        """Remove legacy project-level directories."""
        project_claude_dir = ctx.project_dir / ".claude"

        _clear_directory_safe(project_claude_dir / "rules" / "standard")

        old_commands_dir = project_claude_dir / "commands"
        if old_commands_dir.exists():
            standard_commands = {"spec", "sync", "plan", "implement", "verify", "learn"}
            for cmd_file in old_commands_dir.iterdir():
                if cmd_file.is_file() and cmd_file.suffix == ".md":
                    if cmd_file.stem in standard_commands:
                        try:
                            cmd_file.unlink()
                        except (OSError, IOError):
                            pass
            if old_commands_dir.exists() and not any(old_commands_dir.iterdir()):
                try:
                    old_commands_dir.rmdir()
                except (OSError, IOError):
                    pass

        for old_dir_name in ["pilot", "hooks", "scripts", "plugin", "ccp"]:
            _clear_directory_safe(project_claude_dir / old_dir_name)

        old_custom_rules = project_claude_dir / "rules" / "custom"
        if old_custom_rules.exists() and old_custom_rules.is_dir():
            try:
                gitkeep = old_custom_rules / ".gitkeep"
                if gitkeep.exists():
                    gitkeep.unlink()
                if not any(old_custom_rules.iterdir()):
                    old_custom_rules.rmdir()
            except (OSError, IOError):
                pass

    def _install_categories(
        self,
        categories: dict[str, list[FileInfo]],
        ctx: InstallContext,
        config: DownloadConfig,
        ui: Any,
    ) -> tuple[list[str], int, list[str]]:
        """Install files by category."""
        installed_files: list[str] = []
        file_count = 0
        failed_files: list[str] = []

        category_names = {
            "commands": "slash commands",
            "rules": "standard rules",
            "pilot_plugin": "Pilot plugin files",
            "settings": "settings",
        }

        for category, file_infos in categories.items():
            if not file_infos:
                continue

            count, installed, failed = self._install_category_files(
                category, file_infos, ctx, config, ui, category_names[category]
            )
            file_count += count
            installed_files.extend(installed)
            failed_files.extend(failed)

        return installed_files, file_count, failed_files

    def _install_category_files(
        self,
        category: str,
        file_infos: list[FileInfo],
        ctx: InstallContext,
        config: DownloadConfig,
        ui: Any,
        category_display_name: str,
    ) -> tuple[int, list[str], list[str]]:
        """Install files for a single category."""
        installed: list[str] = []
        failed: list[str] = []

        def install_files() -> None:
            if category == "settings":
                for file_info in file_infos:
                    file_path = file_info.path
                    dest_file = self._get_dest_path(category, file_path, ctx)
                    success = self._install_settings(
                        file_path,
                        dest_file,
                        config,
                    )
                    if success:
                        installed.append(str(dest_file))
                    else:
                        failed.append(file_path)
                return

            dest_paths = [self._get_dest_path(category, fi.path, ctx) for fi in file_infos]
            results = download_files_parallel(file_infos, dest_paths, config)

            for file_info, dest_path, success in zip(file_infos, dest_paths, results):
                if success:
                    installed.append(str(dest_path))
                else:
                    failed.append(file_info.path)

        if ui:
            with ui.spinner(f"Installing {category_display_name}..."):
                install_files()
            ui.success(f"Installed {len(file_infos)} {category_display_name}")
        else:
            install_files()

        return len(installed), installed, failed

    def _get_dest_path(self, category: str, file_path: str, ctx: InstallContext) -> Path:
        """Determine destination path based on category."""
        home_claude_dir = Path.home() / ".claude"
        home_pilot_plugin_dir = home_claude_dir / "pilot"

        if category == "commands":
            rel_path = Path(file_path).relative_to("pilot/commands")
            return home_claude_dir / "commands" / rel_path
        elif category == "rules":
            rel_path = Path(file_path).relative_to("pilot/rules")
            return home_claude_dir / "rules" / rel_path
        elif category == "pilot_plugin":
            rel_path = Path(file_path).relative_to("pilot")
            return home_pilot_plugin_dir / rel_path
        elif category == "settings":
            return ctx.project_dir / ".claude" / "settings.local.json"
        else:
            return ctx.project_dir / file_path

    def _post_install_processing(self, ctx: InstallContext, ui: Any) -> None:
        """Run post-installation processing tasks."""
        home_pilot_plugin_dir = Path.home() / ".claude" / "pilot"

        self._make_scripts_executable(home_pilot_plugin_dir)

        self._update_lsp_config(home_pilot_plugin_dir)

        if not ctx.local_mode:
            self._update_hooks_config(home_pilot_plugin_dir)

        self._merge_app_config(ctx)
        self._patch_overlapping_settings(ctx)
        self._cleanup_stale_rules(ctx)
        self._ensure_project_rules_dir(ctx)

    def _make_scripts_executable(self, plugin_dir: Path) -> None:
        """Make script files executable."""
        scripts_dir = plugin_dir / "scripts"
        if not scripts_dir.exists():
            return

        for script in scripts_dir.glob("*.cjs"):
            try:
                current_mode = script.stat().st_mode
                script.chmod(current_mode | 0o111)
            except (OSError, IOError):
                pass

    def _update_lsp_config(self, plugin_dir: Path) -> None:
        """Process LSP config with consistent formatting."""
        lsp_config_path = plugin_dir / ".lsp.json"
        if not lsp_config_path.exists():
            return

        try:
            lsp_config = json.loads(lsp_config_path.read_text())
            lsp_config_path.write_text(json.dumps(lsp_config, indent=2) + "\n")
        except (json.JSONDecodeError, OSError, IOError):
            pass

    def _update_hooks_config(self, plugin_dir: Path) -> None:
        """Process hooks config with path patching and consistent formatting."""
        hooks_json_path = plugin_dir / "hooks" / "hooks.json"
        if not hooks_json_path.exists():
            return

        try:
            hooks_content = hooks_json_path.read_text()
            hooks_content = patch_claude_paths(hooks_content)
            hooks_config = json.loads(hooks_content)
            hooks_json_path.write_text(json.dumps(hooks_config, indent=2) + "\n")
        except (json.JSONDecodeError, OSError, IOError):
            pass

    def _merge_app_config(self, ctx: InstallContext) -> None:
        """Merge app-level preferences from pilot/claude.json into ~/.claude.json.

        Reads the installed claude.json template and merges its keys into the
        user's ~/.claude.json. Preserves all existing app state (projects,
        oauthAccount, caches, etc.) — only sets keys defined in the template.
        """
        template_path = Path.home() / ".claude" / "pilot" / "claude.json"
        if not template_path.exists():
            return

        claude_json_path = Path.home() / ".claude.json"

        try:
            source = json.loads(template_path.read_text())
        except (json.JSONDecodeError, OSError, IOError):
            return

        try:
            target = json.loads(claude_json_path.read_text()) if claude_json_path.exists() else {}
        except (json.JSONDecodeError, OSError, IOError):
            target = {}

        patched = merge_app_config(target, source)
        if patched is not None:
            try:
                claude_json_path.write_text(json.dumps(patched, indent=2) + "\n")
            except (OSError, IOError):
                pass

    def _patch_overlapping_settings(self, ctx: InstallContext) -> None:
        """Patch global and project settings.json to avoid overriding settings.local.json.

        Both ~/.claude/settings.json and <project>/.claude/settings.json can
        override settings.local.json. Remove overlapping env vars and non-permission
        top-level keys from both so settings.local.json takes clean precedence.
        """
        local_settings_path = ctx.project_dir / ".claude" / "settings.local.json"
        if not local_settings_path.exists():
            return

        try:
            local_settings = json.loads(local_settings_path.read_text())
        except (json.JSONDecodeError, OSError, IOError):
            return

        paths_to_patch = [
            Path.home() / ".claude" / "settings.json",
            ctx.project_dir / ".claude" / "settings.json",
        ]

        for settings_path in paths_to_patch:
            if not settings_path.exists():
                continue
            try:
                target_settings = json.loads(settings_path.read_text())
                patched = patch_global_settings(target_settings, local_settings)
                if patched is not None:
                    settings_path.write_text(json.dumps(patched, indent=2) + "\n")
            except (json.JSONDecodeError, OSError, IOError):
                continue

    def _cleanup_stale_rules(self, ctx: InstallContext) -> None:
        """Remove stale rule files from ~/.claude/rules/ not present in this installation.

        ~/.claude/rules/ is purely installer-managed (user rules go in project .claude/rules/).
        Any file there that wasn't just installed is stale from a previous version.
        """
        global_rules_dir = Path.home() / ".claude" / "rules"
        if not global_rules_dir.exists():
            return

        installed = {Path(p).resolve() for p in ctx.config.get("installed_files", [])}

        for item in global_rules_dir.iterdir():
            if item.is_file() and item.resolve() not in installed:
                try:
                    item.unlink()
                except (OSError, IOError):
                    pass

    def _ensure_project_rules_dir(self, ctx: InstallContext) -> None:
        """Ensure project rules directory exists."""
        project_rules_dir = ctx.project_dir / ".claude" / "rules"
        if not project_rules_dir.exists():
            project_rules_dir.mkdir(parents=True, exist_ok=True)
            (project_rules_dir / ".gitkeep").touch()

    def _report_results(self, ui: Any, file_count: int, failed_files: list[str]) -> None:
        """Report installation results."""
        if not ui:
            return

        if file_count > 0:
            ui.success(f"Installed {file_count} pilot files")
        else:
            ui.warning("No pilot files were installed")

        if failed_files:
            ui.warning(f"Failed to download {len(failed_files)} files")
            for failed in failed_files[:5]:
                ui.print(f"  - {failed}")
            if len(failed_files) > 5:
                ui.print(f"  ... and {len(failed_files) - 5} more")

    def _install_settings(
        self,
        source_path: str,
        dest_path: Path,
        config: DownloadConfig,
    ) -> bool:
        """Download and process settings file."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = Path(tmpdir) / "settings.json"
            if not download_file(source_path, temp_file, config):
                return False

            try:
                settings_content = temp_file.read_text()
                processed_content = process_settings(settings_content)
                processed_content = patch_claude_paths(processed_content)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_text(processed_content)
                return True
            except (json.JSONDecodeError, OSError, IOError):
                return False
