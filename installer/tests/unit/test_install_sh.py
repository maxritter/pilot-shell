"""Tests for install.sh bootstrap script."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


def _run_download_pilot_binary(
    tmp_path: Path,
    wrapper_script: str,
    *,
    system: str = "Linux",
    bash_executable: str = "bash",
    download_failure: str = "",
    downloader: str = "curl",
    activation_failure: str = "",
    signal_after: str = "",
    signal_after_commit_marker: bool = False,
    committed_cleanup_failure: bool = False,
    lock_pid: int | None = None,
    empty_lock: bool = False,
    installer_success: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute download_pilot_binary with local fake release downloads."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()
    macos_helpers = content[
        content.index("is_macos_gatekeeper_block() {") : content.index("\nconfirm_local_install() {")
    ]
    function = content[content.index("download_pilot_binary() {") : content.index("\nrun_installer() {")]

    fake_bin = tmp_path / f"fake-bin-{len(list(tmp_path.glob('fake-bin-*')))}"
    fake_bin.mkdir()
    wrapper_source = tmp_path / "release-pilot"
    wrapper_source.write_text(wrapper_script)
    wrapper_source.chmod(0o755)

    downloader_script = """#!/bin/bash
url=""
dest=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o|-O) dest="$2"; shift 2 ;;
        http*) url="$1"; shift ;;
        *) shift ;;
    esac
done
case "$FAKE_DOWNLOAD_FAILURE:$url" in
    module:*.so|wrapper:*/pilot) exit 22 ;;
esac
case "$url" in
    *.so) printf 'fake compiled module' > "$dest" ;;
    */pilot) cp "$FAKE_WRAPPER_SOURCE" "$dest" ;;
    *) exit 2 ;;
esac
"""
    for command in ("curl", "wget"):
        executable = fake_bin / command
        executable.write_text(downloader_script)
        executable.chmod(0o755)

    uname = fake_bin / "uname"
    uname.write_text(f"#!/bin/bash\necho {system}\n")
    uname.chmod(0o755)

    for command in ("xattr", "spctl"):
        executable = fake_bin / command
        executable.write_text("#!/bin/bash\nexit 1\n" if command == "xattr" else "#!/bin/bash\nexit 0\n")
        executable.chmod(0o755)

    mv = fake_bin / "mv"
    mv.write_text(
        """#!/bin/bash
case "$FAKE_SIGNAL_AFTER:$1:$2" in
    backup:*/bin:*.bin-backup.*|activation:*.bin-stage.*:*/bin)
        /bin/mv "$@"
        kill -TERM "$PPID"
        sleep 1
        exit 0
        ;;
esac
case "$FAKE_ACTIVATION_FAILURE:$1" in
    fail:*.bin-stage.*) exit 1 ;;
    signal:*.bin-stage.*) kill -TERM "$PPID"; sleep 1; exit 1 ;;
esac
exec /bin/mv "$@"
"""
    )
    mv.chmod(0o755)

    touch = fake_bin / "touch"
    touch.write_text(
        """#!/bin/bash
/usr/bin/touch "$@"
if [ "$FAKE_SIGNAL_AFTER_COMMIT_MARKER" = true ]; then
    case "$1" in
        *.bin-backup.*.committed) kill -TERM "$PPID"; sleep 1 ;;
    esac
fi
"""
    )
    touch.chmod(0o755)

    rm = fake_bin / "rm"
    rm.write_text(
        """#!/bin/bash
if [ "$FAKE_COMMITTED_CLEANUP_FAILURE" = true ]; then
    for argument in "$@"; do
        case "$argument" in
            *.bin-backup.*) exit 1 ;;
        esac
    done
fi
exec /bin/rm "$@"
"""
    )
    rm.chmod(0o755)

    harness = f"""#!/bin/bash
set -e
REPO=maxritter/pilot-shell
VERSION=10.7.1
get_platform_suffix() {{ echo linux-x86_64; }}
get_local_so_name() {{ echo pilot.cpython-312-x86_64-linux-gnu.so; }}
command() {{
    if [ "$1" = "-v" ]; then
        case "$FAKE_DOWNLOADER:$2" in
            wget:curl|none:curl|none:wget) return 1 ;;
        esac
    fi
    builtin command "$@"
}}
{macos_helpers}
{function}
acquire_pilot_install_lock
download_pilot_binary
if [ "$FAKE_INSTALLER_SUCCESS" = true ]; then
    commit_pilot_binary_install
