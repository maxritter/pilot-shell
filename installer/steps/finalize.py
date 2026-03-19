"""Finalize step - runs final cleanup tasks and displays success."""

from __future__ import annotations

import re
import subprocess
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
        self._display_success(ctx)

    def _display_success(self, ctx: InstallContext) -> None:
        """Display success panel with next steps."""
        ui = ctx.ui

        if not ui:
            return

        if ui.quiet:
            ui.print(f"  [green]✓[/green] Update complete (v{_get_pilot_version()})")
            return

        steps: list[tuple[str, str]] = []

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
                steps.append(("🔄 Reload shell", f"{cmd_str} (or restart terminal)"))

        steps.append(("Launch Pilot Shell", "Run: pilot (in your project folder)"))
        steps.append(("Pilot Shell Console", "Open in your browser at: http://localhost:41777"))
        steps.append(("/spec", "Plan, implement & verify features and bug fixes (replaces CC plan mode)"))
        steps.append(("/setup-rules", "Create modular and concise rules for your project codebase"))
        steps.append(("/create-skill", "Create well-structured reusable skills for your workflows"))

        ui.next_steps(steps)

        if not ui.quiet:
            ui.rule()
            ui.print()
            ui.print("  [bold yellow]⭐ Star this repo:[/bold yellow] https://github.com/maxritter/pilot-shell")
            ui.print()
            ui.print(f"  [dim]Installed version: {_get_pilot_version()}[/dim]")
            ui.print()
