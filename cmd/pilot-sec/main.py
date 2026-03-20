#!/usr/bin/env python3
"""pilot-sec — Security control plane CLI for pilot-shell.

Commands:
  classify <command>        Classify risk of a shell command
  scan deps [path]          Scan dependencies for vulnerabilities
  scan sast [path]          Run static analysis
  scan container <image>    Scan a container image
  scan iac [path]           Scan infrastructure-as-code
  scan all [path]           Run all scanners
  secrets <file>            Scan a file for secrets
  audit tail [n]            Show last N audit events
  audit path                Show audit log path
  report [path]             Generate a full security report

Usage examples:
  python cmd/pilot-sec/main.py classify "terraform apply"
  python cmd/pilot-sec/main.py scan deps ./
  python cmd/pilot-sec/main.py secrets src/config.py
  python cmd/pilot-sec/main.py audit tail 20
  python cmd/pilot-sec/main.py report ./
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add repo root to path
_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from security.risk.classifier import RiskLevel, classify
from security.policy.engine import PolicyAction, PolicyEngine
from security.secrets.detector import scan_file, scan_text
from security.audit.logger import get_log_path, tail_log
from security.scanners.orchestrator import ScanCategory, get_orchestrator
from security.intel.correlation import correlate

# ── ANSI colours ──────────────────────────────────────────────────────────────

NC = "\033[0m"
BOLD = "\033[1m"
RED = "\033[0;31m"
BOLD_RED = "\033[1;31m"
YELLOW = "\033[0;33m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
BLUE = "\033[0;34m"
DIM = "\033[2m"


def _sev_color(sev: str) -> str:
    return {
        "CRITICAL": BOLD_RED,
        "HIGH": RED,
        "MEDIUM": YELLOW,
        "LOW": GREEN,
        "INFO": CYAN,
    }.get(sev.upper(), NC)


def _print_header(text: str) -> None:
    print(f"\n{BOLD}{CYAN}{'─' * 60}{NC}")
    print(f"{BOLD}{CYAN}  {text}{NC}")
    print(f"{BOLD}{CYAN}{'─' * 60}{NC}")


def _print_finding(sev: str, title: str, detail: str = "") -> None:
    color = _sev_color(sev)
    print(f"  {color}[{sev}]{NC} {title}")
    if detail:
        print(f"         {DIM}{detail}{NC}")


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_classify(args: list[str]) -> int:
    if not args:
        print("Usage: pilot-sec classify <command>", file=sys.stderr)
        return 1

    command = " ".join(args)
    risk = classify(command)
    engine = PolicyEngine(repo_root=_REPO_ROOT)
    verdict = engine.evaluate(risk)

    _print_header(f"Risk Classification: {command[:60]}")

    color = risk.level.color()
    print(f"  Risk Level : {color}{risk.level.label()}{NC}")
    print(f"  Reason     : {risk.reason}")
    print(f"  Tags       : {', '.join(sorted(risk.tags)) or 'none'}")
    print(f"  Rule       : {DIM}{risk.matched_rule}{NC}")
    print()
    print(f"  Policy Decision : {BOLD}{verdict.action.value.upper()}{NC}")
    if verdict.block_reason:
        print(f"  Block Reason    : {RED}{verdict.block_reason}{NC}")
    if verdict.warnings:
        for w in verdict.warnings:
            print(f"  Warning         : {YELLOW}{w}{NC}")
    if verdict.gate_env_var:
        print(f"  Gate Variable   : {CYAN}{verdict.gate_env_var}{NC}")
        print(f"  Gate Details    : {verdict.gate_description}")

    return 2 if verdict.is_blocked else 0


def cmd_scan(args: list[str]) -> int:
    if not args:
        print("Usage: pilot-sec scan <deps|sast|container|iac|all> [target]", file=sys.stderr)
        return 1

    category_name = args[0].lower()
    target = args[1] if len(args) > 1 else str(Path.cwd())

    orchestrator = get_orchestrator()

    _print_header(f"Security Scan: {category_name} → {target}")

    if category_name == "all":
        results = orchestrator.scan_all(target)
    elif category_name == "container":
        from security.scanners.orchestrator import _scan_container_trivy
        results = [_scan_container_trivy(target)]
    else:
        try:
            cat = ScanCategory(category_name)
        except ValueError:
            print(f"Unknown category: {category_name}", file=sys.stderr)
            return 1
        results = [orchestrator.scan(cat, target)]

    all_findings = []
    for result in results:
        if not result.success:
            print(f"  {YELLOW}[{result.tool}]{NC} {result.error}")
            continue

        print(f"\n  {BOLD}Scanner: {result.tool}{NC} ({result.category.value})")
        if not result.findings:
            print(f"  {GREEN}✓ No findings{NC}")
            continue

        for f in result.findings:
            _print_finding(f.severity.value, f.title, f"{f.target} — {f.description[:80]}")
            all_findings.append(f)

    if all_findings:
        report = correlate(all_findings, snapshot_label="cli-scan")
        _print_header("Correlation Summary")
        print(report.summary)
        if report.compound_risks:
            print()
            for risk in report.compound_risks:
                print(f"  {BOLD}Compound risk:{NC} {risk.title}")
                print(f"    → {risk.recommendation}")

    return 1 if any(
        f.severity.value in ("CRITICAL", "HIGH") for f in all_findings
    ) else 0


def cmd_secrets(args: list[str]) -> int:
    if not args:
        print("Usage: pilot-sec secrets <file|-> [-]", file=sys.stderr)
        return 1

    source = args[0]
    _print_header(f"Secret Scan: {source}")

    if source == "-":
        text = sys.stdin.read()
        findings = scan_text(text, source="<stdin>")
    else:
        findings = scan_file(source)

    if not findings:
        print(f"  {GREEN}✓ No secrets detected{NC}")
        return 0

    for f in findings:
        _print_finding(
            f.severity.value,
            f.description,
            f"Line {f.line_number}: {f.redacted}",
        )

    return 1


def cmd_audit(args: list[str]) -> int:
    subcmd = args[0] if args else "tail"

    if subcmd == "path":
        print(get_log_path())
        return 0

    if subcmd == "tail":
        n = int(args[1]) if len(args) > 1 else 20
        events = tail_log(n)
        _print_header(f"Audit Log — last {n} events")
        if not events:
            print(f"  {DIM}No events recorded yet.{NC}")
            return 0
        for event in events:
            ts = event.get("ts", "")[:19]
            etype = event.get("event_type", "")
            tool = event.get("tool_name") or etype
            summary = event.get("summary") or event.get("command") or ""
            risk_info = ""
            if event.get("risk"):
                lvl = event["risk"].get("level", "")
                risk_info = f" [{lvl}]"
            print(f"  {DIM}{ts}{NC}  {CYAN}{tool:<20}{NC}{risk_info}  {summary[:60]}")
        return 0

    print(f"Unknown audit subcommand: {subcmd}", file=sys.stderr)
    return 1


def cmd_report(args: list[str]) -> int:
    target = args[0] if args else str(Path.cwd())
    _print_header(f"Security Report: {target}")

    orchestrator = get_orchestrator()
    results = orchestrator.scan_all(target)
    all_findings = [f for r in results if r.success for f in r.findings]

    if not all_findings:
        print(f"  {GREEN}✓ No security findings across all scanners.{NC}")
    else:
        report = correlate(all_findings, snapshot_label="report")
        print(report.summary)
        print()

        for risk in report.compound_risks:
            color = _sev_color(risk.severity.value)
            print(f"  {color}[{risk.severity.value}]{NC} {BOLD}{risk.title}{NC}")
            print(f"    {risk.description}")
            print(f"    → {risk.recommendation}")
            print()

        if report.new_since_last:
            print(f"  {RED}New since last report: {len(report.new_since_last)} findings{NC}")

    # Write JSON report to disk
    report_path = Path(target) / "security-report.json"
    try:
        if all_findings:
            report_path.write_text(report.to_json())
            print(f"\n  {DIM}Report written to: {report_path}{NC}")
    except OSError:
        pass

    return 1 if any(
        f.severity.value in ("CRITICAL", "HIGH") for f in all_findings
    ) else 0


# ── Entrypoint ────────────────────────────────────────────────────────────────

_COMMANDS = {
    "classify": cmd_classify,
    "scan": cmd_scan,
    "secrets": cmd_secrets,
    "audit": cmd_audit,
    "report": cmd_report,
}


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    command = args[0]
    handler = _COMMANDS.get(command)
    if not handler:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(f"Available: {', '.join(_COMMANDS)}", file=sys.stderr)
        return 1

    return handler(args[1:])


if __name__ == "__main__":
    sys.exit(main())
