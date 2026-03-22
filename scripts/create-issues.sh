#!/usr/bin/env bash
# create-issues.sh — Batch-create the Security Control Plane GitHub issues
#
# Prerequisites:
#   gh auth login   (GitHub CLI authenticated)
#   GitHub Issues must be enabled on the repository
#
# Usage:
#   ./scripts/create-issues.sh [--dry-run]
#
# Pass --dry-run to print issue titles without creating them.

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# Derive repo from git remote, fall back to default
REPO=$(git remote get-url origin 2>/dev/null \
  | sed -E 's|.*github\.com[:/](.+/.+)(\.git)?$|\1|' \
  || echo "canstralian/pilot-shell-devsecops")

# Pre-flight checks
if ! $DRY_RUN; then
  if ! command -v gh &>/dev/null; then
    echo "Error: 'gh' CLI not found. Install from https://cli.github.com" >&2
    exit 1
  fi
  if ! gh auth status &>/dev/null; then
    echo "Error: Not authenticated. Run 'gh auth login' first." >&2
    exit 1
  fi
fi

FAILURES=0
PIDS=()
TITLES=()

create_issue() {
  local title="$1"
  local body="$2"
  local labels="$3"

  if $DRY_RUN; then
    echo "DRY RUN: $title  [$labels]"
    return
  fi

  TITLES+=("$title")
  (
    if gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels" &>/dev/null; then
      echo "Created: $title"
    else
      echo "FAILED:  $title" >&2
      exit 1
    fi
  ) &
  PIDS+=($!)
}

# ── EPIC: Security Control Plane ────────────────────────────────────────────

create_issue \
  "Introduce Pre-Execution Risk Classification Hook" \
  "## Description
Add a pre-execution hook in the command engine to classify risk before any command runs.

## Why
All enforcement depends on understanding risk before execution. This is the first control boundary.

