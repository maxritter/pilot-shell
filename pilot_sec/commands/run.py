"""pilot-sec run — execute with security mediation."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.panel import Panel

from pilot_sec.core.audit import AuditLog
from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter
from pilot_sec.core.risk import classify_command
from pilot_sec.core.session_manager import SessionManager, new_run_id

_RISK_LEVELS = ["low", "medium", "high", "critical"]
_SCOPE_CHOICES = ["repo", "workspace", "env", "network", "custom"]


@click.command("run")
@click.argument("command", nargs=-1, required=True)
@click.option("--risk", "risk_level", default=None, type=click.Choice(_RISK_LEVELS), help="Override risk level")
@click.option("--require-approval", is_flag=True, help="Block until approval token provided")
@click.option("--scope", default=None, type=click.Choice(_SCOPE_CHOICES), help="Execution scope")
@click.option("--allow-network", is_flag=True, help="Allow network access")
@click.option("--allow-write", is_flag=True, help="Allow filesystem writes")
@click.option("--allow-secrets-read", is_flag=True, help="Allow reading secrets")
@click.option("--timeout", default=None, help="Command timeout (e.g. 30s, 5m)")
@click.option("--simulate", is_flag=True, help="Simulate without executing")
@click.option("--explain", is_flag=True, help="Explain policy decision and exit")
@click.option("--reason", default=None, help="Human rationale for this run")
@click.option("--tag", "tags", multiple=True, metavar="K=V", help="Metadata tags")
@click.pass_obj
def run_cmd(
    ctx: SecContext,
    command: tuple[str, ...],
    risk_level: Optional[str],
    require_approval: bool,
    scope: Optional[str],
    allow_network: bool,
    allow_write: bool,
    allow_secrets_read: bool,
    timeout: Optional[str],
    simulate: bool,
    explain: bool,
    reason: Optional[str],
    tags: tuple[str, ...],
) -> None:
    """Execute a command with security mediation and audit trail."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)

    cmd_str = " ".join(command)
    run_id = new_run_id()
    run_dir = ctx.runs_dir / run_id
    audit = AuditLog(run_dir=run_dir, run_id=run_id, enabled=ctx.audit)

    # 1. Classify the command
    detected_risk = risk_level or classify_command(cmd_str)

    # 2. Evaluate against global --fail-on / policy
    policy_level = ctx.get_config().get("policy.level", "standard") if ctx.is_initialized() else "standard"
    decision = _evaluate_policy(cmd_str, detected_risk, policy_level, require_approval, ctx)

    audit.record("classify", {"command": cmd_str, "detected_risk": detected_risk})
    audit.record("policy_eval", {"decision": decision, "policy_level": policy_level})

    # 3. Display decision
    _print_decision(out, cmd_str, detected_risk, decision, run_id, run_dir, reason)

    if explain:
        _print_explanation(out, cmd_str, detected_risk, decision, policy_level)
        raise SystemExit(0)

    if decision == "block":
        audit.finalize("blocked", "block")
        raise SystemExit(3)

    if decision == "approval_required":
        if ctx.yes or ctx.dry_run:
            out.warn("Auto-approving (--yes / --dry-run)")
        else:
            out.console.print("[yellow]Approval required.[/yellow] Provide approval token to continue:")
            token = click.prompt("Approval token", hide_input=True, default="")
            if not token:
                out.err("No approval token provided — blocked.")
                audit.finalize("blocked", "approval_required")
                raise SystemExit(6)

    if ctx.dry_run or simulate:
        out.console.print(f"[dim]dry-run / simulate — would execute:[/dim] {cmd_str}")
        audit.finalize("simulated", decision)
        _emit_result(out, ctx, cmd_str, "simulated", decision, run_id)
        raise SystemExit(0)

    # 4. Execute
    audit.record("execute_start", {"command": cmd_str})
    t0 = time.monotonic()

    try:
        timeout_secs = _parse_timeout(timeout) if timeout else None
        result = subprocess.run(cmd_str, shell=True, timeout=timeout_secs)
        elapsed = time.monotonic() - t0
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        out.err(f"Command timed out after {timeout}")
        audit.finalize("timeout", "error")
        raise SystemExit(1)
    except Exception as exc:
        out.err(f"Execution failed: {exc}")
        audit.finalize("error", "error")
        raise SystemExit(1)

    # 5. Record
    status = "success" if exit_code == 0 else "failed"
    audit.finalize(status, decision, {"exit_code": exit_code, "elapsed_s": round(elapsed, 2)})

    # Attach to session if active
    session_mgr = SessionManager(ctx.sessions_dir)
    current_session = session_mgr.current()
    if current_session:
        current_session.record_command(cmd_str, {"run_id": run_id, "exit_code": exit_code, "status": status})

    _emit_result(out, ctx, cmd_str, status, decision, run_id, run_dir)
    raise SystemExit(exit_code)


