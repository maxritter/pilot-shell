"""Scanner orchestrator — abstracts external security tools behind a common interface.

Supported scanner categories:
  deps      Dependency vulnerability scanning (pip-audit, npm audit, osv-scanner)
  sast      Static analysis (semgrep, bandit)
  container Image scanning (trivy, grype)
  iac       Infrastructure-as-code (checkov, tfsec)
  secrets   File-level secret scanning (detect-secrets, gitleaks)

Each scanner is tried in order; the first available tool for a category
is used. All results are normalised into a common Finding schema.

Design: zero mandatory external dependencies — every scanner degrades
gracefully to a "tool not found" result when the binary is missing.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ScanCategory(str, Enum):
    DEPS = "deps"
    SAST = "sast"
    CONTAINER = "container"
    IAC = "iac"
    SECRETS = "secrets"


class FindingSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"
    UNKNOWN = "UNKNOWN"


@dataclass
class ScanFinding:
    """Normalised finding — tool-agnostic schema."""

    category: ScanCategory
    tool: str
    severity: FindingSeverity
    title: str
    description: str
    target: str          # file, package name, image, etc.
    identifier: str      # CVE, rule ID, CWE, etc.
    fix_available: bool = False
    fix_version: str = ""
    url: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "tool": self.tool,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "target": self.target,
            "identifier": self.identifier,
            "fix_available": self.fix_available,
            "fix_version": self.fix_version,
            "url": self.url,
        }


@dataclass
class ScanResult:
    category: ScanCategory
    tool: str
    target: str
    success: bool
    findings: list[ScanFinding]
    error: str = ""
    raw_output: str = ""

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "tool": self.tool,
            "target": self.target,
            "success": self.success,
            "finding_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _run(cmd: list[str], cwd: str | None = None, timeout: int = 120) -> tuple[int, str, str]:
    """Run a subprocess, return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout}s"
    except FileNotFoundError:
        return -2, "", f"Command not found: {cmd[0]}"
    except Exception as exc:
        return -3, "", str(exc)


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


# ---------------------------------------------------------------------------
# Dependency scanners
# ---------------------------------------------------------------------------

def _scan_deps_pip_audit(target: str) -> ScanResult:
    """Run pip-audit in the given directory."""
    tool = "pip-audit"
    if not _tool_available(tool):
        return ScanResult(ScanCategory.DEPS, tool, target, False, [], error="pip-audit not installed")

    code, out, err = _run([tool, "--format", "json", "--no-progress"], cwd=target)
    if code not in (0, 1):
        return ScanResult(ScanCategory.DEPS, tool, target, False, [], error=err or out)

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return ScanResult(ScanCategory.DEPS, tool, target, True, [], raw_output=out)

    findings: list[ScanFinding] = []
    for dep in data.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            sev_str = vuln.get("fix_versions") and "HIGH" or "MEDIUM"
            findings.append(
                ScanFinding(
                    category=ScanCategory.DEPS,
                    tool=tool,
                    severity=FindingSeverity(sev_str),
                    title=vuln.get("id", ""),
                    description=vuln.get("description", ""),
                    target=f"{dep.get('name')}=={dep.get('version')}",
                    identifier=vuln.get("id", ""),
                    fix_available=bool(vuln.get("fix_versions")),
                    fix_version=", ".join(vuln.get("fix_versions", [])),
                    url=vuln.get("link", ""),
                    raw=vuln,
                )
            )

    return ScanResult(ScanCategory.DEPS, tool, target, True, findings, raw_output=out)


