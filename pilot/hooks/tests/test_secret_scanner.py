"""Tests for _lib.secret_scanner — port of sensitive-canary's 24 secret rules."""

from __future__ import annotations

import time

import pytest
from _lib.secret_scanner import RULES, Finding, entropy, redact, scan


class TestEntropy:
    def test_repeated_char_zero(self):
        assert entropy("aaaaaaaa") == pytest.approx(0.0)

    def test_aws_key_in_band(self):
        h = entropy("AKIAIOSFODNN7EXAMPLE")
        assert 3.4 <= h <= 4.5  # 20-char near-uniform string

    def test_empty_string(self):
        assert entropy("") == pytest.approx(0.0)


class TestRedact:
    def test_redact_short(self):
        assert redact("short") == "****"

    def test_redact_eight(self):
        assert redact("12345678") == "****"

    def test_redact_long(self):
        assert redact("AKIAIOSFODNN7EXAMPLE") == "AKIA****MPLE"

    def test_redact_nine(self):
        # First 4 + **** + last 4
        assert redact("123456789") == "1234****6789"


class TestRulesPresent:
    """All 24 secret rules must be present (PII rules excluded by design)."""

    EXPECTED_IDS = {
        # Cloud
        "aws-access-key",
        "gcp-api-key",
        "private-key",
        # SCM
        "github-pat",
        "github-fine-grained",
        "gitlab-pat",
        # Package
        "npm-token",
        # Comm
        "slack-token",
        "slack-webhook",
        "discord-webhook",
        "telegram-bot-token",
        "twilio-sid",
        # Email
        "sendgrid-key",
        "mailgun-key",
        "mailchimp-key",
        # Payment
        "stripe-secret-key",
        "stripe-restricted-key",
        # AI
        "openai-key",
        "openai-project-key",
        "anthropic-key",
        # Auth
        "jwt",
        # Generic
        "generic-secret",
        "env-assignment",
        "connection-string",
    }

    def test_24_rules(self):
        ids = {r.id for r in RULES}
        assert ids == self.EXPECTED_IDS, f"missing: {self.EXPECTED_IDS - ids} extra: {ids - self.EXPECTED_IDS}"

    def test_no_pii_rules(self):
        """PII rules are intentionally NOT ported (out of scope per plan)."""
        ids = {r.id for r in RULES}
        forbidden = {"pii-email", "pii-credit-card", "pii-ssn", "pii-phone-us"}
        assert ids & forbidden == set()


