"""Keep repository-owned agent instructions synchronized for both agents.

Repositories opt in by installing ``scripts/sync-agent-assets.mjs`` through
``/setup-rules`` or ``$setup-rules``.  That repository file is only an
enrollment marker and update target; the global hook executes exclusively the
trusted checker bundled with Pilot.  The checker owns this synchronization
contract:

* ``AGENTS.md`` is the shared rule source and ``CLAUDE.md`` imports it.
* ``.agents/skills`` is canonical and ``.claude/skills`` is its managed mirror.

At SessionStart the bundled checker refreshes the enrolled repository's local
copy and converges drift.  PreToolUse redirects managed mirror edits to their
canonical paths, while PostToolUse synchronizes canonical changes immediately.
Stop performs the same convergence as a backstop for clients or modes that do
not emit edit hooks, including Codex Code Mode.

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
_OWNERSHIP_MANIFEST = ".pilot-sync-manifest.json"
_RUN_TIMEOUT_SECONDS = 8
_LOCK_WAIT_SECONDS = 3.0
_STALE_LOCK_SECONDS = 30.0
_GIT_DIRECTION_CALLS = 2
_SESSION_STOP_WORST_CASE_SECONDS = _LOCK_WAIT_SECONDS + _RUN_TIMEOUT_SECONDS * (2 + _GIT_DIRECTION_CALLS)
_POST_TOOL_WORST_CASE_SECONDS = _LOCK_WAIT_SECONDS + _RUN_TIMEOUT_SECONDS
_PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$", re.MULTILINE)
_PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to:\s*(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class CheckerResult:
    """Bounded checker outcome used to build hook feedback."""

    ok: bool
    detail: str = ""


@dataclass(frozen=True)
class DirectionEvidence:
    """Trusted Git and session evidence for choosing a safe sync direction."""

    canonical_changes: tuple[str, ...] = ()
    mirror_risks: tuple[str, ...] = ()
    ambiguous_changes: tuple[str, ...] = ()
    error: str = ""


def _is_regular_file(candidate: Path) -> bool:
    try:
        return candidate.is_file() and not candidate.is_symlink()
    except OSError:
        return False


def _bundled_checker() -> Path | None:
    """Return Pilot's trusted bundled checker when installed with this hook."""
    candidate = Path(__file__).resolve().parent.parent / _BUNDLED_CHECKER_RELATIVE
    return candidate if _is_regular_file(candidate) else None


def _session_identity(payload: dict) -> str:
    values = (
        payload.get("session_id"),
        os.environ.get("CLAUDE_CODE_SESSION_ID"),
        os.environ.get("CODEX_THREAD_ID"),
        os.environ.get("PILOT_SESSION_ID"),
        payload.get("transcript_path"),
    )
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown-session"


def _baseline_path(repo: Path, payload: dict) -> Path:
    identity = f"{_session_identity(payload)}\0{repo.resolve(strict=False)}"
    digest = hashlib.sha256(identity.encode()).hexdigest()
    return Path(tempfile.gettempdir()) / "pilot-repo-agent-sync-baselines" / f"{digest}.json"


def _local_only_skill_names(repo: Path) -> set[str]:
    mirror_root = repo / _MIRRORED_SKILLS
    canonical_root = repo / _CANONICAL_SKILLS
    try:
        entries = list(mirror_root.iterdir())
    except (FileNotFoundError, NotADirectoryError, OSError):
        return set()
    names: set[str] = set()
    for entry in entries:
        if entry.name.startswith("."):
            continue
        try:
            if entry.is_dir() and not entry.is_symlink() and not (canonical_root / entry.name).exists():
                names.add(entry.name)
        except OSError:
            continue
    return names


def _record_session_baseline(repo: Path, payload: dict) -> tuple[set[str] | None, str]:
    """Persist initial local-only skill names outside the untrusted repository."""
    baseline = _baseline_path(repo, payload)
    try:
        baseline.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        data = {"version": 1, "local_only_skills": sorted(_local_only_skill_names(repo))}
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        try:
            descriptor = os.open(baseline, flags, 0o600)
        except FileExistsError:
            return _load_session_baseline(repo, payload)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, sort_keys=True)
            stream.write("\n")
        return set(data["local_only_skills"]), ""
    except (OSError, TypeError, ValueError) as error:
        return None, f"could not record the trusted session baseline: {error}"


