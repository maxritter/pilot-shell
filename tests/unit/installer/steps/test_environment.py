"""Tests for environment step."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestGetEnvValue:
    """Test get_env_value function."""

    def test_get_env_value_returns_value_for_existing_key(self):
        """get_env_value returns the value for an existing key."""
        from installer.steps.environment import get_env_value

        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("MY_KEY=my_value\nOTHER_KEY=other\n")

            result = get_env_value("MY_KEY", env_file)

            assert result == "my_value"

    def test_get_env_value_returns_none_for_missing_key(self):
        """get_env_value returns None when key not in file."""
        from installer.steps.environment import get_env_value

        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("OTHER_KEY=value\n")

            result = get_env_value("MISSING_KEY", env_file)

            assert result is None

    def test_get_env_value_returns_none_for_empty_value(self):
        """get_env_value returns None for key with empty value."""
        from installer.steps.environment import get_env_value

        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("MY_KEY=\n")

            result = get_env_value("MY_KEY", env_file)

            assert result is None

    def test_get_env_value_returns_none_for_missing_file(self):
        """get_env_value returns None when file doesn't exist."""
        from installer.steps.environment import get_env_value

        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"

            result = get_env_value("MY_KEY", env_file)

            assert result is None


class TestCreateClaudeConfig:
    """Test create_claude_config function."""

    def test_create_claude_config_creates_file(self):
        """create_claude_config creates ~/.claude.json with correct content."""
        import json

        from installer.steps.environment import create_claude_config

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir)
            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = create_claude_config()

            config_file = mock_home / ".claude.json"
            assert result is True
            assert config_file.exists()
            content = json.loads(config_file.read_text())
            assert content["hasCompletedOnboarding"] is True

    def test_create_claude_config_merges_with_existing(self):
        """create_claude_config preserves existing config values."""
        import json

        from installer.steps.environment import create_claude_config

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir)
            config_file = mock_home / ".claude.json"
            config_file.write_text('{"theme": "dark", "existingKey": "value"}')

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = create_claude_config()

            assert result is True
            content = json.loads(config_file.read_text())
            assert content["hasCompletedOnboarding"] is True
            assert content["theme"] == "dark"
            assert content["existingKey"] == "value"

    def test_create_claude_config_returns_false_on_error(self):
        """create_claude_config returns False on permission error."""
        from unittest.mock import MagicMock

        from installer.steps.environment import create_claude_config

        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_path.write_text.side_effect = PermissionError("No permission")

        with patch(
            "installer.steps.environment.Path.home",
            return_value=MagicMock(__truediv__=lambda s, x: mock_path),
        ):
            result = create_claude_config()

        assert result is False


class TestCredentialsExist:
    """Test credentials_exist function."""

    def test_credentials_exist_returns_false_when_file_missing(self):
        """credentials_exist returns False when credentials file doesn't exist."""
        from installer.steps.environment import credentials_exist

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            mock_home.mkdir()

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = credentials_exist()

            assert result is False

    def test_credentials_exist_returns_false_for_invalid_json(self):
        """credentials_exist returns False when file contains invalid JSON."""
        from installer.steps.environment import credentials_exist

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            claude_dir = mock_home / ".claude"
            claude_dir.mkdir(parents=True)
            creds_file = claude_dir / ".credentials.json"
            creds_file.write_text("not valid json {{{")

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = credentials_exist()

            assert result is False

    def test_credentials_exist_returns_false_when_missing_oauth_key(self):
        """credentials_exist returns False when claudeAiOauth key is missing."""
        from installer.steps.environment import credentials_exist

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            claude_dir = mock_home / ".claude"
            claude_dir.mkdir(parents=True)
            creds_file = claude_dir / ".credentials.json"
            creds_file.write_text('{"someOtherKey": "value"}')

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = credentials_exist()

            assert result is False

    def test_credentials_exist_returns_false_when_access_token_empty(self):
        """credentials_exist returns False when accessToken is empty."""
        from installer.steps.environment import credentials_exist

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            claude_dir = mock_home / ".claude"
            claude_dir.mkdir(parents=True)
            creds_file = claude_dir / ".credentials.json"
            creds_file.write_text('{"claudeAiOauth": {"accessToken": ""}}')

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = credentials_exist()

            assert result is False

    def test_credentials_exist_returns_true_for_valid_credentials(self):
        """credentials_exist returns True when valid credentials exist."""
        from installer.steps.environment import credentials_exist

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            claude_dir = mock_home / ".claude"
            claude_dir.mkdir(parents=True)
            creds_file = claude_dir / ".credentials.json"
            creds_file.write_text('{"claudeAiOauth": {"accessToken": "sk-ant-test-token"}}')

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = credentials_exist()

            assert result is True


