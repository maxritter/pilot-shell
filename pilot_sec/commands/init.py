"""pilot-sec init — bootstrap a repository."""

from __future__ import annotations

import shutil
from pathlib import Path

import click
import yaml

from pilot_sec.core.config import DEFAULT_CONFIG
from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter

_TEMPLATES: dict[str, dict] = {
    "devsecops": {
        "policy": {"level": "strict", "packs": ["devsecops-baseline"]},
        "scanners": {"enabled": []},
        "logging": {"audit": True, "redaction": True},
    },
    "node": {
        "policy": {"level": "standard"},
        "scanners": {"enabled": ["npm-audit", "semgrep", "gitleaks"]},
    },
    "python": {
        "policy": {"level": "standard"},
        "scanners": {"enabled": ["pip-audit", "bandit", "semgrep", "gitleaks"]},
    },
    "minimal": {
        "policy": {"level": "relaxed"},
        "scanners": {"enabled": ["gitleaks"]},
    },
}

_DEFAULT_IGNORE = """# pilot-sec ignore file
# Patterns here suppress findings from scan, secret, and diff commands.

paths:
  - "vendor/**"
  - "node_modules/**"
  - ".venv/**"
  - "**/__pycache__/**"
  - "dist/**"
  - "build/**"

rules: []
"""

_DEFAULT_POLICY = """# pilot-sec baseline policy pack
# Each rule is evaluated by `pilot-sec policy check`.

rules:
  - id: require-scan-before-deploy
    description: A scan must pass before deployment commands run.
    trigger: run
    condition: "command matches deploy|terraform apply|kubectl apply"
    action: block
    severity: high

  - id: no-critical-findings-on-merge
    description: Block merge when critical findings exist.
    trigger: pr
    condition: "findings.critical > 0"
    action: block
    severity: critical

  - id: require-session-for-prod
    description: Production commands must run inside a named session.
    trigger: run
    condition: "scope == prod and session == null"
    action: warn
    severity: medium
"""


@click.command("init")
@click.option("--template", default="devsecops",
              type=click.Choice(list(_TEMPLATES.keys()) + ["devsecops", "node", "python", "minimal"]),
              help="Starter template")
@click.option("--policy-level", default=None,
              type=click.Choice(["relaxed", "standard", "strict"]),
              help="Override policy enforcement level")
@click.option("--no-hooks", is_flag=True, help="Skip pre-commit hook installation")
@click.pass_obj
def init_cmd(ctx: SecContext, template: str, policy_level: str | None, no_hooks: bool) -> None:
    """Bootstrap a repository with pilot-sec configuration."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    pilot_sec_dir = ctx.pilot_sec_dir

    if pilot_sec_dir.exists() and not ctx.yes:
        existing = list(pilot_sec_dir.iterdir())
        if existing:
            out.warn(f".pilot-sec/ already exists at {pilot_sec_dir}")
            if not click.confirm("Re-initialize? (existing config will be preserved)", default=False):
                out.info("Aborted.")
                raise SystemExit(0)

    _create_directory_structure(pilot_sec_dir, out)
    _write_config(pilot_sec_dir, template, policy_level, out)
    _write_ignore(pilot_sec_dir, out)
    _write_baseline_policy(pilot_sec_dir, out)

    if not no_hooks:
        _suggest_hooks(ctx.project_root, out)

    out.console.print()
    out.console.print(f"[bold green]✓ pilot-sec initialized[/bold green] → {pilot_sec_dir}")
    out.console.print()
    out.console.print("Next steps:")
    out.console.print("  [cyan]pilot-sec doctor[/cyan]              validate tooling")
    out.console.print("  [cyan]pilot-sec scan all[/cyan]            run first scan")
    out.console.print("  [cyan]pilot-sec session start[/cyan]       begin a tracked session")


def _create_directory_structure(pilot_sec_dir: Path, out: OutputWriter) -> None:
    dirs = [
        pilot_sec_dir,
        pilot_sec_dir / "policies",
        pilot_sec_dir / "sessions",
        pilot_sec_dir / "reports",
        pilot_sec_dir / "runs",
        pilot_sec_dir / "cache",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        out.step(f"created {d.relative_to(pilot_sec_dir.parent)}")


def _write_config(pilot_sec_dir: Path, template: str, policy_level: str | None, out: OutputWriter) -> None:
    import copy

    config_path = pilot_sec_dir / "config.yaml"
    if config_path.exists():
        out.info(f"  config.yaml already exists — skipping")
        return

    config = copy.deepcopy(DEFAULT_CONFIG)
    overrides = _TEMPLATES.get(template, {})
    for section, values in overrides.items():
        if isinstance(values, dict):
            config.setdefault(section, {}).update(values)
        else:
            config[section] = values

    if policy_level:
        config.setdefault("policy", {})["level"] = policy_level

    config_path.write_text(yaml.dump(config, default_flow_style=False))
    out.step(f"written .pilot-sec/config.yaml (template: {template})")


def _write_ignore(pilot_sec_dir: Path, out: OutputWriter) -> None:
    ignore_path = pilot_sec_dir / "ignore.yaml"
    if ignore_path.exists():
        return
    ignore_path.write_text(_DEFAULT_IGNORE)
    out.step("written .pilot-sec/ignore.yaml")


def _write_baseline_policy(pilot_sec_dir: Path, out: OutputWriter) -> None:
    policy_path = pilot_sec_dir / "policies" / "baseline.yaml"
    if policy_path.exists():
        return
    policy_path.write_text(_DEFAULT_POLICY)
    out.step("written .pilot-sec/policies/baseline.yaml")


def _suggest_hooks(project_root: Path, out: OutputWriter) -> None:
    pre_commit_config = project_root / ".pre-commit-config.yaml"
    if pre_commit_config.exists():
        out.info("  .pre-commit-config.yaml found — add pilot-sec hooks manually if desired")
    else:
        out.info("  tip: run `pilot-sec config set integrations.github.enabled true` for PR gates")
