# Security Control Plane — GitHub Issues

This document tracks the 21 planned GitHub issues for the Security Control Plane epic.
Use `scripts/create-issues.sh` to bulk-create them once GitHub Issues is enabled on this repository.

---

## EPIC: Establish Security Control Plane 🔴

### Issue 1 — Introduce Pre-Execution Risk Classification Hook
**Type:** Feature | **Priority:** Critical | **Labels:** `core` `security` `engine` `critical`

**Description:**
Add a pre-execution hook in the command engine to classify risk before any command runs.

**Why:** All enforcement depends on understanding risk before execution. This is the first control boundary.

**Acceptance Criteria:**
- Every `pilot-sec` run passes through a risk classifier
- Output includes: `risk_score`, `risk_level`, `matched_rules`
- No command executes before classification completes

---

### Issue 2 — Implement Policy Enforcement in Execution Pipeline
**Type:** Feature | **Priority:** Critical | **Labels:** `policy` `engine` `critical`

**Description:**
Add policy evaluation after risk classification and before execution.

**Acceptance Criteria:**
- Policy consumes normalized facts (not raw strings)
- Decision outputs: `allow | warn | block`
- Blocked commands never execute
- Decision trace is logged

---

### Issue 3 — Add Structured Audit Logging (Pre + Post Execution)
**Type:** Feature | **Priority:** Critical | **Labels:** `audit` `observability` `critical`

**Description:**
Log all execution events with full traceability.

**Acceptance Criteria:**
- Pre-execution log (intent)
- Post-execution log (result)
- Includes: `run_id`, `session_id`, `decision`, `risk_score`
- Logs stored under `.pilot-sec/runs/`

---

## EPIC: Scanner + Evidence Normalization 🟠

### Issue 4 — Implement Finding Normalization Schema (finding/v1)
**Type:** Feature | **Priority:** Critical | **Labels:** `scanners` `schema` `critical`

**Description:**
All scanner outputs must be normalized into a single schema.

**Acceptance Criteria:**
- Define `finding/v1` schema
- Reject malformed findings
- Normalize severity into: `low | medium | high | critical`
- Include raw reference pointer

---

### Issue 5 — Build Scanner Provider Abstraction Layer
**Type:** Refactor | **Priority:** High | **Labels:** `scanners` `architecture`

**Description:**
Decouple scanners from specific tools (Semgrep, Checkov, etc.)

**Acceptance Criteria:**
- Introduce provider interface: `run() → normalize()`
- Support multiple providers per scanner type
- No tool-specific logic leaks into core

---

### Issue 6 — Add Scan Result Caching
**Type:** Feature | **Priority:** Medium | **Labels:** `performance` `scanners`

**Description:**
Cache scan results to avoid redundant execution.

**Acceptance Criteria:**
- Cache keyed by commit hash or lockfile hash
- Cache invalidates on change
- CLI flag to bypass cache

---

## EPIC: Policy Engine 🟡

### Issue 7 — Implement Policy Rule Engine (Deterministic)
**Type:** Feature | **Priority:** Critical | **Labels:** `policy` `engine` `critical`

**Description:**
Build rule evaluation engine using normalized facts.

**Acceptance Criteria:**
- Support operators: `equals`, `in`, `gt`, etc.
- Support logic: `all`, `any`, `none`
- Deterministic output

---

### Issue 8 — Add Policy Waiver System
**Type:** Feature | **Priority:** High | **Labels:** `policy` `governance`

**Description:**
Allow scoped, time-bound exceptions to rules.

**Acceptance Criteria:**
- Waivers tied to `rule_id`
- Include expiration
- Applied before final decision
- Logged in audit trail

---

### Issue 9 — Implement Policy Decision Trace Output
**Type:** Feature | **Priority:** High | **Labels:** `policy` `debugging`

**Description:**
Expose why a decision was made.

**Acceptance Criteria:**
- Output includes triggered rules
- Shows evaluated conditions
- Accessible via `--explain`

---

## EPIC: Agent + Skill System 🟢

### Issue 10 — Introduce Shared Skill Contract Layer
**Type:** Feature | **Priority:** Critical | **Labels:** `agents` `skills` `architecture`

**Description:**
Define standardized skill input/output schema.

**Acceptance Criteria:**
- All skills follow `contract.yaml`
- Enforce schema validation
- Shared severity + confidence scales

---

### Issue 11 — Implement diff-analysis Skill
**Type:** Feature | **Priority:** High | **Labels:** `skills` `analysis`

**Description:**
Extract security-relevant signals from diffs.

**Acceptance Criteria:**
- Identifies changed surfaces (code, infra, CI)
- Outputs structured findings
- Used by `security-reviewer` agent

---

### Issue 12 — Enforce Agent Output Validation
**Type:** Feature | **Priority:** High | **Labels:** `agents` `reliability`

