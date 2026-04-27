"""Dependencies step - installs required tools and packages."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from installer.context import InstallContext
from installer.platform_utils import (
    command_exists,
    ensure_sudo_credentials,
    is_linux_arm64,
    needs_sudo,
    npm_global_cmd,
    start_sudo_keepalive,
    stop_sudo_keepalive,
)
from installer.steps.base import BaseStep

MAX_RETRIES = 3
RETRY_DELAY = 2
GLOBAL_NPM_INSTALL_TIMEOUT = 300
UV_TOOL_INSTALL_TIMEOUT = 180
NPX_CACHE_WAIT_TIMEOUT = 180


class _SudoReauthNeeded(Exception):
    """Raised when sudo -n fails and credentials need re-priming outside the spinner."""


_thread_local = threading.local()

_allow_sudo_fallback: bool = False


def _clear_last_error() -> None:
    _thread_local.last_retry_stderr = ""


def _get_last_error() -> str:
    return getattr(_thread_local, "last_retry_stderr", "")


def _run_bash_with_retry(command: str, cwd: Path | None = None, timeout: int = 120, stream: bool = False) -> bool:
    """Run a bash command with retry logic for transient failures.

    When stream=True, stdout/stderr are inherited (visible to the user)
    instead of captured. Use for long-running commands where progress matters.

    On failure, the last stderr output is stored in _last_retry_stderr
    for diagnostic display by the caller.

    When _allow_sudo_fallback is True and a sudo -n command fails with a
    permission error, raises _SudoReauthNeeded so the caller can stop
    the spinner, re-authenticate, and retry.

    Note: stream=True commands inherit stdio (stderr not captured), so
    sudo failures can't be detected — the user sees the error directly.
    """
    for attempt in range(MAX_RETRIES):
        try:
            if stream:
                subprocess.run(
                    ["bash", "-c", command],
                    check=True,
                    cwd=cwd,
                    timeout=timeout,
                )
            else:
                subprocess.run(
                    ["bash", "-c", command],
                    check=True,
                    capture_output=True,
                    cwd=cwd,
                    timeout=timeout,
                )
            return True
        except subprocess.CalledProcessError as e:
            if not stream and e.stderr:
                stderr = e.stderr if isinstance(e.stderr, str) else e.stderr.decode(errors="replace")
                _thread_local.last_retry_stderr = stderr
                if _allow_sudo_fallback and "sudo:" in stderr and "sudo -n" in command:
                    raise _SudoReauthNeeded()
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            continue
        except subprocess.TimeoutExpired:
            _thread_local.last_retry_stderr = f"Command timed out after {timeout}s"
            break
    return False


def _get_nvm_source_cmd() -> str:
    """Get the command to source NVM for nvm-specific commands.

    Only needed for `nvm install`, `nvm use`, etc. - not for npm/node/claude.
    """
    nvm_locations = [
        Path.home() / ".nvm" / "nvm.sh",
        Path("/usr/local/share/nvm/nvm.sh"),
    ]

    for nvm_path in nvm_locations:
        if nvm_path.exists():
            return f"source {nvm_path} && "

    return ""


def install_claude_code() -> bool:
    """Install Claude Code via native installer if not present."""
    if command_exists("claude"):
        return True

    return _run_bash_with_retry(
        "curl -fsSL https://claude.ai/install.sh | bash",
        timeout=300,
    )


def install_nodejs() -> bool:
    """Install Node.js via NVM if not present."""
    if command_exists("node"):
        return True

    nvm_dir = Path.home() / ".nvm"
    if not nvm_dir.exists():
        if not _run_bash_with_retry(
            "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash",
            timeout=180,
        ):
            return False

    nvm_src = _get_nvm_source_cmd()
    nvm_cmd = f'export NVM_DIR="$HOME/.nvm" && {nvm_src}nvm install 22 && nvm use 22'
    if not _run_bash_with_retry(nvm_cmd, timeout=300):
        return False

    nvm_versions = Path.home() / ".nvm" / "versions" / "node"
    if nvm_versions.exists():
        node_bins = sorted(nvm_versions.glob("*/bin"), reverse=True)
        if node_bins:
            node_bin = str(node_bins[0])
            if node_bin not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{node_bin}:{os.environ.get('PATH', '')}"

    return True


def install_uv() -> bool:
    """Install uv package manager if not present."""
    if command_exists("uv"):
        return True

    return _run_bash_with_retry("curl -LsSf https://astral.sh/uv/install.sh | sh")


def install_python_tools() -> bool:
    """Install Python development tools."""
    tools = ["ruff", "basedpyright"]

    for tool in tools:
        if not command_exists(tool):
            if not _run_bash_with_retry(f"uv tool install {tool}"):
                return False
    return True


def install_probe() -> bool:
    """Install or update Probe code search tool globally via npm."""
    if not _run_bash_with_retry(
        npm_global_cmd("npm install -g @probelabs/probe"),
        timeout=GLOBAL_NPM_INSTALL_TIMEOUT,
    ):
        return False

    _symlink_to_pilot_bin("probe")
    return True


def install_rtk() -> bool:
    """Install or update RTK (Rust Token Killer) CLI.

    Brew handles install/upgrade in prerequisites (no sudo needed).
    Curl fallback only runs when brew didn't install it.
    Symlinks to ~/.pilot/bin/ so RTK is on PATH during hook execution.
    """
    if command_exists("rtk"):
        _symlink_to_pilot_bin("rtk")
        return True
    if not _run_bash_with_retry(
        "curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh",
        timeout=120,
    ):
        return False
    _symlink_to_pilot_bin("rtk")
    return True


def _symlink_to_pilot_bin(binary_name: str) -> None:
    """Create a symlink in ~/.pilot/bin/ pointing to the npm global binary.

    This ensures the binary is in PATH even when the npm global bin directory
    (e.g. ~/.nvm/versions/node/vXX/bin/) is not in PATH during hook execution.
    ~/.pilot/bin/ is added to PATH by the shell integration step.
    """
    pilot_bin = Path.home() / ".pilot" / "bin"
    pilot_bin.mkdir(parents=True, exist_ok=True)
    link_path = pilot_bin / binary_name

    source = shutil.which(binary_name)
    if not source:
        return

    source_path = Path(source).resolve()
    try:
        if link_path.is_symlink() or link_path.exists():
            link_path.unlink()
        link_path.symlink_to(source_path)
    except OSError:
        pass


def _is_in_git_repo(directory: Path) -> bool:
    """Check if directory is inside a git repository by walking up the tree."""
    current = directory.resolve()
    while True:
        if (current / ".git").exists():
            return True
        parent = current.parent
        if parent == current:
            return False
        current = parent


def install_codegraph() -> bool:
    """Install or update CodeGraph for code knowledge graph and structural analysis."""
    if not _run_bash_with_retry(
        npm_global_cmd("npm install -g @colbymchenry/codegraph --force"),
        timeout=GLOBAL_NPM_INSTALL_TIMEOUT,
    ):
        return False

    _symlink_to_pilot_bin("codegraph")
    return True


def install_better_sqlite3() -> bool:
    """Install native better-sqlite3 globally so CodeGraph can find it.

    CodeGraph declares `better-sqlite3` as an `optionalDependencies`. npm
    silently skips optional deps in several real-world scenarios (`--force`
    global installs on some npm versions, `.npmrc` with `optional=false`,
    prebuild-install network failures, platform/arch mismatches). When the
    native module is missing, CodeGraph falls back to a WASM SQLite backend
    that has known issues producing `SQLITE_CANTOPEN: unable to open database
    file` on certain filesystems — users see this as "codegraph can't index
    anything".

    Installing better-sqlite3 at the GLOBAL npm root works because Node's
    module resolver walks up from CodeGraph's package directory — eventually
    hitting the global node_modules dir and finding better-sqlite3 as a
    sibling of @colbymchenry/codegraph. No nested install, no tree walking.
    """
    return _run_bash_with_retry(
        npm_global_cmd("npm install -g better-sqlite3 --no-audit --no-fund"),
        timeout=GLOBAL_NPM_INSTALL_TIMEOUT,
    )


def _is_codegraph_indexed(project_dir: Path) -> bool:
    """Check if codegraph has already been indexed.

    Uses the database file size as a reliable indicator: a freshly-init'd
    but unindexed db is ~150KB, while an indexed project is typically >1MB.
    This avoids shelling out to `codegraph status` which can fail due to
    WASM backend issues or db locking from a running MCP server.
    """
    db_path = project_dir / ".codegraph" / "codegraph.db"
    if not db_path.exists():
        return False
    try:
        return db_path.stat().st_size > 1_000_000
    except OSError:
        return False


def _enable_codegraph_embeddings(project_dir: Path) -> None:
    """Enable embeddings in .codegraph/config.json."""
    config_path = project_dir / ".codegraph" / "config.json"
    for _ in range(10):
        if config_path.exists():
            break
        time.sleep(0.5)

    if not config_path.exists():
        return

    try:
        config = json.loads(config_path.read_text())
        if config.get("enableEmbeddings") is True:
            return
        config["enableEmbeddings"] = True
        config_path.write_text(json.dumps(config, indent=2) + "\n")
    except (json.JSONDecodeError, OSError):
        pass


def initialize_codegraph(project_dir: Path) -> bool:
    """Initialize CodeGraph in a project: init, enable embeddings, index, sync.

    Streams output so users see indexing progress.
    Skips indexing if already up to date.
    Only indexes actual git repositories to avoid scanning unrelated files.
    """
    if not command_exists("codegraph"):
        return False

    if not _is_in_git_repo(project_dir):
        return False

    codegraph_dir = project_dir / ".codegraph"

    if not codegraph_dir.exists():
        if not _run_bash_with_retry("codegraph init", cwd=project_dir, timeout=60):
            return False

    _enable_codegraph_embeddings(project_dir)

    if not _is_codegraph_indexed(project_dir):
        if not _run_bash_with_retry("codegraph index", cwd=project_dir, timeout=600, stream=True):
            return False

    _run_bash_with_retry("codegraph sync", cwd=project_dir, timeout=300)
    return True


def codegraph_needs_work(project_dir: Path) -> bool:
    """Check if codegraph initialization or indexing is needed.

    Returns False (no work) when .codegraph/ exists and index is up to date.
    Used by the installer to decide whether to show progress messages.
    Only applies to git repositories.
    """
    if not command_exists("codegraph"):
        return False
    if not _is_in_git_repo(project_dir):
        return False
    codegraph_dir = project_dir / ".codegraph"
    if not codegraph_dir.exists():
        return True
    return not _is_codegraph_indexed(project_dir)


def install_typescript_lsp() -> bool:
    """Install TypeScript language server and compiler globally."""
    if command_exists("vtsls"):
        return True
    return _run_bash_with_retry(
        npm_global_cmd("npm install -g @vtsls/language-server typescript"),
        timeout=GLOBAL_NPM_INSTALL_TIMEOUT,
    )


def install_prettier() -> bool:
    """Install prettier code formatter globally for TypeScript/JavaScript files."""
    if command_exists("prettier"):
        return True
    return _run_bash_with_retry(
        npm_global_cmd("npm install -g prettier"),
        timeout=GLOBAL_NPM_INSTALL_TIMEOUT,
    )


def _install_go_via_apt() -> bool:
    """Install Go and gopls via apt on Linux."""
    import platform

    if platform.system() != "Linux":
        return False
    if not command_exists("apt-get"):
        return False
    return _run_bash_with_retry(
        "sudo apt-get update -qq && sudo apt-get install -y -qq golang-go gopls",
        timeout=180,
    )


def _is_golangci_lint_installed() -> bool:
    """Check if golangci-lint is installed, including in GOPATH/bin."""
    if command_exists("golangci-lint"):
        return True
    if not command_exists("go"):
        return False
    try:
        result = subprocess.run(["go", "env", "GOPATH"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            gopath_bin = Path(result.stdout.strip()) / "bin" / "golangci-lint"
            if gopath_bin.exists():
                return True
    except Exception:
        pass
    return False


def install_golangci_lint() -> bool:
    """Install golangci-lint for comprehensive Go code linting."""
    if _is_golangci_lint_installed():
        return True
    if not command_exists("go"):
        if not _install_go_via_apt():
            return False
    install_cmd = (
        "curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh"
        " | sh -s -- -b $(go env GOPATH)/bin"
    )
    return _run_bash_with_retry(install_cmd, timeout=120)


def _refresh_marketplace(marketplace: str) -> bool:
    """Refresh a marketplace to get latest plugin versions.

    marketplace is in owner/repo format (e.g. "anthropics/claude-plugins-official").
    The update command needs only the short name (e.g. "claude-plugins-official").
    """
    short_name = marketplace.split("/", 1)[-1] if "/" in marketplace else marketplace
    return _run_bash_with_retry(
        f"claude plugins marketplace update {short_name}",
        timeout=60,
    )


def _install_or_update_plugin(
    plugin_id: str,
    marketplace: str,
) -> bool:
    """Install or update a Claude Code plugin via the marketplace.

    Refreshes the marketplace first, then installs or updates the plugin.
    """
    if not command_exists("claude"):
        return False

    already_installed = False
    try:
        result = subprocess.run(
            ["claude", "plugins", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            plugins = json.loads(result.stdout)
            already_installed = any(p.get("id") == plugin_id for p in plugins)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        pass

    if already_installed:
        _refresh_marketplace(marketplace)
        return _run_bash_with_retry(
            f"claude plugins update {plugin_id}",
            timeout=120,
        )

    if not _run_bash_with_retry(
        f"claude plugins marketplace add {marketplace}",
        timeout=60,
    ):
        return False

    return _run_bash_with_retry(
        f"claude plugins install {plugin_id}",
        timeout=120,
    )


def install_context_mode_plugin() -> bool:
    """Install or update the context-mode plugin via the Claude CLI plugin system."""
    return _install_or_update_plugin(
        plugin_id="context-mode@context-mode",
        marketplace="mksglu/context-mode",
    )


def install_codex_plugin() -> bool:
    """Install or update the Codex plugin via the Claude CLI plugin system."""
    return _install_or_update_plugin(
        plugin_id="codex@openai-codex",
        marketplace="openai/codex-plugin-cc",
    )


def install_chrome_devtools_plugin() -> bool:
    """Install or update the Chrome DevTools MCP plugin via the Claude CLI plugin system."""
    return _install_or_update_plugin(
        plugin_id="chrome-devtools-mcp@chrome-devtools-plugins",
        marketplace="ChromeDevTools/chrome-devtools-mcp",
    )


def install_pbt_tools() -> bool:
    """Install property-based testing packages: hypothesis (Python) and fast-check (TypeScript).

    Go PBT is handled by the built-in 'go test -fuzz' (Go 1.18+) — no install needed.
    Both packages are best-effort: failure does not block installation.
    """
    ok = True

    if not command_exists("hypothesis"):
        if not _run_bash_with_retry("uv tool install hypothesis", timeout=UV_TOOL_INSTALL_TIMEOUT):
            ok = False

    if not command_exists("fast-check"):
        try:
            result = subprocess.run(
                ["npm", "list", "-g", "fast-check", "--depth=0"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0 or "fast-check" not in result.stdout:
                if not _run_bash_with_retry(
                    npm_global_cmd("npm install -g fast-check"),
                    timeout=GLOBAL_NPM_INSTALL_TIMEOUT,
                ):
                    ok = False
        except Exception:
            if not _run_bash_with_retry(
                npm_global_cmd("npm install -g fast-check"),
                timeout=GLOBAL_NPM_INSTALL_TIMEOUT,
            ):
                ok = False

    return ok


def _is_agent_browser_ready() -> bool:
    """Check if agent-browser is installed and Chrome is available."""
    if not command_exists("agent-browser"):
        return False

    try:
        result = subprocess.run(
            ["agent-browser", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def install_agent_browser() -> bool:
    """Install or update agent-browser for headless browser automation.

    On Linux ARM64, Chrome for Testing has no builds — install system chromium
    via apt instead. On other Linux, use --with-deps. On macOS, plain install.
    """
    had_browser = _is_agent_browser_ready()

    if not _run_bash_with_retry(npm_global_cmd("npm install -g agent-browser")):
        return False

    if had_browser:
        return True

    if is_linux_arm64():
        if not command_exists("apt-get"):
            return False
        return _run_bash_with_retry(
            "sudo -n apt-get update -qq && sudo -n apt-get install -y -qq chromium",
            timeout=180,
        )

    import platform

    install_cmd = "agent-browser install --with-deps" if platform.system() == "Linux" else "agent-browser install"
    return _run_bash_with_retry(install_cmd, timeout=300)


def _get_playwright_cache_dirs() -> list[Path]:
    """Get possible Playwright cache directories for the current platform."""
    import platform as _platform

    dirs = []
    if _platform.system() == "Darwin":
        dirs.append(Path.home() / "Library" / "Caches" / "ms-playwright")
    dirs.append(Path.home() / ".cache" / "ms-playwright")
    return dirs


def _is_playwright_cli_ready() -> bool:
    """Check if playwright-cli is installed and Chromium is available."""
    if not command_exists("playwright-cli"):
        return False

    for cache_dir in _get_playwright_cache_dirs():
        if not cache_dir.exists():
            continue
        for chromium_dir in cache_dir.glob("chromium-*"):
            if (chromium_dir / "INSTALLATION_COMPLETE").exists():
                return True
        for chromium_dir in cache_dir.glob("chromium_headless_shell-*"):
            if (chromium_dir / "INSTALLATION_COMPLETE").exists():
                return True

    return False


def install_playwright_cli() -> bool:
    """Install or update playwright-cli for advanced browser automation.

    Always runs npm install to keep up to date. Skips browser download
    only if Chromium is already present in the Playwright cache.
    """
    if not _run_bash_with_retry(
        npm_global_cmd("npm install -g @playwright/cli@latest"),
        timeout=GLOBAL_NPM_INSTALL_TIMEOUT,
    ):
        return False

    if _is_playwright_cli_ready():
        return True

    try:
        result = subprocess.run(
            ["playwright-cli", "install-browser", "chromium"],
            capture_output=True,
            text=True,
            timeout=600,
        )
        return result.returncode == 0
    except Exception:
        return False


@dataclass
class _InstallTask:
    """A single install operation that can run in parallel."""

    name: str
    key: str
    fn: Callable[..., bool]
    args: tuple[Any, ...] = ()


@dataclass
class _InstallResult:
    """Result from a parallel install operation."""

    name: str
    key: str
    success: bool
    error: str = ""


def _run_install_silent(task: _InstallTask) -> _InstallResult:
    """Run an install function without UI, capturing result and error.

    Thread-safe: uses thread-local error tracking.
    """
    _clear_last_error()
    try:
        success = task.fn(*task.args) if task.args else task.fn()
        return _InstallResult(
            name=task.name,
            key=task.key,
            success=success,
            error=_get_last_error() if not success else "",
        )
    except _SudoReauthNeeded:
        return _InstallResult(
            name=task.name,
            key=task.key,
            success=False,
            error="sudo credentials expired — re-run the installer",
        )
    except Exception as e:
        return _InstallResult(
            name=task.name,
            key=task.key,
            success=False,
            error=str(e),
        )


def _run_parallel_installs(
    tasks: list[_InstallTask],
    ui: Any,
    max_workers: int = 4,
) -> list[str]:
    """Run multiple installs in parallel with a progress bar.

    Returns list of installed keys.
    """
    if not tasks:
        return []

    installed: list[str] = []
    results: dict[str, _InstallResult] = {}

    if ui:
        with ui.progress(len(tasks), f"Installing {len(tasks)} packages") as progress:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(_run_install_silent, task): task for task in tasks}
                for future in as_completed(futures):
                    task = futures[future]
                    results[task.key] = future.result()
                    progress.advance()
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_run_install_silent, task): task for task in tasks}
            for future in as_completed(futures):
                task = futures[future]
                results[task.key] = future.result()

    # Report results in original order
    for task in tasks:
        result = results[task.key]
        if result.success:
            if ui:
                ui.success(f"{result.name} installed")
            installed.append(result.key)
        else:
            if ui:
                if result.error:
                    last_line = result.error.strip().splitlines()[-1].strip()
                    ui.warning(f"Could not install {result.name} — please install manually")
                    ui.info(f"  Error: {last_line}")
                else:
                    ui.warning(f"Could not install {result.name} — please install manually")

    return installed


def _install_with_spinner(ui: Any, name: str, install_fn: Any, *args: Any) -> bool:
    """Run an installation function with a spinner.

    If sudo credentials expire mid-install, the spinner is stopped so the
    user can see the password prompt, credentials are re-primed, and the
    install is retried once.
    """
    _clear_last_error()
    if ui:
        try:
            with ui.spinner(f"Installing {name}..."):
                result = install_fn(*args) if args else install_fn()
        except _SudoReauthNeeded:
            ui.status("sudo credentials expired — re-authenticating...")
            if ensure_sudo_credentials():
                start_sudo_keepalive()
                try:
                    with ui.spinner(f"Installing {name}..."):
                        result = install_fn(*args) if args else install_fn()
                except _SudoReauthNeeded:
                    _thread_local.last_retry_stderr = "sudo credentials expired — re-run the installer"
                    result = False
            else:
                _thread_local.last_retry_stderr = "sudo credentials expired — re-run the installer"
                result = False
        if result:
            ui.success(f"{name} installed")
        else:
            error = _get_last_error()
            if error:
                last_line = error.strip().splitlines()[-1].strip()
                ui.warning(f"Could not install {name} - please install manually")
                ui.info(f"  Error: {last_line}")
            else:
                ui.warning(f"Could not install {name} - please install manually")
        return result
    else:
        try:
            return install_fn(*args) if args else install_fn()
        except _SudoReauthNeeded:
            if ensure_sudo_credentials():
                start_sudo_keepalive()
                try:
                    return install_fn(*args) if args else install_fn()
                except _SudoReauthNeeded:
                    _thread_local.last_retry_stderr = "sudo credentials expired — re-run the installer"
                    return False
            _thread_local.last_retry_stderr = "sudo credentials expired — re-run the installer"
            return False


def _install_plugin_dependencies(_project_dir: Path, ui: Any = None) -> bool:
    """Install plugin dependencies by running bun/npm install in the plugin folder.

    This installs all Node.js dependencies defined in plugin/package.json,
    which includes runtime dependencies for MCP servers and hooks.
    """
    from installer.steps.claude_files import get_claude_config_dir

    plugin_dir = get_claude_config_dir() / "pilot"

    if not plugin_dir.exists():
        if ui:
            ui.warning("Plugin directory not found - skipping plugin dependencies")
        return False

    package_json = plugin_dir / "package.json"
    if not package_json.exists():
        if ui:
            ui.warning("No package.json in plugin directory - skipping")
        return False

    if command_exists("bun"):
        return _run_bash_with_retry("bun install", cwd=plugin_dir)

    if command_exists("npm"):
        return _run_bash_with_retry("npm install", cwd=plugin_dir)

    return False


def _setup_pilot_memory(ui: Any) -> bool:
    """Setup pilot-memory (no-op, kept for compatibility)."""
    return True


def _extract_npx_package_name(package: str) -> str:
    """Extract npm package name without version/tag suffix.

    Examples: "fetcher-mcp" → "fetcher-mcp",
    "open-websearch@latest" → "open-websearch",
    "@upstash/context7-mcp" → "@upstash/context7-mcp",
    "@scope/pkg@1.0" → "@scope/pkg"
    """
    if package.startswith("@"):
        parts = package[1:].split("@", 1)
        return "@" + parts[0]
    return package.split("@", 1)[0]


def _is_npx_package_cached(package: str) -> bool:
    """Check if an npx package is already cached in ~/.npm/_npx/."""
    npx_cache = Path.home() / ".npm" / "_npx"
    if not npx_cache.exists():
        return False
    pkg_name = _extract_npx_package_name(package)
    for hash_dir in npx_cache.iterdir():
        candidate = hash_dir / "node_modules" / pkg_name
        if candidate.is_dir():
            return True
    return False


def _kill_proc(proc: subprocess.Popen[Any]) -> None:
    """Terminate a process, escalating to kill if needed."""
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)


def _precache_npx_mcp_servers(_ui: Any) -> bool:
    """Pre-cache npx-based MCP server packages so Claude Code can start them instantly.

    Reads .mcp.json from the plugin directory, finds servers that use npx,
    and installs each package into the npx cache using --package + -c "true".
    This ensures packages are fully installed (including all dependencies)
    before returning, avoiding the race condition of launching the actual
    server and killing it mid-install.
    """
    from installer.steps.claude_files import get_claude_config_dir

    mcp_config_path = get_claude_config_dir() / "pilot" / ".mcp.json"
    if not mcp_config_path.exists():
        return True

    try:
        config = json.loads(mcp_config_path.read_text())
    except (json.JSONDecodeError, OSError):
        return False

    servers = config.get("mcpServers", {})
    npx_packages: list[str] = []

    for server_config in servers.values():
        cmd = server_config.get("command", "")
        args = server_config.get("args", [])
        if cmd == "npx" and len(args) >= 2 and args[0] == "-y":
            npx_packages.append(args[1])

    uncached = [p for p in npx_packages if not _is_npx_package_cached(p)]
    if not uncached:
        return True

    procs: list[tuple[str, subprocess.Popen[Any]]] = []
    for package in uncached:
        try:
            proc = subprocess.Popen(
                ["npx", "-y", "--package", package, "-c", "true"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )
            procs.append((package, proc))
        except Exception:
            continue

    if not procs:
        return True

    max_wait = NPX_CACHE_WAIT_TIMEOUT
    for _, proc in procs:
        try:
            proc.wait(timeout=max_wait)
        except subprocess.TimeoutExpired:
            _kill_proc(proc)

    _fix_npx_peer_dependencies()
    return True


def _fix_npx_peer_dependencies() -> None:
    """Install missing peer dependencies in npx cache directories.

    open-websearch depends on @modelcontextprotocol/sdk which declares zod
    as a peer dependency. npm's npx cache doesn't always resolve peer deps,
    causing 'Cannot find package zod' at runtime. This installs zod into
    any cache dir that has open-websearch but is missing zod.
    """
    npx_cache = Path.home() / ".npm" / "_npx"
    if not npx_cache.exists():
        return
    for hash_dir in npx_cache.iterdir():
        nm = hash_dir / "node_modules"
        if (nm / "open-websearch").is_dir() and not (nm / "zod").is_dir():
            try:
                subprocess.run(
                    ["npm", "install", "zod"],
                    cwd=hash_dir,
                    capture_output=True,
                    timeout=60,
                )
            except Exception:
                pass


class DependenciesStep(BaseStep):
    """Step that installs all required dependencies."""

    name = "dependencies"

    def check(self, ctx: InstallContext) -> bool:
        """Always returns False - dependencies should always be checked."""
        return False

    def run(self, ctx: InstallContext) -> None:
        """Install all required dependencies.

        Runs in three phases:
        1. Foundation (sequential) — Claude Code, Node.js, uv (each depends on the previous)
        2. Tools (parallel) — independent npm/uv/curl installs run concurrently
        3. Post-install (sequential) — CodeGraph init, MCP cache (depend on phase 2 binaries)
        """
        global _allow_sudo_fallback
        ui = ctx.ui
        installed: list[str] = []
        try:
            requires_elevation = needs_sudo() or (is_linux_arm64() and command_exists("apt-get"))
            if requires_elevation and not ctx.non_interactive:
                _allow_sudo_fallback = True
                if ui:
                    ui.status("Some packages require elevated privileges — requesting sudo access...")
                if ensure_sudo_credentials():
                    start_sudo_keepalive()
                elif ui:
                    ui.warning("Could not obtain sudo credentials — some installations may fail")

            # --- Phase 1: Foundation (sequential — each depends on the previous) ---
            if _install_with_spinner(ui, "Claude Code", install_claude_code):
                installed.append("claude_code")

            if _install_with_spinner(ui, "Node.js", install_nodejs):
                installed.append("nodejs")

            if _install_with_spinner(ui, "uv", install_uv):
                installed.append("uv")

            # --- Phase 2: Independent tools (parallel) ---
            parallel_tasks = [
                _InstallTask("Python tools", "python_tools", install_python_tools),
                _InstallTask("Plugin dependencies", "plugin_deps", _install_plugin_dependencies, (ctx.project_dir, ui)),
                _InstallTask("vtsls (TypeScript LSP server)", "typescript_lsp", install_typescript_lsp),
                _InstallTask("prettier (TypeScript formatter)", "prettier", install_prettier),
                _InstallTask("golangci-lint (Go linter)", "golangci_lint", install_golangci_lint),
                _InstallTask("PBT tools (hypothesis, fast-check)", "pbt_tools", install_pbt_tools),
                _InstallTask("Probe (code search)", "probe", install_probe),
                _InstallTask("RTK (token optimizer)", "rtk", install_rtk),
                _InstallTask("CodeGraph (code intelligence)", "codegraph", install_codegraph),
                _InstallTask("better-sqlite3 (CodeGraph native backend)", "better_sqlite3", install_better_sqlite3),
                _InstallTask("context-mode plugin", "context_mode_plugin", install_context_mode_plugin),
                _InstallTask("Codex plugin", "codex_plugin", install_codex_plugin),
                _InstallTask("Chrome DevTools MCP plugin", "chrome_devtools_plugin", install_chrome_devtools_plugin),
            ]

            installed.extend(_run_parallel_installs(parallel_tasks, ui))

            if _setup_pilot_memory(ui):
                installed.append("pilot_memory")

            # Browser tools run sequentially (shared Chromium download cache)
            if _install_with_spinner(ui, "agent-browser (browser automation)", install_agent_browser):
                installed.append("agent_browser")

            if _install_with_spinner(ui, "playwright-cli (advanced browser automation)", install_playwright_cli):
                installed.append("playwright_cli")

            # --- Phase 3: Post-install (depends on phase 2 binaries) ---
            needs_work = codegraph_needs_work(ctx.project_dir)
            if needs_work and ui:
                ui.status("Initializing CodeGraph (indexing may take a few minutes)...")
            if initialize_codegraph(ctx.project_dir):
                if needs_work and ui:
                    ui.success("CodeGraph project initialized")
                installed.append("codegraph_init")
            elif needs_work and ui:
                ui.warning("Could not initialize CodeGraph — please run 'codegraph init -i' manually")

            if _install_with_spinner(ui, "MCP server packages", _precache_npx_mcp_servers, ui):
                installed.append("mcp_npx_cache")

            ctx.config["installed_dependencies"] = installed
        finally:
            stop_sudo_keepalive()
            _allow_sudo_fallback = False