class TestScanPositive:
    """Each rule must have at least one positive match."""

    def test_aws_access_key(self):
        # Synthetic fixtures split via string concatenation so GitHub secret
        # scanning doesn't false-positive on the AWS canonical example.
        akia = "AKIA" + "IOSFODNN7EXAMPLE"
        f = scan(f"My AWS key is {akia}")
        assert len(f) == 1
        assert f[0].rule_id == "aws-access-key"
        assert f[0].match_redacted == "AKIA****MPLE"
        assert f[0].secret_value == akia

    def test_aws_session_token(self):
        # Split to avoid GitHub secret-scanning alert on the synthetic fixture.
        f = scan("ASIA" + "IOSFODNN7EXAMPLE" + " here")
        assert any(x.rule_id == "aws-access-key" for x in f)

    def test_gcp_api_key(self):
        # Split to avoid GitHub secret-scanning alert on the synthetic fixture.
        f = scan("AIza" + "SyD-abc123XYZ_qwerty456zxcvbnmasdfg")
        assert any(x.rule_id == "gcp-api-key" for x in f)

    def test_pem_private_key(self):
        f = scan("-----BEGIN RSA PRIVATE KEY-----")
        assert any(x.rule_id == "private-key" for x in f)
        f2 = scan("-----BEGIN OPENSSH PRIVATE KEY-----")
        assert any(x.rule_id == "private-key" for x in f2)
        f3 = scan("-----BEGIN PRIVATE KEY-----")  # bare form
        assert any(x.rule_id == "private-key" for x in f3)

    def test_github_pat(self):
        f = scan("ghp_" + "a" * 36)
        assert any(x.rule_id == "github-pat" for x in f)
        f2 = scan("ghs_" + "B" * 40)
        assert any(x.rule_id == "github-pat" for x in f2)

    def test_github_fine_grained(self):
        f = scan("github_pat_" + "a" * 82)
        assert any(x.rule_id == "github-fine-grained" for x in f)

    def test_gitlab_pat(self):
        f = scan("glpat-" + "AbCdEfGhIjKlMnOpQrSt")  # 20 chars
        assert any(x.rule_id == "gitlab-pat" for x in f)

    def test_npm_token(self):
        f = scan("npm_" + "X" * 36)
        assert any(x.rule_id == "npm-token" for x in f)

    def test_slack_token(self):
        f = scan("xoxb-" + "1234567890-abcdef")
        assert any(x.rule_id == "slack-token" for x in f)

    def test_slack_webhook(self):
        url = "https://hooks.slack.com/services/T12345678/B12345678/" + "x" * 24
        f = scan(url)
        assert any(x.rule_id == "slack-webhook" for x in f)

    def test_discord_webhook(self):
        url = "https://discord.com/api/webhooks/12345678901234567/" + "a" * 68
        f = scan(url)
        assert any(x.rule_id == "discord-webhook" for x in f)

    def test_telegram_bot_token(self):
        f = scan("123456789:AA" + "x" * 33)
        assert any(x.rule_id == "telegram-bot-token" for x in f)

    def test_twilio_sid(self):
        f = scan("AC" + "1234567890abcdef" * 2)
        assert any(x.rule_id == "twilio-sid" for x in f)

    def test_sendgrid_key(self):
        f = scan("SG." + "x" * 22 + "." + "y" * 43)
        assert any(x.rule_id == "sendgrid-key" for x in f)

    def test_mailgun_key(self):
        f = scan("key-" + "0123456789abcdef" * 2)
        assert any(x.rule_id == "mailgun-key" for x in f)

    def test_mailchimp_key(self):
        # Source split via string concatenation so GitHub push-protection
        # doesn't pattern-match the Mailchimp regex against this synthetic
        # fixture; the runtime value is unchanged.
        f = scan("0123456789abcdef" * 2 + "-us12")
        assert any(x.rule_id == "mailchimp-key" for x in f)

    def test_stripe_secret_key(self):
        f = scan("sk_live_" + "abcdefghij" * 2 + "abcd")
        assert any(x.rule_id == "stripe-secret-key" for x in f)
        f2 = scan("sk_test_" + "1234567890" * 2 + "wxyz")
        assert any(x.rule_id == "stripe-secret-key" for x in f2)

    def test_stripe_restricted_key(self):
        f = scan("rk_live_" + "abcdefghij" * 2 + "abcd")
        assert any(x.rule_id == "stripe-restricted-key" for x in f)

    def test_openai_legacy_key(self):
        f = scan("sk-" + "X" * 48)
        assert any(x.rule_id == "openai-key" for x in f)

    def test_openai_project_key(self):
        # Needs entropy >= 3.5; split to avoid GitHub secret-scanning alert.
        f = scan("sk-proj-" + "Abcd1234EfGh5678IjKl9012MnOp3456QrSt7890")
        assert any(x.rule_id == "openai-project-key" for x in f)

    def test_anthropic_key(self):
        f = scan("sk-ant-" + "AbCdEfGhIjKlMnOpQrStUvWxYz1234567890" * 2 + "ABCDEFGHIJKLMNOPQRSTUVW")
        assert any(x.rule_id == "anthropic-key" for x in f)

    def test_jwt(self):
        # Split to avoid GitHub secret-scanning alert on this synthetic JWT.
        f = scan(
            "eyJhbGciOiJIUzI1NiIs."
            + "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
            + "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJVadQssw5c"
        )
        assert any(x.rule_id == "jwt" for x in f)

    def test_generic_secret(self):
        f = scan("api_key: '" + "Abcd1234EfGh5678IjKl9012MnOp3456" + "'")
        assert any(x.rule_id == "generic-secret" for x in f)

    def test_env_assignment_high_entropy(self):
        f = scan("API_KEY=Z9k2p1J4mNqLwR8tH6vBxDcEgFsX5yU0a")
        assert any(x.rule_id == "env-assignment" for x in f)

    def test_env_assignment_low_entropy_skipped(self):
        f = scan("API_KEY=hunter2")
        # entropy < 3.0 OR length < 8 → no env-assignment finding
        assert not any(x.rule_id == "env-assignment" for x in f)

    def test_connection_string(self):
        f = scan("postgres://user:pass@host:5432/db")
        assert any(x.rule_id == "connection-string" for x in f)
        f2 = scan("mongodb://u:p@host/db")
        assert any(x.rule_id == "connection-string" for x in f2)


class TestScanNegative:
    """Patterns that must NOT match (false-positive guards)."""

    def test_random_text(self):
        assert scan("hello world") == []

    def test_empty(self):
        assert scan("") == []

    def test_low_entropy_generic_secret(self):
        # Below entropy threshold of 3.5
        f = scan("api_key: 'aaaaaaaaaaaaaaaaaaaaaa'")
        assert not any(x.rule_id == "generic-secret" for x in f)

    def test_short_aws_prefix_no_false_match(self):
        # AKIA prefix without 16 trailing alphanumerics
        assert scan("AKIA short") == []


class TestPerformance:
    def test_100kb_under_50ms(self):
        # Mostly random text, a few real secrets sprinkled in
        text = "lorem ipsum dolor sit amet " * 4000  # ~100 KB
        text += "AKIAIOSFODNN7EXAMPLE"
        start = time.monotonic()
        findings = scan(text)
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms < 50, f"scan took {elapsed_ms:.1f}ms, budget is 50ms"
        assert any(x.rule_id == "aws-access-key" for x in findings)


class TestFindingShape:
    def test_finding_is_dataclass_with_fields(self):
        f = scan("My AWS key is AKIAIOSFODNN7EXAMPLE")
        assert len(f) == 1
        finding = f[0]
        assert isinstance(finding, Finding)
        assert finding.rule_id == "aws-access-key"
        assert finding.description == "AWS Access Key ID"
        assert finding.match_redacted == "AKIA****MPLE"
        assert finding.secret_value == "AKIAIOSFODNN7EXAMPLE"
