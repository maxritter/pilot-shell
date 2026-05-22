"""Tests for spec_mode_guard hook — blocks /spec in plan mode, blocks on non-Opus,
warns in non-bypass mode."""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import patch

from spec_mode_guard import _is_opus, run_spec_mode_guard


def _run_with_input(prompt: str, permission_mode: str) -> tuple[int, str]:
    """Simulate hook invocation. Returns (exit_code, stdout_output).

    By default the cached active model is mocked as None (no cache yet), which
    bypasses the Opus check. Use ``_run_with_model_cache`` to override.
    """
    hook_data = {"prompt": prompt, "permission_mode": permission_mode}
    stdin = StringIO(json.dumps(hook_data))
    with (
        patch("sys.stdin", stdin),
        patch("sys.stdout", new_callable=StringIO) as stdout,
        patch("spec_mode_guard._read_active_model_from_cache", return_value=None),
    ):
        code = run_spec_mode_guard()
        return code, stdout.getvalue()


def _run_with_model_cache(prompt: str, permission_mode: str, model_id: str | None) -> tuple[int, str]:
    """Simulate hook invocation with a specific cached model_id."""
    hook_data = {"prompt": prompt, "permission_mode": permission_mode}
    stdin = StringIO(json.dumps(hook_data))
    with (
        patch("sys.stdin", stdin),
        patch("sys.stdout", new_callable=StringIO) as stdout,
        patch("spec_mode_guard._read_active_model_from_cache", return_value=model_id),
    ):
        code = run_spec_mode_guard()
        return code, stdout.getvalue()


class TestPlanModeBlocking:
    """Plan mode must hard-block /spec."""

    def test_blocks_spec_in_plan_mode(self):
        code, output = _run_with_input("/spec fix login bug", "plan")
        assert code == 2
        result = json.loads(output)
        assert result["decision"] == "block"
        assert "Plan mode" in result["reason"]
        assert "Shift+Tab" in result["reason"]

    def test_blocks_bare_spec_in_plan_mode(self):
        code, output = _run_with_input("/spec", "plan")
        assert code == 2
        result = json.loads(output)
        assert result["decision"] == "block"

    def test_blocks_spec_with_path_in_plan_mode(self):
        code, output = _run_with_input("/spec docs/plans/my-plan.md", "plan")
        assert code == 2


class TestBypassPermissionsAllowed:
    """/spec in bypassPermissions mode passes through silently."""

    def test_allows_spec_in_bypass_mode(self):
        code, output = _run_with_input("/spec fix login bug", "bypassPermissions")
        assert code == 0
        assert output == ""

    def test_allows_bare_spec_in_bypass_mode(self):
        code, output = _run_with_input("/spec", "bypassPermissions")
        assert code == 0
        assert output == ""


class TestNonBypassWarning:
    """Non-bypass modes get a warning but are not blocked."""

    def test_warns_in_default_mode(self):
        code, output = _run_with_input("/spec fix bug", "default")
        assert code == 0
        result = json.loads(output)
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "default" in ctx
        assert "bypassPermissions" in ctx
        assert "proceed" in ctx.lower()

    def test_warns_in_accept_edits_mode(self):
        code, output = _run_with_input("/spec fix bug", "acceptEdits")
        assert code == 0
        result = json.loads(output)
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "acceptEdits" in ctx
        assert "proceed" in ctx.lower()

    def test_warns_in_dont_ask_mode(self):
        code, output = _run_with_input("/spec fix bug", "dontAsk")
        assert code == 0
        result = json.loads(output)
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "dontAsk" in ctx
        assert "proceed" in ctx.lower()

    def test_warning_does_not_block(self):
        """Non-bypass modes must NOT instruct the LLM to stop."""
        for mode in ("default", "acceptEdits", "dontAsk"):
            code, output = _run_with_input("/spec fix bug", mode)
            assert code == 0
            ctx = json.loads(output)["hookSpecificOutput"]["additionalContext"]
            assert "Do NOT" not in ctx
            assert "STOP" not in ctx


