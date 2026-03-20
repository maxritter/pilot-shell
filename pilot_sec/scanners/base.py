"""Base scanner interface and registry."""

from __future__ import annotations

import shutil
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from pilot_sec.core.findings import Finding, FindingsSummary


@dataclass
class ScanOptions:
    path: Path
    changed_only: bool = False
    since: Optional[str] = None
    baseline: Optional[str] = None
    include: Optional[str] = None
    exclude: Optional[str] = None
    severity: Optional[str] = None
    fix: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


class BaseScanner(ABC):
    name: str = "base"
    category: str = "code"
    required_tools: list[str] = []

    def is_available(self) -> bool:
        return all(shutil.which(t) is not None for t in self.required_tools)

    def check_tool(self) -> Optional[Finding]:
        """Return a Finding if a required tool is missing, else None."""
        missing = [t for t in self.required_tools if not shutil.which(t)]
        if not missing:
            return None
        tools_str = ", ".join(missing)
        return Finding(
            title=f"Scanner tool not available: {tools_str}",
            severity="info",
            category=self.category,
            tool=self.name,
            description=f"Install {tools_str} to enable {self.name} scanning.",
            tags=["setup", "missing-tool"],
        )

    @abstractmethod
    def scan(self, opts: ScanOptions) -> FindingsSummary:
        ...

    def _run(self, cmd: list[str], cwd: Optional[Path] = None, timeout: int = 300) -> tuple[int, str, str]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", f"Command timed out after {timeout}s: {' '.join(cmd)}"
        except FileNotFoundError:
            return 1, "", f"Command not found: {cmd[0]}"


# ------------------------------------------------------------------
# Registry
# ------------------------------------------------------------------

_REGISTRY: dict[str, type[BaseScanner]] = {}


def register(cls: type[BaseScanner]) -> type[BaseScanner]:
    _REGISTRY[cls.name] = cls
    return cls


def get_scanner(name: str) -> Optional[BaseScanner]:
    cls = _REGISTRY.get(name)
    return cls() if cls else None


def all_scanners() -> list[BaseScanner]:
    return [cls() for cls in _REGISTRY.values()]
