"""Tests for one-time model config migrations."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestMigrationV1:
    """Migration v0 → v1: Update model routing from v7.0 to v7.1."""

    def test_spec_verify_opus_migrated_through_to_opus(self, tmp_path: Path) -> None:
        """spec-verify: v1 migrates opus→sonnet, then v8 migrates sonnet→opus."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {"spec-verify": "opus", "spec-plan": "opus"},
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        # v8 renames commands→skills and defaults spec-verify to opus
        assert migrated["skills"]["spec-verify"] == "opus"
        assert migrated["skills"]["spec-plan"] == "opus"
        assert "commands" not in migrated

    def test_spec_verify_sonnet_migrated_to_opus(self, tmp_path: Path) -> None:
        """spec-verify set to sonnet is migrated to opus by v8."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {"spec-verify": "sonnet"},
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        # v8 defaults sonnet→opus for spec-verify
        assert migrated["skills"]["spec-verify"] == "opus"

    def test_stale_agent_keys_removed(self, tmp_path: Path) -> None:
        """Old agent keys from v7.0 are removed."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "agents": {
                        "plan-challenger": "sonnet",
                        "plan-verifier": "sonnet",
                        "spec-reviewer-compliance": "sonnet",
                        "spec-reviewer-quality": "opus",
                        "spec-reviewer-goal": "sonnet",
                        "plan-reviewer": "sonnet",
                        "spec-reviewer": "sonnet",
                    },
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        agents = migrated["agents"]
        assert "plan-challenger" not in agents
        assert "plan-verifier" not in agents
        assert "spec-reviewer-compliance" not in agents
        assert "spec-reviewer-quality" not in agents
        assert "spec-reviewer-goal" not in agents
        # v7 renames plan-reviewer → spec-review, spec-reviewer → changes-review
        assert agents["spec-review"] == "sonnet"
        assert agents["changes-review"] == "sonnet"

    def test_new_agent_keys_added_if_missing(self, tmp_path: Path) -> None:
        """New agent keys are added when they don't exist yet."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "agents": {
                        "plan-challenger": "sonnet",
                        "plan-verifier": "sonnet",
                    },
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        # v1 adds plan-reviewer/spec-reviewer, then v7 renames them
        assert migrated["agents"]["spec-review"] == "sonnet"
        assert migrated["agents"]["changes-review"] == "sonnet"

    def test_config_version_set_after_migration(self, tmp_path: Path) -> None:
        """_configVersion is set to current after migration."""
        from installer.steps.config_migration import (
            CURRENT_CONFIG_VERSION,
            migrate_model_config,
        )

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({"model": "opus", "commands": {}}))

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION


class TestMigrationV2:
    """Migration v1 → v2: Switch sync and learn commands from sonnet to opus."""

    def test_sync_and_learn_migrated_to_opus(self, tmp_path: Path) -> None:
        """Both sync and learn skills are migrated from sonnet to opus."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {"sync": "sonnet", "learn": "sonnet"},
                    "_configVersion": 1,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        # v8 renames commands→skills
        assert migrated["skills"]["sync"] == "opus"
        assert migrated["skills"]["learn"] == "opus"

    def test_already_opus_not_changed(self, tmp_path: Path) -> None:
        """Skills already set to opus are left alone."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {"sync": "opus", "learn": "opus"},
                    "_configVersion": 1,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["skills"]["sync"] == "opus"
        assert migrated["skills"]["learn"] == "opus"

    def test_partial_migration(self, tmp_path: Path) -> None:
        """Only sonnet values are migrated; opus values are untouched."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {"sync": "opus", "learn": "sonnet"},
                    "_configVersion": 1,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["skills"]["sync"] == "opus"
        assert migrated["skills"]["learn"] == "opus"


