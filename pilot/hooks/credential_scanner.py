#!/usr/bin/env python3
"""Credential leak prevention hook.

Handles three Claude Code hook events:
  - UserPromptSubmit: scan submitted prompts for secrets.
  - PreToolUse(Read): name-block .env / .env.*; content-scan other files.
  - PreToolUse(Bash): scan command text, env vars, file-read targets, git commit
    staged diff + staged blobs, and chained `git add … && git commit` patterns
    with effective-cwd tracking.
  - PostToolUse(Bash): scan tool output (stdout+stderr); fail-CLOSED on >1 MB.

Allow tags `[allow-secret]` / `[allow-all]` are honoured ONLY from user-role
transcript messages (or, for UserPromptSubmit, from the prompt text directly).

Toggle: gated by PILOT_CREDENTIAL_SCANNER_ENABLED env var (default "true").
"""

from __future__ import annotations

import json
import os
import re
import shlex
import signal
import stat
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from _lib.allow_tags import (
    apply_allow_tags,
    load_from_transcript,
    parse_allow_tags,
)
from _lib.secret_scanner import Finding, scan
from _lib.util import post_tool_use_block, pre_tool_use_deny

# ── Constants ────────────────────────────────────────────────────────────────

MAX_SCAN_BYTES = 1_048_576  # 1 MB
MAX_BLOB_TOTAL_BYTES = 5 * MAX_SCAN_BYTES  # cap across all staged blobs
GIT_TIMEOUT_SECONDS = 5
REGEX_TIMEOUT_SECONDS = 2

FILE_READ_COMMANDS: frozenset[str] = frozenset({"cat", "head", "tail", "less", "more", "bat", "nl"})

# Match shell segment separators (mirrors tool_redirect.py:102 — &&, ||, ;, newline)
SHELL_SEGMENT_SEP_RE = re.compile(r"(?:&&|\|\||;|\n)")

# Env var reference: $VAR or ${VAR}
ENV_VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")

# Git global options that take a value (consume the next token when stripping).
_GIT_GLOBAL_OPT_VALUE = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix"})

# Git global flags (no value).
_GIT_GLOBAL_OPT_FLAG = frozenset(
    {
        "--no-pager",
        "-p",
        "--paginate",
        "--no-replace-objects",
        "--bare",
        "--no-optional-locks",
        "--exec-path",
        "--html-path",
        "--man-path",
        "--info-path",
        "--literal-pathspecs",
        "--glob-pathspecs",
        "--noglob-pathspecs",
        "--icase-pathspecs",
    }
)


def _parse_git_invocation(segment: str) -> tuple[str | None, str | None]:
    """Parse a shell segment for `git [global-opts] <subcommand> ...`.

    Returns (subcommand, dash_c_dir). Both are None when the segment is not a
    git invocation. `--no-pager`, `-c name=val`, `-C dir`, `--git-dir`, etc.
    are skipped before identifying the subcommand. Closes Codex finding #2.
    """
    tokens = _tokenize_segment(segment)
    if not tokens or tokens[0] != "git":
        return None, None
    idx = 1
    dash_c: str | None = None
    while idx < len(tokens):
        tk = tokens[idx]
        if tk == "-C" and idx + 1 < len(tokens):
            dash_c = tokens[idx + 1]
            idx += 2
            continue
        if tk in _GIT_GLOBAL_OPT_VALUE and idx + 1 < len(tokens):
            idx += 2
            continue
        if tk in _GIT_GLOBAL_OPT_FLAG:
            idx += 1
            continue
        # `--option=value` form (no separate value token)
        if tk.startswith("--") and "=" in tk:
            opt = tk.split("=", 1)[0]
            if opt in _GIT_GLOBAL_OPT_VALUE or opt in _GIT_GLOBAL_OPT_FLAG:
                idx += 1
                continue
        # Unknown flag — be conservative, skip it (single-token).
        if tk.startswith("-"):
            idx += 1
            continue
        # First non-flag token is the subcommand.
        return tk, dash_c
    return None, dash_c


def _segment_invokes(segment: str, subcommand: str) -> bool:
    """True when the segment runs `git <subcommand>` (with any global options)."""
    sub, _ = _parse_git_invocation(segment)
    return sub == subcommand


