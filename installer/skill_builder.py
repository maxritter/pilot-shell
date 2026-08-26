"""Skill builder for bundled and progressively disclosed SKILL.md artifacts.

Used in two places:
1. Directly inside the launcher package (launcher.customize invokes after overlay apply).
2. Via the `pilot skill-build` CLI subcommand — invoked by the installer as a subprocess
   during install, and by pre-commit hooks / equivalence tests in this repo.
"""

from __future__ import annotations

import json
import re
import runpy
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

MANIFEST_V2_FIELDS = frozenset(
    {
        "version",
        "orchestrator",
        "steps",
        "delivery",
        "targets",
        "visibility",
        "invocation",
        "parent",
        "evals",
        "platform",
    }
)
SUPPORTED_TARGETS = frozenset({"claude", "codex"})
# Pilot's sequential workflows are deliberately bundled into one runtime artifact
# so agents do not emit a visible file read for every phase. Keep a generous
# runaway-size guard without forcing those workflows back to progressive reads.
COMPILED_LINE_LIMIT = 1_500
COMPILED_WORD_LIMIT = 20_000
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,127}$")


class BuildError(Exception):
    """Raised when a skill manifest is invalid or fragments cannot be assembled."""


@dataclass(frozen=True)
class SkillFinding:
    """One skill-contract finding."""

    skill: str
    rule: str
    message: str
    path: str | None = None

    def as_dict(self) -> dict[str, str]:
        payload = {"skill": self.skill, "rule": self.rule, "message": self.message}
        if self.path is not None:
            payload["path"] = self.path
        return payload


@dataclass(frozen=True)
class SkillMetrics:
    """Source and compiled size metrics for one validated skill."""

    name: str
    version: int
    delivery: str
    targets: tuple[str, ...]
    source_files: int
    source_lines: int
    source_words: int
    compiled_bytes: int
    compiled_lines: int
    compiled_words: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "delivery": self.delivery,
            "targets": list(self.targets),
            "source": {
                "files": self.source_files,
                "lines": self.source_lines,
                "words": self.source_words,
            },
            "compiled": {
                "bytes": self.compiled_bytes,
                "lines": self.compiled_lines,
                "words": self.compiled_words,
            },
        }


@dataclass
class SkillValidationReport:
    """Read-only validation result for one skill or a skill catalog."""

    errors: list[SkillFinding] = field(default_factory=list)
    warnings: list[SkillFinding] = field(default_factory=list)
    info: list[SkillFinding] = field(default_factory=list)
    skills: list[SkillMetrics] = field(default_factory=list)
    unreadable: bool = False

    @property
    def exit_code(self) -> int:
        if self.unreadable:
            return 2
        return 1 if self.errors else 0

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    def to_json(self) -> str:
        return json.dumps(
            {
                "ok": self.ok,
                "exit_code": self.exit_code,
                "errors": [finding.as_dict() for finding in self.errors],
                "warnings": [finding.as_dict() for finding in self.warnings],
                "info": [finding.as_dict() for finding in self.info],
                "skills": [metrics.as_dict() for metrics in self.skills],
            },
            indent=2,
        )