def _evaluate_policy(
    cmd_str: str,
    risk: str,
    policy_level: str,
    require_approval: bool,
    ctx: SecContext,
) -> str:
    """Return: allow | warn | block | approval_required"""
    if require_approval:
        return "approval_required"

    # If caller explicitly set --fail-on none, allow everything
    if ctx.fail_on == "none":
        return "allow"

    effective_threshold = ctx.fail_on or _policy_fail_on(policy_level)
    risk_values = {"critical": 4, "high": 3, "medium": 2, "low": 1}

    if risk_values.get(risk, 0) >= risk_values.get(effective_threshold, 3):
        if policy_level == "strict":
            return "block"
        return "warn"
    return "allow"


def _policy_fail_on(policy_level: str) -> str:
    return {"strict": "medium", "standard": "high", "relaxed": "critical"}.get(policy_level, "high")


def _print_decision(out: OutputWriter, cmd_str: str, risk: str, decision: str, run_id: str, run_dir: Path, reason: Optional[str]) -> None:
    color_map = {"allow": "green", "warn": "yellow", "block": "red", "approval_required": "yellow"}
    color = color_map.get(decision, "white")

    out.console.print()
    out.console.print(f"  Command : [bold]{cmd_str}[/bold]")
    out.console.print(f"  Risk    : [bold]{risk}[/bold]")
    out.console.print(f"  Decision: [{color}]{decision.upper()}[/{color}]")
    if reason:
        out.console.print(f"  Reason  : {reason}")
    out.console.print(f"  Run ID  : [dim]{run_id}[/dim]")
    out.console.print(f"  Log     : [dim]{run_dir / 'event.json'}[/dim]")
    out.console.print()


def _print_explanation(out: OutputWriter, cmd_str: str, risk: str, decision: str, policy_level: str) -> None:
    out.console.print(Panel(
        f"[bold]Command:[/bold] {cmd_str}\n"
        f"[bold]Detected risk:[/bold] {risk}\n"
        f"[bold]Policy level:[/bold] {policy_level}\n"
        f"[bold]Decision:[/bold] {decision}\n\n"
        "Use [cyan]--risk <level>[/cyan] to override the detected risk.\n"
        "Use [cyan]--reason[/cyan] to attach a human rationale.\n"
        "Use [cyan]--require-approval[/cyan] to force an approval gate.",
        title="Policy Explanation",
    ))


def _emit_result(out: OutputWriter, ctx: SecContext, cmd_str: str, status: str, decision: str, run_id: str, run_dir: Path | None = None) -> None:
    if ctx.output_format in ("json", "yaml"):
        out.emit_result(
            command=f"run {cmd_str}",
            status=status,
            decision=decision,
            run_id=run_id,
            session_id=ctx.session_id,
            artifacts=[str(run_dir / "event.json")] if run_dir else [],
        )


def _parse_timeout(t: str) -> Optional[float]:
    t = t.strip()
    if t.endswith("s"):
        return float(t[:-1])
    if t.endswith("m"):
        return float(t[:-1]) * 60
    if t.endswith("h"):
        return float(t[:-1]) * 3600
    return float(t)


