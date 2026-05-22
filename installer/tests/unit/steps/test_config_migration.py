"""Tests for one-time model config migrations."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestMigrationV1:
    """Migration v0 → v1: Update model routing from v7.0 to v7.1."""

    def test_v1_unit_spec_verify_opus_to_sonnet(self) -> None:
        """v1 migrates commands.spec-verify from opus to sonnet (in-memory raw dict)."""
        from installer.steps.config_migration import _migration_v1

        raw: dict = {"commands": {"spec-verify": "opus", "spec-plan": "opus"}}
        _migration_v1(raw)
        assert raw["commands"]["spec-verify"] == "sonnet"
        assert raw["commands"]["spec-plan"] == "opus"

    def test_v1_unit_spec_verify_sonnet_stays_sonnet(self) -> None:
        """v1 leaves spec-verify=sonnet alone (v8 later handles the sonnet→opus default)."""
        from installer.steps.config_migration import _migration_v1

        raw: dict = {"commands": {"spec-verify": "sonnet"}}
        _migration_v1(raw)
        assert raw["commands"]["spec-verify"] == "sonnet"

    def test_v1_unit_stale_agent_keys_removed(self) -> None:
        """Old agent keys from v7.0 are removed and plan-reviewer/spec-reviewer added."""
        from installer.steps.config_migration import _migration_v1

        raw: dict = {
            "agents": {
                "plan-challenger": "sonnet",
                "plan-verifier": "sonnet",
                "spec-reviewer-compliance": "sonnet",
                "spec-reviewer-quality": "opus",
                "spec-reviewer-goal": "sonnet",
            },
        }
        _migration_v1(raw)
        agents = raw["agents"]
        assert "plan-challenger" not in agents
        assert "plan-verifier" not in agents
        assert "spec-reviewer-compliance" not in agents
        assert "spec-reviewer-quality" not in agents
        assert "spec-reviewer-goal" not in agents
        assert agents["plan-reviewer"] == "sonnet"
        assert agents["spec-reviewer"] == "sonnet"

    def test_v1_unit_new_agent_keys_added_if_missing(self) -> None:
        """New plan-reviewer/spec-reviewer agent keys are added when they don't exist."""
        from installer.steps.config_migration import _migration_v1

        raw: dict = {
            "agents": {"plan-challenger": "sonnet", "plan-verifier": "sonnet"},
        }
        _migration_v1(raw)
        assert raw["agents"]["plan-reviewer"] == "sonnet"
        assert raw["agents"]["spec-reviewer"] == "sonnet"

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

    def test_v2_unit_sync_and_learn_migrated_to_opus(self) -> None:
        """Both sync and learn skills are migrated from sonnet to opus."""
        from installer.steps.config_migration import _migration_v2

        raw: dict = {"commands": {"sync": "sonnet", "learn": "sonnet"}}
        _migration_v2(raw)
        assert raw["commands"]["sync"] == "opus"
        assert raw["commands"]["learn"] == "opus"

    def test_v2_unit_already_opus_not_changed(self) -> None:
        """Skills already set to opus are left alone."""
        from installer.steps.config_migration import _migration_v2

        raw: dict = {"commands": {"sync": "opus", "learn": "opus"}}
        result = _migration_v2(raw)
        assert result is False
        assert raw["commands"]["sync"] == "opus"
        assert raw["commands"]["learn"] == "opus"

    def test_v2_unit_partial_migration(self) -> None:
        """Only sonnet values are migrated; opus values are untouched."""
        from installer.steps.config_migration import _migration_v2

        raw: dict = {"commands": {"sync": "opus", "learn": "sonnet"}}
        _migration_v2(raw)
        assert raw["commands"]["sync"] == "opus"
        assert raw["commands"]["learn"] == "opus"


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
        """Default behavior (create_if_missing=False) skips when config file is absent.

        Tests use this default so they don't trigger subprocess calls or write
        the user's real ~/.pilot/config.json as a side effect.
        """
        from installer.steps.config_migration import migrate_model_config

        result = migrate_model_config(tmp_path / "nonexistent.json")

        assert result is False

    def test_creates_subscription_aware_config_on_fresh_install(self, tmp_path: Path) -> None:
        """create_if_missing=True (used by installer) triggers fresh-install defaults.

        Regression: previously the installer skipped migrations entirely when no
        config file existed, leaving fresh Max installs to fall through to
        DEFAULT_MODEL_CONFIG's sonnet default for spec-implement/spec-verify —
        which doesn't work on Max plan because Max does not include sonnet 1M.
        """
        from installer.steps.config_migration import (
            CURRENT_CONFIG_VERSION,
            migrate_model_config,
        )

        config_path = tmp_path / "nonexistent.json"
        with patch("installer.steps.config_migration._get_subscription_type", return_value="max"):
            result = migrate_model_config(config_path, create_if_missing=True)

        assert result is True
        assert config_path.exists()
        written = json.loads(config_path.read_text())
        assert written.get("_configVersion") == CURRENT_CONFIG_VERSION

    def test_fresh_install_unknown_subscription_still_writes(self, tmp_path: Path) -> None:
        """When subscription can't be detected, fresh install still writes a versioned config."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "nonexistent.json"
        with patch("installer.steps.config_migration._get_subscription_type", return_value=None):
            result = migrate_model_config(config_path, create_if_missing=True)

        assert result is True
        assert config_path.exists()

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
        """Non-model keys like auto_update survive the full migration chain through v12,
        while v12-pruned keys (model, agents, commands/skills, extendedContext) are removed."""
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
        assert migrated["auto_update"] is True
        # v12 pruned the legacy model-routing keys
        assert "model" not in migrated
        assert "extendedContext" not in migrated
        assert "skills" not in migrated
        assert "agents" not in migrated

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
        # v3 disables worktree, v4 re-enables reviewers but NOT worktree, v7 renames, v11 renames to branchIsolation
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True
        # v4 no longer forces worktree back to True — respects whatever v3 set; v11 renamed worktreeSupport → branchIsolation
        assert migrated["specWorkflow"]["branchIsolation"] is False
        assert "worktreeSupport" not in migrated["specWorkflow"]
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
        """askQuestionsDuringPlanning and planApproval are preserved through v3+v4.

        Note: worktreeSupport is intentionally omitted from this input so v11 is
        a no-op for this test. The original intent is preserved — earlier-version
        migrations must not clobber unrelated keys.
        """
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": True, "specReviewer": True},
                    "specWorkflow": {
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
        # v4 enables reviewers, then v7 renames keys, v11 renames worktreeSupport → branchIsolation
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True
        # v4 no longer forces worktree — user's False is preserved; v11 renamed key
        assert migrated["specWorkflow"]["branchIsolation"] is False
        assert "worktreeSupport" not in migrated["specWorkflow"]
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
        # v7 renames keys, v11 renames worktreeSupport → branchIsolation
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True
        assert migrated["specWorkflow"]["branchIsolation"] is True
        assert "worktreeSupport" not in migrated["specWorkflow"]

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
        # v4 enables both, then v7 renames, v11 renames worktreeSupport → branchIsolation
        assert migrated["reviewerAgents"]["specReview"] is True
        assert migrated["reviewerAgents"]["changesReview"] is True
        assert migrated["specWorkflow"]["branchIsolation"] is True
        assert "worktreeSupport" not in migrated["specWorkflow"]

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
        # v11 renamed worktreeSupport → branchIsolation
        assert migrated["specWorkflow"]["branchIsolation"] is False
        assert "worktreeSupport" not in migrated["specWorkflow"]
        assert migrated["specWorkflow"]["askQuestionsDuringPlanning"] is True
        assert migrated["specWorkflow"]["planApproval"] is True

    def test_preserves_other_spec_workflow_toggles(self, tmp_path: Path) -> None:
        """askQuestionsDuringPlanning and planApproval are preserved.

        Note: worktreeSupport is intentionally omitted from this input so v11 is
        a no-op for this test. The original intent is preserved — v4's migration
        must not clobber unrelated keys.
        """
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "model": "opus",
                    "reviewerAgents": {"planReviewer": False, "specReviewer": False},
                    "specWorkflow": {
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

    def test_full_chain_from_v4_lands_at_current_version_with_v12_post_state(self, tmp_path: Path) -> None:
        """End-to-end chain from v4 through v12: legacy model/extendedContext keys are pruned."""
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION, migrate_model_config

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
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION
        # v12 prunes the legacy model + extendedContext keys
        assert "model" not in migrated
        assert "extendedContext" not in migrated

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

    def test_v8_unit_commands_renamed_to_skills(self) -> None:
        """The 'commands' config key is renamed to 'skills' (direct call to _migration_v8)."""
        from installer.steps.config_migration import _migration_v8

        raw: dict = {"model": "opus", "commands": {"spec": "opus", "spec-plan": "opus"}}
        result = _migration_v8(raw)

        assert result is True
        assert "skills" in raw
        assert "commands" not in raw
        assert raw["skills"]["spec"] == "opus"

    def test_v8_unit_sonnet_defaults_migrated_to_opus(self) -> None:
        """spec, spec-implement, and spec-verify are migrated from sonnet to opus."""
        from installer.steps.config_migration import _migration_v8

        raw: dict = {
            "model": "opus",
            "commands": {
                "spec": "sonnet",
                "spec-plan": "opus",
                "spec-implement": "sonnet",
                "spec-verify": "sonnet",
            },
        }
        _migration_v8(raw)

        assert raw["skills"]["spec"] == "opus"
        assert raw["skills"]["spec-plan"] == "opus"
        assert raw["skills"]["spec-implement"] == "opus"
        assert raw["skills"]["spec-verify"] == "opus"

    def test_v8_unit_user_opus_choices_preserved(self) -> None:
        """Skills already set to opus are not changed."""
        from installer.steps.config_migration import _migration_v8

        raw: dict = {"model": "opus", "commands": {"spec": "opus", "spec-implement": "opus"}}
        _migration_v8(raw)

        assert raw["skills"]["spec"] == "opus"
        assert raw["skills"]["spec-implement"] == "opus"

    def test_v8_unit_extended_context_ensured(self) -> None:
        """extendedContext is set to true by v8 (before v12 prunes it)."""
        from installer.steps.config_migration import _migration_v8

        raw: dict = {"model": "opus", "extendedContext": False}
        _migration_v8(raw)

        assert raw["extendedContext"] is True

    def test_v8_unit_skills_key_not_overwritten_by_commands(self) -> None:
        """If both 'skills' and 'commands' exist, 'skills' is kept."""
        from installer.steps.config_migration import _migration_v8

        raw: dict = {"model": "opus", "skills": {"spec": "opus"}, "commands": {"spec": "sonnet"}}
        _migration_v8(raw)

        assert raw["skills"]["spec"] == "opus"


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

    def test_full_migration_for_pro_user_runs_through_to_v12(self, tmp_path: Path) -> None:
        """Full migrate_model_config from v8 runs v9 (sonnet for pro) then v12 (prune model keys).
        The v9 effect is captured in the .bak.v11 backup; the on-disk config has the keys pruned."""
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
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION
        # v12 pruned the legacy model + skills keys
        assert "model" not in migrated
        assert "skills" not in migrated
        # The pre-v12 backup captured the v8 input verbatim
        bak_path = config_path.with_suffix(".json.bak.v11")
        assert bak_path.exists()
        backup = json.loads(bak_path.read_text())
        assert backup["skills"]["spec-implement"] == "opus"  # v9 hasn't run on the backup

    def test_full_migration_for_max_user_runs_through_to_v12(self, tmp_path: Path) -> None:
        """Full migrate_model_config from v8 for max user runs the chain through v12.
        v9 leaves opus intact, v12 then prunes the keys; backup captures the v9 post-state."""
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

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION
        # v12 pruned the keys outright
        assert "model" not in migrated
        assert "skills" not in migrated
        # Backup preserves the v8 input
        bak_path = config_path.with_suffix(".json.bak.v11")
        backup = json.loads(bak_path.read_text())
        assert backup["skills"]["spec-implement"] == "opus"

    def test_no_spec_bugfix_verify_key_added(self) -> None:
        """Migration does not add spec-bugfix-verify key (alias handles it)."""
        from installer.steps.config_migration import _migration_v9

        raw: dict = {
            "skills": {"spec-implement": "opus", "spec-verify": "opus"},
        }

        with patch("installer.steps.config_migration._get_subscription_type", return_value="pro"):
            _migration_v9(raw)

        assert "spec-bugfix-verify" not in raw["skills"]


class TestMigrationV10:
    """Migration v9 → v10: Issue #139 — strip alias [1m] from disk; preserve explicit-id [1m]."""

    def test_current_version_is_at_least_10(self) -> None:
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION

        assert CURRENT_CONFIG_VERSION >= 10

    def test_strips_alias_1m_from_main_model(self) -> None:
        from installer.steps.config_migration import _migration_v10

        raw: dict = {"model": "opus[1m]"}
        modified = _migration_v10(raw)

        assert modified is True
        assert raw["model"] == "opus"

    def test_strips_alias_1m_from_skills(self) -> None:
        from installer.steps.config_migration import _migration_v10

        raw: dict = {
            "skills": {
                "spec-plan": "sonnet[1m]",
                "spec-implement": "opus[1m]",
                "spec-verify": "sonnet",
            }
        }
        modified = _migration_v10(raw)

        assert modified is True
        assert raw["skills"]["spec-plan"] == "sonnet"
        assert raw["skills"]["spec-implement"] == "opus"
        assert raw["skills"]["spec-verify"] == "sonnet"

    def test_preserves_explicit_id_1m_in_main_model(self) -> None:
        """Issue #139: <explicit-id>[1m] (e.g. claude-opus-4-7[1m]) preserved verbatim."""
        from installer.steps.config_migration import _migration_v10

        raw: dict = {"model": "claude-opus-4-7[1m]"}
        modified = _migration_v10(raw)

        assert modified is False
        assert raw["model"] == "claude-opus-4-7[1m]"

    def test_preserves_explicit_id_1m_in_skills(self) -> None:
        from installer.steps.config_migration import _migration_v10

        raw: dict = {"skills": {"spec-plan": "claude-opus-4-7[1m]"}}
        modified = _migration_v10(raw)

        assert modified is False
        assert raw["skills"]["spec-plan"] == "claude-opus-4-7[1m]"

    def test_does_not_touch_agents(self) -> None:
        """Issue #139: agents are out of scope; migration leaves any [1m] alone."""
        from installer.steps.config_migration import _migration_v10

        raw: dict = {"agents": {"spec-review": "sonnet[1m]"}}
        modified = _migration_v10(raw)

        assert modified is False
        assert raw["agents"]["spec-review"] == "sonnet[1m]"

    def test_noop_when_no_1m_anywhere(self) -> None:
        from installer.steps.config_migration import _migration_v10

        raw: dict = {"model": "opus", "skills": {"spec-plan": "sonnet"}}
        modified = _migration_v10(raw)

        assert modified is False

    def test_full_migration_strips_legacy_1m_runs_through_to_v12(self, tmp_path: Path) -> None:
        """End-to-end: a v9 config with legacy alias [1m] runs through v10 (strip [1m])
        and v12 (prune dead model keys) — final state has no model/skills keys."""
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION, migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "_configVersion": 9,
                    "model": "opus[1m]",
                    "skills": {"spec-plan": "sonnet[1m]"},
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["_configVersion"] == CURRENT_CONFIG_VERSION
        # v12 pruned the dead keys outright
        assert "model" not in migrated
        assert "skills" not in migrated
        assert migrated["specWorkflow"]["modelSwitch"] is True
        # v12 also wrote a backup with the pre-migration state
        bak_path = config_path.with_suffix(".json.bak.v11")
        assert bak_path.exists()
        backup = json.loads(bak_path.read_text())
        assert backup["model"] == "opus[1m]"
        assert backup["skills"]["spec-plan"] == "sonnet[1m]"

    def test_v10_idempotent(self, tmp_path: Path) -> None:
        """Re-running migrate on a fully-migrated config is a no-op.

        After v11, a config at version 10 with no legacy `worktreeSupport` key
        and no `branchIsolation` change still gets bumped to v11 — but only
        because the version sentinel is stale, not because the data needs
        rewriting. To keep the test's "data unchanged" intent, mark the input
        as already at CURRENT_CONFIG_VERSION.
        """
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION, migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps({"_configVersion": CURRENT_CONFIG_VERSION, "model": "opus", "skills": {"spec-plan": "sonnet"}})
        )

        result = migrate_model_config(config_path)
        assert result is False