def canonicalize(text: str) -> str:
    """Normalize a skill markdown string for equivalence comparison and hashing.

    Applied identically to both equivalence checks (Tasks 4/5) and drift hashing (Task 2)
    so CRLF/trailing-whitespace/blank-line-reflow changes never trigger false drift.
    """
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    # Collapse runs of 2+ blank lines to a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace
    return text.strip()


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Read and parse manifest.json. Raises BuildError on invalid JSON."""
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise BuildError(f"cannot read manifest {manifest_path}: {e}") from e
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise BuildError(f"invalid JSON in {manifest_path}: {e}") from e
    if not isinstance(data, dict):
        raise BuildError(f"manifest {manifest_path} must be a JSON object")
    validate_manifest(data)
    return data


def _validate_relative_path(value: Any, label: str) -> str:
    """Return a safe POSIX-relative manifest path or raise BuildError."""
    if not isinstance(value, str) or not value:
        raise BuildError(f"{label} must be a non-empty string")
    if "\\" in value or "\x00" in value or ":" in value:
        raise BuildError(f"{label} must be a safe relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise BuildError(f"{label} must be a safe relative path")
    return value


def _validate_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise BuildError(f"{label} must match {_SAFE_ID.pattern}")
    return value


def _validate_steps(steps: Any, *, strict: bool = False) -> list[dict[str, Any]]:
    if not isinstance(steps, list):
        raise BuildError("manifest.steps must be a list")

    seen_ids: set[str] = set()
    for idx, step in enumerate(steps):
        if not isinstance(step, dict):
            raise BuildError(f"manifest.steps[{idx}] must be an object")
        if "id" not in step:
            raise BuildError(f"manifest.steps[{idx}] missing required key: id")
        if "file" not in step:
            raise BuildError(f"manifest.steps[{idx}] missing required key: file")
        if strict and set(step) != {"id", "file"}:
            unknown = sorted(set(step) - {"id", "file"})
            raise BuildError(f"manifest.steps[{idx}] has unknown key(s): {', '.join(unknown)}")
        step_id = _validate_identifier(step["id"], f"manifest.steps[{idx}].id")
        _validate_relative_path(step["file"], f"manifest.steps[{idx}].file")
        if step_id in seen_ids:
            raise BuildError(f"manifest has duplicate step id: {step_id}")
        seen_ids.add(step_id)
    return steps


def _validate_v2_metadata(data: dict[str, Any], steps: list[dict[str, Any]]) -> None:
    unknown = sorted(set(data) - MANIFEST_V2_FIELDS)
    if unknown:
        raise BuildError(f"manifest v2 has unknown key(s): {', '.join(unknown)}")

    for key in ("delivery", "targets", "visibility", "invocation"):
        if key not in data:
            raise BuildError(f"manifest v2 missing required key: {key}")

    if not isinstance(data["delivery"], str) or data["delivery"] not in {"bundled", "progressive"}:
        raise BuildError("manifest.delivery must be bundled or progressive")
    if data["delivery"] == "progressive" and not steps:
        raise BuildError("manifest.delivery progressive requires at least one step")

    targets = data["targets"]
    if (
        not isinstance(targets, list)
        or not targets
        or any(not isinstance(target, str) or target not in SUPPORTED_TARGETS for target in targets)
        or len(set(targets)) != len(targets)
    ):
        raise BuildError("manifest.targets must be a unique non-empty list containing claude and/or codex")
    if not isinstance(data["visibility"], str) or data["visibility"] not in {"public", "internal"}:
        raise BuildError("manifest.visibility must be public or internal")
    if not isinstance(data["invocation"], str) or data["invocation"] not in {"explicit", "implicit"}:
        raise BuildError("manifest.invocation must be explicit or implicit")

    if "parent" in data:
        _validate_identifier(data["parent"], "manifest.parent")
    if "evals" in data:
        _validate_relative_path(data["evals"], "manifest.evals")
    if "platform" not in data:
        return

    platform = data["platform"]
    if not isinstance(platform, dict):
        raise BuildError("manifest.platform must be an object")
    for target, metadata in platform.items():
        if target not in targets:
            raise BuildError("manifest.platform keys must also appear in manifest.targets")
        if not isinstance(metadata, dict):
            raise BuildError(f"manifest.platform.{target} must be an object")
        unknown_metadata = sorted(set(metadata) - {"description", "short_description"})
        if unknown_metadata:
            raise BuildError(f"manifest.platform.{target} has unknown key(s): {', '.join(unknown_metadata)}")
        for key, value in metadata.items():
            if not isinstance(value, str) or not value.strip():
                raise BuildError(f"manifest.platform.{target}.{key} must be a non-empty string")


def validate_manifest(data: dict[str, Any]) -> None:
    """Validate manifest structure. Raises BuildError on any issue."""
    if "version" not in data:
        raise BuildError("manifest missing required key: version")
    if "orchestrator" not in data:
        raise BuildError("manifest missing required key: orchestrator")
    if "steps" not in data:
        raise BuildError("manifest missing required key: steps")
    version = data["version"]
    if isinstance(version, bool) or not isinstance(version, int) or version not in {1, 2}:
        raise BuildError("manifest.version must be 1 or 2")
    _validate_relative_path(data["orchestrator"], "manifest.orchestrator")
    steps = _validate_steps(data["steps"], strict=version == 2)
    if version == 2:
        _validate_v2_metadata(data, steps)


def _resolve_skill_path(skill_dir: Path, relative: str, label: str) -> Path:
    """Resolve a manifest path and reject symlink escapes from the skill root."""
    try:
        root = skill_dir.resolve()
        candidate = (skill_dir / relative).resolve()
    except (OSError, RuntimeError) as exc:
        raise BuildError(f"cannot resolve {label}: {exc}") from exc
    if not candidate.is_relative_to(root):
        raise BuildError(f"{label} resolves outside skill directory: {relative}")
    return candidate


def _build_progressive_index(steps: list[dict[str, Any]]) -> str:
    lines = [
        "## Required phase resources",
        "",
        "Follow these phases in order. Each referenced file is part of this skill's contract; "
        "read it at the named point rather than loading every phase up front.",
        "",
    ]
    for index, step in enumerate(steps, start=1):
        lines.append(
            f"{index}. **{step['id']}** — Read `{step['file']}` completely, then execute this phase before "
            "continuing to the next one."
        )
    return "\n".join(lines)


def build_skill_md(
    skill_dir: Path,
    effective_steps: list[dict[str, Any]] | None = None,
) -> str:
    """Build a bundled skill or a progressive orchestrator with an ordered step index.

    If effective_steps is provided, it overrides the manifest's steps list —
    used by customize overlay application after applying insert/replace/disable ops.
    """
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.is_file():
        raise BuildError(f"manifest.json not found in {skill_dir}")
    manifest = load_manifest(manifest_path)

    orchestrator_rel = manifest["orchestrator"]
    orchestrator_path = _resolve_skill_path(skill_dir, orchestrator_rel, "manifest.orchestrator")
    if not orchestrator_path.is_file():
        raise BuildError(f"orchestrator file not found: {orchestrator_path}")

    steps = effective_steps if effective_steps is not None else manifest["steps"]
    _validate_steps(steps)

    try:
        orchestrator_text = orchestrator_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise BuildError(f"cannot read orchestrator {orchestrator_path}: {e}") from e

    parts: list[str] = [orchestrator_text]

    for step in steps:
        rel = step["file"]
        step_path = _resolve_skill_path(skill_dir, rel, f"step {step['id']}")
        if not step_path.is_file():
            raise BuildError(f"fragment file not found: {step_path} (step id: {step['id']})")
        try:
            step_text = step_path.read_text(encoding="utf-8")
            if manifest.get("delivery", "bundled") == "bundled":
                parts.append(step_text)
        except (OSError, UnicodeDecodeError) as e:
            raise BuildError(f"cannot read fragment {step_path}: {e}") from e

    if manifest.get("delivery") == "progressive":
        parts.append(_build_progressive_index(steps))

    raw = "\n\n".join(parts)
    return canonicalize(raw)


def write_skill_md(skill_dir: Path, output_path: Path | None = None) -> Path:
    """Build SKILL.md and write to disk atomically. Returns the written path."""
    built = build_skill_md(skill_dir)
    target = output_path if output_path is not None else (skill_dir / "SKILL.md")
    manifest = load_manifest(skill_dir / "manifest.json")
    if manifest.get("delivery") == "progressive" and target.parent.resolve() != skill_dir.resolve():
        raise BuildError("progressive SKILL.md output must remain in the skill directory beside its step resources")
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(built, encoding="utf-8")
    import os

    os.replace(str(tmp), str(target))
    return target


def _discover_skill_dirs(path: Path, report: SkillValidationReport) -> list[Path]:
    try:
        if not path.exists():
            raise OSError(f"path does not exist: {path}")
        if path.is_file():
            if path.name != "manifest.json":
                raise OSError(f"expected a skill directory or manifest.json: {path}")
            return [path.parent]
        if (path / "manifest.json").is_file():
            return [path]
        skill_dirs = sorted(child for child in path.iterdir() if child.is_dir() and (child / "manifest.json").is_file())
    except OSError as exc:
        report.unreadable = True
        report.errors.append(SkillFinding(path.name or str(path), "source-unreadable", str(exc), str(path)))
        return []
    if not skill_dirs:
        report.unreadable = True
        report.errors.append(
            SkillFinding(path.name or str(path), "source-unreadable", "no skill manifests found", str(path))
        )
    return skill_dirs


def _read_manifest_for_report(skill_dir: Path, report: SkillValidationReport) -> dict[str, Any] | None:
    path = skill_dir / "manifest.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        report.unreadable = True
        report.errors.append(SkillFinding(skill_dir.name, "source-unreadable", str(exc), str(path)))
        return None
    if not isinstance(data, dict):
        report.errors.append(
            SkillFinding(skill_dir.name, "manifest-invalid", "manifest must be a JSON object", str(path))
        )
        return None
    try:
        validate_manifest(data)
    except BuildError as exc:
        report.errors.append(SkillFinding(skill_dir.name, "manifest-invalid", str(exc), str(path)))
        return None
    return data


def _source_metrics(
    skill_dir: Path,
    manifest: dict[str, Any],
    report: SkillValidationReport,
) -> tuple[int, int, int] | None:
    references = [manifest["orchestrator"], *(step["file"] for step in manifest["steps"])]
    if "evals" in manifest:
        references.append(manifest["evals"])
    unique_references = list(dict.fromkeys(references))
    source_lines = 0
    source_words = 0
    for relative in unique_references:
        try:
            path = _resolve_skill_path(skill_dir, relative, relative)
        except BuildError as exc:
            report.errors.append(SkillFinding(skill_dir.name, "reference-unsafe", str(exc), relative))
            continue
        if not path.is_file():
            report.errors.append(
                SkillFinding(skill_dir.name, "reference-missing", f"referenced file not found: {relative}", relative)
            )
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            report.unreadable = True
            report.errors.append(SkillFinding(skill_dir.name, "source-unreadable", str(exc), str(path)))
            return None
        source_lines += len(text.splitlines())
        source_words += len(text.split())
    return len(unique_references), source_lines, source_words


def _check_orphan_steps(skill_dir: Path, manifest: dict[str, Any], report: SkillValidationReport) -> None:
    steps_dir = skill_dir / "steps"
    if not steps_dir.is_dir():
        return
    listed = {step["file"] for step in manifest["steps"]}
    try:
        on_disk = {path.relative_to(skill_dir).as_posix() for path in steps_dir.rglob("*.md")}
    except (OSError, UnicodeDecodeError) as exc:
        report.unreadable = True
        report.errors.append(SkillFinding(skill_dir.name, "source-unreadable", str(exc), str(steps_dir)))
        return
    for relative in sorted(on_disk - listed):
        report.errors.append(
            SkillFinding(
                skill_dir.name,
                "step-orphan",
                "step file is not listed in manifest.steps and will never execute",
                relative,
            )
        )


def _check_orchestrator_metadata(
    skill_dir: Path,
    manifest: dict[str, Any],
    report: SkillValidationReport,
) -> None:
    """Validate the discoverability metadata agents read before loading a skill."""
    if manifest.get("version") != 2:
        return
    relative = manifest["orchestrator"]
    path = skill_dir / relative
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.unreadable = True
        report.errors.append(SkillFinding(skill_dir.name, "source-unreadable", str(exc), str(path)))
        return
    end = content.find("\n---", 3) if content.startswith("---\n") else -1
    if end == -1:
        report.errors.append(
            SkillFinding(skill_dir.name, "metadata-missing", "v2 orchestrator needs YAML frontmatter", relative)
        )
        return
    try:
        metadata = yaml.safe_load(content[4:end]) or {}
    except yaml.YAMLError as exc:
        report.errors.append(SkillFinding(skill_dir.name, "metadata-invalid", str(exc), relative))
        return
    if not isinstance(metadata, dict):
        report.errors.append(
            SkillFinding(skill_dir.name, "metadata-invalid", "frontmatter must be a YAML mapping", relative)
        )
        return
    name = metadata.get("name")
    if name != skill_dir.name:
        report.errors.append(
            SkillFinding(
                skill_dir.name,
                "metadata-name",
                f"frontmatter name {name!r} must match directory name",
                relative,
            )
        )
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        report.errors.append(
            SkillFinding(skill_dir.name, "metadata-description", "description must be a non-empty string", relative)
        )
    elif len(description) > 1024:
        report.errors.append(
            SkillFinding(skill_dir.name, "metadata-description", "description exceeds 1024 characters", relative)
        )


def _check_parent_reference(skill_dir: Path, manifest: dict[str, Any], report: SkillValidationReport) -> None:
    parent = manifest.get("parent")
    if parent is None:
        return
    if manifest.get("visibility") != "internal":
        report.errors.append(
            SkillFinding(skill_dir.name, "parent-invalid", "only internal skills may declare a parent")
        )
    parent_manifest = skill_dir.parent / parent / "manifest.json"
    if not parent_manifest.is_file():
        report.errors.append(
            SkillFinding(
                skill_dir.name,
                "parent-missing",
                f"parent skill manifest not found: {parent}",
                str(parent_manifest),
            )
        )


def _installed_skills_root(target: str) -> Path:
    import os

    if target == "codex":
        return Path.home() / ".agents" / "skills"
    configured = os.environ.get("CLAUDE_CONFIG_DIR")
    if configured:
        root = Path(configured)
        if not root.is_absolute():
            raise BuildError(f"CLAUDE_CONFIG_DIR must be an absolute path, got: {configured}")
    else:
        root = Path.home() / ".claude"
    return root / "skills"


def _check_installed_skill(
    skill_dir: Path,
    manifest: dict[str, Any],
    targets: tuple[str, ...],
    report: SkillValidationReport,
) -> None:
    for target in targets:
        try:
            installed_dir = _installed_skills_root(target) / skill_dir.name
        except BuildError as exc:
            report.errors.append(SkillFinding(skill_dir.name, "installed-root", str(exc)))
            continue
        skill_md = installed_dir / "SKILL.md"
        if not skill_md.is_file():
            report.errors.append(
                SkillFinding(skill_dir.name, "installed-missing", f"{target} SKILL.md is missing", str(skill_md))
            )
            continue
        if manifest.get("delivery") == "progressive":
            for step in manifest["steps"]:
                installed_step = installed_dir / step["file"]
                if not installed_step.is_file():
                    report.errors.append(
                        SkillFinding(
                            skill_dir.name,
                            "installed-reference-missing",
                            f"{target} progressive step is missing",
                            str(installed_step),
                        )
                    )
        if target != "codex":
            continue
        try:
            runtime_files = [skill_md]
            if manifest.get("delivery") == "progressive":
                runtime_files.extend(installed_dir / step["file"] for step in manifest["steps"])
            foreign = [
                str(path)
                for path in runtime_files
                if path.is_file() and re.search(r"\b(?:Skill|AskUserQuestion)\(", path.read_text(encoding="utf-8"))
            ]
        except (OSError, UnicodeDecodeError) as exc:
            report.unreadable = True
            report.errors.append(SkillFinding(skill_dir.name, "installed-unreadable", str(exc), str(skill_md)))
            continue
        for path in foreign:
            report.errors.append(
                SkillFinding(
                    skill_dir.name,
                    "foreign-tool-syntax",
                    "Codex artifact still contains Claude-only tool syntax",
                    path,
                )
            )


def _load_codex_validation_compiler() -> dict[str, Any] | None:
    candidates = (
        Path(__file__).resolve().parents[1] / "pilot" / "hooks" / "codex_skill_sync.py",
        Path.home() / ".pilot" / "hooks" / "codex_skill_sync.py",
    )
    for path in candidates:
        if not path.is_file():
            continue
        try:
            namespace = runpy.run_path(str(path))
        except (OSError, RuntimeError, ImportError):
            continue
        if callable(namespace.get("_build_codex_skill")) and callable(namespace.get("_adapt")):
            return namespace
    return None


def _check_codex_artifact(skill_dir: Path, manifest: dict[str, Any], report: SkillValidationReport) -> None:
    """Compile and inspect the actual Codex artifact without requiring installation."""
    compiler = _load_codex_validation_compiler()
    if compiler is None:
        report.errors.append(
            SkillFinding(skill_dir.name, "platform-compiler-unavailable", "Codex skill compiler is unavailable")
        )
        return
    try:
        main = compiler["_build_codex_skill"](skill_dir)
    except Exception as exc:
        report.errors.append(SkillFinding(skill_dir.name, "platform-compile-failed", str(exc)))
        return
    if not isinstance(main, str):
        report.errors.append(
            SkillFinding(skill_dir.name, "platform-compile-failed", "Codex build returned no artifact")
        )
        return

    artifacts: list[tuple[str, str]] = [("SKILL.md", main)]
    if manifest.get("delivery") == "progressive":
        adapt = compiler["_adapt"]
        for step in manifest["steps"]:
            try:
                path = _resolve_skill_path(skill_dir, step["file"], f"step {step['id']}")
                artifacts.append((step["file"], adapt(path.read_text(encoding="utf-8"))))
            except (BuildError, OSError, UnicodeDecodeError) as exc:
                report.errors.append(SkillFinding(skill_dir.name, "platform-compile-failed", str(exc), step["file"]))
                continue

    for relative, text in artifacts:
        if "<!-- CC-ONLY -->" in text or "<!-- CODEX-START" in text or "CODEX-END -->" in text:
            report.errors.append(
                SkillFinding(
                    skill_dir.name,
                    "platform-marker",
                    "Codex artifact contains an unresolved platform marker",
                    relative,
                )
            )
        if re.search(r"\b(?:Skill|AskUserQuestion)\(", text):
            report.errors.append(
                SkillFinding(
                    skill_dir.name,
                    "foreign-tool-syntax",
                    "Codex artifact still contains Claude-only tool syntax",
                    relative,
                )
            )
        if re.search(r"plain-text numbered options.{0,40}(?:isn't|cannot|can't|unavailable)", text, re.IGNORECASE):
            report.errors.append(
                SkillFinding(
                    skill_dir.name,
                    "platform-contradiction",
                    "Codex artifact claims its plain-text fallback is unavailable",
                    relative,
                )
            )


def validate_skill_tree(
    path: Path,
    *,
    platform: str = "all",
    check_installed: bool = False,
) -> SkillValidationReport:
    """Validate one skill or a catalog without mutating source or installations."""
    if platform not in {"claude", "codex", "all"}:
        raise ValueError("platform must be claude, codex, or all")
    report = SkillValidationReport()
    for skill_dir in _discover_skill_dirs(path, report):
        manifest = _read_manifest_for_report(skill_dir, report)
        if manifest is None:
            continue
        _check_orchestrator_metadata(skill_dir, manifest, report)
        _check_orphan_steps(skill_dir, manifest, report)
        _check_parent_reference(skill_dir, manifest, report)
        source = _source_metrics(skill_dir, manifest, report)
        try:
            compiled = build_skill_md(skill_dir)
        except BuildError as exc:
            report.errors.append(SkillFinding(skill_dir.name, "compile-failed", str(exc)))
            continue
        if source is None:
            continue

        targets = tuple(manifest.get("targets", ("claude", "codex")))
        selected = targets if platform == "all" else tuple(target for target in targets if target == platform)
        if not selected:
            report.info.append(SkillFinding(skill_dir.name, "platform-skipped", f"skill does not target {platform}"))
        compiled_lines = len(compiled.splitlines())
        compiled_words = len(compiled.split())
        report.skills.append(
            SkillMetrics(
                name=skill_dir.name,
                version=manifest["version"],
                delivery=manifest.get("delivery", "bundled"),
                targets=targets,
                source_files=source[0],
                source_lines=source[1],
                source_words=source[2],
                compiled_bytes=len(compiled.encode("utf-8")),
                compiled_lines=compiled_lines,
                compiled_words=compiled_words,
            )
        )
        if "codex" in selected:
            _check_codex_artifact(skill_dir, manifest, report)
        if compiled_lines > COMPILED_LINE_LIMIT:
            report.errors.append(
                SkillFinding(
                    skill_dir.name,
                    "compiled-size",
                    f"compiled SKILL.md has {compiled_lines} lines; limit is {COMPILED_LINE_LIMIT}",
                )
            )
        if compiled_words > COMPILED_WORD_LIMIT:
            report.errors.append(
                SkillFinding(
                    skill_dir.name,
                    "compiled-size",
                    f"compiled SKILL.md has {compiled_words} words; limit is {COMPILED_WORD_LIMIT}",
                )
            )
        if check_installed and selected:
            _check_installed_skill(skill_dir, manifest, selected, report)
    return report


def render_validation_report(report: SkillValidationReport, path: Path) -> str:
    """Render a concise human-readable skill validation report."""
    lines = [f"Skill validation: {path}"]
    for metrics in report.skills:
        lines.append(
            f"  {metrics.name}: v{metrics.version} {metrics.delivery}; "
            f"source {metrics.source_lines} lines/{metrics.source_words} words; "
            f"compiled {metrics.compiled_lines} lines/{metrics.compiled_words} words"
        )
    for label, findings in (("ERROR", report.errors), ("WARNING", report.warnings), ("INFO", report.info)):
        for finding in findings:
            location = f" ({finding.path})" if finding.path else ""
            lines.append(f"  {label} [{finding.rule}] {finding.skill}: {finding.message}{location}")
    if report.ok:
        lines.append(f"✓ {len(report.skills)} skill(s) valid")
    else:
        lines.append(f"✗ {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return "\n".join(lines)