else
    rollback_pilot_binary_install
    exit 1
fi
"""
    home = tmp_path / "home"
    if lock_pid is not None or empty_lock:
        lock_dir = home / ".pilot" / ".bin-install.lock"
        lock_dir.mkdir(parents=True, exist_ok=True)
        if lock_pid is not None:
            (lock_dir / "pid").write_text(f"{lock_pid}\n")
    env = os.environ.copy()
    env.update(
        {
            "FAKE_WRAPPER_SOURCE": str(wrapper_source),
            "FAKE_DOWNLOAD_FAILURE": download_failure,
            "FAKE_DOWNLOADER": downloader,
            "FAKE_ACTIVATION_FAILURE": activation_failure,
            "FAKE_SIGNAL_AFTER": signal_after,
            "FAKE_SIGNAL_AFTER_COMMIT_MARKER": "true" if signal_after_commit_marker else "false",
            "FAKE_COMMITTED_CLEANUP_FAILURE": "true" if committed_cleanup_failure else "false",
            "FAKE_INSTALLER_SUCCESS": "true" if installer_success else "false",
            "HOME": str(home),
            "PATH": f"{fake_bin}:{env['PATH']}",
        }
    )
    return subprocess.run([bash_executable, "-c", harness], env=env, text=True, capture_output=True, check=False)


def test_install_sh_runs_python_installer():
    """Verify install.sh runs the Python installer module via uv with Python 3.12."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "uv run --python 3.12" in content, "install.sh must run with Python 3.12"
    assert "python -m installer" in content, "install.sh must run Python installer"

    assert "install" in content, "install.sh must pass 'install' command"

    assert "--local-system" in content, "install.sh must support --local-system flag"


