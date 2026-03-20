"""pilot-sec — governed security operator shell.

Usage:
    pilot-sec [global flags] <command> [subcommand] [args]
"""

from __future__ import annotations

import sys
from typing import Optional

import click
from rich.console import Console

import pilot_sec
from pilot_sec.core.context import SecContext

# ------------------------------------------------------------------
# Global CLI group
# ------------------------------------------------------------------

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    max_content_width=100,
)

_BANNER = "[bold cyan]pilot-sec[/bold cyan] [dim]v{version} — governed security operator shell[/dim]"


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--config", "config_path", default=None, metavar="PATH", help="Config file path")
@click.option("--profile", default=None, help="Org/team profile name")
@click.option(
    "--format", "output_format", default="text",
    type=click.Choice(["text", "json", "sarif", "yaml", "table"]),
    help="Output format",
    show_default=True,
)
@click.option("--output", "output_path", default=None, metavar="PATH", help="Write result to file")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--no-color", is_flag=True, help="Disable color output")
@click.option("--project", "project_path", default=None, metavar="PATH", help="Repo root or target dir")
@click.option("--session", "session_id", default=None, metavar="ID", help="Attach to a named session")
@click.option("--policy-pack", default=None, metavar="PATH", help="Extra policy bundle to load")
@click.option(
    "--fail-on", default=None,
    type=click.Choice(["none", "low", "medium", "high", "critical"]),
    help="Exit with code 4 if findings meet or exceed this severity",
)
@click.option("--risk-threshold", default=None, type=float, metavar="SCORE", help="Numeric risk score cutoff (0-100)")
@click.option("--offline", is_flag=True, help="Offline mode — skip network operations")
@click.option("--log-dir", default=None, metavar="PATH", help="Override run log directory")
@click.option("--audit/--no-audit", default=True, help="Enable/disable audit trail (default: on)")
@click.option("--dry-run", is_flag=True, help="Simulate without making changes or running commands")
@click.option("--yes", "-y", is_flag=True, help="Auto-approve all prompts")
@click.version_option(version=pilot_sec.__version__, prog_name="pilot-sec")
@click.pass_context
def cli(
    ctx: click.Context,
    config_path: Optional[str],
    profile: Optional[str],
    output_format: str,
    output_path: Optional[str],
    quiet: bool,
    verbose: bool,
    no_color: bool,
    project_path: Optional[str],
    session_id: Optional[str],
    policy_pack: Optional[str],
    fail_on: Optional[str],
    risk_threshold: Optional[float],
    offline: bool,
    log_dir: Optional[str],
    audit: bool,
    dry_run: bool,
    yes: bool,
) -> None:
    """pilot-sec — governed security operator shell.

    \b
    Verbs:
      run       Execute with security mediation
      scan      Inspect current security state
      diff      Compare posture over time
      policy    Evaluate and enforce rules
      secret    Detect and manage secret exposure
      sbom      Supply-chain evidence
      attest    Build and release provenance
      pr        PR-level security gates
      env       Runtime boundary management
      session   Audit session lifecycle
      report    Generate security artifacts
      config    Configuration management
      plugin    Extensibility
      doctor    Validate tooling and config
      init      Bootstrap a repository

    \b
    Examples:
      pilot-sec init --template devsecops
      pilot-sec scan all
      pilot-sec run -- terraform apply
      pilot-sec pr check --base origin/main --head HEAD
      pilot-sec report findings --format sarif --output findings.sarif
    """
    ctx.ensure_object(dict)
    ctx.obj = SecContext(
        config_path=config_path,
        profile=profile,
        output_format=output_format,
        output_path=output_path,
        quiet=quiet,
        verbose=verbose,
        no_color=no_color,
        project_path=project_path,
        session_id=session_id,
        policy_pack=policy_pack,
        fail_on=fail_on,
        risk_threshold=risk_threshold,
        offline=offline,
        log_dir=log_dir,
        audit=audit,
        dry_run=dry_run,
        yes=yes,
    )


# ------------------------------------------------------------------
# Register all command groups
# ------------------------------------------------------------------

from pilot_sec.commands.init import init_cmd
from pilot_sec.commands.run import run_cmd
from pilot_sec.commands.scan import scan_group
from pilot_sec.commands.diff import diff_group
from pilot_sec.commands.policy import policy_group
from pilot_sec.commands.secret import secret_group
from pilot_sec.commands.sbom import sbom_group
from pilot_sec.commands.attest import attest_group
from pilot_sec.commands.pr import pr_group
from pilot_sec.commands.env import env_group
from pilot_sec.commands.session import session_group
from pilot_sec.commands.report import report_group
from pilot_sec.commands.config_cmd import config_group
from pilot_sec.commands.plugin import plugin_group
from pilot_sec.commands.doctor import doctor_group

cli.add_command(init_cmd, name="init")
cli.add_command(run_cmd, name="run")
cli.add_command(scan_group, name="scan")
cli.add_command(diff_group, name="diff")
cli.add_command(policy_group, name="policy")
cli.add_command(secret_group, name="secret")
cli.add_command(sbom_group, name="sbom")
cli.add_command(attest_group, name="attest")
cli.add_command(pr_group, name="pr")
cli.add_command(env_group, name="env")
cli.add_command(session_group, name="session")
cli.add_command(report_group, name="report")
cli.add_command(config_group, name="config")
cli.add_command(plugin_group, name="plugin")
cli.add_command(doctor_group, name="doctor")

# ------------------------------------------------------------------
# Aliases
# ------------------------------------------------------------------

cli.add_command(scan_group, name="s")
cli.add_command(diff_group, name="d")
cli.add_command(policy_group, name="p")
cli.add_command(run_cmd, name="r")
cli.add_command(report_group, name="rep")

# ------------------------------------------------------------------
# version subcommand (standalone + --json flag)
# ------------------------------------------------------------------

@cli.command("version")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_obj
def version_cmd(ctx: SecContext, as_json: bool) -> None:
    """Show pilot-sec version."""
    import json as _json
    if as_json:
        print(_json.dumps({"version": pilot_sec.__version__, "python": sys.version}))
    else:
        Console().print(f"pilot-sec {pilot_sec.__version__}")


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def main() -> None:
    cli(standalone_mode=False, obj={})


if __name__ == "__main__":
    cli()
