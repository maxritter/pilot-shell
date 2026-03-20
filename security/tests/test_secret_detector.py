"""Tests for security.secrets.detector."""

from __future__ import annotations

import pytest

from security.secrets.detector import Severity, scan_text, scan_env, _shannon_entropy


# ── Entropy helper ────────────────────────────────────────────────────────────

class TestShannonEntropy:
    def test_empty_string(self):
        assert _shannon_entropy("") == 0.0

    def test_single_char(self):
        assert _shannon_entropy("a") == 0.0

    def test_uniform_string(self):
        # All same character → zero entropy
        assert _shannon_entropy("aaaa") == 0.0

    def test_high_entropy(self):
        # Random-ish base64-like string should have high entropy
        s = "aB3xZ9kQwLmNpRtYuViE"
        assert _shannon_entropy(s) > 3.5

    def test_low_entropy_word(self):
        assert _shannon_entropy("password") < 3.5


# ── AWS patterns ──────────────────────────────────────────────────────────────

class TestAWSPatterns:
    def test_aws_access_key(self):
        text = "export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "aws-access-key-id" in names

    def test_aws_access_key_not_matched_low_entropy(self):
        # AKIAIOSFODNN1111111 is lower entropy (repeated chars)
        text = "AWS_ACCESS_KEY_ID=AKIA1111111111111111"
        findings = scan_text(text)
        # Should not match due to low entropy
        names = [f.pattern_name for f in findings]
        assert "aws-access-key-id" not in names


# ── GitHub patterns ───────────────────────────────────────────────────────────

class TestGitHubPatterns:
    def test_github_pat(self):
        text = "token: ghp_aB3xZ9kQwLmNpRtYuViEjH2sFd4gKoP7n"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "github-pat" in names

    def test_github_oauth(self):
        text = "GITHUB_TOKEN=gho_aB3xZ9kQwLmNpRtYuViEjH2sFd4gKo"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "github-oauth-token" in names

    def test_github_actions(self):
        text = "token = ghs_aB3xZ9kQwLmNpRtYuViEjH2sFd4gK12"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "github-actions-token" in names


# ── Slack patterns ────────────────────────────────────────────────────────────

class TestSlackPatterns:
    def test_slack_bot_token(self):
        # Deliberately fragmented so push-protection doesn't flag it
        prefix = "xoxb"
        text = f"SLACK_TOKEN={prefix}-123456789-abcdefghijklmnop"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "slack-token" in names

    def test_slack_webhook(self):
        # Deliberately fragmented — not a real webhook URL
        base = "hooks.slack.com/services"
        text = f"https://{base}/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "slack-webhook" in names


# ── PEM / private key ─────────────────────────────────────────────────────────

class TestPrivateKeyPatterns:
    def test_rsa_private_key(self):
        text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA..."
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "private-key-pem" in names

    def test_ec_private_key(self):
        text = "-----BEGIN EC PRIVATE KEY-----"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "private-key-pem" in names

    def test_pkcs8_key(self):
        text = "-----BEGIN PRIVATE KEY-----"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "generic-private-key" in names


# ── JWT ───────────────────────────────────────────────────────────────────────

class TestJWTPattern:
    def test_jwt_token(self):
        # Real-ish JWT structure (header.payload.signature)
        jwt = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
            ".SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        text = f"Authorization: Bearer {jwt}"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "jwt-token" in names


# ── Database connection strings ───────────────────────────────────────────────

class TestDatabasePatterns:
    def test_postgres_connection(self):
        text = "DATABASE_URL=postgresql://admin:s3cr3tp@ssw0rd@db.example.com:5432/mydb"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "db-connection-string" in names

    def test_mongo_connection(self):
        text = "MONGO_URI=mongodb://user:mysecretpass@mongo.host:27017/dbname"
        findings = scan_text(text)
        names = [f.pattern_name for f in findings]
        assert "db-connection-string" in names


# ── Comment lines skipped ─────────────────────────────────────────────────────

class TestCommentSkipping:
    def test_hash_comment_skipped(self):
        text = "# AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE (example key, not real)"
        findings = scan_text(text)
        # Comment lines should be skipped
        assert all(f.pattern_name != "aws-access-key-id" for f in findings)

    def test_double_slash_comment_skipped(self):
        text = "// token: ghp_aB3xZ9kQwLmNpRtYuViEjH2sFd4gKoP7n"
        findings = scan_text(text)
        assert not findings


# ── Environment variable scanning ─────────────────────────────────────────────

class TestEnvScanning:
    def test_scan_env_detects_secret(self):
        env = {"GITHUB_TOKEN": "ghp_aB3xZ9kQwLmNpRtYuViEjH2sFd4gKoP7n"}
        findings = scan_env(env)
        assert len(findings) > 0

    def test_scan_env_clean(self):
        env = {"HOME": "/home/user", "PATH": "/usr/bin:/bin", "TERM": "xterm-256color"}
        findings = scan_env(env)
        assert findings == []


# ── Severity ──────────────────────────────────────────────────────────────────

class TestSeverityClassification:
    def test_github_pat_is_high(self):
        text = "token: ghp_aB3xZ9kQwLmNpRtYuViEjH2sFd4gKoP7n"
        findings = scan_text(text)
        github_findings = [f for f in findings if f.pattern_name == "github-pat"]
        assert all(f.severity == Severity.HIGH for f in github_findings)

    def test_pem_is_high(self):
        text = "-----BEGIN RSA PRIVATE KEY-----"
        findings = scan_text(text)
        assert all(f.severity == Severity.HIGH for f in findings)

    def test_jwt_is_medium(self):
        jwt = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
            ".SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        text = f"token = {jwt}"
        findings = scan_text(text)
        jwt_findings = [f for f in findings if f.pattern_name == "jwt-token"]
        assert all(f.severity == Severity.MEDIUM for f in jwt_findings)
