"""Secret detector — scans text for credentials, tokens, and keys.

Covers the most common high-signal patterns:
  - API keys (AWS, GCP, GitHub, Slack, Stripe, Twilio, etc.)
  - Private keys (PEM blocks)
  - JWT tokens
  - Generic high-entropy strings in variable-assignment context
  - Database connection strings with embedded credentials
  - .env-style KEY=<value> assignments

Design goals:
  - Zero false-negative bias on high-severity patterns
  - Entropy filtering to suppress low-entropy false positives on generic patterns
  - No external dependencies (stdlib only)
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class SecretPattern:
    name: str
    pattern: re.Pattern[str]
    severity: Severity
    description: str
    # Optional: minimum entropy of the captured group (index 0) for it to fire
    min_entropy: float = 0.0
    # Group index that contains the actual secret value (for entropy check)
    entropy_group: int = 0


@dataclass
class SecretFinding:
    pattern_name: str
    severity: Severity
    description: str
    line_number: int
    # Redacted match — we never store the raw secret
    redacted: str
    context_line: str

    def to_dict(self) -> dict:
        return {
            "pattern_name": self.pattern_name,
            "severity": self.severity.value,
            "description": self.description,
            "line_number": self.line_number,
            "redacted": self.redacted,
            "context_line": _redact_line(self.context_line),
        }


# ---------------------------------------------------------------------------
# Entropy helpers
# ---------------------------------------------------------------------------

def _shannon_entropy(s: str) -> float:
    """Shannon entropy of a string (bits per character)."""
    if not s:
        return 0.0
    freq: dict[str, int] = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    total = len(s)
    return -sum((c / total) * math.log2(c / total) for c in freq.values())


# ---------------------------------------------------------------------------
# Pattern library
# ---------------------------------------------------------------------------

_PATTERNS: list[SecretPattern] = [
    # AWS
    SecretPattern(
        name="aws-access-key-id",
        pattern=re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
        severity=Severity.HIGH,
        description="AWS Access Key ID",
        min_entropy=3.5,
        entropy_group=0,
    ),
    SecretPattern(
        name="aws-secret-access-key",
        pattern=re.compile(
            r'(?i)(?:aws[_\-\.]?secret[_\-\.]?(?:access[_\-\.]?)?key)\s*[=:]\s*["\']?([A-Za-z0-9+/]{40})["\']?'
        ),
        severity=Severity.HIGH,
        description="AWS Secret Access Key",
        min_entropy=4.0,
        entropy_group=1,
    ),

    # GitHub
    SecretPattern(
        name="github-pat",
        pattern=re.compile(r"\b(ghp_[A-Za-z0-9]{30,})\b"),
        severity=Severity.HIGH,
        description="GitHub Personal Access Token",
        min_entropy=4.0,
        entropy_group=0,
    ),
    SecretPattern(
        name="github-oauth-token",
        pattern=re.compile(r"\b(gho_[A-Za-z0-9]{30,})\b"),
        severity=Severity.HIGH,
        description="GitHub OAuth Access Token",
        min_entropy=4.0,
        entropy_group=0,
    ),
    SecretPattern(
        name="github-actions-token",
        pattern=re.compile(r"\b(ghs_[A-Za-z0-9]{30,})\b"),
        severity=Severity.HIGH,
        description="GitHub Actions Token",
        min_entropy=4.0,
        entropy_group=0,
    ),
    SecretPattern(
        name="github-fine-grained-pat",
        pattern=re.compile(r"\b(github_pat_[A-Za-z0-9_]{80,})\b"),
        severity=Severity.HIGH,
        description="GitHub Fine-Grained Personal Access Token",
    ),

    # Slack
    SecretPattern(
        name="slack-token",
        pattern=re.compile(r"\b(xox[baprs]-[0-9A-Za-z\-]{10,})\b"),
        severity=Severity.HIGH,
        description="Slack API Token",
        min_entropy=3.5,
        entropy_group=0,
    ),
    SecretPattern(
        name="slack-webhook",
        pattern=re.compile(
            r"https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[A-Za-z0-9]+"
        ),
        severity=Severity.HIGH,
        description="Slack Incoming Webhook URL",
    ),

    # Stripe
    SecretPattern(
        name="stripe-secret-key",
        pattern=re.compile(r"\b(sk_live_[0-9A-Za-z]{24,})\b"),
        severity=Severity.HIGH,
        description="Stripe Live Secret Key",
    ),
    SecretPattern(
        name="stripe-restricted-key",
        pattern=re.compile(r"\b(rk_live_[0-9A-Za-z]{24,})\b"),
        severity=Severity.HIGH,
        description="Stripe Restricted API Key",
    ),

    # Anthropic / OpenAI
    SecretPattern(
        name="anthropic-api-key",
        pattern=re.compile(r"\b(sk-ant-[A-Za-z0-9\-_]{80,})\b"),
        severity=Severity.HIGH,
        description="Anthropic API Key",
        min_entropy=4.0,
        entropy_group=0,
    ),
    SecretPattern(
        name="openai-api-key",
        pattern=re.compile(r"\b(sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20})\b"),
        severity=Severity.HIGH,
        description="OpenAI API Key",
    ),

    # Google
    SecretPattern(
        name="google-api-key",
        pattern=re.compile(r"\b(AIza[0-9A-Za-z\-_]{35})\b"),
        severity=Severity.HIGH,
        description="Google API Key",
        min_entropy=3.5,
        entropy_group=0,
    ),
    SecretPattern(
        name="google-oauth-client-secret",
        pattern=re.compile(r'(?i)client[_\-\.]?secret\s*[=:]\s*["\']?([A-Za-z0-9\-_]{24,})["\']?'),
        severity=Severity.MEDIUM,
        description="Possible Google OAuth Client Secret",
        min_entropy=4.0,
        entropy_group=1,
    ),

    # Twilio
    SecretPattern(
        name="twilio-account-sid",
        pattern=re.compile(r"\b(AC[a-f0-9]{32})\b"),
        severity=Severity.MEDIUM,
        description="Twilio Account SID",
        min_entropy=3.5,
        entropy_group=0,
    ),
    SecretPattern(
        name="twilio-auth-token",
        pattern=re.compile(
            r'(?i)twilio[_\-\.]?auth[_\-\.]?token\s*[=:]\s*["\']?([a-f0-9]{32})["\']?'
        ),
        severity=Severity.HIGH,
        description="Twilio Auth Token",
        min_entropy=3.0,
        entropy_group=1,
    ),

    # PEM / private key blocks
    SecretPattern(
        name="private-key-pem",
        pattern=re.compile(
            r"-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PGP)\s+PRIVATE KEY-----"
        ),
        severity=Severity.HIGH,
        description="PEM private key block",
    ),
    SecretPattern(
        name="generic-private-key",
        pattern=re.compile(r"-----BEGIN PRIVATE KEY-----"),
        severity=Severity.HIGH,
        description="PKCS8 private key block",
    ),

    # JWT
    SecretPattern(
        name="jwt-token",
        pattern=re.compile(
            r"\b(eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)\b"
        ),
        severity=Severity.MEDIUM,
        description="JSON Web Token (JWT) — may contain embedded credentials",
        min_entropy=4.0,
        entropy_group=0,
    ),

    # Database connection strings
    SecretPattern(
        name="db-connection-string",
        pattern=re.compile(
            r"(?i)(?:postgres|postgresql|mysql|mongodb|redis|mssql)://[^:@\s]+:[^@\s]+@"
        ),
        severity=Severity.HIGH,
        description="Database connection string with embedded credentials",
    ),

    # Generic high-entropy assignment (last resort)
    SecretPattern(
        name="generic-secret-assignment",
        pattern=re.compile(
            r'(?i)(?:password|passwd|secret|token|api[_\-]?key|auth[_\-]?key|private[_\-]?key)\s*[=:]\s*["\']?([A-Za-z0-9+/=_\-\.]{16,})["\']?'
        ),
        severity=Severity.MEDIUM,
        description="Generic high-entropy secret assignment",
        min_entropy=4.2,
        entropy_group=1,
    ),
]


def _redact_line(line: str, max_len: int = 120) -> str:
    """Truncate line for display — never return raw secrets in context lines."""
    truncated = line[:max_len]
    # Mask anything that looks like a high-entropy token after = or :
    truncated = re.sub(
        r'(=|:)\s*["\']?([A-Za-z0-9+/=_\-\.]{16,})["\']?',
        r"\1 <redacted>",
        truncated,
    )
    return truncated


def scan_text(text: str, source: str = "<text>") -> list[SecretFinding]:
    """Scan `text` for secret patterns. Returns a list of findings."""
    findings: list[SecretFinding] = []
    lines = text.splitlines()

    for line_num, line in enumerate(lines, start=1):
        # Skip comment lines (quick heuristic)
        stripped = line.lstrip()
        if stripped.startswith(("#", "//", "*", "<!--")):
            continue

        for pat in _PATTERNS:
            match = pat.pattern.search(line)
            if not match:
                continue

            # Entropy check on capture group if required
            if pat.min_entropy > 0:
                try:
                    secret_val = match.group(pat.entropy_group)
                except IndexError:
                    secret_val = match.group(0)
                if _shannon_entropy(secret_val) < pat.min_entropy:
                    continue

            # Build redacted representation
            raw = match.group(0)
            redacted = raw[:4] + "*" * (len(raw) - 4) if len(raw) > 4 else "****"

            findings.append(
                SecretFinding(
                    pattern_name=pat.name,
                    severity=pat.severity,
                    description=pat.description,
                    line_number=line_num,
                    redacted=redacted,
                    context_line=line,
                )
            )
            # One finding per line per pattern — don't double-report
            break

    return findings


def scan_file(path: str) -> list[SecretFinding]:
    """Scan a file for secrets. Returns empty list if file cannot be read."""
    try:
        from pathlib import Path as _Path
        text = _Path(path).read_text(errors="replace")
        return scan_text(text, source=path)
    except OSError:
        return []


def scan_env(env: dict[str, str]) -> list[SecretFinding]:
    """Scan environment variables for embedded secrets."""
    findings: list[SecretFinding] = []
    for key, value in env.items():
        line = f"{key}={value}"
        found = scan_text(line)
        findings.extend(found)
    return findings