def test_install_rejects_symlinked_pilot_root_without_touching_target(tmp_path: Path) -> None:
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    home = tmp_path / "home"
    home.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "keep.txt"
    sentinel.write_text("keep\n")
    (home / ".pilot").symlink_to(outside, target_is_directory=True)
    env = os.environ.copy()
    env.update({"HOME": str(home), "VERSION": "10.7.1"})

    result = subprocess.run(
        ["/bin/bash", str(install_sh), "--auto-update"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "~/.pilot is a symlink" in result.stderr
    assert sentinel.read_text() == "keep\n"


def test_install_sh_downloads_installer_files():
    """Verify install.sh downloads the installer Python package dynamically."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "download_installer" in content, "install.sh must have download_installer function"

    assert "tree.json" in content, "Must download tree.json from release assets"
    assert "releases/download" in content, "Must use release asset URL pattern"

    assert "api.github.com" in content, "Must use GitHub API for file discovery fallback"
    assert "git/trees" in content, "Must use git trees API endpoint as fallback"

    assert "installer/" in content, "Must filter for installer directory"
    assert "(py|" in content, "Must filter for Python files (extension group)"


def test_install_sh_grep_pattern_includes_yaml_manifests():
    """Regression for #142: download_installer must also fetch installer/upstreams.yaml.

    install.sh's tree-filter grep originally only matched ``.py``, so fresh
    ``curl | bash`` installs landed without ``installer/upstreams.yaml`` and
    crashed at ``installer/manifest.py:127`` with FileNotFoundError.
    """
    import re
    import subprocess

    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    match = re.search(r"grep -oE '(\"path\":[^']+installer/[^']+)'", content)
    assert match, "Could not locate file-selection grep in install.sh"
    grep_pattern = match.group(1)

    sample_tree = (
        '{"tree":['
        '{"path":"installer/cli.py","type":"blob"},'
        '{"path":"installer/upstreams.yaml","type":"blob"},'
        '{"path":"installer/manifest.py","type":"blob"},'
        '{"path":"installer/tests/unit/test_x.py","type":"blob"},'
        '{"path":"docs/site/README.md","type":"blob"}'
        "]}"
    )

    result = subprocess.run(
        ["grep", "-oE", grep_pattern],
        input=sample_tree,
        text=True,
        capture_output=True,
        check=False,
    )
    selected = result.stdout

    assert "installer/cli.py" in selected, "must still match .py files"
    assert "installer/upstreams.yaml" in selected, (
        "install.sh:download_installer must match installer/upstreams.yaml — "
        "issue #142, manifest.py imports it at module load"
    )


def test_install_sh_runs_installer():
    """Verify install.sh runs the Python installer (which downloads Pilot binary)."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "run_installer" in content, "install.sh must have run_installer function"
    assert "python -m installer" in content, "Must run Python installer"


def test_downloaded_binary_is_validated_before_replacing_working_install() -> None:
    """A broken release artifact must leave the previous CLI intact.

    v10.7.0 deleted ``~/.pilot/bin`` before discovering that the replacement
    could not import yaml. That also broke Claude's configured statusline and
    both Claude/Codex shell wrappers, leaving users without a working updater.
    """
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()
    function = content[content.index("download_pilot_binary() {") : content.index("\nrun_installer() {")]

    assert ".bin-stage." in function, "downloads must be staged outside the live bin directory"
    validation = function.index('pilot_output=$("$wrapper_path" --version 2>&1)')
    replacement = function.index('mv "$bin_dir" "$backup_dir"')
    assert validation < replacement, "the staged wrapper must execute successfully before replacing the live bin"
    assert 'echo "  [OK] Existing Pilot installation left unchanged"' in function
    assert 'rm -rf "$bin_dir"' not in function, "never delete the live bin before replacement is known-good"


def test_binary_backup_is_committed_only_after_python_installer_succeeds() -> None:
    """Configuration/dependency failure must still be able to restore the old CLI."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()
    install_call = content.index("if run_installer $INSTALLER_ARGS; then")
    commit = content.index("commit_pilot_binary_install", install_call)
    rollback = content.index("rollback_pilot_binary_install", commit)

    assert install_call < commit < rollback


def test_install_lock_is_acquired_before_installer_directory_mutation() -> None:
    """Concurrent installs serialize before tools or Pilot-owned paths mutate."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()
    main = content[content.rindex('if [ "$USE_LOCAL_INSTALLER" = true ]; then') :]
    lock_call = content.rindex("\nacquire_pilot_install_lock\n")

    assert lock_call < content.rindex("\nif check_uv; then")
    assert lock_call < content.rindex('if [ "$USE_LOCAL_INSTALLER" = true ]; then')
    assert main.index("download_installer") < main.index("download_pilot_binary")


def test_binary_verification_reports_runtime_error_instead_of_false_gatekeeper_warning() -> None:
    """Import/dependency failures must not be presented as macOS policy blocks."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()
    function = content[content.index("download_pilot_binary() {") : content.index("\nrun_installer() {")]

    assert 'pilot_output=$("$wrapper_path" --version 2>&1)' in function
    assert 'printf "%s\\n" "$pilot_output"' in function
    assert "is_macos_gatekeeper_block" in function


def test_failed_binary_verification_preserves_the_working_install(tmp_path: Path) -> None:
    """A broken staged wrapper leaves the live CLI and sidecars byte-for-byte intact."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")
    (live_bin / "semble").write_text("managed sidecar")
    (live_bin / "semble").chmod(0o755)

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho \"ModuleNotFoundError: No module named 'yaml'\" >&2\nexit 1\n",
    )

    assert result.returncode != 0
    assert "ModuleNotFoundError: No module named 'yaml'" in result.stdout
    assert "Gatekeeper" not in result.stdout
    assert "Existing Pilot installation left unchanged" in result.stdout
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"
    assert (live_bin / "semble").read_text() == "managed sidecar"
    assert os.access(live_bin / "semble", os.X_OK)
    assert not list((tmp_path / "home" / ".pilot").glob(".bin-*"))


def test_verified_binary_transactionally_replaces_launcher_and_preserves_sidecars(tmp_path: Path) -> None:
    """A valid staged release replaces Pilot only after reporting the requested version."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")
    (live_bin / "semble").write_text("managed sidecar")
    (live_bin / "semble").chmod(0o755)

    result = _run_download_pilot_binary(tmp_path, "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Pilot binary ready (v10.7.1)" in result.stdout
    assert "Pilot Shell v10.7.1" in (live_bin / "pilot").read_text()
    assert (live_bin / "semble").read_text() == "managed sidecar"
    assert os.access(live_bin / "semble", os.X_OK)
    assert (live_bin / "pilot.cpython-312-x86_64-linux-gnu.so").is_file()
    assert (live_bin.stat().st_mode & 0o777) == 0o755
    assert not list((tmp_path / "home" / ".pilot").glob(".bin-*"))


def test_verified_update_preserves_symlink_sidecars(tmp_path: Path) -> None:
    """Pilot-managed tool links survive the staged directory copy and swap."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")
    target = tmp_path / "tools" / "semble"
    target.parent.mkdir()
    target.write_text("tool")
    (live_bin / "semble").symlink_to(target)

    result = _run_download_pilot_binary(tmp_path, "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n")

    assert result.returncode == 0, result.stdout + result.stderr
    assert (live_bin / "semble").is_symlink()
    assert (live_bin / "semble").resolve() == target


