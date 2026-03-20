# evidence-pack

**Category:** collection
**Contract:** `pilot/skills/_base/contract.yaml`
**Schema:** `pilot/skills/evidence-pack/skill.yaml`

## Purpose

Collect, normalize, and validate all security evidence needed for a release gate or audit event. Produce a structured pack that an agent can use to determine whether sufficient evidence exists to proceed, and that an auditor can inspect to understand what was checked.

## Execution Instructions

1. **Determine required evidence types.** Use `constraints.required_evidence` if provided. If not, collect all available evidence types:
   - `secrets-scan` — gitleaks or equivalent output
   - `iac-scan` — checkov or equivalent output
   - `dep-scan` — osv or equivalent output
   - `sast-scan` — semgrep or equivalent output
   - `diff-analysis` — diff-analysis skill output
   - `threat-model` — threat-modeling skill output
   - `policy-eval` — policy-eval skill output
   - `sbom` — software bill of materials
   - `test-results` — test run results

2. **Locate evidence.** Search in `artifacts` paths and standard locations:
   - `.pilot-sec/reports/`
   - `.pilot-sec/runs/`
   - Provided artifact paths

3. **For each piece of evidence:**
   - Verify it exists and is readable
   - Check freshness (prefer evidence generated in the same run or within 24h)
   - Extract: kind, source path, decision/status, findings count by severity
   - Mark as `present`, `missing`, `stale`, or `invalid`

4. **Identify missing evidence.** Compare collected evidence against `constraints.required_evidence`. List any missing kinds.

5. **Emit output.** The pack is `complete` when all required evidence is `present` and none is `stale`.

## Output Contract

```yaml
skill: "evidence-pack"
status: partial
summary: "5 of 6 required evidence types collected. SBOM is missing. Policy decision: warn."
evidence:
  - id: "ev-001"
    kind: "secrets-scan"
    source: ".pilot-sec/reports/gitleaks.json"
    status: present
    collected_at: "2026-03-20T14:23:00Z"
    summary: "No secrets detected"
    decision: "allow"
    findings_count:
      critical: 0
      high: 0
      medium: 0
      low: 0
  - id: "ev-002"
    kind: "iac-scan"
    source: ".pilot-sec/reports/checkov.json"
    status: present
    collected_at: "2026-03-20T14:25:00Z"
    summary: "2 high findings in infra/s3.tf"
    decision: "warn"
    findings_count:
      critical: 0
      high: 2
      medium: 1
      low: 3
missing_evidence:
  - "sbom"
artifacts_used:
  - ".pilot-sec/reports/gitleaks.json"
  - ".pilot-sec/reports/checkov.json"
confidence: "high"
metadata:
  audit_target: "release-v1.2.0"
  pack_complete: false
  generated_at: "2026-03-20T14:30:00Z"
```

## Constraints

- Do not run scans. Collect existing evidence only.
- Do not modify any files.
- Mark evidence `stale` if its `collected_at` is more than 24 hours before the current request.
- A partial pack is still valid output — emit `status: partial` and list `missing_evidence`.
- If all required evidence is missing, emit `status: failed`.