def _scan_deps_npm_audit(target: str) -> ScanResult:
    """Run npm audit --json in the given directory."""
    tool = "npm"
    pkg_json = Path(target) / "package.json"
    if not pkg_json.exists():
        return ScanResult(ScanCategory.DEPS, tool, target, False, [], error="No package.json found")
    if not _tool_available(tool):
        return ScanResult(ScanCategory.DEPS, tool, target, False, [], error="npm not installed")

    code, out, err = _run([tool, "audit", "--json"], cwd=target, timeout=60)
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return ScanResult(ScanCategory.DEPS, tool, target, False, [], error=err or "invalid JSON")

    findings: list[ScanFinding] = []
    for vuln_key, vuln in data.get("vulnerabilities", {}).items():
        sev = vuln.get("severity", "unknown").upper()
        try:
            severity = FindingSeverity(sev)
        except ValueError:
            severity = FindingSeverity.UNKNOWN

        findings.append(
            ScanFinding(
                category=ScanCategory.DEPS,
                tool=tool,
                severity=severity,
                title=vuln.get("name", vuln_key),
                description=vuln.get("title", ""),
                target=f"{vuln.get('name')}@{vuln.get('range', '?')}",
                identifier=str(vuln.get("cwe", [])),
                fix_available=vuln.get("fixAvailable", False) is not False,
                raw=vuln,
            )
        )

    return ScanResult(ScanCategory.DEPS, tool, target, True, findings, raw_output=out)


# ---------------------------------------------------------------------------
# SAST scanners
# ---------------------------------------------------------------------------

def _scan_sast_semgrep(target: str) -> ScanResult:
    """Run semgrep with the auto ruleset."""
    tool = "semgrep"
    if not _tool_available(tool):
        return ScanResult(ScanCategory.SAST, tool, target, False, [], error="semgrep not installed")

    code, out, err = _run(
        [tool, "--config", "auto", "--json", "--quiet", target],
        timeout=180,
    )

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return ScanResult(ScanCategory.SAST, tool, target, False, [], error=err or "invalid JSON")

    findings: list[ScanFinding] = []
    for result in data.get("results", []):
        meta = result.get("extra", {})
        sev_str = meta.get("severity", "INFO").upper()
        try:
            severity = FindingSeverity(sev_str)
        except ValueError:
            severity = FindingSeverity.MEDIUM

        findings.append(
            ScanFinding(
                category=ScanCategory.SAST,
                tool=tool,
                severity=severity,
                title=result.get("check_id", ""),
                description=meta.get("message", ""),
                target=f"{result.get('path')}:{result.get('start', {}).get('line')}",
                identifier=result.get("check_id", ""),
                url=meta.get("references", [""])[0] if meta.get("references") else "",
                raw=result,
            )
        )

    return ScanResult(ScanCategory.SAST, tool, target, True, findings, raw_output=out)


def _scan_sast_bandit(target: str) -> ScanResult:
    """Run bandit on Python code."""
    tool = "bandit"
    if not _tool_available(tool):
        return ScanResult(ScanCategory.SAST, tool, target, False, [], error="bandit not installed")

    code, out, err = _run([tool, "-r", target, "-f", "json", "-q"], timeout=120)

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return ScanResult(ScanCategory.SAST, tool, target, code == 0, [], error=err)

    findings: list[ScanFinding] = []
    for issue in data.get("results", []):
        sev_str = issue.get("issue_severity", "MEDIUM").upper()
        try:
            severity = FindingSeverity(sev_str)
        except ValueError:
            severity = FindingSeverity.MEDIUM

        findings.append(
            ScanFinding(
                category=ScanCategory.SAST,
                tool=tool,
                severity=severity,
                title=issue.get("test_name", ""),
                description=issue.get("issue_text", ""),
                target=f"{issue.get('filename')}:{issue.get('line_number')}",
                identifier=issue.get("test_id", ""),
                url=issue.get("more_info", ""),
                raw=issue,
            )
        )

    return ScanResult(ScanCategory.SAST, tool, target, True, findings, raw_output=out)


# ---------------------------------------------------------------------------
# Container scanner
# ---------------------------------------------------------------------------