def _segment_dash_c(segment: str) -> str | None:
    """Return the `-C <dir>` value from a git invocation, if any."""
    _, dash_c = _parse_git_invocation(segment)
    return dash_c


# ── Allow-tag aware finding pipeline ──────────────────────────────────────────


def _scan_and_filter(text: str, tags: set[str]) -> list[Finding]:
    """Run scan, apply allow tags, dedupe. Returns final findings list."""
    return apply_allow_tags(scan(text), tags)


# ── BOM-aware file reading ────────────────────────────────────────────────────


def _read_file_text(path: Path, max_bytes: int = MAX_SCAN_BYTES) -> str | None:
    """Read up to max_bytes and decode with BOM detection.

    Returns None on I/O error or non-regular files. Use _is_regular_file() for
    explicit non-regular detection in the caller — this just gracefully returns
    None.
    """
    try:
        with path.open("rb") as f:
            head = f.read(4)
            rest = f.read(max_bytes - len(head))
        raw = head + rest
    except OSError:
        return None

    if not raw:
        return ""

    if raw.startswith(b"\xff\xfe"):
        try:
            return raw[2:].decode("utf-16-le", errors="replace")
        except UnicodeDecodeError:
            return None
    if raw.startswith(b"\xfe\xff"):
        try:
            return raw[2:].decode("utf-16-be", errors="replace")
        except UnicodeDecodeError:
            return None
    if raw.startswith(b"\xef\xbb\xbf"):
        body = raw[3:]
        nul = body.find(b"\x00")
        if nul != -1:
            body = body[:nul]
        return body.decode("utf-8", errors="replace")

    nul = raw.find(b"\x00")
    if nul != -1:
        raw = raw[:nul]
    return raw.decode("utf-8", errors="replace")


def _is_regular_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.lstat().st_mode)
    except OSError:
        return False


def _resolved_target(path: Path) -> Path:
    """Resolve symlinks (best-effort, strict=False)."""
    try:
        return path.resolve(strict=False)
    except OSError:
        return path


# ── Regex-timeout safeguard (POSIX only) ──────────────────────────────────────


@contextmanager
def _regex_timeout(seconds: int = REGEX_TIMEOUT_SECONDS) -> Iterator[None]:
    """Wrap a scan in signal.alarm guard on POSIX. No-op elsewhere."""
    if not hasattr(signal, "alarm"):
        yield
        return

    def _on_alarm(_signum: int, _frame: object) -> None:
        raise TimeoutError("regex scan timeout")

    prev_handler = signal.signal(signal.SIGALRM, _on_alarm)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, prev_handler)


# ── Block helpers ─────────────────────────────────────────────────────────────


def _format_finding_lines(findings: list[Finding]) -> list[str]:
    return [f"  [Secret] {f.description} ({f.rule_id}): {f.match_redacted}" for f in findings]


def _allow_hint(action_text: str = "this action") -> str:
    return (
        f"To allow {action_text}, add an allow tag to the next user prompt:\n"
        "  [allow-secret]  — allow secret findings\n"
        "  [allow-all]     — bypass all credential-scanner checks"
    )


def _user_prompt_block(findings: list[Finding]) -> int:
    msg_lines = [
        "🚫 Pilot credential-scanner blocked this prompt — it contains sensitive data:",
        "",
        *_format_finding_lines(findings),
        "",
        _allow_hint("this prompt"),
    ]
    sys.stderr.write("\n".join(msg_lines) + "\n")
    return 2


def _name_block_dotenv(file_path: str) -> int:
    reason = (
        f"Blocked: {file_path} resolves to a .env / .env.* file. These contain secrets and "
        "must not be read into the conversation.\n\n" + _allow_hint(f"reading {file_path}")
    )
    print(pre_tool_use_deny(reason))
    return 2


def _name_block_non_regular(file_path: str) -> int:
    reason = f"Blocked: {file_path} is not a regular file (FIFO, socket, char device, etc.)."
    print(pre_tool_use_deny(reason))
    return 2


def _content_block(source: str, findings: list[Finding]) -> int:
    reason = "\n".join(
        [
            f"Blocked: {source} contains sensitive data:",
            "",
            *_format_finding_lines(findings),
            "",
            _allow_hint(f"this {source}"),
        ]
    )
    print(pre_tool_use_deny(reason))
    return 2


