# Skill: evidence-pack

## Purpose

Collect and normalize evidence from scanner reports, prior skill outputs, and
CI artifacts into a structured evidence record. Used as the input to release
gates and audit logs.

This skill collects; it does not evaluate. Policy decisions belong to policy-eval.

## Input

- `artifacts`: paths to scanner reports, skill output JSON files, CI log paths, or git refs
- `constraints.required_evidence_kinds`: list of evidence types the caller requires
- `constraints.min_confidence`: minimum confidence level to accept an evidence item
- `context.release_ref`: git ref being evaluated (commit sha, tag, branch)

## Execution steps

1. For each artifact in `artifacts`:
   a. Determine its `kind` from file name, path pattern, or content inspection.
   b. Read the artifact and extract: status (passed/failed/partial), confidence, summary.
   c. Record the artifact reference exactly as found (path + optional anchor).
2. For each `required_evidence_kinds` entry:
   a. Check whether a matching evidence item was found.
   b. If not found, add its kind to `missing_evidence`.
3. Filter out evidence items below `min_confidence` if specified.
4. Set aggregate `status`:
   - `success`: all required kinds found, none failed
   - `partial`: some required kinds missing, or some items are partial
   - `failed`: critical evidence failed or majority of required kinds missing

## Evidence kind patterns

| kind | Typical file patterns |
|------|-----------------------|
| secret-scan | `*gitleaks*`, `*truffleog*`, `*secret*` |
| dep-scan | `*osv*`, `*snyk*`, `*deps*` |
| iac-scan | `*checkov*`, `*tfsec*`, `*iac*` |
| sast-scan | `*semgrep*`, `*sast*`, `*sarif*` |
| policy-decision | `*policy*`, `*policy-eval*` |
| test-results | `*junit*`, `*pytest*`, `*coverage*` |
| threat-model | `*threat-model*`, `*threat*` |

## Output contract

Return a JSON object conforming to `skill.yaml#output_schema`.

```json
{
  "skill": "evidence-pack",
  "status": "partial",
  "summary": "4 of 5 required evidence kinds collected; dep-scan missing",
  "evidence": [
    {
      "id": "ev-001",
      "kind": "secret-scan",
      "source": "gitleaks",
      "status": "passed",
      "confidence": "high",
      "ref": ".pilot-sec/reports/gitleaks.json",
      "summary": "No secrets detected in 14 changed files"
    }
  ],
  "missing_evidence": ["dep-scan"],
  "artifacts_used": [".pilot-sec/reports/"],
  "confidence": "medium"
}
```

## Constraints

- Do not run scanners. Collect and normalize existing reports only.
- Do not modify any files.
- If an artifact is unreadable, record it as `status: partial` and continue.
- Redact any secret values found in report content; reference only metadata.
