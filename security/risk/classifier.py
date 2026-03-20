"""Risk classifier — assigns a risk level to every command before execution.

Risk levels:
  CRITICAL  Irreversible system damage, data destruction, privilege escalation
  HIGH      Deployment, infrastructure changes, force operations, supply chain
  MEDIUM    Network calls, package installs, file mutations outside repo
  LOW       Read-only, local analysis, lint, tests, safe git reads
  INFO      Metadata ops (git status, ls, echo, help flags)

Each entry in RISK_RULES is evaluated in order; first match wins.
Rules are intentionally conservative — unknown commands default to MEDIUM.
"""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass, field
from enum import IntEnum


class RiskLevel(IntEnum):
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    def label(self) -> str:
        return self.name

    def color(self) -> str:
        return {
            RiskLevel.INFO: "\033[0;36m",      # cyan
            RiskLevel.LOW: "\033[0;32m",       # green
            RiskLevel.MEDIUM: "\033[0;33m",    # yellow
            RiskLevel.HIGH: "\033[0;31m",      # red
            RiskLevel.CRITICAL: "\033[1;31m",  # bold red
        }[self]


@dataclass(frozen=True)
class RiskRule:
    pattern: re.Pattern[str]
    level: RiskLevel
    reason: str
    tags: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def make(
        cls,
        pattern: str,
        level: RiskLevel,
        reason: str,
        tags: tuple[str, ...] = (),
    ) -> "RiskRule":
        return cls(
            pattern=re.compile(pattern, re.IGNORECASE),
            level=level,
            reason=reason,
            tags=frozenset(tags),
        )


@dataclass
class RiskResult:
    level: RiskLevel
    reason: str
    command: str
    tags: frozenset[str]
    matched_rule: str

    @property
    def requires_confirmation(self) -> bool:
        return self.level >= RiskLevel.HIGH

    @property
    def is_blocked_by_default(self) -> bool:
        return self.level >= RiskLevel.CRITICAL

    def to_dict(self) -> dict:
        return {
            "level": self.level.label(),
            "level_int": int(self.level),
            "reason": self.reason,
            "command": self.command,
            "tags": sorted(self.tags),
            "matched_rule": self.matched_rule,
            "requires_confirmation": self.requires_confirmation,
            "is_blocked_by_default": self.is_blocked_by_default,
        }


# ---------------------------------------------------------------------------
# Rule table — ordered, first match wins
# ---------------------------------------------------------------------------

