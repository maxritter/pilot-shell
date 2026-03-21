# DevSecOps Implementation Plan

> Specific insertion points, files to change, and recommended implementation sequence.
> Companion to `devsecops-control-plane.md`, `trust-boundaries.md`, and `risk-tiers.md`.

---

## 1. Insertion Points

### 1.1 Risk-Tiered Execution

**Where to insert:** `pilot/hooks/tool_redirect.py`

Current state: Blocks WebSearch, WebFetch, Plan/Explore agents by name.
Required addition: Classify all tool calls by risk tier before dispatch. Block Tier 3 tools without a session-level approval flag.

```
pilot/hooks/tool_redirect.py          ← add RISK_TIER map, tier-gate logic
pilot/hooks/_lib/util.py              ← add pre_tool_use_deny variant with tier metadata
pilot/hooks/hooks.json                ← extend PreToolUse matcher to include Write/Edit
```

The tier gate reads a session flag file (`.claude/session-tier-approvals.json`) to check whether a Tier 3 action has been explicitly approved in this session. If not, it blocks and surfaces the required evidence.

---

### 1.2 Secret Scanning Hook

**Where to insert:** `pilot/hooks/` (new file) + `hooks.json` + `.githooks/pre-commit`

New hook: `pilot/hooks/secret_scanner.py`
- Triggers on `PostToolUse` for `Write|Edit|MultiEdit`
- Reads the written file content
- Scans for secret patterns: API keys, tokens, private keys, connection strings
- Returns `additionalContext` warning (non-blocking at T1; blocking at T2 commit gate)

Pre-commit integration: Add a targeted `detect-secrets` or pattern-based scan step in `.githooks/pre-commit` for staged files, separate from the broad Trivy scan.

```
pilot/hooks/secret_scanner.py         ← NEW: pattern-based secret detection
pilot/hooks/hooks.json                ← add PostToolUse hook for Write|Edit
.githooks/pre-commit                  ← add secret scan step for staged files (line 18-29 vicinity)
```

Pattern library (minimal starter set):
- `(sk-|pk-|rk-|sk_live_|pk_live_)[a-zA-Z0-9]{20,}` — Stripe/API keys
- `(ghp_|gho_|ghs_|github_pat_)[a-zA-Z0-9]{36,}` — GitHub tokens
- `-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----` — private keys
- `[a-zA-Z0-9+/]{40}` adjacent to `secret|token|key|password|credential` — generic secrets
- `.env` file content containing `=` and token-length values

---

### 1.3 Dependency Audit Hook

**Where to insert:** `pilot/hooks/` (new file) + `hooks.json` + `.github/workflows/`

New hook: `pilot/hooks/dependency_audit.py`
- Triggers on `PostToolUse` for `Write|Edit` when the written file is `pyproject.toml`, `package.json`, `uv.lock`, or `bun.lockb`
- Runs `uv pip audit --format json` or `npm audit --json` in a subprocess
- Parses output for CRITICAL/HIGH findings against introduced packages
- Returns warning context; blocks at pre-commit if new CRITICAL CVE introduced

CI workflow: `.github/workflows/security-checks.yml` (new)
- Triggers on PR open/synchronize
- Jobs: `secret-scan` (Trivy + detect-secrets), `dep-audit` (pip audit + npm audit), `workflow-policy` (validate .github/workflows/ files)

```
pilot/hooks/dependency_audit.py       ← NEW: CVE check on dependency file writes
pilot/hooks/hooks.json                ← add PostToolUse hook for pyproject.toml/package.json
.github/workflows/security-checks.yml ← NEW: CI secret scan + dep audit + policy check
```

---

### 1.4 Policy Checks

**Where to insert:** `.github/workflows/security-checks.yml` (new job) + `pilot/hooks/`

Two-level policy enforcement:

**Level 1 — Local (hook):** `pilot/hooks/policy_check.py` (new)
- Triggers on `PostToolUse` for Write/Edit of `.github/workflows/*.yml`
- Validates workflow files for known unsafe patterns:
  - `permissions: write-all` or `permissions: write` on `contents`
  - Third-party actions without pinned SHA (`uses: owner/repo@v1` instead of `@<sha>`)
  - `pull_request_target` with `checkout` of `github.event.pull_request.head` (PWN request risk)
  - Secrets referenced in log-emitting steps
- Returns `additionalContext` warning for T2; blocks for T3 (workflow file changes are T3)

**Level 2 — CI:** Add `workflow-policy` job to `security-checks.yml`
- Uses `zizmor` or custom script to lint all workflow files
- Fails PR if critical workflow security violations found

```
pilot/hooks/policy_check.py           ← NEW: workflow file safety checks
pilot/hooks/hooks.json                ← add PostToolUse for .github/workflows/*.yml writes
.github/workflows/security-checks.yml ← add workflow-policy job
```