def _post_tool_use_findings_block(findings: list[Finding]) -> int:
    reason = "\n".join(
        [
            "🚫 Bash tool output dropped — contained sensitive data:",
            "",
            *_format_finding_lines(findings),
            "",
            _allow_hint("this output to pass through"),
        ]
    )
    print(post_tool_use_block(reason))
    return 2


def _post_tool_use_oversize_block() -> int:
    reason = (
        "🚫 Bash tool output exceeds 1 MB scan budget — blocked as a precaution. "
        "Use [allow-secret] in your next prompt to allow this specific output through."
    )
    print(post_tool_use_block(reason))
    return 2


def _bash_unresolvable_repo() -> int:
    reason = (
        "Blocked: git chain has unresolvable repo path (cd to non-existent dir or invalid -C). "
        "Use [allow-secret] to override."
    )
    print(pre_tool_use_deny(reason))
    return 2


# ── Path helpers ──────────────────────────────────────────────────────────────


def _is_blocked_env_basename(name: str) -> bool:
    return name == ".env" or name.startswith(".env.")


def _scan_file_path(file_path: str, tags: set[str]) -> int:
    """Scan a file for secrets, applying name-block + content-block rules.

    Returns 2 (block) or 0 (pass).
    """
    if not file_path:
        return 0
    p = Path(file_path)
    requested_basename = p.name
    target = _resolved_target(p)
    target_basename = target.name

    # Name-block applies to BOTH the requested basename and the resolved target.
    if _is_blocked_env_basename(requested_basename) or _is_blocked_env_basename(target_basename):
        if "all" in tags or "secret" in tags:
            return 0
        return _name_block_dotenv(file_path)

    # Reject non-regular files (FIFOs, sockets, etc.) BEFORE reading.
    # If file does not exist, lstat fails — treat as not-a-regular-file → pass through
    # (the Read tool will error on its own).
    if not target.exists():
        return 0
    if not _is_regular_file(target):
        return _name_block_non_regular(file_path)

    text = _read_file_text(target)
    if not text:
        return 0
    try:
        with _regex_timeout():
            findings = _scan_and_filter(text, tags)
    except TimeoutError:
        return 0  # regex catastrophic-backtrack bailout
    if not findings:
        return 0
    return _content_block(file_path, findings)


# ── Bash command parsing ──────────────────────────────────────────────────────


def _split_segments(command: str) -> list[str]:
    return [s.strip() for s in SHELL_SEGMENT_SEP_RE.split(command) if s.strip()]


def _extract_env_var_names(command: str) -> list[str]:
    names: list[str] = []
    for m in ENV_VAR_RE.finditer(command):
        name = m.group(1) or m.group(2)
        if name and name not in names:
            names.append(name)
    return names


def _tokenize_segment(segment: str) -> list[str]:
    """Best-effort shell tokenizer. Returns [] on parse failure (graceful)."""
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return []


def _extract_file_read_targets(segment: str) -> list[str]:
    """If segment is a cat/head/etc. invocation, return positional file args."""
    tokens = _tokenize_segment(segment)
    if len(tokens) < 2:
        return []
    cmd = Path(tokens[0]).name
    if cmd not in FILE_READ_COMMANDS:
        return []
    paths: list[str] = []
    skip_next = False
    for t in tokens[1:]:
        if skip_next:
            skip_next = False
            continue
        if t.startswith("-"):
            continue
        if t in (">", ">>", "<"):
            skip_next = True
            continue
        paths.append(t)
    return paths


def _git_add_tail_tokens(segment: str) -> list[str] | None:
    """Tokens AFTER `git [global-opts] add` (or None if not a git-add segment).

    Honours the same global-option set as `_parse_git_invocation`, so
    `git --no-pager add foo` is parsed correctly.
    """
    tokens = _tokenize_segment(segment)
    if not tokens or tokens[0] != "git":
        return None
    idx = 1
    while idx < len(tokens):
        tk = tokens[idx]
        if tk in _GIT_GLOBAL_OPT_VALUE and idx + 1 < len(tokens):
            idx += 2
            continue
        if tk in _GIT_GLOBAL_OPT_FLAG:
            idx += 1
            continue
        if tk.startswith("--") and "=" in tk:
            opt = tk.split("=", 1)[0]
            if opt in _GIT_GLOBAL_OPT_VALUE or opt in _GIT_GLOBAL_OPT_FLAG:
                idx += 1
                continue
        if tk.startswith("-"):
            idx += 1
            continue
        break
    if idx >= len(tokens) or tokens[idx] != "add":
        return None
    return tokens[idx + 1 :]


