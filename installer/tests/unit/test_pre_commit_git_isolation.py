"""Commit-hook tests must not direct fixture Git commands at the real checkout."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[3] / ".github/hooks/pre-commit"


def test_hook_child_git_isolated_from_parent_repository(tmp_path: Path) -> None:
    source = HOOK.read_text()
    start = source.index("run_isolated_tests() (")
    function = source[start : source.index("\n)\n", start) + 3]
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(HOME=str(tmp_path), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    parent = tmp_path / "parent"
    subprocess.run(["git", "init", "-q", str(parent)], env=env, check=True)
    metadata = parent / ".git"
    before = {name: (metadata / name).read_bytes() for name in ("config", "HEAD")}
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    env.update(
        GIT_DIR=str(metadata),
        GIT_COMMON_DIR=str(metadata),
        GIT_WORK_TREE=str(parent),
        GIT_INDEX_FILE=str(metadata / "private-index"),
    )
    script = (
        function
        + "\nrun_isolated_tests bash -c 'git init --bare -q remote.git && git init -q work && git -C work rev-parse --show-toplevel'\n"
    )
    result = subprocess.run(
        ["/bin/bash", "-c", script], cwd=fixture, env=env, capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).resolve() == (fixture / "work").resolve()
    assert (fixture / "remote.git/HEAD").is_file()
    assert {name: (metadata / name).read_bytes() for name in before} == before
    assert not (metadata / "private-index").exists()


@pytest.mark.parametrize("command", ["uv run pytest", "bun test"])
def test_python_and_console_suites_use_isolated_git_environment(command: str) -> None:
    lines = HOOK.read_text().splitlines()
    matching = [line.strip() for line in lines if command in line and 'HOME="$fake_home"' in line]
    assert len(matching) == 1
    assert matching[0].startswith("run_isolated_tests env ")
