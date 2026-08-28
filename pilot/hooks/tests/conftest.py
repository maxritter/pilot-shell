"""Configure sys.path so hook modules are importable in tests."""

import sys
from pathlib import Path

import pytest

_hooks_dir = str(Path(__file__).resolve().parent.parent)
if _hooks_dir not in sys.path:
    sys.path.insert(0, _hooks_dir)


@pytest.fixture(autouse=True)
def isolate_session_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep hook tests independent of the agent running pytest."""
    for name in ("PILOT_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "CODEX_THREAD_ID"):
        monkeypatch.delenv(name, raising=False)
