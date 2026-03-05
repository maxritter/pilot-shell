"""Tests for TypeScript/JavaScript file checker."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from _checkers.typescript import (
    TS_EXTENSIONS,
    check_typescript,
    find_project_root,
    find_tool,
)


class TestTsExtensions:
    """Verify supported file extensions."""

    def test_includes_standard_extensions(self) -> None:
        """All common TS/JS extensions are supported."""
        for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".mts"):
            assert ext in TS_EXTENSIONS


class TestFindProjectRoot:
    """Project root detection via package.json."""

    def test_finds_package_json_in_parent(self, tmp_path: Path) -> None:
        """Finds package.json in parent directory."""
        (tmp_path / "package.json").write_text("{}")
        sub_dir = tmp_path / "src"
        sub_dir.mkdir()
        ts_file = sub_dir / "app.ts"
        ts_file.write_text("")

        result = find_project_root(ts_file)

        assert result == tmp_path

    def test_returns_none_without_package_json(self, tmp_path: Path) -> None:
        """Returns None when no package.json exists."""
        ts_file = tmp_path / "app.ts"
        ts_file.write_text("")

        result = find_project_root(ts_file)

        assert result is None


class TestFindTool:
    """Tool binary discovery."""

    def test_prefers_local_node_modules(self, tmp_path: Path) -> None:
        """Local node_modules/.bin is preferred over global."""
        local_bin = tmp_path / "node_modules" / ".bin" / "eslint"
        local_bin.parent.mkdir(parents=True)
        local_bin.write_text("")

        result = find_tool("eslint", tmp_path)

        assert result == str(local_bin)

    def test_falls_back_to_which(self, tmp_path: Path) -> None:
        """Falls back to shutil.which when no local binary."""
        with patch("_checkers.typescript.shutil.which", return_value="/usr/bin/eslint"):
            result = find_tool("eslint", tmp_path)

        assert result == "/usr/bin/eslint"

    def test_returns_none_when_not_found(self, tmp_path: Path) -> None:
        """Returns None when tool is not found anywhere."""
        with patch("_checkers.typescript.shutil.which", return_value=None):
            result = find_tool("eslint", tmp_path)

        assert result is None

    def test_which_fallback_with_no_project_root(self) -> None:
        """Falls back to which when project_root is None."""
        with patch("_checkers.typescript.shutil.which", return_value="/usr/bin/tsc"):
            result = find_tool("tsc", None)

        assert result == "/usr/bin/tsc"


class TestCheckTypescriptTestFileSkip:
    """Test files should skip validation."""

    def test_test_files_skip_checks(self, tmp_path: Path) -> None:
        """Files with .test. in name skip checks."""
        ts_file = tmp_path / "app.test.ts"
        ts_file.write_text("const x: string = 123;\n")

        exit_code, reason = check_typescript(ts_file)

        assert exit_code == 0
        assert reason == ""

    def test_spec_files_skip_checks(self, tmp_path: Path) -> None:
        """Files with .spec. in name skip checks."""
        ts_file = tmp_path / "app.spec.tsx"
        ts_file.write_text("const x: string = 123;\n")

        exit_code, reason = check_typescript(ts_file)

        assert exit_code == 0
        assert reason == ""


class TestCheckTypescriptNoTools:
    """When no tools are available, skip gracefully."""

    def test_no_tools_returns_zero(self, tmp_path: Path) -> None:
        """No eslint or tsc installed returns 0."""
        ts_file = tmp_path / "app.ts"
        ts_file.write_text("const x = 1;\n")

        with (
            patch("_checkers.typescript.check_file_length", return_value=""),
            patch("_checkers.typescript.find_project_root", return_value=None),
            patch("_checkers.typescript.find_tool", return_value=None),
        ):
            exit_code, reason = check_typescript(ts_file)

        assert exit_code == 0
        assert reason == ""


class TestCheckTypescriptEslintIssues:
    """ESLint issue detection and counting."""

    def test_eslint_errors_reported_in_reason(self, tmp_path: Path) -> None:
        """ESLint errors and warnings are counted."""
        ts_file = tmp_path / "app.ts"
        ts_file.write_text("const x = 1;\n")

        eslint_json = json.dumps([{
            "filePath": str(ts_file),
            "errorCount": 2,
            "warningCount": 1,
            "messages": [
                {"line": 1, "ruleId": "no-unused-vars", "message": "x is unused", "severity": 2},
                {"line": 2, "ruleId": "no-console", "message": "no console", "severity": 2},
                {"line": 3, "ruleId": "semi", "message": "missing semi", "severity": 1},
            ],
        }])

        mock_eslint = MagicMock(returncode=1, stdout=eslint_json, stderr="")

        with (
            patch("_checkers.typescript.check_file_length", return_value=""),
            patch("_checkers.typescript.find_project_root", return_value=None),
            patch("_checkers.typescript.find_tool", side_effect=lambda name, _: f"/usr/bin/{name}" if name == "eslint" else None),
            patch("_checkers.typescript.subprocess.run", return_value=mock_eslint),
        ):
            exit_code, reason = check_typescript(ts_file)

        assert exit_code == 0
        assert "3 eslint" in reason


class TestCheckTypescriptCleanFile:
    """Clean files should pass."""

    def test_clean_file_returns_success(self, tmp_path: Path) -> None:
        """Clean TS file returns exit 0 with empty reason."""
        ts_file = tmp_path / "app.ts"
        ts_file.write_text("const x = 1;\n")

        eslint_json = json.dumps([{"filePath": str(ts_file), "errorCount": 0, "warningCount": 0, "messages": []}])

        mock_eslint = MagicMock(returncode=0, stdout=eslint_json, stderr="")

        with (
            patch("_checkers.typescript.check_file_length", return_value=""),
            patch("_checkers.typescript.find_project_root", return_value=None),
            patch("_checkers.typescript.find_tool", side_effect=lambda name, _: f"/usr/bin/{name}" if name == "eslint" else None),
            patch("_checkers.typescript.subprocess.run", return_value=mock_eslint),
        ):
            exit_code, reason = check_typescript(ts_file)

        assert exit_code == 0
        assert reason == ""


class TestCheckTypescriptCommentsPreserved:
    """Regression test: check_typescript must not strip comments from user files."""

    def test_regular_comment_survives_check(self, tmp_path: Path) -> None:
        """Regular comments are preserved after check_typescript runs."""
        ts_file = tmp_path / "app.ts"
        ts_file.write_text("const x = 1; // important doc comment\n")

        with (
            patch("_checkers.typescript.check_file_length", return_value=""),
            patch("_checkers.typescript.find_project_root", return_value=None),
            patch("_checkers.typescript.find_tool", return_value=None),
        ):
            check_typescript(ts_file)

        assert "// important doc comment" in ts_file.read_text()


class TestCheckTypescriptReadOnly:
    """Hooks must never modify user files."""

    def test_no_write_commands_invoked(self, tmp_path: Path) -> None:
        """check_typescript must not run prettier --write or any formatting command."""
        ts_file = tmp_path / "app.ts"
        ts_file.write_text("const x = 1;\n")

        eslint_json = json.dumps([{"filePath": str(ts_file), "errorCount": 0, "warningCount": 0, "messages": []}])
        mock_result = MagicMock(returncode=0, stdout=eslint_json, stderr="")
        called_commands: list[list[str]] = []

        def run_side_effect(cmd, **_kwargs):
            called_commands.append(list(cmd))
            return mock_result

        with (
            patch("_checkers.typescript.check_file_length", return_value=""),
            patch("_checkers.typescript.find_project_root", return_value=None),
            patch("_checkers.typescript.find_tool", side_effect=lambda name, _: f"/usr/bin/{name}" if name == "eslint" else None),
            patch("_checkers.typescript.subprocess.run", side_effect=run_side_effect),
        ):
            check_typescript(ts_file)

        for cmd in called_commands:
            assert "--write" not in cmd, f"Hook must not run prettier --write: {cmd}"
            assert "--fix" not in cmd, f"Hook must not run eslint --fix: {cmd}"

    def test_file_content_unchanged_after_check(self, tmp_path: Path) -> None:
        """File content must be identical before and after check_typescript."""
        ts_file = tmp_path / "app.ts"
        original = "const x = 'single quotes';\n"
        ts_file.write_text(original)

        with (
            patch("_checkers.typescript.check_file_length", return_value=""),
            patch("_checkers.typescript.find_project_root", return_value=None),
            patch("_checkers.typescript.find_tool", return_value=None),
        ):
            check_typescript(ts_file)

        assert ts_file.read_text() == original


class TestCheckTypescriptTscNotCalled:
    """Verify tsc is NOT called (removed from per-edit hooks)."""

    def test_tsc_not_invoked_even_if_available(self, tmp_path: Path) -> None:
        """Even when tsc is on PATH, it is not called."""
        ts_file = tmp_path / "app.ts"
        ts_file.write_text("const x = 1;\n")

        eslint_json = json.dumps([{"filePath": str(ts_file), "errorCount": 0, "warningCount": 0, "messages": []}])
        mock_eslint = MagicMock(returncode=0, stdout=eslint_json, stderr="")

        called_commands: list[list[str]] = []

        def run_side_effect(cmd, **_kwargs):
            called_commands.append(cmd)
            return mock_eslint

        with (
            patch("_checkers.typescript.check_file_length", return_value=""),
            patch("_checkers.typescript.find_project_root", return_value=None),
            patch("_checkers.typescript.find_tool", side_effect=lambda name, _: f"/usr/bin/{name}"),
            patch("_checkers.typescript.subprocess.run", side_effect=run_side_effect),
        ):
            check_typescript(ts_file)

        invoked_binaries = [cmd[0] for cmd in called_commands]
        assert not any("tsc" in b for b in invoked_binaries)
