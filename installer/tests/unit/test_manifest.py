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
        "id": "test-pkg",
        "name": "@testorg/test-pkg",
        "source_type": "npm",
        "source_url": "@testorg/test-pkg",
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
        assert entry.id == "test-pkg"
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

    def test_curl_live_version_label_requires_soft_pin(self) -> None:
        """Hard-pinning a 'live-*' / 'vendor-managed-*' label is the GH #147 bug class.

        These labels mark vendor endpoints with no version stability guarantee
        — every upstream release rewrites the script and drifts the hash. Hard
        pin + live label is structurally unsafe; require soft_pin so the
        installer logs a re-pin warning instead of bricking.
        """
        with pytest.raises(ManifestError, match="non-version-stable"):
            UpstreamEntry(**_valid_curl_entry(version="live-2026-05-18"))
        with pytest.raises(ManifestError, match="non-version-stable"):
            UpstreamEntry(**_valid_curl_entry(version="vendor-managed-2026-05-18"))

    def test_curl_live_version_label_with_soft_pin_ok(self) -> None:
        """Soft-pin is the explicit acknowledgement that drift is expected."""
        entry = UpstreamEntry(
            **_valid_curl_entry(
                version="live-2026-05-18",
                soft_pin=True,
                soft_pin_reason="vendor-managed endpoint with no version stability",
            )
        )
        assert entry.version == "live-2026-05-18"
        assert entry.soft_pin is True

    def test_curl_versioned_label_does_not_require_soft_pin(self) -> None:
        """Real versions / commit pins are immutable upstream — hard-pin is correct."""
        for ver in ("0.11.14", "v1.2.3", "commit-540da2c"):
            entry = UpstreamEntry(**_valid_curl_entry(version=ver))
            assert entry.soft_pin is False, f"version={ver!r} should not require soft_pin"

    def test_known_vendor_managed_urls_require_soft_pin_regardless_of_version(self) -> None:
        """Bypass closure: a contributor cannot mask a vendor-managed live endpoint
        with a plausible-looking version string.

        Codex reviewer flagged the version-label-only rule as bypassable — pinning
        https://bun.sh/install with version: '1.3.14' and a sha256 would slip past
        the live-/vendor-managed- prefix check. The fix is to identify the
        endpoint by its URL, not its human-chosen version label.
        """
        for unstable_url in (
            "https://bun.sh/install",
            "https://claude.ai/install.sh",
            "https://astral.sh/uv/install.sh",
        ):
            with pytest.raises(ManifestError, match="vendor-managed"):
                UpstreamEntry(
                    **_valid_curl_entry(
                        source_url=unstable_url,
                        version="1.2.3",  # plausible-looking but the URL is what matters
                    )
                )

    def test_known_vendor_managed_urls_with_soft_pin_ok(self) -> None:
        """Soft-pin escape hatch works against the URL-based rule too."""
        entry = UpstreamEntry(
            **_valid_curl_entry(
                source_url="https://bun.sh/install",
                version="1.2.3",
                soft_pin=True,
                soft_pin_reason="vendor-managed endpoint",
            )
        )
        assert entry.soft_pin is True

    def test_versioned_astral_url_not_flagged(self) -> None:
        """The fix for uv used a per-version URL — that must remain valid."""
        entry = UpstreamEntry(
            **_valid_curl_entry(
                source_url="https://astral.sh/uv/0.11.14/install.sh",
                version="0.11.14",
            )
        )
        assert entry.soft_pin is False

    def test_invalid_source_type(self) -> None:
        with pytest.raises(ManifestError, match="source_type"):
            UpstreamEntry(**_valid_npm_entry(source_type="bogus"))

    def test_invalid_pin_kind(self) -> None:
        with pytest.raises(ManifestError, match="pin_kind"):
            UpstreamEntry(**_valid_npm_entry(pin_kind="soft"))


class TestManifestValidate:
    """Cross-entry rules enforced by validate(manifest)."""

    def test_unique_ids(self) -> None:
        a = UpstreamEntry(**_valid_npm_entry(id="dup-pkg"))
        b = UpstreamEntry(**_valid_npm_entry(id="dup-pkg", source_url="@other/dup-pkg"))
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
            "  - id: test-pkg\n"
            "    name: test-pkg\n"
            "    source_type: npm\n"
            "    source_url: '@testorg/test-pkg'\n"
            "    version: 1.2.3\n"
            "    last_audited: 2026-05-07\n"
        )
        m = load(path=yaml)
        e = get("test-pkg", manifest=m)
        assert e.version == "1.2.3"

    def test_get_missing_raises_keyerror(self, tmp_path: Path) -> None:
        yaml = tmp_path / "upstreams.yaml"
        yaml.write_text(
            "version: 1\n"
            "entries:\n"
            "  - id: test-pkg\n"
            "    name: test-pkg\n"
            "    source_type: npm\n"
            "    source_url: '@testorg/test-pkg'\n"
            "    version: 1.2.3\n"
            "    last_audited: 2026-05-07\n"
        )
        m = load(path=yaml)
        with pytest.raises(KeyError):
            get("does-not-exist", manifest=m)


class TestShippedManifest:
    """Invariants on the actual installer/upstreams.yaml shipped with Pilot."""

    def test_bun_installer_safe_against_hash_drift(self) -> None:
        """bun.sh/install is a vendor-managed live endpoint with no per-version URL.

        Regression: same class as GH #147 — without soft_pin, hash will drift on
        every bun release and brick the installer.
        """
        bun = get("bun-installer", manifest=load())
        assert bun.source_type == "curl"
        is_live_endpoint = bun.version.startswith(("live-", "vendor-managed-"))
        if is_live_endpoint:
            assert bun.soft_pin is True, (
                "bun-installer pins a vendor-managed live endpoint but is hard-pinned. "
                "bun.sh/install rewrites on every release; the hash will drift. "
                "Set soft_pin: true with a reason."
            )

    def test_uv_installer_soft_pins_floating_endpoint(self) -> None:
        """uv-installer deliberately tracks the latest uv via the floating endpoint.

        Decision (2026-06-12): always install the latest uv. The floating
        https://astral.sh/uv/install.sh is rewritten on every release, so a
        hard pin against it bricks the installer (GH #147) - the entry must be
        soft-pinned (hash is a monitoring snapshot, not an execution gate).
        """
        uv = get("uv-installer", manifest=load())
        assert uv.source_type == "curl"
        assert uv.source_url == "https://astral.sh/uv/install.sh", (
            "uv-installer must point at the floating live endpoint so installs always get the latest uv."
        )
        assert uv.soft_pin is True, (
            "uv-installer pins a vendor-managed live endpoint; hard-pinning it drifts on every uv release (GH #147)."
        )
        assert uv.version.startswith("live-"), (
            f"uv-installer version {uv.version!r} must use the 'live-*' label for the vendor-managed endpoint."
        )

    def test_open_claude_design_tracks_latest_checksum_verified_release(self) -> None:
        """Pilot follows Max's latest stable Open Claude Design release without manual pin bumps."""
        design = get("open-claude-design", manifest=load())

        assert design.source_url == (
            "https://github.com/maxritter/open-claude-design/releases/latest/download/SHA256SUMS"
        )
        assert design.version == "live-github-release"
        assert design.soft_pin is True
        assert design.pin_kind == "monitor"


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
