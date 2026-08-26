"""Release automation contracts for versioned runtime artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[3]


def _plugin_config(name: str) -> dict[str, object]:
    config = json.loads((REPO_ROOT / ".releaserc.json").read_text())
    for plugin in config["plugins"]:
        if isinstance(plugin, list) and plugin[0] == name:
            return plugin[1]
    raise AssertionError(f"missing release plugin: {name}")


def test_semantic_release_rebuilds_and_commits_versioned_runtime_bundles() -> None:
    command = str(_plugin_config("@semantic-release/exec")["prepareCmd"])
    version_update = command.index("console/package.json pilot/package.json")
    rebuild = command.index("bun run --cwd console build")
    assert version_update < rebuild

    assets = _plugin_config("@semantic-release/git")["assets"]
    assert isinstance(assets, list)
    assert "pilot/scripts/*.cjs" in assets
    assert "pilot/ui/**" in assets


def test_release_workflow_prepares_bun_and_keeps_manual_versioning_equivalent() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text()
    publish = workflow[workflow.index("  publish-release:") : workflow.index("  deploy-website:")]

    semantic = publish.index("name: Create release with semantic-release")
    assert publish.index("uses: oven-sh/setup-bun@", 0, semantic) < semantic
    assert publish.index("bun install --frozen-lockfile", 0, semantic) < semantic
    assert 'console/package.json pilot/package.json' in publish
    assert "name: Rebuild versioned runtime bundles for manual trigger" in publish
    assert "bun run build" in publish
    assert "pilot/scripts/*.cjs pilot/ui" in publish


def test_release_trigger_accepts_scoped_features_and_changelog_starts_at_current_tag() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text()
    assert "(fix|feat)(\\([^)]*\\))?!?:" in workflow
    assert "args: v${{ steps.current.outputs.version }}.. --unreleased" in workflow


def test_every_release_binary_runs_through_the_shipped_wrapper_before_upload() -> None:
    """Building a Cython module is insufficient; execute its isolated wrapper."""
    workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text()

    assert workflow.count("scripts/smoke_pilot_artifact.py") == 4
    assert workflow.count("Verify installer on macOS system Bash") == 2

    prerelease_workflow = (REPO_ROOT / ".github" / "workflows" / "release-dev.yml").read_text()
    assert prerelease_workflow.count("scripts/smoke_pilot_artifact.py") == 2
    assert prerelease_workflow.count("Verify installer on macOS system Bash") == 1