class TestMigrationIdempotency:
    """Migrations are skipped when already applied."""

    def test_skips_when_version_current(self, tmp_path: Path) -> None:
        """No changes when _configVersion matches current."""
        from installer.steps.config_migration import (
            CURRENT_CONFIG_VERSION,
            migrate_model_config,
        )

        config_path = tmp_path / "config.json"
        original = {
            "model": "opus",
            "commands": {"spec-verify": "opus"},
            "_configVersion": CURRENT_CONFIG_VERSION,
        }
        config_path.write_text(json.dumps(original))

        result = migrate_model_config(config_path)

        assert result is False
        assert json.loads(config_path.read_text()) == original

    def test_skips_when_no_config_file(self, tmp_path: Path) -> None:
        """Returns False when config file doesn't exist."""
        from installer.steps.config_migration import migrate_model_config

        result = migrate_model_config(tmp_path / "nonexistent.json")

        assert result is False

    def test_second_run_is_noop(self, tmp_path: Path) -> None:
        """Running migration twice doesn't change anything the second time."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {"spec-verify": "opus"},
                    "agents": {"plan-challenger": "sonnet"},
                }
            )
        )

        migrate_model_config(config_path)
        first_result = config_path.read_text()

        result = migrate_model_config(config_path)

        assert result is False
        assert config_path.read_text() == first_result


class TestMigrationPreservesExistingData:
    """Migrations preserve non-model keys in config.json."""

    def test_preserves_non_model_keys(self, tmp_path: Path) -> None:
        """Keys like auto_update are untouched."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "extendedContext": True,
                    "auto_update": True,
                    "commands": {"spec-verify": "opus"},
                    "agents": {},
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        assert migrated["extendedContext"] is True
        assert migrated["auto_update"] is True
        assert migrated["model"] == "opus"

    def test_handles_missing_commands_key(self, tmp_path: Path) -> None:
        """Config without commands key doesn't crash."""
        from installer.steps.config_migration import (
            CURRENT_CONFIG_VERSION,
            migrate_model_config,
        )

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({"model": "opus"}))

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION

    def test_handles_missing_agents_key(self, tmp_path: Path) -> None:
        """Config without agents key doesn't crash."""
        from installer.steps.config_migration import (
            CURRENT_CONFIG_VERSION,
            migrate_model_config,
        )

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({"model": "opus", "commands": {}}))

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION


class TestMigrationV3:
    """Migration v2 → v3: Disable plan review, spec review, and worktree support.

    Note: These tests use _configVersion: 2, so both v3 and v4 run.
    v3 disables, then v4 re-enables. Tests for v3 in isolation use
    the unit function directly.
    """

    def test_v3_disables_and_v4_preserves_user_choice(self, tmp_path: Path) -> None:
        """v3 disables worktree, v4 no longer force-re-enables it (preserves user choice)."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": True, "specReviewer": True},
                    "specWorkflow": {
                        "worktreeSupport": True,
                        "askQuestionsDuringPlanning": True,
                        "planApproval": True,
                    },
                    "_configVersion": 2,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        # v3 disables worktree, v4 re-enables reviewers but NOT worktree, v7 renames
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True
        # v4 no longer forces worktree back to True — respects whatever v3 set
        assert migrated["specWorkflow"]["worktreeSupport"] is False
        assert migrated["specWorkflow"]["askQuestionsDuringPlanning"] is True
        assert migrated["specWorkflow"]["planApproval"] is True

    def test_v3_unit_disables_when_enabled(self, tmp_path: Path) -> None:
        """v3 migration function disables enabled toggles."""
        from installer.steps.config_migration import _migration_v3

        raw = {
            "reviewerAgents": {"planReviewer": True, "specReviewer": True},
            "specWorkflow": {
                "worktreeSupport": True,
                "askQuestionsDuringPlanning": True,
                "planApproval": True,
            },
        }

        result = _migration_v3(raw)

        assert result is True
        assert raw["reviewerAgents"]["planReviewer"] is False
        assert raw["reviewerAgents"]["specReviewer"] is False
        assert raw["specWorkflow"]["worktreeSupport"] is False

    def test_v3_unit_creates_defaults_when_missing(self, tmp_path: Path) -> None:
        """v3 migration function creates defaults when keys are missing."""
        from installer.steps.config_migration import _migration_v3

        raw: dict = {"model": "opus"}

        result = _migration_v3(raw)

        assert result is True
        assert raw["reviewerAgents"]["planReviewer"] is False
        assert raw["reviewerAgents"]["specReviewer"] is False
        assert raw["specWorkflow"]["worktreeSupport"] is False
        assert raw["specWorkflow"]["askQuestionsDuringPlanning"] is True
        assert raw["specWorkflow"]["planApproval"] is True

    def test_preserves_other_spec_workflow_toggles(self, tmp_path: Path) -> None:
        """askQuestionsDuringPlanning and planApproval are preserved through v3+v4."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": True, "specReviewer": True},
                    "specWorkflow": {
                        "worktreeSupport": True,
                        "askQuestionsDuringPlanning": False,
                        "planApproval": False,
                    },
                    "_configVersion": 2,
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        assert migrated["specWorkflow"]["askQuestionsDuringPlanning"] is False
        assert migrated["specWorkflow"]["planApproval"] is False


