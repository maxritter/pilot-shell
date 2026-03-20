"""Findings data model and severity helpers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]
SEVERITY_COLORS = {
    "critical": "bold red",
    "high": "red",
    "medium": "yellow",
    "low": "blue",
    "info": "dim",
}


def severity_value(sev: str) -> int:
    """Return numeric value for severity comparison (higher = more severe)."""
    try:
        return len(SEVERITY_ORDER) - SEVERITY_ORDER.index(sev.lower())
    except ValueError:
        return 0


def meets_threshold(sev: str, threshold: str) -> bool:
    """Return True if sev is >= threshold."""
    return severity_value(sev) >= severity_value(threshold)


@dataclass
class Finding:
    title: str
    severity: str  # critical|high|medium|low|info
    category: str  # code|deps|secrets|iac|container|ci|license
    tool: str
    id: str = field(default_factory=lambda: f"finding_{uuid.uuid4().hex[:8]}")
    description: str = ""
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    rule_id: Optional[str] = None
    remediation: Optional[str] = None
    risk_score: float = 0.0
    tags: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw: Optional[dict[str, Any]] = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "category": self.category,
            "tool": self.tool,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "rule_id": self.rule_id,
            "remediation": self.remediation,
            "risk_score": self.risk_score,
            "tags": self.tags,
            "timestamp": self.timestamp,
        }


@dataclass
class FindingsSummary:
    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def counts(self) -> dict[str, int]:
        result: dict[str, int] = {s: 0 for s in SEVERITY_ORDER}
        for f in self.findings:
            key = f.severity.lower()
            if key in result:
                result[key] += 1
        return result

    def total(self) -> int:
        return len(self.findings)

    def max_severity(self) -> Optional[str]:
        for sev in SEVERITY_ORDER:
            if any(f.severity.lower() == sev for f in self.findings):
                return sev
        return None

    def exceeds_threshold(self, threshold: str) -> bool:
        return any(meets_threshold(f.severity, threshold) for f in self.findings)

    def filter_by_severity(self, min_severity: str) -> list[Finding]:
        return [f for f in self.findings if meets_threshold(f.severity, min_severity)]

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.counts().items()}
