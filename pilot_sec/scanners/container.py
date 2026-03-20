"""Container image scanner (wraps trivy)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pilot_sec.core.findings import Finding, FindingsSummary
from pilot_sec.scanners.base import BaseScanner, ScanOptions, register

_SEVERITY_MAP = {"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low", "UNKNOWN": "medium"}


@register
class TrivyImageScanner(BaseScanner):
    name = "trivy-image"
    category = "container"
    required_tools = ["trivy"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        image = opts.extra.get("image")
        if not image:
            return summary

        cmd = ["trivy", "image", "--format", "json", image]
        rc, stdout, stderr = self._run(cmd)
        try:
            data = json.loads(stdout or "{}")
            for result in data.get("Results", []):
                for vuln in result.get("Vulnerabilities", []):
                    severity = _SEVERITY_MAP.get(vuln.get("Severity", "UNKNOWN").upper(), "medium")
                    summary.add(Finding(
                        title=f"{vuln.get('PkgName')} — {vuln.get('VulnerabilityID')}",
                        severity=severity,
                        category="container",
                        tool=self.name,
                        description=vuln.get("Description", ""),
                        rule_id=vuln.get("VulnerabilityID"),
                        remediation=f"Fixed in: {vuln.get('FixedVersion', 'unknown')}",
                        tags=["container", "image"],
                    ))
        except (json.JSONDecodeError, TypeError):
            pass
        return summary


@register
class DockerfileScanner(BaseScanner):
    name = "hadolint"
    category = "container"
    required_tools = ["hadolint"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        dockerfiles = list(opts.path.glob("**/Dockerfile*")) + list(opts.path.glob("**/dockerfile*"))
        for dockerfile in dockerfiles:
            cmd = ["hadolint", "--format", "json", str(dockerfile)]
            rc, stdout, stderr = self._run(cmd)
            try:
                results = json.loads(stdout or "[]") or []
                for r in results:
                    level = r.get("level", "warning").lower()
                    severity = "medium" if level in ("error", "warning") else "low"
                    summary.add(Finding(
                        title=f"{r.get('code')}: {r.get('message', '')}",
                        severity=severity,
                        category="container",
                        tool=self.name,
                        description=r.get("message", ""),
                        file_path=str(dockerfile),
                        line_number=r.get("line"),
                        rule_id=r.get("code"),
                        tags=["container", "dockerfile"],
                    ))
            except (json.JSONDecodeError, TypeError):
                pass
        return summary