class TestNonSpecPrompts:
    """Non-/spec prompts pass through regardless of mode."""

    def test_allows_regular_prompt_in_plan_mode(self):
        code, output = _run_with_input("fix the login bug", "plan")
        assert code == 0
        assert output == ""

    def test_allows_regular_prompt_in_default_mode(self):
        code, output = _run_with_input("explain this code", "default")
        assert code == 0
        assert output == ""

    def test_allows_other_commands_in_plan_mode(self):
        code, output = _run_with_input("/setup-rules", "plan")
        assert code == 0
        assert output == ""

    def test_allows_create_skill_in_plan_mode(self):
        code, output = _run_with_input("/create-skill", "plan")
        assert code == 0
        assert output == ""


class TestEdgeCases:
    """Edge cases and malformed input."""

    def test_handles_invalid_json(self):
        stdin = StringIO("not json")
        with patch("sys.stdin", stdin):
            assert run_spec_mode_guard() == 0

    def test_handles_empty_stdin(self):
        stdin = StringIO("")
        with patch("sys.stdin", stdin):
            assert run_spec_mode_guard() == 0

    def test_handles_missing_prompt(self):
        stdin = StringIO(json.dumps({"permission_mode": "plan"}))
        with patch("sys.stdin", stdin), patch("sys.stdout", new_callable=StringIO):
            assert run_spec_mode_guard() == 0

    def test_handles_missing_permission_mode(self):
        code, output = _run_with_input("/spec fix bug", "")
        assert code == 0
        assert output == ""

    def test_handles_empty_prompt(self):
        code, output = _run_with_input("", "plan")
        assert code == 0
        assert output == ""


class TestIsOpus:
    """_is_opus helper accepts the right model strings and rejects the wrong ones."""

    def test_accepts_bare_opus(self) -> None:
        assert _is_opus("opus") is True

    def test_accepts_opus_with_1m_suffix(self) -> None:
        assert _is_opus("opus[1m]") is True

    def test_accepts_explicit_opus_id(self) -> None:
        assert _is_opus("claude-opus-4-6") is True
        assert _is_opus("claude-opus-4-7") is True

    def test_accepts_explicit_opus_id_with_1m(self) -> None:
        assert _is_opus("claude-opus-4-7[1m]") is True

    def test_rejects_sonnet(self) -> None:
        assert _is_opus("sonnet") is False
        assert _is_opus("sonnet[1m]") is False

    def test_rejects_claude_sonnet_id(self) -> None:
        assert _is_opus("claude-sonnet-4-6") is False

    def test_rejects_lookalike_prefix(self) -> None:
        """`claude-opusculus-1` starts with 'claude-opus' but is NOT an Opus model."""
        assert _is_opus("claude-opusculus-1") is False

    def test_rejects_empty_string(self) -> None:
        assert _is_opus("") is False

    def test_rejects_non_string(self) -> None:
        assert _is_opus(None) is False  # type: ignore[arg-type]


class TestOpusModelBlocking:
    """/spec on a non-Opus model is hard-blocked when the cache has a model_id."""

    def test_blocks_spec_when_active_model_is_sonnet(self) -> None:
        code, output = _run_with_model_cache("/spec build a feature", "bypassPermissions", "sonnet")
        assert code == 2
        result = json.loads(output)
        assert result["decision"] == "block"
        assert "Opus" in result["reason"]
        assert "/model opus[1m]" in result["reason"]

    def test_blocks_spec_when_active_model_is_explicit_sonnet_id(self) -> None:
        code, output = _run_with_model_cache("/spec build a feature", "bypassPermissions", "claude-sonnet-4-6")
        assert code == 2

    def test_allows_spec_when_active_model_is_opus(self) -> None:
        code, output = _run_with_model_cache("/spec build a feature", "bypassPermissions", "opus")
        assert code == 0
        assert output == ""

    def test_allows_spec_when_active_model_is_opus_1m(self) -> None:
        code, output = _run_with_model_cache("/spec build a feature", "bypassPermissions", "opus[1m]")
        assert code == 0

    def test_allows_spec_when_active_model_is_explicit_opus_id(self) -> None:
        code, output = _run_with_model_cache("/spec build a feature", "bypassPermissions", "claude-opus-4-6")
        assert code == 0

    def test_does_not_block_when_cache_missing(self) -> None:
        """No statusline render yet → no cache → don't block (fall-through path)."""
        code, output = _run_with_model_cache("/spec build a feature", "bypassPermissions", None)
        assert code == 0
        assert output == ""

    def test_plan_mode_precedes_opus_block(self) -> None:
        """When both checks would fire, Plan-mode block wins (it's the user's
        more-actionable first step)."""
        code, output = _run_with_model_cache("/spec build a feature", "plan", "sonnet")
        assert code == 2
        result = json.loads(output)
        assert "Plan mode" in result["reason"]


