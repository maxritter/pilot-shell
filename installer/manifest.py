"""Upstream manifest loader, validator, and accessor.

Single source of truth for every upstream Pilot Shell installs: npm globals,
curl-pipe installers, Homebrew formulas, MCP servers, PyPI packages.

Schema lives in `installer/upstreams.yaml`. This module loads it, validates it,
and exposes typed entries to the installer steps.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

SourceType = Literal["npm", "brew", "curl", "mcp", "pypi"]
ScriptsPolicy = Literal["deny", "allow"]
PinKind = Literal["hard", "monitor"]

_SOURCE_TYPES: tuple[str, ...] = ("npm", "brew", "curl", "mcp", "pypi")
_SCRIPTS_POLICIES: tuple[str, ...] = ("deny", "allow")
_PIN_KINDS: tuple[str, ...] = ("hard", "monitor")
_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_DEFAULT_MANIFEST_PATH = Path(__file__).parent / "upstreams.yaml"


class ManifestError(ValueError):
    """Raised when the upstream manifest fails schema or cross-entry validation."""


@dataclass(frozen=True)
class UpstreamEntry:
    id: str
    name: str
    source_type: SourceType
    source_url: str
    version: str
    last_audited: str
    sha256: str | None = None
    commit: str | None = None
    scripts_policy: ScriptsPolicy = "deny"
    scripts_justification: str | None = None
    soft_pin: bool = False
    soft_pin_reason: str | None = None
    pin_kind: PinKind = "hard"
    auto_upgrade: bool = True
    # Brew-specific (only meaningful when source_type == "brew"):
    brew_formula: str | None = None  # `brew install <formula>` argument
    brew_tap: str | None = None  # required tap origin (e.g., "homebrew/core")

    def __post_init__(self) -> None:
        if not _ID_RE.match(self.id):
            raise ManifestError(
                f"invalid id {self.id!r}: must match ^[a-z][a-z0-9-]*$"
            )
        if self.source_type not in _SOURCE_TYPES:
            raise ManifestError(
                f"invalid source_type {self.source_type!r} for {self.id}: "
                f"must be one of {_SOURCE_TYPES}"
            )
        if self.scripts_policy not in _SCRIPTS_POLICIES:
            raise ManifestError(
                f"invalid scripts_policy {self.scripts_policy!r} for {self.id}"
            )
        if self.pin_kind not in _PIN_KINDS:
            raise ManifestError(
                f"invalid pin_kind {self.pin_kind!r} for {self.id}: "
                f"must be one of {_PIN_KINDS}"
            )
        if self.source_type == "brew":
            if not (self.brew_formula and self.brew_formula.strip()):
                raise ManifestError(
                    f"brew entry {self.id} requires non-empty brew_formula"
                )
            if not (self.brew_tap and self.brew_tap.strip()):
                raise ManifestError(
                    f"brew entry {self.id} requires non-empty brew_tap"
                )
        if self.source_type == "curl" and not self.sha256:
            raise ManifestError(
                f"curl entry {self.id} requires sha256 (commit field is optional metadata)"
            )
        if self.source_type == "npm" and self.version.strip().lower() == "latest":
            raise ManifestError(
                f"npm entry {self.id} cannot pin to 'latest'"
            )
        if self.scripts_policy == "allow" and not (
            self.scripts_justification and self.scripts_justification.strip()
        ):
            raise ManifestError(
                f"scripts_policy=allow on {self.id} requires non-empty scripts_justification"
            )
        if self.soft_pin and not (self.soft_pin_reason and self.soft_pin_reason.strip()):
            raise ManifestError(
                f"soft_pin=true on {self.id} requires non-empty soft_pin_reason"
            )


@dataclass(frozen=True)
class Manifest:
    version: int
    entries: list[UpstreamEntry] = field(default_factory=list)


def validate(manifest: Manifest) -> None:
    """Run cross-entry validation rules. Raises ManifestError on any violation."""
    if manifest.version != 1:
        raise ManifestError(
            f"unsupported manifest version: {manifest.version} (expected 1)"
        )
    seen: set[str] = set()
    for entry in manifest.entries:
        if entry.id in seen:
            raise ManifestError(f"duplicate entry id: {entry.id}")
        seen.add(entry.id)


def load(path: Path | None = None) -> Manifest:
    """Load + validate the upstream manifest from YAML.

    Defaults to `installer/upstreams.yaml` resolved relative to this module.
    """
    yaml_path = path or _DEFAULT_MANIFEST_PATH
    raw = yaml.safe_load(yaml_path.read_text())
    if not isinstance(raw, dict):
        raise ManifestError(f"manifest at {yaml_path} is not a YAML mapping")
    version = raw.get("version")
    if not isinstance(version, int):
        raise ManifestError("manifest is missing integer 'version' field")
    if "entries" in raw:
        raw_entries = raw["entries"]
        if raw_entries is None:
            raw_entries = []
    else:
        raw_entries = []
    if not isinstance(raw_entries, list):
        raise ManifestError("'entries' must be a list")
    entries: list[UpstreamEntry] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict):
            raise ManifestError(f"entry must be a mapping, got {type(raw_entry).__name__}")
        entries.append(UpstreamEntry(**raw_entry))
    manifest = Manifest(version=version, entries=entries)
    validate(manifest)
    return manifest


_cached: Manifest | None = None


def cached_load() -> Manifest:
    """Cached read of the default manifest. Reads YAML once per process."""
    global _cached
    if _cached is None:
        _cached = load()
    return _cached


def get(entry_id: str, *, manifest: Manifest | None = None) -> UpstreamEntry:
    """Look up an entry by id. Raises KeyError if missing."""
    m = manifest or cached_load()
    for entry in m.entries:
        if entry.id == entry_id:
            return entry
    raise KeyError(entry_id)
