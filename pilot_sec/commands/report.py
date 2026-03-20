"""pilot-sec report — artifact synthesis."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click

from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter
from pilot_sec.core.risk import compute_risk_score
from pilot_sec.core.session_manager import SessionManager


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@click.group("report")
@click.pass_obj
def report_group(ctx: SecContext) -> None:
    """Generate security reports and artifacts."""


@report_group.command("findings")
@click.option("--format", "report_fmt", default=None,
              type=click.Choice(["text", "json", "sarif", "markdown"]))
@click.option("--output", "output_path", default=None, metavar="PATH")
@click.option("--severity", default=None,
              type=click.Choice(["low", "medium", "high", "critical"]))
@click.pass_obj
def report_findings(ctx: SecContext, report_fmt: Optional[str], output_path: Optional[str],
                    severity: Optional[str]) -> None:
    """Generate a findings report."""
    fmt = report_fmt or ctx.output_format
    out = OutputWriter(fmt=fmt, output_path=output_path, no_color=ctx.no_color, quiet=ctx.quiet)
    out.step("Scanning for findings...")

    from pilot_sec.commands.scan import _dispatch
    summary = _dispatch("all", ctx.project_root, severity, {})

    if severity:
        summary.findings = summary.filter_by_severity(severity)

    dest = Path(output_path) if output_path else ctx.reports_dir / _report_filename("findings", fmt)

    if fmt == "sarif":
        from pilot_sec.core.output import to_sarif
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(to_sarif(summary), indent=2))
        out.success(f"SARIF report written → {dest}")
    elif fmt == "json":
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps({
            "generated_at": _now(),
            "total": summary.total(),
            "counts": summary.to_dict(),
            "findings": [f.to_dict() for f in summary.findings],
        }, indent=2))
        out.success(f"JSON report written → {dest}")
    elif fmt == "markdown":
        md = _findings_markdown(summary)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(md)
        out.success(f"Markdown report written → {dest}")
    else:
        out.print_findings(summary, title="Findings Report")


@report_group.command("risk")
@click.option("--output", "output_path", default=None, metavar="PATH")
@click.pass_obj
def report_risk(ctx: SecContext, output_path: Optional[str]) -> None:
    """Generate a risk score report."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    from pilot_sec.commands.scan import _dispatch
    summary = _dispatch("all", ctx.project_root, None, {})
    risk_score = compute_risk_score(summary)
    counts = summary.to_dict()

    if ctx.output_format == "json":
        out.emit_result(
            command="report risk",
            status="success",
            risk_score=risk_score,
            findings_summary=counts,
        )
    else:
        from pilot_sec.core.risk import risk_label
        label = risk_label(risk_score)
        colors = {"none": "green", "low": "blue", "medium": "yellow", "high": "red", "critical": "bold red"}
        color = colors.get(label, "white")
        out.console.print(f"[bold]Risk Score:[/bold] [{color}]{risk_score} ({label.upper()})[/{color}]")
        out.console.print()
        out.print_findings(summary)


@report_group.command("audit")
@click.option("--session", "session_id", default=None, help="Session ID (default: current)")
@click.option("--output", "output_path", default=None, metavar="PATH")
@click.pass_obj
def report_audit(ctx: SecContext, session_id: Optional[str], output_path: Optional[str]) -> None:
    """Generate an audit trail report."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    mgr = SessionManager(ctx.sessions_dir)

    if session_id == "current" or not session_id:
        session = mgr.current()
    else:
        session = mgr.load(session_id)

    if not session:
        out.warn("No active or specified session found. Use `pilot-sec session start` first.")
        raise SystemExit(0)

    data = session.to_dict()
    dest = Path(output_path) if output_path else ctx.reports_dir / f"audit-{session.id}.json"

    if ctx.output_format == "json":
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data, indent=2))
        out.success(f"Audit report written → {dest}")
    else:
        out.console.print(f"[bold]Audit report[/bold] — session: {session.id}")
        out.console.print(f"  Started  : {session.started_at}")
        out.console.print(f"  Status   : {session.status}")
        out.console.print(f"  Commands : {len(data.get('commands', []))}")
        out.console.print(f"  Findings : {len(data.get('findings', []))}")
        for cmd in data.get("commands", []):
            ts = cmd.get("timestamp", "")[:19]
            out.console.print(f"  [dim]{ts}[/dim] {cmd.get('command', '')}")


@report_group.command("release")
@click.option("--output", "output_path", default=None, metavar="PATH")
@click.pass_obj
def report_release(ctx: SecContext, output_path: Optional[str]) -> None:
    """Generate a release security report."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    from pilot_sec.commands.scan import _dispatch
    summary = _dispatch("all", ctx.project_root, None, {})
    risk_score = compute_risk_score(summary)

    dest = Path(output_path) if output_path else ctx.reports_dir / "release-security.md"
    md = _release_markdown(summary, risk_score)

    if not ctx.dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(md)
        out.success(f"Release report written → {dest}")
    else:
        print(md)


