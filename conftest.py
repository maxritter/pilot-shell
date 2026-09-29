"""Isolate test HOME before collection imports bind launcher path constants."""

import hashlib
import os
import tempfile
from pathlib import Path

import pytest

_REAL_PILOT = Path.home() / ".pilot"
_SAVED_ENV = {name: os.environ.get(name) for name in ("HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME")}
_HOME = tempfile.TemporaryDirectory(prefix="pilot-pytest-home-")
os.environ["HOME"] = _HOME.name
os.environ.pop("CLAUDE_CONFIG_DIR", None)
os.environ.pop("CODEX_HOME", None)


def _fingerprint():
    files = {}
    if not _REAL_PILOT.exists():
        return files
    for path in _REAL_PILOT.rglob("*"):
        if path.is_symlink():
            files[str(path)] = os.readlink(path)
        elif path.is_file():
            files[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


_BEFORE = _fingerprint()


@pytest.fixture(scope="session", autouse=True)
def isolated_test_home():
    """The startup environment covers subprocesses as well as imported constants."""
    yield Path(_HOME.name)
    assert _fingerprint() == _BEFORE, "Tests changed the real ~/.pilot; use temporary homes only"


def pytest_unconfigure(config):
    for name, value in _SAVED_ENV.items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value
    _HOME.cleanup()
