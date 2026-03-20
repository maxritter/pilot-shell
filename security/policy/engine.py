"""Policy engine — deterministic control layer over command execution.

Policies are loaded from YAML files (policies/default/rules.yaml and
policies/org/*.yaml). Each rule specifies a condition and an action:

  action: block   → deny execution (exit 2, reason returned to Claude)
  action: warn    → allow but inject warning context
  action: require → block unless an environment gate variable is set
  action: allow   → explicitly allow (can override earlier block rules)

Rules are evaluated in definition order; the first matching rule with
action=block or action=require wins. Warn rules accumulate.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

from security.risk.classifier import RiskLevel, RiskResult


class PolicyAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    REQUIRE = "require"  # block unless env gate is set


@dataclass(frozen=True)
class PolicyRule:
    name: str
    description: str
    action: PolicyAction
    # Condition fields (at least one required)
    command_pattern: re.Pattern[str] | None = None
    min_risk_level: RiskLevel | None = None
    tags: frozenset[str] = field(default_factory=frozenset)
    # For 'require' action: env var that must be set/truthy to bypass
    gate_env_var: str = ""
    gate_description: str = ""

    def matches(self, result: RiskResult) -> bool:
        """Return True if this rule applies to the given RiskResult."""
        if self.command_pattern and not self.command_pattern.search(result.command):
            return False
        if self.min_risk_level and result.level < self.min_risk_level:
            return False
        if self.tags and not self.tags.intersection(result.tags):
            return False
        return True


@dataclass
class PolicyVerdict:
    action: PolicyAction
    matched_rules: list[str]
    warnings: list[str]
    block_reason: str = ""
    gate_env_var: str = ""
    gate_description: str = ""

    @property
    def is_blocked(self) -> bool:
        return self.action in (PolicyAction.BLOCK, PolicyAction.REQUIRE)

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "matched_rules": self.matched_rules,
            "warnings": self.warnings,
            "block_reason": self.block_reason,
            "gate_env_var": self.gate_env_var,
            "gate_description": self.gate_description,
            "is_blocked": self.is_blocked,
        }


# ---------------------------------------------------------------------------
# Built-in default rules (used when YAML loading is unavailable or missing)
# ---------------------------------------------------------------------------

_BUILTIN_RULES: list[PolicyRule] = [
    PolicyRule(
        name="block-pipe-to-shell",
        description="Prevent curl/wget piped directly into a shell interpreter",
        action=PolicyAction.BLOCK,
        command_pattern=re.compile(
            r"\bcurl\b.*(sh|bash|python|ruby|perl)\b.*\|\s*(ba)?sh\b",
            re.IGNORECASE,
        ),
    ),
    PolicyRule(
        name="block-world-writable-chmod",
        description="Prevent setting world-writable permissions (chmod 777 / o+w)",
        action=PolicyAction.BLOCK,
        command_pattern=re.compile(r"\bchmod\s+(-R\s+)?777\b", re.IGNORECASE),
    ),
    PolicyRule(
        name="require-approval-terraform",
        description="terraform apply/destroy requires PILOT_SEC_INFRA_APPROVED=1",
        action=PolicyAction.REQUIRE,
        command_pattern=re.compile(r"\bterraform\s+(apply|destroy)\b", re.IGNORECASE),
        gate_env_var="PILOT_SEC_INFRA_APPROVED",
        gate_description=(
            "Set PILOT_SEC_INFRA_APPROVED=1 to allow terraform apply/destroy. "
            "Alternatively run `terraform plan` first and review the output."
        ),
    ),
    PolicyRule(
        name="require-approval-kubectl-delete",
        description="kubectl delete requires PILOT_SEC_INFRA_APPROVED=1",
        action=PolicyAction.REQUIRE,
        command_pattern=re.compile(r"\bkubectl\s+delete\b", re.IGNORECASE),
        gate_env_var="PILOT_SEC_INFRA_APPROVED",
        gate_description="Set PILOT_SEC_INFRA_APPROVED=1 to allow kubectl delete.",
    ),
    PolicyRule(
        name="warn-force-push",
        description="Warn on git force-push — history rewrite affects collaborators",
        action=PolicyAction.WARN,
        command_pattern=re.compile(r"\bgit\s+push\s+.*--force\b", re.IGNORECASE),
    ),
    PolicyRule(
        name="warn-supply-chain-install",
        description="Warn on package installs — dependency confusion / typosquat risk",
        action=PolicyAction.WARN,
        tags=frozenset({"supply-chain", "deps"}),
    ),
    PolicyRule(
        name="warn-sudo",
        description="Warn on sudo — elevated privileges expand blast radius",
        action=PolicyAction.WARN,
        tags=frozenset({"privilege"}),
    ),
    PolicyRule(
        name="warn-critical-risk",
        description="Warn when risk level is CRITICAL",
        action=PolicyAction.WARN,
        min_risk_level=RiskLevel.CRITICAL,
    ),
    PolicyRule(
        name="block-eval-subshell",
        description="Block eval of subshell output — arbitrary code execution vector",
        action=PolicyAction.BLOCK,
        command_pattern=re.compile(r"\beval\s+\$\(", re.IGNORECASE),
    ),
]


def _load_yaml_rules(rules_path: Path) -> list[PolicyRule]:
    """Load rules from a YAML file. Returns empty list on any error."""
    if not _YAML_AVAILABLE or not rules_path.exists():
        return []

    try:
        with rules_path.open() as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return []

    loaded: list[PolicyRule] = []
    for rule_data in data.get("rules", []):
        try:
            action = PolicyAction(rule_data["action"])
            pattern = None
            if "command_pattern" in rule_data:
                pattern = re.compile(rule_data["command_pattern"], re.IGNORECASE)

            min_risk = None
            if "min_risk_level" in rule_data:
                min_risk = RiskLevel[rule_data["min_risk_level"].upper()]

            tags: frozenset[str] = frozenset(rule_data.get("tags", []))

            loaded.append(
                PolicyRule(
                    name=rule_data["name"],
                    description=rule_data.get("description", ""),
                    action=action,
                    command_pattern=pattern,
                    min_risk_level=min_risk,
                    tags=tags,
                    gate_env_var=rule_data.get("gate_env_var", ""),
                    gate_description=rule_data.get("gate_description", ""),
                )
            )
        except (KeyError, ValueError):
            continue

    return loaded


class PolicyEngine:
    """Evaluates a set of policy rules against a RiskResult.

    Rule loading order (later = higher precedence is NOT assumed;
    rules are evaluated in order and the first blocking rule wins):
      1. Built-in rules
      2. policies/default/rules.yaml (from repo root)
      3. policies/org/*.yaml (alphabetical)
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        self._rules: list[PolicyRule] = list(_BUILTIN_RULES)
        if repo_root:
            self._load_from_repo(repo_root)

    def _load_from_repo(self, root: Path) -> None:
        default_path = root / "policies" / "default" / "rules.yaml"
        org_dir = root / "policies" / "org"

        self._rules.extend(_load_yaml_rules(default_path))

        if org_dir.is_dir():
            for p in sorted(org_dir.glob("*.yaml")):
                self._rules.extend(_load_yaml_rules(p))

    def evaluate(self, result: RiskResult) -> PolicyVerdict:
        """Evaluate all policy rules and return a consolidated verdict."""
        warnings: list[str] = []
        matched: list[str] = []

        for rule in self._rules:
            if not rule.matches(result):
                continue

            matched.append(rule.name)

            if rule.action == PolicyAction.BLOCK:
                return PolicyVerdict(
                    action=PolicyAction.BLOCK,
                    matched_rules=matched,
                    warnings=warnings,
                    block_reason=f"[{rule.name}] {rule.description}",
                )

            if rule.action == PolicyAction.REQUIRE:
                gate_value = os.environ.get(rule.gate_env_var, "").strip()
                if gate_value not in ("1", "true", "yes"):
                    return PolicyVerdict(
                        action=PolicyAction.REQUIRE,
                        matched_rules=matched,
                        warnings=warnings,
                        block_reason=(
                            f"[{rule.name}] {rule.description}\n"
                            f"Gate variable not set: {rule.gate_env_var}"
                        ),
                        gate_env_var=rule.gate_env_var,
                        gate_description=rule.gate_description,
                    )

            if rule.action == PolicyAction.WARN:
                warnings.append(f"[{rule.name}] {rule.description}")

        final_action = PolicyAction.WARN if warnings else PolicyAction.ALLOW
        return PolicyVerdict(
            action=final_action,
            matched_rules=matched,
            warnings=warnings,
        )


def _find_repo_root() -> Path | None:
    """Walk up from cwd to find a directory containing pyproject.toml or .git."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return None


_ENGINE: PolicyEngine | None = None


def get_engine() -> PolicyEngine:
    """Return a singleton PolicyEngine, initialised from the detected repo root."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = PolicyEngine(repo_root=_find_repo_root())
    return _ENGINE
