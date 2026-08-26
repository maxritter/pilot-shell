#!/usr/bin/env python3
"""Execute a compiled Pilot release module through its shipped wrapper."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def _installed_module_name() -> str:
    """Return the filename used by install.sh for this Python 3.12 platform."""
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Darwin":
        return "pilot.cpython-312-darwin.so"
    if system == "Linux":
        architecture = "x86_64" if machine in {"x86_64", "amd64"} else "aarch64"
        return f"pilot.cpython-312-{architecture}-linux-gnu.so"
    raise RuntimeError(f"unsupported release smoke-test platform: {system} {machine}")


def _run(wrapper: Path, args: list[str], *, env: dict[str, str], stdin: str | None = None) -> str:
    """Run the staged wrapper and return stdout, raising with full diagnostics."""
    result = subprocess.run(
        [str(wrapper), *args],
        cwd=wrapper.parent,
        env=env,
        input=stdin,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{wrapper.name} {' '.join(args)} exited {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout


def _run_compiled_formatter(stage: Path, wrapper: Path, *, env: dict[str, str], stdin: str) -> str:
    """Exercise the real formatter without requiring a production license fixture."""
    requirements = re.findall(r"--with\s+([A-Za-z0-9._+-]+==[A-Za-z0-9.+-]+)", wrapper.read_text())
    command = ["uv", "run", "--python", "3.12", "--no-project", "--no-config"]
    for requirement in requirements:
        command.extend(["--with", requirement])
    command.extend(
        [
            "python",
            "-c",
            "import os, sys; sys.path.insert(0, os.getcwd()); "
            "from pilot import run_formatter; raise SystemExit(run_formatter())",
        ]
    )
    result = subprocess.run(
        command,
        cwd=stage,
        env=env,
        input=stdin,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"compiled statusline formatter exited {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout


def smoke(wrapper_source: Path, module_source: Path, expected_version: str) -> None:
    """Stage release assets exactly like install.sh and exercise public commands."""
    with tempfile.TemporaryDirectory(prefix="pilot-release-smoke-") as temp_dir:
        stage = Path(temp_dir)
        wrapper = stage / "pilot"
        module = stage / _installed_module_name()
        shutil.copy2(wrapper_source, wrapper)
        shutil.copy2(module_source, module)
        wrapper.chmod(0o755)
        module.chmod(0o755)

        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)
        env.pop("UV_PROJECT_ENVIRONMENT", None)
        env.update(
            {
                "HOME": str(stage / "home"),
                "PYTHONNOUSERSITE": "1",
                "UV_CACHE_DIR": str(stage / "uv-cache"),
                "UV_NO_CONFIG": "1",
            }
        )
        Path(env["HOME"]).mkdir()

        version_output = _run(wrapper, ["--version"], env=env)
        expected = f"Pilot Shell v{expected_version}"
        if expected not in version_output:
            raise RuntimeError(f"expected {expected!r}, got {version_output!r}")

        statusline_input = json.dumps(
            {
                "model": {"display_name": "release-smoke"},
                "workspace": {"current_dir": str(stage)},
                "context_window": {"used_percentage": 1},
            }
        )
        statusline_output = _run(wrapper, ["statusline"], env=env, stdin=statusline_input)
        if not statusline_output.strip():
            raise RuntimeError("pilot statusline returned no output")

        formatter_output = _run_compiled_formatter(stage, wrapper, env=env, stdin=statusline_input)
        for expected_field in ("release-smoke", "1%", "Pilot"):
            if expected_field not in formatter_output:
                raise RuntimeError(f"compiled statusline output is missing {expected_field!r}: {formatter_output!r}")


def main() -> int:
    """Parse release artifacts and run the smoke test."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--wrapper", type=Path, required=True)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()
    smoke(args.wrapper.resolve(), args.module.resolve(), args.expected_version)
    print(f"Release wrapper smoke test passed for v{args.expected_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
