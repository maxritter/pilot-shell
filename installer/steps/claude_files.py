"""Claude files installation step - installs .claude directory files."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from installer.context import InstallContext
from installer.downloads import DownloadConfig, download_file, get_repo_files
from installer.steps.base import BaseStep

SETTINGS_FILE = "settings.local.json"
PYTHON_CHECKER_HOOK = "uv run python .claude/hooks/file_checker_python.py"
TYPESCRIPT_CHECKER_HOOK = "uv run python .claude/hooks/file_checker_ts.py"
GOLANG_CHECKER_HOOK = "uv run python .claude/hooks/file_checker_go.py"
HOOKS_PATH_PATTERN = ".claude/hooks/"
BIN_PATH_PATTERN = ".claude/bin/"
SOURCE_REPO_HOOKS_PATH = "/workspaces/claude-codepro/.claude/hooks/"
SOURCE_REPO_BIN_PATH = "/workspaces/claude-codepro/.claude/bin/"


def patch_claude_paths(content: str, project_dir: Path) -> str:
    """Patch .claude paths to use absolute paths for the target project.

    Handles both relative paths (.claude/hooks/, .claude/bin/) and existing
    absolute paths from the source repo (/workspaces/claude-codepro/.claude/).
    """
    abs_hooks_path = str(project_dir / ".claude" / "hooks") + "/"
    abs_bin_path = str(project_dir / ".claude" / "bin") + "/"

    content = content.replace(SOURCE_REPO_HOOKS_PATH, abs_hooks_path)
    content = content.replace(SOURCE_REPO_BIN_PATH, abs_bin_path)

    content = content.replace(" " + HOOKS_PATH_PATTERN, " " + abs_hooks_path)
    content = content.replace('"' + HOOKS_PATH_PATTERN, '"' + abs_hooks_path)
    content = content.replace(" " + BIN_PATH_PATTERN, " " + abs_bin_path)
    content = content.replace('"' + BIN_PATH_PATTERN, '"' + abs_bin_path)

    return content


def process_settings(settings_content: str, enable_python: bool, enable_typescript: bool, enable_golang: bool) -> str:
    """Process settings JSON, optionally removing Python/TypeScript/Go-specific hooks.

    Args:
        settings_content: Raw JSON content of the settings file
        enable_python: Whether Python support is enabled
        enable_typescript: Whether TypeScript support is enabled
        enable_golang: Whether Go support is enabled

    Returns:
        Processed JSON string with hooks removed based on enable flags
    """
    config: dict[str, Any] = json.loads(settings_content)

    files_to_remove: list[str] = []
    if not enable_python:
        files_to_remove.append("file_checker_python.py")
    if not enable_typescript:
        files_to_remove.append("file_checker_ts.py")
    if not enable_golang:
        files_to_remove.append("file_checker_go.py")

    if files_to_remove:
        try:
            for hook_group in config["hooks"]["PostToolUse"]:
                hook_group["hooks"] = [
                    h for h in hook_group["hooks"] if not any(f in h.get("command", "") for f in files_to_remove)
                ]
        except (KeyError, TypeError, AttributeError):
            pass

    return json.dumps(config, indent=2) + "\n"


class ClaudeFilesStep(BaseStep):
    """Step that installs .claude directory files from the repository."""

    name = "claude_files"

    def check(self, ctx: InstallContext) -> bool:
        """Check if .claude files are already installed.

        Note: Always returns False to ensure settings.local.json is updated.
        This step is idempotent - files are overwritten without backup.
        """
        return False

    def run(self, ctx: InstallContext) -> None:
        """Install all .claude files from repository."""
        ui = ctx.ui

        repo_branch = "main"
        if ctx.target_version:
            if ctx.target_version.startswith("dev-"):
                repo_branch = ctx.target_version
            else:
                repo_branch = f"v{ctx.target_version}"

        config = DownloadConfig(
            repo_url="https://github.com/maxritter/claude-codepro",
            repo_branch=repo_branch,
            local_mode=ctx.local_mode,
            local_repo_dir=ctx.local_repo_dir,
        )

        if ui:
            ui.status("Installing .claude files...")

        claude_files = get_repo_files(".claude", config)

        if not claude_files:
            if ui:
                ui.warning("No .claude files found in repository")
                if not config.local_mode:
                    ui.print("  This may be due to GitHub API rate limiting.")
                    ui.print("  Try running with --local flag if you have the repo cloned.")
            return

        installed_files: list[str] = []
        file_count = 0
        failed_files: list[str] = []

        categories: dict[str, list[str]] = {
            "commands": [],
            "rules_standard": [],
            "rules": [],
            "hooks": [],
            "skills": [],
            "other": [],
        }

        for file_path in claude_files:
            if not file_path:
                continue

            if "__pycache__" in file_path:
                continue

            if file_path.endswith(".pyc"):
                continue

            if "/config/" in file_path:
                continue
            if "/bin/" in file_path:
                continue
            if "/installer/" in file_path:
                continue
            if "/claude-code-chat-images/" in file_path:
                continue
            if file_path.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                continue
            if Path(file_path).name == ".gitignore":
                continue

            if "/rules/custom/" in file_path:
                continue

            if not ctx.enable_python:
                if "file_checker_python.py" in file_path:
                    continue
                if "python-rules.md" in file_path:
                    continue

            if not ctx.enable_typescript:
                if "file_checker_ts.py" in file_path:
                    continue
                if "typescript-rules.md" in file_path:
                    continue

            if not ctx.enable_golang:
                if "file_checker_go.py" in file_path:
                    continue
                if "golang-rules.md" in file_path:
                    continue

            if not ctx.enable_agent_browser:
                if "agent-browser.md" in file_path:
                    continue

            if "/commands/" in file_path:
                categories["commands"].append(file_path)
            elif "/rules/standard/" in file_path:
                categories["rules_standard"].append(file_path)
            elif "/rules/" in file_path:
                categories["rules"].append(file_path)
            elif "/hooks/" in file_path:
                categories["hooks"].append(file_path)
            elif "/skills/" in file_path:
                skill_name = Path(file_path).parent.name
                if skill_name.startswith("standards-"):
                    categories["skills"].append(file_path)
            elif "/scripts/" in file_path:
                continue
            else:
                categories["other"].append(file_path)

        category_names = {
            "commands": "slash commands",
            "rules_standard": "standard rules",
            "rules": "custom rules",
            "hooks": "hooks",
            "skills": "skills",
            "other": "config files",
        }

        source_is_destination = (
            config.local_mode and config.local_repo_dir and config.local_repo_dir.resolve() == ctx.project_dir.resolve()
        )

        if not source_is_destination:
            dirs_to_clear = [
                ("hooks", categories["hooks"], ctx.project_dir / ".claude" / "hooks"),
                ("standard rules", categories["rules_standard"], ctx.project_dir / ".claude" / "rules" / "standard"),
            ]

            for name, has_files, dir_path in dirs_to_clear:
                if dir_path.exists() and has_files:
                    try:
                        shutil.rmtree(dir_path)
                    except (OSError, IOError) as e:
                        if ui:
                            ui.warning(f"Failed to clear {name} directory: {e}")

            commands_dir = ctx.project_dir / ".claude" / "commands"
            if commands_dir.exists() and categories["commands"]:
                standard_command_names = {"spec", "sync", "plan", "implement", "verify"}
                for cmd_file in commands_dir.iterdir():
                    if cmd_file.is_file() and cmd_file.suffix == ".md":
                        name = cmd_file.stem
                        if name in standard_command_names:
                            try:
                                cmd_file.unlink()
                            except (OSError, IOError) as e:
                                if ui:
                                    ui.warning(f"Failed to clear command {name}: {e}")

            skills_dir = ctx.project_dir / ".claude" / "skills"
            if skills_dir.exists():
                migrated_to_commands = {"plan", "implement", "verify"}
                for skill_subdir in skills_dir.iterdir():
                    if skill_subdir.is_dir():
                        name = skill_subdir.name
                        if name in migrated_to_commands or name.startswith("standards-"):
                            try:
                                shutil.rmtree(skill_subdir)
                            except (OSError, IOError) as e:
                                if ui:
                                    ui.warning(f"Failed to clear skill {name}: {e}")

            scripts_dir = ctx.project_dir / ".claude" / "scripts"
            if scripts_dir.exists():
                try:
                    shutil.rmtree(scripts_dir)
                except (OSError, IOError) as e:
                    if ui:
                        ui.warning(f"Failed to remove scripts directory: {e}")

        for category, files in categories.items():
            if not files:
                continue

            if ui:
                with ui.spinner(f"Installing {category_names[category]}..."):
                    for file_path in files:
                        dest_file = ctx.project_dir / file_path
                        if Path(file_path).name == SETTINGS_FILE:
                            success = self._install_settings(
                                file_path,
                                dest_file,
                                config,
                                ctx.enable_python,
                                ctx.enable_typescript,
                                ctx.enable_golang,
                                ctx.project_dir,
                            )
                            if success:
                                file_count += 1
                                installed_files.append(str(dest_file))
                            else:
                                failed_files.append(file_path)
                        elif download_file(file_path, dest_file, config):
                            file_count += 1
                            installed_files.append(str(dest_file))
                        else:
                            failed_files.append(file_path)
                ui.success(f"Installed {len(files)} {category_names[category]}")
                if not ui.quiet:
                    for file_path in files:
                        if category == "skills":
                            file_name = Path(file_path).parent.name
                        else:
                            file_name = Path(file_path).stem
                        ui.print(f"    [dim]✓ {file_name}[/dim]")
            else:
                for file_path in files:
                    dest_file = ctx.project_dir / file_path
                    if Path(file_path).name == SETTINGS_FILE:
                        success = self._install_settings(
                            file_path,
                            dest_file,
                            config,
                            ctx.enable_python,
                            ctx.enable_typescript,
                            ctx.enable_golang,
                            ctx.project_dir,
                        )
                        if success:
                            file_count += 1
                            installed_files.append(str(dest_file))
                        else:
                            failed_files.append(file_path)
                    elif download_file(file_path, dest_file, config):
                        file_count += 1
                        installed_files.append(str(dest_file))
                    else:
                        failed_files.append(file_path)

        ctx.config["installed_files"] = installed_files

        hooks_dir = ctx.project_dir / ".claude" / "hooks"
        if hooks_dir.exists():
            for hook_file in hooks_dir.glob("*.sh"):
                hook_file.chmod(0o755)
            for hook_file in hooks_dir.glob("*.py"):
                hook_file.chmod(0o755)

        custom_dir = ctx.project_dir / ".claude" / "rules" / "custom"
        if not custom_dir.exists():
            custom_dir.mkdir(parents=True, exist_ok=True)
            (custom_dir / ".gitkeep").touch()

        skills_dir = ctx.project_dir / ".claude" / "skills"
        if not skills_dir.exists():
            skills_dir.mkdir(parents=True, exist_ok=True)

        if ui:
            if file_count > 0:
                ui.success(f"Installed {file_count} .claude files")
            else:
                ui.warning("No .claude files were installed")

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
        install_python: bool,
        install_typescript: bool,
        install_golang: bool,
        project_dir: Path,
    ) -> bool:
        """Download and process settings file.

        Args:
            source_path: Path to settings file in repository
            dest_path: Local destination path
            config: Download configuration
            install_python: Whether Python support is being installed
            install_typescript: Whether TypeScript support is being installed
            install_golang: Whether Go support is being installed
            project_dir: Project directory for absolute hook paths

        Returns:
            True if successful, False otherwise
        """
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = Path(tmpdir) / "settings.json"
            if not download_file(source_path, temp_file, config):
                return False

            try:
                settings_content = temp_file.read_text()
                processed_content = process_settings(
                    settings_content, install_python, install_typescript, install_golang
                )
                processed_content = patch_claude_paths(processed_content, project_dir)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_text(processed_content)
                return True
            except (json.JSONDecodeError, OSError, IOError):
                return False