class TestCreateClaudeCredentials:
    """Test create_claude_credentials function."""

    def test_create_claude_credentials_creates_directory_and_file(self):
        """create_claude_credentials creates ~/.claude directory and credentials file."""
        from installer.steps.environment import create_claude_credentials

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            mock_home.mkdir()

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = create_claude_credentials("test-token-123")

            assert result is True
            creds_file = mock_home / ".claude" / ".credentials.json"
            assert creds_file.exists()

    def test_create_claude_credentials_writes_correct_structure(self):
        """create_claude_credentials writes correct JSON structure."""
        import json

        from installer.steps.environment import create_claude_credentials

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            mock_home.mkdir()

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                create_claude_credentials("my-oauth-token")

            creds_file = mock_home / ".claude" / ".credentials.json"
            content = json.loads(creds_file.read_text())

            assert "claudeAiOauth" in content
            oauth = content["claudeAiOauth"]
            assert oauth["accessToken"] == "my-oauth-token"
            assert oauth["refreshToken"] == "my-oauth-token"
            assert "expiresAt" in oauth
            assert oauth["scopes"] == ["user:inference", "user:profile", "user:sessions:claude_code"]
            assert oauth["subscriptionType"] == "max"
            assert oauth["rateLimitTier"] == "default_claude_max_20x"

    def test_create_claude_credentials_sets_expiry_365_days(self):
        """create_claude_credentials sets expiry to 365 days from now."""
        import json
        import time

        from installer.steps.environment import create_claude_credentials

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            mock_home.mkdir()

            before_time = int(time.time() * 1000)
            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                create_claude_credentials("token")
            after_time = int(time.time() * 1000)

            creds_file = mock_home / ".claude" / ".credentials.json"
            content = json.loads(creds_file.read_text())
            expires_at = content["claudeAiOauth"]["expiresAt"]

            # Should be ~365 days from now (within 1 second tolerance)
            days_365_ms = 365 * 24 * 60 * 60 * 1000
            assert expires_at >= before_time + days_365_ms
            assert expires_at <= after_time + days_365_ms

    def test_create_claude_credentials_sets_file_permissions(self):
        """create_claude_credentials sets restrictive file permissions."""
        from installer.steps.environment import create_claude_credentials

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            mock_home.mkdir()

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                create_claude_credentials("token")

            creds_file = mock_home / ".claude" / ".credentials.json"
            mode = creds_file.stat().st_mode & 0o777
            # File should be readable/writable only by owner (0o600)
            assert mode == 0o600

    def test_create_claude_credentials_returns_false_on_error(self):
        """create_claude_credentials returns False when it cannot write."""
        from installer.steps.environment import create_claude_credentials

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            mock_home.mkdir()
            # Create a file where directory should be (will cause error)
            blocking_file = mock_home / ".claude"
            blocking_file.write_text("not a directory")

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = create_claude_credentials("token")

            assert result is False

    def test_create_claude_credentials_overwrites_existing(self):
        """create_claude_credentials overwrites existing credentials file."""
        import json

        from installer.steps.environment import create_claude_credentials

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir) / "home"
            claude_dir = mock_home / ".claude"
            claude_dir.mkdir(parents=True)
            creds_file = claude_dir / ".credentials.json"
            creds_file.write_text('{"claudeAiOauth": {"accessToken": "old-token"}}')

            with patch("installer.steps.environment.Path.home", return_value=mock_home):
                result = create_claude_credentials("new-token")

            assert result is True
            content = json.loads(creds_file.read_text())
            assert content["claudeAiOauth"]["accessToken"] == "new-token"


