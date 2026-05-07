"""Tests for _lib.allow_tags — transcript-tail parser + tag application."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from _lib.allow_tags import (
    apply_allow_tags,
    load_from_transcript,
    parse_allow_tags,
)
from _lib.secret_scanner import Finding


def _user_text(text: str) -> dict:
    return {"type": "user", "message": {"role": "user", "content": text}}


def _user_blocks(blocks: list[dict]) -> dict:
    return {"type": "user", "message": {"role": "user", "content": blocks}}


def _assistant(text: str) -> dict:
    return {"type": "assistant", "message": {"role": "assistant", "content": text}}


def _tool_result_block(content: str) -> dict:
    return {"type": "tool_result", "content": content}


def _text_block(text: str) -> dict:
    return {"type": "text", "text": text}


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _make_finding(rule_id: str = "aws-access-key", value: str = "AKIAIOSFODNN7EXAMPLE") -> Finding:
    return Finding(
        rule_id=rule_id,
        description="AWS Access Key ID",
        match_redacted="AKIA****MPLE",
        secret_value=value,
    )


class TestParseAllowTags:
    def test_no_tag(self):
        assert parse_allow_tags("hello") == set()

    def test_allow_secret(self):
        assert parse_allow_tags("[allow-secret] my key") == {"secret"}

    def test_allow_all(self):
        assert parse_allow_tags("[allow-all] anything") == {"all"}

    def test_case_insensitive(self):
        assert parse_allow_tags("[Allow-All]") == {"all"}
        assert parse_allow_tags("[ALLOW-SECRET]") == {"secret"}

    def test_multiple_tags(self):
        assert parse_allow_tags("[allow-secret] [allow-all] x") == {"secret", "all"}

    def test_lowercase_stored(self):
        # Source case is preserved in input but stored lowercased
        assert parse_allow_tags("[allow-SECRET]") == {"secret"}


class TestLoadFromTranscript:
    def test_missing_file(self, tmp_path: Path):
        assert load_from_transcript(str(tmp_path / "nope.jsonl")) == set()

    def test_empty_file(self, tmp_path: Path):
        p = tmp_path / "empty.jsonl"
        p.write_text("")
        assert load_from_transcript(str(p)) == set()

    def test_one_user_text_with_tag(self, tmp_path: Path):
        p = tmp_path / "t.jsonl"
        _write_jsonl(p, [_user_text("[allow-secret] please")])
        assert load_from_transcript(str(p)) == {"secret"}

    def test_consumed_by_subsequent_tool_result_record(self, tmp_path: Path):
        """A user-role record with ONLY a tool_result block (no text block) is a
        SUBSEQUENT JSONL record and consumes the tag.

        Authoritative reference: sensitive-canary/src/pre-tool-use-hook.ts:75-96.
        """
        p = tmp_path / "t.jsonl"
        _write_jsonl(
            p,
            [
                _user_text("[allow-secret] please"),
                _user_blocks([_tool_result_block("ok")]),
            ],
        )
        assert load_from_transcript(str(p)) == set()

    def test_assistant_record_does_not_consume(self, tmp_path: Path):
        p = tmp_path / "t.jsonl"
        _write_jsonl(
            p,
            [
                _user_text("[allow-secret] please"),
                _assistant("ack"),
            ],
        )
        assert load_from_transcript(str(p)) == {"secret"}

    def test_later_user_text_replaces(self, tmp_path: Path):
        """Most recent user text message is the source of truth."""
        p = tmp_path / "t.jsonl"
        _write_jsonl(
            p,
            [
                _user_text("no tag"),
                _user_text("[allow-secret] now I want it"),
            ],
        )
        assert load_from_transcript(str(p)) == {"secret"}

    def test_later_user_text_without_tag_replaces(self, tmp_path: Path):
        """Tag from earlier message is gone if later user text doesn't have it."""
        p = tmp_path / "t.jsonl"
        _write_jsonl(
            p,
            [
                _user_text("[allow-secret] earlier"),
                _user_text("just a follow-up"),
            ],
        )
        assert load_from_transcript(str(p)) == set()

    def test_malformed_lines_skipped(self, tmp_path: Path):
        p = tmp_path / "t.jsonl"
        with p.open("w") as f:
            f.write("not json\n")
            f.write(json.dumps(_user_text("[allow-all] hi")) + "\n")
            f.write("garbage{}{}\n")
        assert load_from_transcript(str(p)) == {"all"}

    def test_only_last_64kb_read(self, tmp_path: Path):
        """File > 64 KB: only the tail is parsed."""
        p = tmp_path / "big.jsonl"
        with p.open("w") as f:
            # Pad with 100 KB of garbage user-text records (no tag)
            for _ in range(2000):
                f.write(json.dumps(_user_text("x" * 50)) + "\n")
            # Append a tagged user message at the very end
            f.write(json.dumps(_user_text("[allow-secret] tail")) + "\n")
        # Tag in the tail must be visible; padding records are far past the cutoff
        assert load_from_transcript(str(p)) == {"secret"}

    def test_post_tool_use_keeps_last_tool_result_unconsumed(self, tmp_path: Path):
        """When for_post_tool_use=True, the LAST tool_result record is treated as
        the call that triggered THIS hook — the tag is NOT yet consumed.

        This addresses the timing edge case where Claude Code may have appended
        the just-completed tool_result to the transcript before firing PostToolUse.
        """
        p = tmp_path / "t.jsonl"
        _write_jsonl(
            p,
            [
                _user_text("[allow-secret] please"),
                _user_blocks([_tool_result_block("output")]),
            ],
        )
        # PreToolUse semantics: tag consumed
        assert load_from_transcript(str(p)) == set()
        # PostToolUse semantics: tag still valid
        assert load_from_transcript(str(p), for_post_tool_use=True) == {"secret"}

    def test_post_tool_use_with_two_subsequent_tool_results_still_consumed(self, tmp_path: Path):
        """Even in PostToolUse mode, MORE than one tool_result after the last text
        means earlier tool calls already consumed the tag — only the LAST one is
        the call that triggered this hook, but a non-last one already used it up.
        """
        p = tmp_path / "t.jsonl"
        _write_jsonl(
            p,
            [
                _user_text("[allow-secret] please"),
                _user_blocks([_tool_result_block("call1")]),
                _user_blocks([_tool_result_block("call2")]),
            ],
        )
        assert load_from_transcript(str(p), for_post_tool_use=True) == set()

    def test_text_block_in_content_array(self, tmp_path: Path):
        """User content can be a list with a text block — tag must still parse."""
        p = tmp_path / "t.jsonl"
        _write_jsonl(p, [_user_blocks([_text_block("[allow-secret] in block")])])
        assert load_from_transcript(str(p)) == {"secret"}


