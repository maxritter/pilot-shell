"""pilot-sec scan — unified inspection entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from pilot_sec.core.context import SecContext
from pilot_sec.core.findings import FindingsSummary, meets_threshold
from pilot_sec.core.output import OutputWriter
from pilot_sec.core.risk import compute_risk_score
from pilot_sec.core.session_manager import new_run_id


@click.group("scan")
@click.pass_obj
def scan_group(ctx: SecContext) -> None:
    """Inspect the current security state."""


def _common_scan_options(fn):  # type: ignore[return]
    fn = click.option("--path", "scan_path", default=None, metavar="PATH", help="Target path")(fn)
    fn = click.option("--changed-only", is_flag=True, help="Scan only changed files")(fn)
    fn = click.option("--since", default=None, metavar="GIT-REF", help="Changed since this ref")(fn)
    fn = click.option("--baseline", default=None, metavar="PATH", help="Baseline findings file")(fn)
    fn = click.option("--include", default=None, metavar="PATTERN", help="Include files matching")(fn)
    fn = click.option("--exclude", default=None, metavar="PATTERN", help="Exclude files matching")(fn)
    fn = click.option(
        "--severity", default=None,
        type=click.Choice(["low", "medium", "high", "critical"]),
        help="Minimum severity to report",
    )(fn)
    fn = click.option("--sarif", is_flag=True, help="Output SARIF")(fn)
    fn = click.option("--fix", is_flag=True, help="Apply auto-fixes where supported")(fn)
    return fn


def _resolve_path(ctx: SecContext, scan_path: Optional[str]) -> Path:
    return Path(scan_path) if scan_path else ctx.project_root


def _run_scan(ctx: SecContext, category: str, scan_path: Path, severity: Optional[str], sarif: bool, **kwargs) -> int:
    """Execute scan and print results. Returns exit code."""
    fmt = "sarif" if sarif else ctx.output_format
    out = OutputWriter(fmt=fmt, no_color=ctx.no_color, quiet=ctx.quiet)
    run_id = new_run_id()

    # Import scanners lazily to avoid import loops
    from pilot_sec.scanners import code, deps, secrets, iac, container, ci  # noqa: F401

    summary = _dispatch(category, scan_path, severity, kwargs)

    if severity:
        summary.findings = summary.filter_by_severity(severity)

    out.print_findings(summary, title=f"Scan: {category}")

    risk_score = compute_risk_score(summary)

    if fmt in ("json", "yaml", "sarif"):
        pass  # already printed by print_findings
    else:
        if risk_score > 0:
            out.console.print(f"  Risk score: [bold]{risk_score}[/bold]")

    # Emit JSON envelope if requested
    if ctx.output_format == "json":
        out.emit_result(
            command=f"scan {category}",
            status="success",
            run_id=run_id,
            session_id=ctx.session_id,
            risk_score=risk_score,
            findings_summary=summary.to_dict(),
        )

    # Attach to session
    from pilot_sec.core.session_manager import SessionManager
    session_mgr = SessionManager(ctx.sessions_dir)
    session = session_mgr.current()
    if session:
        for f in summary.findings:
            session.record_finding(f.to_dict())

    fail_on = ctx.fail_on
    if fail_on and fail_on != "none" and summary.exceeds_threshold(fail_on):
        return 4
    return 0


def _dispatch(category: str, scan_path: Path, severity: Optional[str], kwargs: dict) -> FindingsSummary:
    from pilot_sec.scanners.code import run_code_scan
    from pilot_sec.scanners.deps import run_deps_scan
    from pilot_sec.scanners.secrets import run_secret_scan
    from pilot_sec.scanners.iac import run_iac_scan
    from pilot_sec.scanners.base import all_scanners
    from pilot_sec.scanners.container import TrivyImageScanner, DockerfileScanner
    from pilot_sec.scanners.ci import CIPipelineScanner
    from pilot_sec.scanners.base import ScanOptions

    if category == "code":
        return run_code_scan(scan_path, severity)
    if category == "deps":
        return run_deps_scan(scan_path, severity)
    if category == "secrets":
        return run_secret_scan(
            scan_path,
            staged=kwargs.get("staged", False),
            history=kwargs.get("history", False),
        )
    if category == "iac":
        return run_iac_scan(scan_path, severity)
    if category == "container":
        summary = FindingsSummary()
        image = kwargs.get("image")
        if image:
            opts = ScanOptions(path=scan_path, extra={"image": image})
            result = TrivyImageScanner().scan(opts)
            summary.findings.extend(result.findings)
        opts = ScanOptions(path=scan_path)
        result = DockerfileScanner().scan(opts)
        summary.findings.extend(result.findings)
        return summary
    if category == "ci":
        opts = ScanOptions(path=scan_path)
        return CIPipelineScanner().scan(opts)
    if category == "all":
        summary = FindingsSummary()
        for sub in ["code", "deps", "secrets", "iac", "ci"]:
            sub_result = _dispatch(sub, scan_path, severity, kwargs)
            summary.findings.extend(sub_result.findings)
        return summary
    return FindingsSummary()


# ------------------------------------------------------------------
# Subcommands
# ------------------------------------------------------------------

@scan_group.command("all")
@_common_scan_options
@click.pass_obj
def scan_all(ctx, scan_path, changed_only, since, baseline, include, exclude, severity, sarif, fix):
    """Run all scanners."""
    path = _resolve_path(ctx, scan_path)
    rc = _run_scan(ctx, "all", path, severity, sarif)
    raise SystemExit(rc)


@scan_group.command("code")
@_common_scan_options
@click.pass_obj
def scan_code(ctx, scan_path, changed_only, since, baseline, include, exclude, severity, sarif, fix):
    """SAST — static analysis."""
    path = _resolve_path(ctx, scan_path)
    rc = _run_scan(ctx, "code", path, severity, sarif)
    raise SystemExit(rc)


@scan_group.command("deps")
@_common_scan_options
@click.pass_obj
def scan_deps(ctx, scan_path, changed_only, since, baseline, include, exclude, severity, sarif, fix):
    """Dependency vulnerability scan."""
    path = _resolve_path(ctx, scan_path)
    rc = _run_scan(ctx, "deps", path, severity, sarif)
    raise SystemExit(rc)


@scan_group.command("secrets")
@_common_scan_options
@click.option("--staged", is_flag=True, help="Scan staged changes only")
@click.option("--history", is_flag=True, help="Scan full git history")
@click.option("--env", "scan_env", is_flag=True, help="Scan environment variables")
@click.pass_obj
def scan_secrets(ctx, scan_path, changed_only, since, baseline, include, exclude, severity, sarif, fix, staged, history, scan_env):
    """Secret detection."""
    path = _resolve_path(ctx, scan_path)
    rc = _run_scan(ctx, "secrets", path, severity, sarif, staged=staged, history=history, scan_env=scan_env)
    raise SystemExit(rc)


@scan_group.command("iac")
@_common_scan_options
@click.pass_obj
def scan_iac(ctx, scan_path, changed_only, since, baseline, include, exclude, severity, sarif, fix):
    """IaC security — Terraform, K8s, Helm."""
    path = _resolve_path(ctx, scan_path)
    rc = _run_scan(ctx, "iac", path, severity, sarif)
    raise SystemExit(rc)


@scan_group.command("container")
@_common_scan_options
@click.option("--image", default=None, help="Container image name to scan")
@click.pass_obj
def scan_container(ctx, scan_path, changed_only, since, baseline, include, exclude, severity, sarif, fix, image):
    """Container image and Dockerfile security."""
    path = _resolve_path(ctx, scan_path)
    rc = _run_scan(ctx, "container", path, severity, sarif, image=image)
    raise SystemExit(rc)


@scan_group.command("dockerfile")
@_common_scan_options
@click.pass_obj
def scan_dockerfile(ctx, scan_path, changed_only, since, baseline, include, exclude, severity, sarif, fix):
    """Dockerfile best-practice checks."""
    path = _resolve_path(ctx, scan_path)
    rc = _run_scan(ctx, "container", path, severity, sarif)
    raise SystemExit(rc)


@scan_group.command("ci")
@_common_scan_options
@click.pass_obj
def scan_ci(ctx, scan_path, changed_only, since, baseline, include, exclude, severity, sarif, fix):
    """CI pipeline security checks."""
    path = _resolve_path(ctx, scan_path)
    rc = _run_scan(ctx, "ci", path, severity, sarif)
    raise SystemExit(rc)


@scan_group.command("licenses")
@_common_scan_options
@click.option("--allow", multiple=True, metavar="SPDX-ID", help="Allowed license IDs")
@click.option("--deny", multiple=True, metavar="SPDX-ID", help="Denied license IDs")
@click.pass_obj
def scan_licenses(ctx, scan_path, changed_only, since, baseline, include, exclude, severity, sarif, fix, allow, deny):
    """License compliance check."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    out.warn("License scanning requires `pip-licenses` or `license-checker`. Install to enable.")
    raise SystemExit(0)