def _load_session_baseline(repo: Path, payload: dict) -> tuple[set[str] | None, str]:
    baseline = _baseline_path(repo, payload)
    if not _is_regular_file(baseline):
        return None, "trusted SessionStart baseline is missing or not a regular file"
    try:
        data = json.loads(baseline.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return None, f"trusted SessionStart baseline is unreadable: {error}"
    skills = data.get("local_only_skills") if isinstance(data, dict) and data.get("version") == 1 else None
    if not isinstance(skills, list) or not all(isinstance(name, str) and name for name in skills):
        return None, "trusted SessionStart baseline has an invalid schema"
    return set(skills), ""


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


def _should_redirect_mirror(repo: Path, path: Path) -> bool:
    """Redirect managed skills and brand-new mirror skill directories."""
    try:
        suffix = path.relative_to(_MIRRORED_SKILLS)
    except ValueError:
        return False
    if not suffix.parts:
        return False
    skill_name = suffix.parts[0]
    canonical_skill = repo / _CANONICAL_SKILLS / skill_name
    mirror_skill = repo / _MIRRORED_SKILLS / skill_name
    try:
        if canonical_skill.is_dir() and not canonical_skill.is_symlink():
            return True
        return not mirror_skill.exists()
    except OSError:
        return False


def _is_managed_mirror(repo: Path, path: Path) -> bool:
    """Return whether a mirror path belongs to a canonical project skill."""
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


def _git_status_entries(repo: Path) -> tuple[dict[str, set[str]] | None, str]:
    """Return non-ignored skill paths with porcelain status codes."""
    try:
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "status",
                "--porcelain=v1",
                "-z",
                "--untracked-files=all",
                "--",
                _CANONICAL_SKILLS.as_posix(),
                _MIRRORED_SKILLS.as_posix(),
            ],
            capture_output=True,
            timeout=_RUN_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, f"git status timed out after {_RUN_TIMEOUT_SECONDS} seconds"
    except (OSError, ValueError) as error:
        return None, f"git status could not start: {error}"
    if completed.returncode != 0:
        detail = completed.stderr.decode(errors="replace").strip()
        return None, detail or f"git status exited with status {completed.returncode}"

    fields = completed.stdout.split(b"\0")
    changed: dict[str, set[str]] = {}
    index = 0
    while index < len(fields):
        record = fields[index]
        index += 1
        if not record:
            continue
        if len(record) < 4:
            return None, "git status returned a malformed porcelain record"
        status = record[:2].decode(errors="replace")
        changed.setdefault(os.fsdecode(record[3:]), set()).add(status)
        if "R" in status or "C" in status:
            if index >= len(fields) or not fields[index]:
                return None, "git status returned an incomplete rename record"
            changed.setdefault(os.fsdecode(fields[index]), set()).add(status)
            index += 1
    return changed, ""


