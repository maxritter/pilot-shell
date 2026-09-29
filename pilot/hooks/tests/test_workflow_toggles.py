"""Console autonomy controls are opt-in and update running hooks immediately."""

import json
from pathlib import Path

import pytest
from _lib import util


@pytest.mark.parametrize("key", ["autoPause", "runawayGuard"])
def test_toggle_is_opt_in_and_read_fresh(tmp_path: Path, monkeypatch, key: str) -> None:
    monkeypatch.setattr(util.Path, "home", lambda: tmp_path)
    config = tmp_path / ".pilot/config.json"
    assert util.read_workflow_toggle(key) is False
    config.parent.mkdir()
    config.write_text(json.dumps({"specWorkflow": {key: True}}))
    assert util.read_workflow_toggle(key) is True
    config.write_text(json.dumps({"specWorkflow": {key: False}}))
    assert util.read_workflow_toggle(key) is False
    for malformed in ("yes", 1, None, [], {}):
        config.write_text(json.dumps({"specWorkflow": {key: malformed}}))
        assert util.read_workflow_toggle(key) is False
    config.write_text("{broken")
    assert util.read_workflow_toggle(key) is False