class TestMigrationV4:
    """Migration v3 → v4: Enable reviewer subagents, preserve worktree user choice."""

    def test_enables_reviewers_preserves_worktree(self, tmp_path: Path) -> None:
        """Reviewer agents are enabled but worktree is NOT force-enabled."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": False, "specReviewer": False},
                    "specWorkflow": {
                        "worktreeSupport": False,
                        "askQuestionsDuringPlanning": True,
                        "planApproval": True,
                    },
                    "_configVersion": 3,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        # v4 enables reviewers, then v7 renames keys
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True
        # v4 no longer forces worktree — user's False is preserved
        assert migrated["specWorkflow"]["worktreeSupport"] is False
        assert migrated["specWorkflow"]["askQuestionsDuringPlanning"] is True
        assert migrated["specWorkflow"]["planApproval"] is True

    def test_already_enabled_not_changed(self, tmp_path: Path) -> None:
        """Toggles already set to true are left alone."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": True, "specReviewer": True},
                    "specWorkflow": {
                        "worktreeSupport": True,
                        "askQuestionsDuringPlanning": True,
                        "planApproval": True,
                    },
                    "_configVersion": 3,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        # v7 renames keys
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True
        assert migrated["specWorkflow"]["worktreeSupport"] is True

    def test_partial_disabled(self, tmp_path: Path) -> None:
        """Only disabled toggles are enabled; already-true ones stay true."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": False, "specReviewer": True},
                    "specWorkflow": {
                        "worktreeSupport": True,
                        "askQuestionsDuringPlanning": True,
                        "planApproval": True,
                    },
                    "_configVersion": 3,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        # v4 enables both, then v7 renames
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True
        assert migrated["specWorkflow"]["worktreeSupport"] is True

    def test_missing_reviewer_agents_creates_enabled_defaults(self, tmp_path: Path) -> None:
        """Missing reviewerAgents key gets created with enabled defaults."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {},
                    "_configVersion": 3,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        # v4 creates with old names enabled, v7 renames
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True

    def test_missing_spec_workflow_creates_safe_defaults(self, tmp_path: Path) -> None:
        """Missing specWorkflow key gets created with worktree disabled (safe default)."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": False, "specReviewer": False},
                    "_configVersion": 3,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["specWorkflow"]["worktreeSupport"] is False
        assert migrated["specWorkflow"]["askQuestionsDuringPlanning"] is True
        assert migrated["specWorkflow"]["planApproval"] is True

    def test_preserves_other_spec_workflow_toggles(self, tmp_path: Path) -> None:
        """askQuestionsDuringPlanning and planApproval are preserved."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": False, "specReviewer": False},
                    "specWorkflow": {
                        "worktreeSupport": False,
                        "askQuestionsDuringPlanning": False,
                        "planApproval": False,
                    },
                    "_configVersion": 3,
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        assert migrated["specWorkflow"]["askQuestionsDuringPlanning"] is False
        assert migrated["specWorkflow"]["planApproval"] is False


