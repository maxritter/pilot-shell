"""Names of session-scoped artifacts shared by hook readers and cleanup."""

from __future__ import annotations

PAUSE_SENTINELS = (
    "spec-approval-pending",
    "build-handback-pending",
    "verify-gate-pending",
)

STALE_SESSION_FILES = (
    "active_plan.json",
    "plan-mode-active",
    "bypass-restore-pending",
    "pre-plan-permission-mode",
    "plan-model-warned",
    "plan-model-confirmed",
    "preflight-context-warned",
    "spec-stop-guard",
    *PAUSE_SENTINELS,
    "continuation.md",
    "context-cache.json",
    "context-pct.json",
    "pre-compact-state.json",
)

STALE_SESSION_PATTERNS = (
    "findings-spec-review*.json",
    "findings-changes-review*.json",
    "findings-codex-spec-review*.json",
    "findings-codex-changes-review*.json",
)
