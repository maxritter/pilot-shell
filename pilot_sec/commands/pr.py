"""pilot-sec pr — developer workflow integration."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import click

from pilot_sec.core.context import SecContext
from pilot_sec.core.findings import FindingsSummary
from pilot_sec.core.output import OutputWriter
from pilot_sec.core.risk import compute_risk_score


def _git(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except Exception:
        return ""


@click.group("pr")
@click.pass_obj
def pr_group(ctx: SecContext) -> None:
    """PR-level security gates and summaries."""


@pr_group.command("check")
@click.option("--base", default="origin/main", metavar="REF", help="Base branch")
@click.option("--head", default="HEAD", metavar="REF", help="Head branch/commit")
@click.option("--changed-only", is_flag=True, default=True, help="Only scan changed files")
@click.pass_obj
def pr_check(ctx: SecContext, base: str, head: str, changed_only: bool) -> None:
    """Run security checks for a PR diff."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    out.step(f"PR check: {base} → {head}")

    changed = _get_changed_files(base, head, ctx.project_root)
    out.info(f"  {len(changed)} changed file(s)")

    # Run relevant scanners
    from pilot_sec.commands.scan import _dispatch
    summary = _dispatch("all", ctx.project_root, None, {})

    # Only report findings in changed files if --changed-only
    if changed_only and changed:
        summary.findings = [
            f for f in summary.findings
            if not f.file_path or any(c.endswith(f.file_path or "") or (f.file_path or "").endswith(c) for c in changed)
        ]

    out.print_findings(summary, title="PR findings")

    risk_score = compute_risk_score(summary)
    counts = summary.to_dict()

    out.console.print()
    out.console.print(f"  Risk score : {risk_score}")
    out.console.print(f"  Critical   : {counts.get('critical', 0)}")
    out.console.print(f"  High       : {counts.get('high', 0)}")

    fail_on = ctx.fail_on or "high"
    if fail_on != "none" and summary.exceeds_threshold(fail_on):
        out.err(f"PR gate failed — findings exceed --fail-on {fail_on}")
        raise SystemExit(4)


@pr_group.command("summarize")
@click.option("--base", default="origin/main", metavar="REF")
@click.option("--head", default="HEAD", metavar="REF")
@click.option("--format", "fmt", default=None, type=click.Choice(["text", "markdown", "json"]))
@click.pass_obj
def pr_summarize(ctx: SecContext, base: str, head: str, fmt: Optional[str]) -> None:
    """Generate a security summary for a PR."""
    out = OutputWriter(fmt=fmt or ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    from pilot_sec.commands.scan import _dispatch
    summary = _dispatch("all", ctx.project_root, None, {})
    risk_score = compute_risk_score(summary)
    counts = summary.to_dict()

    if fmt == "markdown" or (not fmt and ctx.output_format == "text"):
        _print_markdown_summary(out, summary, counts, risk_score, base, head)
    else:
        out.emit_result(
            command="pr summarize",
            status="success",
            risk_score=risk_score,
            findings_summary=counts,
        )


@pr_group.command("gate")
@click.option("--fail-on", "fail_on_level", default="high",
              type=click.Choice(["none", "low", "medium", "high", "critical"]))
@click.pass_obj
def pr_gate(ctx: SecContext, fail_on_level: str) -> None:
    """Enforce a hard gate — exit non-zero if threshold exceeded."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    from pilot_sec.commands.scan import _dispatch
    summary = _dispatch("all", ctx.project_root, None, {})

    if fail_on_level != "none" and summary.exceeds_threshold(fail_on_level):
        out.err(f"Gate failed — findings at or above '{fail_on_level}' severity")
        raise SystemExit(4)
    out.success(f"Gate passed — no findings at or above '{fail_on_level}'")


@pr_group.command("comment")
@click.option("--provider", default="github",
              type=click.Choice(["github", "gitlab", "bitbucket"]))
@click.option("--pr-number", default=None, type=int, help="PR number")
@click.pass_obj
def pr_comment(ctx: SecContext, provider: str, pr_number: Optional[int]) -> None:
    """Post a security summary as a PR comment."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    out.warn(f"PR comment posting to {provider} requires provider credentials.")
    out.info("  Use `gh pr comment` with the output of `pilot-sec pr summarize --format markdown`")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _get_changed_files(base: str, head: str, cwd: Path) -> list[str]:
    output = _git(["diff", "--name-only", base, head], cwd)
    return [f.strip() for f in output.splitlines() if f.strip()]


def _print_markdown_summary(out: OutputWriter, summary: FindingsSummary, counts: dict, risk_score: float, base: str, head: str) -> None:
    lines = [
        "## Security Summary",
        "",
        f"**PR:** `{base}` → `{head}`  ",
        f"**Risk Score:** {risk_score}  ",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    for sev in ["critical", "high", "medium", "low"]:
        lines.append(f"| {sev.capitalize()} | {counts.get(sev, 0)} |")

    if summary.total() > 0:
        lines += ["", "### Findings", ""]
        for f in summary.findings[:20]:
            loc = f" (`{f.file_path}:{f.line_number}`)" if f.file_path else ""
            lines.append(f"- **[{f.severity.upper()}]** {f.title}{loc}")
        if summary.total() > 20:
            lines.append(f"- _...and {summary.total() - 20} more_")
    else:
        lines += ["", "✅ No security findings."]

    print("\n".join(lines))
