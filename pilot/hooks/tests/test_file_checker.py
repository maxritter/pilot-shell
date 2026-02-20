"""Tests for consolidated file_checker.py."""

from __future__ import annotations

import io
import json
from unittest.mock import patch

from file_checker import main


def _make_stdin(tool_name: str, file_path: str) -> io.StringIO:
    """Create a stdin mock with hook JSON data."""
    data = {"tool_name": tool_name, "tool_input": {"file_path": file_path}}
    return io.StringIO(json.dumps(data))


def test_python_file_dispatches_to_python_checker(tmp_path):
    """Python files are handled by Python checker."""
    py_file = tmp_path / "test.py"
    py_file.write_text("print('hello')\n")

    with patch("sys.stdin", _make_stdin("Edit", str(py_file))):
        with patch("file_checker.check_python") as mock_check:
            mock_check.return_value = (0, "")
            result = main()

            mock_check.assert_called_once_with(py_file)
            assert result == 0


def test_typescript_file_dispatches_to_typescript_checker(tmp_path):
    """TypeScript files are handled by TypeScript checker."""
    ts_file = tmp_path / "test.ts"
    ts_file.write_text("const x = 1;\n")

    with patch("sys.stdin", _make_stdin("Edit", str(ts_file))):
        with patch("file_checker.check_typescript") as mock_check:
            mock_check.return_value = (0, "")
            result = main()

            mock_check.assert_called_once_with(ts_file)
            assert result == 0


def test_go_file_dispatches_to_go_checker(tmp_path):
    """Go files are handled by Go checker."""
    go_file = tmp_path / "test.go"
    go_file.write_text("package main\n")

    with patch("sys.stdin", _make_stdin("Edit", str(go_file))):
        with patch("file_checker.check_go") as mock_check:
            mock_check.return_value = (0, "")
            result = main()

            mock_check.assert_called_once_with(go_file)
            assert result == 0


def test_unsupported_file_returns_zero(tmp_path):
    """Unsupported files return 0."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Heading\n")

    with patch("sys.stdin", _make_stdin("Edit", str(md_file))):
        result = main()
        assert result == 0


def test_nonexistent_file_returns_zero():
    """Nonexistent files return 0."""
    with patch("sys.stdin", _make_stdin("Edit", "/nonexistent/file.py")):
        result = main()
        assert result == 0


class TestContextOutput:
    """Test additionalContext output on stdout."""

    def test_context_output_when_issues_found(self, tmp_path, capsys):
        """Should print additionalContext JSON when checker finds issues."""
        py_file = tmp_path / "app.py"
        py_file.write_text("x = 1\n")

        with patch("sys.stdin", _make_stdin("Edit", str(py_file))):
            with patch("file_checker.check_python") as mock_check:
                mock_check.return_value = (2, "Python: 3 ruff issues in app.py")
                main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "hookSpecificOutput" in output
        assert output["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        assert "Python" in output["hookSpecificOutput"]["additionalContext"]

    def test_no_output_when_clean(self, tmp_path, capsys):
        """Should print nothing when checks pass."""
        py_file = tmp_path / "app.py"
        py_file.write_text("x = 1\n")

        with patch("sys.stdin", _make_stdin("Edit", str(py_file))):
            with patch("file_checker.check_python") as mock_check:
                mock_check.return_value = (0, "")
                with patch("file_checker._tdd_check", return_value=""):
                    main()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_no_output_for_unsupported_files(self, tmp_path, capsys):
        """Should not print anything for unsupported file types."""
        md_file = tmp_path / "readme.md"
        md_file.write_text("# Hello\n")

        with patch("sys.stdin", _make_stdin("Edit", str(md_file))):
            main()

        captured = capsys.readouterr()
        assert captured.out == ""
