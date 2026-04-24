"""Fail-safe isolation of globally-installed rules and skills.

Without this module, benchmarks are silently contaminated: files in
`~/.claude/rules/` and `~/.claude/skills/` load in every `claude -p` subprocess
regardless of cwd, so if the user has the target rule/skill installed globally,
the `without` config still has it and the benchmark measures nothing.

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
        for pair in pairs:
            if not (isinstance(pair, list) and len(pair) == 2):
                continue
            src = Path(str(pair[0]))
            hidden = Path(str(pair[1]))
            if hidden.exists() and not src.exists():
                try:
                    hidden.rename(src)
                    restored += 1
                    print(f"  🛠  recovered hidden file from prior crash: {src}", file=sys.stderr)
                except OSError as err:
                    print(f"  ⚠  failed to recover {src} from {hidden}: {err}", file=sys.stderr)
        manifest.unlink(missing_ok=True)
    return restored


def _restore_hidden_paths() -> None:
    """Belt-and-braces restore for anything left in HIDDEN_RESTORE_QUEUE."""
    while HIDDEN_RESTORE_QUEUE:
        src, hidden = HIDDEN_RESTORE_QUEUE.pop()
        try:
            if hidden.exists() and not src.exists():
                hidden.rename(src)
        except OSError:
            pass
    try:
        _clear_manifest()
    except OSError:
        pass


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


def detect_global_contamination(target: TargetConfig) -> list[Path]:
    """Return ~/.claude/ paths that duplicate the target's rule/skill."""
    target_type = target.get("type", "skill")
    raw_path = target.get("path")
    if not raw_path:
        return []
    source_path = Path(raw_path).expanduser().resolve()
    if not source_path.exists():
        return []

    home_claude = Path.home() / ".claude"
    suspects: list[Path] = []

    def _same_path(a: Path, b: Path) -> bool:
        try:
            return a.resolve() == b.resolve()
        except OSError:
            return False

    if target_type == "rules":
        rules_dir = home_claude / "rules"
        if not rules_dir.exists():
            return []
        sources = [source_path] if source_path.is_file() else list(source_path.rglob("*.md"))
        for src in sources:
            candidate = rules_dir / src.name
            if candidate.exists() and candidate.is_file() and not _same_path(candidate, src):
                suspects.append(candidate)
    elif target_type == "skill":
        skill_name = target.get("name") or source_path.name
        candidate = home_claude / "skills" / skill_name
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
                f"  ⚠  could not write recovery manifest ({err}); aborting "
                "isolation to stay fail-safe",
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
            if hidden.exists() and not src.exists():
                try:
                    hidden.rename(src)
                except OSError as err:
                    failures.append((src, hidden, str(err)))
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
