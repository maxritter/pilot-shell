"""pilot-sec policy — policy control plane."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
import yaml

from pilot_sec.core.config import PilotSecConfig
from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter


@click.group("policy")
@click.pass_obj
def policy_group(ctx: SecContext) -> None:
    """Evaluate and enforce policy rules."""


@policy_group.command("check")
@click.option("--input", "input_path", default=None, metavar="PATH", help="Findings JSON to evaluate")
@click.option("--context", "context_path", default=None, metavar="PATH", help="Extra context file")
@click.option("--on", "trigger", default=None,
              type=click.Choice(["run", "scan", "pr", "deploy", "commit"]),
              help="Trigger context")
@click.option("--waiver", default=None, metavar="PATH", help="Waiver file")
@click.option("--waiver-id", default=None, help="Specific waiver ID")
@click.pass_obj
def policy_check(ctx: SecContext, input_path: Optional[str], context_path: Optional[str],
                 trigger: Optional[str], waiver: Optional[str], waiver_id: Optional[str]) -> None:
    """Evaluate findings against policy rules. Returns allow/warn/block."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    cfg = _load_config(ctx)
    rules = _load_rules(ctx)

    findings = []
    if input_path:
        try:
            findings = json.loads(Path(input_path).read_text())
        except Exception as exc:
            out.err(f"Failed to read findings: {exc}")
            raise SystemExit(5)

    results = []
    overall = "allow"
    for rule in rules:
        if trigger and rule.get("trigger") and rule["trigger"] != trigger:
            continue
        decision = _evaluate_rule(rule, findings, ctx)
        if decision != "allow":
            results.append({"rule": rule.get("id"), "decision": decision, "description": rule.get("description", "")})
        if decision == "block":
            overall = "block"
        elif decision == "warn" and overall == "allow":
            overall = "warn"

    if ctx.output_format == "json":
        print(json.dumps({"overall": overall, "rules": results, "policy_level": cfg.get("policy.level")}, indent=2))
    else:
        if not results:
            out.success(f"All policy rules passed — decision: [green]{overall.upper()}[/green]")
        else:
            color = "red" if overall == "block" else "yellow"
            out.console.print(f"[bold]Policy check:[/bold] [{color}]{overall.upper()}[/{color}]")
            for r in results:
                icon = "✗" if r["decision"] == "block" else "⚠"
                color = "red" if r["decision"] == "block" else "yellow"
                out.console.print(f"  [{color}]{icon}[/{color}] [{r['rule']}] {r['description']}")

    raise SystemExit(3 if overall == "block" else 2 if overall == "warn" else 0)


@policy_group.command("enforce")
@click.option("--on", "trigger", required=True,
              type=click.Choice(["run", "scan", "pr", "deploy", "commit"]),
              help="Trigger context to enforce on")
@click.option("--decision", "decision_filter", default=None,
              type=click.Choice(["allow", "warn", "block"]),
              help="Only show rules with this decision")
@click.pass_obj
def policy_enforce(ctx: SecContext, trigger: str, decision_filter: Optional[str]) -> None:
    """Make policy decisions binding for a given trigger context."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    rules = _load_rules(ctx)
    trigger_rules = [r for r in rules if r.get("trigger") == trigger or not r.get("trigger")]
    out.console.print(f"[bold]Enforced policy rules for trigger:[/bold] {trigger}")
    for r in trigger_rules:
        action = r.get("action", "warn")
        if decision_filter and action != decision_filter:
            continue
        color = {"block": "red", "warn": "yellow", "allow": "green"}.get(action, "white")
        out.console.print(f"  [{color}]{action.upper():6}[/{color}]  [{r.get('id')}]  {r.get('description', '')}")


@policy_group.command("test")
@click.argument("policy_dir", default=None, required=False)
@click.pass_obj
def policy_test(ctx: SecContext, policy_dir: Optional[str]) -> None:
    """Test policy files for syntax and logic errors."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    target = Path(policy_dir) if policy_dir else ctx.policies_dir

    if not target.exists():
        out.warn(f"Policy directory not found: {target}")
        raise SystemExit(5)

    errors = 0
    for policy_file in target.glob("**/*.yaml"):
        try:
            data = yaml.safe_load(policy_file.read_text())
            if not isinstance(data, dict):
                out.err(f"{policy_file}: expected a YAML mapping")
                errors += 1
                continue
            rules = data.get("rules", [])
            for rule in rules:
                if not rule.get("id"):
                    out.warn(f"{policy_file}: rule missing 'id'")
                if not rule.get("action"):
                    out.warn(f"{policy_file}: rule '{rule.get('id')}' missing 'action'")
            out.success(f"{policy_file.name}: {len(rules)} rule(s) valid")
        except yaml.YAMLError as exc:
            out.err(f"{policy_file}: YAML parse error — {exc}")
            errors += 1

    raise SystemExit(5 if errors else 0)