class TestMigrationV5:
    """Migration v4 → v5: Enable extended context (1M) by default."""

    def test_enables_extended_context_when_false(self, tmp_path: Path) -> None:
        """extendedContext: false gets set to true."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "extendedContext": False,
                    "_configVersion": 4,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["extendedContext"] is True

    def test_noop_when_already_true(self, tmp_path: Path) -> None:
        """extendedContext: true stays true."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "extendedContext": True,
                    "_configVersion": 4,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["extendedContext"] is True

    def test_sets_true_when_absent(self, tmp_path: Path) -> None:
        """Missing extendedContext key gets set to true."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "_configVersion": 4,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["extendedContext"] is True

    def test_v5_unit_returns_false_when_already_true(self) -> None:
        """Unit function returns False when no change needed."""
        from installer.steps.config_migration import _migration_v5

        raw: dict = {"extendedContext": True}
        assert _migration_v5(raw) is False

    def test_v5_unit_sets_true_when_false(self) -> None:
        """Unit function sets extendedContext to true."""
        from installer.steps.config_migration import _migration_v5

        raw: dict = {"extendedContext": False}
        result = _migration_v5(raw)

        assert result is True
        assert raw["extendedContext"] is True


class TestMigrationV6:
    """Migration v5 → v6: Disable reviewer sub-agents for non-Max users."""

    def test_disables_agents_for_pro_users(self, tmp_path: Path) -> None:
        """Pro users get sub-agents disabled."""
        from installer.steps.config_migration import _migration_v6

        raw: dict = {
            "reviewerAgents": {"planReviewer": True, "specReviewer": True},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            result = _migration_v6(raw)

        assert result is True
        assert raw["reviewerAgents"]["planReviewer"] is False
        assert raw["reviewerAgents"]["specReviewer"] is False

    def test_disables_agents_for_team_users(self, tmp_path: Path) -> None:
        """Team users get sub-agents disabled."""
        from installer.steps.config_migration import _migration_v6

        raw: dict = {
            "reviewerAgents": {"planReviewer": True, "specReviewer": True},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="team"):
            result = _migration_v6(raw)

        assert result is True
        assert raw["reviewerAgents"]["planReviewer"] is False
        assert raw["reviewerAgents"]["specReviewer"] is False

    def test_disables_agents_for_enterprise_users(self, tmp_path: Path) -> None:
        """Enterprise users get sub-agents disabled."""
        from installer.steps.config_migration import _migration_v6

        raw: dict = {
            "reviewerAgents": {"planReviewer": True, "specReviewer": True},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="enterprise"):
            result = _migration_v6(raw)

        assert result is True
        assert raw["reviewerAgents"]["planReviewer"] is False
        assert raw["reviewerAgents"]["specReviewer"] is False

    def test_preserves_agents_for_max_users(self, tmp_path: Path) -> None:
        """Max users keep sub-agents enabled."""
        from installer.steps.config_migration import _migration_v6

        raw: dict = {
            "reviewerAgents": {"planReviewer": True, "specReviewer": True},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="max"):
            result = _migration_v6(raw)

        assert result is False
        assert raw["reviewerAgents"]["planReviewer"] is True
        assert raw["reviewerAgents"]["specReviewer"] is True

    def test_no_change_when_detection_fails(self, tmp_path: Path) -> None:
        """When subscription can't be detected, leave settings unchanged."""
        from installer.steps.config_migration import _migration_v6

        raw: dict = {
            "reviewerAgents": {"planReviewer": True, "specReviewer": True},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value=None):
            result = _migration_v6(raw)

        assert result is False
        assert raw["reviewerAgents"]["planReviewer"] is True
        assert raw["reviewerAgents"]["specReviewer"] is True

    def test_creates_reviewer_agents_when_missing(self, tmp_path: Path) -> None:
        """Creates reviewerAgents dict with disabled values for non-Max users."""
        from installer.steps.config_migration import _migration_v6

        raw: dict = {"model": "opus"}

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            result = _migration_v6(raw)

        assert result is True
        assert raw["reviewerAgents"]["planReviewer"] is False
        assert raw["reviewerAgents"]["specReviewer"] is False

    def test_already_disabled_not_modified(self, tmp_path: Path) -> None:
        """Already-disabled agents are not re-modified."""
        from installer.steps.config_migration import _migration_v6

        raw: dict = {
            "reviewerAgents": {"planReviewer": False, "specReviewer": False},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            result = _migration_v6(raw)

        assert result is False
        assert raw["reviewerAgents"]["planReviewer"] is False
        assert raw["reviewerAgents"]["specReviewer"] is False

    def test_full_migration_for_pro_user(self, tmp_path: Path) -> None:
        """Full migrate_model_config disables agents for pro user at version 5."""
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION, migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": True, "specReviewer": True},
                    "extendedContext": True,
                    "_configVersion": 5,
                }
            )
        )

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        # v6 disables, then v7 renames
        assert migrated["reviewerAgents"]["specReview"] is False
        assert migrated["reviewerAgents"]["changesReview"] is False
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION

    def test_full_migration_for_max_user_preserves_agents(self, tmp_path: Path) -> None:
        """Full migrate_model_config preserves agents for max user at version 5."""
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION, migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": True, "specReviewer": True},
                    "extendedContext": True,
                    "_configVersion": 5,
                }
            )
        )

        with patch("installer.steps.config_migration._get_subscription_type", return_value="max"):
            result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        # v7 renames but preserves values
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION


class TestMigrationV7:
    """Migration v6 → v7: Rename reviewer agents and add Codex reviewer config."""

    def test_renames_reviewer_agent_keys(self) -> None:
        """planReviewer → specReview, specReviewer → changesReview."""
        from installer.steps.config_migration import _migration_v7

        raw: dict = {
            "reviewerAgents": {"planReviewer": True, "specReviewer": False},
        }

        result = _migration_v7(raw)

        assert result is True
        assert raw["reviewerAgents"]["specReview"] is True
        assert raw["reviewerAgents"]["changesReview"] is False
        assert "planReviewer" not in raw["reviewerAgents"]
        assert "specReviewer" not in raw["reviewerAgents"]

    def test_renames_agent_model_keys(self) -> None:
        """plan-reviewer → spec-review, spec-reviewer → changes-review."""
        from installer.steps.config_migration import _migration_v7

        raw: dict = {
            "agents": {"plan-reviewer": "opus", "spec-reviewer": "sonnet"},
        }

        result = _migration_v7(raw)

        assert result is True
        assert raw["agents"]["spec-review"] == "opus"
        assert raw["agents"]["changes-review"] == "sonnet"
        assert "plan-reviewer" not in raw["agents"]
        assert "spec-reviewer" not in raw["agents"]

    def test_adds_codex_reviewers_defaults(self) -> None:
        """codexReviewers added with both disabled."""
        from installer.steps.config_migration import _migration_v7

        raw: dict = {"model": "opus"}

        result = _migration_v7(raw)

        assert result is True
        assert raw["codexReviewers"]["specReview"] is False
        assert raw["codexReviewers"]["changesReview"] is False

    def test_preserves_existing_codex_reviewers(self) -> None:
        """Existing codexReviewers not overwritten."""
        from installer.steps.config_migration import _migration_v7

        raw: dict = {
            "codexReviewers": {"specReview": True, "changesReview": True},
        }

        result = _migration_v7(raw)

        assert result is False
        assert raw["codexReviewers"]["specReview"] is True

    def test_noop_when_already_migrated(self) -> None:
        """No changes when keys already use new names."""
        from installer.steps.config_migration import _migration_v7

        raw: dict = {
            "reviewerAgents": {"specReview": True, "changesReview": True},
            "agents": {"spec-review": "sonnet", "changes-review": "sonnet"},
            "codexReviewers": {"specReview": False, "changesReview": False},
        }

        result = _migration_v7(raw)

        assert result is False


