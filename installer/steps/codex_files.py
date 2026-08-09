"""Installer step for Codex CLI-specific file installation.

Installs hooks, skills, MCP config, and rules for Codex users.
Only runs when the Codex CLI binary is detected on the system.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import Any, Callable

from installer.claude_paths import get_claude_config_dir
from installer.context import InstallContext
from installer.platform_utils import is_codex_installed
from installer.steps.base import BaseStep

_CODEX_REVIEW_AGENT_MODEL = "codex-auto-review"

# Codex silently truncates AGENTS.md beyond project_doc_max_bytes (default
# 32 KiB; openai/codex config.schema.json / DEFAULT_PROJECT_DOC_MAX_BYTES).
# Pilot merges its full rule set into ~/.codex/AGENTS.md (~88 KB and growing),
# so without this the majority of the rules never reach Codex startup
# instructions. Raise the ceiling to 1 MiB (a cap, not a preallocation, so it
# only costs context up to the file's actual size) to guarantee every rule
# primes startup rather than being dropped at the 32 KiB cutoff.
_CODEX_PROJECT_DOC_MAX_BYTES = 1024 * 1024


def _claude_rules_dir_or_none() -> Path | None:
    """Rules dir in the active Claude profile, for the Codex rules fallback.

    Returns None when CLAUDE_CONFIG_DIR is invalid, matching the caller's existing
    `Path | None` handling for its other two candidates, so the fallback is simply
    skipped rather than reading the personal profile. Read-only fallback; the
    primary source is ~/.pilot/rules.
    """
    try:
        return get_claude_config_dir() / "rules"
    except ValueError:
        return None


def _get_codex_config_dir() -> Path:
    """Resolve the Codex config directory, respecting CODEX_HOME env var."""
    env_dir = os.environ.get("CODEX_HOME")
    if env_dir:
        p = Path(env_dir)
        if not p.is_absolute():
            raise ValueError(f"CODEX_HOME must be an absolute path, got: {env_dir}")
        return p
    return Path.home() / ".codex"


# Per-sub-install label formatters used by CodexFilesStep.run(). Each
# receives the sub-install's return value (count or bool) and returns the
# success-line string, or None to suppress (for empty/no-op installs).
def _label_hook_events(n: int) -> str | None:
    return f"Configured {n} hook events" if n else None


def _label_adapted_skills(n: int) -> str | None:
    return f"Installed {n} adapted skills" if n else None


def _label_review_agents(n: int) -> str | None:
    return f"Installed {n} review agents" if n else None


def _label_codex_config(changed: bool) -> str | None:
    return "Configured Codex config.toml" if changed else None


def _label_mcp_servers(n: int) -> str | None:
    return f"Configured {n} MCP servers" if n else None


def _label_codex_rules(n: int) -> str | None:
    return f"Merged {n} rule files AGENTS.md" if n else None


class _CodexReport:
    """Accumulator + reporter for CodexFilesStep sub-installs.

    Replaces the previous pattern of six ``if ui and n_X: ui.success(...)``
    inline calls scattered across :meth:`CodexFilesStep.run`. Adding a new
    sub-install now means: write the method, write its label formatter, and
    add ONE ``report.record(...)`` call — no extra UI gates or format strings
    to thread through ``run()``.
    """

    def __init__(self, ui: Any) -> None:
        self._ui = ui

    def record(self, value: int | bool, formatter: "Callable[[Any], str | None]") -> None:
        if self._ui is None:
            return
        line = formatter(value)
        if line:
            self._ui.success(line)


class CodexFilesStep(BaseStep):
    """Install Pilot Shell assets for Codex CLI."""

    name = "codex_files"

    def check(self, ctx: InstallContext) -> bool:
        return False

    def run(self, ctx: InstallContext) -> None:
        ui = ctx.ui
        if not is_codex_installed():
            if ui:
                ui.info("Codex CLI not detected — skipping Codex file installation")
            return

        if ui:
            ui.status("Installing Codex CLI integration...")

        # Sub-install pipeline: each entry is (method, label-formatter).
        # The formatter receives the method's return value and produces the
        # success line, or None to suppress (when nothing was installed).
        # Errors are caught around the right slice — TOML errors only happen
        # inside the config/mcp methods.
        report = _CodexReport(ui)

        try:
            report.record(self._install_codex_hooks(ctx), _label_hook_events)
            report.record(self._install_codex_skills(ctx), _label_adapted_skills)
            report.record(self._install_codex_agents(ctx), _label_review_agents)
        except ValueError as e:
            if ui:
                ui.warning(f"Skipping Codex file installation: {e}")
            return

        try:
            report.record(self._install_codex_config(ctx), _label_codex_config)
            report.record(self._install_codex_mcp(ctx), _label_mcp_servers)
        except _TomlStructureError as e:
            if ui:
                ui.warning(f"Skipping Codex TOML config due to structure error: {e}")
        except ValueError as e:
            if ui:
                ui.warning(f"Skipping Codex file installation: {e}")
            return

        try:
            report.record(self._install_codex_rules(ctx), _label_codex_rules)
        except ValueError as e:
            if ui:
                ui.warning(f"Skipping Codex file installation: {e}")

        self._heal_codex_config_env(ui)

    def _heal_codex_config_env(self, ui: Any = None) -> None:
        """Proactively heal the managed env block in ~/.codex/config.toml.

        ``pilot sync-env --codex-only`` collapses any duplicated / left-over
        ``[shell_environment_policy.set]`` managed region into one (the
        idempotent ``_merge_env_block``), so a config corrupted by a pre-fix
        version is repaired the moment the user updates, not lazily on the
        next Codex session start. The reactive session-start heal
        (``codex_skill_sync.py``) fires only on matcher ``"startup"`` and only
        when the license is valid, so resume-only, Codex-only, or lapsed-license
        users could otherwise keep the duplicate-key breakage that aborts Codex
        ``skills/list``.

        ``--codex-only`` keeps this scoped to the Codex config: it does NOT
        touch Claude Code settings (a Codex-only user must not get
        ~/.claude/settings.json as a side effect) and its exit code reflects the
        Codex heal, so a genuine failure is surfaced here rather than swallowed.

        Subprocesses the freshly-installed binary rather than importing launcher
        logic (package boundary). Non-fatal: a sync hiccup must never break the
        install.
        """
        pilot_bin = Path.home() / ".pilot" / "bin" / "pilot"
        if not pilot_bin.is_file():
            return

        try:
            result = subprocess.run(
                [str(pilot_bin), "sync-env", "--codex-only"],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (subprocess.SubprocessError, OSError):
            return

        if result.returncode != 0 and ui:
            detail = (result.stderr or result.stdout or "").strip().splitlines()
            reason = detail[-1] if detail else f"exit {result.returncode}"
            ui.warning(f"Could not heal ~/.codex/config.toml env block: {reason}")

    def _install_codex_hooks(self, ctx: InstallContext) -> int:
        """Install hooks.json for Codex CLI. Returns # of hook events configured."""
        codex_dir = _get_codex_config_dir()
        codex_dir.mkdir(parents=True, exist_ok=True)

        template_path = self._find_codex_hooks_template(ctx)
        if template_path is None:
            return 0

        try:
            incoming = json.loads(template_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 0

        return self._merge_codex_hooks(codex_dir, incoming)

    def _find_codex_hooks_template(self, ctx: InstallContext) -> Path | None:
        """Locate the codex_hooks.json template from install source."""
        if ctx.local_mode and ctx.local_repo_dir:
            candidate = ctx.local_repo_dir / "pilot" / "hooks" / "codex_hooks.json"
            if candidate.is_file():
                return candidate

        pilot_home = Path.home() / ".pilot"
        candidate = pilot_home / "hooks" / "codex_hooks.json"
        if candidate.is_file():
            return candidate

        return None

    def _merge_codex_hooks(self, codex_dir: Path, incoming: dict[str, Any]) -> int:
        """Write or merge hooks into ~/.codex/hooks.json.

        Pilot Shell-managed hook entries are identified by commands containing
        '/.pilot/' in their command string. User-added entries are preserved.
        Returns the number of Pilot-managed hook events present in the result.
        """
        hooks_file = codex_dir / "hooks.json"
        incoming_hooks = incoming.get("hooks", {})

        if not hooks_file.exists():
            hooks_file.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write(hooks_file, json.dumps(incoming, indent=2) + "\n")
            return len(incoming_hooks)

        try:
            existing = json.loads(hooks_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _atomic_write(hooks_file, json.dumps(incoming, indent=2) + "\n")
            return len(incoming_hooks)

        existing_hooks = existing.get("hooks", {})

        merged: dict[str, list[Any]] = {}

        all_events = set(existing_hooks.keys()) | set(incoming_hooks.keys())
        for event in all_events:
            existing_entries = existing_hooks.get(event, [])
            incoming_entries = incoming_hooks.get(event, [])

            user_entries = [e for e in existing_entries if not _is_pilot_managed_entry(e)]

            merged[event] = incoming_entries + user_entries

        result = dict(existing)
        result["hooks"] = merged
        _atomic_write(hooks_file, json.dumps(result, indent=2) + "\n")
        return len(incoming_hooks)

    def _install_codex_mcp(self, ctx: InstallContext) -> int:
        """Generate MCP server config in ~/.codex/config.toml from .mcp.json.

        Returns the number of MCP servers written into the managed block.
        """
        pilot_home = Path.home() / ".pilot"
        mcp_json_path = pilot_home / ".mcp.json"
        if not mcp_json_path.is_file():
            return 0

        try:
            mcp_data = json.loads(mcp_json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 0

        toml_block = _mcp_json_to_toml(mcp_data)
        if not toml_block.strip():
            return 0

        codex_dir = _get_codex_config_dir()
        codex_dir.mkdir(parents=True, exist_ok=True)
        config_path = codex_dir / "config.toml"

        existing = ""
        if config_path.is_file():
            try:
                existing = config_path.read_text(encoding="utf-8")
            except OSError:
                pass

        managed_names = _managed_server_names(mcp_data)
        preserved, dropped = _clean_mcp_config(existing, managed_names)
        if dropped and ctx.ui:
            ctx.ui.warning(
                "Replacing [mcp_servers.*] tables found outside the pilot-managed block in "
                f"~/.codex/config.toml: {', '.join(sorted(dropped))} (leftovers of an earlier "
                "corrupted write, or a user copy of a Pilot-managed server -- re-add custom "
                "servers under a different name)"
            )

        managed_block = f"\n{_MCP_MARKER_START}\n{toml_block}{_MCP_MARKER_END}\n"
        final = preserved.rstrip("\n") + "\n" + managed_block if preserved.strip() else managed_block.lstrip("\n")
        try:
            tomllib.loads(final)
        except tomllib.TOMLDecodeError as e:
            # Attribute the failure: a pre-existing user syntax error needs a
            # different remediation than a bug in our own surgery/generation.
            try:
                tomllib.loads(existing)
            except tomllib.TOMLDecodeError as e_existing:
                raise _TomlStructureError(
                    "existing ~/.codex/config.toml is invalid TOML and could not be healed "
                    f"(fix it manually and re-run): {e_existing}"
                ) from e_existing
            raise _TomlStructureError(f"generated config.toml would be invalid: {e}") from e
        _atomic_write(config_path, final)
        return len(managed_names)

    def _install_codex_rules(self, ctx: InstallContext) -> int:
        """Merge Pilot Shell rules into ~/.codex/AGENTS.md between markers."""
        rules_dir: Path | None = None
        if ctx.local_mode and ctx.local_repo_dir:
            candidate = ctx.local_repo_dir / "pilot" / "rules"
            if candidate.is_dir():
                rules_dir = candidate
        if rules_dir is None:
            pilot_home = Path.home() / ".pilot"
            candidate = pilot_home / "rules"
            if candidate.is_dir():
                rules_dir = candidate
        if rules_dir is None:
            rules_dir = _claude_rules_dir_or_none()
        if rules_dir is None or not rules_dir.is_dir():
            return 0

        rule_files = sorted(f for f in rules_dir.iterdir() if f.suffix == ".md" and f.is_file())
        if not rule_files:
            return 0

        parts: list[str] = []
        for rule_file in rule_files:
            try:
                content = rule_file.read_text(encoding="utf-8").strip()
                adapted = _adapt_invocation_syntax(content)
                parts.append(adapted)
            except OSError:
                continue

        if not parts:
            return 0

        codex_preamble = (
            "## Codex Compatibility\n\n"
            "This agent is Codex CLI. The following Claude Code tools are NOT available:\n\n"
            "- **`AskUserQuestion`** — not supported. When instructions say to use `AskUserQuestion`, "
            "instead present numbered options as plain text and ask the user to reply with a number or "
            "free text. Format: `1. Option A — description\\n2. Option B — description\\n"
            "Reply with a number or type your preference:`\n"
            "- **`suppressOutput`** — parsed but not implemented in hook responses. Never rely on it.\n"
            "- **`systemMessage`** — surfaced as a UI warning or event-stream message; do not use it for hidden context.\n\n"
            "Tool name mapping: `Edit`/`Write` → `apply_patch` (Codex uses `apply_patch` for file edits, "
            "but `Edit`/`Write` work as aliases).\n\n"
            "Skill invocation: use `$skill-name` (not `/skill-name`).\n"
        )

        managed_content = codex_preamble + "\n\n" + "\n\n".join(parts)
        block = f"<!-- PILOT:START -->\n{managed_content}\n<!-- PILOT:END -->"

        codex_dir = _get_codex_config_dir()
        codex_dir.mkdir(parents=True, exist_ok=True)
        agents_md = codex_dir / "AGENTS.md"

        if agents_md.is_file():
            try:
                existing = agents_md.read_text(encoding="utf-8")
            except OSError:
                existing = ""

            if "<!-- PILOT:START -->" in existing and "<!-- PILOT:END -->" in existing:
                start = existing.index("<!-- PILOT:START -->")
                end = existing.index("<!-- PILOT:END -->") + len("<!-- PILOT:END -->")
                if start < end:
                    final = existing[:start] + block + existing[end:]
                else:
                    final = existing.rstrip("\n") + "\n\n" + block + "\n"
            else:
                final = existing.rstrip("\n") + "\n\n" + block + "\n"
        else:
            final = block + "\n"

        _atomic_write(agents_md, final)
        return len(rule_files)

    def _install_codex_config(self, ctx: InstallContext) -> bool:
        """Set Codex full-access config in ~/.codex/config.toml.

        Top-level keys are inserted before the first [section] header so they
        don't accidentally land inside an unrelated TOML table.
        """
        _ = ctx
        codex_dir = _get_codex_config_dir()
        codex_dir.mkdir(parents=True, exist_ok=True)
        config_path = codex_dir / "config.toml"

        existing = ""
        if config_path.is_file():
            try:
                existing = config_path.read_text(encoding="utf-8")
            except OSError:
                pass

        required_top_level = {
            "approval_policy": '"never"',
            "sandbox_mode": '"danger-full-access"',
            "model_reasoning_effort": '"xhigh"',
            "model_reasoning_summary": '"concise"',
            "personality": '"pragmatic"',
            "check_for_update_on_startup": "true",
            "file_opener": '"vscode"',
            # Suppress the "Under-development features enabled" warning that Codex
            # prints because we opt into unstable features (e.g. mentions_v2) below.
            "suppress_unstable_features_warning": "true",
            # Load the full merged AGENTS.md instead of Codex's 32 KiB default.
            "project_doc_max_bytes": str(_CODEX_PROJECT_DOC_MAX_BYTES),
        }
        changed = False
        section_match = re.search(r"(?m)^\[", existing)
        top_level_scope = existing[: section_match.start()] if section_match else existing
        for key, value in required_top_level.items():
            if not re.search(rf"(?m)^{re.escape(key)}\s*=", top_level_scope):
                existing = _insert_top_level_key(existing, key, value)
                sm = re.search(r"(?m)^\[", existing)
                top_level_scope = existing[: sm.start()] if sm else existing
                changed = True

        deprecated_keys = ["bypass_hook_trust"]
        for key in deprecated_keys:
            pattern = rf"(?m)^{re.escape(key)}\s*=\s*[^\n]*\n?"
            if re.search(pattern, top_level_scope):
                existing = re.sub(pattern, "", existing)
                changed = True

        required_features = {
            "apps": "false",
            "hooks": "true",
            "memories": "true",
            "mentions_v2": "true",
            "plugins": "true",
            "terminal_resize_reflow": "true",
            "tool_call_mcp_elicitation": "true",
            "tool_search": "true",
            "tool_suggest": "true",
            "undo": "true",
        }
        existing, features_changed = _ensure_section_keys(existing, "features", required_features)
        changed = changed or features_changed

        if "[sandbox_workspace_write]" not in existing:
            if existing and not existing.endswith("\n\n"):
                existing = existing.rstrip("\n") + "\n\n"
            existing += "[sandbox_workspace_write]\nnetwork_access = true\n"
            changed = True

        required_tui = {
            "status_line": '["project-name", "model-with-reasoning", "branch-changes", "context-used", "task-progress", "run-state", "five-hour-limit", "weekly-limit"]',
            "status_line_use_colors": "true",
        }
        existing, tui_changed = _ensure_section_keys(existing, "tui", required_tui)
        changed = changed or tui_changed

        if "[notice]" not in existing:
            if existing and not existing.endswith("\n\n"):
                existing = existing.rstrip("\n") + "\n\n"
            existing += "[notice]\nhide_full_access_warning = true\n"
            changed = True
        elif "hide_full_access_warning" not in existing:
            idx = existing.index("[notice]")
            newline_idx = existing.find("\n", idx)
            end = newline_idx + 1 if newline_idx != -1 else len(existing)
            insert_prefix = "" if end == 0 or existing[end - 1 : end] == "\n" else "\n"
            existing = existing[:end] + insert_prefix + "hide_full_access_warning = true\n" + existing[end:]
            changed = True

        if changed:
            _validate_toml_structure(existing)
            _atomic_write(config_path, existing)
        return changed

    _CODEX_SUPPORTED_SKILLS = frozenset(
        {
            "spec",
            "spec-plan",
            "spec-bugfix-plan",
            "spec-implement",
            "spec-verify",
            "spec-bugfix-verify",
            "fix",
            "build",
            "prd",
            "benchmark",
            "setup-rules",
            "create-skill",
        }
    )

    _CODEX_STALE_SKILLS = frozenset({"bot-boot", "bot-channel-task", "bot-defaults", "bot-heartbeat", "bot-jobs"})
    # Keep in sync with pilot/hooks/codex_skill_sync.py:_SUPPORTED_REVIEW_AGENTS
    # (.claude/rules/pilot-shell-codex-skill-sync.md). Names only -- the sibling
    # `<name>-codex.md` files are companion prompt templates for `task
    # --prompt-file`, not custom agents, so they are never built.
    _CODEX_MANAGED_REVIEW_AGENTS = frozenset({"build-review", "changes-review", "spec-review"})

    def _install_codex_skills(self, ctx: InstallContext) -> int:
        """Install supported Pilot Shell skills to ~/.agents/skills/ for Codex.

        Only skills in _CODEX_SUPPORTED_SKILLS ship to Codex. Bot skills (bot-boot,
        bot-channel-task, bot-defaults, bot-heartbeat, bot-jobs) depend on Claude Code
        cron/remote-control, so they stay CC-only. Stale bot-* skills from older
        installs are cleaned up. Returns the number of adapted SKILL.md files
        successfully written.
        """
        # Source is the ACTIVE Claude profile: with CLAUDE_CONFIG_DIR set, a
        # hardcoded ~/.claude finds nothing and Codex silently gets zero skills.
        # ~/.agents is NOT relocatable (Codex derives it from $HOME).
        try:
            claude_skills_dir = get_claude_config_dir() / "skills"
        except ValueError:
            return 0
        agents_skills_dir = Path.home() / ".agents" / "skills"

        if not claude_skills_dir.is_dir():
            return 0

        if agents_skills_dir.is_dir():
            for name in self._CODEX_STALE_SKILLS:
                stale = agents_skills_dir / name
                if stale.is_dir():
                    shutil.rmtree(stale, ignore_errors=True)

        decomposed = [
            p
            for p in sorted(claude_skills_dir.iterdir())
            if p.is_dir() and (p / "manifest.json").is_file() and p.name in self._CODEX_SUPPORTED_SKILLS
        ]

        written = 0
        for skill_dir in decomposed:
            try:
                codex_content = build_codex_skill_md(skill_dir)
            except Exception as e:
                if ctx.ui:
                    ctx.ui.warning(f"Failed to build SKILL.md for {skill_dir.name}: {e}")
                continue

            dest_dir = agents_skills_dir / skill_dir.name
            dest_dir.mkdir(parents=True, exist_ok=True)
            _atomic_write(dest_dir / "SKILL.md", codex_content)
            written += 1
        return written

    def _find_codex_review_agents_source(self, ctx: InstallContext) -> Path | None:
        """Locate the source markdown agents used to build Codex custom agents."""
        if getattr(ctx, "local_mode", False) is True:
            local_repo_dir = ctx.local_repo_dir
            if local_repo_dir is not None:
                candidate = local_repo_dir / "pilot" / "agents"
                if candidate.is_dir():
                    return candidate

        try:
            candidate = get_claude_config_dir() / "agents"
        except ValueError:
            return None
        if candidate.is_dir():
            return candidate

        return None

    def _install_codex_agents(self, ctx: InstallContext) -> int:
        """Install Pilot-managed review agents as Codex custom-agent TOML files.

        Returns the number of agent files written.
        """
        source_dir = self._find_codex_review_agents_source(ctx)
        if source_dir is None:
            return 0

        codex_agents_dir = _get_codex_config_dir() / "agents"
        codex_agents_dir.mkdir(parents=True, exist_ok=True)

        written = 0
        for agent_name in sorted(self._CODEX_MANAGED_REVIEW_AGENTS):
            source = source_dir / f"{agent_name}.md"
            if not source.is_file():
                continue
            try:
                codex_content = build_codex_review_agent_toml(source)
            except Exception as e:
                if ctx.ui:
                    ctx.ui.warning(f"Failed to build Codex agent for {agent_name}: {e}")
                continue
            target = codex_agents_dir / f"{agent_name}.toml"
            if target.exists() and not _is_pilot_managed_codex_review_agent(target):
                if ctx.ui:
                    ctx.ui.warning(f"Preserving user-created Codex agent: {target}")
                continue
            _atomic_write(target, codex_content)
            written += 1
        return written


def _ensure_section_keys(
    content: str,
    section: str,
    keys: dict[str, str],
) -> tuple[str, bool]:
    """Ensure keys exist inside a ``[section]`` table, creating it if needed.

    Returns (updated_content, changed). Existing user values are preserved —
    only missing keys are added.
    """
    header = f"[{section}]"
    changed = False

    if header not in content:
        if content and not content.endswith("\n\n"):
            content = content.rstrip("\n") + "\n\n"
        lines = [header]
        for k, v in keys.items():
            lines.append(f"{k} = {v}")
        content += "\n".join(lines) + "\n"
        return content, True

    idx = content.index(header)
    end = content.index("\n", idx) + 1

    next_section = re.search(r"(?m)^\[", content[end:])
    section_end = end + next_section.start() if next_section else len(content)
    section_text = content[end:section_end]

    for key, value in keys.items():
        if not re.search(rf"(?m)^{re.escape(key)}\s*=", section_text):
            content = content[:end] + f"{key} = {value}\n" + content[end:]
            insertion_len = len(f"{key} = {value}\n")
            end += insertion_len
            section_end += insertion_len
            section_text = content[end:section_end]
            changed = True

    return content, changed


def _insert_top_level_key(content: str, key: str, value: str) -> str:
    """Insert a key=value pair into the top-level scope of a TOML string.

    Inserts before the first ``[section]`` header so the key doesn't
    accidentally land inside an unrelated table.
    """
    line = f"{key} = {value}\n"
    m = re.search(r"(?m)^\[", content)
    if m:
        pos = m.start()
        prefix = content[:pos]
        if prefix and not prefix.endswith("\n"):
            prefix += "\n"
        return prefix + line + content[pos:]
    if content and not content.endswith("\n"):
        content += "\n"
    return content + line


# Also hard-coded in uninstall.sh (marker_pairs + its grep gate) and
# test_uninstall_sh.py -- keep the literals in sync when editing.
_MCP_MARKER_START = "# --- pilot-shell managed MCP servers ---"
_MCP_MARKER_END = "# --- end pilot-shell managed MCP servers ---"

# Matches the [mcp_servers.<name>] table header and ANY of its sub-tables
# (.env, .headers, ...). Name may be bare or quoted; whitespace inside the
# brackets is tolerated. No naive '#'-split: a comment after ']' simply isn't
# consumed, and quoted names containing '#' survive.
_MCP_TABLE_HEADER_RE = re.compile(r"^\[\s*mcp_servers\s*\.\s*(?:\"([^\"]+)\"|'([^']+)'|([^.\s\]\"']+))\s*[.\]]")

_TOML_HEADER_LINE_RE = re.compile(r"^\[.*\]\s*(?:#.*)?$")


def _mcp_table_name(line: str) -> str | None:
    """Return the server name when `line` is a table header of
    [mcp_servers.<name>] or any of its sub-tables, else None. Sibling of the
    env-block header check in pilot/hooks/codex_skill_sync.py."""
    m = _MCP_TABLE_HEADER_RE.match(line.strip())
    if not m:
        return None
    name = next((g for g in m.groups() if g is not None), None)
    return name or None


def _managed_server_names(mcp_data: dict[str, Any]) -> set[str]:
    """Server names Pilot will (re)write -- the single authority for which
    entries _mcp_json_to_toml emits and _clean_mcp_config strips."""
    servers = mcp_data.get("mcpServers", {})
    if not isinstance(servers, dict):
        return set()
    return {name for name, config in servers.items() if isinstance(config, dict)}


def _split_marker_lines(existing: str) -> list[str]:
    """splitlines(), additionally splitting any line that embeds a marker
    mid-line into (prefix, marker, suffix) lines. Heals the historical
    newline-loss corruption where a marker got concatenated with adjacent
    content (e.g. '# --- pilot-shell managed MCP servers ---[mcp_servers.x]'),
    which whole-line marker matching would otherwise miss entirely."""
    out: list[str] = []
    for raw in existing.splitlines():
        rest = raw
        while True:
            if rest.strip() in (_MCP_MARKER_START, _MCP_MARKER_END):
                out.append(rest.strip())
                break
            hits = [
                (idx, marker) for marker in (_MCP_MARKER_END, _MCP_MARKER_START) if (idx := rest.find(marker)) != -1
            ]
            if not hits:
                out.append(rest)
                break
            idx, marker = min(hits)
            prefix = rest[:idx]
            if prefix.strip():
                out.append(prefix)
            out.append(marker)
            rest = rest[idx + len(marker) :]
            if not rest.strip():
                break
    return out


def _clean_mcp_config(existing: str, managed_names: set[str]) -> tuple[str, set[str]]:
    """Strip prior pilot-shell managed MCP state from existing config.toml content.

    Returns (cleaned_content, dropped_names): dropped_names are managed-name
    tables removed OUTSIDE any marker region -- content the user could regard
    as their own (leftovers of a lost marker, or a hand-written override), so
    the caller surfaces a warning for them. Two removal mechanisms, both
    required:

    - Marker regions: every well-formed START..END region is dropped whole.
      This is the only mechanism that removes tables whose names Pilot no
      longer ships (region content is Pilot-owned regardless of name). The
      forward scan is non-greedy: an orphaned START whose next marker is
      another START (or nothing) drops just the marker line, never the user
      content after it. Lone END markers are dropped as single lines.
    - Managed-name tables: any [mcp_servers.<name>] table (and its
      sub-tables) matching a name Pilot is about to (re)write is dropped
      wherever it appears. Without this, a table left outside the markers by
      a lost START marker would duplicate the freshly appended block -- a
      duplicate key/table that aborts Codex startup loading config.toml.
      The skip stops at header-shaped lines only, so multi-line values whose
      continuation happens to start with '[' don't truncate the removal.

    Line endings are normalized to LF; user bytes are otherwise preserved
    verbatim (deliberately no blank-line rewriting -- a global newline
    collapse previously corrupted multi-line TOML string values).
    """
    lines = _split_marker_lines(existing)

    cleaned: list[str] = []
    dropped: set[str] = set()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == _MCP_MARKER_START:
            nxt = next(
                (j for j in range(i + 1, len(lines)) if lines[j].strip() in (_MCP_MARKER_START, _MCP_MARKER_END)),
                None,
            )
            if nxt is not None and lines[nxt].strip() == _MCP_MARKER_END:
                i = nxt + 1  # well-formed region: drop it whole
            else:
                i += 1  # orphaned START: drop the marker line, keep what follows
            continue
        if stripped == _MCP_MARKER_END:
            i += 1  # lone END marker
            continue
        name = _mcp_table_name(lines[i])
        if name is not None and name in managed_names:
            dropped.add(name)
            i += 1
            while i < len(lines) and not _TOML_HEADER_LINE_RE.match(lines[i].strip()):
                i += 1
            continue
        cleaned.append(lines[i])
        i += 1

    return "\n".join(cleaned), dropped


def _mcp_json_to_toml(mcp_data: dict[str, Any]) -> str:
    """Convert .mcp.json mcpServers dict to TOML [mcp_servers.*] sections."""
    servers = mcp_data.get("mcpServers", {})
    if not isinstance(servers, dict):
        return ""

    lines: list[str] = []
    for name, config in servers.items():
        if not isinstance(config, dict):
            continue
        lines.append(f"[mcp_servers.{name}]")

        server_type = config.get("type", "")
        if server_type == "http" or "url" in config:
            url = config.get("url", "")
            if url:
                lines.append(f"url = {_toml_string(url)}")
        else:
            cmd = config.get("command", "")
            if cmd:
                lines.append(f"command = {_toml_string(cmd)}")
            args = config.get("args")
            if isinstance(args, list) and args:
                args_str = ", ".join(_toml_string(str(a)) for a in args)
                lines.append(f"args = [{args_str}]")

        env = config.get("env")
        if isinstance(env, dict) and env:
            lines.append("")
            lines.append(f"[mcp_servers.{name}.env]")
            for k, v in env.items():
                lines.append(f"{k} = {_toml_string(str(v))}")

        lines.append("")

    return "\n".join(lines) + "\n" if lines else ""


_PILOT_SKILL_NAMES = frozenset(
    {
        "spec",
        "spec-plan",
        "spec-bugfix-plan",
        "spec-implement",
        "spec-verify",
        "spec-bugfix-verify",
        "setup-rules",
        "create-skill",
        "prd",
        "benchmark",
        "fix",
        "build",
        "bot-boot",
        "bot-channel-task",
        "bot-defaults",
        "bot-heartbeat",
        "bot-jobs",
    }
)

_SKILL_INVOCATION_RE = re.compile(
    r"(?<![a-zA-Z0-9_/])/"
    r"(" + "|".join(re.escape(s) for s in sorted(_PILOT_SKILL_NAMES, key=len, reverse=True)) + r")"
    r"(?![a-zA-Z0-9_/])"
)


def build_codex_skill_md(skill_dir: Path) -> str:
    """Build a Codex-format SKILL.md with YAML frontmatter from a decomposed skill.

    Reads the manifest.json, builds the skill content (same as Claude Code),
    extracts name/description from the orchestrator's frontmatter, prepends
    Codex-style YAML frontmatter, and adapts invocation syntax (/ → $).
    """
    from installer.skill_builder import build_skill_md

    content = build_skill_md(skill_dir)

    name, description = _extract_skill_metadata(content)
    description = _adapt_invocation_syntax(description)

    adapted = _adapt_invocation_syntax(content)

    if adapted.startswith("---\n"):
        end = adapted.find("\n---", 3)
        if end != -1:
            adapted = adapted[end + 4 :].lstrip("\n")

    frontmatter = f"---\nname: {name}\ndescription: {description}\n---\n\n"
    return frontmatter + adapted


def build_codex_review_agent_toml(agent_file: Path) -> str:
    """Build a Codex custom-agent TOML file from a Pilot review-agent markdown file."""
    content = agent_file.read_text(encoding="utf-8")
    metadata, body = _extract_agent_metadata(content)
    name = metadata.get("name") or agent_file.stem
    description = metadata.get("description") or f"Pilot {name} review agent."
    instructions = _adapt_review_agent_instructions_for_codex(body)
    return (
        "# pilot-shell managed Codex review agent\n"
        f"name = {_toml_string(name)}\n"
        f"description = {_toml_string(description)}\n"
        f"model = {_toml_string(_CODEX_REVIEW_AGENT_MODEL)}\n"
        f"developer_instructions = {_toml_string(instructions)}\n"
    )


def _extract_agent_metadata(content: str) -> tuple[dict[str, str], str]:
    """Extract simple YAML frontmatter key/value pairs from a markdown agent."""
    if not content.startswith("---\n"):
        return {}, content

    end = content.find("\n---", 3)
    if end == -1:
        return {}, content

    metadata: dict[str, str] = {}
    for line in content[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, content[end + 4 :].lstrip("\n")


def _adapt_review_agent_instructions_for_codex(body: str) -> str:
    """Convert Claude Code output-file review agents into Codex final-response agents."""
    adapted = body
    adapted = adapted.replace(" (excluding the final Write)", "")
    adapted = adapted.replace(" → Write output (1)", " → final JSON response")
    adapted = re.sub(
        r"\*\*⛔ MANDATORY: Write output\.\*\*.*?(?=\n\n)",
        (
            "**⛔ MANDATORY: Return output.** Your final response MUST be the JSON object. "
            "At the tool-call budget, stop exploring and return what you have. "
            "No final JSON means the parent workflow cannot continue."
        ),
        adapted,
        flags=re.DOTALL,
    )
    adapted = adapted.replace("### 4. Write Output", "### 4. Return Output")
    adapted = adapted.replace("### 5. Write Output", "### 5. Return Output")
    adapted = adapted.replace(
        "**Write JSON to `output_path` as your FINAL action.**", "**Return JSON as your final response.**"
    )
    adapted = adapted.replace(
        "Write JSON to `output_path` as your FINAL action.", "Return JSON as your final response."
    )
    adapted = adapted.replace("The orchestrator provides:", "The parent prompt provides:")
    adapted = adapted.replace(", `output_path`", "")
    adapted = adapted.replace("`output_path`, ", "")
    adapted = adapted.replace("`output_path`", "the parent prompt")
    adapted = adapted.replace("write what you have", "return what you have")
    adapted = adapted.replace("No file = orchestrator stalls.", "No final JSON = parent workflow cannot continue.")
    adapted = re.sub(r"\n{3,}", "\n\n", adapted).strip()
    return (
        "Pilot-managed Codex review agent. Return ONLY valid JSON as the final response. "
        "Do not write files, do not wrap JSON in markdown, and do not include commentary outside the JSON object.\n\n"
        + adapted
    )


def _toml_string(value: str) -> str:
    """Serialize a Python string as a TOML basic string."""
    return json.dumps(value)


def _is_pilot_managed_codex_review_agent(agent_file: Path) -> bool:
    try:
        content = agent_file.read_text(encoding="utf-8")
    except OSError:
        return False
    return "pilot-shell managed Codex review agent" in content or "Pilot-managed Codex review agent" in content


def _extract_skill_metadata(content: str) -> tuple[str, str]:
    """Extract name and description from Claude Code YAML frontmatter in skill content."""
    name = ""
    description = ""

    if content.startswith("---\n"):
        end = content.find("\n---", 3)
        if end != -1:
            fm_block = content[4:end]
            for line in fm_block.split("\n"):
                if line.startswith("name:"):
                    name = line[5:].strip()
                elif line.startswith("description:"):
                    description = line[12:].strip()

    return name or "unknown", description or ""


_CC_ONLY_RE = re.compile(
    r"<!-- CC-ONLY -->\n?.*?<!-- /CC-ONLY -->\n?",
    re.DOTALL,
)

_CODEX_BLOCK_RE = re.compile(
    r"<!-- CODEX-START\n(.*?)CODEX-END -->(?:\n?)",
    re.DOTALL,
)

_SKILL_CALL_RE = re.compile(
    r"Skill\(\s*(?:skill\s*=\s*)?['\"]([^'\"]+)['\"]\s*"
    r"(?:,\s*args\s*=\s*['\"]([^'\"]*)['\"])?\s*\)"
)

_ASK_USER_QUESTION_BLOCK_RE = re.compile(
    r"^(?P<indent>[ \t]*)AskUserQuestion\(\n(?P<body>.*?)(?=^[ \t]*\)\s*$)^[ \t]*\)\s*$",
    re.DOTALL | re.MULTILINE,
)


def _adapt_invocation_syntax(content: str) -> str:
    """Replace /skill-name with $skill-name and adapt Codex-incompatible tool references.

    Processing order:
    1. Strip ``<!-- CC-ONLY -->`` … ``<!-- /CC-ONLY -->`` blocks (CC-specific sections).
    2. Unwrap ``<!-- CODEX-START`` … ``CODEX-END -->`` blocks (Codex alternatives hidden as HTML comments).
    3. Replace ``Skill(skill='X', args='Y')`` calls with Codex skill-instruction handoffs.
    4. Replace ``/skill-name`` with ``$skill-name`` for user-facing references.
    5. Replace ``AskUserQuestion`` with plain-text alternative note.
    """
    adapted = _CC_ONLY_RE.sub("", content)

    adapted = _CODEX_BLOCK_RE.sub(lambda m: m.group(1), adapted)

    def _replace_skill_call(m: re.Match[str]) -> str:
        skill = m.group(1)
        args = m.group(2) or ""
        if args:
            return f"the `${skill}` skill instructions with arguments: `{args}`"
        return f"the `${skill}` skill instructions"

    adapted = _SKILL_CALL_RE.sub(_replace_skill_call, adapted)

    def _replace_ask_user_question_block(m: re.Match[str]) -> str:
        body = m.group("body").rstrip()
        return f"{m.group('indent')}Present numbered options in plain text using this prompt and option list:\n{body}"

    adapted = _ASK_USER_QUESTION_BLOCK_RE.sub(_replace_ask_user_question_block, adapted)

    adapted = _SKILL_INVOCATION_RE.sub(lambda m: "$" + m.group(1), adapted)
    adapted = adapted.replace(
        "AskUserQuestion(multiSelect: true)",
        "plain-text numbered options with multi-select",
    )
    for old, new in (
        ("`AskUserQuestion` tool", "`plain-text numbered options` format"),
        ("AskUserQuestion tool", "plain-text numbered options format"),
        ("`AskUserQuestion` calls", "`plain-text numbered options` prompts"),
        ("AskUserQuestion calls", "plain-text numbered options prompts"),
        ("`AskUserQuestion` call", "`plain-text numbered options` prompt"),
        ("AskUserQuestion call", "plain-text numbered options prompt"),
    ):
        adapted = adapted.replace(old, new)
    adapted = adapted.replace(
        "AskUserQuestion",
        "plain-text numbered options",
    )
    return adapted


def _is_pilot_managed_entry(entry: dict[str, Any]) -> bool:
    """Check if a hook entry is Pilot Shell-managed (references ~/.pilot/ paths)."""
    for hook in entry.get("hooks", []):
        cmd = hook.get("command", "")
        if "/.pilot/" in cmd:
            return True
    return False


class _TomlStructureError(Exception):
    """Raised when generated TOML content has structural problems."""


_TOML_SECTION_RE = re.compile(r"\[[\w._-]+\]")
_TOML_QUOTED_RE = re.compile(r'"[^"]*"')


def _validate_toml_structure(content: str) -> None:
    """Validate TOML content won't cause Codex parse errors.

    Checks every line for a [section] header appearing mid-line — the
    corruption pattern that concatenates sections when newlines are lost.
    Quoted strings are blanked before matching so values like
    "semble[mcp]" don't trigger false positives.
    Raises _TomlStructureError with the offending line number and content.
    """
    for lineno, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        unquoted = _TOML_QUOTED_RE.sub("", stripped)
        match = _TOML_SECTION_RE.search(unquoted)
        if match and match.start() > 0:
            raise _TomlStructureError(f"line {lineno}: section header not at start of line: {stripped!r}")


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(str(tmp), str(path))