def test_version_mismatch_preserves_existing_install(tmp_path: Path) -> None:
    """A valid but incorrectly versioned release asset is never activated."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")

    result = _run_download_pilot_binary(tmp_path, "#!/bin/bash\necho 'Pilot Shell v10.7.0'\n")

    assert result.returncode != 0
    assert "expected v10.7.1" in result.stdout
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"


@pytest.mark.parametrize("failure", ["fail", "signal"])
def test_activation_failure_or_signal_restores_previous_binary(tmp_path: Path, failure: str) -> None:
    """The rollback trap closes the interruption window between directory moves."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")
    (live_bin / "rtk").write_text("managed sidecar")

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        activation_failure=failure,
    )

    assert result.returncode != 0
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"
    assert (live_bin / "rtk").read_text() == "managed sidecar"
    assert not list((tmp_path / "home" / ".pilot").glob(".bin-*"))


@pytest.mark.parametrize("move", ["backup", "activation"])
def test_signal_after_successful_directory_move_restores_previous_binary(tmp_path: Path, move: str) -> None:
    """Deferred Bash signal traps see rollback state published before each rename."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        signal_after=move,
    )

    assert result.returncode != 0
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"
    assert not list((tmp_path / "home" / ".pilot").glob(".bin-*"))


def test_downstream_installer_failure_restores_previous_binary(tmp_path: Path) -> None:
    """The old bin remains recoverable until the Python installer succeeds."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        installer_success=False,
    )

    assert result.returncode != 0
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"
    assert not list((tmp_path / "home" / ".pilot").glob(".bin-*"))


def test_signal_after_commit_marker_never_removes_both_binary_versions(tmp_path: Path) -> None:
    """A deferred signal at commit restores the old binary instead of stranding it."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        signal_after_commit_marker=True,
    )

    assert result.returncode != 0
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"
    assert not list((tmp_path / "home" / ".pilot").glob(".bin-*"))


def test_committed_backup_cleanup_failure_cannot_trigger_future_downgrade(tmp_path: Path) -> None:
    """A marked committed backup is cleanup-only and is never restored later."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")

    installed = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        committed_cleanup_failure=True,
    )

    assert installed.returncode == 0, installed.stdout + installed.stderr
    assert "could not remove old binary backup" in installed.stdout
    committed_backups = list((tmp_path / "home" / ".pilot").glob(".bin-backup.*"))
    committed_backups = [path for path in committed_backups if path.is_dir()]
    assert len(committed_backups) == 1
    assert Path(f"{committed_backups[0]}.committed").is_file()
    assert "Pilot Shell v10.7.1" in (live_bin / "pilot").read_text()

    retry = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        download_failure="module",
    )

    assert retry.returncode != 0
    assert "Pilot Shell v10.7.1" in (live_bin / "pilot").read_text()
    assert not list((tmp_path / "home" / ".pilot").glob(".bin-backup.*"))


