"""Secret detection scanner (wraps gitleaks, trufflehog)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from pilot_sec.core.findings import Finding, FindingsSummary
from pilot_sec.scanners.base import BaseScanner, ScanOptions, register


@register
class GitLeaksScanner(BaseScanner):
    name = "gitleaks"
    category = "secrets"
    required_tools = ["gitleaks"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        staged = opts.extra.get("staged", False)
        history = opts.extra.get("history", False)

        cmd = ["gitleaks", "detect", "--report-format", "json", "--report-path", "-", "--no-banner"]
        if staged:
            cmd += ["--staged"]
        if history:
            cmd += ["--log-opts", opts.extra.get("since", "HEAD")]
        cmd += ["--source", str(opts.path)]

        rc, stdout, stderr = self._run(cmd)
        if not stdout:
            return summary
        try:
            findings = json.loads(stdout) or []
            for item in findings:
                summary.add(Finding(
                    title=f"Secret detected: {item.get('RuleID', 'unknown')}",
                    severity="high",
                    category="secrets",
                    tool=self.name,
                    description=f"Match: {item.get('Match', '')[:80]}",
                    file_path=item.get("File"),
                    line_number=item.get("StartLine"),
                    rule_id=item.get("RuleID"),
                    remediation="Revoke the secret, rotate credentials, and remove from history.",
                    tags=["secret", item.get("RuleID", "unknown")],
                ))
        except (json.JSONDecodeError, TypeError):
            pass
        return summary


@register
class TruffleHogScanner(BaseScanner):
    name = "trufflehog"
    category = "secrets"
    required_tools = ["trufflehog"]

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        missing = self.check_tool()
        if missing:
            summary.add(missing)
            return summary

        cmd = ["trufflehog", "filesystem", str(opts.path), "--json", "--no-update"]
        rc, stdout, stderr = self._run(cmd)
        for line in (stdout or "").splitlines():
            try:
                item = json.loads(line)
                summary.add(Finding(
                    title=f"Secret: {item.get('DetectorName', 'unknown')}",
                    severity="high",
                    category="secrets",
                    tool=self.name,
                    description=item.get("Raw", "")[:80],
                    file_path=item.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("file"),
                    rule_id=item.get("DetectorName"),
                    remediation="Revoke and rotate the exposed credential.",
                    tags=["secret"],
                ))
            except (json.JSONDecodeError, TypeError):
                pass
        return summary


def run_secret_scan(
    path: Path,
    staged: bool = False,
    history: bool = False,
    since: Optional[str] = None,
    scan_env: bool = False,
) -> FindingsSummary:
    """Run all available secret scanners."""
    from pilot_sec.scanners.base import get_scanner

    summary = FindingsSummary()
    extra = {"staged": staged, "history": history, "since": since or ""}

    for scanner_name in ["gitleaks", "trufflehog"]:
        scanner = get_scanner(scanner_name)
        if scanner:
            opts = ScanOptions(path=path, extra=extra)
            result = scanner.scan(opts)
            summary.findings.extend(result.findings)

    if scan_env:
        _scan_env_vars(summary)

    return summary


def _scan_env_vars(summary: FindingsSummary) -> None:
    """Heuristically check environment variables for secret-like values."""
    secret_patterns = [
        "key", "secret", "token", "password", "passwd", "credential",
        "api_key", "access_key", "private_key", "auth",
    ]
    for key, value in os.environ.items():
        key_lower = key.lower()
        if any(p in key_lower for p in secret_patterns) and len(value) > 8:
            summary.add(Finding(
                title=f"Potential secret in env var: {key}",
                severity="medium",
                category="secrets",
                tool="env-scanner",
                description=f"Environment variable {key} looks like it may contain a secret.",
                tags=["secret", "env"],
            ))
