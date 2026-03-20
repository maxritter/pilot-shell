"""SAST scanner (wraps semgrep, bandit)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pilot_sec.core.findings import Finding, FindingsSummary
from pilot_sec.scanners.base import BaseScanner, ScanOptions, register

_SEMGREP_SEVERITY = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}


@register
class SemgrepScanner(BaseScanner):
    name = "semgrep"
    category = "code"
    required_tools = ["semgrep"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        cmd = [
            "semgrep",
            "--config", "auto",
            "--json",
            "--quiet",
            str(opts.path),
        ]
        if opts.exclude:
            cmd += ["--exclude", opts.exclude]

        rc, stdout, stderr = self._run(cmd)
        try:
            data = json.loads(stdout or "{}")
            for result in data.get("results", []):
                severity = _SEMGREP_SEVERITY.get(result.get("extra", {}).get("severity", ""), "medium")
                summary.add(Finding(
                    title=result.get("check_id", "semgrep-finding"),
                    severity=severity,
                    category="code",
                    tool=self.name,
                    description=result.get("extra", {}).get("message", ""),
                    file_path=result.get("path"),
                    line_number=result.get("start", {}).get("line"),
                    rule_id=result.get("check_id"),
                    remediation=result.get("extra", {}).get("fix"),
                    tags=["sast", "semgrep"],
                ))
        except (json.JSONDecodeError, TypeError):
            pass
        return summary


@register
class BanditScanner(BaseScanner):
    name = "bandit"
    category = "code"
    required_tools = ["bandit"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        cmd = ["bandit", "-r", str(opts.path), "-f", "json", "-q"]
        rc, stdout, stderr = self._run(cmd)
        try:
            data = json.loads(stdout or "{}")
            for result in data.get("results", []):
                severity = result.get("issue_severity", "MEDIUM").lower()
                summary.add(Finding(
                    title=f"{result.get('test_id')}: {result.get('issue_text', '')}",
                    severity=severity if severity in ("critical", "high", "medium", "low") else "medium",
                    category="code",
                    tool=self.name,
                    description=result.get("issue_text", ""),
                    file_path=result.get("filename"),
                    line_number=result.get("line_number"),
                    rule_id=result.get("test_id"),
                    tags=["sast", "bandit", "python"],
                ))
        except (json.JSONDecodeError, TypeError):
            pass
        return summary


def run_code_scan(path: Path, severity_filter: Optional[str] = None) -> FindingsSummary:
    """Run all available SAST scanners and merge results."""
    from pilot_sec.scanners.base import get_scanner

    summary = FindingsSummary()
    for scanner_name in ["semgrep", "bandit"]:
        scanner = get_scanner(scanner_name)
        if scanner:
            opts = ScanOptions(path=path, severity=severity_filter)
            result = scanner.scan(opts)
            summary.findings.extend(result.findings)
    return summary
