"""Cross-platform utilities for the installer."""

from __future__ import annotations

import os
import shutil
import subprocess
import threading
from pathlib import Path


def has_nvidia_gpu() -> bool:
    """Check if NVIDIA GPU is available via nvidia-smi or /dev/nvidia* fallback."""
    try:
        proc = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError, subprocess.SubprocessError):
        pass

    try:
        nvidia_devices = list(Path("/dev").glob("nvidia*"))
        if nvidia_devices:
            return True
    except (OSError, PermissionError):
        pass

    return False


def command_exists(command: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(command) is not None


def needs_npm_sudo() -> bool:
    """Check if npm global installs require sudo.

    Returns True when the npm global prefix directory is not writable
    by the current user (e.g. /usr/lib/node_modules on system-wide installs).
    """
    if not command_exists("npm"):
        return False
    try:
        result = subprocess.run(
            ["npm", "prefix", "-g"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return False
        prefix = Path(result.stdout.strip())
        node_modules = prefix / "lib" / "node_modules"
        check_dir = node_modules if node_modules.exists() else prefix
        return not os.access(check_dir, os.W_OK)
    except Exception:
        return False


def npm_global_cmd(cmd: str) -> str:
    """Wrap an npm global command with sudo if needed.

    Uses sudo -n (non-interactive) so it fails fast if credentials
    aren't cached. Call ensure_sudo_credentials() first to prime them.
    """
    if needs_npm_sudo():
        return f"sudo -n {cmd}"
    return cmd


def needs_sudo() -> bool:
    """Check if any installer operations will require sudo.

    Only returns True when npm global installs actually need sudo
    (e.g. system-wide Node where prefix dir is not writable).
    Most users (nvm, Homebrew) never hit this.
    """
    return needs_npm_sudo()


def ensure_sudo_credentials() -> bool:
    """Prompt the user for sudo credentials and cache them.

    Runs `sudo -v` with inherited stdio so the user sees the password
    prompt and can type their password. Once authenticated, subsequent
    `sudo -n` commands succeed without prompting.

    Returns True if sudo credentials are available, False on failure.
    """
    try:
        result = subprocess.run(["sudo", "-v"], timeout=60)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


_sudo_keepalive_stop: threading.Event | None = None
_sudo_keepalive_thread: threading.Thread | None = None


def start_sudo_keepalive() -> None:
    """Start a background thread that refreshes sudo credentials every 60s.

    macOS caches sudo credentials for ~5 minutes by default. Long install
    sequences exceed this, causing `sudo -n` to fail and interactive sudo
    to hang inside spinners where the user can't see the password prompt.

    Call stop_sudo_keepalive() when elevated operations are done.
    """
    global _sudo_keepalive_stop, _sudo_keepalive_thread

    if _sudo_keepalive_thread is not None and _sudo_keepalive_thread.is_alive():
        return

    _sudo_keepalive_stop = None
    _sudo_keepalive_thread = None

    _sudo_keepalive_stop = threading.Event()
    stop_event = _sudo_keepalive_stop

    def _keepalive() -> None:
        while not stop_event.wait(timeout=60):
            try:
                subprocess.run(
                    ["sudo", "-vn"],
                    capture_output=True,
                    timeout=5,
                )
            except Exception:
                pass

    _sudo_keepalive_thread = threading.Thread(target=_keepalive, daemon=True)
    _sudo_keepalive_thread.start()


def stop_sudo_keepalive() -> None:
    """Stop the sudo keepalive background thread."""
    global _sudo_keepalive_stop, _sudo_keepalive_thread

    if _sudo_keepalive_stop is not None:
        _sudo_keepalive_stop.set()
    if _sudo_keepalive_thread is not None and _sudo_keepalive_thread.is_alive():
        _sudo_keepalive_thread.join(timeout=5)
    _sudo_keepalive_stop = None
    _sudo_keepalive_thread = None


def is_homebrew_available() -> bool:
    """Check if Homebrew is available."""
    return shutil.which("brew") is not None


def is_apt_available() -> bool:
    """Check if apt is available (Debian/Ubuntu Linux)."""
    return shutil.which("apt-get") is not None


def is_dnf_available() -> bool:
    """Check if dnf is available (RHEL 8+/AlmaLinux/Rocky/Fedora)."""
    return shutil.which("dnf") is not None


def is_yum_available() -> bool:
    """Check if yum is available (older RHEL/CentOS)."""
    return shutil.which("yum") is not None


def is_linux() -> bool:
    """Check if running on Linux."""
    import platform

    return platform.system() == "Linux"


def is_linux_arm64() -> bool:
    """Check if running on Linux ARM64 (aarch64)."""
    import platform

    return platform.system() == "Linux" and platform.machine() in ("aarch64", "arm64")


def is_macos_arm64() -> bool:
    """Check if running on macOS with Apple Silicon (M-series chip)."""
    import platform

    return platform.system() == "Darwin" and platform.machine() == "arm64"


def get_shell_config_files() -> list[Path]:
    """Get list of shell configuration files for the current user."""
    home = Path.home()
    configs = []

    bashrc = home / ".bashrc"
    bash_profile = home / ".bash_profile"
    if bashrc.exists():
        configs.append(bashrc)
    if bash_profile.exists():
        configs.append(bash_profile)

    zshrc = home / ".zshrc"
    if zshrc.exists():
        configs.append(zshrc)

    fish_config = home / ".config" / "fish" / "config.fish"
    if fish_config.exists():
        configs.append(fish_config)

    if not configs:
        configs = [bashrc, zshrc, fish_config]

    return configs
