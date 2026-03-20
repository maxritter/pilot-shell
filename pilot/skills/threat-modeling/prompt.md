# Skill: threat-modeling

## Purpose

Identify assets, trust boundaries, entry points, and abuse cases from code,
config, and infrastructure artifacts. This skill produces structured threat
intelligence that agents use to scope security reviews and prioritize controls.

This skill does not evaluate policy. It identifies what could go wrong and what
an attacker would target.

## Input

- `objective`: what the caller wants to model (e.g. "identify abuse cases introduced in this PR")
- `scope`: directory paths or file patterns bounding the analysis
- `artifacts`: may include diff-analysis output, file paths, architecture docs
- `constraints.focus`: optional list to narrow to specific domains (auth, network, data, etc.)

## Execution steps

1. Read relevant source files, config, and infra artifacts within scope.
2. Identify **assets**: what data or capabilities are worth protecting.
   - Map sensitivity using: critical (secrets, PII, prod credentials), high (auth tokens, internal APIs), medium (user data, config), low (public data, logs).
3. Identify **trust boundaries**: where control or data crosses between zones.
   - Examples: internet → API, API → database, CI → production, user → admin, dependency → runtime.
4. Identify **entry points**: how external actors or data reach the system.
   - Classify by kind: http, rpc, cli, file, event, webhook, ci-trigger.
   - Assess authentication and authorization at each point.
5. Derive **abuse cases**: what an actor could do at each entry point targeting each asset.
   - Structure each case with actor, technique (MITRE-style if applicable), target asset, severity, and proposed mitigations.
6. Score severity using the shared scale: low / medium / high / critical.

## Output contract

Return a JSON object conforming to `skill.yaml#output_schema`.

```json
{
  "skill": "threat-modeling",
  "status": "success",
  "summary": "3 critical assets identified; 2 trust boundaries lack authentication; 4 abuse cases scoped",
  "assets": [
    {
      "id": "asset-001",
      "name": "Production database credentials",
      "sensitivity": "critical",
      "description": "Referenced in .env.prod and CI secrets"
    }
  ],
  "trust_boundaries": [],
  "entry_points": [],
  "abuse_cases": [],
  "artifacts_used": ["infra/", ".github/workflows/deploy.yml"],
  "confidence": "medium"
}
```

## Constraints

- Base analysis on what is present in the artifacts; do not speculate beyond evidence.
- If scope is a PR diff, focus on threats introduced or modified by the change.
- Do not duplicate findings from secret-hygiene or dep-analysis; reference them.
- If artifacts are insufficient to model a boundary, mark it with `risk_hint: unknown` and note in summary.
