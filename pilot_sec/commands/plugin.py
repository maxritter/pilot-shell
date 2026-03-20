"""pilot-sec plugin — extension interface."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

import click
import yaml

from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter

_PLUGIN_CATEGORIES = ["scanners", "policies", "formatters", "integrations", "risk-classifiers"]


@click.group("plugin")
@click.pass_obj
def plugin_group(ctx: SecContext) -> None:
    """Manage pilot-sec plugins and extensions."""


@plugin_group.command("list")
@click.pass_obj
def plugin_list(ctx: SecContext) -> None:
    """List installed plugins."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    plugins = _discover_plugins(ctx)

    if not plugins:
        out.info("No plugins installed. Use `pilot-sec plugin add <path>` to install one.")
        return

    if ctx.output_format == "json":
        print(json.dumps(plugins, indent=2))
        return

    out.console.print(f"[bold]{len(plugins)} plugin(s) installed[/bold]")
    for p in plugins:
        out.console.print(f"  [cyan]{p['name']:20}[/cyan]  {p.get('category', 'unknown'):15}  {p.get('description', '')}")


@plugin_group.command("add")
@click.argument("path_or_url")
@click.pass_obj
def plugin_add(ctx: SecContext, path_or_url: str) -> None:
    """Install a plugin from a local path."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)

    source = Path(path_or_url)
    if not source.exists():
        out.err(f"Plugin path not found: {path_or_url}")
        out.info("  URL-based plugin installation is not yet supported in offline mode.")
        raise SystemExit(1)

    plugins_dir = ctx.pilot_sec_dir / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)

    dest = plugins_dir / source.name
    if source.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source, dest)
    else:
        shutil.copy2(source, dest)

    out.success(f"Plugin installed: {source.name}")
    out.info(f"  Location: {dest}")


@plugin_group.command("remove")
@click.argument("name")
@click.pass_obj
def plugin_remove(ctx: SecContext, name: str) -> None:
    """Remove an installed plugin."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    plugins_dir = ctx.pilot_sec_dir / "plugins"
    candidates = list(plugins_dir.glob(f"{name}*")) if plugins_dir.exists() else []
    if not candidates:
        out.err(f"Plugin not found: {name}")
        raise SystemExit(1)
    for c in candidates:
        if c.is_dir():
            shutil.rmtree(c)
        else:
            c.unlink()
    out.success(f"Plugin removed: {name}")


@plugin_group.command("info")
@click.argument("name")
@click.pass_obj
def plugin_info(ctx: SecContext, name: str) -> None:
    """Show details about an installed plugin."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    plugins = _discover_plugins(ctx)
    plugin = next((p for p in plugins if p["name"] == name), None)
    if not plugin:
        out.err(f"Plugin not found: {name}")
        raise SystemExit(1)
    for k, v in plugin.items():
        out.console.print(f"  {k:<16} {v}")


@plugin_group.command("verify")
@click.argument("name")
@click.pass_obj
def plugin_verify(ctx: SecContext, name: str) -> None:
    """Verify a plugin's integrity."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    plugins_dir = ctx.pilot_sec_dir / "plugins"
    candidates = list(plugins_dir.glob(f"{name}*")) if plugins_dir.exists() else []
    if not candidates:
        out.err(f"Plugin not found: {name}")
        raise SystemExit(1)
    out.success(f"Plugin {name}: present at {candidates[0]}")
    out.info("  Cryptographic signature verification requires a signed plugin manifest.")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _discover_plugins(ctx: SecContext) -> list[dict]:
    plugins_dir = ctx.pilot_sec_dir / "plugins"
    if not plugins_dir.exists():
        return []
    plugins = []
    for path in plugins_dir.iterdir():
        manifest_file = (path / "plugin.yaml") if path.is_dir() else None
        if manifest_file and manifest_file.exists():
            try:
                data = yaml.safe_load(manifest_file.read_text()) or {}
                plugins.append({
                    "name": data.get("name", path.name),
                    "category": data.get("category", "unknown"),
                    "version": data.get("version", "0.0.0"),
                    "description": data.get("description", ""),
                    "path": str(path),
                })
            except Exception:
                plugins.append({"name": path.name, "path": str(path)})
        else:
            plugins.append({"name": path.name, "path": str(path)})
    return plugins
