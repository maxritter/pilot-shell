"""Shared utilities and type definitions for the benchmark skill scripts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, NotRequired, TypedDict, cast, final

CONDITIONAL_LOADING_FIELDS: tuple[str, ...] = ("path", "paths")
_CONDITIONAL_FIELD_RE = re.compile(r"^(?P<name>path|paths)\s*:")


def strip_conditional_loading_frontmatter(content: str) -> tuple[str, list[str]]:
    """Remove ``path:`` / ``paths:`` keys from a markdown file's YAML frontmatter.

    Pilot rules use ``paths:`` to scope when Claude Code loads them (e.g.
    ``paths: ["**/*.py"]`` for Python-only rules). When a benchmark's prompts
    don't fall inside the glob, the rule stays dormant in the ``with`` config
    and the delta collapses to zero — measuring activation, not the rule's
    actual content. Stripping these fields from the copy installed into the
    ``with`` sandbox forces unconditional loading so we measure the rule itself.

    Returns ``(modified_content, removed_fields)``. ``modified_content`` is
    returned unchanged when the file has no frontmatter or no conditional
    fields. Multi-line list values (``paths:\\n  - a\\n  - b``) are stripped
    along with their indented continuation lines.
    """
    if not content:
        return content, []
    lines = content.split("\n")
    if lines[0].strip() != "---":
        return content, []

    end_idx: int | None = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return content, []

    removed: list[str] = []
    new_front: list[str] = []
    skipping = False
    for line in lines[1:end_idx]:
        if skipping:
            if line and line[0] in (" ", "\t"):
                continue
            skipping = False

        match = _CONDITIONAL_FIELD_RE.match(line)
        if match is not None:
            removed.append(match.group("name"))
            skipping = True
            continue
        new_front.append(line)

    if not removed:
        return content, []

    new_lines = [lines[0], *new_front, *lines[end_idx:]]
    return "\n".join(new_lines), removed

VALID_TARGET_TYPES: set[str] = {"skill", "rules"}

TargetType = Literal["skill", "rules"]
ConfigKind = Literal["with", "without"]
ConfigDirName = Literal["with_skill", "without_skill"]


class TargetConfig(TypedDict):
    """`target` block in evals.json after validation by `load_target_config`."""

    type: TargetType
    path: NotRequired[str]
    name: NotRequired[str]


class EvalSpec(TypedDict, total=False):
    """One eval entry in `evals.json`."""

    id: int
    name: str
    prompt: str
    expected_output: str
    expectations: list[str]
    assertions: list[str]


class EvalsFile(TypedDict, total=False):
    """Top-level shape of an `evals.json` file."""

    target: TargetConfig
    evals: list[EvalSpec]


class ResultUsage(TypedDict, total=False):
    """`usage` block of a stream-json result event."""

    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int


class ResultEvent(TypedDict, total=False):
    """Stream-json `result` event shape (subset that we read)."""

    type: str
    duration_ms: int
    duration_api_ms: int
    usage: ResultUsage
    total_cost_usd: float
    is_error: bool
    result: str
    stop_reason: str
    session_id: str


class ParsedResult(TypedDict):
    """Normalized parse of a result event — never has missing keys."""

    duration_ms: int
    duration_api_ms: int | None
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    total_tokens: int
    total_cost_usd: float | None
    is_error: bool
    result_text: str
    stop_reason: str | None
    session_id: str | None


@final
@dataclass(frozen=True, slots=True)
class ExecuteSuccess:
    """Successful executor run with timing + token counts."""

    duration_ms: int
    total_tokens: int
    run_dir: str
    success: Literal[True] = True


@final
@dataclass(frozen=True, slots=True)
class ExecuteFailure:
    """Failed executor run with a reason code."""

    reason: str
    success: Literal[False] = False


ExecuteResult = ExecuteSuccess | ExecuteFailure


@final
@dataclass(frozen=True, slots=True)
class GraderSuccess:
    """Grader produced a verdict that parsed as JSON."""

    grading: dict[str, object]
    graded: Literal[True] = True


@final
@dataclass(frozen=True, slots=True)
class GraderFailure:
    """Grader failed to produce or parse a verdict."""

    reason: str
    graded: Literal[False] = False


GraderResult = GraderSuccess | GraderFailure


class StatBlock(TypedDict):
    """mean/stddev/min/max for one numeric metric."""

    mean: float
    stddev: float
    min: float
    max: float


class RunSummaryEntry(TypedDict):
    pass_rate: StatBlock
    time_seconds: StatBlock
    tokens: StatBlock


class DeltaEntry(TypedDict):
    pass_rate: str
    time_seconds: str
    tokens: str


class BenchmarkMetadata(TypedDict, total=False):
    skill_name: str
    skill_path: str
    target_type: str
    target_name: str
    target_path: str
    executor_model: str
    analyzer_model: str
    timestamp: str
    evals_run: list[int]
    runs_per_configuration: int


class BenchmarkSnapshot(TypedDict):
    metadata: BenchmarkMetadata
    runs: list[dict[str, object]]
    run_summary: dict[str, RunSummaryEntry | DeltaEntry]
    notes: list[str]


class ParsedRunRecord(TypedDict):
    """Per-run record used during aggregation."""

    eval_id: int
    run_number: int
    pass_rate: float
    time_seconds: float
    tokens: int
    expectations: list[dict[str, object]]
    notes: list[str]
    errors: NotRequired[int]
    config: NotRequired[str]


class EmbeddedFile(TypedDict, total=False):
    """One file rendered into the review HTML.

    `type` discriminates the union: text|image|pdf|xlsx|binary|error.
    """

    name: str
    type: str
    content: str
    mime: str
    data_uri: str
    data_b64: str


class RunData(TypedDict):
    """One run as discovered by the viewer's `find_runs` helper."""

    id: str
    prompt: str
    eval_id: int | None
    outputs: list[EmbeddedFile]
    grading: dict[str, object] | None