class TestApplyAllowTags:
    def test_no_tags_pass_through(self):
        f = [_make_finding()]
        assert apply_allow_tags(f, set()) == f

    def test_all_drops_everything(self):
        f = [_make_finding(), _make_finding(rule_id="github-pat", value="ghp_" + "x" * 36)]
        assert apply_allow_tags(f, {"all"}) == []

    def test_secret_drops_everything(self):
        """All findings are secret-category in our port (PII out of scope)."""
        f = [_make_finding()]
        assert apply_allow_tags(f, {"secret"}) == []

    def test_dedupes_by_secret_value(self):
        """Duplicate secret values are deduped on output."""
        f1 = _make_finding()
        f2 = _make_finding()  # same value
        f3 = _make_finding(rule_id="github-pat", value="ghp_unique")
        result = apply_allow_tags([f1, f2, f3], set())
        # f2 deduped; f1 and f3 remain
        assert len(result) == 2
        values = {x.secret_value for x in result}
        assert values == {"AKIAIOSFODNN7EXAMPLE", "ghp_unique"}


@pytest.mark.parametrize(
    "tag_input,expected",
    [
        ("[allow-secret]", {"secret"}),
        ("[allow-all]", {"all"}),
        ("[Allow-Secret][ALLOW-ALL]", {"secret", "all"}),
        ("nothing here", set()),
    ],
)
def test_parse_param(tag_input: str, expected: set[str]):
    assert parse_allow_tags(tag_input) == expected