class TestGetSubscriptionType:
    """Tests for _get_subscription_type helper."""

    def test_returns_type_from_claude_auth_status(self) -> None:
        """Should return subscription type from claude auth status."""
        from installer.steps.config_migration import _get_subscription_type

        mock_result = MagicMock(
            returncode=0,
            stdout='{"loggedIn": true, "subscriptionType": "max"}',
        )

        with patch("subprocess.run", return_value=mock_result):
            result = _get_subscription_type()

        assert result == "max"

    def test_normalizes_to_lowercase(self) -> None:
        """Should normalize subscription type to lowercase."""
        from installer.steps.config_migration import _get_subscription_type

        mock_result = MagicMock(
            returncode=0,
            stdout='{"loggedIn": true, "subscriptionType": "Pro"}',
        )

        with patch("subprocess.run", return_value=mock_result):
            result = _get_subscription_type()

        assert result == "pro"

    def test_returns_none_when_claude_not_installed(self) -> None:
        """Should return None when claude CLI is not available."""
        from installer.steps.config_migration import _get_subscription_type

        with patch("subprocess.run", side_effect=FileNotFoundError("claude not found")):
            with patch("pathlib.Path.exists", return_value=False):
                result = _get_subscription_type()

        assert result is None

    def test_falls_back_to_credentials_file(self, tmp_path: Path) -> None:
        """Should fall back to credentials file when claude auth status fails."""
        from installer.steps.config_migration import _get_subscription_type

        mock_result = MagicMock(returncode=1, stdout="", stderr="not logged in")
        creds = {"claudeAiOauth": {"subscriptionType": "team"}}

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("pathlib.Path.home", return_value=tmp_path),
        ):
            # Create the expected path structure
            claude_dir = tmp_path / ".claude"
            claude_dir.mkdir(exist_ok=True)
            creds_file = claude_dir / ".credentials.json"
            creds_file.write_text(json.dumps(creds))

            result = _get_subscription_type()

        assert result == "team"

    def test_returns_none_when_no_subscription_type(self) -> None:
        """Should return None when auth status has no subscriptionType."""
        from installer.steps.config_migration import _get_subscription_type

        mock_result = MagicMock(
            returncode=0,
            stdout='{"loggedIn": true}',
        )

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("pathlib.Path.exists", return_value=False),
        ):
            result = _get_subscription_type()

        assert result is None