---

### 1.5 Review-Gated Release Controls

**Where to insert:** `.github/workflows/release.yml` + `.releaserc.json`

Current state: `release.yml` triggers on push to main and runs semantic-release automatically.
Required addition: Insert a manual approval step before the release job executes.

```
.github/workflows/release.yml         ← add environment: production (requires approval)
.github/workflows/release.yml         ← add evidence-summary job before release job
.releaserc.json                       ← no change needed (semver logic is correct)
```

GitHub Environment `production` must be configured in repository settings with:
- Required reviewers: maintainer(s)
- Wait timer: 0 (immediate on approval)
- Deployment branches: `main` only

Additionally, add a `pre-release-check` job that:
1. Verifies all PRs in the release include passing CI checks
2. Verifies no open `security-debt` issues are blocking
3. Generates a release evidence summary (scans, test results, PR list)

---

## 2. Files to Change — Prioritised List

### Tier A: Foundation (enables all other controls)

| File | Change Type | Purpose |
|------|------------|---------|
| `pilot/hooks/tool_redirect.py` | Modify | Add risk-tier map and tier-gate logic |
| `pilot/hooks/hooks.json` | Modify | Add new hook registrations |
| `pilot/hooks/_lib/util.py` | Modify | Add tier-aware denial helper |

### Tier B: Secret & Dependency Safety

| File | Change Type | Purpose |
|------|------------|---------|
| `pilot/hooks/secret_scanner.py` | Create | Pattern-based secret detection on writes |
| `pilot/hooks/dependency_audit.py` | Create | CVE check on dependency file changes |
| `.githooks/pre-commit` | Modify | Add detect-secrets / pattern scan for staged files |
| `.github/workflows/security-checks.yml` | Create | CI secret scan + dep audit workflow |

### Tier C: Policy & Workflow Safety

| File | Change Type | Purpose |
|------|------------|---------|
| `pilot/hooks/policy_check.py` | Create | Workflow file safety validation |
| `.github/workflows/security-checks.yml` | Modify | Add workflow-policy check job |
| `pilot/rules/devsecops.md` | Create | Claude-facing rules for DevSecOps behaviour |

### Tier D: Release Controls

| File | Change Type | Purpose |
|------|------------|---------|
| `.github/workflows/release.yml` | Modify | Add manual approval gate + evidence summary |
| `pilot/hooks/spec_stop_guard.py` | Modify | Surface evidence record on session stop |

### Tier E: Audit & Evidence

| File | Change Type | Purpose |
|------|------------|---------|
| `pilot/hooks/session_end.py` | Modify | Write structured session evidence record |
| `pilot/skills-manifest.json` | Create | Track installed skills with provenance |
| `docs/architecture/devsecops-control-plane.md` | Exists | Reference document for all gates |

---

## 3. Recommended Implementation Sequence

### Sprint 1 — Establish the Hook Foundation

**Goal:** Risk-tiered execution is wired. Every tool call passes through a tier classifier.

1. **`pilot/hooks/_lib/util.py`** — Add `tier_deny(tier, action, reason)` helper function that structures the denial with tier metadata.
2. **`pilot/hooks/tool_redirect.py`** — Import and apply a `RISK_TIER_MAP` dict. For any tool call at T3, check for session approval flag; deny if absent.
3. **`pilot/hooks/hooks.json`** — Extend `PreToolUse` matcher to also capture `Write|Edit|MultiEdit` (currently only `Bash|WebSearch|WebFetch|...`).
4. **Write tests** — `pilot/hooks/tests/test_tool_redirect.py` covering tier classification cases.

Acceptance: `tool_redirect.py` classifies at least `Bash` (T1/T2/T3 depending on command), `Write` (T1), and workflow file writes (T3). Pre-existing tests green.

---

### Sprint 2 — Secret Scanning

**Goal:** Secrets cannot be written to files or committed without detection.

1. **`pilot/hooks/secret_scanner.py`** — Implement pattern scanner. Read file content from `tool_result`, scan against pattern library, emit `additionalContext` warning with file:line.
2. **`pilot/hooks/hooks.json`** — Register `secret_scanner.py` on `PostToolUse` for `Write|Edit|MultiEdit`.
3. **`.githooks/pre-commit`** — Add step after Trivy: scan staged files for secret patterns using `git diff --cached` pipe into scanner. Exit 1 on match.
4. **`.trivyignore`** — Add documentation comment block for any accepted false positives.
5. **Write tests** — `pilot/hooks/tests/test_secret_scanner.py` with synthetic positive and negative examples.

Acceptance: Writing a file containing `ghp_XXXXXXXXXXXXXXXXXX` triggers a warning. A clean file produces no output.

---

