"""IaC scanner (wraps checkov, tfsec, kube-score)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pilot_sec.core.findings import Finding, FindingsSummary
from pilot_sec.scanners.base import BaseScanner, ScanOptions, register

_SEVERITY_MAP = {
    "CRITICAL": "critical",
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low",
    "INFO": "info",
    "UNKNOWN": "medium",
}


@register
class CheckovScanner(BaseScanner):
    name = "checkov"
    category = "iac"
    required_tools = ["checkov"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        cmd = [
            "checkov", "--directory", str(opts.path),
            "--output", "json",
            "--quiet",
            "--compact",
        ]
        rc, stdout, stderr = self._run(cmd)
        try:
            data = json.loads(stdout or "{}")
            results = data.get("results", {})
            for check in results.get("failed_checks", []):
                summary.add(Finding(
                    title=f"{check.get('check_id')}: {check.get('check_type', '')} — {check.get('resource', '')}",
                    severity=_SEVERITY_MAP.get(check.get("severity", "MEDIUM").upper(), "medium"),
                    category="iac",
                    tool=self.name,
                    description=check.get("check_name", ""),
                    file_path=check.get("file_path"),
                    line_number=check.get("file_line_range", [None])[0],
                    rule_id=check.get("check_id"),
                    remediation=check.get("guideline"),
                    tags=["iac", check.get("check_type", "").lower()],
                ))
        except (json.JSONDecodeError, TypeError):
            pass
        return summary


@register
class TfsecScanner(BaseScanner):
    name = "tfsec"
    category = "iac"
    required_tools = ["tfsec"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        cmd = ["tfsec", str(opts.path), "--format", "json", "--no-colour"]
        rc, stdout, stderr = self._run(cmd)
        try:
            data = json.loads(stdout or "{}")
            for result in data.get("results", []):
                severity = result.get("severity", "MEDIUM").lower()
                summary.add(Finding(
                    title=f"{result.get('rule_id')}: {result.get('rule_summary', '')}",
                    severity=severity if severity in ("critical", "high", "medium", "low") else "medium",
                    category="iac",
                    tool=self.name,
                    description=result.get("description", ""),
                    file_path=result.get("location", {}).get("filename"),
                    line_number=result.get("location", {}).get("start_line"),
                    rule_id=result.get("rule_id"),
                    remediation=result.get("rule_provider"),
                    tags=["iac", "terraform"],
                ))
        except (json.JSONDecodeError, TypeError):
            pass
        return summary


@register
class KubeScoreScanner(BaseScanner):
    name = "kube-score"
    category = "iac"
    required_tools = ["kube-score"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        # Find k8s manifests
        manifests = list(opts.path.glob("**/*.yaml")) + list(opts.path.glob("**/*.yml"))
        k8s_manifests = [m for m in manifests if _looks_like_k8s(m)]
        if not k8s_manifests:
            return summary

        cmd = ["kube-score", "score", "--output-format", "json"] + [str(m) for m in k8s_manifests[:20]]
        rc, stdout, stderr = self._run(cmd)
        try:
            data = json.loads(stdout or "[]") or []
            for obj in data:
                for check in obj.get("checks", []):
                    if check.get("grade", 10) < 5:
                        summary.add(Finding(
                            title=f"k8s {obj.get('object_name')}: {check.get('check', {}).get('name', '')}",
                            severity="medium",
                            category="iac",
                            tool=self.name,
                            description="\n".join(
                                c.get("summary", "") for c in check.get("comments", [])
                            ),
                            tags=["iac", "kubernetes"],
                        ))
        except (json.JSONDecodeError, TypeError):
            pass
        return summary


def _looks_like_k8s(path: Path) -> bool:
    try:
        content = path.read_text(errors="replace")
        return "apiVersion:" in content and "kind:" in content
    except Exception:
        return False


def run_iac_scan(path: Path, severity_filter: Optional[str] = None) -> FindingsSummary:
    """Run all available IaC scanners and merge results."""
    from pilot_sec.scanners.base import get_scanner

    summary = FindingsSummary()
    for scanner_name in ["checkov", "tfsec", "kube-score"]:
        scanner = get_scanner(scanner_name)
        if scanner:
            opts = ScanOptions(path=path, severity=severity_filter)
            result = scanner.scan(opts)
            summary.findings.extend(result.findings)
    return summary
