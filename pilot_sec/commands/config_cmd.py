"""pilot-sec config — configuration lifecycle."""

from __future__ import annotations

import json
from typing import Optional

import click
import yaml

from pilot_sec.core.config import PilotSecConfig
from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter


@click.group("config")
@click.pass_obj
def config_group(ctx: SecContext) -> None:
    """Manage pilot-sec configuration."""


@config_group.command("show")
@click.pass_obj
def config_show(ctx: SecContext) -> None:
    """Display current configuration."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    cfg = _load(ctx)

    if ctx.output_format == "json":
        print(json.dumps(cfg.to_dict(), indent=2))
    elif ctx.output_format == "yaml":
        print(yaml.dump(cfg.to_dict(), default_flow_style=False), end="")
    else:
        from rich.pretty import Pretty
        out.console.print(Pretty(cfg.to_dict()))
        if cfg.path:
            out.console.print(f"\n[dim]Config file: {cfg.path}[/dim]")


@config_group.command("get")
@click.argument("key")
@click.pass_obj
def config_get(ctx: SecContext, key: str) -> None:
    """Get a configuration value by dot-notation key."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    cfg = _load(ctx)
    value = cfg.get(key)
    if value is None:
        out.err(f"Key not found: {key}")
        raise SystemExit(5)
    if ctx.output_format == "json":
        print(json.dumps({key: value}, indent=2))
    else:
        print(value)


@config_group.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_obj
def config_set(ctx: SecContext, key: str, value: str) -> None:
    """Set a configuration value."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    if not ctx.is_initialized():
        out.err("Not initialized. Run `pilot-sec init` first.")
        raise SystemExit(5)

    cfg = _load(ctx)
    old = cfg.get(key)
    cfg.set(key, value)
    if not ctx.dry_run:
        cfg.save()
        out.success(f"{key} = {cfg.get(key)}  (was: {old})")
    else:
        out.info(f"  dry-run: would set {key} = {value}")


@config_group.command("validate")
@click.pass_obj
def config_validate(ctx: SecContext) -> None:
    """Validate the current configuration."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    cfg = _load(ctx)
    errors = cfg.validate()
    if not errors:
        out.success("Configuration is valid")
    else:
        for err in errors:
            out.err(err)
        raise SystemExit(5)


@config_group.command("migrate")
@click.pass_obj
def config_migrate(ctx: SecContext) -> None:
    """Migrate config to latest schema version."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    if not ctx.is_initialized():
        out.err("Not initialized.")
        raise SystemExit(5)
    cfg = _load(ctx)
    # Apply any missing defaults
    from pilot_sec.core.config import DEFAULT_CONFIG, _deep_merge
    migrated = _deep_merge(DEFAULT_CONFIG, cfg.to_dict())
    cfg._data = migrated
    if not ctx.dry_run:
        cfg.save()
        out.success("Config migrated to latest schema")
    else:
        out.info("  dry-run: would migrate config")


def _load(ctx: SecContext) -> PilotSecConfig:
    if ctx.is_initialized():
        return PilotSecConfig.load(ctx.pilot_sec_dir, ctx.config_path)
    return PilotSecConfig.defaults()
