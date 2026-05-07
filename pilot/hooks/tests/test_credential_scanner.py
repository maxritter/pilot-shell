"""Tests for credential_scanner hook — UserPromptSubmit + PreToolUse(Read|Bash) + PostToolUse(Bash)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import credential_scanner
import pytest

HOOK_PATH = Path(__file__).resolve().parent.parent / "credential_scanner.py"

AKIA = "AKIAIOSFODNN7EXAMPLE"


# ── Test helpers ──────────────────────────────────────────────────────────────


def _run(payload: dict) -> tuple[int, str, str]:
    """Run the hook in-process. Returns (exit_code, stdout, stderr)."""
    stdin = StringIO(json.dumps(payload))
    out = StringIO()
    err = StringIO()
    with patch("sys.stdin", stdin), patch("sys.stdout", out), patch("sys.stderr", err):
        code = credential_scanner.run_credential_scanner()
    return code, out.getvalue(), err.getvalue()


def _is_pre_deny(stdout: str) -> bool:
    try:
        d = json.loads(stdout.strip())
        return d.get("permissionDecision") == "deny"
    except (json.JSONDecodeError, ValueError):
        return False


def _is_post_block(stdout: str) -> bool:
    try:
        d = json.loads(stdout.strip())
        return d.get("decision") == "block"
    except (json.JSONDecodeError, ValueError):
        return False


def _deny_reason(stdout: str) -> str:
    try:
        return json.loads(stdout.strip()).get("reason", "")
    except (json.JSONDecodeError, ValueError):
        return ""


def _make_transcript(tmp_path: Path, user_text: str | None = None) -> str:
    """Write a JSONL transcript with one user-text record (or empty file)."""
    p = tmp_path / "transcript.jsonl"
    if user_text is not None:
        rec = {"type": "user", "message": {"role": "user", "content": user_text}}
        p.write_text(json.dumps(rec) + "\n")
    else:
        p.write_text("")
    return str(p)


# ── Toggle gate ───────────────────────────────────────────────────────────────


class TestToggle:
    def test_toggle_off_skips_user_prompt(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "false")
        code, out, _ = _run({"hook_event_name": "UserPromptSubmit", "prompt": f"My key {AKIA}"})
        assert code == 0
        assert out == ""

    def test_toggle_off_skips_read(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "false")
        f = tmp_path / "secret.yml"
        f.write_text(f"key: {AKIA}")
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0

    def test_toggle_off_skips_bash(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "false")
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": f"echo {AKIA}"},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0

    def test_toggle_default_on(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("PILOT_CREDENTIAL_SCANNER_ENABLED", raising=False)
        code, _, _ = _run({"hook_event_name": "UserPromptSubmit", "prompt": f"My key {AKIA}"})
        assert code == 2

    def test_toggle_explicit_true(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run({"hook_event_name": "UserPromptSubmit", "prompt": f"My key {AKIA}"})
        assert code == 2


# ── UserPromptSubmit ──────────────────────────────────────────────────────────


class TestUserPromptSubmit:
    def test_secret_blocks(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, err = _run({"hook_event_name": "UserPromptSubmit", "prompt": f"My key {AKIA}"})
        assert code == 2
        assert "aws-access-key" in err

    def test_clean_passes(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run({"hook_event_name": "UserPromptSubmit", "prompt": "hello, please help"})
        assert code == 0

    def test_allow_secret_bypasses(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run(
            {
                "hook_event_name": "UserPromptSubmit",
                "prompt": f"[allow-secret] my key {AKIA}",
            }
        )
        assert code == 0

    def test_allow_all_bypasses(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run(
            {
                "hook_event_name": "UserPromptSubmit",
                "prompt": f"[allow-all] my key {AKIA}",
            }
        )
        assert code == 0

    def test_empty_prompt_passes(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run({"hook_event_name": "UserPromptSubmit", "prompt": ""})
        assert code == 0


# ── PreToolUse(Read) ──────────────────────────────────────────────────────────


class TestPreToolUseRead:
    def test_dotenv_name_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / ".env"
        f.write_text("# innocuous\n")
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert _is_pre_deny(out)
        assert ".env" in _deny_reason(out)

    def test_dotenv_local_name_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / ".env.local"
        f.write_text("# innocuous\n")
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert _is_pre_deny(out)

    def test_dotenv_with_allow_tag_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / ".env"
        f.write_text("# innocuous\n")
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path, "[allow-secret] read it"),
            }
        )
        assert code == 0

    def test_content_with_secret_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / "config.yaml"
        f.write_text(f"api_key: {AKIA}\n")
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert "aws-access-key" in _deny_reason(out)

    def test_content_clean_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / "ok.yaml"
        f.write_text("name: hello\nvalue: world\n")
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0

    def test_missing_file_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Missing file → no findings, hook passes (Read tool will then error on its own)."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(tmp_path / "nope.txt")},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0

    def test_symlink_to_dotenv_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        target = tmp_path / "actual" / ".env"
        target.parent.mkdir()
        target.write_text("# innocuous\n")
        link = tmp_path / "safe.txt"
        link.symlink_to(target)
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(link)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert _is_pre_deny(out)
        assert ".env" in _deny_reason(out)

    def test_fifo_rejected(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Non-regular files (FIFO) get denied without scanning."""
        if not hasattr(os, "mkfifo"):
            pytest.skip("FIFO not supported on this platform")
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        fifo = tmp_path / "pipe"
        os.mkfifo(fifo)
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(fifo)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert "regular file" in _deny_reason(out)

    def test_utf16_le_with_secret_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / "u16.yml"
        # UTF-16-LE BOM + content
        content = f"api_key: {AKIA}".encode("utf-16-le")
        f.write_bytes(b"\xff\xfe" + content)
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert "aws-access-key" in _deny_reason(out)

    def test_utf8_bom_with_secret_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / "u8bom.yml"
        f.write_bytes(b"\xef\xbb\xbf" + f"api_key: {AKIA}".encode())
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert "aws-access-key" in _deny_reason(out)

    def test_oversize_file_passes_quickly(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """File > 1 MB: only 1 MB is scanned. Should pass quickly with no findings."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / "big.txt"
        f.write_bytes(b"x" * (2 * 1024 * 1024))  # 2 MB of x's
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0

    def test_binary_with_nul_truncated(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Binary file with NUL byte: scanner reads up to NUL, decodes errors=replace, no crash."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / "b.bin"
        # No BOM, NUL at byte 5, then bytes — scan only first 5 bytes
        f.write_bytes(b"hello\x00\xff\xff\xff" + AKIA.encode())
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0  # AKIA after NUL not scanned


# ── PreToolUse(Bash) ──────────────────────────────────────────────────────────


class TestPreToolUseBash:
    def test_command_text_secret_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": f"echo {AKIA}"},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert "aws-access-key" in _deny_reason(out)

    def test_clean_command_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "ls -la"},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0

    def test_env_var_with_secret_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        monkeypatch.setenv("AWS_ACCESS_KEY", AKIA)
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "echo $AWS_ACCESS_KEY"},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert "aws-access-key" in _deny_reason(out)

    def test_cat_secrets_file_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / "secrets.yaml"
        f.write_text(f"api_key: {AKIA}\n")
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": f"cat {f}"},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(tmp_path),
            }
        )
        assert code == 2
        assert "aws-access-key" in _deny_reason(out)

    def test_allow_tag_in_command_does_not_bypass(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Literal [allow-secret] in command string is NOT honoured (only transcript)."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        f = tmp_path / "secrets.txt"
        f.write_text(AKIA)
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": f"echo '[allow-secret]' && cat {f}"},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(tmp_path),
            }
        )
        assert code == 2
        assert _is_pre_deny(out)


class TestPreToolUseBashGitCommit:
    """Git commit + chained add+commit detection."""

    @staticmethod
    def _init_repo(repo: Path) -> None:
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@test"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=repo, check=True)

    def test_commit_with_clean_diff_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "f.txt").write_text("hello\n")
        subprocess.run(["git", "add", "f.txt"], cwd=repo, check=True)
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 0

    def test_commit_with_staged_secret_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets.txt").write_text(f"key={AKIA}\n")
        subprocess.run(["git", "add", "secrets.txt"], cwd=repo, check=True)
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2
        assert "aws-access-key" in _deny_reason(out)

    def test_commit_no_verify_still_blocks(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """--no-verify skips git's own hooks but NOT our PreToolUse hook."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets.txt").write_text(AKIA)
        subprocess.run(["git", "add", "secrets.txt"], cwd=repo, check=True)
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git commit --no-verify -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2

    def test_commit_amend_blocks(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        # initial commit
        (repo / "a.txt").write_text("a\n")
        subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
        # stage a secret on top
        (repo / "secrets.txt").write_text(AKIA)
        subprocess.run(["git", "add", "secrets.txt"], cwd=repo, check=True)
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "git commit --amend --no-edit"},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2

    def test_chained_add_commit_blocks_via_file_scan(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """File initially UNSTAGED — chain detection must scan the file directly."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets.txt").write_text(AKIA)
        # Note: NOT staged — chain detection must catch it
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git add secrets.txt && git commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2
        assert _is_pre_deny(out)

    def test_chained_add_dash_a(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """`git add -A`: enumerate via git ls-files."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets.txt").write_text(AKIA)
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git add -A && git commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2

    def test_chain_with_cd_redirects_cwd(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """`cd /repo && git add x.txt && git commit -m y` — effective cwd tracking."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets.txt").write_text(AKIA)
        # Hook process cwd is tmp_path (which has no secrets.txt). Effective cwd via cd.
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'cd {repo} && git add secrets.txt && git commit -m "x"',
                },
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(tmp_path),
            }
        )
        assert code == 2

    def test_chained_add_directory_blocks(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Closes Codex finding #1 — `git add <dir>` with secret inside the dir must block."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets_dir").mkdir()
        (repo / "secrets_dir" / "key.txt").write_text(AKIA)
        # Note: dir is unstaged. Chain detection must walk into the directory.
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git add secrets_dir && git commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2

    def test_no_pager_global_option_does_not_bypass_commit(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Closes Codex finding #2 — `git --no-pager commit` must NOT bypass scanning."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets.txt").write_text(AKIA)
        subprocess.run(["git", "add", "secrets.txt"], cwd=repo, check=True)
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git --no-pager commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2

    def test_no_pager_chain_does_not_bypass(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """`git add x && git --no-pager commit` — both detection paths must hit."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets.txt").write_text(AKIA)
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {
                    "command": 'git add secrets.txt && git --no-pager commit -m "x"',
                },
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2

    def test_add_dash_a_does_not_blow_budget_on_clean_tracked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Closes Codex finding #3 — `--cached` was including clean tracked files,
        which could exhaust the 1 MB budget before reaching the modified secret-bearing file.
        Setup: many large clean tracked files (already committed), plus one small modified
        file with the secret. The fix drops `--cached` from enumeration so clean files
        are not scanned.
        """
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        # Commit several large, clean files (tracked, no secret)
        for i in range(3):
            (repo / f"big{i}.txt").write_text("x" * 400_000)  # 1.2 MB total
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
        # Now create a modified untracked file containing the secret
        (repo / "secrets.txt").write_text(AKIA)
        # `git add -A && git commit` should detect the secret — clean tracked files
        # MUST NOT exhaust the budget first.
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git add -A && git commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2

    def test_chain_with_spaces_in_cd_path_resolves(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Closes Claude reviewer should_fix #1 — paths with spaces must be tracked."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo_dir = tmp_path / "my repo"
        repo_dir.mkdir()
        self._init_repo(repo_dir)
        (repo_dir / "secrets.txt").write_text(AKIA)
        # Quoted path with space → must resolve correctly, not fall back to initial_cwd
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'cd "{repo_dir}" && git add secrets.txt && git commit -m "x"',
                },
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(tmp_path),
            }
        )
        assert code == 2

    def test_chain_with_unresolvable_cd_fails_closed(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """cd to non-existent dir → fail-closed deny."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        bogus = tmp_path / "does_not_exist"
        code, out, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'cd {bogus} && git add secrets.txt && git commit -m "x"',
                },
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(tmp_path),
            }
        )
        assert code == 2
        assert "unresolvable" in _deny_reason(out).lower()

    def test_git_dash_c_redirects_repo(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """`git -C /repo add file && git -C /repo commit` — -C flag honoured."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets.txt").write_text(AKIA)
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'git -C {repo} add secrets.txt && git -C {repo} commit -m "x"',
                },
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(tmp_path),
            }
        )
        assert code == 2

    def test_staged_utf16_blob_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """UTF-16 staged file: patch text doesn't contain raw bytes; blob scan must catch it."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        f = repo / "u16.txt"
        f.write_bytes(b"\xff\xfe" + f"key={AKIA}".encode("utf-16-le"))
        subprocess.run(["git", "add", "u16.txt"], cwd=repo, check=True)
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(repo),
            }
        )
        assert code == 2

    def test_commit_with_allow_tag_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        (repo / "secrets.txt").write_text(AKIA)
        subprocess.run(["git", "add", "secrets.txt"], cwd=repo, check=True)
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path, "[allow-secret] commit it"),
                "cwd": str(repo),
            }
        )
        assert code == 0

    def test_commit_outside_repo_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Not a git repo → fail open (no commit will happen anyway)."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 'git commit -m "x"'},
                "transcript_path": _make_transcript(tmp_path),
                "cwd": str(tmp_path),
            }
        )
        assert code == 0


