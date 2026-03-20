"""pilot-sec doctor — operational diagnostics."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter

# (tool_name, install_hint, category, required)
_TOOLS: list[tuple[str, str, str, bool]] = [
    # Secrets
    ("gitleaks",  "https://github.com/gitleaks/gitleaks",  "secrets",    False),
    ("trufflehog","https://github.com/trufflesecurity/trufflehog", "secrets", False),
    # SAST
    ("semgrep",   "pip install semgrep",                   "sast",       False),
    ("bandit",    "pip install bandit",                    "sast",       False),
    # Deps
    ("pip-audit", "pip install pip-audit",                 "deps",       False),
    ("npm",       "https://nodejs.org",                    "deps",       False),
    # IaC
    ("checkov",   "pip install checkov",                   "iac",        False),
    ("tfsec",     "https://github.com/aquasecurity/tfsec", "iac",        False),
    ("kube-score","https://github.com/zegl/kube-score",   "iac",        False),
    # Container
    ("trivy",     "https://github.com/aquasecurity/trivy", "container",  False),
    ("hadolint",  "https://github.com/hadolint/hadolint",  "container",  False),
    ("syft",      "https://github.com/anchore/syft",       "sbom",       False),
    ("cosign",    "https://github.com/sigstore/cosign",    "attest",     False),
    # Core
    ("git",       "https://git-scm.com",                  "core",       True),
]


@click.group("doctor", invoke_without_command=True)
@click.pass_context
def doctor_group(click_ctx: click.Context) -> None:
    """Validate tooling, config, and environment."""
    if click_ctx.invoked_subcommand is None:
        ctx = click_ctx.obj
        _run_full_check(ctx)


@doctor_group.command("tools")
@click.pass_obj
def doctor_tools(ctx: SecContext) -> None:
    """Check scanner tool availability."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    _check_tools(out)


@doctor_group.command("config")
@click.pass_obj
def doctor_config(ctx: SecContext) -> None:
    """Validate configuration files."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    _check_config(ctx, out)


@doctor_group.command("permissions")
@click.pass_obj
def doctor_permissions(ctx: SecContext) -> None:
    """Check filesystem and runtime permissions."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    _check_permissions(ctx, out)


# ------------------------------------------------------------------
# Checks
# ------------------------------------------------------------------

def _run_full_check(ctx: SecContext) -> None:
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    out.console.print("[bold]pilot-sec doctor[/bold]")
    out.console.print()

    issues = 0
    issues += _check_python(out)
    issues += _check_tools(out)
    issues += _check_config(ctx, out)
    issues += _check_permissions(ctx, out)

    out.console.print()
    if issues == 0:
        out.success("All checks passed")
    else:
        out.console.print(f"[yellow]{issues} issue(s) found[/yellow]")

    raise SystemExit(1 if issues else 0)


def _check_python(out: OutputWriter) -> int:
    issues = 0
    out.console.print("[bold]Python[/bold]")
    version = sys.version_info
    if version >= (3, 12):
        out.console.print(f"  [green]✓[/green]  Python {version.major}.{version.minor}.{version.micro}")
    else:
        out.console.print(f"  [red]✗[/red]  Python {version.major}.{version.minor} — requires 3.12+")
        issues += 1
    return issues


def _check_tools(out: OutputWriter) -> int:
    issues = 0
    out.console.print()
    out.console.print("[bold]Tools[/bold]")

    by_category: dict[str, list] = {}
    for tool, hint, category, required in _TOOLS:
        by_category.setdefault(category, []).append((tool, hint, required))

    for category, tools in sorted(by_category.items()):
        out.console.print(f"  [dim]{category}[/dim]")
        for tool, hint, required in tools:
            found = shutil.which(tool) is not None
            if found:
                version = _tool_version(tool)
                out.console.print(f"    [green]✓[/green]  {tool:<16} {version}")
            else:
                color = "red" if required else "yellow"
                label = "REQUIRED" if required else "optional"
                out.console.print(f"    [{color}]✗[/{color}]  {tool:<16} not found  [dim]({label})[/dim]")
                out.console.print(f"       install: {hint}")
                if required:
                    issues += 1
    return issues


def _check_config(ctx: SecContext, out: OutputWriter) -> int:
    issues = 0
    out.console.print()
    out.console.print("[bold]Configuration[/bold]")

    if not ctx.is_initialized():
        out.console.print("  [yellow]![/yellow]  .pilot-sec/ not found — run [cyan]pilot-sec init[/cyan]")
        return 1

    out.console.print(f"  [green]✓[/green]  .pilot-sec/ exists")

    config_path = ctx.pilot_sec_dir / "config.yaml"
    if config_path.exists():
        from pilot_sec.core.config import PilotSecConfig
        cfg = PilotSecConfig.load(ctx.pilot_sec_dir)
        errors = cfg.validate()
        if errors:
            for err in errors:
                out.console.print(f"  [red]✗[/red]  config: {err}")
                issues += 1
        else:
            out.console.print(f"  [green]✓[/green]  config.yaml valid")
    else:
        out.console.print("  [yellow]![/yellow]  config.yaml missing")
        issues += 1

    policies_dir = ctx.policies_dir
    if policies_dir.exists() and list(policies_dir.glob("**/*.yaml")):
        out.console.print(f"  [green]✓[/green]  policies/ present")
    else:
        out.console.print("  [yellow]![/yellow]  no policy files found")

    return issues


def _check_permissions(ctx: SecContext, out: OutputWriter) -> int:
    issues = 0
    out.console.print()
    out.console.print("[bold]Permissions[/bold]")

    # Check writable project root
    test_file = ctx.project_root / ".pilot-sec" / ".write-test"
    try:
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()
        test_file.unlink()
        out.console.print(f"  [green]✓[/green]  .pilot-sec/ is writable")
    except Exception as exc:
        out.console.print(f"  [red]✗[/red]  .pilot-sec/ not writable: {exc}")
        issues += 1

    # Git repo check
    git_dir = ctx.project_root / ".git"
    if git_dir.exists():
        out.console.print(f"  [green]✓[/green]  git repository detected")
    else:
        out.console.print(f"  [yellow]![/yellow]  not a git repository — some features limited")

    return issues


def _tool_version(tool: str) -> str:
    for flag in ["--version", "version", "-v"]:
        try:
            result = subprocess.run(
                [tool, flag], capture_output=True, text=True, timeout=5
            )
            line = (result.stdout or result.stderr or "").splitlines()
            if line:
                return line[0].strip()[:40]
        except Exception:
            pass
    return ""
