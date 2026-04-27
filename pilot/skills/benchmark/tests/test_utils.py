"""Tests for scripts.utils — frontmatter parsing, target loading, model resolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.utils import (
    DEFAULT_FALLBACK_MODEL,
    ExecuteFailure,
    ExecuteSuccess,
    GraderFailure,
    GraderSuccess,
    load_target_config,
    parse_skill_frontmatter_field,
    parse_skill_md,
    resolve_executor_model,
    strip_conditional_loading_frontmatter,
)

# ----------------------------------------------------------------------------
# parse_skill_md
# ----------------------------------------------------------------------------


def _make_skill(dir_path: Path, *, filename: str = "SKILL.md", content: str | None = None) -> Path:
    dir_path.mkdir(parents=True, exist_ok=True)
    if content is None:
        content = (
            "---\n"
            'name: my-skill\n'
            'description: "A short description"\n'
            "---\n"
            "\n# Body\n"
        )
    file_path = dir_path / filename
    _ = file_path.write_text(content)
    return file_path


class TestParseSkillMd:
    def test_reads_skill_md(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path)
        name, desc, content = parse_skill_md(tmp_path)
        assert name == "my-skill"
        assert desc == "A short description"
        assert "# Body" in content

    def test_falls_back_to_orchestrator_md(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path, filename="orchestrator.md")
        name, _desc, _content = parse_skill_md(tmp_path)
        assert name == "my-skill"

    def test_handles_block_scalar_description(self, tmp_path: Path) -> None:
        body = (
            "---\n"
            "name: x\n"
            "description: >\n"
            "  This is a long description\n"
            "  that spans two lines\n"
            "---\n"
        )
        _ = _make_skill(tmp_path, content=body)
        _name, desc, _ = parse_skill_md(tmp_path)
        assert "two lines" in desc

    def test_raises_when_no_skill_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            _ = parse_skill_md(tmp_path)

    def test_raises_on_missing_opening_frontmatter(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path, content="no frontmatter here\n")
        with pytest.raises(ValueError, match="opening ---"):
            _ = parse_skill_md(tmp_path)

    def test_raises_on_missing_closing_frontmatter(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path, content="---\nname: x\nstill open\n")
        with pytest.raises(ValueError, match="closing ---"):
            _ = parse_skill_md(tmp_path)


# ----------------------------------------------------------------------------
# parse_skill_frontmatter_field
# ----------------------------------------------------------------------------


class TestParseFrontmatterField:
    def test_returns_field_value(self, tmp_path: Path) -> None:
        body = "---\nname: a\nmodel: opus\n---\n"
        _ = _make_skill(tmp_path, content=body)
        assert parse_skill_frontmatter_field(tmp_path, "model") == "opus"

    def test_returns_none_when_missing(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path)
        assert parse_skill_frontmatter_field(tmp_path, "model") is None

    def test_returns_none_when_no_skill_file(self, tmp_path: Path) -> None:
        assert parse_skill_frontmatter_field(tmp_path, "model") is None

    def test_strips_quotes_and_whitespace(self, tmp_path: Path) -> None:
        body = '---\nname: a\nmodel:  "sonnet"  \n---\n'
        _ = _make_skill(tmp_path, content=body)
        assert parse_skill_frontmatter_field(tmp_path, "model") == "sonnet"


# ----------------------------------------------------------------------------
# load_target_config
# ----------------------------------------------------------------------------


def _write_evals(tmp_path: Path, payload: object) -> Path:
    p = tmp_path / "evals.json"
    _ = p.write_text(json.dumps(payload))
    return p


class TestLoadTargetConfig:
    def test_skill_target(self, tmp_path: Path) -> None:
        path = _write_evals(tmp_path, {"target": {"type": "skill", "path": "/x"}})
        target = load_target_config(path)
        assert target["type"] == "skill"
        assert target.get("path") == "/x"

    def test_defaults_to_skill_when_missing(self, tmp_path: Path) -> None:
        path = _write_evals(tmp_path, {"evals": []})
        target = load_target_config(path)
        assert target["type"] == "skill"

    def test_rejects_invalid_type(self, tmp_path: Path) -> None:
        path = _write_evals(tmp_path, {"target": {"type": "bogus"}})
        with pytest.raises(ValueError, match="target.type must be one of"):
            _ = load_target_config(path)

    def test_handles_non_object_root(self, tmp_path: Path) -> None:
        path = _write_evals(tmp_path, ["not", "an", "object"])
        target = load_target_config(path)
        assert target["type"] == "skill"


# ----------------------------------------------------------------------------
# resolve_executor_model
# ----------------------------------------------------------------------------


class TestResolveExecutorModel:
    def test_returns_fallback_for_rules(self) -> None:
        assert resolve_executor_model({"type": "rules"}) == DEFAULT_FALLBACK_MODEL

    def test_returns_fallback_when_no_path(self) -> None:
        assert resolve_executor_model({"type": "skill"}) == DEFAULT_FALLBACK_MODEL

    def test_resolves_alias_from_frontmatter(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path, content="---\nname: x\nmodel: opus\n---\n")
        result = resolve_executor_model({"type": "skill", "path": str(tmp_path)})
        assert result == "claude-opus-4-7"

    def test_resolves_sonnet_alias(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path, content="---\nname: x\nmodel: sonnet\n---\n")
        result = resolve_executor_model({"type": "skill", "path": str(tmp_path)})
        assert result == "claude-sonnet-4-6"

    def test_passes_through_explicit_model_id(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path, content="---\nname: x\nmodel: claude-opus-4-9\n---\n")
        result = resolve_executor_model({"type": "skill", "path": str(tmp_path)})
        assert result == "claude-opus-4-9"

    def test_falls_back_on_unknown_alias(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path, content="---\nname: x\nmodel: gpt5\n---\n")
        result = resolve_executor_model({"type": "skill", "path": str(tmp_path)})
        assert result == DEFAULT_FALLBACK_MODEL

    def test_falls_back_when_skill_has_no_model_field(self, tmp_path: Path) -> None:
        _ = _make_skill(tmp_path)
        result = resolve_executor_model({"type": "skill", "path": str(tmp_path)})
        assert result == DEFAULT_FALLBACK_MODEL


# ----------------------------------------------------------------------------
# Result dataclasses (smoke tests for the union narrowing pattern)
# ----------------------------------------------------------------------------


class TestExecuteResultDataclasses:
    def test_success_carries_metrics(self) -> None:
        ok = ExecuteSuccess(duration_ms=1234, total_tokens=42, run_dir="/tmp/x")
        assert ok.success is True
        assert ok.duration_ms == 1234
        assert ok.total_tokens == 42

    def test_failure_carries_reason(self) -> None:
        bad = ExecuteFailure(reason="timeout")
        assert bad.success is False
        assert bad.reason == "timeout"

    def test_isinstance_narrowing(self) -> None:
        result: ExecuteSuccess | ExecuteFailure = ExecuteSuccess(
            duration_ms=1, total_tokens=1, run_dir="/x"
        )
        assert isinstance(result, ExecuteSuccess)
        assert not isinstance(result, ExecuteFailure)


class TestGraderResultDataclasses:
    def test_success_carries_grading(self) -> None:
        ok = GraderSuccess(grading={"summary": {"pass_rate": 1.0}})
        assert ok.graded is True
        assert ok.grading["summary"] == {"pass_rate": 1.0}

    def test_failure_carries_reason(self) -> None:
        bad = GraderFailure(reason="grader-no-output")
        assert bad.graded is False
        assert bad.reason == "grader-no-output"


# ----------------------------------------------------------------------------
# strip_conditional_loading_frontmatter
# ----------------------------------------------------------------------------


class TestStripConditionalLoading:
    def test_no_frontmatter_unchanged(self) -> None:
        body = "# Heading\n\nbody text\n"
        out, removed = strip_conditional_loading_frontmatter(body)
        assert out == body
        assert removed == []

    def test_empty_string_unchanged(self) -> None:
        out, removed = strip_conditional_loading_frontmatter("")
        assert out == ""
        assert removed == []

    def test_frontmatter_without_conditional_fields_unchanged(self) -> None:
        content = "---\nname: x\ndescription: y\n---\n# body\n"
        out, removed = strip_conditional_loading_frontmatter(content)
        assert out == content
        assert removed == []

    def test_strips_singular_path_inline(self) -> None:
        content = "---\nname: x\npath: src/**/*.py\ndescription: y\n---\n# body\n"
        out, removed = strip_conditional_loading_frontmatter(content)
        assert removed == ["path"]
        assert "path:" not in out
        assert "name: x" in out
        assert "description: y" in out

    def test_strips_inline_paths_list(self) -> None:
        content = '---\nname: x\npaths: ["**/*.py", "**/*.ts"]\n---\n# body\n'
        out, removed = strip_conditional_loading_frontmatter(content)
        assert removed == ["paths"]
        assert "paths:" not in out
        assert "**/*.py" not in out

    def test_strips_multiline_paths_list(self) -> None:
        # The real shape used by Pilot rules — `paths:` followed by indented `-` items.
        content = (
            "---\n"
            "name: standards-python\n"
            'paths:\n  - "**/*.py"\n  - "tests/**/*.py"\n'
            "description: Python rules\n"
            "---\n"
            "# Python\n"
        )
        out, removed = strip_conditional_loading_frontmatter(content)
        assert removed == ["paths"]
        assert "**/*.py" not in out
        assert "tests/**/*.py" not in out
        assert "name: standards-python" in out
        assert "description: Python rules" in out

    def test_strips_both_path_and_paths(self) -> None:
        content = (
            "---\n"
            "name: x\n"
            "path: legacy/path.md\n"
            "paths:\n  - new\n"
            "---\n"
            "# body\n"
        )
        out, removed = strip_conditional_loading_frontmatter(content)
        assert sorted(removed) == ["path", "paths"]
        assert "path:" not in out
        assert "paths:" not in out
        assert "name: x" in out

    def test_preserves_indented_content_in_other_fields(self) -> None:
        # An indented line that does NOT belong to paths shouldn't be eaten.
        content = (
            "---\n"
            'description: |\n  multi\n  line\n'
            'paths:\n  - "**/*.py"\n'
            "name: x\n"
            "---\n"
            "# body\n"
        )
        out, removed = strip_conditional_loading_frontmatter(content)
        assert removed == ["paths"]
        assert "multi" in out and "line" in out
        assert "**/*.py" not in out

    def test_unterminated_frontmatter_unchanged(self) -> None:
        # No closing --- → don't touch the file (avoid corrupting).
        content = "---\npaths:\n  - foo\n# never closed\n"
        out, removed = strip_conditional_loading_frontmatter(content)
        assert out == content
        assert removed == []

    def test_only_strips_at_start_of_line(self) -> None:
        # A `paths:` mention inside a description value (indented) is part of
        # that field's continuation, not a separate key. We don't strip it.
        content = (
            "---\n"
            "description: |\n"
            "  the user types `paths:` to do X\n"
            "name: x\n"
            "---\n"
        )
        out, removed = strip_conditional_loading_frontmatter(content)
        assert removed == []
        assert "user types `paths:`" in out
