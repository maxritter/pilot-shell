#!/usr/bin/env python3
"""Deterministically validate Pilot's shipped rule pack and skill routing catalog."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = REPO_ROOT / "pilot" / "hooks"
DEFAULT_CATALOG = REPO_ROOT / "benchmarks" / "skill-routing" / "catalog.json"
DEFAULT_RATCHET = REPO_ROOT / "benchmarks" / "skill-routing" / "ratchet.json"
VALID_VISIBILITY = {"public", "internal"}
VALID_INVOCATION = {"explicit", "implicit"}
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a",
    "after",
    "an",
    "and",
    "for",
    "from",
    "in",
    "internal",
    "invoked",
    "only",
    "or",
    "phase",
    "the",
    "to",
    "use",
    "user",
    "when",
    "with",
}


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


@dataclass(frozen=True)
class SkillRecord:
    name: str
    source: Path
    visibility: str
    invocation: str
    parent: str | None
    description: str
    positives: tuple[dict[str, Any], ...]
    negatives: tuple[dict[str, Any], ...]


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _generated_description(skill_dir: Path) -> str:
    if str(HOOKS_DIR) not in sys.path:
        sys.path.insert(0, str(HOOKS_DIR))
    from codex_skill_sync import _build_codex_skill

    generated = _build_codex_skill(skill_dir)
    if generated is None:
        raise ValueError(f"could not compile {skill_dir}")
    if not generated.startswith("---\n") or "\n---\n" not in generated[4:]:
        raise ValueError(f"compiled skill has no YAML frontmatter: {skill_dir}")
    frontmatter = generated[4 : generated.index("\n---\n", 4)]
    metadata = yaml.safe_load(frontmatter)
    description = metadata.get("description") if isinstance(metadata, dict) else None
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"compiled skill has no description: {skill_dir}")
    return description.strip()


def _resolve_metadata(entry: dict[str, Any], manifest: dict[str, Any]) -> tuple[str, str, str | None]:
    """Prefer manifest v2 routing metadata; catalog values are v1 compatibility fallbacks."""
    visibility = manifest.get("visibility", entry.get("visibility"))
    invocation = manifest.get("invocation", entry.get("invocation"))
    parent = manifest.get("parent", entry.get("parent"))
    if visibility not in VALID_VISIBILITY:
        raise ValueError(f"invalid visibility {visibility!r}")
    if invocation not in VALID_INVOCATION:
        raise ValueError(f"invalid invocation {invocation!r}")
    if parent is not None and not isinstance(parent, str):
        raise ValueError("parent must be a skill name")
    return visibility, invocation, parent


def _load_records(repo_root: Path, catalog: dict[str, Any]) -> list[SkillRecord]:
    records: list[SkillRecord] = []
    entries = catalog.get("skills")
    if not isinstance(entries, list):
        raise ValueError("catalog.skills must be an array")
    for raw in entries:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str) or not isinstance(raw.get("source"), str):
            raise ValueError("each catalog skill needs string id and source fields")
        source = repo_root / raw["source"]
        manifest = _read_json(source / "manifest.json")
        visibility, invocation, parent = _resolve_metadata(raw, manifest)
        positives = raw.get("positives", [])
        negatives = raw.get("negatives", [])
        if not isinstance(positives, list) or not isinstance(negatives, list):
            raise ValueError(f"{raw['id']}: positives and negatives must be arrays")
        records.append(
            SkillRecord(
                name=raw["id"],
                source=source,
                visibility=visibility,
                invocation=invocation,
                parent=parent,
                description=_generated_description(source),
                positives=tuple(positives),
                negatives=tuple(negatives),
            )
        )
    return records


def _tokens(text: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(text.lower()) if token not in STOP_WORDS and len(token) > 1}


def _invokes(prompt: str, name: str) -> bool:
    return re.search(rf"(?<![a-z0-9_-])[$/]{re.escape(name)}(?![a-z0-9_-])", prompt.lower()) is not None


def _requested_internal_parent(prompt: str, records: list[SkillRecord]) -> str | None:
    for record in records:
        if record.visibility == "internal" and record.parent and _invokes(prompt, record.name):
            return record.parent
    return None


def _route(prompt: str, context: dict[str, Any], records: list[SkillRecord]) -> list[tuple[str, float]]:
    prompt_tokens = _tokens(prompt)
    document_frequency: dict[str, int] = {}
    for record in records:
        for token in _tokens(record.description):
            document_frequency[token] = document_frequency.get(token, 0) + 1
    requested_parent = _requested_internal_parent(prompt, records)
    ranked: list[tuple[str, float]] = []
    for record in records:
        invoked = _invokes(prompt, record.name)
        if record.visibility == "internal":
            eligible = context.get("parent") == record.parent and invoked
        elif record.invocation == "explicit":
            eligible = invoked or requested_parent == record.name
        else:
            eligible = True
        if not eligible:
            continue
        description_tokens = _tokens(record.description) | _tokens(record.name)
        overlap = prompt_tokens & description_tokens
        if not invoked and requested_parent != record.name and not overlap:
            continue
        score = sum(math.log((len(records) + 1) / (document_frequency.get(token, 0) + 1)) + 1 for token in overlap)
        if invoked:
            score += 100
        elif requested_parent == record.name:
            score += 50
        ranked.append((record.name, round(score, 6)))
    return sorted(ranked, key=lambda item: (-item[1], item[0]))


def _validate_catalog_shape(records: list[SkillRecord]) -> list[Finding]:
    findings: list[Finding] = []
    names = [record.name for record in records]
    if len(names) != len(set(names)):
        findings.append(Finding("catalog.duplicate", "catalog skill ids must be unique"))
    name_set = set(names)
    for record in records:
        if not record.positives:
            findings.append(Finding("catalog.positive-missing", f"{record.name} has no positive routing cases"))
        if not record.negatives:
            findings.append(Finding("catalog.negative-missing", f"{record.name} has no negative routing cases"))
        if record.visibility == "internal" and (not record.parent or record.parent not in name_set):
            findings.append(Finding("catalog.parent", f"{record.name} needs a catalogued parent"))
        if record.visibility == "public" and record.parent:
            findings.append(Finding("catalog.parent", f"public skill {record.name} cannot declare a parent"))
        for case in (*record.positives, *record.negatives):
            if not isinstance(case, dict) or not isinstance(case.get("prompt"), str):
                findings.append(Finding("catalog.case", f"{record.name} has a case without a string prompt"))
        for case in record.negatives:
            owner = case.get("owner")
            if owner != "direct" and owner not in name_set:
                findings.append(Finding("catalog.owner", f"{record.name} negative has unknown owner {owner!r}"))
    return findings


def _validate_descriptions(records: list[SkillRecord], ratchet: dict[str, Any]) -> tuple[list[Finding], float]:
    findings: list[Finding] = []
    pairwise: list[tuple[float, str, str]] = []
    for index, left in enumerate(records):
        if len(left.description.split()) > 60:
            findings.append(Finding("description.length", f"{left.name} description exceeds 60 words"))
        if left.description.casefold().startswith("use only"):
            findings.append(
                Finding(
                    "description.leading-routing",
                    f"{left.name} description starts with routing policy instead of its capability",
                )
            )
        if left.visibility == "public" and left.invocation == "explicit" and "explicit" not in left.description.lower():
            findings.append(
                Finding("description.explicit", f"{left.name} description does not state explicit invocation")
            )
        if left.visibility == "internal" and "internal" not in left.description.lower():
            findings.append(
                Finding("description.internal", f"{left.name} description does not state internal visibility")
            )
        for right in records[index + 1 :]:
            left_tokens, right_tokens = _tokens(left.description), _tokens(right.description)
            union = left_tokens | right_tokens
            similarity = len(left_tokens & right_tokens) / len(union) if union else 1.0
            pairwise.append((similarity, left.name, right.name))
    pairwise.sort(reverse=True)
    maximum = pairwise[0][0] if pairwise else 0.0
    limits = ratchet["descriptions"]
    for similarity, left, right in pairwise:
        if similarity > float(limits["error_jaccard"]):
            findings.append(Finding("description.collision", f"{left} and {right} collide at {similarity:.3f}"))
    if maximum > float(limits["max_pairwise_jaccard"]):
        findings.append(
            Finding(
                "description.ratchet",
                f"maximum pairwise description similarity {maximum:.3f} exceeds ratchet "
                f"{float(limits['max_pairwise_jaccard']):.3f}",
            )
        )
    return findings, maximum


def _validate_routing(records: list[SkillRecord], ratchet: dict[str, Any]) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    positive_count = rank_one_count = top_three_count = 0
    for record in records:
        for case in record.positives:
            positive_count += 1
            ranked = [name for name, _ in _route(case["prompt"], case.get("context", {}), records)]
            rank_one_count += bool(ranked and ranked[0] == record.name)
            top_three_count += record.name in ranked[:3]
            if record.name not in ranked[:3]:
                findings.append(
                    Finding("routing.positive", f"{record.name} missed top three for {case['prompt']!r}: {ranked[:3]}")
                )
        for case in record.negatives:
            ranked = [name for name, _ in _route(case["prompt"], case.get("context", {}), records)]
            owner = case["owner"]
            if owner == "direct":
                if record.name in ranked:
                    findings.append(
                        Finding("routing.hijack", f"{record.name} hijacks direct request {case['prompt']!r}")
                    )
            elif record.name in ranked and (owner not in ranked or ranked.index(record.name) <= ranked.index(owner)):
                findings.append(
                    Finding("routing.owner", f"{record.name} outranks owner {owner} for {case['prompt']!r}")
                )
    rank_one_rate = rank_one_count / positive_count if positive_count else 0.0
    top_three_rate = top_three_count / positive_count if positive_count else 0.0
    limits = ratchet["routing"]
    if top_three_rate < float(limits["min_positive_top_three_rate"]):
        findings.append(Finding("routing.top-three-ratchet", f"positive top-three rate is {top_three_rate:.1%}"))
    if rank_one_rate < float(limits["min_positive_rank_one_rate"]):
        findings.append(Finding("routing.rank-one-ratchet", f"positive rank-one rate is {rank_one_rate:.1%}"))
    return findings, {
        "positive_cases": positive_count,
        "positive_rank_one_rate": rank_one_rate,
        "positive_top_three_rate": top_three_rate,
    }


def _validate_rules(repo_root: Path, config: dict[str, Any]) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    lines = words = 0
    unscoped_files = 0
    for path in sorted((repo_root / "pilot" / "rules").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            continue
        file_lines = len(text.splitlines())
        lines += file_lines
        words += len(text.split())
        unscoped_files += 1
        if file_lines > int(config["max_unscoped_file_lines"]):
            findings.append(Finding("rules.file-lines", f"{path.name} has {file_lines} unscoped lines"))
        if re.search(r"\b20\d{2}\b", text):
            findings.append(Finding("rules.dated-claim", f"{path.name} contains a dated claim"))
    if lines > int(config["max_unscoped_lines"]):
        findings.append(Finding("rules.lines", f"unscoped rule pack has {lines} lines"))
    if words > int(config["max_unscoped_words"]):
        findings.append(Finding("rules.words", f"unscoped rule pack has {words} words"))
    return findings, {"unscoped_files": unscoped_files, "unscoped_lines": lines, "unscoped_words": words}


def validate(repo_root: Path, catalog_path: Path, ratchet_path: Path) -> dict[str, Any]:
    catalog, ratchet = _read_json(catalog_path), _read_json(ratchet_path)
    records = _load_records(repo_root, catalog)
    findings = _validate_catalog_shape(records)
    try:
        if str(HOOKS_DIR) not in sys.path:
            sys.path.insert(0, str(HOOKS_DIR))
        from codex_skill_sync import _SUPPORTED_SKILLS

        catalog_names = {record.name for record in records}
        if catalog_names != set(_SUPPORTED_SKILLS):
            findings.append(
                Finding(
                    "catalog.coverage",
                    f"catalog differs from Codex-supported skills: missing={sorted(set(_SUPPORTED_SKILLS) - catalog_names)}, "
                    f"extra={sorted(catalog_names - set(_SUPPORTED_SKILLS))}",
                )
            )
    except ImportError as exc:
        raise ValueError(f"cannot load Codex skill compiler: {exc}") from exc
    description_findings, maximum_similarity = _validate_descriptions(records, ratchet)
    routing_findings, routing_metrics = _validate_routing(records, ratchet)
    rule_findings, rule_metrics = _validate_rules(repo_root, catalog["rules"])
    findings.extend(description_findings + routing_findings + rule_findings)
    return {
        "ok": not findings,
        "findings": [asdict(finding) for finding in findings],
        "metrics": {
            "skills": len(records),
            "max_description_jaccard": maximum_similarity,
            **routing_metrics,
            **rule_metrics,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--ratchet", type=Path, default=DEFAULT_RATCHET)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)
    try:
        result = validate(args.repo.resolve(), args.catalog.resolve(), args.ratchet.resolve())
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        if args.json_output:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"agent asset validation could not run: {exc}", file=sys.stderr)
        return 2
    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        metrics = result["metrics"]
        print(
            "agent assets valid: "
            f"{metrics['skills']} skills, {metrics['positive_cases']} routing cases, "
            f"{metrics['unscoped_lines']} unscoped rule lines/{metrics['unscoped_words']} words"
        )
    else:
        for finding in result["findings"]:
            print(f"{finding['code']}: {finding['message']}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
