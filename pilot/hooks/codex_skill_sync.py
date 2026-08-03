"""SessionStart hook: rebuild Codex SKILL.md files from CC skill sources.

Runs on every session start for both Claude Code (async) and Codex (sync).
If the license is invalid or deactivated, deletes built SKILL.md files so
unlicensed users cannot invoke the skills.

The build logic is self-contained (no launcher/installer imports) to respect
the package boundary. It replicates the same transformations as
``installer.steps.codex_files.build_codex_skill_md``:
  1. Concatenate orchestrator + steps from manifest.json
  2. Strip ``<!-- CC-ONLY -->`` blocks
  3. Unwrap ``<!-- CODEX-START ... CODEX-END -->`` blocks
  4. Transform ``Skill()`` calls to Codex skill-instruction handoffs
  5. Replace ``/skill-name`` with ``$skill-name``
  6. Replace ``AskUserQuestion`` with Codex alternative note
  7. Prepend Codex YAML frontmatter
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.util import claude_config_dir, pilot_owned_skill_names  # noqa: E402

_SUPPORTED_SKILLS = frozenset(
    {
        "spec",
        "spec-plan",
        "spec-bugfix-plan",
        "spec-implement",
        "spec-verify",
        "spec-bugfix-verify",
        "fix",
        "prd",
        "benchmark",
        "setup-rules",
        "create-skill",
    }
)

_SUPPORTED_REVIEW_AGENTS = frozenset({"changes-review", "spec-review"})
_CODEX_REVIEW_AGENT_MODEL = "codex-auto-review"

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


def _get_codex_config_dir() -> Path:
    env_dir = os.environ.get("CODEX_HOME")
    if env_dir:
        path = Path(env_dir)
        if not path.is_absolute():
            raise ValueError(f"CODEX_HOME must be an absolute path, got: {env_dir}")
        return path
    return Path.home() / ".codex"


_CC_ONLY_RE = re.compile(r"<!-- CC-ONLY -->\n?.*?<!-- /CC-ONLY -->\n?", re.DOTALL)
_CODEX_BLOCK_RE = re.compile(r"<!-- CODEX-START\n(.*?)CODEX-END -->(?:\n?)", re.DOTALL)
_SKILL_CALL_RE = re.compile(
    r"Skill\(\s*(?:skill\s*=\s*)?['\"]([^'\"]+)['\"]\s*"
    r"(?:,\s*args\s*=\s*['\"]([^'\"]*)['\"])?\s*\)"
)

_ASK_USER_QUESTION_BLOCK_RE = re.compile(
    r"^(?P<indent>[ \t]*)AskUserQuestion\(\n(?P<body>.*?)(?=^[ \t]*\)\s*$)^[ \t]*\)\s*$",
    re.DOTALL | re.MULTILINE,
)


def _check_license() -> bool:
    pilot_bin = Path.home() / ".pilot" / "bin" / "pilot"
    if not pilot_bin.is_file():
        return True
    try:
        result = subprocess.run(
            [str(pilot_bin), "verify", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        data = json.loads(result.stdout)
        return data.get("valid", False)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
        return False


def _canonicalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _build_skill(skill_dir: Path) -> str | None:
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    orch_path = skill_dir / manifest.get("orchestrator", "orchestrator.md")
    if not orch_path.is_file():
        return None

    parts = [orch_path.read_text(encoding="utf-8")]
    for step in manifest.get("steps", []):
        step_path = skill_dir / step["file"]
        if not step_path.is_file():
            return None
        parts.append(step_path.read_text(encoding="utf-8"))

    return _canonicalize("\n\n".join(parts))


def _extract_metadata(content: str) -> tuple[str, str]:
    if content.startswith("---\n"):
        end = content.find("\n---", 3)
        if end != -1:
            fm = content[4:end]
            name = desc = ""
            for line in fm.split("\n"):
                if line.startswith("name:"):
                    name = line[5:].strip()
                elif line.startswith("description:"):
                    desc = line[12:].strip()
            return name or "unknown", desc
    return "unknown", ""


def _adapt(content: str) -> str:
    adapted = _CC_ONLY_RE.sub("", content)
    adapted = _CODEX_BLOCK_RE.sub(lambda m: m.group(1), adapted)

    def _replace_skill_call(m: re.Match[str]) -> str:
        skill = m.group(1)
        args = m.group(2) or ""
        if args:
            return f"the `${skill}` skill instructions with arguments: `{args}`"
        return f"the `${skill}` skill instructions"

    adapted = _SKILL_CALL_RE.sub(_replace_skill_call, adapted)
    adapted = _ASK_USER_QUESTION_BLOCK_RE.sub(
        lambda m: (
            f"{m.group('indent')}Present numbered options in plain text using this prompt and option list:\n"
            f"{m.group('body').rstrip()}"
        ),
        adapted,
    )
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


def _build_codex_skill(skill_dir: Path) -> str | None:
    content = _build_skill(skill_dir)
    if content is None:
        return None
    name, desc = _extract_metadata(content)
    desc = _adapt(desc)
    adapted = _adapt(content)
    if adapted.startswith("---\n"):
        end = adapted.find("\n---", 3)
        if end != -1:
            adapted = adapted[end + 4 :].lstrip("\n")
    return f"---\nname: {name}\ndescription: {desc}\n---\n\n{adapted}"


def _build_codex_review_agent(agent_file: Path) -> str | None:
    """Build a Codex custom-agent TOML file from a Pilot review-agent markdown file."""
    if not agent_file.is_file():
        return None
    try:
        content = agent_file.read_text(encoding="utf-8")
    except OSError:
        return None
    metadata, body = _extract_agent_metadata(content)
    name = metadata.get("name") or agent_file.stem
    description = metadata.get("description") or f"Pilot {name} review agent."
    instructions = _adapt_review_agent_instructions(body)
    return (
        "# pilot-shell managed Codex review agent\n"
        f"name = {_toml_string(name)}\n"
        f"description = {_toml_string(description)}\n"
        f"model = {_toml_string(_CODEX_REVIEW_AGENT_MODEL)}\n"
        f"developer_instructions = {_toml_string(instructions)}\n"
    )


def _extract_agent_metadata(content: str) -> tuple[dict[str, str], str]:
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


def _adapt_review_agent_instructions(body: str) -> str:
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
    return json.dumps(value)


def _is_pilot_managed_codex_review_agent(agent_file: Path) -> bool:
    try:
        content = agent_file.read_text(encoding="utf-8")
    except OSError:
        return False
    return "pilot-shell managed Codex review agent" in content or "Pilot-managed Codex review agent" in content


def _scoped_pilot_skill_names() -> frozenset[str]:
    """Pilot skill allowlist, narrowed to manifest-tracked skills when available.

    When ``<config dir>/.pilot-manifest.json`` lists installed skills, only skills
    Pilot actually installed are eligible for removal — a user skill that happens
    to share a Pilot name (e.g. their own ``fix``) is preserved. When the manifest
    is absent/unreadable, fall back to the static allowlist (legacy behavior).
    """
    owned = pilot_owned_skill_names()
    if owned:
        return frozenset(_PILOT_SKILL_NAMES & owned)
    return _PILOT_SKILL_NAMES


def _remove_codex_skills() -> int:
    agents_dir = Path.home() / ".agents" / "skills"
    removed = 0
    for skill_name in _scoped_pilot_skill_names():
        skill_md = agents_dir / skill_name / "SKILL.md"
        if skill_md.is_file():
            skill_md.unlink()
            removed += 1
    return removed


def _remove_codex_review_agents() -> int:
    agents_dir = _get_codex_config_dir() / "agents"
    removed = 0
    for agent_name in _SUPPORTED_REVIEW_AGENTS:
        agent_file = agents_dir / f"{agent_name}.toml"
        if agent_file.is_file() and _is_pilot_managed_codex_review_agent(agent_file):
            agent_file.unlink()
            removed += 1
    return removed


def _sync_codex_skills() -> tuple[int, int]:
    claude_dir = claude_config_dir()
    if claude_dir is None:
        return 0, 0

    cc_skills = claude_dir / "skills"
    # ~/.agents is NOT relocatable: Codex derives it from the home directory and
    # exposes no override (verified against codex-cli 0.144.5). CODEX_HOME only
    # governs ~/.codex.
    agents_dir = Path.home() / ".agents" / "skills"
    built = 0
    failed = 0

    if not cc_skills.is_dir():
        return 0, 0

    for skill_name in _SUPPORTED_SKILLS:
        skill_dir = cc_skills / skill_name
        if not skill_dir.is_dir() or not (skill_dir / "manifest.json").is_file():
            continue
        try:
            codex_content = _build_codex_skill(skill_dir)
            if codex_content is None:
                failed += 1
                continue
            dest = agents_dir / skill_name
            dest.mkdir(parents=True, exist_ok=True)
            tmp = dest / "SKILL.md.tmp"
            tmp.write_text(codex_content, encoding="utf-8")
            os.replace(str(tmp), str(dest / "SKILL.md"))
            built += 1
        except Exception:
            failed += 1

    return built, failed


def _sync_codex_review_agents() -> tuple[int, int]:
    claude_dir = claude_config_dir()
    if claude_dir is None:
        return 0, 0

    source_dir = claude_dir / "agents"
    dest_dir = _get_codex_config_dir() / "agents"
    built = 0
    failed = 0

    if not source_dir.is_dir():
        return 0, 0

    for agent_name in _SUPPORTED_REVIEW_AGENTS:
        source = source_dir / f"{agent_name}.md"
        if not source.is_file():
            continue
        try:
            codex_content = _build_codex_review_agent(source)
            if codex_content is None:
                failed += 1
                continue
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp = dest_dir / f"{agent_name}.toml.tmp"
            tmp.write_text(codex_content, encoding="utf-8")
            os.replace(str(tmp), str(dest_dir / f"{agent_name}.toml"))
            built += 1
        except Exception:
            failed += 1

    return built, failed


_ENV_MARKER_START = "# --- pilot-shell managed env vars ---"
_ENV_MARKER_END = "# --- end pilot-shell managed env vars ---"
_ENV_SECTION_HEADER = "[shell_environment_policy.set]"


def _merge_env_block(existing: str, env_lines: list[str]) -> str:
    """Merge the pilot-managed env block into config.toml content.

    A TOML table may only be declared once, so when the config already has a
    [shell_environment_policy.set] header the managed lines are inserted inside
    that table; only otherwise is a self-contained block (header inside the
    markers) appended.

    The merge is idempotent and self-healing: every prior managed region is
    removed (not just the first), every [shell_environment_policy.set]
    declaration is collapsed into one, and any managed key left in that table
    outside the markers is dropped before the fresh block is written. Without
    this, managed state left behind by a double-write/race, a lost marker, or a
    manual edit would be emitted twice -- a duplicate key, or a duplicate table
    header -- and Codex aborts startup with a "duplicate key" error loading
    config.toml.
    """
    managed_keys = {line.split("=", 1)[0].strip() for line in env_lines}
    lines = existing.splitlines()

    # Drop every managed region, not just the first. Older formats kept the
    # section header inside the markers, so it is removed together with the
    # region. Marker pairs are matched explicitly so an orphaned marker can
    # never swallow unrelated config; a leftover marker comment is dropped alone.
    cleaned: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i] == _ENV_MARKER_START:
            end = next((j for j in range(i + 1, len(lines)) if lines[j] == _ENV_MARKER_END), None)
            if end is not None:
                i = end + 1
                continue
        if lines[i] in (_ENV_MARKER_START, _ENV_MARKER_END):
            i += 1
            continue
        cleaned.append(lines[i])
        i += 1

    # Collapse every [shell_environment_policy.set] declaration into a single
    # managed table. Declaring that table twice is itself a fatal TOML error,
    # and a managed key repeated inside it is the "duplicate key" crash, so each
    # table's surviving (non-managed) keys are pulled out, every [set] header is
    # dropped, and one managed table is re-emitted at the position of the first.
    # Scoped to that table, so an identically-named key elsewhere is untouched.
    body_keys: list[str] = []
    rest: list[str] = []
    insert_at: int | None = None
    i = 0
    while i < len(cleaned):
        if cleaned[i].split("#", 1)[0].strip() == _ENV_SECTION_HEADER:
            if insert_at is None:
                insert_at = len(rest)
            i += 1
            while i < len(cleaned):
                inner = cleaned[i].split("#", 1)[0].strip()
                if inner.startswith("[") and inner.endswith("]"):
                    break
                if cleaned[i].strip() and cleaned[i].split("=", 1)[0].strip() not in managed_keys:
                    body_keys.append(cleaned[i])
                i += 1
            continue
        rest.append(cleaned[i])
        i += 1

    if insert_at is not None:
        rest[insert_at:insert_at] = [_ENV_SECTION_HEADER, _ENV_MARKER_START, *env_lines, _ENV_MARKER_END, *body_keys]
    else:
        while rest and not rest[-1].strip():
            rest.pop()
        rest += ["", _ENV_MARKER_START, _ENV_SECTION_HEADER, *env_lines, _ENV_MARKER_END]
    return "\n".join(rest) + "\n"


def _sync_codex_env_vars() -> int:
    """Read Console settings and inject PILOT_* env vars into Codex config."""
    config_path = Path.home() / ".pilot" / "config.json"
    codex_config = _get_codex_config_dir() / "config.toml"

    if not codex_config.is_file():
        return 0

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
    except (OSError, json.JSONDecodeError):
        raw = {}

    spec = raw.get("specWorkflow", {})
    reviewers = raw.get("reviewerAgents", {})
    codex_rev = raw.get("codexReviewers", {})

    env_vars = {
        "PILOT_BRANCH_ISOLATION_ENABLED": "true" if spec.get("branchIsolation", True) else "false",
        "PILOT_PLAN_QUESTIONS_ENABLED": "true" if spec.get("askQuestionsDuringPlanning", True) else "false",
        "PILOT_PLAN_APPROVAL_ENABLED": "true" if spec.get("planApproval", True) else "false",
        # PILOT_MODEL_SWITCH_MODE is intentionally NOT emitted for Codex:
        # Model Switching (opusplan + EnterPlanMode/ExitPlanMode, manual /model
        # pauses) is Claude-Code-only. Codex runs plan -> implement -> verify
        # continuously on the active Codex model.
        "PILOT_SPEC_REVIEW_ENABLED": "true" if reviewers.get("specReview", True) else "false",
        "PILOT_CHANGES_REVIEW_ENABLED": "true" if reviewers.get("changesReview", True) else "false",
        "PILOT_CODEX_SPEC_REVIEW_ENABLED": "true" if codex_rev.get("specReview", False) else "false",
        "PILOT_CODEX_CHANGES_REVIEW_ENABLED": "true" if codex_rev.get("changesReview", False) else "false",
    }

    env_lines = [f'{k} = "{v}"' for k, v in sorted(env_vars.items())]

    try:
        existing = codex_config.read_text(encoding="utf-8")
    except OSError:
        return 0

    new_content = _merge_env_block(existing, env_lines)

    if new_content != existing:
        tmp = codex_config.with_suffix(".toml.tmp")
        tmp.write_text(new_content, encoding="utf-8")
        os.replace(str(tmp), str(codex_config))
        return len(env_vars)
    return 0


def main() -> None:
    try:
        codex_config_dir = _get_codex_config_dir()
    except ValueError as e:
        print(json.dumps({"continue": True, "systemMessage": f"Skipping Codex sync: {e}"}))
        return

    codex_bin = codex_config_dir / "bin" / "codex"
    codex_on_path = any((Path(p) / "codex").is_file() for p in os.environ.get("PATH", "").split(os.pathsep) if p)
    if not codex_bin.is_file() and not codex_on_path:
        print(json.dumps({"continue": True}))
        return

    valid = _check_license()

    if valid:
        built, failed = _sync_codex_skills()
        built_agents, failed_agents = _sync_codex_review_agents()
        env_synced = _sync_codex_env_vars()
        msg = f"Codex skills synced: {built} built"
        if failed:
            msg += f", {failed} failed"
        if built_agents or failed_agents:
            msg += f", review agents: {built_agents} built"
        if failed_agents:
            msg += f", {failed_agents} failed"
        if env_synced:
            msg += f", {env_synced} env vars"
        print(json.dumps({"continue": True, "systemMessage": msg}))
    else:
        removed = _remove_codex_skills() + _remove_codex_review_agents()
        msg = f"License invalid — removed {removed} Codex managed asset(s)" if removed else ""
        print(json.dumps({"continue": True, "systemMessage": msg} if msg else {"continue": True}))


if __name__ == "__main__":
    main()