### Sprint 3 — Dependency Audit

**Goal:** New dependencies are checked for known CVEs before commit.

1. **`pilot/hooks/dependency_audit.py`** — Implement subprocess call to `uv pip audit` or `npm audit`. Parse JSON output. Emit `additionalContext` with findings.
2. **`pilot/hooks/hooks.json`** — Register on `PostToolUse` for `Write|Edit` when path matches `pyproject.toml|package.json|uv.lock`.
3. **`.github/workflows/security-checks.yml`** — Create new workflow:
   - Trigger: `pull_request` (opened, synchronize)
   - Jobs: `secret-scan` (Trivy filesystem scan on PR diff), `dep-audit` (pip audit + npm audit), `workflow-policy` (basic workflow lint)
   - All jobs produce PR check statuses
4. **Write tests** — Mock subprocess outputs for clean and CVE-found cases.

Acceptance: A PR adding a known-vulnerable package version fails the `dep-audit` CI check.

---

### Sprint 4 — Policy Checks

**Goal:** Generated or modified CI workflows are validated for security.

1. **`pilot/hooks/policy_check.py`** — Implement workflow file linter: check permissions scope, action pinning, PWN request patterns.
2. **`pilot/hooks/hooks.json`** — Register on `PostToolUse` for `Write|Edit` when path matches `.github/workflows/*.yml`.
3. **`.github/workflows/security-checks.yml`** — Add `workflow-policy` job: runs `zizmor` (or equivalent) on all `.github/workflows/*.yml` files in the PR diff.
4. **`pilot/rules/devsecops.md`** — Add Claude-facing rule file documenting that workflow file writes are T3 and require human confirmation.
5. **Write tests** — `test_policy_check.py` with unsafe workflow fixtures.

Acceptance: Writing a workflow with `permissions: write-all` triggers a T3 denial. A correctly scoped workflow passes.

---

### Sprint 5 — Review-Gated Release

**Goal:** Releases require explicit human approval and an evidence summary.

1. **`.github/workflows/release.yml`** — Add `environment: production` to the release job. Create `production` environment in GitHub repository settings with required reviewers.
2. **`.github/workflows/release.yml`** — Add `evidence-summary` job that runs before the release job. Summarises: included PRs, CI check statuses, security scan results.
3. **`pilot/hooks/session_end.py`** — Write a structured evidence record (JSON) to `.claude/evidence/<date>.json` at session end. Include: session ID, tools used, files changed, test outcomes.
4. **`pilot/skills-manifest.json`** — Create manifest tracking installed skills: name, source, install date, reviewer.

Acceptance: A push to main does not auto-release. A human must approve the `production` environment deployment. Evidence summary is visible in the workflow run.

---

### Sprint 6 — Hardening & Documentation

**Goal:** Close remaining gaps; document the evidence trail.

1. **`pilot/hooks/spec_stop_guard.py`** — Emit a structured evidence record when blocking (test failures) or passing. Output format: JSON to `.claude/verify-records/`.
2. **`pilot/.mcp.json`** — Add version pins or commit refs to MCP server entries where possible.
3. **`pilot/rules/devsecops.md`** — Finalise Claude-facing rules covering risk tier awareness, secret handling, and trust boundary behaviour.
4. **Integration test** — End-to-end test: `/spec` → implement → verify → commit → push → PR. Verify all gates fire in expected sequence.
5. **`docs/architecture/`** — Update these documents based on implementation learnings.

---

## 4. Implementation Dependency Graph

```
Sprint 1 (hook foundation)
    ├── Sprint 2 (secret scanning)
    │       └── Sprint 3 (dep audit)
    │               └── Sprint 5 (release gate)
    └── Sprint 4 (policy checks)
            └── Sprint 5 (release gate)
                    └── Sprint 6 (hardening)
```

Sprints 2 and 4 can be parallelised after Sprint 1. Sprint 5 requires both 2 and 4 (or at minimum 4) to have CI checks in place before the release gate is meaningful.

---

## 5. Quick Wins (Low-effort, High-value)

These can be done immediately without waiting for the sprint sequence:

| Action | File | Effort | Value |
|--------|------|--------|-------|
| Pin GitHub Actions to SHA | `.github/workflows/*.yml` | Low | Prevents supply chain attack |
| Add `workflow-policy` job skeleton | `.github/workflows/security-checks.yml` | Low | CI infrastructure ready |
| Add T3 comment to `hooks.json` entries | `pilot/hooks/hooks.json` | Low | Documents existing risk levels |
| Add `pilot/rules/devsecops.md` | new file | Low | Claude-aware security policy |
| Create `pilot/skills-manifest.json` | new file | Low | Foundation for skill provenance |
| Set `SKIP_TRIVY` guidance in README | docs | Low | Prevents accidental bypass |
