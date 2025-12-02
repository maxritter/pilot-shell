"""Premium features step - handles license validation and binary installation."""

from __future__ import annotations

import json
import platform
import stat
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING

from installer.steps.base import BaseStep

if TYPE_CHECKING:
    from installer.context import InstallContext

GUMROAD_VERIFY_URL = "https://api.gumroad.com/v2/licenses/verify"
PRODUCT_ID = "c3Sr8oRvWIimCH1zf5I02w=="
GITHUB_REPO = "maxritter/claude-codepro"


def get_platform_binary_name() -> str:
    """Get the correct binary name for the current platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine

    if system == "darwin":
        return f"ccp-premium-darwin-{arch}"
    elif system == "linux":
        return f"ccp-premium-linux-{arch}"
    elif system == "windows":
        return f"ccp-premium-windows-{arch}.exe"
    else:
        return f"ccp-premium-{system}-{arch}"


def validate_license_key(license_key: str) -> tuple[bool, str]:
    """Validate license key with Gumroad API."""
    try:
        data = urllib.parse.urlencode(
            {
                "product_id": PRODUCT_ID,
                "license_key": license_key,
                "increment_uses_count": "false",
            }
        ).encode()

        request = urllib.request.Request(
            GUMROAD_VERIFY_URL,
            data=data,
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode())

            if result.get("success"):
                purchase = result.get("purchase", {})
                if purchase.get("refunded"):
                    return False, "License has been refunded"
                if purchase.get("disputed"):
                    return False, "License is disputed"

                uses = result.get("uses", 0)
                return True, f"License valid (activation #{uses})"

            return False, result.get("message", "Invalid license key")

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "Invalid license key"
        return False, f"License server error: HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, f"Network error: {e.reason}"
    except json.JSONDecodeError:
        return False, "Invalid response from license server"
    except Exception as e:
        return False, f"Validation error: {e}"


def download_premium_binary(
    dest_dir: Path,
    version: str,
    local_mode: bool = False,
    local_repo_dir: Path | None = None,
) -> tuple[bool, str]:
    """Download premium binary from GitHub releases or copy from local dist."""
    import shutil

    binary_name = get_platform_binary_name()
    dest_path = dest_dir / "ccp-premium"

    if local_mode and local_repo_dir:
        source_path = local_repo_dir / "premium" / "dist" / binary_name
        if not source_path.exists():
            return False, f"Premium binary not found at {source_path}"

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            dest_path.chmod(dest_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            return True, str(dest_path)
        except Exception as e:
            return False, f"Copy error: {e}"

    url = f"https://github.com/{GITHUB_REPO}/releases/download/{version}/{binary_name}"

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "claude-codepro-installer/1.0"},
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(response.read())
            dest_path.chmod(dest_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            return True, str(dest_path)

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "Premium binary not found (release may not exist yet)"
        return False, f"Download failed: HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, f"Network error: {e}"
    except Exception as e:
        return False, f"Download error: {e}"


def save_env_var(project_dir: Path, var_name: str, value: str) -> None:
    """Save an environment variable to .env file."""
    env_file = project_dir / ".env"

    existing_lines: list[str] = []
    if env_file.exists():
        existing_lines = env_file.read_text().splitlines()

    filtered_lines = [line for line in existing_lines if not line.startswith(f"{var_name}=")]
    filtered_lines.append(f"{var_name}={value}")

    env_file.write_text("\n".join(filtered_lines) + "\n")


def remove_premium_hooks_from_settings(settings_file: Path) -> bool:
    """Remove all premium hooks from settings.local.json for non-premium users."""
    if not settings_file.exists():
        return False

    try:
        settings = json.loads(settings_file.read_text())

        if "hooks" not in settings:
            return True

        # Remove premium hooks from all hook types
        for hook_type in ["PreToolUse", "PostToolUse", "Stop"]:
            if hook_type in settings["hooks"]:
                settings["hooks"][hook_type] = [
                    hook_group
                    for hook_group in settings["hooks"][hook_type]
                    if not any("ccp-premium" in h.get("command", "") for h in hook_group.get("hooks", []))
                ]
                # Remove empty hook arrays
                if not settings["hooks"][hook_type]:
                    del settings["hooks"][hook_type]

        # Remove hooks key if empty
        if not settings["hooks"]:
            del settings["hooks"]

        settings_file.write_text(json.dumps(settings, indent=2) + "\n")
        return True
    except (json.JSONDecodeError, OSError):
        return False


class PremiumStep(BaseStep):
    """Step that handles premium license validation and binary installation."""

    name = "premium"

    def check(self, ctx: InstallContext) -> bool:
        """Check if premium setup is needed."""
        settings_file = ctx.project_dir / ".claude" / "settings.local.json"

        # If no premium key, check if we need to clean up premium hooks
        if not ctx.premium_key:
            # Check if settings file has premium hooks that need removal
            if settings_file.exists():
                try:
                    settings = json.loads(settings_file.read_text())
                    hooks = settings.get("hooks", {})
                    for hook_type in ["PreToolUse", "PostToolUse", "Stop"]:
                        for hook_group in hooks.get(hook_type, []):
                            for hook in hook_group.get("hooks", []):
                                if "ccp-premium" in hook.get("command", ""):
                                    return False  # Need to run cleanup
                except (json.JSONDecodeError, OSError):
                    pass
            return True  # No cleanup needed

        # Check if premium binary already exists
        bin_dir = ctx.project_dir / ".claude" / "bin"
        if (bin_dir / "ccp-premium").exists():
            return True

        return False

    def run(self, ctx: InstallContext) -> None:
        """Handle premium features installation."""
        ui = ctx.ui
        settings_file = ctx.project_dir / ".claude" / "settings.local.json"

        # If no premium key, remove premium hooks and return
        if not ctx.premium_key:
            if ui:
                ui.status("Skipping premium features (no license key)")
            remove_premium_hooks_from_settings(settings_file)
            return

        if ui:
            ui.section("Premium Features")
            ui.status("Validating license key...")

        # Validate license
        valid, message = validate_license_key(ctx.premium_key)
        if not valid:
            if ui:
                ui.error(f"License validation failed: {message}")
            remove_premium_hooks_from_settings(settings_file)
            return

        if ui:
            ui.success(message)

        # Save license to .env
        save_env_var(ctx.project_dir, "CCP_LICENSE_KEY", ctx.premium_key)
        if ui:
            ui.success("Saved license key to .env")

        # Download premium binary
        if ctx.local_mode:
            if ui:
                ui.status("Copying premium binary from local dist...")
        else:
            if ui:
                ui.status("Downloading premium binary...")

        bin_dir = ctx.project_dir / ".claude" / "bin"
        success, result = download_premium_binary(
            bin_dir,
            "latest",  # Use latest release
            ctx.local_mode,
            ctx.local_repo_dir,
        )

        if not success:
            if ui:
                ui.error(f"{'Copy' if ctx.local_mode else 'Download'} failed: {result}")
                ui.warning("Premium features will not be available")
            remove_premium_hooks_from_settings(settings_file)
            return

        if ui:
            ui.success(f"Installed premium binary to {result}")

        # Prompt for Gemini API key (if interactive)
        if not ctx.non_interactive and ui:
            ui.print()
            ui.section("Rules Supervisor (Gemini API)")
            ui.status("The Rules Supervisor uses Gemini to analyze coding sessions.")
            ui.print("  • Cost: Very low (~$0.01 per session analysis)")
            ui.print("  • Get API key at: https://aistudio.google.com/apikey")
            ui.print()

            if ui.confirm("Configure Gemini API key?", default=False):
                gemini_key = ui.password("Enter your Gemini API key")
                if gemini_key:
                    save_env_var(ctx.project_dir, "GEMINI_API_KEY", gemini_key)
                    ui.success("Saved Gemini API key to .env")
                else:
                    ui.warning("No key entered. Rules Supervisor will be disabled.")

        if ui:
            ui.success("Premium features enabled")

    def rollback(self, ctx: InstallContext) -> None:
        """Remove premium binary and env entries."""
        import shutil

        bin_dir = ctx.project_dir / ".claude" / "bin"
        premium_binary = bin_dir / "ccp-premium"
        if premium_binary.exists():
            premium_binary.unlink()

        # Note: We don't remove .env entries as that could be disruptive