RISK_RULES: list[RiskRule] = [
    # ── CRITICAL ──────────────────────────────────────────────────────────
    RiskRule.make(
        r"\brm\s+(-[a-z]*f[a-z]*\s+)?-[a-z]*r[a-z]*\b",
        RiskLevel.CRITICAL,
        "Recursive remove: can permanently delete entire directory trees",
        ("destructive", "filesystem"),
    ),
    RiskRule.make(
        r"\b(dd|shred|wipe|srm)\b",
        RiskLevel.CRITICAL,
        "Disk-level destruction tool: overwrites data with no recovery path",
        ("destructive", "filesystem"),
    ),
    RiskRule.make(
        r">\s*/dev/(s?d[a-z][0-9]*|nvme[0-9])",
        RiskLevel.CRITICAL,
        "Writing directly to block device: will corrupt disk/partition",
        ("destructive", "filesystem"),
    ),
    RiskRule.make(
        r"\b(chmod|chown)\s+(-R\s+)?777\b",
        RiskLevel.CRITICAL,
        "World-writable permissions: removes all access controls",
        ("permissions", "escalation"),
    ),
    RiskRule.make(
        r"\bsudo\s+rm\b",
        RiskLevel.CRITICAL,
        "Privileged recursive remove: system-level data destruction risk",
        ("destructive", "privilege"),
    ),
    RiskRule.make(
        r"\b(DROP\s+DATABASE|DROP\s+TABLE|TRUNCATE\s+TABLE)\b",
        RiskLevel.CRITICAL,
        "Destructive SQL: drops or truncates tables/databases",
        ("destructive", "database"),
    ),
    RiskRule.make(
        r"\bcurl\b.*(sh|bash|python|ruby|perl)\b.*\|\s*(ba)?sh\b",
        RiskLevel.CRITICAL,
        "Pipe-to-shell pattern: executes remote code without inspection",
        ("rce", "supply-chain"),
    ),
    RiskRule.make(
        r"\beval\s+\$\(",
        RiskLevel.CRITICAL,
        "eval of subshell output: arbitrary code execution vector",
        ("rce",),
    ),

    # ── HIGH ──────────────────────────────────────────────────────────────
    RiskRule.make(
        r"\bterraform\s+(apply|destroy)\b",
        RiskLevel.HIGH,
        "Terraform apply/destroy: modifies or destroys real infrastructure",
        ("iac", "infra"),
    ),
    RiskRule.make(
        r"\bkubectl\s+(delete|apply|patch|replace|exec)\b",
        RiskLevel.HIGH,
        "kubectl mutation: changes live Kubernetes cluster state",
        ("k8s", "infra"),
    ),
    RiskRule.make(
        r"\baws\s+(ec2|s3|iam|rds|lambda|eks|cloudformation)\b.*\b(delete|terminate|remove|destroy|create|put|attach|detach)\b",
        RiskLevel.HIGH,
        "AWS mutation: creates, modifies, or destroys cloud resources",
        ("cloud", "infra"),
    ),
    RiskRule.make(
        r"\bgcloud\b.*(delete|create|deploy|iam)\b",
        RiskLevel.HIGH,
        "GCP mutation: changes live Google Cloud resources",
        ("cloud", "infra"),
    ),
    RiskRule.make(
        r"\baz\b.*(delete|create|deploy)\b",
        RiskLevel.HIGH,
        "Azure CLI mutation: changes live Azure resources",
        ("cloud", "infra"),
    ),
    RiskRule.make(
        r"\bgit\s+push\s+.*--force\b",
        RiskLevel.HIGH,
        "Force push: overwrites remote history, potential data loss for team",
        ("git", "destructive"),
    ),
    RiskRule.make(
        r"\bgit\s+(reset|clean)\s+.*(-f|--hard)\b",
        RiskLevel.HIGH,
        "Hard git reset/clean: permanently discards local changes",
        ("git", "destructive"),
    ),
    RiskRule.make(
        r"\bnpm\s+(publish|unpublish|deprecate)\b",
        RiskLevel.HIGH,
        "NPM publish/unpublish: affects public package registry",
        ("supply-chain", "publish"),
    ),
    RiskRule.make(
        r"\bpip\s+install\b.*--index-url\b",
        RiskLevel.HIGH,
        "pip install with custom index: supply chain substitution risk",
        ("supply-chain", "deps"),
    ),
    RiskRule.make(
        r"\bsudo\b",
        RiskLevel.HIGH,
        "Sudo execution: elevated privileges, wider blast radius",
        ("privilege",),
    ),
    RiskRule.make(
        r"\bkill\s+-9\b",
        RiskLevel.HIGH,
        "SIGKILL: force-terminates process with no cleanup opportunity",
        ("process",),
    ),
    RiskRule.make(
        r"\bdocker\s+(run|exec)\b.*--privileged\b",
        RiskLevel.HIGH,
        "Docker --privileged: container has near-full host kernel access",
        ("container", "privilege"),
    ),
    RiskRule.make(
        r"\bssh\s+.*-o\s+StrictHostKeyChecking=no\b",
        RiskLevel.HIGH,
        "SSH with host-key checking disabled: MITM attack surface",
        ("network", "mitm"),
    ),

    # ── MEDIUM ────────────────────────────────────────────────────────────
    RiskRule.make(
        r"\b(npm|yarn|pnpm)\s+(install|add|update)\b",
        RiskLevel.MEDIUM,
        "Package install: introduces external dependencies, supply chain risk",
        ("supply-chain", "deps"),
    ),
    RiskRule.make(
        r"\bpip\s+install\b",
        RiskLevel.MEDIUM,
        "pip install: introduces external Python package",
        ("supply-chain", "deps"),
    ),
    RiskRule.make(
        r"\bgo\s+(get|install)\b",
        RiskLevel.MEDIUM,
        "go get/install: downloads and compiles external Go module",
        ("supply-chain", "deps"),
    ),
    RiskRule.make(
        r"\bcargo\s+install\b",
        RiskLevel.MEDIUM,
        "cargo install: downloads and builds external Rust crate",
        ("supply-chain", "deps"),
    ),
    RiskRule.make(
        r"\bgit\s+push\b(?!.*--force)",
        RiskLevel.MEDIUM,
        "git push: publishes local changes to remote repository",
        ("git",),
    ),
    RiskRule.make(
        r"\bgit\s+commit\b",
        RiskLevel.MEDIUM,
        "git commit: creates a new commit in local history",
        ("git",),
    ),
    RiskRule.make(
        r"\bdocker\s+(build|push|run)\b",
        RiskLevel.MEDIUM,
        "Docker build/push/run: container lifecycle operation",
        ("container",),
    ),
    RiskRule.make(
        r"\bcurl\b.*-[oO]\b",
        RiskLevel.MEDIUM,
        "curl with output: downloads file from network",
        ("network", "download"),
    ),
    RiskRule.make(
        r"\bwget\b",
        RiskLevel.MEDIUM,
        "wget: downloads file from network",
        ("network", "download"),
    ),
    RiskRule.make(
        r"\bchmod\b",
        RiskLevel.MEDIUM,
        "chmod: changes file permissions",
        ("permissions",),
    ),
    RiskRule.make(
        r"\benv\b.*=",
        RiskLevel.MEDIUM,
        "env var mutation: modifies process environment",
        ("environment",),
    ),
    RiskRule.make(
        r"\b(export|set)\s+\w+=",
        RiskLevel.MEDIUM,
        "Environment variable assignment: may leak to child processes",
        ("environment",),
    ),
    RiskRule.make(
        r"\bssh\b",
        RiskLevel.MEDIUM,
        "SSH connection: outbound network access to remote host",
        ("network",),
    ),

    # ── LOW ───────────────────────────────────────────────────────────────
    RiskRule.make(
        r"\b(pytest|python\s+-m\s+pytest|jest|mocha|cargo\s+test|go\s+test|bun\s+test)\b",
        RiskLevel.LOW,
        "Test runner: executes local test suite",
        ("test",),
    ),
    RiskRule.make(
        r"\b(ruff|eslint|flake8|pylint|mypy|tsc|basedpyright)\b",
        RiskLevel.LOW,
        "Linter/type-checker: static analysis only, no mutations",
        ("lint",),
    ),
    RiskRule.make(
        r"\bgit\s+(status|log|diff|show|branch|fetch|pull)\b",
        RiskLevel.LOW,
        "git read operation: inspects repository state",
        ("git", "read"),
    ),
    RiskRule.make(
        r"\b(cat|less|head|tail|grep|rg|fd|find)\b",
        RiskLevel.LOW,
        "Read-only filesystem inspection",
        ("read",),
    ),
    RiskRule.make(
        r"\b(ls|pwd|whoami|id|date|uname|hostname)\b",
        RiskLevel.INFO,
        "System info command: read-only, no side effects",
        ("read",),
    ),
    RiskRule.make(
        r"\b(echo|printf)\b",
        RiskLevel.INFO,
        "Print command: no system effects",
        ("read",),
    ),
    RiskRule.make(
        r"\b(which|type|command\s+-v|help|man)\b",
        RiskLevel.INFO,
        "Help/info lookup: no system effects",
        ("read",),
    ),
]

