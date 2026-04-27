"""Tests for scripts.runner — parsers, validators, prepare_config_dir, and mocked execute_run/grader."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from scripts.runner import (
    REQUIRED_RESULT_FIELDS,
    SANDBOX_PLACEHOLDER,
    RunConfig,
    _make_subprocess_env,
    _run_grader,
    _safe_prefixes,
    _validate_target_path,
    _write_failed_marker,
    execute_run,
    extract_final_result_event,
    parse_result_event,
    prepare_config_dir,
    substitute_sandbox,
    validate_prompt_isolation,
)
from scripts.utils import (
    ExecuteFailure,
    ExecuteSuccess,
    GraderFailure,
    GraderSuccess,
    ResultEvent,
    TargetConfig,
)

FIXTURES = Path(__file__).parent / "fixtures"


# ----------------------------------------------------------------------------
# parse_result_event / extract_final_result_event
# ----------------------------------------------------------------------------


class TestParseResultEvent:
    def test_parses_complete_event(self) -> None:
        event: ResultEvent = {
            "type": "result",
            "duration_ms": 1500,
            "duration_api_ms": 1200,
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20,
                "cache_creation_input_tokens": 5,
                "cache_read_input_tokens": 3,
            },
            "result": "hi",
            "is_error": False,
            "session_id": "abc",
            "stop_reason": "end_turn",
            "total_cost_usd": 0.001,
        }
        parsed = parse_result_event(event)
        assert parsed["duration_ms"] == 1500
        assert parsed["total_tokens"] == 38  # 10 + 20 + 5 + 3
        assert parsed["result_text"] == "hi"
        assert parsed["session_id"] == "abc"

    def test_rejects_non_result_event(self) -> None:
        with pytest.raises(ValueError, match="not a result event"):
            _ = parse_result_event({"type": "assistant"})

    def test_rejects_missing_required_fields(self) -> None:
        with pytest.raises(ValueError, match="missing required fields"):
            _ = parse_result_event({"type": "result"})

    def test_rejects_missing_duration_ms(self) -> None:
        # usage is present but duration_ms missing
        with pytest.raises(ValueError, match="missing required fields"):
            _ = parse_result_event({"type": "result", "usage": {}})

    def test_required_fields_constant(self) -> None:
        assert "duration_ms" in REQUIRED_RESULT_FIELDS
        assert "usage" in REQUIRED_RESULT_FIELDS


class TestExtractFinalResultEvent:
    def test_real_fixture(self) -> None:
        fixture = FIXTURES / "sample-stream-json.jsonl"
        lines = fixture.read_text().splitlines()
        result = extract_final_result_event(lines)
        assert result is not None
        assert result.get("type") == "result"
        assert result.get("duration_ms") == 3588

    def test_returns_none_when_no_result(self) -> None:
        lines = [
            json.dumps({"type": "system"}),
            json.dumps({"type": "assistant"}),
        ]
        assert extract_final_result_event(lines) is None

    def test_picks_last_result_event(self) -> None:
        lines = [
            json.dumps({"type": "result", "duration_ms": 100, "usage": {}}),
            json.dumps({"type": "result", "duration_ms": 200, "usage": {}}),
        ]
        result = extract_final_result_event(lines)
        assert result is not None
        assert result.get("duration_ms") == 200

    def test_skips_malformed_lines(self) -> None:
        lines = [
            "not json",
            json.dumps({"type": "result", "duration_ms": 50, "usage": {}}),
            "",
        ]
        result = extract_final_result_event(lines)
        assert result is not None
        assert result.get("duration_ms") == 50


# ----------------------------------------------------------------------------
# _safe_prefixes / _validate_target_path
# ----------------------------------------------------------------------------


class TestSafePrefixes:
    def test_includes_home_and_tmp(self) -> None:
        prefixes = _safe_prefixes()
        assert any(str(p) == str(Path.home().resolve()) for p in prefixes)
        assert any(str(p) == str(Path("/tmp").resolve()) for p in prefixes)


class TestValidateTargetPath:
    def test_accepts_home(self) -> None:
        _validate_target_path(Path.home())

    def test_accepts_tmp(self) -> None:
        _validate_target_path(Path("/tmp"))

    def test_rejects_root_etc(self) -> None:
        with pytest.raises(ValueError, match="resolves outside approved locations"):
            _validate_target_path(Path("/etc"))


# ----------------------------------------------------------------------------
# _make_subprocess_env
# ----------------------------------------------------------------------------


class TestMakeSubprocessEnv:
    def test_strips_claudecode(self) -> None:
        with patch.dict("os.environ", {"CLAUDECODE": "1", "HOME": "/h"}):
            env = _make_subprocess_env()
            assert "CLAUDECODE" not in env
            assert env.get("HOME") == "/h"


# ----------------------------------------------------------------------------
# prepare_config_dir
# ----------------------------------------------------------------------------


class TestPrepareConfigDir:
    def test_without_config_creates_empty_claude_dir(self, tmp_path: Path) -> None:
        target: TargetConfig = {"type": "skill", "path": "/x"}
        result = prepare_config_dir(target, "without", tmp_path)
        assert result == tmp_path / "without"
        assert (result / ".claude").is_dir()
        # No skill should be installed
        assert not (result / ".claude" / "skills").exists()

    def test_with_config_copies_skill(self, tmp_path: Path) -> None:
        # Source skill
        skill_src = tmp_path / "src" / "my-skill"
        skill_src.mkdir(parents=True)
        _ = (skill_src / "SKILL.md").write_text("---\nname: my-skill\n---\n")
        target: TargetConfig = {"type": "skill", "path": str(skill_src), "name": "my-skill"}
        dest_root = tmp_path / "dest"
        dest_root.mkdir()
        result = prepare_config_dir(target, "with", dest_root)
        installed = result / ".claude" / "skills" / "my-skill" / "SKILL.md"
        assert installed.exists()

    def test_with_rules_target_copies_md_files(self, tmp_path: Path) -> None:
        rules_src = tmp_path / "src" / "rules"
        rules_src.mkdir(parents=True)
        _ = (rules_src / "a.md").write_text("rule A")
        _ = (rules_src / "b.md").write_text("rule B")
        target: TargetConfig = {"type": "rules", "path": str(rules_src), "name": "rules"}
        dest_root = tmp_path / "dest"
        dest_root.mkdir()
        result = prepare_config_dir(target, "with", dest_root)
        assert (result / ".claude" / "rules" / "a.md").exists()
        assert (result / ".claude" / "rules" / "b.md").exists()

    def test_raises_when_path_missing(self, tmp_path: Path) -> None:
        target: TargetConfig = {"type": "skill"}
        with pytest.raises(ValueError, match="target.path is required"):
            _ = prepare_config_dir(target, "with", tmp_path)

    def test_with_rules_target_strips_paths_frontmatter(self, tmp_path: Path) -> None:
        """A rule whose frontmatter has `paths: [...]` should be installed
        WITHOUT that field so the rule loads unconditionally during the run.
        Otherwise the rule stays dormant and delta collapses to zero."""
        rules_src = tmp_path / "src" / "rules"
        rules_src.mkdir(parents=True)
        original = (
            "---\n"
            "name: standards-python\n"
            'paths:\n  - "**/*.py"\n'
            "description: Python rules\n"
            "---\n"
            "# Python content\n"
        )
        _ = (rules_src / "standards-python.md").write_text(original)
        target: TargetConfig = {
            "type": "rules",
            "path": str(rules_src),
            "name": "standards-python",
        }
        dest_root = tmp_path / "dest"
        dest_root.mkdir()
        result = prepare_config_dir(target, "with", dest_root)
        installed = (result / ".claude" / "rules" / "standards-python.md").read_text()
        assert "paths:" not in installed
        assert "**/*.py" not in installed
        # Other frontmatter fields preserved.
        assert "name: standards-python" in installed
        assert "description: Python rules" in installed
        assert "# Python content" in installed
        # SOURCE file must be untouched.
        assert (rules_src / "standards-python.md").read_text() == original

    def test_with_rules_single_file_strips_paths(self, tmp_path: Path) -> None:
        """Single-file rules target also gets its `paths:` stripped."""
        rule_src = tmp_path / "rule.md"
        original = "---\npaths:\n  - foo\nname: r\n---\nbody\n"
        _ = rule_src.write_text(original)
        target: TargetConfig = {"type": "rules", "path": str(rule_src), "name": "rule"}
        dest_root = tmp_path / "dest"
        dest_root.mkdir()
        result = prepare_config_dir(target, "with", dest_root)
        installed = (result / ".claude" / "rules" / "rule.md").read_text()
        assert "paths:" not in installed
        assert "name: r" in installed
        assert rule_src.read_text() == original

    def test_with_skill_target_strips_skill_md_paths(self, tmp_path: Path) -> None:
        """SKILL.md frontmatter with conditional fields gets stripped on install."""
        skill_src = tmp_path / "src" / "my-skill"
        skill_src.mkdir(parents=True)
        original = (
            "---\n"
            "name: my-skill\n"
            "description: x\n"
            "paths:\n  - src/**\n"
            "---\n"
            "# body\n"
        )
        _ = (skill_src / "SKILL.md").write_text(original)
        target: TargetConfig = {"type": "skill", "path": str(skill_src), "name": "my-skill"}
        dest_root = tmp_path / "dest"
        dest_root.mkdir()
        result = prepare_config_dir(target, "with", dest_root)
        installed = (result / ".claude" / "skills" / "my-skill" / "SKILL.md").read_text()
        assert "paths:" not in installed
        assert "src/**" not in installed
        assert "name: my-skill" in installed
        assert (skill_src / "SKILL.md").read_text() == original

    def test_with_rules_no_paths_field_unchanged(self, tmp_path: Path) -> None:
        """When a rule has no conditional fields, the install is byte-identical
        to the source — the strip path is purely additive."""
        rule_src = tmp_path / "plain.md"
        original = "---\nname: plain\n---\nhello\n"
        _ = rule_src.write_text(original)
        target: TargetConfig = {"type": "rules", "path": str(rule_src), "name": "plain"}
        dest_root = tmp_path / "dest"
        dest_root.mkdir()
        result = prepare_config_dir(target, "with", dest_root)
        installed = (result / ".claude" / "rules" / "plain.md").read_text()
        assert installed == original


# ----------------------------------------------------------------------------
# _write_failed_marker
# ----------------------------------------------------------------------------


class TestWriteFailedMarker:
    def test_writes_failed_json(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run"
        _write_failed_marker(run_dir, reason="timeout", details="after 600s")
        marker = run_dir / "failed.json"
        assert marker.exists()
        data = json.loads(marker.read_text())
        assert data["failed"] is True
        assert data["reason"] == "timeout"
        assert data["details"] == "after 600s"


# ----------------------------------------------------------------------------
# execute_run (mocked subprocess)
# ----------------------------------------------------------------------------


def _success_stream(duration_ms: int = 100, total_tokens: int = 5) -> str:
    """Build a minimal stream-json transcript with one result event."""
    events = [
        {"type": "system", "subtype": "init", "session_id": "s"},
        {
            "type": "result",
            "duration_ms": duration_ms,
            "usage": {
                "input_tokens": total_tokens,
                "output_tokens": 0,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
            "result": "ok",
            "is_error": False,
            "session_id": "s",
        },
    ]
    return "\n".join(json.dumps(e) for e in events) + "\n"


class TestExecuteRun:
    def _run(
        self, tmp_path: Path, *, stdout: str, stderr: str = "", returncode: int = 0
    ):
        config_dir = tmp_path / "cfg"
        run_dir = tmp_path / "out"
        config_dir.mkdir()
        completed = MagicMock()
        completed.stdout = stdout
        completed.stderr = stderr
        completed.returncode = returncode
        with patch("scripts.runner.subprocess.run", return_value=completed):
            return execute_run(
                prompt="hi",
                config_dir=config_dir,
                run_dir=run_dir,
                model="m",
                timeout=10,
            )

    def test_success_returns_executesuccess_with_metrics(self, tmp_path: Path) -> None:
        result = self._run(tmp_path, stdout=_success_stream(duration_ms=750, total_tokens=42))
        assert isinstance(result, ExecuteSuccess)
        assert result.duration_ms == 750
        assert result.total_tokens == 42
        assert (tmp_path / "out" / "outputs" / "transcript.jsonl").exists()
        assert (tmp_path / "out" / "timing.json").exists()

    def test_no_result_event_returns_failure(self, tmp_path: Path) -> None:
        result = self._run(tmp_path, stdout=json.dumps({"type": "system"}) + "\n")
        assert isinstance(result, ExecuteFailure)
        assert result.reason == "no-result-event"
        assert (tmp_path / "out" / "failed.json").exists()

    def test_timeout_returns_failure(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "cfg"
        run_dir = tmp_path / "out"
        config_dir.mkdir()
        with patch(
            "scripts.runner.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=1),
        ):
            result = execute_run(
                prompt="hi",
                config_dir=config_dir,
                run_dir=run_dir,
                model="m",
                timeout=1,
            )
        assert isinstance(result, ExecuteFailure)
        assert result.reason == "timeout"

    def test_missing_cli_returns_failure(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "cfg"
        run_dir = tmp_path / "out"
        config_dir.mkdir()
        with patch("scripts.runner.subprocess.run", side_effect=FileNotFoundError()):
            result = execute_run(
                prompt="hi",
                config_dir=config_dir,
                run_dir=run_dir,
                model="m",
                timeout=1,
            )
        assert isinstance(result, ExecuteFailure)
        assert result.reason == "claude-cli-not-found"

    def test_appends_skip_permissions_flag(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "cfg"
        run_dir = tmp_path / "out"
        config_dir.mkdir()
        completed = MagicMock(stdout=_success_stream(), stderr="", returncode=0)
        with patch("scripts.runner.subprocess.run", return_value=completed) as mock_run:
            _ = execute_run(
                prompt="x",
                config_dir=config_dir,
                run_dir=run_dir,
                model="m",
                timeout=1,
                skip_permissions=True,
            )
        cmd_arg = mock_run.call_args.args[0]
        assert "--dangerously-skip-permissions" in cmd_arg


# ----------------------------------------------------------------------------
# _run_grader (mocked subprocess)
# ----------------------------------------------------------------------------


class TestRunGrader:
    @pytest.fixture(autouse=True)
    def _stub_grader_prompt(self, tmp_path: Path):
        """Provide a fake agents/grader.md so _run_grader can read it.

        The runner resolves the grader prompt via Path(__file__).parent.parent /
        "agents" / "grader.md" — pointing at the real installed file. For tests
        we monkeypatch only that exact path's read.
        """
        agents_dir = Path(__file__).resolve().parent.parent / "agents"
        grader_md = agents_dir / "grader.md"
        # If the real file exists, reuse it. Otherwise create a stub temporarily.
        created = False
        if not grader_md.exists():
            agents_dir.mkdir(parents=True, exist_ok=True)
            _ = grader_md.write_text("test grader instructions")
            created = True
        yield
        if created:
            grader_md.unlink(missing_ok=True)

    def test_success_loads_grading(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run"
        run_dir.mkdir()
        _ = (run_dir / "grading.json").write_text(
            json.dumps({"summary": {"pass_rate": 1.0, "passed": 1, "failed": 0, "total": 1}})
        )
        with patch("scripts.runner.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
            result = _run_grader(
                run_dir=run_dir,
                assertions=["a", "b"],
                target_type="skill",
                model="m",
                timeout=1,
            )
        assert isinstance(result, GraderSuccess)
        assert result.grading["summary"] == {
            "pass_rate": 1.0,
            "passed": 1,
            "failed": 0,
            "total": 1,
        }

    def test_timeout_returns_failure(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run"
        run_dir.mkdir()
        with patch(
            "scripts.runner.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=1),
        ):
            result = _run_grader(
                run_dir=run_dir,
                assertions=["a"],
                target_type="skill",
                model="m",
                timeout=1,
            )
        assert isinstance(result, GraderFailure)
        assert result.reason == "grader-failed"

    def test_no_grading_file_returns_failure(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run"
        run_dir.mkdir()
        with patch("scripts.runner.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
            result = _run_grader(
                run_dir=run_dir,
                assertions=["a"],
                target_type="skill",
                model="m",
                timeout=1,
            )
        assert isinstance(result, GraderFailure)
        assert result.reason == "grader-no-output"


# ----------------------------------------------------------------------------
# RunConfig dataclass
# ----------------------------------------------------------------------------


class TestRunConfig:
    def test_frozen_immutable(self) -> None:
        cfg = RunConfig(runs=1, model="m", grader_model="m", timeout=1, grader_timeout=1)
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            cfg.runs = 5  # type: ignore[misc]

    def test_default_skip_permissions_false(self) -> None:
        cfg = RunConfig(runs=1, model="m", grader_model="m", timeout=1, grader_timeout=1)
        assert cfg.skip_permissions is False


# ----------------------------------------------------------------------------
# substitute_sandbox / validate_prompt_isolation
# ----------------------------------------------------------------------------


class TestSubstituteSandbox:
    def test_placeholder_replaced_with_path(self) -> None:
        out = substitute_sandbox("write {sandbox}/out.py", Path("/tmp/bench-xyz/with"))
        assert out == "write /tmp/bench-xyz/with/out.py"

    def test_no_placeholder_passthrough(self) -> None:
        out = substitute_sandbox("write out.py", Path("/tmp/bench-xyz/with"))
        assert out == "write out.py"

    def test_multiple_placeholders_all_replaced(self) -> None:
        out = substitute_sandbox(
            "save impl {sandbox}/a.py and test {sandbox}/b.py",
            Path("/tmp/bench-xyz/with"),
        )
        assert "{sandbox}" not in out
        assert out.count("/tmp/bench-xyz/with") == 2

    def test_constant_matches_implementation(self) -> None:
        assert SANDBOX_PLACEHOLDER == "{sandbox}"


class TestValidatePromptIsolation:
    def test_relative_paths_pass(self) -> None:
        assert validate_prompt_isolation("write the result to slugify.py") is None

    def test_sandbox_placeholder_passes(self) -> None:
        assert (
            validate_prompt_isolation("write the result to {sandbox}/slugify.py") is None
        )

    def test_hardcoded_tmp_warns(self) -> None:
        warning = validate_prompt_isolation("save to /tmp/testing-bench-1/out.py")
        assert warning is not None
        assert "/tmp/" in warning or "hardcoded" in warning.lower()

    def test_tmp_plus_sandbox_ok(self) -> None:
        # If the prompt uses both /tmp/ and {sandbox}, trust the author — they
        # may be referencing a scratch path alongside the sandbox.
        assert (
            validate_prompt_isolation(
                "save to {sandbox}/out.py (reference: /tmp/somewhere.log)"
            )
            is None
        )
