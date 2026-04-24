"""Finalize step - runs final cleanup tasks and displays success."""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

from installer import __version__
from installer.context import InstallContext
from installer.steps.base import BaseStep


def _get_pilot_version() -> str:
    """Get version from Pilot binary, fallback to installer version."""
    pilot_path = Path.home() / ".pilot" / "bin" / "pilot"
    if pilot_path.exists():
        try:
            result = subprocess.run(
                [str(pilot_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                match = re.search(r" v(\S+)$", result.stdout.strip())
                if match:
                    return match.group(1)
        except Exception:
            pass
    return __version__


class FinalizeStep(BaseStep):
    """Step that runs final cleanup tasks and displays success panel."""

    name = "finalize"

    def check(self, ctx: InstallContext) -> bool:
        """Always returns False - finalize always runs."""
        return False

    def run(self, ctx: InstallContext) -> None:
        """Run final cleanup tasks and display success."""
        self._kill_stale_worker()
        self._display_success(ctx)

    @staticmethod
    def _kill_stale_worker() -> None:
        """Kill any running Console worker so it restarts with the newly installed files."""
        try:
            result = subprocess.run(
                ["lsof", "-ti", ":41777"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            pids = result.stdout.strip()
            if pids:
                for pid in pids.splitlines():
                    p = pid.strip()
                    if not re.fullmatch(r"\d+", p):
                        continue
                    # SIGTERM first for graceful shutdown
                    subprocess.run(["kill", p], capture_output=True, timeout=5)
                    time.sleep(1)
                    # SIGKILL only if still alive
                    alive = subprocess.run(["kill", "-0", p], capture_output=True, timeout=2)
                    if alive.returncode == 0:
                        subprocess.run(["kill", "-9", p], capture_output=True, timeout=5)
        except Exception:
            pass

    def _display_success(self, ctx: InstallContext) -> None:
        """Display success panel with next steps."""
        ui = ctx.ui

        if not ui:
            return

        if ui.quiet:
            ui.print(f"  [green]✓[/green] Update complete (v{_get_pilot_version()})")
            return

        getting_started: list[tuple[str, str]] = []

        if ctx.config.get("shell_needs_reload"):
            modified = ctx.config.get("modified_shell_configs", [])
            reload_cmds = []
            for f in modified:
                if ".zshrc" in f:
                    reload_cmds.append("source ~/.zshrc")
                elif ".bashrc" in f:
                    reload_cmds.append("source ~/.bashrc")
                elif "fish" in f:
                    reload_cmds.append("source ~/.config/fish/config.fish")

            if reload_cmds:
                cmd_str = " or ".join(reload_cmds)
                getting_started.append(("🔄 Reload shell", f"{cmd_str} (or restart terminal)"))

        getting_started.extend(
            [
                ("Launch Pilot Shell", "Run 'pilot' in your project folder instead of 'claude'"),
                ("Pilot Shell Console", "Open the UI in your browser at: http://localhost:41777"),
                ("Pilot Bot", "Run 'pilot bot' for 24/7 automation with scheduled tasks"),
                ("Claude Chrome", "Install and enable for better browser automation"),
            ]
        )

        workflows: list[tuple[str, str]] = [
            ("/setup-rules", "Create modular and concise rules for your project codebase"),
            ("/create-skill", "Create well-structured reusable skills for your workflows"),
            ("/prd", "Brainstorm ideas into PRDs with optional research before /spec"),
            ("/spec", "Plan, implement & verify features and bug fixes (replaces CC plan mode)"),
        ]

        ui.next_steps(
            [
                ("Getting Started", getting_started),
                ("Workflows", workflows),
            ]
        )

        if not ui.quiet:
            ui.rule()
            ui.print()
            ui.print("  [bold yellow]⭐ Star this repo:[/bold yellow] https://github.com/maxritter/pilot-shell")
            ui.print()
            ui.print(f"  [muted]Installed version: {_get_pilot_version()}[/muted]")
            ui.print()
