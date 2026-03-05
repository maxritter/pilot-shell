"""Python file checker — ruff."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from _util import check_file_length


def check_python(file_path: Path) -> tuple[int, str]:
    """Check Python file with ruff. Returns (0, reason)."""
    if "test_" in file_path.name or "spec" in file_path.name:
        return 0, ""

    length_warning = check_file_length(file_path)

    ruff_bin = shutil.which("ruff")
    if not ruff_bin:
        return 0, length_warning

    results: dict[str, tuple] = {}
    has_issues = False

    try:
        result = subprocess.run(
            [ruff_bin, "check", "--output-format=concise", str(file_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout + result.stderr
        error_pattern = re.compile(r":\d+:\d+: [A-Z]{1,3}\d+")
        error_lines = [line for line in output.splitlines() if error_pattern.search(line)]
        if error_lines:
            has_issues = True
            results["ruff"] = (len(error_lines), error_lines)
    except Exception:
        pass

    if has_issues:
        parts = []
        for tool_name, (count, _) in results.items():
            parts.append(f"{count} {tool_name}")
        reason = f"Python: {', '.join(parts)} in {file_path.name}"
        details = _format_python_issues(file_path, results)
        if details:
            reason = f"{reason}\n{details}"
        if length_warning:
            reason = f"{reason}\n{length_warning}"
        return 0, reason

    return 0, length_warning


def _format_python_issues(file_path: Path, results: dict[str, tuple]) -> str:
    """Format Python diagnostic issues as plain text."""
    lines: list[str] = []
    try:
        display_path = file_path.relative_to(Path.cwd())
    except ValueError:
        display_path = file_path
    lines.append(f"Python Issues found in: {display_path}")

    if "ruff" in results:
        count, error_lines = results["ruff"]
        plural = "issue" if count == 1 else "issues"
        lines.append(f"Ruff: {count} {plural}")
        for line in error_lines:
            parts = line.split(None, 1)
            if parts:
                code = parts[0]
                msg = parts[1] if len(parts) > 1 else ""
                msg = msg.replace("[*] ", "")
                lines.append(f"  {code}: {msg}")

    lines.append("Fix Python issues above before continuing")
    return "\n".join(lines)
