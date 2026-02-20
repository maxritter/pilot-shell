"""Tests for _util.py — model config, JSON helpers, session paths, and shared utilities."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from _util import (
    BLUE,
    CYAN,
    FILE_LENGTH_CRITICAL,
    FILE_LENGTH_WARN,
    GREEN,
    MAGENTA,
    NC,
    RED,
    YELLOW,
    _sessions_base,
    find_git_root,
    get_edited_file_from_stdin,
    get_session_cache_path,
    get_session_plan_path,
    is_waiting_for_user_input,
    read_hook_stdin,
)


class TestReadModelFromConfig:
    """Tests for _read_model_from_config()."""

    def test_returns_model_from_config(self, tmp_path: Path) -> None:
        from _util import _read_model_from_config

        config = tmp_path / ".pilot" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"model": "opus[1m]"}))

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = _read_model_from_config()

        assert result == "opus[1m]"

    def test_returns_sonnet_default_when_config_missing(self, tmp_path: Path) -> None:
        from _util import _read_model_from_config

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = _read_model_from_config()

        assert result == "sonnet"

    def test_returns_sonnet_for_unknown_model(self, tmp_path: Path) -> None:
        from _util import _read_model_from_config

        config = tmp_path / ".pilot" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"model": "gpt-4"}))

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = _read_model_from_config()

        assert result == "sonnet"


class TestGetMaxContextTokens:
    """Tests for _get_max_context_tokens()."""

    def test_returns_200k_for_sonnet(self, tmp_path: Path) -> None:
        from _util import _get_max_context_tokens

        config = tmp_path / ".pilot" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"model": "sonnet"}))

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = _get_max_context_tokens()

        assert result == 200_000

    def test_returns_1m_for_sonnet_1m(self, tmp_path: Path) -> None:
        from _util import _get_max_context_tokens

        config = tmp_path / ".pilot" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"model": "sonnet[1m]"}))

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = _get_max_context_tokens()

        assert result == 1_000_000

    def test_returns_1m_for_opus_1m(self, tmp_path: Path) -> None:
        from _util import _get_max_context_tokens

        config = tmp_path / ".pilot" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"model": "opus[1m]"}))

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = _get_max_context_tokens()

        assert result == 1_000_000

    def test_returns_200k_when_config_missing(self, tmp_path: Path) -> None:
        from _util import _get_max_context_tokens

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = _get_max_context_tokens()

        assert result == 200_000


class TestGetCompactionThresholdPct:
    """Tests for _get_compaction_threshold_pct()."""

    def test_returns_83_5_for_200k_model(self, tmp_path: Path) -> None:
        from _util import _get_compaction_threshold_pct

        config = tmp_path / ".pilot" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"model": "opus"}))

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = _get_compaction_threshold_pct()

        assert abs(result - 83.5) < 0.1

    def test_returns_96_7_for_1m_model(self, tmp_path: Path) -> None:
        from _util import _get_compaction_threshold_pct

        config = tmp_path / ".pilot" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"model": "opus[1m]"}))

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = _get_compaction_threshold_pct()

        assert abs(result - 96.7) < 0.1


class TestJsonHelpers:
    """Tests for JSON response helper functions."""

    def test_post_tool_use_block(self) -> None:
        from _util import post_tool_use_block

        result = json.loads(post_tool_use_block("Fix lint errors"))
        assert result == {"decision": "block", "reason": "Fix lint errors"}

    def test_post_tool_use_context(self) -> None:
        from _util import post_tool_use_context

        result = json.loads(post_tool_use_context("Context at 80%"))
        assert result == {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "Context at 80%",
            }
        }

    def test_pre_tool_use_deny(self) -> None:
        from _util import pre_tool_use_deny

        result = json.loads(pre_tool_use_deny("Use MCP instead"))
        assert result == {"permissionDecision": "deny", "reason": "Use MCP instead"}

    def test_pre_tool_use_context(self) -> None:
        from _util import pre_tool_use_context

        result = json.loads(pre_tool_use_context("Try vexor first"))
        assert result == {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "Try vexor first",
            }
        }

    def test_stop_block(self) -> None:
        from _util import stop_block

        result = json.loads(stop_block("Spec workflow in progress"))
        assert result == {"decision": "block", "reason": "Spec workflow in progress"}

    def test_helpers_handle_special_chars(self) -> None:
        from _util import post_tool_use_block

        msg = 'File "test.py" has\nnewlines & "quotes"'
        result = json.loads(post_tool_use_block(msg))
        assert result["reason"] == msg


class TestCheckFileLength:
    """Tests for check_file_length returning string."""

    def test_returns_empty_for_normal_file(self, tmp_path: Path) -> None:
        from _util import check_file_length

        f = tmp_path / "small.py"
        f.write_text("\n".join(f"line {i}" for i in range(100)))
        assert check_file_length(f) == ""

    def test_returns_warning_for_long_file(self, tmp_path: Path) -> None:
        from _util import check_file_length

        f = tmp_path / "growing.py"
        f.write_text("\n".join(f"line {i}" for i in range(350)))
        result = check_file_length(f)
        assert "growing.py" in result
        assert "350" in result
        assert "300" in result

    def test_returns_critical_for_very_long_file(self, tmp_path: Path) -> None:
        from _util import check_file_length

        f = tmp_path / "huge.py"
        f.write_text("\n".join(f"line {i}" for i in range(550)))
        result = check_file_length(f)
        assert "huge.py" in result
        assert "550" in result
        assert "500" in result

    def test_returns_empty_for_nonexistent_file(self, tmp_path: Path) -> None:
        from _util import check_file_length

        result = check_file_length(tmp_path / "nope.py")
        assert result == ""

    def test_no_ansi_codes_in_output(self, tmp_path: Path) -> None:
        from _util import check_file_length

        f = tmp_path / "big.py"
        f.write_text("\n".join(f"line {i}" for i in range(550)))
        result = check_file_length(f)
        assert "\033[" not in result




class TestColorConstants:
    """Color constants are defined and non-empty."""

    def test_all_colors_defined(self):
        assert RED
        assert YELLOW
        assert GREEN
        assert CYAN
        assert BLUE
        assert MAGENTA
        assert NC


class TestFileLengthConstants:
    """File length constants have expected values."""

    def test_warn_threshold(self):
        assert FILE_LENGTH_WARN == 300

    def test_critical_threshold(self):
        assert FILE_LENGTH_CRITICAL == 500




class TestSessionsBase:
    """Tests for _sessions_base()."""

    def test_returns_path_under_home(self):
        base = _sessions_base()
        assert isinstance(base, Path)
        assert base == Path.home() / ".pilot" / "sessions"


class TestGetSessionCachePath:
    """Tests for get_session_cache_path()."""

    @patch.dict("os.environ", {"PILOT_SESSION_ID": "test-session-123"})
    def test_with_session_id(self):
        path = get_session_cache_path()
        assert isinstance(path, Path)
        assert "test-session-123" in str(path)
        assert path.name == "context-cache.json"

    @patch.dict("os.environ", {}, clear=True)
    def test_defaults_to_default(self):
        path = get_session_cache_path()
        assert isinstance(path, Path)
        assert "default" in str(path)


class TestGetSessionPlanPath:
    """Tests for get_session_plan_path()."""

    @patch.dict("os.environ", {"PILOT_SESSION_ID": "test-session-456"})
    def test_returns_session_scoped_plan_path(self):
        path = get_session_plan_path()
        assert isinstance(path, Path)
        assert "test-session-456" in str(path)
        assert path.name == "active_plan.json"




class TestFindGitRoot:
    """Tests for find_git_root()."""

    @patch("subprocess.run")
    def test_returns_root_when_in_repo(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="/home/user/repo\n")
        result = find_git_root()
        assert result == Path("/home/user/repo")

    @patch("subprocess.run")
    def test_returns_none_when_not_in_repo(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        result = find_git_root()
        assert result is None

    @patch("subprocess.run", side_effect=Exception("Git not found"))
    def test_handles_exception(self, mock_run):
        result = find_git_root()
        assert result is None




class TestReadHookStdin:
    """Tests for read_hook_stdin()."""

    def test_parses_valid_json(self, monkeypatch):
        test_data = {"tool_name": "Write", "tool_input": {"file_path": "test.py"}}
        monkeypatch.setattr("sys.stdin", MagicMock(read=lambda: json.dumps(test_data)))
        result = read_hook_stdin()
        assert result == test_data

    def test_returns_empty_dict_on_invalid_json(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", MagicMock(read=lambda: "not json"))
        result = read_hook_stdin()
        assert result == {}

    def test_returns_empty_dict_on_empty_input(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", MagicMock(read=lambda: ""))
        result = read_hook_stdin()
        assert result == {}


class TestGetEditedFileFromStdin:
    """Tests for get_edited_file_from_stdin()."""

    def test_extracts_file_path(self, monkeypatch):
        test_data = {"tool_input": {"file_path": "/path/to/file.py"}}
        with patch("select.select") as mock_select:
            mock_select.return_value = ([sys.stdin], [], [])
            monkeypatch.setattr("sys.stdin", MagicMock(read=lambda: json.dumps(test_data)))
            with patch("json.load", return_value=test_data):
                result = get_edited_file_from_stdin()
                assert result == Path("/path/to/file.py")

    def test_returns_none_without_file_path(self, monkeypatch):
        test_data = {"tool_input": {}}
        with patch("select.select") as mock_select:
            mock_select.return_value = ([sys.stdin], [], [])
            with patch("json.load", return_value=test_data):
                result = get_edited_file_from_stdin()
                assert result is None

    def test_returns_none_when_stdin_empty(self, monkeypatch):
        with patch("select.select") as mock_select:
            mock_select.return_value = ([], [], [])
            result = get_edited_file_from_stdin()
            assert result is None




class TestIsWaitingForUserInput:
    """Tests for is_waiting_for_user_input()."""

    def test_returns_true_when_last_tool_is_ask_user_question(self, tmp_path):
        transcript = tmp_path / "transcript.jsonl"
        msg = {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "name": "AskUserQuestion", "input": {}}
                ]
            },
        }
        transcript.write_text(json.dumps(msg) + "\n")
        assert is_waiting_for_user_input(str(transcript)) is True

    def test_returns_false_when_last_tool_is_not_ask(self, tmp_path):
        transcript = tmp_path / "transcript.jsonl"
        msg = {
            "type": "assistant",
            "message": {
                "content": [{"type": "tool_use", "name": "Write", "input": {}}]
            },
        }
        transcript.write_text(json.dumps(msg) + "\n")
        assert is_waiting_for_user_input(str(transcript)) is False

    def test_returns_false_for_missing_file(self):
        assert is_waiting_for_user_input("/nonexistent/transcript.jsonl") is False

    def test_returns_false_for_empty_transcript(self, tmp_path):
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text("")
        assert is_waiting_for_user_input(str(transcript)) is False

    def test_uses_last_assistant_message(self, tmp_path):
        transcript = tmp_path / "transcript.jsonl"
        ask_msg = {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "name": "AskUserQuestion", "input": {}}
                ]
            },
        }
        write_msg = {
            "type": "assistant",
            "message": {
                "content": [{"type": "tool_use", "name": "Write", "input": {}}]
            },
        }
        lines = [json.dumps(ask_msg), json.dumps(write_msg)]
        transcript.write_text("\n".join(lines) + "\n")
        assert is_waiting_for_user_input(str(transcript)) is False