class PreviousIteration(TypedDict):
    """Carried forward from a previous run for side-by-side display."""

    feedback: str
    outputs: list[EmbeddedFile]


def _find_skill_doc(skill_path: Path) -> Path | None:
    """Return the SKILL.md or orchestrator.md path if either exists."""
    for name in ("SKILL.md", "orchestrator.md"):
        candidate = skill_path / name
        if candidate.exists():
            return candidate
    return None


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse SKILL.md (or orchestrator.md), returning (name, description, full_content).

    Pilot-style decomposed skills use orchestrator.md instead of SKILL.md, so both
    filenames are probed.
    """
    target_file = _find_skill_doc(skill_path)
    if target_file is None:
        raise FileNotFoundError(f"No SKILL.md or orchestrator.md in {skill_path}")

    content = target_file.read_text()
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{target_file.name} missing frontmatter (no opening ---)")

    end_idx: int | None = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError(f"{target_file.name} missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:") :].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:") :].strip()
            if value in (">", "|", ">-", "|-"):
                continuation_lines: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (
                    frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")
                ):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            description = value.strip('"').strip("'")
        i += 1

    return name, description, content


def parse_skill_frontmatter_field(skill_path: Path, field: str) -> str | None:
    """Extract a single scalar field from SKILL.md / orchestrator.md frontmatter.

    Used for reading `model:` etc. without a full YAML dependency.
    Returns None when the file or field is missing.
    """
    target_file = _find_skill_doc(skill_path)
    if target_file is None:
        return None

    lines = target_file.read_text().split("\n")
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        if line.strip() == "---":
            return None
        prefix = f"{field}:"
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip('"').strip("'")
    return None


def load_target_config(evals_path: Path) -> TargetConfig:
    """Read the `target` block from an evals.json file.

    Returns the target dict with `type` guaranteed. Legacy skill-creator
    evals.json files without a target block default to ``{"type": "skill"}``.
    """
    data: Any = json.loads(Path(evals_path).read_text())
    raw_target = data.get("target") if isinstance(data, dict) else None
    if not isinstance(raw_target, dict):
        raw_target = {}
    raw_typed = cast(dict[str, Any], raw_target)
    raw_typed.setdefault("type", "skill")
    target_type = raw_typed["type"]
    if not isinstance(target_type, str) or target_type not in VALID_TARGET_TYPES:
        raise ValueError(f"target.type must be one of {sorted(VALID_TARGET_TYPES)}, got {target_type!r}")
    return cast(TargetConfig, raw_typed)


_MODEL_ALIASES: dict[str, str] = {
    "opus": "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5-20251001",
}

DEFAULT_FALLBACK_MODEL = "claude-sonnet-4-6"


def resolve_executor_model(target: TargetConfig) -> str:
    """Pick the executor model for a benchmark run.

    Priority:
      1. `model:` in the target skill's frontmatter (alias → ID).
      2. DEFAULT_FALLBACK_MODEL for rules targets or skills without a model field.

    Aliases (`opus`, `sonnet`, `haiku`) translate to current model IDs;
    explicit `claude-…` IDs in frontmatter pass through unchanged.
    """
    if target.get("type") != "skill":
        return DEFAULT_FALLBACK_MODEL
    target_path = target.get("path")
    if not target_path:
        return DEFAULT_FALLBACK_MODEL
    declared = parse_skill_frontmatter_field(Path(target_path).expanduser(), "model")
    if declared is None:
        return DEFAULT_FALLBACK_MODEL
    declared = declared.strip()
    if declared.startswith("claude-"):
        return declared
    return _MODEL_ALIASES.get(declared.lower(), DEFAULT_FALLBACK_MODEL)