# ── Subprocess-mode sanity check ──────────────────────────────────────────────


class TestPostToolUseBash:
    """Task 8: PostToolUse(Bash) output scanner."""

    def test_clean_output_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, out, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "ls"},
                "tool_response": {"stdout": "hello world\n", "stderr": "", "interrupted": False},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0
        assert out == ""

    def test_secret_in_stdout_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, out, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python -c 'print(...)'"},
                "tool_response": {
                    "stdout": f'{{"key": "{AKIA}"}}\n',
                    "stderr": "",
                    "interrupted": False,
                },
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert _is_post_block(out)
        assert "aws-access-key" in _deny_reason(out)

    def test_secret_in_stderr_blocked(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, out, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "x"},
                "tool_response": {"stdout": "", "stderr": f"error: token={AKIA}\n"},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert _is_post_block(out)

    def test_allow_tag_in_transcript_bypasses(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "x"},
                "tool_response": {"stdout": f"key={AKIA}", "stderr": ""},
                "transcript_path": _make_transcript(tmp_path, "[allow-secret] please run it"),
            }
        )
        assert code == 0

    def test_oversize_no_secret_blocks_fail_closed(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Closes Codex critical #1 / Claude must_fix #1 — fail-CLOSED on >1 MB."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        big = "x" * (1_500_000)
        code, out, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "x"},
                "tool_response": {"stdout": big, "stderr": ""},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert _is_post_block(out)
        assert "1 MB" in _deny_reason(out) or "scan budget" in _deny_reason(out)

    def test_oversize_byte_count_with_multibyte_chars(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Closes Claude reviewer should_fix #2 — byte length, not char length.

        700_000 emoji chars = ~2.8 MB of UTF-8 bytes. Should fail-CLOSED on oversize
        even though Python str length is well under MAX_SCAN_BYTES.
        """
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        # 700_000 4-byte emojis = 2.8 MB UTF-8, but only 700_000 code points
        emoji_blob = "🔐" * 700_000
        code, out, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "x"},
                "tool_response": {"stdout": emoji_blob, "stderr": ""},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2
        assert _is_post_block(out)
        # Block should cite the oversize reason (not a finding)
        assert "scan budget" in _deny_reason(out) or "1 MB" in _deny_reason(out)

    def test_oversize_with_secret_beyond_window(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Secret at byte 1.5M (past the 1 MB scan window) — oversize blocks regardless."""
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        padding = "x" * 1_500_000
        big = padding + AKIA
        code, _, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "x"},
                "tool_response": {"stdout": big, "stderr": ""},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 2

    def test_oversize_with_allow_tag_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        big = "x" * 1_500_000
        code, _, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "x"},
                "tool_response": {"stdout": big, "stderr": ""},
                "transcript_path": _make_transcript(tmp_path, "[allow-secret] big output ok"),
            }
        )
        assert code == 0

    def test_post_tool_use_non_bash_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": "/tmp/x"},
                "tool_response": {"stdout": AKIA, "stderr": ""},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0

    def test_missing_tool_response_passes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "true")
        code, _, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "x"},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0

    def test_toggle_off_bypasses(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("PILOT_CREDENTIAL_SCANNER_ENABLED", "false")
        code, _, _ = _run(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "x"},
                "tool_response": {"stdout": AKIA, "stderr": ""},
                "transcript_path": _make_transcript(tmp_path),
            }
        )
        assert code == 0


class TestSubprocess:
    def test_subprocess_exits_2_with_deny_json(self, tmp_path: Path):
        env = {**os.environ, "PILOT_CREDENTIAL_SCANNER_ENABLED": "true"}
        result = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": f"key {AKIA}"}),
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 2

    def test_subprocess_toggle_off_exits_0(self, tmp_path: Path):
        env = {**os.environ, "PILOT_CREDENTIAL_SCANNER_ENABLED": "false"}
        result = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": f"key {AKIA}"}),
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0
