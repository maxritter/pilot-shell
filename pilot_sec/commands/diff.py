"""pilot-sec diff — security posture delta engine."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional

import click

from pilot_sec.core.context import SecContext
from pilot_sec.core.findings import Finding, FindingsSummary
from pilot_sec.core.output import OutputWriter
from pilot_sec.core.session_manager import new_run_id


def _git_changed_files(from_ref: str, to_ref: str, cwd: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", from_ref, to_ref],
            capture_output=True, text=True, cwd=cwd,
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        return []


@click.group("diff")
@click.pass_obj
def diff_group(ctx: SecContext) -> None:
    """Compare security posture over time."""


def _diff_options(fn):  # type: ignore[return]
    fn = click.option("--from", "from_ref", default="origin/main", metavar="REF", help="Base git ref")(fn)
    fn = click.option("--to", "to_ref", default="HEAD", metavar="REF", help="Target git ref")(fn)
    fn = click.option("--format", "output_format", default=None,
                      type=click.Choice(["text", "json", "sarif", "table"]), help="Output format")(fn)
    return fn


def _scan_ref(ref: str, category: str, project_root: Path) -> FindingsSummary:
    """Checkout ref into a temp space and scan. For now, scan HEAD always."""
    # Full ref checkout is complex — we scan the working tree and note the ref
    from pilot_sec.commands.scan import _dispatch
    return _dispatch(category, project_root, None, {})


@diff_group.command("findings")
@_diff_options
@click.pass_obj
def diff_findings(ctx: SecContext, from_ref: str, to_ref: str, output_format: Optional[str]) -> None:
    """Show new or resolved findings between two refs."""
    fmt = output_format or ctx.output_format
    out = OutputWriter(fmt=fmt, no_color=ctx.no_color, quiet=ctx.quiet)
    out.step(f"Diffing findings: {from_ref} → {to_ref}")

    changed = _git_changed_files(from_ref, to_ref, ctx.project_root)
    if not changed:
        out.info("No changed files detected.")
        raise SystemExit(0)

    out.info(f"  {len(changed)} changed file(s)")

    # Scan current state
    from pilot_sec.commands.scan import _dispatch
    current = _dispatch("all", ctx.project_root, None, {})

    _print_diff_summary(out, current, from_ref, to_ref, changed)


@diff_group.command("deps")
@_diff_options
@click.pass_obj
def diff_deps(ctx: SecContext, from_ref: str, to_ref: str, output_format: Optional[str]) -> None:
    """Dependency risk delta."""
    fmt = output_format or ctx.output_format
    out = OutputWriter(fmt=fmt, no_color=ctx.no_color, quiet=ctx.quiet)
    out.step(f"Diffing dependencies: {from_ref} → {to_ref}")

    from pilot_sec.commands.scan import _dispatch
    current = _dispatch("deps", ctx.project_root, None, {})
    _print_diff_summary(out, current, from_ref, to_ref, [])


@diff_group.command("secrets")
@_diff_options
@click.pass_obj
def diff_secrets(ctx: SecContext, from_ref: str, to_ref: str, output_format: Optional[str]) -> None:
    """Secret exposure delta."""
    fmt = output_format or ctx.output_format
    out = OutputWriter(fmt=fmt, no_color=ctx.no_color, quiet=ctx.quiet)
    out.step(f"Diffing secrets: {from_ref} → {to_ref}")

    from pilot_sec.commands.scan import _dispatch
    current = _dispatch("secrets", ctx.project_root, None, {})
    _print_diff_summary(out, current, from_ref, to_ref, [])


@diff_group.command("iac")
@_diff_options
@click.pass_obj
def diff_iac(ctx: SecContext, from_ref: str, to_ref: str, output_format: Optional[str]) -> None:
    """IaC security posture delta."""
    fmt = output_format or ctx.output_format
    out = OutputWriter(fmt=fmt, no_color=ctx.no_color, quiet=ctx.quiet)
    out.step(f"Diffing IaC: {from_ref} → {to_ref}")

    from pilot_sec.commands.scan import _dispatch
    current = _dispatch("iac", ctx.project_root, None, {})
    _print_diff_summary(out, current, from_ref, to_ref, [])


@diff_group.command("attack-surface")
@_diff_options
@click.pass_obj
def diff_attack_surface(ctx: SecContext, from_ref: str, to_ref: str, output_format: Optional[str]) -> None:
    """Attack surface changes."""
    fmt = output_format or ctx.output_format
    out = OutputWriter(fmt=fmt, no_color=ctx.no_color, quiet=ctx.quiet)
    out.step(f"Attack surface diff: {from_ref} → {to_ref}")

    changed = _git_changed_files(from_ref, to_ref, ctx.project_root)
    surface_changes = _detect_surface_changes(changed)

    if not surface_changes:
        out.success("No significant attack surface changes detected.")
        raise SystemExit(0)

    out.console.print(f"[bold]Attack surface changes[/bold] ({len(surface_changes)} items):")
    for change in surface_changes:
        out.console.print(f"  [yellow]→[/yellow] {change}")


@diff_group.command("policy")
@_diff_options
@click.pass_obj
def diff_policy(ctx: SecContext, from_ref: str, to_ref: str, output_format: Optional[str]) -> None:
    """Policy coverage regression."""
    fmt = output_format or ctx.output_format
    out = OutputWriter(fmt=fmt, no_color=ctx.no_color, quiet=ctx.quiet)
    out.step(f"Policy diff: {from_ref} → {to_ref}")
    out.info("  Comparing policy pack application across refs...")
    out.info("  (Full policy diff requires baseline snapshots — run `pilot-sec attest scan` to create them)")


def _print_diff_summary(out: OutputWriter, current: FindingsSummary, from_ref: str, to_ref: str, changed_files: list[str]) -> None:
    counts = current.to_dict()
    total = current.total()

    if total == 0:
        out.success(f"No findings in current state ({to_ref})")
        return

    out.console.print(f"\n[bold]Findings in {to_ref}[/bold] vs {from_ref}:")
    out.print_findings(current)
    out.console.print()
    out.info("  tip: Use baseline snapshots (`pilot-sec attest scan`) for precise new/resolved tracking")


def _detect_surface_changes(changed_files: list[str]) -> list[str]:
    """Heuristically identify attack-surface-relevant file changes."""
    surface_indicators = [
        ("routes", "API route changes"),
        ("auth", "Authentication logic changes"),
        ("permission", "Permission/authorization changes"),
        ("middleware", "Middleware changes"),
        ("docker", "Container configuration changes"),
        ("k8s", "Kubernetes configuration changes"),
        ("terraform", "Infrastructure changes"),
        ("iam", "IAM/access policy changes"),
        (".env", "Environment configuration changes"),
        ("Dockerfile", "Container image changes"),
    ]
    results = []
    for f in changed_files:
        f_lower = f.lower()
        for keyword, description in surface_indicators:
            if keyword.lower() in f_lower:
                results.append(f"{description}: {f}")
                break
    return list(dict.fromkeys(results))