@policy_group.command("list")
@click.pass_obj
def policy_list(ctx: SecContext) -> None:
    """List all policy rules."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    rules = _load_rules(ctx)
    if not rules:
        out.info("No policy rules found. Run `pilot-sec init` to create a baseline.")
        return
    out.console.print(f"[bold]{len(rules)} policy rules[/bold]")
    for rule in rules:
        action = rule.get("action", "warn")
        color = {"block": "red", "warn": "yellow", "allow": "green"}.get(action, "white")
        out.console.print(f"  [{color}]{action.upper():6}[/{color}]  [cyan]{rule.get('id', '?')}[/cyan]  {rule.get('description', '')}")


@policy_group.command("explain")
@click.argument("rule_id")
@click.pass_obj
def policy_explain(ctx: SecContext, rule_id: str) -> None:
    """Explain a specific policy rule."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    rules = _load_rules(ctx)
    rule = next((r for r in rules if r.get("id") == rule_id), None)
    if not rule:
        out.err(f"Rule not found: {rule_id}")
        raise SystemExit(1)
    out.console.print(f"[bold]{rule.get('id')}[/bold]")
    out.console.print(f"  Description : {rule.get('description', '')}")
    out.console.print(f"  Trigger     : {rule.get('trigger', 'any')}")
    out.console.print(f"  Condition   : {rule.get('condition', '')}")
    out.console.print(f"  Action      : {rule.get('action', '')}")
    out.console.print(f"  Severity    : {rule.get('severity', '')}")


@policy_group.command("trace")
@click.option("--rule", "rule_id", required=True, help="Rule ID to trace")
@click.pass_obj
def policy_trace(ctx: SecContext, rule_id: str) -> None:
    """Trace how a rule would apply in current context."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    out.info(f"Tracing rule: {rule_id}")
    out.info("  (Full trace requires active run or scan context)")


@policy_group.group("pack")
@click.pass_obj
def policy_pack(ctx: SecContext) -> None:
    """Manage policy packs."""


@policy_pack.command("add")
@click.argument("path_or_url")
@click.pass_obj
def pack_add(ctx: SecContext, path_or_url: str) -> None:
    """Add a policy pack."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    source = Path(path_or_url)
    if source.exists():
        import shutil
        dest = ctx.policies_dir / source.name
        shutil.copy2(source, dest)
        out.success(f"Policy pack added: {dest.name}")
    else:
        out.err(f"Path not found: {path_or_url}  (URL packs not yet supported in offline mode)")
        raise SystemExit(1)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _load_config(ctx: SecContext) -> PilotSecConfig:
    if ctx.is_initialized():
        return PilotSecConfig.load(ctx.pilot_sec_dir, ctx.policy_pack)
    return PilotSecConfig.defaults()


def _load_rules(ctx: SecContext) -> list[dict]:
    rules: list[dict] = []
    if not ctx.policies_dir.exists():
        return rules
    for policy_file in ctx.policies_dir.glob("**/*.yaml"):
        try:
            data = yaml.safe_load(policy_file.read_text()) or {}
            rules.extend(data.get("rules", []))
        except Exception:
            pass
    return rules


def _evaluate_rule(rule: dict, findings: list[dict], ctx: SecContext) -> str:
    """Very simple rule evaluator — extend with a proper OPA/Rego engine later."""
    condition = rule.get("condition", "")
    action = rule.get("action", "warn")

    # Trivially evaluate conditions based on findings
    if "findings.critical > 0" in condition:
        if any(f.get("severity") == "critical" for f in findings):
            return action
    if "findings.high > 0" in condition:
        if any(f.get("severity") == "high" for f in findings):
            return action

    return "allow"
