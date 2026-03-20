# Skill: policy-eval

## Purpose

Evaluate normalized findings and facts against policy packs and return a
structured decision. This skill is the enforcement gate: it translates evidence
into allow / warn / block / investigate.

This skill does not collect evidence. It only evaluates what is given to it.

## Input

- `artifacts`: normalized `finding/v1` records or prior skill output files
- `policy_context.packs`: paths to policy pack directories to load
- `policy_context.environment`, `.branch`, `.actor`: facts used in rule conditions
- `policy_context.waivers_file`: optional path to active waivers
- `policy_context.fail_on`: minimum severity that triggers a non-allow decision

## Execution steps

1. Load all rule files from each policy pack directory.
2. Load waivers from `waivers_file` if provided; filter to non-expired, in-scope waivers.
3. For each normalized finding in `artifacts`:
   a. Extract facts: `finding.type`, `finding.severity`, `finding.path`, etc.
   b. Evaluate matching rules using their `match` conditions.
   c. Apply waiver if one covers the rule_id and finding scope.
   d. Collect the rule effect: allow, warn, or block.
4. Determine the aggregate `decision`:
   - Any `block` effect → `block`
   - Any unwaived finding at or above `fail_on` severity → `block`
   - Any `warn` effect with no blocks → `warn`
   - Any unevaluable rule without evidence → `investigate`
   - Otherwise → `allow`
5. Populate `failed_rules` and `waivers_applied`.

## Condition evaluation

Rules use `match.all`, `match.any`, or `match.none` with these operators:
`equals`, `not_equals`, `in`, `not_in`, `contains`, `regex`, `gt`, `gte`, `lt`, `lte`

Facts available during evaluation (see `policy/facts.schema.yaml`):
- `finding.type`, `finding.severity`, `finding.path`
- `finding.package.name`, `finding.package.version`
- `finding.network.exposure`, `finding.secret.kind`
- `policy.context.environment`, `git.branch`, `session.actor`

## Output contract

Return a JSON object conforming to `skill.yaml#output_schema`.

```json
{
  "skill": "policy-eval",
  "status": "success",
  "summary": "2 rules failed; 1 waiver applied; decision: block",
  "decision": "block",
  "failed_rules": [
    {
      "rule_id": "no-public-storage",
      "title": "Disallow public object storage",
      "severity": "high",
      "finding_ref": ".pilot-sec/reports/checkov.json#CKV_AWS_20",
      "effect": "block",
      "message": "Public buckets are not allowed outside dev"
    }
  ],
  "waivers_applied": [],
  "artifacts_used": ["policies/default/", ".pilot-sec/reports/checkov.json"],
  "confidence": "high",
  "metadata": {
    "rules_evaluated": 12,
    "waivers_checked": 3,
    "pack_sources": ["policies/default", "policies/devsecops"]
  }
}
```

## Constraints

- Do not modify any files.
- If a policy pack file is missing or malformed, set `status: partial` and continue with available packs.
- Do not invent rules. Only evaluate rules found in the loaded packs.
- Expired waivers must not be applied; note them in `metadata`.
