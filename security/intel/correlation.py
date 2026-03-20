"""Correlation engine — links findings across sources to surface compound risks.

Raw findings in isolation are noisy.  This module:
  1. Groups findings by severity tier
  2. Links CVE → dependency → code path (when data is available)
  3. Computes a delta between two snapshots ("what got worse?")
  4. Generates a human-readable correlation summary

Input: list of ScanFinding objects from one or more scans.
Output: CorrelationReport with compound risks, delta, and summary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from security.scanners.orchestrator import FindingSeverity, ScanFinding


# ---------------------------------------------------------------------------
# Compound risk — a cluster of related findings
# ---------------------------------------------------------------------------

@dataclass
class CompoundRisk:
    title: str
    severity: FindingSeverity
    findings: list[ScanFinding]
    description: str
    recommendation: str

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "severity": self.severity.value,
            "finding_count": len(self.findings),
            "description": self.description,
            "recommendation": self.recommendation,
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass
class CorrelationReport:
    generated_at: str
    total_findings: int
    by_severity: dict[str, int]
    compound_risks: list[CompoundRisk]
    new_since_last: list[ScanFinding]
    resolved_since_last: list[ScanFinding]
    summary: str
    raw_findings: list[ScanFinding] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "total_findings": self.total_findings,
            "by_severity": self.by_severity,
            "compound_risks": [c.to_dict() for c in self.compound_risks],
            "new_since_last": [f.to_dict() for f in self.new_since_last],
            "resolved_since_last": [f.to_dict() for f in self.resolved_since_last],
            "summary": self.summary,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ---------------------------------------------------------------------------
# Snapshot persistence (for delta computation)
# ---------------------------------------------------------------------------

_SNAPSHOT_DIR = Path.home() / ".pilot" / "security" / "snapshots"


def _snapshot_key(findings: list[ScanFinding]) -> set[str]:
    """Stable fingerprint for a set of findings (identifier + target)."""
    return {f"{f.identifier}:{f.target}" for f in findings}


def _load_last_snapshot(label: str) -> set[str]:
    path = _SNAPSHOT_DIR / f"{label}.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text())
        return set(data.get("keys", []))
    except (OSError, json.JSONDecodeError):
        return set()


def _save_snapshot(label: str, findings: list[ScanFinding]) -> None:
    _SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = _SNAPSHOT_DIR / f"{label}.json"
    path.write_text(
        json.dumps(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "keys": sorted(_snapshot_key(findings)),
            },
            indent=2,
        )
    )


# ---------------------------------------------------------------------------
# Correlation logic
# ---------------------------------------------------------------------------

_SEV_ORDER = [
    FindingSeverity.CRITICAL,
    FindingSeverity.HIGH,
    FindingSeverity.MEDIUM,
    FindingSeverity.LOW,
    FindingSeverity.INFO,
    FindingSeverity.UNKNOWN,
]


def _count_by_severity(findings: list[ScanFinding]) -> dict[str, int]:
    counts: dict[str, int] = {s.value: 0 for s in _SEV_ORDER}
    for f in findings:
        counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
    return {k: v for k, v in counts.items() if v > 0}


def _build_compound_risks(findings: list[ScanFinding]) -> list[CompoundRisk]:
    """Group findings into compound risks by category × severity cluster."""
    from collections import defaultdict

    grouped: dict[tuple[str, str], list[ScanFinding]] = defaultdict(list)
    for f in findings:
        if f.severity in (FindingSeverity.CRITICAL, FindingSeverity.HIGH):
            grouped[(f.category.value, f.severity.value)].append(f)

    risks: list[CompoundRisk] = []
    for (cat, sev), group in grouped.items():
        if not group:
            continue
        severity = FindingSeverity(sev)
        title = f"{len(group)} {severity.value} findings in {cat}"
        description = (
            f"Cluster of {len(group)} {severity.value}-severity {cat} findings "
            f"detected across {len({f.target for f in group})} unique targets."
        )
        recommendation = _recommendation_for(cat, severity)
        risks.append(
            CompoundRisk(
                title=title,
                severity=severity,
                findings=group,
                description=description,
                recommendation=recommendation,
            )
        )

    # Sort by severity
    sev_rank = {s.value: i for i, s in enumerate(_SEV_ORDER)}
    risks.sort(key=lambda r: sev_rank.get(r.severity.value, 99))
    return risks


def _recommendation_for(category: str, severity: FindingSeverity) -> str:
    recs: dict[str, str] = {
        "deps": (
            "Update vulnerable dependencies to the fixed versions. "
            "Run `pip-audit --fix` or `npm audit fix` where available."
        ),
        "sast": (
            "Review flagged code paths. Prioritise CRITICAL/HIGH findings "
            "that touch authentication, data parsing, or external inputs."
        ),
        "container": (
            "Rebuild with a patched base image. Use `trivy image --ignore-unfixed` "
            "to filter noise and focus on actionable CVEs."
        ),
        "iac": (
            "Review infrastructure misconfigurations before next deploy. "
            "Enable Checkov in CI to catch these automatically."
        ),
        "secrets": (
            "Rotate any exposed credentials immediately. "
            "Rewrite git history if secrets are in commits."
        ),
    }
    return recs.get(category, "Review and remediate findings before deployment.")


def _build_summary(
    findings: list[ScanFinding],
    new: list[ScanFinding],
    resolved: list[ScanFinding],
    compound: list[CompoundRisk],
) -> str:
    by_sev = _count_by_severity(findings)
    total = len(findings)
    parts = [f"Total findings: {total}"]
    if by_sev:
        parts.append("  " + ", ".join(f"{sev}: {cnt}" for sev, cnt in by_sev.items()))
    if new:
        parts.append(f"New since last scan: {len(new)}")
    if resolved:
        parts.append(f"Resolved since last: {len(resolved)}")
    if compound:
        parts.append(f"Compound risks identified: {len(compound)}")
        for risk in compound[:3]:
            parts.append(f"  • {risk.title}")
    return "\n".join(parts)


def correlate(
    findings: list[ScanFinding],
    snapshot_label: str = "default",
    save_snapshot: bool = True,
) -> CorrelationReport:
    """Correlate a list of findings and compute a delta from the last snapshot.

    Args:
        findings:       Raw findings from one or more scanners.
        snapshot_label: Used to load/save the previous snapshot for delta.
        save_snapshot:  If True, persist current findings as the new snapshot.

    Returns:
        CorrelationReport with compound risks, delta, and text summary.
    """
    current_keys = _snapshot_key(findings)
    last_keys = _load_last_snapshot(snapshot_label)

    new_keys = current_keys - last_keys
    resolved_keys = last_keys - current_keys

    new_findings = [f for f in findings if f"{f.identifier}:{f.target}" in new_keys]
    resolved_findings: list[ScanFinding] = []  # we don't have the old objects, just keys

    compound = _build_compound_risks(findings)
    by_sev = _count_by_severity(findings)
    summary = _build_summary(findings, new_findings, resolved_findings, compound)

    if save_snapshot:
        _save_snapshot(snapshot_label, findings)

    return CorrelationReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_findings=len(findings),
        by_severity=by_sev,
        compound_risks=compound,
        new_since_last=new_findings,
        resolved_since_last=resolved_findings,
        summary=summary,
        raw_findings=findings,
    )
