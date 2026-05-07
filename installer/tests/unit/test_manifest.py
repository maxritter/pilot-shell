"""Unit tests for installer.manifest module."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from installer.manifest import (
    Manifest,
    ManifestError,
    UpstreamEntry,
    get,
    load,
    validate,
)


def _valid_npm_entry(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "probe",
        "name": "@probelabs/probe",
        "source_type": "npm",
        "source_url": "@probelabs/probe",
        "version": "1.2.3",
        "last_audited": "2026-05-07",
    }
    base.update(overrides)
    return base


def _valid_curl_entry(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "nvm-curl",
        "name": "nvm install.sh (v0.40.0)",
        "source_type": "curl",
        "source_url": "https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh",
        "version": "v0.40.0",
        "sha256": "0" * 64,
        "last_audited": "2026-05-07",
    }
    base.update(overrides)
    return base


def _valid_brew_entry(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "git",
        "name": "git",
        "source_type": "brew",
        "source_url": "https://github.com/git/git",
        "version": "2.43.0",
        "pin_kind": "monitor",
        "auto_upgrade": False,
        "brew_formula": "git",
        "brew_tap": "homebrew/core",
        "last_audited": "2026-05-07",
    }
    base.update(overrides)
    return base


class TestUpstreamEntryValidation:
    """Validation rules enforced by UpstreamEntry post-init."""

    def test_valid_npm_entry_constructs(self) -> None:
        entry = UpstreamEntry(**_valid_npm_entry())
        assert entry.id == "probe"
        assert entry.scripts_policy == "deny"
        assert entry.pin_kind == "hard"
        assert entry.auto_upgrade is True

    def test_valid_curl_entry_with_sha256(self) -> None:
        entry = UpstreamEntry(**_valid_curl_entry())
        assert entry.sha256 == "0" * 64

    def test_valid_curl_entry_with_commit_and_sha256(self) -> None:
        entry = UpstreamEntry(**_valid_curl_entry(commit="abc123"))
        assert entry.commit == "abc123"
        assert entry.sha256 == "0" * 64

    def test_id_must_be_kebab_case(self) -> None:
        with pytest.raises(ManifestError, match="id"):
            UpstreamEntry(**_valid_npm_entry(id="Bad_ID"))

    def test_id_cannot_start_with_number(self) -> None:
        with pytest.raises(ManifestError, match="id"):
            UpstreamEntry(**_valid_npm_entry(id="1bad"))

    def test_curl_requires_sha256(self) -> None:
        with pytest.raises(ManifestError, match="sha256"):
            UpstreamEntry(**_valid_curl_entry(sha256=None))

    def test_curl_with_commit_still_requires_sha256(self) -> None:
        with pytest.raises(ManifestError, match="sha256"):
            UpstreamEntry(**_valid_curl_entry(sha256=None, commit="abc123"))

    def test_npm_version_cannot_be_latest(self) -> None:
        with pytest.raises(ManifestError, match="latest"):
            UpstreamEntry(**_valid_npm_entry(version="latest"))

    def test_scripts_policy_allow_requires_justification(self) -> None:
        with pytest.raises(ManifestError, match="justification"):
            UpstreamEntry(**_valid_npm_entry(scripts_policy="allow"))

    def test_scripts_policy_allow_with_justification_ok(self) -> None:
        entry = UpstreamEntry(
            **_valid_npm_entry(
                scripts_policy="allow",
                scripts_justification="native build via node-gyp",
            )
        )
        assert entry.scripts_policy == "allow"

    def test_soft_pin_requires_reason(self) -> None:
        with pytest.raises(ManifestError, match="soft_pin_reason"):
            UpstreamEntry(**_valid_curl_entry(soft_pin=True))

    def test_soft_pin_with_reason_ok(self) -> None:
        entry = UpstreamEntry(
            **_valid_curl_entry(
                soft_pin=True,
                soft_pin_reason="vendor-managed endpoint",
            )
        )
        assert entry.soft_pin is True

    def test_invalid_source_type(self) -> None:
        with pytest.raises(ManifestError, match="source_type"):
            UpstreamEntry(**_valid_npm_entry(source_type="bogus"))

    def test_invalid_pin_kind(self) -> None:
        with pytest.raises(ManifestError, match="pin_kind"):
            UpstreamEntry(**_valid_npm_entry(pin_kind="soft"))


class TestManifestValidate:
    """Cross-entry rules enforced by validate(manifest)."""

    def test_unique_ids(self) -> None:
        a = UpstreamEntry(**_valid_npm_entry(id="probe"))
        b = UpstreamEntry(**_valid_npm_entry(id="probe", source_url="@other/probe"))
        m = Manifest(version=1, entries=[a, b])
        with pytest.raises(ManifestError, match="duplicate"):
            validate(m)

    def test_unsupported_manifest_version(self) -> None:
        m = Manifest(version=2, entries=[])
        with pytest.raises(ManifestError, match="version"):
            validate(m)

    def test_empty_manifest_is_valid(self) -> None:
        m = Manifest(version=1, entries=[])
        validate(m)


class TestLoad:
    """YAML load + validate round-trip."""

    def test_load_minimal_yaml(self, tmp_path: Path) -> None:
        yaml = tmp_path / "upstreams.yaml"
        yaml.write_text(
            "version: 1\n"
            "entries:\n"
            "  - id: nvm-curl\n"
            "    name: nvm install.sh (v0.40.0)\n"
            "    source_type: curl\n"
            "    source_url: https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh\n"
            "    version: v0.40.0\n"
            '    sha256: "' + ("0" * 64) + '"\n'
            "    last_audited: 2026-05-07\n"
        )
        m = load(path=yaml)
        assert m.version == 1
        assert len(m.entries) == 1
        assert m.entries[0].id == "nvm-curl"

    def test_load_invalid_yaml_raises(self, tmp_path: Path) -> None:
        yaml = tmp_path / "upstreams.yaml"
        yaml.write_text(
            "version: 1\n"
            "entries:\n"
            "  - id: bad-curl\n"
            "    name: bad\n"
            "    source_type: curl\n"
            "    source_url: https://example.com/x.sh\n"
            "    version: v1\n"
            "    last_audited: 2026-05-07\n"
        )
        with pytest.raises(ManifestError):
            load(path=yaml)

    def test_load_default_path_uses_package_yaml(self) -> None:
        m = load()
        assert m.version == 1
        assert any(e.id for e in m.entries)


class TestGet:
    """Lookup by id."""

    def test_get_returns_entry(self, tmp_path: Path) -> None:
        yaml = tmp_path / "upstreams.yaml"
        yaml.write_text(
            "version: 1\n"
            "entries:\n"
            "  - id: probe\n"
            "    name: probe\n"
            "    source_type: npm\n"
            "    source_url: '@probelabs/probe'\n"
            "    version: 1.2.3\n"
            "    last_audited: 2026-05-07\n"
        )
        m = load(path=yaml)
        e = get("probe", manifest=m)
        assert e.version == "1.2.3"

    def test_get_missing_raises_keyerror(self, tmp_path: Path) -> None:
        yaml = tmp_path / "upstreams.yaml"
        yaml.write_text(
            "version: 1\n"
            "entries:\n"
            "  - id: probe\n"
            "    name: probe\n"
            "    source_type: npm\n"
            "    source_url: '@probelabs/probe'\n"
            "    version: 1.2.3\n"
            "    last_audited: 2026-05-07\n"
        )
        m = load(path=yaml)
        with pytest.raises(KeyError):
            get("does-not-exist", manifest=m)


class TestBrewEntries:
    """Brew entries can omit sha256 but require brew_formula + brew_tap."""

    def test_brew_entry_no_sha256_required(self) -> None:
        entry = UpstreamEntry(**_valid_brew_entry())
        assert entry.pin_kind == "monitor"
        assert entry.sha256 is None
        assert entry.brew_formula == "git"
        assert entry.brew_tap == "homebrew/core"

    def test_brew_entry_requires_brew_formula(self) -> None:
        with pytest.raises(ManifestError, match="brew_formula"):
            UpstreamEntry(**_valid_brew_entry(brew_formula=""))

    def test_brew_entry_requires_brew_tap(self) -> None:
        with pytest.raises(ManifestError, match="brew_tap"):
            UpstreamEntry(**_valid_brew_entry(brew_tap=""))
