"""Keep repository-owned agent instructions synchronized for both agents.

Repositories opt in by installing ``scripts/sync-agent-assets.mjs`` through
``/setup-rules`` or ``$setup-rules``.  The checker owns the synchronization
contract:

* ``AGENTS.md`` is the shared rule source and ``CLAUDE.md`` imports it.
* ``.agents/skills`` is canonical and ``.claude/skills`` is its managed mirror.

At SessionStart the bundled checker refreshes the enrolled repository's local
copy and converges drift.  PostToolUse runs the local checker immediately after
an agent changes a canonical asset.  Generated-side edits are never copied
back: the hook tells the agent which canonical path to edit instead.

Hook input is untrusted and best-effort.  Malformed payloads and repositories
without the opt-in checker are quiet no-ops.  Checker processes and the
cross-agent lock are bounded so an unrelated tool or broken repository cannot
stall the client indefinitely.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

_CHECKER_RELATIVE = Path("scripts") / "sync-agent-assets.mjs"
_BUNDLED_CHECKER_RELATIVE = Path("skills") / "setup-rules" / "scripts" / "sync-agent-assets.mjs"
_CANONICAL_SKILLS = Path(".agents") / "skills"
_MIRRORED_SKILLS = Path(".claude") / "skills"
_RUN_TIMEOUT_SECONDS = 8
_LOCK_WAIT_SECONDS = 3.0
_STALE_LOCK_SECONDS = 30.0
_PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$", re.MULTILINE)
_PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to:\s*(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class CheckerResult:
    """Bounded checker outcome used to build hook feedback."""

    ok: bool
    detail: str = ""


def _is_regular_file(candidate: Path) -> bool:
    try:
        return candidate.is_file() and not candidate.is_symlink()
    except OSError:
        return False


def _bundled_checker() -> Path | None:
    """Return Pilot's trusted bundled checker when installed with this hook."""
    candidate = Path(__file__).resolve().parent.parent / _BUNDLED_CHECKER_RELATIVE
    return candidate if _is_regular_file(candidate) else None


def _candidate_directory(value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        candidate = Path(value).expanduser().resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return None
    return candidate if candidate.is_dir() else candidate.parent


def _enrolled_repo_from(candidate: Path) -> Path | None:
    """Find the nearest enrolled repo without crossing a nested git boundary."""
    current = candidate
    while True:
        if _is_regular_file(current / _CHECKER_RELATIVE):
            return current
        if (current / ".git").exists():
            return None
        if current.parent == current:
            return None
        current = current.parent


def _input_base(payload: dict) -> Path:
    for value in (payload.get("cwd"), os.environ.get("CLAUDE_PROJECT_ROOT")):
        candidate = _candidate_directory(value)
        if candidate is not None:
            return candidate
    return Path.cwd().resolve(strict=False)


def _find_enrolled_repo(payload: dict, raw_paths: list[str]) -> Path | None:
    candidates: list[Path] = []
    base = _input_base(payload)
    candidates.append(base)

    for raw_path in raw_paths:
        try:
            path = Path(raw_path).expanduser()
            absolute = path if path.is_absolute() else base / path
            candidates.append(absolute.resolve(strict=False).parent)
        except (OSError, RuntimeError, ValueError):
            continue

    cwd = Path.cwd().resolve(strict=False)
    if cwd not in candidates:
        candidates.append(cwd)

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        repo = _enrolled_repo_from(candidate)
        if repo is not None:
            return repo
    return None


def _extract_changed_paths(payload: dict) -> list[str]:
    """Extract Claude file paths and Codex apply_patch paths."""
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_name, str) or not isinstance(tool_input, dict):
        return []

    normalized_tool = tool_name.rsplit(".", 1)[-1]
    if normalized_tool in {"Write", "Edit", "MultiEdit"}:
        file_path = tool_input.get("file_path")
        return [file_path] if isinstance(file_path, str) and file_path.strip() else []

    if normalized_tool != "apply_patch":
        return []
    command = tool_input.get("command")
    if not isinstance(command, str):
        return []
    return [*_PATCH_PATH_RE.findall(command), *_PATCH_MOVE_RE.findall(command)]


