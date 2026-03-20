"""pilot-sec env — environment boundary management."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import click
import yaml

from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter


@click.group("env")
@click.pass_obj
def env_group(ctx: SecContext) -> None:
    """Define and inspect the runtime environment boundary."""


@env_group.command("inspect")
@click.pass_obj
def env_inspect(ctx: SecContext) -> None:
    """Show current environment state and active guardrails."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)

    env_state = {
        "cwd": str(Path.cwd()),
        "project_root": str(ctx.project_root),
        "pilot_sec_dir": str(ctx.pilot_sec_dir),
        "initialized": ctx.is_initialized(),
        "session_id": ctx.session_id,
        "dry_run": ctx.dry_run,
        "offline": ctx.offline,
    }

    if ctx.output_format == "json":
        print(json.dumps(env_state, indent=2))
        return

    out.console.print("[bold]Environment State[/bold]")
    for k, v in env_state.items():
        out.console.print(f"  {k:<20} {v}")

    # Show security-relevant env vars (names only, not values)
    sensitive_keys = [k for k in os.environ if any(
        p in k.lower() for p in ["secret", "token", "key", "password", "credential"]
    )]
    if sensitive_keys:
        out.console.print()
        out.console.print(f"[yellow]Sensitive env vars detected ({len(sensitive_keys)}):[/yellow]")
        for k in sensitive_keys[:10]:
            out.console.print(f"  {k}")
        if len(sensitive_keys) > 10:
            out.console.print(f"  ... and {len(sensitive_keys) - 10} more")


@env_group.command("lock")
@click.option("--network", default=None,
              type=click.Choice(["on", "off", "restricted"]),
              help="Network access level")
@click.option("--write", "write_mode", default=None,
              type=click.Choice(["off", "repo-only", "workspace", "full"]),
              help="Write access scope")
@click.option("--secrets", "secrets_mode", default=None,
              type=click.Choice(["deny", "prompt", "allow"]),
              help="Secret access mode")
@click.pass_obj
def env_lock(ctx: SecContext, network: Optional[str], write_mode: Optional[str], secrets_mode: Optional[str]) -> None:
    """Apply environment guardrails for subsequent commands."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)

    lock_file = ctx.pilot_sec_dir / "env.lock.yaml"
    lock_data: dict = {}
    if lock_file.exists():
        lock_data = yaml.safe_load(lock_file.read_text()) or {}

    if network:
        lock_data["network"] = network
    if write_mode:
        lock_data["write"] = write_mode
    if secrets_mode:
        lock_data["secrets"] = secrets_mode

    if not ctx.dry_run:
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text(yaml.dump(lock_data, default_flow_style=False))
        out.success(f"Environment lock applied → {lock_file}")
    else:
        out.info("  dry-run: would write env.lock.yaml")

    for k, v in lock_data.items():
        out.console.print(f"  {k:<12} {v}")


@env_group.command("allow")
@click.argument("resource")
@click.argument("target")
@click.pass_obj
def env_allow(ctx: SecContext, resource: str, target: str) -> None:
    """Allow specific resource access (e.g. network github.com)."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    lock_file = ctx.pilot_sec_dir / "env.lock.yaml"
    lock_data: dict = {}
    if lock_file.exists():
        lock_data = yaml.safe_load(lock_file.read_text()) or {}

    lock_data.setdefault("allow", {}).setdefault(resource, [])
    if target not in lock_data["allow"][resource]:
        lock_data["allow"][resource].append(target)

    if not ctx.dry_run:
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text(yaml.dump(lock_data, default_flow_style=False))
    out.success(f"Allowed: {resource} → {target}")


@env_group.command("deny")
@click.argument("resource")
@click.argument("target")
@click.pass_obj
def env_deny(ctx: SecContext, resource: str, target: str) -> None:
    """Deny specific resource access."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    lock_file = ctx.pilot_sec_dir / "env.lock.yaml"
    lock_data: dict = {}
    if lock_file.exists():
        lock_data = yaml.safe_load(lock_file.read_text()) or {}

    lock_data.setdefault("deny", {}).setdefault(resource, [])
    if target not in lock_data["deny"][resource]:
        lock_data["deny"][resource].append(target)

    if not ctx.dry_run:
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text(yaml.dump(lock_data, default_flow_style=False))
    out.success(f"Denied: {resource} → {target}")


@env_group.command("snapshot")
@click.option("--output", "output_path", default=None, metavar="PATH")
@click.pass_obj
def env_snapshot(ctx: SecContext, output_path: Optional[str]) -> None:
    """Save a snapshot of the current environment state."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    dest = Path(output_path) if output_path else ctx.reports_dir / "env.json"

    snapshot = {
        "cwd": str(Path.cwd()),
        "project_root": str(ctx.project_root),
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
        "env_vars_count": len(os.environ),
        "sensitive_vars": [k for k in os.environ if any(
            p in k.lower() for p in ["secret", "token", "key", "password"]
        )],
    }

    if not ctx.dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(snapshot, indent=2))
        out.success(f"Environment snapshot written → {dest}")
    else:
        out.info(f"  dry-run: would write {dest}")