def _extract_git_add_args(segment: str) -> list[str]:
    """Return positional path args to `git add` (drops flag tokens)."""
    tail = _git_add_tail_tokens(segment)
    if tail is None:
        return []
    return [t for t in tail if not t.startswith("-")]


def _add_segment_is_wildcard(segment: str) -> bool:
    """Detect `git add` wildcard forms: -A, --all, -u, --update, ., or no positional args."""
    tail = _git_add_tail_tokens(segment)
    if tail is None:
        return False
    explicit_paths = [t for t in tail if not t.startswith("-")]
    if not explicit_paths:
        return True
    if any(t in ("-A", "--all", "-u", "--update", ".") for t in tail):
        return True
    return False


def _segment_git_dash_c(segment: str) -> str | None:
    """Return the directory argument from `git -C <dir>` if present."""
    return _segment_dash_c(segment)


def _segment_is_cd(segment: str) -> bool:
    """True when the segment's first non-empty token is `cd`."""
    stripped = segment.strip()
    if not stripped:
        return False
    return stripped == "cd" or stripped.startswith("cd ") or stripped.startswith("cd\t")


def _extract_cd_target(segment: str) -> str | None:
    """Extract the path argument to `cd`. Handles quoted paths and embedded spaces.

    Returns None when the segment cannot be parsed (e.g. unbalanced quotes) — caller
    should treat as unresolvable cwd and fail CLOSED.
    """
    tokens = _tokenize_segment(segment)
    if len(tokens) < 2 or tokens[0] != "cd":
        return None
    return tokens[1]


def _resolve_cwd_chain(segments: list[str], initial_cwd: Path) -> tuple[list[Path | None], Path | None]:
    """Compute per-segment effective cwd by tracking `cd <dir>` segments.

    Returns (per_segment_cwd, final_cwd). When a `cd` segment cannot be parsed
    or its target does not resolve to a directory, the corresponding entry is
    None and final_cwd is None — fail-CLOSED on unresolvable cwd. Closes
    Claude reviewer should_fix #1 (CD_RE didn't handle paths with spaces).
    """
    cwds: list[Path | None] = []
    cur: Path | None = initial_cwd
    for seg in segments:
        if _segment_is_cd(seg):
            target = _extract_cd_target(seg)
            if target is None:
                cur = None
                cwds.append(cur)
                continue
            new_cwd = (cur / target).resolve(strict=False) if cur is not None else Path(target).resolve(strict=False)
            cur = new_cwd if new_cwd.is_dir() else None
            cwds.append(cur)
        else:
            cwds.append(cur)
    return cwds, cur


def _git_run(args: list[str], cwd: Path, max_bytes: int = MAX_SCAN_BYTES) -> bytes | None:
    """Run a git command; return stdout up to max_bytes, or None on failure."""
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
        )
        if result.returncode != 0:
            return None
        return result.stdout[:max_bytes]
    except (OSError, subprocess.TimeoutExpired):
        return None


def _scan_staged_diff(repo_cwd: Path, tags: set[str]) -> list[Finding]:
    out = _git_run(["git", "diff", "--cached", "--no-color", "-U0"], repo_cwd)
    if not out:
        return []
    nul = out.find(b"\x00")
    if nul != -1:
        out = out[:nul]
    text = out.decode("utf-8", errors="replace")
    return _scan_and_filter(text, tags)


def _scan_staged_blobs(repo_cwd: Path, tags: set[str]) -> list[Finding]:
    """Enumerate staged paths and read each blob via `git show :<path>`. BOM-aware."""
    name_out = _git_run(["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"], repo_cwd)
    if not name_out:
        return []
    paths = [p.decode("utf-8", errors="replace") for p in name_out.split(b"\x00") if p]
    findings: list[Finding] = []
    total_bytes = 0
    for rel in paths:
        if total_bytes >= MAX_BLOB_TOTAL_BYTES:
            break
        remaining = MAX_BLOB_TOTAL_BYTES - total_bytes
        budget = min(MAX_SCAN_BYTES, remaining)
        blob = _git_run(["git", "show", f":{rel}"], repo_cwd, max_bytes=budget)
        if blob is None:
            continue
        total_bytes += len(blob)
        text = _decode_blob(blob)
        if not text:
            continue
        findings.extend(_scan_and_filter(text, tags))
    return findings