def _repo_relative_paths(repo: Path, payload: dict, raw_paths: list[str]) -> list[Path]:
    base = _input_base(payload)
    relative_paths: list[Path] = []
    for raw_path in raw_paths:
        try:
            candidate = Path(raw_path).expanduser()
            absolute = candidate if candidate.is_absolute() else base / candidate
            relative = absolute.resolve(strict=False).relative_to(repo.resolve(strict=False))
        except (OSError, RuntimeError, ValueError):
            continue
        if relative not in relative_paths:
            relative_paths.append(relative)
    return relative_paths


def _is_within(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _is_managed_mirror(repo: Path, path: Path) -> bool:
    """Return whether a Claude skill path has a canonical project skill."""
    try:
        suffix = path.relative_to(_MIRRORED_SKILLS)
    except ValueError:
        return False
    if not suffix.parts:
        return False
    canonical_skill = repo / _CANONICAL_SKILLS / suffix.parts[0]
    try:
        return canonical_skill.is_dir() and not canonical_skill.is_symlink()
    except OSError:
        return False


def _generated_edit_message(paths: list[Path]) -> str:
    mappings: list[str] = []
    for path in paths:
        if path == Path("CLAUDE.md"):
            mappings.append("CLAUDE.md -> AGENTS.md")
            continue
        try:
            suffix = path.relative_to(_MIRRORED_SKILLS)
        except ValueError:
            continue
        mappings.append(f"{path.as_posix()} -> {(_CANONICAL_SKILLS / suffix).as_posix()}")

    shown = ", ".join(mappings[:3])
    if len(mappings) > 3:
        shown += f", and {len(mappings) - 3} more"
    return (
        "Move this generated agent edit to the canonical source "
        f"({shown}), then edit only AGENTS.md or .agents/skills; the hook will regenerate Claude's mirror."
    )


def _canonical_raw_path(repo: Path, payload: dict, raw_path: str) -> str | None:
    """Map one generated mirror path to its canonical spelling for the tool."""
    base = _input_base(payload)
    try:
        candidate = Path(raw_path).expanduser()
        absolute = candidate if candidate.is_absolute() else base / candidate
        relative = absolute.resolve(strict=False).relative_to(repo.resolve(strict=False))
        suffix = relative.relative_to(_MIRRORED_SKILLS)
    except (OSError, RuntimeError, ValueError):
        return None

    target = repo / _CANONICAL_SKILLS / suffix
    if candidate.is_absolute():
        return str(target)
    try:
        return Path(os.path.relpath(target, base)).as_posix()
    except (OSError, ValueError):
        return None


def _rewrite_apply_patch(repo: Path, payload: dict, command: str) -> str:
    marker = re.compile(
        r"^(\*\*\* (?:Add|Update|Delete) File:\s*)(.+?)(\s*)$|"
        r"^(\*\*\* Move to:\s*)(.+?)(\s*)$",
        re.MULTILINE,
    )

    def replace(match: re.Match[str]) -> str:
        prefix = match.group(1) or match.group(4)
        raw_path = match.group(2) or match.group(5)
        trailing = match.group(3) if match.group(1) else match.group(6)
        rewritten = _canonical_raw_path(repo, payload, raw_path)
        return f"{prefix}{rewritten or raw_path}{trailing or ''}"

    return marker.sub(replace, command)


def _pre_tool_payload(message: str, decision: str, updated_input: dict | None = None) -> dict:
    output: dict = {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
    }
    if decision == "deny":
        output["permissionDecisionReason"] = message
    if updated_input is not None:
        output["updatedInput"] = updated_input
        output["additionalContext"] = message
    return {"systemMessage": message, "hookSpecificOutput": output}


def _short_detail(completed: subprocess.CompletedProcess[str]) -> str:
    detail = (completed.stderr or "").strip() or (completed.stdout or "").strip()
    if not detail:
        return f"checker exited with status {completed.returncode}"
    compact = " ".join(detail.split())
    return compact if len(compact) <= 700 else f"{compact[:697]}..."


def _run_checker(checker: Path, mode: str, repo: Path) -> CheckerResult:
    node = shutil.which("node")
    if node is None:
        return CheckerResult(False, "Node.js is unavailable; install Node.js and restart the agent session")
    try:
        completed = subprocess.run(
            [node, str(checker), f"--{mode}", "--repo", str(repo)],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=_RUN_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return CheckerResult(False, f"checker timed out after {_RUN_TIMEOUT_SECONDS} seconds")
    except (OSError, ValueError) as error:
        return CheckerResult(False, f"checker could not start: {error}")
    if completed.returncode != 0:
        return CheckerResult(False, _short_detail(completed))
    return CheckerResult(True)


def _lock_path(repo: Path) -> Path:
    digest = hashlib.sha256(str(repo.resolve(strict=False)).encode()).hexdigest()[:20]
    return Path(tempfile.gettempdir()) / f"pilot-repo-agent-sync-{digest}.lock"


@contextmanager
def _repo_lock(repo: Path) -> Iterator[bool]:
    """Serialize simultaneous Claude/Codex syncs without leaving repo files."""
    lock = _lock_path(repo)
    deadline = time.monotonic() + _LOCK_WAIT_SECONDS
    acquired = False
    while time.monotonic() < deadline:
        try:
            lock.mkdir(mode=0o700)
            acquired = True
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > _STALE_LOCK_SECONDS:
                    lock.rmdir()
                    continue
            except (FileNotFoundError, OSError):
                pass
            time.sleep(0.05)
        except OSError:
            break
    try:
        yield acquired
    finally:
        if acquired:
            try:
                lock.rmdir()
            except OSError:
                pass


def _payload(message: str = "", event: str = "", *, block: bool = False) -> dict:
    if not message:
        return {"continue": True}

    result: dict = {"systemMessage": message}
    if block:
        result.update({"decision": "block", "reason": message})
    else:
        result["continue"] = True
    if event in {"SessionStart", "PostToolUse"}:
        result["hookSpecificOutput"] = {
            "hookEventName": event,
            "additionalContext": message,
        }
    return result


def _same_contents(left: Path, right: Path) -> bool:
    try:
        return left.read_bytes() == right.read_bytes()
    except OSError:
        return False


def _session_start(repo: Path) -> dict:
    local_checker = repo / _CHECKER_RELATIVE
    bundled = _bundled_checker()
    checker = bundled or local_checker
    needs_install = bundled is not None and not _same_contents(bundled, local_checker)
    with _repo_lock(repo) as acquired:
        if not acquired:
            return _payload(
                "Pilot agent sync skipped because another synchronization did not finish in time.",
                "SessionStart",
            )
        if not needs_install:
            check = _run_checker(checker, "check", repo)
            if check.ok:
                return _payload()
        mode = "install" if bundled is not None else "write"
        result = _run_checker(checker, mode, repo)
    if not result.ok:
        return _payload(f"Pilot could not synchronize repository agent assets: {result.detail}", "SessionStart")
    action = "refreshed and synchronized" if mode == "install" else "synchronized"
    return _payload(f"Pilot {action} this repository's shared agent rules and skills.", "SessionStart")


def _pre_tool_use(repo: Path, payload: dict, raw_paths: list[str]) -> dict:
    relative_paths = _repo_relative_paths(repo, payload, raw_paths)
    if Path("CLAUDE.md") in relative_paths:
        return _pre_tool_payload(
            "CLAUDE.md is generated and must remain exactly @AGENTS.md. Apply the rule change to AGENTS.md instead.",
            "deny",
        )

    mirrored = [path for path in relative_paths if _is_managed_mirror(repo, path)]
    if not mirrored:
        return _payload()

    tool_input = payload.get("tool_input")
    tool_name = payload.get("tool_name")
    if not isinstance(tool_input, dict) or not isinstance(tool_name, str):
        return _payload()
    updated_input = dict(tool_input)
    normalized_tool = tool_name.rsplit(".", 1)[-1]
    if normalized_tool in {"Write", "Edit", "MultiEdit"}:
        file_path = tool_input.get("file_path")
        if not isinstance(file_path, str):
            return _payload()
        rewritten = _canonical_raw_path(repo, payload, file_path)
        if rewritten is None:
            return _payload()
        updated_input["file_path"] = rewritten
    elif normalized_tool == "apply_patch":
        command = tool_input.get("command")
        if not isinstance(command, str):
            return _payload()
        updated_input["command"] = _rewrite_apply_patch(repo, payload, command)
    else:
        return _payload()

    return _pre_tool_payload(
        "Pilot redirected this Claude skill mirror edit to its canonical .agents/skills path.",
        "allow",
        updated_input,
    )


def _post_tool_use(repo: Path, payload: dict, raw_paths: list[str]) -> dict:
    relative_paths = _repo_relative_paths(repo, payload, raw_paths)
    generated = [
        path for path in relative_paths if path == Path("CLAUDE.md") or _is_managed_mirror(repo, path)
    ]
    if generated:
        with _repo_lock(repo) as acquired:
            if not acquired:
                return _payload(
                    f"Pilot could not restore this generated edit because another sync is still running. "
                    f"{_generated_edit_message(generated)}",
                    "PostToolUse",
                    block=True,
                )
            result = _run_checker(repo / _CHECKER_RELATIVE, "write", repo)
        if not result.ok:
            return _payload(
                f"Pilot could not restore this generated edit: {result.detail}. "
                f"{_generated_edit_message(generated)}",
                "PostToolUse",
                block=True,
            )
        return _payload(
            f"Pilot restored this generated edit from canonical state. {_generated_edit_message(generated)}",
            "PostToolUse",
            block=True,
        )

    canonical = [
        path for path in relative_paths if path == Path("AGENTS.md") or _is_within(path, _CANONICAL_SKILLS)
    ]
    if not canonical:
        return _payload()

    with _repo_lock(repo) as acquired:
        if not acquired:
            return _payload(
                "Pilot could not synchronize this canonical agent edit because another sync is still running. "
                "Run node scripts/sync-agent-assets.mjs --write before continuing.",
                "PostToolUse",
                block=True,
            )
        result = _run_checker(repo / _CHECKER_RELATIVE, "write", repo)
    if not result.ok:
        return _payload(
            f"Pilot could not synchronize this canonical agent edit: {result.detail}. "
            "Fix the reported issue and run node scripts/sync-agent-assets.mjs --write.",
            "PostToolUse",
            block=True,
        )
    return _payload("Pilot synchronized this repository's shared agent rules and skills.", "PostToolUse")


def handle(payload: object) -> dict:
    """Handle one hook payload and always return a valid fail-open response."""
    if not isinstance(payload, dict):
        return _payload()
    event = payload.get("hook_event_name")
    if event == "SessionStart":
        repo = _find_enrolled_repo(payload, [])
        return _session_start(repo) if repo is not None else _payload()
    if event not in {"PreToolUse", "PostToolUse"}:
        return _payload()

    raw_paths = _extract_changed_paths(payload)
    if not raw_paths:
        return _payload()
    repo = _find_enrolled_repo(payload, raw_paths)
    if repo is None:
        return _payload()
    if event == "PreToolUse":
        return _pre_tool_use(repo, payload, raw_paths)
    return _post_tool_use(repo, payload, raw_paths)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        result = handle(payload)
    except Exception:
        # Hook input and project state are untrusted. Never strand an agent
        # session because a best-effort synchronization hook could not parse it.
        result = _payload()
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