**Description:**
Ensure all agents produce valid structured JSON.

**Acceptance Criteria:**
- Reject invalid output
- Validate against schema
- Fail agent execution on malformed output

---

## EPIC: Config System 🔵

### Issue 13 — Implement Config Inheritance and Precedence
**Type:** Feature | **Priority:** Critical | **Labels:** `config` `architecture` `critical`

**Description:**
Support layered config resolution.

**Acceptance Criteria:**
- Precedence: `defaults < project < profile < runtime`
- Deep merge for objects
- Explicit array merge rules

---

### Issue 14 — Add Config Schema Validation
**Type:** Feature | **Priority:** High | **Labels:** `config` `validation`

**Description:**
Validate config before runtime.

**Acceptance Criteria:**
- Fail fast on invalid config
- Provide clear error messages
- Schema versioning supported

---

### Issue 15 — Add Config Resolution Debug Mode
**Type:** Feature | **Priority:** Medium | **Labels:** `config` `debugging`

**Description:**
Explain final resolved config.

**Acceptance Criteria:**
- Show value + source
- CLI: `pilot-sec config explain`
- Useful for debugging overrides

---

## EPIC: Runtime + Sessions 🟣

### Issue 16 — Implement Session Lifecycle Management
**Type:** Feature | **Priority:** High | **Labels:** `sessions` `core`

**Description:**
Track execution sessions.

**Acceptance Criteria:**
- Start / stop sessions
- Persist session metadata
- Attach runs to sessions

---

### Issue 17 — Add Runtime Sandbox Enforcement
**Type:** Feature | **Priority:** Critical | **Labels:** `security` `runtime` `critical`

**Description:**
Enforce execution boundaries.

**Acceptance Criteria:**
- Control network access
- Control filesystem writes
- Block secret reads unless allowed

---

## EPIC: DevEx + CI Integration ⚫

### Issue 18 — Implement PR Security Summary Command
**Type:** Feature | **Priority:** High | **Labels:** `integration` `github`

**Description:**
Summarize security impact for pull requests.

**Acceptance Criteria:**
- Shows new findings only
- Includes severity breakdown
- Outputs markdown + JSON

---

### Issue 19 — Map Policy Decisions to CI Status Checks
**Type:** Feature | **Priority:** Medium | **Labels:** `ci` `integration`

**Description:**
Integrate with GitHub checks.

**Acceptance Criteria:**
- `allow` → success
- `warn` → neutral
- `block` → failure

---

## META: System Integrity Risks 🔥

### Issue 20 — Define Unified Fact Model
**Type:** Architecture | **Priority:** Critical | **Labels:** `architecture` `critical`

**Description:**
Standardize facts used across scanners, policy, and agents.

**Acceptance Criteria:**
- Document fact schema
- All systems consume same model
- No direct scanner output in policy layer

---

### Issue 21 — Implement Deterministic Replay System
**Type:** Feature | **Priority:** High | **Labels:** `audit` `reliability`

**Description:**
Enable full reproducibility of runs.

**Acceptance Criteria:**
- Replay run from logs
- Same inputs → same outputs
- Includes config + context snapshot

---

## Summary

| # | Title | Epic | Priority |
|---|-------|------|----------|
| 1 | Pre-Execution Risk Classification Hook | Security Control Plane | Critical |
| 2 | Policy Enforcement in Execution Pipeline | Security Control Plane | Critical |
| 3 | Structured Audit Logging | Security Control Plane | Critical |
| 4 | Finding Normalization Schema (finding/v1) | Scanner Normalization | Critical |
| 5 | Scanner Provider Abstraction Layer | Scanner Normalization | High |
| 6 | Scan Result Caching | Scanner Normalization | Medium |
| 7 | Policy Rule Engine (Deterministic) | Policy Engine | Critical |
| 8 | Policy Waiver System | Policy Engine | High |
| 9 | Policy Decision Trace Output | Policy Engine | High |
| 10 | Shared Skill Contract Layer | Agent + Skill System | Critical |
| 11 | diff-analysis Skill | Agent + Skill System | High |
| 12 | Agent Output Validation | Agent + Skill System | High |
| 13 | Config Inheritance and Precedence | Config System | Critical |
| 14 | Config Schema Validation | Config System | High |
| 15 | Config Resolution Debug Mode | Config System | Medium |
| 16 | Session Lifecycle Management | Runtime + Sessions | High |
| 17 | Runtime Sandbox Enforcement | Runtime + Sessions | Critical |
| 18 | PR Security Summary Command | DevEx + CI | High |
| 19 | Policy Decisions to CI Status Checks | DevEx + CI | Medium |
| 20 | Unified Fact Model | System Integrity | Critical |
| 21 | Deterministic Replay System | System Integrity | High |

**Critical count:** 9 | **High count:** 9 | **Medium count:** 3