def _decode_blob(raw: bytes) -> str:
    """Decode bytes with BOM detection (mirrors _read_file_text)."""
    if not raw:
        return ""
    if raw.startswith(b"\xff\xfe"):
        return raw[2:].decode("utf-16-le", errors="replace")
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be", errors="replace")
    if raw.startswith(b"\xef\xbb\xbf"):
        body = raw[3:]
        nul = body.find(b"\x00")
        if nul != -1:
            body = body[:nul]
        return body.decode("utf-8", errors="replace")
    nul = raw.find(b"\x00")
    if nul != -1:
        raw = raw[:nul]
    return raw.decode("utf-8", errors="replace")


def _enumerate_working_tree_files(repo_cwd: Path) -> list[str]:
    """Enumerate files that `git add -A` / `-u` / `.` would stage.

    `-A` covers modified + untracked + deleted in the working tree. `--cached`
    is intentionally OMITTED — clean tracked files have no pending changes and
    would otherwise exhaust the 1 MB scan budget before the secret-bearing file
    is reached (Codex finding #3).
    """
    out = _git_run(
        ["git", "ls-files", "--modified", "--others", "--exclude-standard"],
        repo_cwd,
    )
    if out is None:
        return []
    return [line for line in out.decode("utf-8", errors="replace").splitlines() if line]


# ── Event handlers ────────────────────────────────────────────────────────────


def _handle_user_prompt_submit(data: dict) -> int:
    prompt = data.get("prompt") or ""
    if not isinstance(prompt, str) or not prompt:
        return 0
    tags = parse_allow_tags(prompt)
    try:
        with _regex_timeout():
            findings = _scan_and_filter(prompt, tags)
    except TimeoutError:
        return 0
    if not findings:
        return 0
    return _user_prompt_block(findings)


def _handle_pre_tool_use_read(data: dict) -> int:
    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""
    transcript_path = data.get("transcript_path") or ""
    tags = load_from_transcript(transcript_path) if transcript_path else set()
    return _scan_file_path(file_path, tags)


def _handle_pre_tool_use_bash(data: dict) -> int:
    tool_input = data.get("tool_input") or {}
    command = tool_input.get("command") or ""
    if not isinstance(command, str) or not command:
        return 0
    transcript_path = data.get("transcript_path") or ""
    tags = load_from_transcript(transcript_path) if transcript_path else set()
    initial_cwd = _initial_cwd(data)

    segments = _split_segments(command)
    if not segments:
        return 0
    seg_cwds, _ = _resolve_cwd_chain(segments, initial_cwd)

    # 1) Env-var scan
    for var_name in _extract_env_var_names(command):
        value = os.environ.get(var_name)
        if not value:
            continue
        findings = _scan_and_filter(value, tags)
        if findings:
            return _content_block(f"environment variable ${var_name}", findings)

    # 2) Command-text scan (raw command text — catches inline echo AKIA…)
    cmd_findings = _scan_and_filter(command, tags)
    if cmd_findings:
        return _content_block("bash command", cmd_findings)

    # 3) File-read commands (cat/head/tail/...)
    for seg, seg_cwd in zip(segments, seg_cwds):
        for raw_path in _extract_file_read_targets(seg):
            path = _resolve_path_in_cwd(raw_path, seg_cwd or initial_cwd)
            if path is None:
                continue
            ret = _scan_file_path(str(path), tags)
            if ret != 0:
                return ret

    # 4) Detect chains and git commit (Codex finding #2 — shlex-based detection
    # so global options like --no-pager don't bypass)
    has_commit = any(_segment_invokes(s, "commit") for s in segments)
    has_add = any(_segment_invokes(s, "add") for s in segments)

    if has_commit:
        # Determine the cwd of the commit segment
        commit_cwd = _commit_segment_cwd(segments, seg_cwds, initial_cwd)
        if commit_cwd is None:
            return _bash_unresolvable_repo()
        # Patch-text scan
        diff_findings = _scan_staged_diff(commit_cwd, tags)
        # Staged-blob scan (catches UTF-16 / binary blobs)
        blob_findings = _scan_staged_blobs(commit_cwd, tags)
        all_findings = diff_findings + blob_findings

        if has_add:
            chain_findings = _scan_chain_add_files(segments, seg_cwds, initial_cwd, tags)
            if chain_findings is None:
                return _bash_unresolvable_repo()
            all_findings.extend(chain_findings)

        all_findings = apply_allow_tags(all_findings, tags)
        if all_findings:
            return _content_block("staged commit", all_findings)

    return 0