class TestMigrationV8:
    """Migration v7 → v8: Rename commands→skills and default all to opus."""

    def test_commands_renamed_to_skills(self, tmp_path: Path) -> None:
        """The 'commands' config key is renamed to 'skills'."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {"spec": "opus", "spec-plan": "opus"},
                    "_configVersion": 7,
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert "skills" in migrated
        assert "commands" not in migrated
        assert migrated["skills"]["spec"] == "opus"

    def test_sonnet_defaults_migrated_to_opus(self, tmp_path: Path) -> None:
        """spec, spec-implement, and spec-verify are migrated from sonnet to opus."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {
                        "spec": "sonnet",
                        "spec-plan": "opus",
                        "spec-implement": "sonnet",
                        "spec-verify": "sonnet",
                    },
                    "_configVersion": 7,
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        assert migrated["skills"]["spec"] == "opus"
        assert migrated["skills"]["spec-plan"] == "opus"
        assert migrated["skills"]["spec-implement"] == "opus"
        assert migrated["skills"]["spec-verify"] == "opus"

    def test_user_opus_choices_preserved(self, tmp_path: Path) -> None:
        """Skills already set to opus are not changed."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "commands": {"spec": "opus", "spec-implement": "opus"},
                    "_configVersion": 7,
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        assert migrated["skills"]["spec"] == "opus"
        assert migrated["skills"]["spec-implement"] == "opus"

    def test_extended_context_ensured(self, tmp_path: Path) -> None:
        """extendedContext is set to true."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "extendedContext": False,
                    "_configVersion": 7,
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        assert migrated["extendedContext"] is True

    def test_skills_key_not_overwritten_by_commands(self, tmp_path: Path) -> None:
        """If both 'skills' and 'commands' exist, 'skills' is kept."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "skills": {"spec": "opus"},
                    "commands": {"spec": "sonnet"},
                    "_configVersion": 7,
                }
            )
        )

        migrate_model_config(config_path)

        migrated = json.loads(config_path.read_text())
        assert migrated["skills"]["spec"] == "opus"


class TestMigrationV9:
    """Migration v8 → v9: Set spec-implement/spec-verify to sonnet for non-Max users."""

    def test_sets_sonnet_for_pro_users(self) -> None:
        """Pro users get spec-implement and spec-verify set to sonnet."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec-implement": "opus", "spec-verify": "opus"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            result = _migration_v9(raw)

        assert result is True
        assert raw["skills"]["spec-implement"] == "sonnet"
        assert raw["skills"]["spec-verify"] == "sonnet"

    def test_sets_sonnet_for_team_users(self) -> None:
        """Team users get spec-implement and spec-verify set to sonnet."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec-implement": "opus", "spec-verify": "opus"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="team"):
            result = _migration_v9(raw)

        assert result is True
        assert raw["skills"]["spec-implement"] == "sonnet"
        assert raw["skills"]["spec-verify"] == "sonnet"

    def test_sets_sonnet_for_enterprise_users(self) -> None:
        """Enterprise users get spec-implement and spec-verify set to sonnet."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec-implement": "opus", "spec-verify": "opus"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="enterprise"):
            result = _migration_v9(raw)

        assert result is True
        assert raw["skills"]["spec-implement"] == "sonnet"
        assert raw["skills"]["spec-verify"] == "sonnet"

    def test_sets_sonnet_for_api_users(self) -> None:
        """API-only users get spec-implement and spec-verify set to sonnet."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec-implement": "opus", "spec-verify": "opus"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="api"):
            result = _migration_v9(raw)

        assert result is True
        assert raw["skills"]["spec-implement"] == "sonnet"
        assert raw["skills"]["spec-verify"] == "sonnet"

    def test_preserves_opus_for_max_users(self) -> None:
        """Max users keep spec-implement and spec-verify as opus."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec-implement": "opus", "spec-verify": "opus"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="max"):
            result = _migration_v9(raw)

        assert result is False
        assert raw["skills"]["spec-implement"] == "opus"
        assert raw["skills"]["spec-verify"] == "opus"

    def test_no_change_when_detection_fails(self) -> None:
        """When subscription can't be detected, leave settings unchanged."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec-implement": "opus", "spec-verify": "opus"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value=None):
            result = _migration_v9(raw)

        assert result is False
        assert raw["skills"]["spec-implement"] == "opus"
        assert raw["skills"]["spec-verify"] == "opus"

    def test_creates_skills_dict_when_missing(self) -> None:
        """Creates skills dict with sonnet values for non-Max users when skills key absent."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {"model": "opus"}

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            result = _migration_v9(raw)

        assert result is True
        assert raw["skills"]["spec-implement"] == "sonnet"
        assert raw["skills"]["spec-verify"] == "sonnet"

    def test_already_sonnet_not_modified(self) -> None:
        """Skills already set to sonnet are not re-modified."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec-implement": "sonnet", "spec-verify": "sonnet"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            result = _migration_v9(raw)

        assert result is False

    def test_handles_missing_skill_keys_in_existing_dict(self) -> None:
        """Skill keys absent from existing skills dict are treated as opus (migrated)."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec": "opus", "spec-plan": "opus"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            result = _migration_v9(raw)

        assert result is True
        assert raw["skills"]["spec-implement"] == "sonnet"
        assert raw["skills"]["spec-verify"] == "sonnet"
        # Other skills unchanged
        assert raw["skills"]["spec"] == "opus"

    def test_full_migration_for_pro_user(self, tmp_path: Path) -> None:
        """Full migrate_model_config from v8 sets sonnet for pro user."""
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION, migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "skills": {
                        "spec": "opus",
                        "spec-plan": "opus",
                        "spec-implement": "opus",
                        "spec-verify": "opus",
                    },
                    "_configVersion": 8,
                }
            )
        )

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["skills"]["spec-implement"] == "sonnet"
        assert migrated["skills"]["spec-verify"] == "sonnet"
        # Other skills unchanged
        assert migrated["skills"]["spec"] == "opus"
        assert migrated["skills"]["spec-plan"] == "opus"
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION

    def test_full_migration_for_max_user_preserves_opus(self, tmp_path: Path) -> None:
        """Full migrate_model_config from v8 preserves opus for max user."""
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION, migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "skills": {
                        "spec": "opus",
                        "spec-plan": "opus",
                        "spec-implement": "opus",
                        "spec-verify": "opus",
                    },
                    "_configVersion": 8,
                }
            )
        )

        with patch("installer.steps.config_migration._get_subscription_type", return_value="max"):
            result = migrate_model_config(config_path)

        assert result is True  # Version bump still counts as modified
        migrated = json.loads(config_path.read_text())
        assert migrated["skills"]["spec-implement"] == "opus"
        assert migrated["skills"]["spec-verify"] == "opus"
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION

    def test_no_spec_bugfix_verify_key_added(self) -> None:
        """Migration does not add spec-bugfix-verify key (alias handles it)."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec-implement": "opus", "spec-verify": "opus"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            _migration_v9(raw)

        assert "spec-bugfix-verify" not in raw["skills"]