def test_active_install_lock_rejects_concurrent_update(tmp_path: Path) -> None:
    """A second updater cannot race the verified directory swap."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        lock_pid=os.getpid(),
    )

    assert result.returncode != 0
    assert "Another Pilot install or update is already running" in result.stdout
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"


def test_ownerless_lock_is_not_deleted_during_initialisation_race(tmp_path: Path) -> None:
    """A second updater treats a just-created lock without a pid as active."""
    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        empty_lock=True,
    )

    assert result.returncode != 0
    assert "left a stale lock" in result.stdout
    assert (tmp_path / "home" / ".pilot" / ".bin-install.lock").is_dir()


def test_concurrent_lock_acquisition_has_exactly_one_winner(tmp_path: Path) -> None:
    """Real simultaneous Bash processes cannot both enter the install transaction."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()
    helpers = content[content.index("recover_abandoned_pilot_binary_install() {") : content.index("\nconfirm_local_install() {")]
    start_file = tmp_path / "start"
    harness = f"""#!/bin/bash
set -e
PILOT_BIN_LIVE_DIR=""
PILOT_BIN_STAGE_DIR=""
PILOT_BIN_BACKUP_DIR=""
PILOT_BIN_LOCK_DIR=""
PILOT_BIN_ACTIVATED=false
{helpers}
while [ ! -f "$START_FILE" ]; do :; done
acquire_pilot_install_lock
sleep 2
commit_pilot_binary_install
"""
    env = os.environ.copy()
    env.update({"HOME": str(tmp_path / "home"), "START_FILE": str(start_file)})
    processes = [
        subprocess.Popen(
            ["/bin/bash", "-c", harness],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _ in range(8)
    ]
    start_file.touch()
    results = [process.communicate(timeout=10) + (process.returncode,) for process in processes]

    assert sum(returncode == 0 for _, _, returncode in results) == 1, results
    assert not (tmp_path / "home" / ".pilot" / ".bin-install.lock").exists()


def test_concurrent_stale_lock_takeover_fails_closed(tmp_path: Path) -> None:
    """No contender removes a dead-owner lock while peers are inspecting it."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()
    helpers = content[content.index("recover_abandoned_pilot_binary_install() {") : content.index("\nconfirm_local_install() {")]
    home = tmp_path / "home"
    lock_dir = home / ".pilot" / ".bin-install.lock"
    lock_dir.mkdir(parents=True)
    (lock_dir / "pid").write_text("999999999\n")
    start_file = tmp_path / "stale-start"
    harness = f"""#!/bin/bash
set -e
PILOT_BIN_LIVE_DIR=""
PILOT_BIN_STAGE_DIR=""
PILOT_BIN_BACKUP_DIR=""
PILOT_BIN_LOCK_DIR=""
PILOT_BIN_ACTIVATED=false
{helpers}
while [ ! -f "$START_FILE" ]; do :; done
acquire_pilot_install_lock
commit_pilot_binary_install
"""
    env = os.environ.copy()
    env.update({"HOME": str(home), "START_FILE": str(start_file)})
    processes = [
        subprocess.Popen(
            ["/bin/bash", "-c", harness],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _ in range(8)
    ]
    start_file.touch()
    results = [process.communicate(timeout=10) + (process.returncode,) for process in processes]

    assert all(returncode != 0 for _, _, returncode in results), results
    assert (lock_dir / "pid").read_text() == "999999999\n"


def test_stale_install_lock_fails_closed_with_recovery_instructions(tmp_path: Path) -> None:
    """Dead-owner locks are never raced or removed behind another updater."""
    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        lock_pid=999_999_999,
    )

    assert result.returncode != 0
    assert "left a stale lock" in result.stdout
    assert "remove that directory" in result.stdout


def test_stale_lock_restores_uncommitted_backup_before_retry(tmp_path: Path) -> None:
    """Recovery after SIGKILL/power loss rolls back the prior uncommitted swap."""
    pilot_home = tmp_path / "home" / ".pilot"
    live_bin = pilot_home / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("interrupted new wrapper")
    backup = pilot_home / ".bin-backup.crashed"
    backup.mkdir()
    (backup / "pilot").write_text("working old wrapper")
    abandoned_stage = pilot_home / ".bin-stage.crashed"
    abandoned_stage.mkdir()

    blocked = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        lock_pid=999_999_999,
    )
    assert blocked.returncode != 0
    (pilot_home / ".bin-install.lock" / "pid").unlink()
    (pilot_home / ".bin-install.lock").rmdir()

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        download_failure="module",
    )

    assert result.returncode != 0
    assert "Restored Pilot binary from an interrupted update" in result.stdout
    assert (live_bin / "pilot").read_text() == "working old wrapper"
    assert not list(pilot_home.glob(".bin-*"))


def test_transactional_update_runs_with_the_system_bash(tmp_path: Path) -> None:
    """The update path stays compatible with macOS's Bash 3.2-era syntax."""
    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        bash_executable="/bin/bash",
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_macos_runtime_failure_is_not_misclassified_as_gatekeeper(tmp_path: Path) -> None:
    """A normal Python failure on Darwin retains its traceback and working install."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho \"ModuleNotFoundError: No module named 'yaml'\" >&2\nexit 1\n",
        system="Darwin",
    )

    assert result.returncode != 0
    assert "ModuleNotFoundError: No module named 'yaml'" in result.stdout
    assert "Gatekeeper is blocking" not in result.stdout
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"


def test_macos_gatekeeper_diagnostic_requires_a_policy_denial_signal(tmp_path: Path) -> None:
    """A Darwin killed-by-policy signal still receives the actionable warning."""
    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Killed: 9' >&2\nexit 1\n",
        system="Darwin",
    )

    assert result.returncode != 0
    assert "Gatekeeper is blocking the pilot binary" in result.stdout


def test_failed_fresh_install_leaves_no_partial_bin_directory(tmp_path: Path) -> None:
    """Fresh installs clean the staging directory when the release cannot start."""
    result = _run_download_pilot_binary(tmp_path, "#!/bin/bash\necho broken >&2\nexit 1\n")

    assert result.returncode != 0
    pilot_home = tmp_path / "home" / ".pilot"
    assert not (pilot_home / "bin").exists()
    assert not list(pilot_home.glob(".bin-*"))


@pytest.mark.parametrize("failure", ["module", "wrapper"])
def test_download_failure_preserves_existing_install(tmp_path: Path, failure: str) -> None:
    """Network failures at either asset leave the prior launcher and sidecars intact."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")
    (live_bin / "rtk").write_text("managed sidecar")

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        download_failure=failure,
    )

    assert result.returncode != 0
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"
    assert (live_bin / "rtk").read_text() == "managed sidecar"
    assert not list((tmp_path / "home" / ".pilot").glob(".bin-*"))