def _initial_cwd(data: dict) -> Path:
    cwd = data.get("cwd")
    if isinstance(cwd, str) and cwd:
        return Path(cwd)
    return Path.cwd()


def _resolve_path_in_cwd(raw_path: str, cwd: Path) -> Path | None:
    p = Path(raw_path)
    if p.is_absolute():
        return p
    try:
        return (cwd / raw_path).resolve(strict=False)
    except OSError:
        return None


def _commit_segment_cwd(segments: list[str], seg_cwds: list[Path | None], initial_cwd: Path) -> Path | None:
    """Find the effective cwd of the first `git commit` segment."""
    for seg, cwd in zip(segments, seg_cwds):
        if not _segment_invokes(seg, "commit"):
            continue
        # If the segment uses `git -C <dir>`, that overrides the cwd.
        dash_c = _segment_git_dash_c(seg)
        if dash_c:
            target = Path(dash_c)
            if not target.is_absolute() and cwd is not None:
                target = (cwd / dash_c).resolve(strict=False)
            elif target.is_absolute():
                target = target.resolve(strict=False)
            else:
                target = (initial_cwd / dash_c).resolve(strict=False)
            return target if target.is_dir() else None
        return cwd
    return None


def _scan_chain_add_files(
    segments: list[str],
    seg_cwds: list[Path | None],
    initial_cwd: Path,
    tags: set[str],
) -> list[Finding] | None:
    """Scan files referenced by `git add` segments. Returns None on cwd failure."""
    findings: list[Finding] = []
    for seg, seg_cwd in zip(segments, seg_cwds):
        if not _segment_invokes(seg, "add"):
            continue
        dash_c = _segment_git_dash_c(seg)
        if dash_c:
            target = Path(dash_c)
            if not target.is_absolute() and seg_cwd is not None:
                target = (seg_cwd / dash_c).resolve(strict=False)
            elif target.is_absolute():
                target = target.resolve(strict=False)
            else:
                target = (initial_cwd / dash_c).resolve(strict=False)
            if not target.is_dir():
                return None
            effective_cwd = target
        else:
            effective_cwd = seg_cwd

        if effective_cwd is None:
            return None

        if _add_segment_is_wildcard(seg):
            # Enumerate files the add form will stage. `-A` and `.` cover
            # modified-and-new (NOT clean tracked files); we drop `--cached`
            # so clean tracked files can't exhaust the budget before reaching
            # the new modified secret-bearing file (Codex finding #3).
            files = _enumerate_working_tree_files(effective_cwd)
            findings.extend(_scan_files_under_budget(files, effective_cwd, tags))
        else:
            for raw_arg in _extract_git_add_args(seg):
                p_obj = Path(raw_arg)
                if not p_obj.is_absolute():
                    p_obj = (effective_cwd / raw_arg).resolve(strict=False)
                if not p_obj.exists():
                    continue
                if p_obj.is_file():
                    text = _read_file_text(p_obj)
                    if text:
                        findings.extend(_scan_and_filter(text, tags))
                elif p_obj.is_dir():
                    # Codex finding #1: `git add <dir>` stages every file under <dir>.
                    # Enumerate via git ls-files restricted to the directory pathspec.
                    rel_dir = _relative_path(p_obj, effective_cwd)
                    files_under_dir = _enumerate_pathspec_files(effective_cwd, rel_dir)
                    findings.extend(_scan_files_under_budget(files_under_dir, effective_cwd, tags))
    return findings