_DEFAULT_LEVEL = RiskLevel.MEDIUM
_DEFAULT_REASON = "Unknown command — defaulting to MEDIUM risk (no matching rule)"


def classify(command: str) -> RiskResult:
    """Classify a shell command and return a RiskResult.

    Evaluates RISK_RULES in order; first match wins.
    Unknown commands default to MEDIUM.
    """
    stripped = command.strip()

    for rule in RISK_RULES:
        if rule.pattern.search(stripped):
            return RiskResult(
                level=rule.level,
                reason=rule.reason,
                command=stripped,
                tags=rule.tags,
                matched_rule=rule.pattern.pattern,
            )

    # Heuristic: if command looks purely like arg-parsing / help, downgrade to INFO
    try:
        tokens = shlex.split(stripped)
        if tokens and tokens[-1] in ("--help", "-h", "--version", "-V"):
            return RiskResult(
                level=RiskLevel.INFO,
                reason="Help/version flag detected: read-only invocation",
                command=stripped,
                tags=frozenset({"read"}),
                matched_rule="heuristic:help-flag",
            )
    except ValueError:
        pass

    return RiskResult(
        level=_DEFAULT_LEVEL,
        reason=_DEFAULT_REASON,
        command=stripped,
        tags=frozenset(),
        matched_rule="default",
    )