def test_wget_only_update_path_replaces_verified_binary(tmp_path: Path) -> None:
    """Hosts without curl use wget with the same staged verification semantics."""
    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        downloader="wget",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Pilot binary ready (v10.7.1)" in result.stdout


def test_missing_downloaders_leave_existing_install_unchanged(tmp_path: Path) -> None:
    """A host with neither downloader gets a direct error and no staging leak."""
    live_bin = tmp_path / "home" / ".pilot" / "bin"
    live_bin.mkdir(parents=True)
    (live_bin / "pilot").write_text("working v10.6 wrapper")

    result = _run_download_pilot_binary(
        tmp_path,
        "#!/bin/bash\necho 'Pilot Shell v10.7.1'\n",
        downloader="none",
    )

    assert result.returncode != 0
    assert "Neither curl nor wget" in result.stdout
    assert (live_bin / "pilot").read_text() == "working v10.6 wrapper"
    assert not list((tmp_path / "home" / ".pilot").glob(".bin-*"))


def test_install_sh_ensures_uv_available():
    """Verify install.sh ensures uv is available."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "check_uv" in content, "install.sh must have check_uv function"
    assert "install_uv" in content, "install.sh must have install_uv function"
    # Deliberately unpinned floating endpoint (soft_pin in the manifest):
    # always installs the latest uv. A hard sha256 pin against this URL
    # breaks on every uv release (GH #147).
    assert 'UV_INSTALL_URL="https://astral.sh/uv/install.sh"' in content, "Must use official floating uv installer URL"
    assert "UV_INSTALL_SHA256" not in content, "uv bootstrap is soft-pinned; hard sha256 pin is forbidden (GH #147)"


def test_install_sh_is_executable_bash_script():
    """Verify install.sh has proper shebang."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert content.startswith("#!/bin/bash"), "install.sh must start with bash shebang"


def test_install_sh_uses_with_flags():
    """Verify install.sh uses --with flags for inline deps (no venv created)."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "--with rich" in content, "Must use --with for rich"
    assert "PYTHONPATH" in content, "Must set PYTHONPATH for installer module"


def test_install_sh_uses_python_312():
    """Verify install.sh uses Python 3.12 via uv run."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "--python 3.12" in content, "Must use --python 3.12 flag"
    assert "--no-project" in content, "Must use --no-project to avoid modifying user's venv"