def _relative_path(target: Path, cwd: Path) -> str:
    """Return target relative to cwd; falls back to absolute if not relative."""
    try:
        return str(target.relative_to(cwd))
    except ValueError:
        return str(target)


def _scan_files_under_budget(rel_paths: list[str], base_cwd: Path, tags: set[str]) -> list[Finding]:
    """Scan a list of file paths (relative to base_cwd), within MAX_SCAN_BYTES total."""
    findings: list[Finding] = []
    total = 0
    for rel in rel_paths:
        if total >= MAX_SCAN_BYTES:
            break
        p = (base_cwd / rel).resolve(strict=False)
        if not p.is_file():
            continue
        text = _read_file_text(p, max_bytes=MAX_SCAN_BYTES - total)
        if not text:
            continue
        total += len(text.encode("utf-8", errors="replace"))
        findings.extend(_scan_and_filter(text, tags))
    return findings


def _enumerate_pathspec_files(repo_cwd: Path, pathspec: str) -> list[str]:
    """Enumerate working-tree files under a directory pathspec via git ls-files.

    Uses `--modified --others --exclude-standard` to capture both newly-added
    untracked files and modified-tracked files, restricted to the pathspec.
    """
    out = _git_run(
        ["git", "ls-files", "--modified", "--others", "--exclude-standard", "--", pathspec],
        repo_cwd,
    )
    if out is None:
        return []
    return [line for line in out.decode("utf-8", errors="replace").splitlines() if line]


def _handle_post_tool_use_bash(data: dict) -> int:
    tool_response = data.get("tool_response") or {}
    if not isinstance(tool_response, dict):
        return 0
    stdout_b = tool_response.get("stdout") or ""
    stderr_b = tool_response.get("stderr") or ""
    if not isinstance(stdout_b, str):
        stdout_b = ""
    if not isinstance(stderr_b, str):
        stderr_b = ""

    # Use UTF-8 BYTE length (not Python str/code-point length). Multi-byte chars
    # would otherwise undercount, allowing a secret at byte 1,048,577 to pass
    # the oversize check. Closes Claude reviewer should_fix #2.
    combined_byte_len = (
        len(stdout_b.encode("utf-8", errors="replace"))
        + 1  # the "\n" separator
        + len(stderr_b.encode("utf-8", errors="replace"))
    )

    transcript_path = data.get("transcript_path") or ""
    tags = load_from_transcript(transcript_path, for_post_tool_use=True) if transcript_path else set()

    # Scan the first MAX_SCAN_BYTES bytes of combined output. Slice by bytes,
    # not by characters, so the cap matches combined_byte_len.
    combined_bytes = (stdout_b + "\n" + stderr_b).encode("utf-8", errors="replace")[:MAX_SCAN_BYTES]
    combined = combined_bytes.decode("utf-8", errors="replace")
    try:
        with _regex_timeout():
            findings = _scan_and_filter(combined, tags)
    except TimeoutError:
        findings = []

    if findings:
        return _post_tool_use_findings_block(findings)

    # Fail-CLOSED on oversize output (Codex finding #1 / Claude must_fix #1).
    # Compare UTF-8 BYTE length, not character length, so multi-byte output
    # cannot undercount and slip past the budget guard.
    if combined_byte_len > MAX_SCAN_BYTES:
        if "all" in tags or "secret" in tags:
            return 0
        return _post_tool_use_oversize_block()

    return 0


# ── Main dispatch ─────────────────────────────────────────────────────────────


def _enabled() -> bool:
    return os.environ.get("PILOT_CREDENTIAL_SCANNER_ENABLED", "true").lower() != "false"


def run_credential_scanner() -> int:
    """Main entry — read stdin, dispatch on event, return exit code."""
    if not _enabled():
        return 0

    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not raw:
        return 0
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0
    if not isinstance(data, dict):
        return 0

    event = data.get("hook_event_name") or ""
    tool_name = data.get("tool_name") or ""

    if event == "UserPromptSubmit":
        return _handle_user_prompt_submit(data)

    if event == "PreToolUse":
        if tool_name == "Read":
            return _handle_pre_tool_use_read(data)
        if tool_name == "Bash":
            return _handle_pre_tool_use_bash(data)
        return 0

    if event == "PostToolUse":
        if tool_name == "Bash":
            return _handle_post_tool_use_bash(data)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(run_credential_scanner())