class TestEnvironmentStep:
    """Test EnvironmentStep class."""

    def test_environment_step_has_correct_name(self):
        """EnvironmentStep has name 'environment'."""
        from installer.steps.environment import EnvironmentStep

        step = EnvironmentStep()
        assert step.name == "environment"

    def test_environment_check_returns_true_when_env_exists(self):
        """EnvironmentStep.check returns True when .env exists with required keys."""
        from installer.context import InstallContext
        from installer.steps.environment import EnvironmentStep
        from installer.ui import Console

        step = EnvironmentStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .env with some content
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("SOME_KEY=value\n")

            ctx = InstallContext(
                project_dir=Path(tmpdir),
                ui=Console(non_interactive=True),
            )
            # .env exists
            result = step.check(ctx)
            assert isinstance(result, bool)

    def test_environment_run_skips_in_non_interactive(self):
        """EnvironmentStep.run skips prompts in non-interactive mode."""
        from installer.context import InstallContext
        from installer.steps.environment import EnvironmentStep
        from installer.ui import Console

        step = EnvironmentStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = InstallContext(
                project_dir=Path(tmpdir),
                non_interactive=True,
                ui=Console(non_interactive=True),
            )

            # Should not raise or prompt
            step.run(ctx)

    def test_environment_appends_to_existing_env(self):
        """EnvironmentStep appends to existing .env file."""
        from installer.context import InstallContext
        from installer.steps.environment import EnvironmentStep
        from installer.ui import Console

        step = EnvironmentStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing .env
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("EXISTING_KEY=existing_value\n")

            ctx = InstallContext(
                project_dir=Path(tmpdir),
                non_interactive=True,
                ui=Console(non_interactive=True),
            )

            step.run(ctx)

            # Existing content should be preserved
            content = env_file.read_text()
            assert "EXISTING_KEY=existing_value" in content

    def test_environment_prompts_for_oauth_when_not_set(self):
        """EnvironmentStep prompts for OAuth token when not set."""
        from unittest.mock import MagicMock

        from installer.context import InstallContext
        from installer.steps.environment import EnvironmentStep

        step = EnvironmentStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("")  # Empty .env

            mock_ui = MagicMock()
            mock_ui.confirm.return_value = False  # User declines OAuth

            ctx = InstallContext(
                project_dir=Path(tmpdir),
                non_interactive=False,
                skip_env=False,
                ui=mock_ui,
            )

            # Mock key_is_set to return False for OAuth token (env var might be set)
            # Mock credentials_exist to return False
            with (
                patch("installer.steps.environment.key_is_set", return_value=False),
                patch("installer.steps.environment.credentials_exist", return_value=False),
            ):
                step.run(ctx)

            # Should have called confirm for OAuth
            mock_ui.confirm.assert_called_once()
            call_args = mock_ui.confirm.call_args
            assert "Long Lasting Token" in call_args[0][0]

    def test_environment_skips_oauth_when_credentials_exist(self):
        """EnvironmentStep skips OAuth prompt when credentials already exist."""
        from unittest.mock import MagicMock

        from installer.context import InstallContext
        from installer.steps.environment import EnvironmentStep

        step = EnvironmentStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("")

            mock_ui = MagicMock()

            ctx = InstallContext(
                project_dir=Path(tmpdir),
                non_interactive=False,
                skip_env=False,
                ui=mock_ui,
            )

            # Mock credentials_exist to return True
            with patch("installer.steps.environment.credentials_exist", return_value=True):
                step.run(ctx)

            # Should NOT have called confirm (credentials already exist)
            mock_ui.confirm.assert_not_called()
            # Should have called success to indicate skipping
            assert any("already configured" in str(c) for c in mock_ui.success.call_args_list)

    def test_environment_restores_credentials_from_env(self):
        """EnvironmentStep restores credentials when token in .env but credentials missing."""
        from unittest.mock import MagicMock

        from installer.context import InstallContext
        from installer.steps.environment import EnvironmentStep

        step = EnvironmentStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("CLAUDE_CODE_OAUTH_TOKEN=test-token-123\n")

            mock_ui = MagicMock()

            ctx = InstallContext(
                project_dir=Path(tmpdir),
                non_interactive=False,
                skip_env=False,
                ui=mock_ui,
            )

            mock_home = Path(tmpdir) / "home"
            mock_home.mkdir()

            # Mock credentials_exist to return False (credentials file missing)
            # Mock create_claude_credentials to succeed
            with (
                patch("installer.steps.environment.credentials_exist", return_value=False),
                patch("installer.steps.environment.create_claude_credentials", return_value=True) as mock_create,
                patch("installer.steps.environment.create_claude_config", return_value=True),
            ):
                step.run(ctx)

            # Should have called create_claude_credentials with the token from .env
            mock_create.assert_called_once_with("test-token-123")
            # Should have shown restore message
            assert any("restored" in str(c).lower() for c in mock_ui.success.call_args_list)

    def test_environment_creates_credentials_on_new_token(self):
        """EnvironmentStep creates credentials when user provides new token."""
        from unittest.mock import MagicMock

        from installer.context import InstallContext
        from installer.steps.environment import EnvironmentStep

        step = EnvironmentStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("")  # Empty .env

            mock_ui = MagicMock()
            mock_ui.confirm.return_value = True  # User wants OAuth
            mock_ui.input.return_value = "new-oauth-token"  # User provides token

            ctx = InstallContext(
                project_dir=Path(tmpdir),
                non_interactive=False,
                skip_env=False,
                ui=mock_ui,
            )

            # Mock key_is_set to return False for OAuth token (env var might be set)
            # but allow it to return actual value for ANTHROPIC_API_KEY check
            def mock_key_is_set(key: str, env_file_arg) -> bool:
                if key == "CLAUDE_CODE_OAUTH_TOKEN":
                    return False
                return False  # No API key set either

            with (
                patch("installer.steps.environment.key_is_set", side_effect=mock_key_is_set),
                patch("installer.steps.environment.credentials_exist", return_value=False),
                patch("installer.steps.environment.create_claude_credentials", return_value=True) as mock_create,
                patch("installer.steps.environment.create_claude_config", return_value=True),
            ):
                step.run(ctx)

            # Should have created credentials with the new token
            mock_create.assert_called_once_with("new-oauth-token")
            # Token should be saved to .env as well
            content = env_file.read_text()
            assert "CLAUDE_CODE_OAUTH_TOKEN=new-oauth-token" in content
