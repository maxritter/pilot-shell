"""OS-native notification support for hooks.

Sends cross-platform notifications with thread-based timeout protection.
Plays sound via afplay (macOS) or paplay (Linux) independently of notification
permissions, ensuring audible alerts even when notification banners are blocked.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError

_warning_shown = False

_MACOS_SOUND = "/System/Library/Sounds/Glass.aiff"
_LINUX_SOUND = "/usr/share/sounds/freedesktop/stereo/complete.oga"


def _play_sound(system: str) -> None:
    """Play alert sound in background (fire-and-forget)."""
    try:
        if system == "Darwin":
            subprocess.Popen(
                ["afplay", _MACOS_SOUND],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Linux" and shutil.which("paplay"):
            subprocess.Popen(
                ["paplay", _LINUX_SOUND],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception:
        pass


def send_notification(title: str, message: str) -> None:
    """Send OS-native notification with sound.

    Args:
        title: Notification title
        message: Notification message

    Returns silently if platform unsupported or command not available.
    Thread-based timeout ensures function returns within 3 seconds.
    Sound is played independently via afplay/paplay as a fallback.
    """
    global _warning_shown

    system = platform.system()

    if system == "Darwin":
        cmd_name = "osascript"
        if not shutil.which(cmd_name):
            if not _warning_shown:
                print(f"[Pilot] Notifications disabled: {cmd_name} not found", file=sys.stderr)
                _warning_shown = True
            _play_sound(system)
            return

        safe_title = title.replace("\\", "\\\\").replace('"', '\\"')
        safe_message = message.replace("\\", "\\\\").replace('"', '\\"')
        cmd = [
            "osascript",
            "-e",
            f'display notification "{safe_message}" with title "{safe_title}" sound name "Glass"',
        ]
    elif system == "Linux":
        cmd_name = "notify-send"
        if not shutil.which(cmd_name):
            if not _warning_shown:
                print(f"[Pilot] Notifications disabled: {cmd_name} not found", file=sys.stderr)
                _warning_shown = True
            _play_sound(system)
            return

        cmd = ["notify-send", "--urgency=critical", title, message]
    else:
        return

    if system != "Darwin":
        _play_sound(system)

    def _run_notification():
        subprocess.run(cmd, capture_output=True, check=False)

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_notification)
            future.result(timeout=3)
    except TimeoutError:
        pass
    except Exception as e:
        print(f"[Pilot] Notification failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    send_notification("Pilot Test", "Notification system working!")
    print("Test notification sent (check your notification center)")
