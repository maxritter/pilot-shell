"""Cross-platform utilities for the installer."""

from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path


def has_nvidia_gpu(verbose: bool = False) -> bool | dict[str, object]:
    """Check if NVIDIA GPU is available via nvidia-smi or /dev/nvidia* fallback.

    Args:
        verbose: If True, return dict with diagnostic info instead of bool.

    Returns:
        bool if verbose=False, dict with detection details if verbose=True.
    """
    result_info: dict[str, object] = {
        "detected": False,
        "method": None,
        "error": None,
        "nvidia_smi_output": None,
    }

    try:
        proc = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            timeout=10,
        )
        if proc.returncode == 0:
            result_info["detected"] = True
            result_info["method"] = "nvidia_smi"
            result_info["nvidia_smi_output"] = proc.stdout.decode("utf-8", errors="replace")[:500]
            return result_info if verbose else True
        else:
            result_info["error"] = f"nvidia-smi exited with code {proc.returncode}"
            stderr = proc.stderr.decode("utf-8", errors="replace")[:200]
            if stderr:
                result_info["error"] += f": {stderr}"
    except FileNotFoundError as e:
        result_info["error"] = f"nvidia-smi not found: {e}"
    except subprocess.TimeoutExpired:
        result_info["error"] = "nvidia-smi timed out after 10 seconds"
    except OSError as e:
        result_info["error"] = f"OSError running nvidia-smi: {e}"
    except subprocess.SubprocessError as e:
        result_info["error"] = f"SubprocessError running nvidia-smi: {e}"

    try:
        nvidia_devices = list(Path("/dev").glob("nvidia*"))
        if nvidia_devices:
            result_info["detected"] = True
            result_info["method"] = "dev_nvidia"
            result_info["nvidia_devices"] = [str(d) for d in nvidia_devices[:5]]
            return result_info if verbose else True
    except (OSError, PermissionError) as e:
        if result_info["error"]:
            result_info["error"] += f"; /dev/nvidia* check failed: {e}"
        else:
            result_info["error"] = f"/dev/nvidia* check failed: {e}"

    return result_info if verbose else False


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == "Linux"


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"


def is_wsl() -> bool:
    """Check if running in Windows Subsystem for Linux."""
    if not is_linux():
        return False
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower()
    except (OSError, IOError):
        return False


def is_in_devcontainer() -> bool:
    """Check if running inside a dev container."""
    return Path("/.dockerenv").exists() or Path("/run/.containerenv").exists()


def command_exists(command: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(command) is not None


def is_homebrew_available() -> bool:
    """Check if Homebrew is available."""
    return shutil.which("brew") is not None


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
