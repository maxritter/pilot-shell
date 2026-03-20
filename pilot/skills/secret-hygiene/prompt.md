# secret-hygiene

**Category:** analysis
**Contract:** `pilot/skills/_base/contract.yaml`
**Schema:** `pilot/skills/secret-hygiene/skill.yaml`

## Purpose

Detect, classify, and assess the exposure of secrets in source code, diffs, or scan reports. Produce a structured finding set and an exposure assessment with concrete revocation guidance. Always redact actual secret values in output.

## Execution Instructions

1. **Load inputs.** Read scan reports (gitleaks JSON, semgrep output) from `artifacts`. If no pre-existing reports, use `Grep` to scan `scope` paths for secret patterns.

2. **For each detected secret:**
   - Classify `kind`: `api-key`, `token`, `password`, `certificate`, `private-key`, `connection-string`, `generic`
   - Assign `severity`:
     - `critical`: private keys, production credentials, cloud IAM keys
     - `high`: API keys, tokens with broad scope
     - `medium`: test credentials, limited-scope tokens
     - `low`: placeholder values, example patterns
   - Record `path` and `line`
   - Set `redacted: true` — never include the actual value in output
   - Set `likely_valid: true` if the value pattern matches a known live format (not a test/example)

3. **Assess exposure.** For the full finding set:
   - `likely_live`: true if any finding has `likely_valid: true`
   - `locations`: where each secret appears (`current code`, `git history`, `PR diff`)
   - `blast_radius`: worst-case scope of compromise
   - `revoke_guidance`: ordered steps — rotate first, then audit, then close gaps
   - `notify_required`: true if likely_live and severity >= high

4. **Emit output.** Produce a valid output matching the schema.

## Output Contract

```yaml
skill: "secret-hygiene"
status: success
summary: "1 critical finding: likely-live AWS access key in src/config.ts. Immediate rotation required."
findings:
  - id: "sh-001"
    severity: "critical"
    kind: "api-key"
    path: "src/config.ts"
    line: 42
    description: "AWS access key pattern detected (AKIA...); value redacted"
    redacted: true
    evidence_ref: ".pilot-sec/reports/gitleaks.json#rule-aws-access-key"
    likely_valid: true
exposure_assessment:
  likely_live: true
  locations:
    - "current code"
    - "git history (3 commits)"
  revoke_guidance:
    - "Immediately revoke the AWS access key in IAM console"
    - "Audit CloudTrail for usage since first commit date"
    - "Rotate all secrets that share the same IAM user"
    - "Remove from git history using git-filter-repo"
    - "Add pre-commit secret scanning hook"
  notify_required: true
  blast_radius: "critical"
artifacts_used:
  - ".pilot-sec/reports/gitleaks.json"
confidence: "high"
```

## Constraints

- Never emit actual secret values. Always set `redacted: true` and omit the value.
- If `constraints.include_git_history` is true, check git log for secrets removed from HEAD but present in history.
- `likely_valid` is a best-effort assessment based on format patterns, not live API validation.
- Emit `status: partial` if some artifact files were unreadable.
- Revoke guidance should always be specific and ordered — not generic advice.
