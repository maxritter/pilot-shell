"""Claude files installation step - installs pilot directory files."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
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
from installer.steps.config_migration import migrate_model_config
from installer.steps.settings_merge import (
    cleanup_managed_files,
    load_manifest,
    merge_app_config,
    merge_settings,
    save_manifest,
)

SETTINGS_FILE = "settings.json"
SETTINGS_BASELINE_FILE = ".pilot-settings-baseline.json"
PILOT_MANIFEST_FILE = ".pilot-manifest.json"


REPO_URL = "https://github.com/maxritter/pilot-shell"

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


def get_claude_config_dir() -> Path:
    """Resolve the Claude config directory from CLAUDE_CONFIG_DIR env var.

    Returns Path(CLAUDE_CONFIG_DIR) if set, otherwise ~/.claude.
    Raises ValueError if CLAUDE_CONFIG_DIR is set to a relative path.
    """
    env_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if env_dir:
        p = Path(env_dir)
        if not p.is_absolute():
            raise ValueError(f"CLAUDE_CONFIG_DIR must be an absolute path, got: {env_dir}")
        return p
    return Path.home() / ".claude"


def patch_claude_paths(content: str) -> str:
    """Expand ~/.pilot/bin/ paths to absolute paths."""
    home = Path.home()
    abs_bin_path = str(home / ".pilot" / "bin") + "/"
    return content.replace('"~/.pilot/bin/', '"' + abs_bin_path)


def process_settings(settings_content: str) -> str:
    """Process settings JSON - parse and re-serialize with consistent formatting."""
    config: dict[str, Any] = json.loads(settings_content)
    return json.dumps(config, indent=2) + "\n"


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
    elif "/skills/" in file_path:
        return "skills"
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
            "skills": [],
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
        """Clean up Pilot-managed files before reinstallation.

        Uses manifests to track which files Pilot installed. Only removes
        Pilot-managed files — user-created files in commands/ and rules/ are preserved.
        """
        home_claude_dir = get_claude_config_dir()
        home_pilot_plugin_dir = home_claude_dir / "pilot"

        self._cleanup_legacy_standards_skills(home_pilot_plugin_dir)

        _clear_directory_contents(home_pilot_plugin_dir)

        source_is_destination = (
            config.local_mode and config.local_repo_dir and config.local_repo_dir.resolve() == ctx.project_dir.resolve()
        )
        if source_is_destination:
            return

        manifest_path = home_claude_dir / PILOT_MANIFEST_FILE
        if not manifest_path.exists():
            self._seed_manifest_from_existing(home_claude_dir, manifest_path)
        cleanup_managed_files(home_claude_dir / "commands", manifest_path, "commands/")
        cleanup_managed_files(home_claude_dir / "skills", manifest_path, "skills/")
        cleanup_managed_files(home_claude_dir / "rules", manifest_path, "rules/")

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

    def _seed_manifest_from_existing(self, home_claude_dir: Path, manifest_path: Path) -> None:
        """Seed manifest from existing files for legacy upgrades.

        When upgrading from a pre-manifest Pilot version, no manifest exists yet.
        The old installer nuked these directories entirely, so all existing files
        are Pilot-managed. Seed the manifest with them so cleanup_managed_files
        can remove stale ones while future user-added files remain safe.
        """
        files: set[str] = set()
        for subdir in ("commands", "rules"):
            directory = home_claude_dir / subdir
            if not directory.exists():
                continue
            for item in directory.iterdir():
                if item.name.startswith("."):
                    continue
                files.add(f"{subdir}/{item.name}")
        if files:
            save_manifest(manifest_path, files)

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
            "skills": "skills",
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
            ui.success(self._format_install_summary(category, category_display_name, file_infos))
        else:
            install_files()

        return len(installed), installed, failed

    def _format_install_summary(
        self,
        category: str,
        category_display_name: str,
        file_infos: list,
    ) -> str:
        """Summarize an install run. For skills, report skill count + file count
        separately since a single decomposed skill contains manifest.json,
        orchestrator.md, and step fragments — raw file counts mislead users.
        """
        file_count = len(file_infos)
        if category == "skills":
            skill_names: set[str] = set()
            for fi in file_infos:
                # fi.path is like "pilot/skills/<skill-name>/..."
                parts = Path(fi.path).parts
                if len(parts) >= 3 and parts[0] == "pilot" and parts[1] == "skills":
                    skill_names.add(parts[2])
            skill_count = len(skill_names)
            if skill_count:
                file_word = "file" if file_count == 1 else "files"
                return f"Installed {skill_count} skills ({file_count} {file_word})"
        return f"Installed {file_count} {category_display_name}"

    def _get_dest_path(self, category: str, file_path: str, ctx: InstallContext) -> Path:
        """Determine destination path based on category."""
        home_claude_dir = get_claude_config_dir()
        home_pilot_plugin_dir = home_claude_dir / "pilot"

        if category == "skills":
            rel_path = Path(file_path).relative_to("pilot/skills")
            return home_claude_dir / "skills" / rel_path
        elif category == "rules":
            rel_path = Path(file_path).relative_to("pilot/rules")
            return home_claude_dir / "rules" / rel_path
        elif category == "pilot_plugin":
            rel_path = Path(file_path).relative_to("pilot")
            return home_pilot_plugin_dir / rel_path
        elif category == "settings":
            return home_claude_dir / SETTINGS_FILE
        else:
            return ctx.project_dir / file_path

    def _post_install_processing(self, ctx: InstallContext, ui: Any) -> None:
        """Run post-installation processing tasks."""
        home_pilot_plugin_dir = get_claude_config_dir() / "pilot"

        self._make_scripts_executable(home_pilot_plugin_dir)

        self._update_lsp_config(home_pilot_plugin_dir)

        if not ctx.local_mode:
            self._update_hooks_config(home_pilot_plugin_dir)

        self._merge_app_config()
        migrate_model_config()
        self._cleanup_stale_managed_files(ctx)
        self._build_skill_md_files(ctx, ui)
        self._save_pilot_manifest(ctx)
        self._reapply_customization(ui)

    def _save_pilot_manifest(self, ctx: InstallContext) -> None:
        """Save manifest of Pilot-managed files in skills/ and rules/.

        Records filenames (relative to ~/.claude/) so the next update
        can selectively remove only Pilot's files, preserving user files.
        """
        home_claude_dir = get_claude_config_dir()
        installed = ctx.config.get("installed_files", [])

        skills_dir = home_claude_dir / "skills"
        rules_dir = home_claude_dir / "rules"
        managed_files: set[str] = set()

        for filepath_str in installed:
            filepath = Path(filepath_str)
            try:
                if filepath.is_relative_to(skills_dir):
                    managed_files.add("skills/" + str(filepath.relative_to(skills_dir)))
                elif filepath.is_relative_to(rules_dir):
                    managed_files.add("rules/" + str(filepath.relative_to(rules_dir)))
            except (ValueError, TypeError):
                continue

        save_manifest(home_claude_dir / PILOT_MANIFEST_FILE, managed_files)

    def _build_skill_md_files(self, ctx: InstallContext, ui: Any) -> None:
        """Generate SKILL.md for each decomposed skill by concatenating fragments in-process.

        Iterates ~/.claude/skills/*/ and builds for any skill directory containing
        manifest.json. Skills without manifest.json are skipped (legacy monolithic
        skills copied as-is during the fragment+manifest rollout window).

        Builds in-process via the vendored installer.skill_builder — keeps the
        installer independent of the pilot binary at runtime
        (.claude/rules/pilot-shell-package-boundaries.md). Failures must be fatal:
        a silent continue would leave ~/.claude/skills/<skill>/SKILL.md missing,
        breaking /spec.

        Recovery is lazy: only on BuildError do we re-download missing fragments
        and retry once. This self-heals transient download failures (flaky
        networks, proxy hiccups) without paying stat-every-fragment overhead on
        the happy path.
        """
        from installer.skill_builder import BuildError, write_skill_md

        skills_dir = get_claude_config_dir() / "skills"
        if not skills_dir.is_dir():
            return

        decomposed = [p for p in sorted(skills_dir.iterdir()) if p.is_dir() and (p / "manifest.json").is_file()]
        if not decomposed:
            return  # nothing to build — legacy monolithic skills or no skills installed

        config = self._create_download_config(ctx)
        installed_files: list[str] = list(ctx.config.get("installed_files", []))

        failures: list[str] = []
        for skill_dir in decomposed:
            first_err: BuildError | OSError | None = None
            try:
                write_skill_md(skill_dir)
                continue
            except (BuildError, OSError) as err:
                first_err = err

            recovered = self._recover_missing_fragments(skill_dir, config, ui)
            if recovered:
                installed_files.extend(recovered)
                try:
                    write_skill_md(skill_dir)
                    continue
                except (BuildError, OSError) as retry_err:
                    failures.append(f"{skill_dir.name}: {retry_err}")
                    self._log_skill_dir_diagnostics(skill_dir, config, ui)
                    continue

            failures.append(f"{skill_dir.name}: {first_err}")
            self._log_skill_dir_diagnostics(skill_dir, config, ui)

        ctx.config["installed_files"] = installed_files

        if failures:
            if ui:
                for msg in failures:
                    ui.error(f"⚠ SKILL.md generation FAILED — {msg}")
            raise RuntimeError(
                "skill-build failed for "
                + str(len(failures))
                + " skill(s); aborting install before manifests are finalized. "
                "Affected: " + ", ".join(f.split(":", 1)[0] for f in failures)
            )

    def _recover_missing_fragments(
        self,
        skill_dir: Path,
        config: DownloadConfig,
        ui: Any,
    ) -> list[str]:
        """Ensure all fragments referenced by manifest.json exist on disk.

        Returns a list of absolute dest paths that were successfully re-downloaded
        (empty when nothing was missing or every download failed). Missing
        fragments are re-fetched from the repository. Two-stage recovery:
        (1) the parallel-install helper `download_file`, (2) a single-threaded
        urllib fallback with expanded diagnostics so a persistent failure gives
        actionable error output (URL, HTTP status, exception type).
        """
        try:
            manifest_data = json.loads((skill_dir / "manifest.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(manifest_data, dict):
            return []

        skills_dir = get_claude_config_dir() / "skills"
        required: list[str] = []
        orchestrator = manifest_data.get("orchestrator")
        if isinstance(orchestrator, str) and orchestrator:
            required.append(orchestrator)
        for step in manifest_data.get("steps", []) or []:
            if isinstance(step, dict):
                rel = step.get("file")
                if isinstance(rel, str) and rel:
                    required.append(rel)

        recovered: list[str] = []
        for rel_path in required:
            dest = skill_dir / rel_path
            if dest.is_file():
                continue

            try:
                skill_rel = skill_dir.relative_to(skills_dir)
            except ValueError:
                continue
            repo_path = f"pilot/skills/{skill_rel}/{rel_path}"

            if ui:
                ui.warning(f"Missing fragment after install: {dest} — attempting recovery")

            if download_file(repo_path, dest, config) and dest.is_file():
                recovered.append(str(dest))
                continue

            # Stage 2: single-threaded urllib fallback with diagnostics.
            if self._direct_download_with_diagnostics(repo_path, dest, config, ui):
                recovered.append(str(dest))

        return recovered

    def _direct_download_with_diagnostics(
        self,
        repo_path: str,
        dest: Path,
        config: DownloadConfig,
        ui: Any,
    ) -> bool:
        """Direct urllib download that reports URL, status, and exception on failure.

        Bypasses the thread pool entirely (useful when ThreadPoolExecutor +
        DrvFs on WSL2 is suspected), reads the full body synchronously, writes
        atomically via temp + os.replace. Returns True only when the file is on
        disk with non-zero size after the write.
        """
        import urllib.error
        import urllib.request

        from installer.downloads import _get_ssl_context

        if config.local_mode and config.local_repo_dir:
            source_file = config.local_repo_dir / repo_path
            if not source_file.is_file():
                if ui:
                    ui.error(f"  diagnostic: local source missing: {source_file}")
                return False
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(source_file.read_bytes())
                return dest.is_file() and dest.stat().st_size > 0
            except OSError as e:
                if ui:
                    ui.error(f"  diagnostic: local copy failed: {type(e).__name__}: {e}")
                return False

        file_url = f"{config.repo_url}/raw/{config.repo_branch}/{repo_path}"
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            request = urllib.request.Request(file_url)
            with urllib.request.urlopen(request, timeout=60.0, context=_get_ssl_context()) as response:
                status = getattr(response, "status", None)
                if status != 200:
                    if ui:
                        ui.error(f"  diagnostic: {file_url} returned HTTP {status}")
                    return False
                body = response.read()
        except urllib.error.HTTPError as e:
            if ui:
                ui.error(f"  diagnostic: {file_url} HTTPError {e.code} {e.reason}")
            return False
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            if ui:
                ui.error(f"  diagnostic: {file_url} {type(e).__name__}: {e}")
            return False

        if not body:
            if ui:
                ui.error(f"  diagnostic: {file_url} returned empty body")
            return False

        tmp = dest.with_suffix(dest.suffix + ".tmp")
        try:
            tmp.write_bytes(body)
            os.replace(str(tmp), str(dest))
        except OSError as e:
            if ui:
                ui.error(f"  diagnostic: write to {dest} failed: {type(e).__name__}: {e}")
            return False

        return dest.is_file() and dest.stat().st_size > 0

    def _log_skill_dir_diagnostics(
        self,
        skill_dir: Path,
        config: DownloadConfig,
        ui: Any,
    ) -> None:
        """Dump on-disk state of a failed skill plus the URLs its manifest expected.

        Runs only when skill-build fails — so the operator sees exactly what's
        on disk vs. what's missing, with the exact URL that would have been
        used. Cheap and safe to emit: a few `ui.print` lines per failure.
        """
        if not ui:
            return

        try:
            ui.print(f"  diagnostic: skill dir = {skill_dir}")
        except Exception:
            return

        try:
            entries = sorted(p.relative_to(skill_dir).as_posix() for p in skill_dir.rglob("*") if p.is_file())
            ui.print(f"  diagnostic: on-disk files ({len(entries)}):")
            for entry in entries:
                full = skill_dir / entry
                size = full.stat().st_size if full.is_file() else 0
                ui.print(f"    - {entry} ({size} bytes)")
        except OSError as e:
            ui.print(f"  diagnostic: could not list skill dir: {type(e).__name__}: {e}")

        manifest_path = skill_dir / "manifest.json"
        if not manifest_path.is_file():
            ui.print("  diagnostic: manifest.json missing from skill dir")
            return

        try:
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            ui.print(f"  diagnostic: manifest.json unreadable: {type(e).__name__}: {e}")
            return

        skills_dir = get_claude_config_dir() / "skills"
        try:
            skill_rel = skill_dir.relative_to(skills_dir)
        except ValueError:
            return

        required: list[str] = []
        orchestrator = manifest_data.get("orchestrator")
        if isinstance(orchestrator, str) and orchestrator:
            required.append(orchestrator)
        for step in manifest_data.get("steps", []) or []:
            if isinstance(step, dict):
                rel = step.get("file")
                if isinstance(rel, str) and rel:
                    required.append(rel)

        ui.print(f"  diagnostic: manifest expects {len(required)} fragment file(s):")
        for rel in required:
            exists = (skill_dir / rel).is_file()
            url = f"{config.repo_url}/raw/{config.repo_branch}/pilot/skills/{skill_rel}/{rel}"
            marker = "OK" if exists else "MISSING"
            ui.print(f"    [{marker}] {rel}  <- {url}")

    def _reapply_customization(self, ui: Any) -> None:
        """Re-apply customization after core file installation.

        Reads ~/.pilot/config.json for an active customization, then calls
        the pilot binary to update and re-apply it. Non-fatal: warns on
        failure but never breaks the core install.
        """
        config_path = Path.home() / ".pilot" / "config.json"
        if not config_path.is_file():
            return

        try:
            raw = json.loads(config_path.read_text())
        except (json.JSONDecodeError, OSError):
            return

        cust = raw.get("customization")
        if not isinstance(cust, dict) or not cust.get("source"):
            return

        pilot_bin = Path.home() / ".pilot" / "bin" / "pilot"
        if not pilot_bin.is_file():
            if ui:
                ui.warning("Pilot binary not found — skipping customization re-apply")
            return

        try:
            # Try update first (pulls latest from remote + applies)
            result = subprocess.run(
                [str(pilot_bin), "customize", "update", "--quiet", "--json"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                # Fall back to apply from cache (no network needed)
                fallback = subprocess.run(
                    [str(pilot_bin), "customize", "apply", "--quiet", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if fallback.returncode != 0 and ui:
                    ui.error(
                        f"⚠ Customization reapply FAILED (update: {result.returncode}, "
                        f"apply: {fallback.returncode}) — your custom workflow may be broken. "
                        f"Run `pilot customize status` after install."
                    )
        except (subprocess.SubprocessError, OSError) as e:
            if ui:
                ui.error(
                    f"⚠ Customization reapply FAILED: {e} — your custom workflow may be broken. "
                    f"Run `pilot customize status` after install."
                )

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

    def _merge_app_config(self) -> None:
        """Merge app-level preferences from pilot/claude.json into ~/.claude.json.

        Uses three-way merge with baseline to preserve user customizations.
        Reads the installed claude.json template and merges its keys into the
        user's ~/.claude.json. Preserves all existing app state (projects,
        oauthAccount, caches, etc.) — only sets/updates keys defined in the template.
        """
        template_path = get_claude_config_dir() / "pilot" / "claude.json"
        if not template_path.exists():
            return

        claude_json_path = Path.home() / ".claude.json"
        baseline_path = get_claude_config_dir() / ".pilot-claude-baseline.json"

        try:
            source = json.loads(template_path.read_text())
        except (json.JSONDecodeError, OSError, IOError):
            return

        try:
            target = json.loads(claude_json_path.read_text()) if claude_json_path.exists() else {}
        except (json.JSONDecodeError, OSError, IOError):
            target = {}

        baseline: dict[str, Any] | None = None
        if baseline_path.exists():
            try:
                baseline = json.loads(baseline_path.read_text())
            except (json.JSONDecodeError, OSError, IOError):
                baseline = None

        patched = merge_app_config(target, source, baseline)
        if patched is not None:
            try:
                claude_json_path.write_text(json.dumps(patched, indent=2) + "\n")
            except (OSError, IOError):
                pass

        try:
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            baseline_path.write_text(json.dumps(source, indent=2) + "\n")
        except (OSError, IOError):
            pass

    def _cleanup_stale_managed_files(self, ctx: InstallContext) -> None:
        """Remove stale Pilot-managed files not present in this installation.

        Only removes files that Pilot previously installed (tracked in manifest)
        but are no longer part of the current installation. User-created files
        are never touched. Handles rules/, skills/, and legacy commands/ entries.
        """
        home_claude_dir = get_claude_config_dir()
        manifest_path = home_claude_dir / PILOT_MANIFEST_FILE
        previous_managed = load_manifest(manifest_path)
        installed = {Path(p).resolve() for p in ctx.config.get("installed_files", [])}

        for entry in previous_managed:
            file_path = home_claude_dir / entry
            if file_path.exists() and file_path.resolve() not in installed:
                try:
                    file_path.unlink()
                    parent = file_path.parent
                    if parent != home_claude_dir and parent.exists() and not any(parent.iterdir()):
                        parent.rmdir()
                except (OSError, IOError):
                    pass

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
        """Download, merge, and install settings to ~/.claude/settings.json.

        Uses three-way merge to preserve user customizations:
        - baseline (~/.claude/.pilot-settings-baseline.json) = what Pilot installed last time
        - current (~/.claude/settings.json) = what's on disk now (may have user changes)
        - incoming (downloaded settings.json) = new Pilot settings
        """
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = Path(tmpdir) / "settings.json"
            if not download_file(source_path, temp_file, config):
                return False

            try:
                raw_content = temp_file.read_text()
                processed_content = patch_claude_paths(process_settings(raw_content))
                incoming: dict[str, Any] = json.loads(processed_content)

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                baseline_path = dest_path.parent / SETTINGS_BASELINE_FILE

                current: dict[str, Any] | None = None
                baseline: dict[str, Any] | None = None

                if dest_path.exists():
                    try:
                        current = json.loads(dest_path.read_text())
                    except (json.JSONDecodeError, OSError, IOError):
                        current = None

                if baseline_path.exists():
                    try:
                        baseline = json.loads(baseline_path.read_text())
                    except (json.JSONDecodeError, OSError, IOError):
                        baseline = None

                if current is not None:
                    merged = merge_settings(baseline, current, incoming)
                else:
                    merged = incoming

                dest_path.write_text(json.dumps(merged, indent=2) + "\n")

                baseline_path.write_text(json.dumps(incoming, indent=2) + "\n")

                return True
            except (json.JSONDecodeError, OSError, IOError):
                return False
