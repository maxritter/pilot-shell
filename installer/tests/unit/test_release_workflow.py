"""Release automation contracts for versioned runtime artifacts."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

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


def test_maintenance_release_qualifies_prepared_source_without_rewriting_it() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text()
    parsed = yaml.load(workflow, Loader=yaml.BaseLoader)
    for job in parsed["jobs"].values():
        for step in job["steps"]:
            if step.get("uses", "").startswith("actions/checkout@"):
                assert step["with"]["ref"] == "${{ inputs.source_sha }}"
                assert step["with"]["persist-credentials"] == "false"
    assert "git diff --exit-code -- pilot/scripts pilot/ui" in workflow
    assert '"console/package.json", "pilot/package.json"' in workflow
    publish = workflow[workflow.index("  publish-release:") :]
    assert "semantic-release" not in publish
    for mutation in ("git commit", "git push", "git reset", "sed -i"):
        assert mutation not in publish
    assert 'make_latest: "false"' in publish
    assert "Uploaded asset bytes differ from the qualified local set" in publish
    assert "actions/attest-build-provenance@" in publish


def test_maintenance_dispatch_binds_the_reviewed_11x_source_and_changelog() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text()
    parsed = yaml.load(workflow, Loader=yaml.BaseLoader)
    assert list(parsed["on"]) == ["workflow_dispatch"]
    assert parsed["on"]["workflow_dispatch"]["inputs"]["source_sha"]["required"] == "true"
    assert 'test "$GITHUB_REF" = refs/heads/11.x' in workflow
    assert 'test "$SOURCE_SHA" = "$GITHUB_SHA"' in workflow
    assert "args: v${{ steps.current.outputs.version }}.. --unreleased" in workflow


def test_every_release_binary_runs_through_the_shipped_wrapper_before_upload() -> None:
    """Building a Cython module is insufficient; execute its isolated wrapper."""
    workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text()

    assert workflow.count("scripts/smoke_pilot_artifact.py") == 4
    assert workflow.count("Verify installer on macOS system Bash") == 2

    prerelease_workflow = (REPO_ROOT / ".github" / "workflows" / "release-dev.yml").read_text()
    assert prerelease_workflow.count("scripts/smoke_pilot_artifact.py") == 2
    assert prerelease_workflow.count("Verify installer on macOS system Bash") == 1


def test_maintenance_release_preserves_approval_and_never_deploys_a_website() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text()
    parsed = yaml.load(workflow, Loader=yaml.BaseLoader)
    assert parsed["jobs"]["approve-release"]["environment"] == "production"
    assert "approve-release" in parsed["jobs"]["publish-release"]["needs"]
    assert "deploy-website" not in parsed["jobs"]
    assert "vercel deploy" not in workflow
    assert "vercel alias" not in workflow


@pytest.mark.parametrize(
    ("tags", "expected"),
    [
        ("v11.1.0-beta.1\nv11.0.10-rc.1\nv11.0.9\nv11.0.8", "11.0.9"),
        ("v11.0.10\nv11.0.9", "11.0.10"),
        ("v11.1.0-beta.1\nv11.0.10-rc.1", None),
        ("v12.2.0\nv11.0.9+build.1\nv11.0.9", "11.0.9"),
    ],
)
def test_previous_legacy_version_selects_a_stable_tag(tmp_path: Path, tags: str, expected: str | None) -> None:
    workflow = yaml.load((REPO_ROOT / ".github/workflows/release.yml").read_text(), Loader=yaml.BaseLoader)
    script = next(step["run"] for step in workflow["jobs"]["prepare-release"]["steps"] if step.get("id") == "current")
    git = tmp_path / "git"
    git.write_text('#!/bin/sh\n[ "$1" = tag ] || exit 95\nprintf "%s\\n" "$FIXTURE_TAGS"\n')
    git.chmod(0o755)
    output = tmp_path / "output"
    env = {
        **os.environ,
        "HOME": str(tmp_path),
        "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
        "FIXTURE_TAGS": tags,
        "GITHUB_OUTPUT": str(output),
    }
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env, capture_output=True, timeout=5)
    if expected is None:
        assert result.returncode != 0
    else:
        assert result.returncode == 0, result.stderr.decode()
        assert output.read_text().strip() == f"version={expected}"


def test_release_gates_trial_and_skill_sync_regressions_and_excludes_public_test_routes() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text()
    approval = workflow[workflow.index("  approve-release:") : workflow.index("  publish-release:")]
    assert "      - website-tests" in approval
    assert "node --test pilot/skills/setup-rules/tests/sync-agent-assets.test.mjs" in workflow
    assert "working-directory: docs/site\n        run: npm test" in workflow
    assert "**/*.test.ts" in (REPO_ROOT / ".vercelignore").read_text()


def test_legacy_readme_recipes_pin_product_source_and_export_runtime_version(tmp_path: Path) -> None:
    version = json.loads((REPO_ROOT / "console/package.json").read_text())["version"]
    readme = (REPO_ROOT / "README.md").read_text()
    blocks = [
        block
        for block in re.findall(r"```bash\n(.*?)```", readme, re.S)
        if "install.sh" in block and "uninstall.sh" not in block
    ]
    assert len(blocks) == 4
    curl = tmp_path / "curl"
    curl.write_text('#!/bin/sh\nprintf "%s\\n" "$*" > "$CURL_ARGUMENTS"\nprintf "dummy fixture bytes\\n"\n')
    curl.chmod(0o755)
    bash = tmp_path / "bash"
    bash.write_text('#!/bin/sh\nprintf "%s\\n" "$VERSION" > "$BASH_VERSION_ENV"\ncat > /dev/null\n')
    bash.chmod(0o755)
    for block in blocks:
        recipe = "\n".join(line for line in block.splitlines() if line.startswith(("export VERSION=", "curl ")))
        arguments, received_version = tmp_path / "arguments", tmp_path / "version"
        env = {
            **os.environ,
            "HOME": str(tmp_path),
            "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
            "CURL_ARGUMENTS": str(arguments),
            "BASH_VERSION_ENV": str(received_version),
        }
        env.pop("VERSION", None)
        result = subprocess.run(["/bin/bash", "-c", recipe], cwd=tmp_path, env=env, capture_output=True, timeout=5)
        assert result.returncode == 0, result.stderr.decode()
        assert (
            f"https://raw.githubusercontent.com/maxritter/qualitylayer/v{version}/install.sh" in arguments.read_text()
        )
        assert received_version.read_text().strip() == version
    uninstall = [line for line in readme.splitlines() if line.startswith("curl ") and "uninstall.sh" in line]
    assert len(uninstall) == 3
    assert all(f"/qualitylayer/v{version}/uninstall.sh" in line for line in uninstall)
    assert "/main/install.sh" not in readme
    assert "/main/uninstall.sh" not in readme
