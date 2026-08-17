"""Fail-safe isolation of globally-installed rules and skills.

Without this module, benchmarks are silently contaminated: files in the active
Claude config dir's `rules/` and `skills/` (`$CLAUDE_CONFIG_DIR`, else
`~/.claude`) load in every `claude -p` subprocess regardless of cwd, so if the
user has the target rule/skill installed globally, the `without` config still
has it and the benchmark measures nothing.
For Codex skill benchmarks, `~/.agents/skills/` is isolated the same way.

Layered protection — each layer catches what the previous can't:

1. **Crash-proof on-disk manifest** (`~/.pilot/bench-recovery/hidden-<pid>.json`)
   — written atomically BEFORE any rename. Survives SIGKILL, power loss,
   segfaults. Scanned at every runner startup by `recover_stale_manifests()`.
2. **atexit handler** — restores paths still in the in-memory queue when the
   interpreter shuts down (including via unhandled exception / SystemExit).
3. **Signal handlers** — SIGINT / SIGTERM / SIGHUP route through restore-then-exit.
4. **try/finally in the context manager** — restores on normal exit.
"""

from __future__ import annotations

import atexit
import contextlib
import json
import os
import signal
import sys
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

from scripts.utils import TargetConfig

HIDDEN_SUFFIX = ".pilot-bench-hidden"
RECREATED_SUFFIX = ".pilot-bench-recreated"
RECOVERY_DIR = Path.home() / ".pilot" / "bench-recovery"
HIDDEN_RESTORE_QUEUE: list[tuple[Path, Path]] = []

SIGNALS_TO_HANDLE: tuple[int, ...] = tuple(
    sig
    for sig in (
        getattr(signal, "SIGINT", None),
        getattr(signal, "SIGTERM", None),
        getattr(signal, "SIGHUP", None),
    )
    if sig is not None
)


def _manifest_path(pid: int) -> Path:
    return RECOVERY_DIR / f"hidden-{pid}.json"


def _write_manifest(pairs: list[tuple[Path, Path]]) -> None:
    """Atomically record (src → hidden) pairs for the current PID."""
    RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
    path = _manifest_path(os.getpid())
    payload: dict[str, object] = {
        "pid": os.getpid(),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pairs": [[str(src), str(hidden)] for src, hidden in pairs],
    }
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.rename(path)


def _clear_manifest() -> None:
    _manifest_path(os.getpid()).unlink(missing_ok=True)


def _process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _recreated_backup_path(src: Path) -> Path:
    """Return a collision-free path for content recreated during isolation."""
    base = src.with_name(f"{src.name}{RECREATED_SUFFIX}-{os.getpid()}")
    candidate = base
    counter = 2
    while candidate.exists():
        candidate = base.with_name(f"{base.name}-{counter}")
        counter += 1
    return candidate


def _restore_hidden_path(src: Path, hidden: Path) -> Path | None:
    """Restore one hidden path, preserving a concurrently recreated source."""
    if not hidden.exists():
        return None
    if not src.exists():
        hidden.rename(src)
        return None

    backup = _recreated_backup_path(src)
    src.rename(backup)
    try:
        hidden.rename(src)
    except OSError:
        with contextlib.suppress(OSError):
            backup.rename(src)
        raise
    print(
        f"  ⚠  {src} was recreated during isolation; restored the original and preserved "
        f"the concurrent copy at {backup}",
        file=sys.stderr,
    )
    return backup