class TestResumeExistingPlanBypass:
    """`/spec <path/to/plan.md>` resumes an existing plan — must NOT be Opus-gated.

    This is the core modelSwitch=true return path: user plans on Opus, then
    switches to Sonnet (Option A: `/model sonnet[1m]` + any prompt; Option B:
    `/clear` + `/spec <plan.md>`). If the guard blocks the resume prompt, the
    entire modelSwitch flow is unreachable on non-Opus.
    """

    def test_resume_on_sonnet_passes_guard(self) -> None:
        code, output = _run_with_model_cache(
            "/spec docs/plans/2026-05-21-build-feature.md", "bypassPermissions", "sonnet"
        )
        assert code == 0
        assert output == ""

    def test_resume_on_sonnet_1m_passes_guard(self) -> None:
        code, output = _run_with_model_cache(
            "/spec docs/plans/2026-05-21-build-feature.md", "bypassPermissions", "sonnet[1m]"
        )
        assert code == 0

    def test_resume_with_explicit_sonnet_id_passes_guard(self) -> None:
        code, output = _run_with_model_cache(
            "/spec docs/plans/2026-05-21-build-feature.md", "bypassPermissions", "claude-sonnet-4-6"
        )
        assert code == 0

    def test_new_plan_on_sonnet_still_blocks(self) -> None:
        """Sanity: new plan prompts (without a `.md` argument) still hit the guard."""
        code, output = _run_with_model_cache("/spec build a feature", "bypassPermissions", "sonnet")
        assert code == 2
        result = json.loads(output)
        assert "/model opus[1m]" in result["reason"]

    def test_plan_mode_still_blocks_resume(self) -> None:
        """Plan-mode block precedes the resume bypass — fix the permission mode first."""
        code, output = _run_with_model_cache("/spec docs/plans/2026-05-21-build-feature.md", "plan", "sonnet")
        assert code == 2
        result = json.loads(output)
        assert "Plan mode" in result["reason"]

    def test_resume_path_with_trailing_flag_passes_guard(self) -> None:
        """Tokenisation only inspects the first whitespace-delimited token —
        trailing flags/args don't change the verdict."""
        code, output = _run_with_model_cache(
            "/spec docs/plans/2026-05-21-build-feature.md --foo", "bypassPermissions", "sonnet"
        )
        assert code == 0

    def test_resume_with_bare_spec_does_not_match_resume(self) -> None:
        """`/spec` with no argument is NOT a resume — still subject to Opus gate."""
        code, output = _run_with_model_cache("/spec", "bypassPermissions", "sonnet")
        assert code == 2


