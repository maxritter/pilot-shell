"""Pytest configuration for installer tests."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clear_claude_config_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure CLAUDE_CONFIG_DIR is unset for all installer tests.

    Prevents env var leaking from the host environment and silently
    bypassing Path.home() mocks in existing tests.
    """
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
