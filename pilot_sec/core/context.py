"""Shared execution context passed through Click commands."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SecContext:
    """Runtime context propagated to every command via Click's obj."""

    config_path: Optional[str] = None
    profile: Optional[str] = None
    output_format: str = "text"
    output_path: Optional[str] = None
    quiet: bool = False
    verbose: bool = False
    no_color: bool = False
    project_path: Optional[str] = None
    session_id: Optional[str] = None
    policy_pack: Optional[str] = None
    fail_on: Optional[str] = None
    risk_threshold: Optional[float] = None
    offline: bool = False
    log_dir: Optional[str] = None
    audit: bool = True
    dry_run: bool = False
    yes: bool = False

    # Resolved at runtime
    _project_root: Optional[Path] = field(default=None, repr=False)
    _pilot_sec_dir: Optional[Path] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        root = Path(self.project_path) if self.project_path else self._find_project_root()
        self._project_root = root
        self._pilot_sec_dir = root / ".pilot-sec"

    @property
    def project_root(self) -> Path:
        assert self._project_root is not None
        return self._project_root

    @property
    def pilot_sec_dir(self) -> Path:
        assert self._pilot_sec_dir is not None
        return self._pilot_sec_dir

    @property
    def runs_dir(self) -> Path:
        if self.log_dir:
            return Path(self.log_dir)
        return self.pilot_sec_dir / "runs"

    @property
    def reports_dir(self) -> Path:
        return self.pilot_sec_dir / "reports"

    @property
    def sessions_dir(self) -> Path:
        return self.pilot_sec_dir / "sessions"

    @property
    def policies_dir(self) -> Path:
        return self.pilot_sec_dir / "policies"

    @property
    def cache_dir(self) -> Path:
        return self.pilot_sec_dir / "cache"

    def is_initialized(self) -> bool:
        return (self.pilot_sec_dir / "config.yaml").exists()

    def get_config(self):  # type: ignore[return]
        """Load and return PilotSecConfig for this context."""
        from pilot_sec.core.config import PilotSecConfig
        if self.is_initialized():
            return PilotSecConfig.load(self.pilot_sec_dir, self.config_path)
        return PilotSecConfig.defaults()

    @staticmethod
    def _find_project_root() -> Path:
        """Walk up from cwd looking for .git or .pilot-sec, else use cwd."""
        cwd = Path(os.getcwd())
        for parent in [cwd, *cwd.parents]:
            if (parent / ".git").exists() or (parent / ".pilot-sec").exists():
                return parent
        return cwd
