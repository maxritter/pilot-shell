# incident-triage

**Category:** analysis
**Contract:** `pilot/skills/_base/contract.yaml`
**Schema:** `pilot/skills/incident-triage/skill.yaml`

## Purpose

Triage one or more security signals into a structured incident assessment. Correlate related signals, determine overall severity, and produce a prioritized response action list. This skill does not take remediation actions — it produces triage structure for human or agent response.

## Execution Instructions

1. **Load inputs.** Read all provided `artifacts`: alert data, scan findings, skill outputs (secret-hygiene, iac-analysis, dep-analysis, diff-analysis), log excerpts.

2. **Enumerate signals.** For each distinct security signal:
   - Assign `id` (e.g. `sig-001`)
   - Classify `kind`: `secret-exposure`, `vulnerability`, `misconfiguration`, `anomaly`, `policy-violation`, `supply-chain`
   - Assign `severity` using normalization vocabulary
   - Note `source` (file, report, or skill output ref)
   - Set `likely_false_positive: true` if the signal matches a test fixture, placeholder, or known-safe pattern

3. **Correlate signals.** Identify related signals that describe the same underlying issue:
   - A secret in code + a CI pipeline with network access = correlated
   - A public bucket + a vulnerability in the app that reads from it = correlated
   - Add `correlated_signals` refs

4. **Determine overall severity.** Set `severity` to the highest non-false-positive signal severity.

5. **Generate response actions.** For each action needed:
   - Assign `priority` (1 = most urgent)
   - Write a specific, actionable `action` statement
   - Assign `owner` (security-team, developer, infra-team, etc.)
   - Set `urgency`: `immediate` (now), `hours` (same day), `days` (this week), `sprint` (this iteration)

6. **Set `escalate`.** True if any signal is critical and likely_live, or if correlated signals create a combined critical risk.

7. **Emit output.** Produce a valid output matching the schema.

## Output Contract

```yaml
skill: "incident-triage"
status: success
summary: "Critical: live AWS key exposed in source + CI has network access. Immediate rotation and pipeline freeze required."
severity: "critical"
escalate: true
signals:
  - id: "sig-001"
    kind: "secret-exposure"
    severity: "critical"
    description: "AWS access key (AKIA...) found in src/config.ts, committed 3 days ago; pattern matches live key format"
    source: ".pilot-sec/reports/gitleaks.json"
    correlated_signals: ["sig-002"]
    likely_false_positive: false
  - id: "sig-002"
    kind: "misconfiguration"
    severity: "high"
    description: "CI workflow has unrestricted outbound network access, increasing blast radius of key exposure"
    source: ".github/workflows/deploy.yml"
    correlated_signals: ["sig-001"]
    likely_false_positive: false
response_actions:
  - priority: 1
    action: "Revoke AWS access key immediately via IAM console"
    owner: "security-team"
    urgency: "immediate"
    rationale: "Key is likely live and CI has network access; any CI run may have exfiltrated or misused credentials"
  - priority: 2
    action: "Freeze all CI pipelines that reference the compromised key"
    owner: "infra-team"
    urgency: "immediate"
  - priority: 3
    action: "Audit CloudTrail for key usage over the past 7 days"
    owner: "security-team"
    urgency: "hours"
  - priority: 4
    action: "Remove key from git history using git-filter-repo and force-push"
    owner: "developer"
    urgency: "hours"
artifacts_used:
  - ".pilot-sec/reports/gitleaks.json"
  - ".github/workflows/deploy.yml"
confidence: "high"
```

## Constraints

- Do not take remediation actions.
- Mark `likely_false_positive: true` explicitly when applicable — do not silently drop signals.
- Correlation is additive — correlated signals may increase overall severity beyond any individual signal.
- Response actions must be specific, not generic. "Rotate credentials" is insufficient — specify what and where.
- Set `escalate: true` conservatively; reserve it for situations requiring immediate human judgment.