def _git_tracked_mirror_paths(repo: Path) -> tuple[set[str] | None, str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-z", "--", _MIRRORED_SKILLS.as_posix()],
            capture_output=True,
            timeout=_RUN_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, f"git ls-files timed out after {_RUN_TIMEOUT_SECONDS} seconds"
    except (OSError, ValueError) as error:
        return None, f"git ls-files could not start: {error}"
    if completed.returncode != 0:
        detail = completed.stderr.decode(errors="replace").strip()
        return None, detail or f"git ls-files exited with status {completed.returncode}"
    return {os.fsdecode(path) for path in completed.stdout.split(b"\0") if path}, ""


def _changed_skill_relatives(paths: set[str], root: Path) -> set[str]:
    prefix = f"{root.as_posix()}/"
    relatives = {path[len(prefix) :] for path in paths if path.startswith(prefix) and len(path) > len(prefix)}
    if root == _MIRRORED_SKILLS:
        relatives.discard(_OWNERSHIP_MANIFEST)
    return relatives


def _direction_evidence(repo: Path, baseline_local_only: set[str]) -> DirectionEvidence:
    changed, error = _git_status_entries(repo)
    if changed is None:
        return DirectionEvidence(error=error)
    tracked_mirror, error = _git_tracked_mirror_paths(repo)
    if tracked_mirror is None:
        return DirectionEvidence(error=error)

    canonical = _changed_skill_relatives(set(changed), _CANONICAL_SKILLS)
    mirror = _changed_skill_relatives(set(changed), _MIRRORED_SKILLS)
    mirror_changes: set[str] = set()
    for relative in mirror:
        full_path = (_MIRRORED_SKILLS / relative).as_posix()
        statuses = changed.get(full_path, set())
        skill_name = relative.split("/", 1)[0]
        if statuses == {"??"} and skill_name in baseline_local_only:
            continue
        mirror_changes.add(relative)

    prefix = f"{_MIRRORED_SKILLS.as_posix()}/"
    clean_tracked_mirror_only = {
        path[len(prefix) :]
        for path in tracked_mirror
        if path.startswith(prefix)
        and path != f"{prefix}{_OWNERSHIP_MANIFEST}"
        and not (repo / _CANONICAL_SKILLS / path[len(prefix) :].split("/", 1)[0]).exists()
    }
    return DirectionEvidence(
        canonical_changes=tuple(sorted(canonical)),
        mirror_risks=tuple(sorted((mirror_changes - canonical) | clean_tracked_mirror_only)),
        ambiguous_changes=tuple(sorted(mirror_changes & canonical)),
    )


def _mirror_risk_message(risks: tuple[str, ...]) -> str:
    mappings = [
        f"{(_MIRRORED_SKILLS / relative).as_posix()} -> {(_CANONICAL_SKILLS / relative).as_posix()}"
        for relative in risks
    ]
    shown = ", ".join(mappings[:3])
    if len(mappings) > 3:
        shown += f", and {len(mappings) - 3} more"
    return f"Preserved mirror-side work; move or merge it into the canonical path ({shown})."


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


def _session_start(repo: Path, payload: dict) -> dict:
    local_checker = repo / _CHECKER_RELATIVE
    baseline_local_only, baseline_error = _record_session_baseline(repo, payload)
    if baseline_local_only is None:
        return _payload(
            f"Pilot preserved repository agent assets because {baseline_error}.",
            "SessionStart",
        )
    bundled = _bundled_checker()
    if bundled is None:
        return _payload(
            "Pilot found repository agent sync enrollment, but its trusted bundled checker is unavailable. "
            "Reinstall or update Pilot Shell; the repository-local checker was not executed.",
            "SessionStart",
        )
    needs_install = not _same_contents(bundled, local_checker)
    with _repo_lock(repo) as acquired:
        if not acquired:
            return _payload(
                "Pilot agent sync skipped because another synchronization did not finish in time.",
                "SessionStart",
            )
        check = _run_checker(bundled, "check", repo)
        evidence = _direction_evidence(repo, baseline_local_only)
        if evidence.error:
            return _payload(
                "Pilot preserved repository agent assets because the safe sync direction could not be proven: "
                f"{evidence.error}. Resolve the Git status error, then restart the session.",
                "SessionStart",
            )
        if evidence.mirror_risks:
            return _payload(
                f"Pilot did not synchronize to avoid overwriting repository agent work. "
                f"{_mirror_risk_message(evidence.mirror_risks)}",
                "SessionStart",
            )
        if not check.ok and evidence.ambiguous_changes:
            return _payload(
                f"Pilot did not synchronize because canonical and mirror changes are ambiguous. "
                f"{_mirror_risk_message(evidence.ambiguous_changes)}",
                "SessionStart",
            )
        if check.ok and not needs_install:
            return _payload()
        if not check.ok and not evidence.canonical_changes:
            return _payload(
                f"Pilot did not auto-repair repository agent assets because canonical-only drift was not proven: "
                f"{check.detail}. Run setup-rules to review the preserved state.",
                "SessionStart",
            )
        result = _run_checker(bundled, "install", repo)
    if not result.ok:
        return _payload(f"Pilot could not synchronize repository agent assets: {result.detail}", "SessionStart")
    return _payload("Pilot refreshed and synchronized this repository's shared agent rules and skills.", "SessionStart")


def _pre_tool_use(repo: Path, payload: dict, raw_paths: list[str]) -> dict:
    relative_paths = _repo_relative_paths(repo, payload, raw_paths)
    if Path("CLAUDE.md") in relative_paths:
        return _pre_tool_payload(
            "CLAUDE.md is generated and must remain exactly @AGENTS.md. Apply the rule change to AGENTS.md instead.",
            "deny",
        )

    mirrored = [path for path in relative_paths if _should_redirect_mirror(repo, path)]
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
    generated = [path for path in relative_paths if path == Path("CLAUDE.md") or _is_managed_mirror(repo, path)]
    if generated:
        return _payload(
            f"Pilot preserved this generated-side edit. {_generated_edit_message(generated)}",
            "PostToolUse",
            block=True,
        )

    canonical = [path for path in relative_paths if path == Path("AGENTS.md") or _is_within(path, _CANONICAL_SKILLS)]
    if not canonical:
        return _payload()

    bundled = _bundled_checker()
    if bundled is None:
        return _payload(
            "Pilot could not synchronize this canonical agent edit because its trusted bundled checker is "
            "unavailable. Reinstall or update Pilot Shell; the repository-local checker was not executed.",
            "PostToolUse",
            block=True,
        )
    with _repo_lock(repo) as acquired:
        if not acquired:
            return _payload(
                "Pilot could not synchronize this canonical agent edit because another sync is still running. "
                "Wait for it to finish, then retry the canonical edit.",
                "PostToolUse",
                block=True,
            )
        result = _run_checker(bundled, "write", repo)
    if not result.ok:
        return _payload(
            f"Pilot could not synchronize this canonical agent edit: {result.detail}. "
            "Fix the reported issue, then retry the edit or restart the session.",
            "PostToolUse",
            block=True,
        )
    return _payload("Pilot synchronized this repository's shared agent rules and skills.", "PostToolUse")


def _stop(repo: Path, payload: dict) -> dict:
    """Converge an enrolled repo when a client emitted no edit lifecycle hook."""
    baseline_local_only, baseline_error = _load_session_baseline(repo, payload)
    if baseline_local_only is None:
        return _payload(
            f"Pilot cannot safely finish repository agent synchronization because {baseline_error}.",
            "Stop",
            block=True,
        )
    bundled = _bundled_checker()
    if bundled is None:
        return _payload(
            "Pilot cannot verify repository agent assets because its trusted bundled checker is unavailable. "
            "Reinstall or update Pilot Shell; the repository-local checker was not executed.",
            "Stop",
            block=True,
        )
    with _repo_lock(repo) as acquired:
        if not acquired:
            return _payload(
                "Pilot could not verify repository agent assets because another sync is still running. "
                "Wait for it to finish, then finish again.",
                "Stop",
                block=True,
            )
        check = _run_checker(bundled, "check", repo)
        evidence = _direction_evidence(repo, baseline_local_only)
        if evidence.error:
            return _payload(
                f"Pilot cannot safely finish repository agent synchronization because Git status failed: "
                f"{evidence.error}.",
                "Stop",
                block=True,
            )
        if evidence.mirror_risks:
            return _payload(
                f"Pilot preserved repository agent work instead of overwriting it. "
                f"{_mirror_risk_message(evidence.mirror_risks)}",
                "Stop",
                block=True,
            )
        if not check.ok and evidence.ambiguous_changes:
            return _payload(
                f"Pilot preserved both canonical and mirror changes because their direction is ambiguous. "
                f"{_mirror_risk_message(evidence.ambiguous_changes)}",
                "Stop",
                block=True,
            )
        if check.ok:
            return _payload()
        if not evidence.canonical_changes:
            return _payload(
                f"Pilot cannot auto-repair repository agent assets because canonical-only drift was not proven: "
                f"{check.detail}. Run setup-rules to review the preserved state.",
                "Stop",
                block=True,
            )
        result = _run_checker(bundled, "write", repo)
    if not result.ok:
        return _payload(
            f"Pilot could not synchronize repository agent assets before completion: {result.detail}. "
            "Fix the reported issue, then finish again or restart the session.",
            "Stop",
            block=True,
        )
    return _payload()


def handle(payload: object) -> dict:
    """Handle one hook payload and always return a valid fail-open response."""
    if not isinstance(payload, dict):
        return _payload()
    event = payload.get("hook_event_name")
    if event == "SessionStart":
        repo = _find_enrolled_repo(payload, [])
        return _session_start(repo, payload) if repo is not None else _payload()
    if event == "Stop":
        repo = _find_enrolled_repo(payload, [])
        return _stop(repo, payload) if repo is not None else _payload()
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