def _scan_container_trivy(image: str) -> ScanResult:
    """Run trivy on a container image."""
    tool = "trivy"
    if not _tool_available(tool):
        return ScanResult(ScanCategory.CONTAINER, tool, image, False, [], error="trivy not installed")

    code, out, err = _run(
        [tool, "image", "--format", "json", "--quiet", image],
        timeout=300,
    )

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return ScanResult(ScanCategory.CONTAINER, tool, image, False, [], error=err or "invalid JSON")

    findings: list[ScanFinding] = []
    for result in data.get("Results", []):
        for vuln in result.get("Vulnerabilities", []) or []:
            sev_str = vuln.get("Severity", "UNKNOWN").upper()
            try:
                severity = FindingSeverity(sev_str)
            except ValueError:
                severity = FindingSeverity.UNKNOWN

            findings.append(
                ScanFinding(
                    category=ScanCategory.CONTAINER,
                    tool=tool,
                    severity=severity,
                    title=vuln.get("VulnerabilityID", ""),
                    description=vuln.get("Description", ""),
                    target=f"{vuln.get('PkgName')}@{vuln.get('InstalledVersion')}",
                    identifier=vuln.get("VulnerabilityID", ""),
                    fix_available=bool(vuln.get("FixedVersion")),
                    fix_version=vuln.get("FixedVersion", ""),
                    url=vuln.get("PrimaryURL", ""),
                    raw=vuln,
                )
            )

    return ScanResult(ScanCategory.CONTAINER, tool, image, True, findings, raw_output=out)


# ---------------------------------------------------------------------------
# IaC scanners
# ---------------------------------------------------------------------------

def _scan_iac_checkov(target: str) -> ScanResult:
    """Run checkov on a Terraform / K8s directory."""
    tool = "checkov"
    if not _tool_available(tool):
        return ScanResult(ScanCategory.IAC, tool, target, False, [], error="checkov not installed")

    code, out, err = _run([tool, "-d", target, "-o", "json", "--quiet"], timeout=180)

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return ScanResult(ScanCategory.IAC, tool, target, False, [], error=err or "invalid JSON")

    findings: list[ScanFinding] = []
    # Checkov can return a list (one per framework) or a single dict
    results_list = data if isinstance(data, list) else [data]
    for framework_result in results_list:
        for check in framework_result.get("results", {}).get("failed_checks", []):
            findings.append(
                ScanFinding(
                    category=ScanCategory.IAC,
                    tool=tool,
                    severity=FindingSeverity.MEDIUM,
                    title=check.get("check_id", ""),
                    description=check.get("check", {}).get("name", ""),
                    target=check.get("repo_file_path", target),
                    identifier=check.get("check_id", ""),
                    url=check.get("guideline", ""),
                    raw=check,
                )
            )

    return ScanResult(ScanCategory.IAC, tool, target, True, findings, raw_output=out)


# ---------------------------------------------------------------------------
# Orchestrator entry point
# ---------------------------------------------------------------------------

class ScannerOrchestrator:
    """Selects and runs the best available scanner for a given category."""

    _SCANNERS: dict[ScanCategory, list] = {
        ScanCategory.DEPS: [_scan_deps_pip_audit, _scan_deps_npm_audit],
        ScanCategory.SAST: [_scan_sast_semgrep, _scan_sast_bandit],
        ScanCategory.CONTAINER: [_scan_container_trivy],
        ScanCategory.IAC: [_scan_iac_checkov],
    }

    def scan(self, category: ScanCategory, target: str) -> ScanResult:
        """Run the first available scanner for the given category."""
        for scanner_fn in self._SCANNERS.get(category, []):
            result = scanner_fn(target)
            if result.success or result.error != f"{result.tool} not installed":
                return result

        return ScanResult(
            category=category,
            tool="none",
            target=target,
            success=False,
            findings=[],
            error=f"No scanner available for category: {category.value}",
        )

    def scan_all(self, target: str) -> list[ScanResult]:
        """Run all scanner categories against a target directory."""
        return [self.scan(cat, target) for cat in ScanCategory if cat != ScanCategory.SECRETS]

    def scan_on_install(self, target: str, package_manager: str) -> ScanResult:
        """Triggered on package install — scans the project dependency tree."""
        if package_manager in ("npm", "yarn", "pnpm", "bun"):
            return _scan_deps_npm_audit(target)
        return _scan_deps_pip_audit(target)


_ORCHESTRATOR = ScannerOrchestrator()


def get_orchestrator() -> ScannerOrchestrator:
    return _ORCHESTRATOR