class TestMigrationV11:
    """Migration v10 → v11: Rename specWorkflow.worktreeSupport → branchIsolation."""

    def test_current_version_is_at_least_11(self) -> None:
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION

        assert CURRENT_CONFIG_VERSION >= 11

    def test_v11_migrates_worktree_support_true(self) -> None:
        from installer.steps.config_migration import _migration_v11

        raw: dict = {"specWorkflow": {"worktreeSupport": True, "askQuestionsDuringPlanning": True}}
        modified = _migration_v11(raw)

        assert modified is True
        assert raw["specWorkflow"]["branchIsolation"] is True
        assert "worktreeSupport" not in raw["specWorkflow"]

    def test_v11_migrates_worktree_support_false(self) -> None:
        from installer.steps.config_migration import _migration_v11

        raw: dict = {"specWorkflow": {"worktreeSupport": False, "askQuestionsDuringPlanning": True}}
        modified = _migration_v11(raw)

        assert modified is True
        assert raw["specWorkflow"]["branchIsolation"] is False
        assert "worktreeSupport" not in raw["specWorkflow"]

    def test_v11_no_op_when_no_spec_workflow(self) -> None:
        from installer.steps.config_migration import _migration_v11

        raw: dict = {"model": "opus"}
        modified = _migration_v11(raw)

        assert modified is False
        assert "specWorkflow" not in raw

    def test_v11_no_op_when_no_worktree_support_key(self) -> None:
        from installer.steps.config_migration import _migration_v11

        raw: dict = {"specWorkflow": {"askQuestionsDuringPlanning": True, "planApproval": True}}
        modified = _migration_v11(raw)

        assert modified is False
        assert "branchIsolation" not in raw["specWorkflow"]

    def test_v11_unchanged_when_already_v11_and_no_legacy_keys(self) -> None:
        """A config at v11 with no legacy worktreeSupport gets no changes from _migration_v11."""
        from installer.steps.config_migration import _migration_v11

        raw: dict = {"specWorkflow": {"branchIsolation": True}}
        result = _migration_v11(raw)
        assert result is False
        assert raw["specWorkflow"]["branchIsolation"] is True

    def test_v11_preserves_other_spec_workflow_keys(self) -> None:
        from installer.steps.config_migration import _migration_v11

        raw: dict = {
            "specWorkflow": {
                "worktreeSupport": True,
                "askQuestionsDuringPlanning": False,
                "planApproval": False,
            }
        }
        modified = _migration_v11(raw)

        assert modified is True
        assert raw["specWorkflow"]["branchIsolation"] is True
        assert raw["specWorkflow"]["askQuestionsDuringPlanning"] is False
        assert raw["specWorkflow"]["planApproval"] is False

    def test_v11_both_keys_present_branchIsolation_wins(self) -> None:
        """If branchIsolation is already set, keep it — clean up legacy key only."""
        from installer.steps.config_migration import _migration_v11

        raw: dict = {
            "specWorkflow": {
                "worktreeSupport": True,
                "branchIsolation": False,
                "askQuestionsDuringPlanning": True,
            }
        }
        modified = _migration_v11(raw)

        assert modified is True
        # branchIsolation preserved at user's explicit value
        assert raw["specWorkflow"]["branchIsolation"] is False
        # legacy key cleaned up
        assert "worktreeSupport" not in raw["specWorkflow"]

    def test_v11_non_bool_worktree_support_defaults_to_false(self) -> None:
        """Non-bool legacy values fall back to False (safe default)."""
        from installer.steps.config_migration import _migration_v11

        raw: dict = {"specWorkflow": {"worktreeSupport": "yes"}}
        modified = _migration_v11(raw)

        assert modified is True
        assert raw["specWorkflow"]["branchIsolation"] is False
        assert "worktreeSupport" not in raw["specWorkflow"]

    def test_full_migration_renames_worktree_support_and_bumps_version(self, tmp_path: Path) -> None:
        """End-to-end: a v10 config with worktreeSupport reaches v11 with branchIsolation."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "_configVersion": 10,
                    "specWorkflow": {
                        "worktreeSupport": True,
                        "askQuestionsDuringPlanning": True,
                        "planApproval": True,
                    },
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["specWorkflow"]["branchIsolation"] is True
        assert "worktreeSupport" not in migrated["specWorkflow"]
        assert migrated["specWorkflow"]["askQuestionsDuringPlanning"] is True
        assert migrated["specWorkflow"]["planApproval"] is True


class TestMigrationV12:
    """Migration v11 → v12: Strip dead model keys, seed specWorkflow.modelSwitch, write .bak.v11 once."""

    def test_current_version_is_12(self) -> None:
        from installer.steps.config_migration import CURRENT_CONFIG_VERSION

        assert CURRENT_CONFIG_VERSION == 12

    def test_v12_strips_dead_model_keys_and_seeds_model_switch(self, tmp_path: Path) -> None:
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "_configVersion": 11,
                    "model": "opus",
                    "skills": {"spec-plan": "opus", "spec-implement": "sonnet"},
                    "agents": {"spec-review": "sonnet"},
                    "extendedContext": True,
                    "extendedContextOverrides": {"main": True},
                    "specWorkflow": {
                        "branchIsolation": True,
                        "askQuestionsDuringPlanning": True,
                        "planApproval": True,
                    },
                    "reviewerAgents": {"specReview": True, "changesReview": True},
                }
            )
        )

        result = migrate_model_config(config_path)

        assert result is True
        migrated = json.loads(config_path.read_text())
        assert migrated["_configVersion"] == 12
        for dead in ("model", "skills", "agents", "extendedContext", "extendedContextOverrides"):
            assert dead not in migrated, f"{dead} should have been pruned"
        assert migrated["specWorkflow"]["modelSwitch"] is True
        assert migrated["specWorkflow"]["branchIsolation"] is True
        assert migrated["reviewerAgents"]["specReview"] is True

    def test_v12_writes_bak_v11_with_pre_migration_content(self, tmp_path: Path) -> None:
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        pre_migration_payload = {
            "_configVersion": 11,
            "model": "opus",
            "skills": {"spec-plan": "opus"},
        }
        config_path.write_text(json.dumps(pre_migration_payload))

        migrate_model_config(config_path)

        bak_path = config_path.with_suffix(".json.bak.v11")
        assert bak_path.exists()
        backup = json.loads(bak_path.read_text())
        assert backup == pre_migration_payload

    def test_v12_bak_not_overwritten_on_second_run(self, tmp_path: Path) -> None:
        """Idempotency: backup holds genuine v11 snapshot even after re-runs."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        original = {"_configVersion": 11, "model": "opus", "skills": {"spec-plan": "opus"}}
        config_path.write_text(json.dumps(original))

        migrate_model_config(config_path)
        first_backup = (config_path.with_suffix(".json.bak.v11")).read_text()

        # Re-run; config is already v12, but explicitly invoke again
        migrate_model_config(config_path)
        second_backup = (config_path.with_suffix(".json.bak.v11")).read_text()

        assert first_backup == second_backup
        assert json.loads(first_backup) == original

    def test_v12_idempotent_when_already_v12(self, tmp_path: Path) -> None:
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "_configVersion": 12,
                    "specWorkflow": {"modelSwitch": True, "branchIsolation": True},
                }
            )
        )

        result = migrate_model_config(config_path)
        assert result is False

    def test_v12_seeds_model_switch_when_specworkflow_missing(self, tmp_path: Path) -> None:
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({"_configVersion": 11}))

        migrate_model_config(config_path)
        migrated = json.loads(config_path.read_text())
        assert migrated["specWorkflow"]["modelSwitch"] is True

    def test_v12_preserves_user_model_switch_false(self, tmp_path: Path) -> None:
        """If user already set modelSwitch=false explicitly, do not overwrite to true."""
        from installer.steps.config_migration import migrate_model_config

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "_configVersion": 11,
                    "specWorkflow": {"modelSwitch": False, "branchIsolation": True},
                }
            )
        )

        migrate_model_config(config_path)
        migrated = json.loads(config_path.read_text())
        assert migrated["specWorkflow"]["modelSwitch"] is False
