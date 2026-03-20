"""pilot-sec session — session lifecycle management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
from rich.table import Table

from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter
from pilot_sec.core.session_manager import SessionManager


@click.group("session")
@click.pass_obj
def session_group(ctx: SecContext) -> None:
    """Manage audit sessions."""


@session_group.command("start")
@click.option("--name", default=None, help="Human name for this session")
@click.pass_obj
def session_start(ctx: SecContext, name: Optional[str]) -> None:
    """Start a new session."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    mgr = SessionManager(ctx.sessions_dir)
    session = mgr.start(name=name)

    if ctx.output_format == "json":
        print(json.dumps(session.to_dict(), indent=2))
    else:
        out.success(f"Session started: [bold]{session.id}[/bold]")
        if name:
            out.console.print(f"  Name : {name}")
        out.console.print(f"  File : {session.path}")
        out.console.print()
        out.console.print("Use [cyan]pilot-sec run[/cyan] and [cyan]pilot-sec scan[/cyan] to record activity.")
        out.console.print("Stop with [cyan]pilot-sec session stop[/cyan].")


@session_group.command("stop")
@click.option("--id", "session_id", default=None, help="Session ID (default: current)")
@click.pass_obj
def session_stop(ctx: SecContext, session_id: Optional[str]) -> None:
    """Stop the active session."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    mgr = SessionManager(ctx.sessions_dir)
    session = mgr.stop(session_id)
    if not session:
        out.warn("No active session found.")
        raise SystemExit(0)

    if ctx.output_format == "json":
        print(json.dumps(session.to_dict(), indent=2))
    else:
        out.success(f"Session stopped: {session.id}")
        out.console.print(f"  Commands recorded : {len(session.to_dict().get('commands', []))}")
        out.console.print(f"  Findings recorded : {len(session.to_dict().get('findings', []))}")
        out.console.print(f"  Log               : {session.path}")


@session_group.command("status")
@click.pass_obj
def session_status(ctx: SecContext) -> None:
    """Show current session status."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    mgr = SessionManager(ctx.sessions_dir)
    session = mgr.current()

    if not session:
        out.console.print("[dim]No active session.[/dim]")
        raise SystemExit(0)

    data = session.to_dict()
    if ctx.output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        out.console.print(f"[bold]Active session:[/bold] {session.id}")
        out.console.print(f"  Name      : {session.name}")
        out.console.print(f"  Started   : {session.started_at}")
        out.console.print(f"  Commands  : {len(data.get('commands', []))}")
        out.console.print(f"  Findings  : {len(data.get('findings', []))}")


@session_group.command("list")
@click.pass_obj
def session_list(ctx: SecContext) -> None:
    """List all sessions."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    mgr = SessionManager(ctx.sessions_dir)
    sessions = mgr.list_sessions()

    if not sessions:
        out.info("No sessions found.")
        return

    if ctx.output_format == "json":
        print(json.dumps(sessions, indent=2))
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Status", width=10)
    table.add_column("Started")
    table.add_column("Cmds", justify="right")
    table.add_column("Findings", justify="right")

    for s in sessions:
        color = "green" if s["status"] == "active" else "dim"
        table.add_row(
            s.get("id", ""),
            s.get("name", ""),
            f"[{color}]{s.get('status', '')}[/{color}]",
            (s.get("started_at") or "")[:19],
            str(s.get("commands", 0)),
            str(s.get("findings", 0)),
        )
    out.console.print(table)


@session_group.command("replay")
@click.argument("session_id")
@click.pass_obj
def session_replay(ctx: SecContext, session_id: str) -> None:
    """Replay the command timeline of a session."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    mgr = SessionManager(ctx.sessions_dir)
    session = mgr.load(session_id)
    if not session:
        out.err(f"Session not found: {session_id}")
        raise SystemExit(1)

    data = session.to_dict()
    out.console.print(f"[bold]Session replay:[/bold] {session_id}")
    for cmd_entry in data.get("commands", []):
        ts = cmd_entry.get("timestamp", "")[:19]
        cmd = cmd_entry.get("command", "")
        rc = cmd_entry.get("result", {}).get("exit_code", "?")
        color = "green" if rc == 0 else "red"
        out.console.print(f"  [dim]{ts}[/dim]  [{color}]{cmd}[/{color}]")


@session_group.command("export")
@click.argument("session_id")
@click.option("--output", "output_path", default=None, metavar="PATH")
@click.pass_obj
def session_export(ctx: SecContext, session_id: str, output_path: Optional[str]) -> None:
    """Export a session to a file."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    mgr = SessionManager(ctx.sessions_dir)
    session = mgr.load(session_id)
    if not session:
        out.err(f"Session not found: {session_id}")
        raise SystemExit(1)

    dest = Path(output_path) if output_path else ctx.reports_dir / f"{session_id}.export.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(session.to_dict(), indent=2))
    out.success(f"Session exported → {dest}")
