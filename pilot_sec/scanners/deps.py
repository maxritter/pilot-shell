"""Dependency vulnerability scanner (wraps pip-audit, npm audit, trivy)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pilot_sec.core.findings import Finding, FindingsSummary
from pilot_sec.scanners.base import BaseScanner, ScanOptions, register


@register
class PipAuditScanner(BaseScanner):
    name = "pip-audit"
    category = "deps"
    required_tools = ["pip-audit"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        cmd = ["pip-audit", "--format", "json", "--progress-spinner", "off"]
        rc, stdout, stderr = self._run(cmd, cwd=opts.path)
        try:
            data = json.loads(stdout or "[]")
            for entry in data:
                for vuln in entry.get("vulns", []):
                    summary.add(Finding(
                        title=f"{entry.get('name')}@{entry.get('version')} — {vuln.get('id')}",
                        severity=_cvss_to_severity(vuln.get("fix_versions", [])),
                        category="deps",
                        tool=self.name,
                        description=vuln.get("description", ""),
                        rule_id=vuln.get("id"),
                        remediation=f"Upgrade to: {', '.join(vuln.get('fix_versions', []))}",
                    ))
        except (json.JSONDecodeError, TypeError):
            if stderr:
                summary.add(Finding(
                    title="pip-audit scan error",
                    severity="info",
                    category="deps",
                    tool=self.name,
                    description=stderr[:500],
                ))
        return summary


@register
class NpmAuditScanner(BaseScanner):
    name = "npm-audit"
    category = "deps"
    required_tools = ["npm"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        pkg_json = opts.path / "package.json"
        if not pkg_json.exists():
            return summary  # Not an npm project

        cmd = ["npm", "audit", "--json"]
        rc, stdout, stderr = self._run(cmd, cwd=opts.path)
        try:
            data = json.loads(stdout or "{}")
            vulns = data.get("vulnerabilities", {})
            for pkg_name, info in vulns.items():
                severity = info.get("severity", "medium")
                summary.add(Finding(
                    title=f"{pkg_name} — {severity} vulnerability",
                    severity=severity,
                    category="deps",
                    tool=self.name,
                    description=f"Via: {', '.join(info.get('via', []) or [])}",
                    remediation=info.get("fixAvailable", {}).get("version") if isinstance(info.get("fixAvailable"), dict) else None,
                ))
        except (json.JSONDecodeError, TypeError):
            pass
        return summary


@register
class TrivyDepsScanner(BaseScanner):
    name = "trivy-deps"
    category = "deps"
    required_tools = ["trivy"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        cmd = ["trivy", "fs", "--format", "json", "--scanners", "vuln", str(opts.path)]
        rc, stdout, stderr = self._run(cmd)
        try:
            data = json.loads(stdout or "{}")
            for result in data.get("Results", []):
                for vuln in result.get("Vulnerabilities", []):
                    severity = vuln.get("Severity", "UNKNOWN").lower()
                    summary.add(Finding(
                        title=f"{vuln.get('PkgName')}@{vuln.get('InstalledVersion')} — {vuln.get('VulnerabilityID')}",
                        severity=severity if severity in ("critical", "high", "medium", "low") else "medium",
                        category="deps",
                        tool=self.name,
                        description=vuln.get("Description", ""),
                        rule_id=vuln.get("VulnerabilityID"),
                        remediation=f"Fixed in: {vuln.get('FixedVersion', 'unknown')}",
                    ))
        except (json.JSONDecodeError, TypeError):
            pass
        return summary


def _cvss_to_severity(fix_versions: list[Any]) -> str:
    # pip-audit doesn't expose CVSS in basic mode; default to medium
    return "medium"


def run_deps_scan(path: Path, severity_filter: str | None = None) -> FindingsSummary:
    """Run all available dependency scanners and merge results."""
    from pilot_sec.scanners.base import get_scanner

    summary = FindingsSummary()
    for scanner_name in ["pip-audit", "npm-audit", "trivy-deps"]:
        scanner = get_scanner(scanner_name)
        if scanner:
            opts = ScanOptions(path=path, severity=severity_filter)
            result = scanner.scan(opts)
            summary.findings.extend(result.findings)
    return summary