class TestSpecFamilyPrefixMatch:
    """Regression for C1: prompt.startswith('/spec') must NOT overmatch sibling
    slash commands (`/spec-implement`, `/spec-verify`, `/spec-plan`,
    `/spec-bugfix-plan`, `/spec-bugfix-verify`). They're designed to run on
    Sonnet during the model-switch handoff and must not trip the Opus gate.
    """

    def test_spec_implement_on_sonnet_not_blocked(self) -> None:
        code, output = _run_with_model_cache("/spec-implement docs/plans/foo.md", "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""

    def test_spec_verify_on_sonnet_not_blocked(self) -> None:
        code, output = _run_with_model_cache("/spec-verify docs/plans/foo.md", "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""

    def test_spec_plan_on_sonnet_not_blocked(self) -> None:
        code, output = _run_with_model_cache("/spec-plan", "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""

    def test_spec_bugfix_plan_on_sonnet_not_blocked(self) -> None:
        code, output = _run_with_model_cache("/spec-bugfix-plan", "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""

    def test_spec_bugfix_verify_on_sonnet_not_blocked(self) -> None:
        code, output = _run_with_model_cache("/spec-bugfix-verify", "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""

    def test_spec_underscore_suffix_not_matched(self) -> None:
        """Defensive: `/spec_foo` is not a /spec invocation either."""
        code, output = _run_with_model_cache("/spec_foo bar", "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""

    def test_plain_spec_with_space_still_blocked(self) -> None:
        """Sanity: `/spec ...` (with whitespace) still triggers the gate."""
        code, output = _run_with_model_cache("/spec build a feature", "bypassPermissions", "sonnet")
        assert code == 2

    def test_plain_spec_alone_still_blocked(self) -> None:
        """Sanity: bare `/spec` still triggers the gate."""
        code, output = _run_with_model_cache("/spec", "bypassPermissions", "sonnet")
        assert code == 2


class TestResumePathRobustness:
    """Regression for C2: resume detection must be case-insensitive on `.md`
    and must handle quoted paths containing spaces.
    """

    def test_resume_uppercase_md_extension(self) -> None:
        code, output = _run_with_model_cache("/spec docs/plans/Foo.MD", "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""

    def test_resume_mixed_case_md_extension(self) -> None:
        code, output = _run_with_model_cache("/spec docs/plans/Foo.Md", "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""

    def test_resume_double_quoted_path_with_spaces(self) -> None:
        """`/spec "docs/plans/my plan.md"` — shlex must surface this as a single
        token ending in `.md`."""
        code, output = _run_with_model_cache('/spec "docs/plans/my plan.md"', "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""

    def test_resume_single_quoted_path_with_spaces(self) -> None:
        code, output = _run_with_model_cache("/spec 'docs/plans/my plan.md'", "bypassPermissions", "sonnet")
        assert code == 0
        assert output == ""


class TestCacheMissingEmitsWarning:
    """Regression for C3: when the statusline cache is missing the gate still
    fails open (per project preference), but it must emit a stderr warning so
    the user knows the Opus check did not run."""

    def test_warning_emitted_when_cache_missing(self) -> None:
        import io as _io

        hook_data = {"prompt": "/spec build a feature", "permission_mode": "bypassPermissions"}
        stdin = StringIO(json.dumps(hook_data))
        with (
            patch("sys.stdin", stdin),
            patch("sys.stdout", new_callable=StringIO),
            patch("sys.stderr", new_callable=_io.StringIO) as stderr,
            patch("spec_mode_guard._read_active_model_from_cache", return_value=None),
        ):
            code = run_spec_mode_guard()
            assert code == 0
            err = stderr.getvalue()
            assert "Pilot" in err
            assert "Opus" in err

    def test_no_warning_when_cache_has_opus(self) -> None:
        """Sanity: when the cache resolves to Opus, no warning fires."""
        import io as _io

        hook_data = {"prompt": "/spec build a feature", "permission_mode": "bypassPermissions"}
        stdin = StringIO(json.dumps(hook_data))
        with (
            patch("sys.stdin", stdin),
            patch("sys.stdout", new_callable=StringIO),
            patch("sys.stderr", new_callable=_io.StringIO) as stderr,
            patch("spec_mode_guard._read_active_model_from_cache", return_value="opus"),
        ):
            code = run_spec_mode_guard()
            assert code == 0
            assert stderr.getvalue() == ""

    def test_no_warning_on_resume_path_even_when_cache_missing(self) -> None:
        """Resume invocations bypass the Opus check entirely — no warning."""
        import io as _io

        hook_data = {"prompt": "/spec docs/plans/foo.md", "permission_mode": "bypassPermissions"}
        stdin = StringIO(json.dumps(hook_data))
        with (
            patch("sys.stdin", stdin),
            patch("sys.stdout", new_callable=StringIO),
            patch("sys.stderr", new_callable=_io.StringIO) as stderr,
            patch("spec_mode_guard._read_active_model_from_cache", return_value=None),
        ):
            code = run_spec_mode_guard()
            assert code == 0
            assert stderr.getvalue() == ""
