"""CI pipeline security scanner."""

from __future__ import annotations

import re
from pathlib import Path

from pilot_sec.core.findings import Finding, FindingsSummary
from pilot_sec.scanners.base import BaseScanner, ScanOptions, register

# Insecure CI patterns (regex, message, severity)
_CI_CHECKS: list[tuple[str, str, str]] = [
    (r"pull_request_target", "Dangerous trigger: pull_request_target can expose secrets to forks", "high"),
    (r"actions/checkout@v[12][^3]", "Outdated actions/checkout — use v3+", "medium"),
    (r"\$\{\{.*github\.event\..*\}\}", "Untrusted input in expression — possible injection", "high"),
    (r"curl\s+.*\|\s*(sh|bash)", "Piping curl to shell in CI is dangerous", "high"),
    (r"set\s+-x", "Shell debugging (set -x) may leak secrets in logs", "medium"),
    (r"echo\s+\$[A-Z_]*SECRET", "Echoing secret variable to logs", "high"),
    (r"echo\s+\$[A-Z_]*TOKEN", "Echoing token variable to logs", "high"),
    (r"echo\s+\$[A-Z_]*PASSWORD", "Echoing password variable to logs", "high"),
    (r"--privileged", "Privileged container mode in CI", "high"),
    (r"sudo\s+", "Sudo usage in CI pipeline", "medium"),
    (r"npm\s+install\s+--ignore-scripts\s*$", "", "info"),  # positive case
    (r"pip\s+install.*--pre\b", "Installing pre-release packages in CI", "low"),
]

_CI_FILES = [
    "**/.github/workflows/*.yml",
    "**/.github/workflows/*.yaml",
    "**/.gitlab-ci.yml",
    "**/Jenkinsfile",
    "**/.circleci/config.yml",
    "**/.travis.yml",
    "**/azure-pipelines.yml",
    "**/.bitbucket-pipelines.yml",
]


@register
class CIPipelineScanner(BaseScanner):
    name = "ci-scanner"
    category = "ci"
    required_tools = []  # Pure Python, no external tools

    def scan(self, opts: ScanOptions) -> FindingsSummary:
        summary = FindingsSummary()
        ci_files: list[Path] = []
        for pattern in _CI_FILES:
            ci_files.extend(opts.path.glob(pattern))

        if not ci_files:
            return summary

        for ci_file in ci_files:
            try:
                content = ci_file.read_text(errors="replace")
            except Exception:
                continue
            for pattern, message, severity in _CI_CHECKS:
                if not message:
                    continue  # positive / skip
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_no = content[: match.start()].count("\n") + 1
                    summary.add(Finding(
                        title=message,
                        severity=severity,
                        category="ci",
                        tool=self.name,
                        description=f"Pattern match: `{match.group()[:80]}`",
                        file_path=str(ci_file.relative_to(opts.path)),
                        line_number=line_no,
                        rule_id=f"ci-{re.sub(r'[^a-z0-9]', '-', pattern[:20].lower())}",
                        tags=["ci", "pipeline"],
                    ))
        return summary
