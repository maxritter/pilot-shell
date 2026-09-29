"""Generated verification skills honor the user's checkpoint setting."""

from pathlib import Path

import pytest

from installer.skill_builder import build_skill_md
from installer.steps.codex_files import build_codex_skill_md

SKILLS_ROOT = Path(__file__).resolve().parents[3] / "pilot" / "skills"


@pytest.mark.parametrize("skill_name", ["spec", "spec-plan", "spec-bugfix-plan"])
@pytest.mark.parametrize("platform", ["claude", "codex"])
def test_generated_handoffs_do_not_require_a_magic_resume_word(skill_name, platform):
    builder = build_skill_md if platform == "claude" else build_codex_skill_md
    artifact = builder(SKILLS_ROOT / skill_name)
    assert "Any other message leaves the gate armed" not in artifact
    assert "Exact `resume`, `/spec resume`" not in artifact


@pytest.mark.parametrize("skill_name", ["spec-verify", "spec-bugfix-verify"])
@pytest.mark.parametrize("platform", ["claude", "codex"])
def test_generated_verification_uses_opt_in_progress_based_checkpoints(skill_name: str, platform: str) -> None:
    """Check the runtime artifact, including every embedded failure-routing step."""
    builder = build_skill_md if platform == "claude" else build_codex_skill_md
    artifact = builder(SKILLS_ROOT / skill_name)
    failure_flow = artifact.split("### Failed verification: diagnose and continue", 1)[1]

    # A saved setting is re-read at the decision point and strict true is opt-in.
    assert "read `~/.pilot/config.json` fresh with the current runtime's native file-reading tool" in failure_flow
    assert "Only JSON boolean `true` at `specWorkflow.runawayGuard`" in failure_flow
    assert (
        "Missing, unreadable, or malformed config, a missing key, or a non-boolean value means **off**" in failure_flow
    )
    assert "`Iterations:` records loop history; it never imposes an attempt cap" in failure_flow

    default_flow = failure_flow.split("- **Default (off):**", 1)[1].split("- **Enabled:**", 1)[0]
    assert "next evidence-backed fix within the authorized scope, and continue automatically" in default_flow
    assert (
        "Record the current unresolved evidence and progress in the plan for comparison with the next evaluation"
        in default_flow
    )
    assert "repeated output, cosmetic edits, and restated plans are not progress" in default_flow
    enabled_flow = failure_flow.split("- **Enabled:**", 1)[1].split("- **Running jobs:**", 1)[0]
    assert (
        "only when repeated failed verification has the same unresolved evidence and no meaningful progress"
        in enabled_flow
    )
    assert "Continue while diagnosis or fixes make progress, regardless of the iteration count" in enabled_flow
    assert "Elapsed time or a polling timeout alone never triggers a checkpoint" in failure_flow

    # Genuine missing input remains pending once; the answer itself resumes work.
    assert "true blocker or material scope choice" in failure_flow
    assert (
        "Ask once about the concrete blocker or choice and keep that decision pending across turns and compaction"
        in failure_flow
    )
    assert 'plan-state pause --kind decision --message "<concrete question>" $LANE_FLAG' in failure_flow
    assert "run `pilot plan-state resume $LANE_FLAG` and continue immediately" in failure_flow
    assert "without another confirmation or a standalone resume request" in failure_flow

    # All old cross references must disappear from the bundled runtime artifact.
    for retired_gate in (
        "iteration-cap",
        "Iteration cap",
        "Iterations >= 3",
        "Iterations < 3",
        "if `>= 3`",
        "Three verify iterations have failed",
        "Three fix iterations have failed",
        "Continue / Pivot / Abandon",
        "Continue/Pivot/Abandon",
        "rarely the right answer",
        "FAIL after 2 attempts",
        "Max 2 iterations",
    ):
        assert retired_gate not in artifact, retired_gate

    # Removing routine checkpoints must retain sign-off of the concrete result.
    assert "### Approval and evidence precondition" in artifact
    assert (
        "explicitly approved that result after it was presented, or supplied applicable standing authorization"
        in artifact
    )
    assert "Do not repeatedly ask for the same pending answer" in artifact
    assert "Status: PENDING" in failure_flow
    if platform == "codex":
        assert "`$spec-implement` skill instructions" in failure_flow
    else:
        assert "Skill(skill='spec-implement', args='<plan-path> $LANE_FLAG')" in failure_flow
