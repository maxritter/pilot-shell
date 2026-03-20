"""Output formatting — text, JSON, SARIF, YAML, table."""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pilot_sec.core.findings import Finding, FindingsSummary, SEVERITY_COLORS


def _make_console(no_color: bool = False, quiet: bool = False) -> Console:
    if quiet:
        return Console(stderr=True, quiet=True)
    return Console(highlight=not no_color, markup=True)


class OutputWriter:
    """Handles all output for a single command invocation."""

    def __init__(
        self,
        fmt: str = "text",
        output_path: Optional[str] = None,
        no_color: bool = False,
        quiet: bool = False,
    ):
        self.fmt = fmt
        self.output_path = output_path
        self.no_color = no_color
        self.quiet = quiet
        self.console = _make_console(no_color=no_color, quiet=quiet)
        self._stderr = Console(stderr=True, markup=True)

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def print(self, *args: Any, **kwargs: Any) -> None:
        if not self.quiet:
            self.console.print(*args, **kwargs)

    def err(self, msg: str) -> None:
        self._stderr.print(f"[red]error:[/red] {msg}")

    def warn(self, msg: str) -> None:
        if not self.quiet:
            self._stderr.print(f"[yellow]warn:[/yellow] {msg}")

    def info(self, msg: str) -> None:
        if not self.quiet:
            self.console.print(f"[dim]{msg}[/dim]")

    def success(self, msg: str) -> None:
        if not self.quiet:
            self.console.print(f"[green]✓[/green] {msg}")

    def step(self, msg: str) -> None:
        if not self.quiet:
            self.console.print(f"[cyan]→[/cyan] {msg}")

    # ------------------------------------------------------------------
    # Structured result envelope
    # ------------------------------------------------------------------

    def emit_result(
        self,
        command: str,
        status: str,
        decision: str = "allow",
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        risk_score: float = 0.0,
        findings_summary: Optional[dict[str, int]] = None,
        artifacts: Optional[list[str]] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        envelope: dict[str, Any] = {
            "command": command,
            "status": status,
            "decision": decision,
            "run_id": run_id or f"run_{uuid.uuid4().hex[:12]}",
            "session_id": session_id,
            "risk_score": risk_score,
            "findings_summary": findings_summary or {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "artifacts": artifacts or [],
            **(extra or {}),
        }

        if self.output_path:
            self._write_file(envelope)
            return

        if self.fmt == "json":
            print(json.dumps(envelope, indent=2))
        elif self.fmt == "yaml":
            print(yaml.dump(envelope, default_flow_style=False), end="")
        # text/table results are handled by the individual command printers

    def _write_file(self, data: Any) -> None:
        path = Path(self.output_path)  # type: ignore[arg-type]
        path.parent.mkdir(parents=True, exist_ok=True)
        if self.fmt in ("json", "sarif"):
            path.write_text(json.dumps(data, indent=2))
        elif self.fmt == "yaml":
            path.write_text(yaml.dump(data, default_flow_style=False))
        else:
            path.write_text(str(data))
        self.success(f"Output written to {path}")

    # ------------------------------------------------------------------
    # Findings display
    # ------------------------------------------------------------------

    def print_findings(self, summary: FindingsSummary, title: str = "Findings") -> None:
        if self.fmt == "json":
            print(json.dumps([f.to_dict() for f in summary.findings], indent=2))
            return
        if self.fmt == "yaml":
            print(yaml.dump([f.to_dict() for f in summary.findings], default_flow_style=False), end="")
            return
        if self.fmt == "sarif":
            print(json.dumps(to_sarif(summary), indent=2))
            return

        counts = summary.counts()
        total = summary.total()

        if total == 0:
            self.console.print(f"[green]No findings[/green]")
            return

        # Summary line
        parts = []
        for sev in ["critical", "high", "medium", "low"]:
            n = counts.get(sev, 0)
            if n:
                color = SEVERITY_COLORS[sev]
                parts.append(f"[{color}]{n} {sev}[/{color}]")
        self.console.print(f"[bold]{title}:[/bold] {total} total — " + " · ".join(parts))

        if self.fmt == "table":
            self._print_findings_table(summary)
        else:
            for f in summary.findings:
                self._print_finding_row(f)

    def _print_findings_table(self, summary: FindingsSummary) -> None:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Severity", width=10)
        table.add_column("Category", width=12)
        table.add_column("Title")
        table.add_column("Location", width=30)
        table.add_column("Tool", width=14)
        for f in summary.findings:
            color = SEVERITY_COLORS.get(f.severity.lower(), "white")
            loc = f.file_path or ""
            if f.line_number:
                loc += f":{f.line_number}"
            table.add_row(
                Text(f.severity.upper(), style=color),
                f.category,
                f.title,
                loc,
                f.tool,
            )
        self.console.print(table)

    def _print_finding_row(self, f: Finding) -> None:
        color = SEVERITY_COLORS.get(f.severity.lower(), "white")
        loc = ""
        if f.file_path:
            loc = f"[dim]{f.file_path}"
            if f.line_number:
                loc += f":{f.line_number}"
            loc += "[/dim]"
        self.console.print(f"  [{color}]{f.severity.upper():8}[/{color}]  {f.title}  {loc}")
        if f.remediation:
            self.console.print(f"           [dim]→ {f.remediation}[/dim]")


# ------------------------------------------------------------------
# SARIF conversion
# ------------------------------------------------------------------

def to_sarif(summary: FindingsSummary) -> dict[str, Any]:
    results = []
    for f in summary.findings:
        result: dict[str, Any] = {
            "ruleId": f.rule_id or f.id,
            "level": _sarif_level(f.severity),
            "message": {"text": f.title},
        }
        if f.file_path:
            result["locations"] = [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f.file_path},
                    "region": {"startLine": f.line_number or 1},
                }
            }]
        results.append(result)
    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{"tool": {"driver": {"name": "pilot-sec", "version": "0.1.0"}}, "results": results}],
    }


def _sarif_level(sev: str) -> str:
    mapping = {"critical": "error", "high": "error", "medium": "warning", "low": "note", "info": "note"}
    return mapping.get(sev.lower(), "note")
