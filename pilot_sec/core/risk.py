"""Risk classification and scoring."""

from __future__ import annotations

import re
from typing import Optional

from pilot_sec.core.findings import FindingsSummary

# Weight per severity in risk score calculation
SEVERITY_WEIGHTS = {
    "critical": 40,
    "high": 20,
    "medium": 8,
    "low": 2,
    "info": 0,
}

# Inherently risky command patterns
HIGH_RISK_PATTERNS = [
    r"terraform\s+apply",
    r"kubectl\s+apply",
    r"kubectl\s+delete",
    r"kubectl\s+exec",
    r"aws\s+.*--delete",
    r"gcloud\s+.*delete",
    r"rm\s+-rf",
    r"git\s+push\s+.*--force",
    r"docker\s+run",
    r"helm\s+upgrade",
    r"helm\s+install",
    r"npm\s+publish",
    r"pip\s+.*--upgrade",
]

MEDIUM_RISK_PATTERNS = [
    r"git\s+push",
    r"docker\s+build",
    r"npm\s+install",
    r"pip\s+install",
    r"curl\s+.*\|.*sh",
    r"wget\s+.*\|.*sh",
]

CRITICAL_RISK_PATTERNS = [
    r"DROP\s+TABLE",
    r"DROP\s+DATABASE",
    r"DELETE\s+FROM",
    r"TRUNCATE",
    r"rm\s+-rf\s+/",
    r"chmod\s+777",
    r"sudo\s+.*rm",
]


def classify_command(command: str) -> str:
    """Return risk level for a shell command string."""
    for pattern in CRITICAL_RISK_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "critical"
    for pattern in HIGH_RISK_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "high"
    for pattern in MEDIUM_RISK_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "medium"
    return "low"


def compute_risk_score(summary: FindingsSummary) -> float:
    """Compute 0-100 risk score from a FindingsSummary."""
    counts = summary.counts()
    raw = sum(counts.get(sev, 0) * weight for sev, weight in SEVERITY_WEIGHTS.items())
    # Sigmoid-like compression to 0-100
    score = min(100.0, raw)
    return round(score, 1)


def risk_label(score: float) -> str:
    if score >= 75:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    if score > 0:
        return "low"
    return "none"