def test_install_sh_uses_no_config_flag():
    """Verify install.sh isolates uv from ambient uv.toml config.

    Without --no-config, a user-level uv.toml with authenticated corporate
    indexes (e.g. Google Artifact Registry with expired credentials) breaks
    the bootstrap's dependency resolution."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    uv_run_lines = [line for line in content.splitlines() if line.lstrip().startswith("uv run")]
    assert uv_run_lines, "install.sh must contain a uv run invocation"
    for line in uv_run_lines:
        assert "--no-config" in line, f"uv run invocation missing --no-config: {line.strip()}"


def test_install_sh_exports_uv_no_config():
    """Verify install.sh exports UV_NO_CONFIG so nested uv invocations
    (downloaded wrapper verification, installer's `uv tool install` calls)
    are hermetic against ambient uv.toml config."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "export UV_NO_CONFIG=1" in content, "Must export UV_NO_CONFIG=1 for nested uv calls"


def test_install_sh_skips_prompt_on_restart():
    """Verify install.sh skips install mode prompt during auto-updates."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert 'RESTART_PILOT" = true' in content, "Must check RESTART_PILOT flag"
    assert "Updating local installation" in content, "Must show update message"


def test_install_sh_no_global_install_mode():
    """Verify install.sh does not store install_mode in global config."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "save_install_mode" not in content, "Must not save install_mode globally"
    assert "get_saved_install_mode" not in content, "Must not read global install_mode"


def test_install_sh_has_auto_version_fetch():
    """Verify install.sh has get_latest_release function for auto-fetching version."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "get_latest_release()" in content, "Must have get_latest_release function"
    assert "api.github.com" in content, "Must use GitHub API"
    assert "releases/latest" in content, "Must query releases/latest endpoint"
    assert "tag_name" in content, "Must parse tag_name from API response"


def test_install_sh_supports_version_env_var():
    """Verify install.sh supports VERSION environment variable."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert 'VERSION="${VERSION:-}"' in content, "Must read VERSION env var with empty default"
    assert "Fetching latest version" in content, "Must have message for auto-fetch mode"


def test_install_sh_handles_api_failure():
    """Verify install.sh handles GitHub API failures gracefully."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "Failed to fetch" in content or "Could not" in content, "Must have error message for API failure"


def test_install_sh_detects_native_windows():
    """Verify install.sh detects native Windows (MINGW/MSYS/Cygwin) and directs to WSL2."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "is_native_windows" in content, "Must have Windows detection function"
    assert "MINGW" in content, "Must detect Git Bash (MINGW)"
    assert "MSYS" in content, "Must detect MSYS2"
    assert "CYGWIN" in content, "Must detect Cygwin"
    assert "WSL2" in content or "WSL" in content, "Must mention WSL2 as an option"


@pytest.mark.parametrize("uname_output", ["MINGW64_NT-10.0", "MSYS_NT-10.0", "CYGWIN_NT-10.0"])
def test_native_windows_exits_before_modifying_user_files(tmp_path: Path, uname_output: str) -> None:
    """Unsupported native Windows shells route to WSL2 without a partial install."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    uname = fake_bin / "uname"
    uname.write_text(f"#!/bin/bash\necho {uname_output}\n")
    uname.chmod(0o755)

    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env.update({"HOME": str(home), "PATH": f"{fake_bin}:{env['PATH']}"})
    env.pop("VERSION", None)
    result = subprocess.run(
        ["/bin/bash", str(install_sh), "--auto-update"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Windows Detected" in result.stdout
    assert "wsl --install -d Ubuntu" in result.stdout
    assert not (home / ".pilot").exists()


def test_install_sh_uses_redirect_for_version_detection():
    """Verify install.sh uses redirect-based approach before API for version detection."""
    install_sh = Path(__file__).parent.parent.parent.parent / "install.sh"
    content = install_sh.read_text()

    assert "redirect_url" in content, "Must use redirect_url for curl"
    assert "releases/latest" in content, "Must query releases/latest for redirect"

    assert "--spider" in content or "Location:" in content, "Must detect wget redirects"

    assert "api.github.com" in content, "Must still have API fallback"
    assert "releases/latest" in content, "Must query both redirect and API endpoints"

    assert "tr -d" in content, "Must strip carriage returns from redirect response"
    assert "%{redirect_url}" in content, "Must detect literal %{redirect_url} from old curl versions"
    assert "releases/tag/v" in content, "Must parse version from redirect URL path"