@report_group.command("executive")
@click.option("--from", "from_ref", default="origin/main")
@click.option("--to", "to_ref", default="HEAD")
@click.option("--output", "output_path", default=None, metavar="PATH")
@click.pass_obj
def report_executive(ctx: SecContext, from_ref: str, to_ref: str, output_path: Optional[str]) -> None:
    """Executive summary report."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    from pilot_sec.commands.scan import _dispatch
    summary = _dispatch("all", ctx.project_root, None, {})
    risk_score = compute_risk_score(summary)

    dest = Path(output_path) if output_path else ctx.reports_dir / "executive-summary.md"
    md = _executive_markdown(summary, risk_score, from_ref, to_ref)

    if not ctx.dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(md)
        out.success(f"Executive report written → {dest}")
    else:
        print(md)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _report_filename(name: str, fmt: str) -> str:
    ext = {"sarif": "sarif", "json": "json", "markdown": "md"}.get(fmt, "txt")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    return f"{name}-{ts}.{ext}"


def _findings_markdown(summary) -> str:
    counts = summary.to_dict()
    lines = [
        "# Findings Report",
        "",
        f"Generated: {_now()}",
        "",
        "## Summary",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    for sev in ["critical", "high", "medium", "low"]:
        lines.append(f"| {sev.capitalize()} | {counts.get(sev, 0)} |")
    lines += ["", "## Findings", ""]
    for f in summary.findings:
        loc = f" (`{f.file_path}:{f.line_number}`)" if f.file_path else ""
        lines.append(f"### [{f.severity.upper()}] {f.title}{loc}")
        if f.description:
            lines.append(f.description)
        if f.remediation:
            lines.append(f"\n**Remediation:** {f.remediation}")
        lines.append("")
    return "\n".join(lines)


def _release_markdown(summary, risk_score: float) -> str:
    counts = summary.to_dict()
    return f"""# Release Security Report

Generated: {_now()}

## Risk Score: {risk_score}

## Findings Summary

| Severity | Count |
|----------|-------|
| Critical | {counts.get('critical', 0)} |
| High | {counts.get('high', 0)} |
| Medium | {counts.get('medium', 0)} |
| Low | {counts.get('low', 0)} |

## Assessment

{"⚠️ **Action required** — critical or high findings present." if counts.get('critical', 0) + counts.get('high', 0) > 0 else "✅ No critical or high findings."}
"""


def _executive_markdown(summary, risk_score: float, from_ref: str, to_ref: str) -> str:
    counts = summary.to_dict()
    return f"""# Executive Security Summary

Generated: {_now()}
Scope: `{from_ref}` → `{to_ref}`

## Overall Risk: {risk_score}/100

| Category | Count |
|----------|-------|
| Critical | {counts.get('critical', 0)} |
| High | {counts.get('high', 0)} |
| Medium | {counts.get('medium', 0)} |
| Low | {counts.get('low', 0)} |

## Status

{"🔴 Immediate action required" if counts.get('critical', 0) > 0 else "🟡 Review recommended" if counts.get('high', 0) > 0 else "🟢 Acceptable risk posture"}
"""