## Acceptance Criteria
- [ ] Every \`pilot-sec\` run passes through a risk classifier
- [ ] Output includes: \`risk_score\`, \`risk_level\`, \`matched_rules\`
- [ ] No command executes before classification completes" \
  "core,security,engine,critical"

create_issue \
  "Implement Policy Enforcement in Execution Pipeline" \
  "## Description
Add policy evaluation after risk classification and before execution.

## Acceptance Criteria
- [ ] Policy consumes normalized facts (not raw strings)
- [ ] Decision outputs: \`allow | warn | block\`
- [ ] Blocked commands never execute
- [ ] Decision trace is logged" \
  "policy,engine,critical"

create_issue \
  "Add Structured Audit Logging (Pre + Post Execution)" \
  "## Description
Log all execution events with full traceability.

## Acceptance Criteria
- [ ] Pre-execution log (intent)
- [ ] Post-execution log (result)
- [ ] Includes: \`run_id\`, \`session_id\`, \`decision\`, \`risk_score\`
- [ ] Logs stored under \`.pilot-sec/runs/\`" \
  "audit,observability,critical"

# ── EPIC: Scanner + Evidence Normalization ───────────────────────────────────

create_issue \
  "Implement Finding Normalization Schema (finding/v1)" \
  "## Description
All scanner outputs must be normalized into a single schema.

## Acceptance Criteria
- [ ] Define \`finding/v1\` schema
- [ ] Reject malformed findings
- [ ] Normalize severity into: \`low | medium | high | critical\`
- [ ] Include raw reference pointer" \
  "scanners,schema,critical"

create_issue \
  "Build Scanner Provider Abstraction Layer" \
  "## Description
Decouple scanners from specific tools (Semgrep, Checkov, etc.)

## Acceptance Criteria
- [ ] Introduce provider interface: \`run() → normalize()\`
- [ ] Support multiple providers per scanner type
- [ ] No tool-specific logic leaks into core" \
  "scanners,architecture"

create_issue \
  "Add Scan Result Caching" \
  "## Description
Cache scan results to avoid redundant execution.

## Acceptance Criteria
- [ ] Cache keyed by commit hash or lockfile hash
- [ ] Cache invalidates on change
- [ ] CLI flag to bypass cache" \
  "performance,scanners"

# ── EPIC: Policy Engine ──────────────────────────────────────────────────────

create_issue \
  "Implement Policy Rule Engine (Deterministic)" \
  "## Description
Build rule evaluation engine using normalized facts.

## Acceptance Criteria
- [ ] Support operators: \`equals\`, \`in\`, \`gt\`, etc.
- [ ] Support logic: \`all\`, \`any\`, \`none\`
- [ ] Deterministic output" \
  "policy,engine,critical"

create_issue \
  "Add Policy Waiver System" \
  "## Description
Allow scoped, time-bound exceptions to rules.

## Acceptance Criteria
- [ ] Waivers tied to \`rule_id\`
- [ ] Include expiration
- [ ] Applied before final decision
- [ ] Logged in audit trail" \
  "policy,governance"

create_issue \
  "Implement Policy Decision Trace Output" \
  "## Description
Expose why a decision was made.

## Acceptance Criteria
- [ ] Output includes triggered rules
- [ ] Shows evaluated conditions
- [ ] Accessible via \`--explain\`" \
  "policy,debugging"

# ── EPIC: Agent + Skill System ───────────────────────────────────────────────

create_issue \
  "Introduce Shared Skill Contract Layer" \
  "## Description
Define standardized skill input/output schema.

## Acceptance Criteria
- [ ] All skills follow \`contract.yaml\`
- [ ] Enforce schema validation
- [ ] Shared severity + confidence scales" \
  "agents,skills,architecture"

create_issue \
  "Implement diff-analysis Skill" \
  "## Description
Extract security-relevant signals from diffs.

## Acceptance Criteria
- [ ] Identifies changed surfaces (code, infra, CI)
- [ ] Outputs structured findings
- [ ] Used by \`security-reviewer\` agent" \
  "skills,analysis"

create_issue \
  "Enforce Agent Output Validation" \
  "## Description
Ensure all agents produce valid structured JSON.

## Acceptance Criteria
- [ ] Reject invalid output
- [ ] Validate against schema
- [ ] Fail agent execution on malformed output" \
  "agents,reliability"

# ── EPIC: Config System ──────────────────────────────────────────────────────

create_issue \
  "Implement Config Inheritance and Precedence" \
  "## Description
Support layered config resolution.

## Acceptance Criteria
- [ ] Precedence: \`defaults < project < profile < runtime\`
- [ ] Deep merge for objects
- [ ] Explicit array merge rules" \
  "config,architecture,critical"

create_issue \
  "Add Config Schema Validation" \
  "## Description
Validate config before runtime.

## Acceptance Criteria
- [ ] Fail fast on invalid config
- [ ] Provide clear error messages
- [ ] Schema versioning supported" \
  "config,validation"

create_issue \
  "Add Config Resolution Debug Mode" \
  "## Description
Explain final resolved config.

## Acceptance Criteria
- [ ] Show value + source
- [ ] CLI: \`pilot-sec config explain\`
- [ ] Useful for debugging overrides" \
  "config,debugging"

# ── EPIC: Runtime + Sessions ─────────────────────────────────────────────────

create_issue \
  "Implement Session Lifecycle Management" \
  "## Description
Track execution sessions.

## Acceptance Criteria
- [ ] Start / stop sessions
- [ ] Persist session metadata
- [ ] Attach runs to sessions" \
  "sessions,core"

create_issue \
  "Add Runtime Sandbox Enforcement" \
  "## Description
Enforce execution boundaries.

## Acceptance Criteria
- [ ] Control network access
- [ ] Control filesystem writes
- [ ] Block secret reads unless allowed" \
  "security,runtime,critical"

# ── EPIC: DevEx + CI Integration ─────────────────────────────────────────────

create_issue \
  "Implement PR Security Summary Command" \
  "## Description
Summarize security impact for pull requests.

## Acceptance Criteria
- [ ] Shows new findings only
- [ ] Includes severity breakdown
- [ ] Outputs markdown + JSON" \
  "integration,github"

create_issue \
  "Map Policy Decisions to CI Status Checks" \
  "## Description
Integrate with GitHub checks.

## Acceptance Criteria
- [ ] \`allow\` → success
- [ ] \`warn\` → neutral
- [ ] \`block\` → failure" \
  "ci,integration"

# ── META: System Integrity ───────────────────────────────────────────────────

create_issue \
  "Define Unified Fact Model" \
  "## Description
Standardize facts used across scanners, policy, and agents.

## Acceptance Criteria
- [ ] Document fact schema
- [ ] All systems consume same model
- [ ] No direct scanner output in policy layer" \
  "architecture,critical"

create_issue \
  "Implement Deterministic Replay System" \
  "## Description
Enable full reproducibility of runs.

## Acceptance Criteria
- [ ] Replay run from logs
- [ ] Same inputs → same outputs
- [ ] Includes config + context snapshot" \
  "audit,reliability"

# ── Wait for all background jobs ─────────────────────────────────────────────

if ! $DRY_RUN; then
  for pid in "${PIDS[@]}"; do
    wait "$pid" || FAILURES=$((FAILURES + 1))
  done

  echo ""
  echo "Done. $((${#PIDS[@]} - FAILURES))/${#PIDS[@]} issues created successfully."
  [[ $FAILURES -gt 0 ]] && echo "$FAILURES issue(s) failed — check output above." >&2 && exit 1
else
  echo ""
  echo "Done. 21 issues listed (dry run)."
fi
