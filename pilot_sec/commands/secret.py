"""pilot-sec secret — secret detection and management."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

import click

from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter


@click.group("secret")
@click.pass_obj
def secret_group(ctx: SecContext) -> None:
    """Detect and manage secret exposure."""


@secret_group.command("scan")
@click.option("--staged", is_flag=True, help="Scan staged changes")
@click.option("--history", is_flag=True, help="Scan full git history")
@click.option("--env", "scan_env", is_flag=True, help="Scan environment variables")
@click.option("--path", "scan_path", default=None, metavar="PATH")
@click.option("--since", default=None, metavar="GIT-REF")
@click.option("--provider", default=None,
              type=click.Choice(["aws", "gcp", "azure", "github", "custom"]),
              help="Verify provider for live secret check")
@click.option("--revoke-hints", is_flag=True, help="Print revocation instructions")
@click.pass_obj
def secret_scan(ctx: SecContext, staged: bool, history: bool, scan_env: bool,
                scan_path: Optional[str], since: Optional[str], provider: Optional[str],
                revoke_hints: bool) -> None:
    """Scan for exposed secrets."""
    from pilot_sec.scanners import secrets as _  # noqa: F401 — trigger registration
    from pilot_sec.scanners.secrets import run_secret_scan

    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    path = Path(scan_path) if scan_path else ctx.project_root

    out.step(f"Scanning for secrets in {path}")
    summary = run_secret_scan(path, staged=staged, history=history, since=since, scan_env=scan_env)

    out.print_findings(summary, title="Secrets")

    if revoke_hints and summary.total() > 0:
        out.console.print()
        out.console.print("[bold]Revocation checklist:[/bold]")
        out.console.print("  1. Revoke the exposed credential in the provider console")
        out.console.print("  2. Rotate all affected downstream services")
        out.console.print("  3. Remove from git history: [cyan]git filter-repo[/cyan] or [cyan]BFG Repo Cleaner[/cyan]")
        out.console.print("  4. Force-push cleaned history and notify collaborators")
        out.console.print("  5. Enable secret scanning alerts in your CI/CD platform")

    fail_on = ctx.fail_on
    if fail_on and fail_on != "none" and summary.exceeds_threshold(fail_on):
        raise SystemExit(4)


@secret_group.command("redact")
@click.argument("file_path")
@click.option("--dry-run", "dry", is_flag=True, help="Show what would be redacted without modifying")
@click.pass_obj
def secret_redact(ctx: SecContext, file_path: str, dry: bool) -> None:
    """Redact detected secrets from a file."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    path = Path(file_path)
    if not path.exists():
        out.err(f"File not found: {file_path}")
        raise SystemExit(1)

    content = path.read_text(errors="replace")
    redacted, count = _redact_secrets(content)

    if count == 0:
        out.success(f"No patterns found in {file_path}")
        return

    out.console.print(f"[yellow]Found {count} potential secret pattern(s) to redact[/yellow]")
    if dry or ctx.dry_run:
        out.info("  dry-run — no changes written")
    else:
        path.write_text(redacted)
        out.success(f"Redacted {count} pattern(s) in {file_path}")


@secret_group.command("inventory")
@click.option("--path", "scan_path", default=None, metavar="PATH")
@click.pass_obj
def secret_inventory(ctx: SecContext, scan_path: Optional[str]) -> None:
    """Map secret locations across the repository."""
    from pilot_sec.scanners import secrets as _  # noqa: F401
    from pilot_sec.scanners.secrets import run_secret_scan

    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    path = Path(scan_path) if scan_path else ctx.project_root
    summary = run_secret_scan(path)

    if ctx.output_format == "json":
        print(json.dumps({
            "total": summary.total(),
            "by_file": _group_by_file(summary),
        }, indent=2))
    else:
        out.console.print(f"[bold]Secret inventory[/bold] — {summary.total()} finding(s)")
        for file_path, count in _group_by_file(summary).items():
            out.console.print(f"  {count:3}  {file_path}")


@secret_group.command("verify")
@click.option("--provider", required=True,
              type=click.Choice(["aws", "gcp", "azure", "github", "custom"]))
@click.pass_obj
def secret_verify(ctx: SecContext, provider: str) -> None:
    """Verify whether exposed secrets are still live (safe providers only)."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    out.warn(f"Live secret verification for {provider} requires provider-specific credentials.")
    out.info("  Use your provider's API to validate exposed tokens before revoking.")


@secret_group.group("ignore")
@click.pass_obj
def secret_ignore(ctx: SecContext) -> None:
    """Manage secret ignore patterns."""


@secret_ignore.command("add")
@click.argument("pattern")
@click.pass_obj
def ignore_add(ctx: SecContext, pattern: str) -> None:
    """Add a pattern to the secret ignore list."""
    import yaml

    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    ignore_file = ctx.pilot_sec_dir / "ignore.yaml"
    if not ignore_file.exists():
        out.err("No ignore.yaml found. Run `pilot-sec init` first.")
        raise SystemExit(5)

    data = yaml.safe_load(ignore_file.read_text()) or {}
    data.setdefault("secrets", [])
    if pattern not in data["secrets"]:
        data["secrets"].append(pattern)
        ignore_file.write_text(yaml.dump(data, default_flow_style=False))
        out.success(f"Added ignore pattern: {pattern}")
    else:
        out.info(f"Pattern already ignored: {pattern}")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

_REDACT_PATTERNS = [
    (re.compile(r'((?:password|passwd|secret|api[_-]?key|token|credential)["\s]*[=:]["\s]*)([^\s\n"\']{8,})', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(AKIA[0-9A-Z]{16})'), '***AWS-KEY-REDACTED***'),
    (re.compile(r'(ghp_[A-Za-z0-9]{36})'), '***GH-TOKEN-REDACTED***'),
]


def _redact_secrets(content: str) -> tuple[str, int]:
    count = 0
    for pattern, replacement in _REDACT_PATTERNS:
        new_content, n = re.subn(pattern, replacement, content)
        content = new_content
        count += n
    return content, count


def _group_by_file(summary) -> dict[str, int]:
    result: dict[str, int] = {}
    for f in summary.findings:
        key = f.file_path or "<unknown>"
        result[key] = result.get(key, 0) + 1
    return result