def recover_stale_manifests() -> int:
    """Restore paths from any manifest belonging to a dead PID. Returns count."""
    if not RECOVERY_DIR.exists():
        return 0
    restored = 0
    for manifest in sorted(RECOVERY_DIR.glob("hidden-*.json")):
        try:
            data = json.loads(manifest.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        pid = data.get("pid", 0)
        if _process_alive(pid):
            continue
        pairs = data.get("pairs", [])
        if not isinstance(pairs, list):
            manifest.unlink(missing_ok=True)
            continue
        failures = False
        for pair in pairs:
            if not (isinstance(pair, list) and len(pair) == 2):
                continue
            src = Path(str(pair[0]))
            hidden = Path(str(pair[1]))
            if hidden.exists():
                try:
                    _restore_hidden_path(src, hidden)
                    restored += 1
                    print(f"  🛠  recovered hidden file from prior crash: {src}", file=sys.stderr)
                except OSError as err:
                    failures = True
                    print(f"  ⚠  failed to recover {src} from {hidden}: {err}", file=sys.stderr)
        if not failures:
            manifest.unlink(missing_ok=True)
    return restored


def _restore_hidden_paths() -> None:
    """Belt-and-braces restore for anything left in HIDDEN_RESTORE_QUEUE."""
    failures: list[tuple[Path, Path]] = []
    while HIDDEN_RESTORE_QUEUE:
        src, hidden = HIDDEN_RESTORE_QUEUE.pop()
        try:
            _restore_hidden_path(src, hidden)
        except OSError as err:
            failures.append((src, hidden))
            print(f"  ⚠  failed to restore {src} from {hidden}: {err}", file=sys.stderr)
    HIDDEN_RESTORE_QUEUE.extend(failures)
    if not failures:
        with contextlib.suppress(OSError):
            _clear_manifest()


def install_signal_handlers() -> None:
    """Route SIGINT/SIGTERM/SIGHUP through the restore path before exit.

    SIGKILL is uncatchable; the on-disk manifest is the safety net for that case.
    """

    def _handle(signum: int, frame: object) -> None:
        _ = frame
        _restore_hidden_paths()
        sys.exit(128 + signum)

    for sig in SIGNALS_TO_HANDLE:
        try:
            signal.signal(sig, _handle)
        except (OSError, ValueError):
            # SIGHUP etc. may be missing (Windows) or blocked (embedded shells).
            pass


atexit.register(_restore_hidden_paths)


def detect_global_contamination(target: TargetConfig, agent: str = "claude") -> list[Path]:
    """Return global paths that duplicate the target's rule/skill."""
    target_type = target.get("type", "skill")
    raw_path = target.get("path")
    if not raw_path:
        return []
    source_path = Path(raw_path).expanduser().resolve()
    if not source_path.exists():
        return []

    def _same_path(a: Path, b: Path) -> bool:
        try:
            return a.resolve() == b.resolve()
        except OSError:
            return False

    # Codex composes project AGENTS.md with ~/.codex/AGENTS.md. Leaving the
    # global file or globally discovered agent skills installed contaminates
    # both halves of a rules A/B benchmark, so hide both with the same
    # crash-safe mechanism used for a targeted skill benchmark.
    if agent == "codex" and target_type == "rules":
        global_rules = Path.home() / ".codex" / "AGENTS.md"
        global_skills = Path.home() / ".agents" / "skills"
        suspects: list[Path] = []
        if global_rules.is_file() and not _same_path(global_rules, source_path):
            suspects.append(global_rules)
        if global_skills.is_dir() and not _same_path(global_skills, source_path):
            suspects.append(global_skills)
        return suspects

    # Honour CLAUDE_CONFIG_DIR: isolation MOVES these files aside for the run, so
    # resolving the wrong profile would relocate another profile's real assets.
    # ~/.agents has no equivalent override (Codex derives it from $HOME).
    if agent == "codex":
        global_config_dir = Path.home() / ".agents"
    else:
        env_dir = os.environ.get("CLAUDE_CONFIG_DIR")
        global_config_dir = Path(env_dir) if env_dir and Path(env_dir).is_absolute() else Path.home() / ".claude"
    suspects: list[Path] = []

    if target_type == "rules":
        rules_dir = global_config_dir / "rules"
        if not rules_dir.exists():
            return []
        sources = [source_path] if source_path.is_file() else list(source_path.rglob("*.md"))
        for src in sources:
            candidate = rules_dir / src.name
            if candidate.exists() and candidate.is_file() and not _same_path(candidate, src):
                suspects.append(candidate)
    elif target_type == "skill":
        skill_name = target.get("name") or source_path.name
        candidate = global_config_dir / "skills" / skill_name
        if candidate.exists() and not _same_path(candidate, source_path):
            suspects.append(candidate)

    return suspects


@contextlib.contextmanager
def isolate_global_contamination(paths: list[Path]) -> Iterator[list[Path]]:
    """Hide `paths` (rename to `<name>.pilot-bench-hidden-<pid>`) for the block.

    See module docstring for the fail-safe layering. Restores on normal exit;
    atexit / signal handlers / next-run recovery catch abnormal exits.
    """
    moved: list[tuple[Path, Path]] = []
    planned: list[tuple[Path, Path]] = []
    for src in paths:
        hidden = src.with_name(f"{src.name}{HIDDEN_SUFFIX}-{os.getpid()}")
        if hidden.exists():
            print(
                f"  ⚠  {hidden.name} already exists (stale from a prior crash?); "
                f"leaving {src.name} in place — run may be contaminated",
                file=sys.stderr,
            )
            continue
        planned.append((src, hidden))

    if planned:
        try:
            _write_manifest(planned)
        except OSError as err:
            print(
                f"  ⚠  could not write recovery manifest ({err}); aborting isolation to stay fail-safe",
                file=sys.stderr,
            )
            yield []
            return

    try:
        for src, hidden in planned:
            try:
                src.rename(hidden)
            except OSError as err:
                print(f"  ⚠  could not hide {src}: {err}", file=sys.stderr)
                continue
            moved.append((src, hidden))
            HIDDEN_RESTORE_QUEUE.append((src, hidden))
        yield [h for _, h in moved]
    finally:
        failures: list[tuple[Path, Path, str]] = []
        for src, hidden in moved:
            try:
                _restore_hidden_path(src, hidden)
            except OSError as err:
                failures.append((src, hidden, str(err)))
            else:
                with contextlib.suppress(ValueError):
                    HIDDEN_RESTORE_QUEUE.remove((src, hidden))
        if failures:
            # Leave the manifest for next-run recovery; surface loudly.
            for src, hidden, reason in failures:
                print(
                    f"  ⚠  FAILED to restore {src} from {hidden}: {reason}. "
                    "Re-run the benchmark or pass `--restore-hidden` to recover.",
                    file=sys.stderr,
                )
        else:
            _clear_manifest()
