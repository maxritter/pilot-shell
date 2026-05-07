"""Secret detection — port of sensitive-canary's 24 secret rules.

Pure module. Zero I/O. Importable from any hook script.
PII rules (sensitive-canary's PII_RULES + Luhn validator) are intentionally NOT
ported — out of scope per the credential-leak-prevention plan.

Source: sensitive-canary/src/lib/rules.ts:58-231 (gitleaks + TruffleHog).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule_id: str
    description: str
    match_redacted: str
    secret_value: str


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    regex: re.Pattern[str]
    secret_group: int = 0
    entropy_threshold: float | None = None


def entropy(s: str) -> float:
    """Shannon entropy in bits per character (0–8)."""
    if not s:
        return 0.0
    freq: dict[str, int] = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    h = 0.0
    for count in freq.values():
        p = count / n
        h -= p * math.log2(p)
    return h


def redact(s: str) -> str:
    """First 4 + **** + last 4; full-mask strings ≤ 8 chars."""
    if len(s) <= 8:
        return "****"
    return f"{s[:4]}****{s[-4:]}"


# ── Secret rules (24) ─────────────────────────────────────────────────────────
RULES: list[Rule] = [
    # Cloud
    Rule(
        id="aws-access-key",
        description="AWS Access Key ID",
        regex=re.compile(r"\b(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}\b"),
    ),
    Rule(
        id="gcp-api-key",
        description="Google Cloud API Key",
        regex=re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
    ),
    Rule(
        id="private-key",
        description="PEM Private Key",
        regex=re.compile(r"-----BEGIN (RSA |EC |DSA |PGP |OPENSSH )?PRIVATE KEY"),
    ),
    # Source control
    Rule(
        id="github-pat",
        description="GitHub Personal Access Token",
        regex=re.compile(r"gh[pousr]_[A-Za-z0-9]{36,255}"),
    ),
    Rule(
        id="github-fine-grained",
        description="GitHub Fine-Grained Token",
        regex=re.compile(r"github_pat_[A-Za-z0-9_]{82}"),
    ),
    Rule(
        id="gitlab-pat",
        description="GitLab Personal Access Token",
        regex=re.compile(r"glpat-[A-Za-z0-9_=\-]{20,22}"),
    ),
    # Package registries
    Rule(
        id="npm-token",
        description="npm Access Token",
        regex=re.compile(r"npm_[A-Za-z0-9]{36}"),
    ),
    # Communication
    Rule(
        id="slack-token",
        description="Slack Token",
        regex=re.compile(r"xox[baprs]-[0-9a-zA-Z\-]{10,72}"),
    ),
    Rule(
        id="slack-webhook",
        description="Slack Webhook URL",
        regex=re.compile(
            r"https://hooks\.slack\.com/services/T[A-Za-z0-9_]{8,10}/B[A-Za-z0-9_]{8,12}/[A-Za-z0-9_]{23,24}"
        ),
    ),
    Rule(
        id="discord-webhook",
        description="Discord Webhook URL",
        regex=re.compile(r"https://discord(?:app)?\.com/api/webhooks/[0-9]{17,20}/[A-Za-z0-9_\-]{68}"),
    ),
    Rule(
        id="telegram-bot-token",
        description="Telegram Bot Token",
        regex=re.compile(r"[0-9]{8,10}:AA[0-9A-Za-z_\-]{33}"),
    ),
    Rule(
        id="twilio-sid",
        description="Twilio Account SID",
        regex=re.compile(r"AC[0-9a-f]{32}"),
    ),
    # Email services
    Rule(
        id="sendgrid-key",
        description="SendGrid API Key",
        regex=re.compile(r"SG\.[A-Za-z0-9_\-]{20,24}\.[A-Za-z0-9_\-]{39,50}"),
    ),
    Rule(
        id="mailgun-key",
        description="Mailgun API Key",
        regex=re.compile(r"key-[0-9a-zA-Z]{32}"),
    ),
    Rule(
        id="mailchimp-key",
        description="Mailchimp API Key",
        regex=re.compile(r"[0-9a-f]{32}-us[0-9]{1,2}"),
    ),
    # Payment
    Rule(
        id="stripe-secret-key",
        description="Stripe Secret Key",
        regex=re.compile(r"sk_(live|test)_[0-9a-zA-Z]{24}"),
    ),
    Rule(
        id="stripe-restricted-key",
        description="Stripe Restricted Key",
        regex=re.compile(r"rk_(live|test)_[0-9a-zA-Z]{24}"),
    ),
    # AI services
    Rule(
        id="openai-key",
        description="OpenAI API Key (legacy)",
        regex=re.compile(r"sk-(?!proj-|ant-)[A-Za-z0-9]{48}"),
    ),
    Rule(
        id="openai-project-key",
        description="OpenAI Project API Key",
        regex=re.compile(r"sk-proj-[A-Za-z0-9_\-]{40,}"),
        entropy_threshold=3.5,
    ),
    Rule(
        id="anthropic-key",
        description="Anthropic API Key",
        regex=re.compile(r"sk-ant-[A-Za-z0-9_\-]{95}"),
    ),
    # Auth
    Rule(
        id="jwt",
        description="JSON Web Token (JWT)",
        regex=re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
    ),
    # Generic / env-based
    Rule(
        id="generic-secret",
        description="Generic API Key / Secret",
        regex=re.compile(
            r"(api[_\-]?key|secret[_\-]?key|access[_\-]?token|api[_\-]?secret)\s*[:=]\s*['\"]?([A-Za-z0-9\-_.]{20,})",
            re.IGNORECASE,
        ),
        secret_group=2,
        entropy_threshold=3.5,
    ),
    Rule(
        id="env-assignment",
        description=".env style secret assignment",
        regex=re.compile(r"\b[A-Z_]*(SECRET|PASSWORD|PASSWD|TOKEN|API_KEY|PRIVATE_KEY)[A-Z_0-9]*\s*=\s*(\S{8,})"),
        secret_group=2,
        entropy_threshold=3.0,
    ),
    Rule(
        id="connection-string",
        description="Database Connection String with credentials",
        regex=re.compile(r"(mongodb|mysql|postgres|postgresql|redis)://[^:\s]+:[^@\s]+@"),
    ),
]


def scan(text: str) -> list[Finding]:
    """Scan text for secrets across all rules. Findings are NOT deduped."""
    findings: list[Finding] = []
    if not text:
        return findings
    for rule in RULES:
        for match in rule.regex.finditer(text):
            try:
                secret_value = match.group(rule.secret_group)
            except IndexError:
                continue
            if not secret_value:
                continue
            if rule.entropy_threshold is not None and entropy(secret_value) < rule.entropy_threshold:
                continue
            findings.append(
                Finding(
                    rule_id=rule.id,
                    description=rule.description,
                    match_redacted=redact(secret_value),
                    secret_value=secret_value,
                )
            )
    return findings
