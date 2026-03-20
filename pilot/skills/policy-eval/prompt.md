# policy-eval

**Category:** evaluation
**Contract:** `pilot/skills/_base/contract.yaml`
**Schema:** `pilot/skills/policy-eval/skill.yaml`

## Purpose

Evaluate normalized evidence (findings from other skills, scan outputs) against policy rules and emit a structured decision. The decision is one of: `allow`, `warn`, `block`, `investigate`.

Policy evaluation is deterministic given the same facts and rules. This skill should not perform new discovery — it consumes evidence already collected.

## Execution Instructions

1. **Load policy packs.** Read the rule files listed in `policy_context.packs`. Also read `policy_context.waivers_file` if provided. Use `Read` and `Glob` to locate rule YAML files under `pilot/policy/`.

2. **Normalize incoming facts.** Parse all artifacts (skill output JSON/YAML, finding files). Extract the fact model fields needed for rule evaluation:
   - `finding.type`, `finding.severity`, `finding.path`
   - `policy.context.environment`, `git.branch`, `session.actor`
   - Any additional facts referenced by rules

3. **Evaluate rules.** For each rule in the loaded packs:
   - Check `applies_to.events` and `applies_to.targets` — skip rules that don't apply
   - Evaluate the `match` conditions using the fact model
   - Check if a valid, non-expired waiver covers this rule+scope combination
   - Classify the outcome: passed, failed-and-blocked, failed-and-warned, waived

4. **Determine overall decision.** Apply this logic:
   - Any rule with `effect: block` and no covering waiver → `decision: block`
   - Any rule with `effect: warn` and no covering waiver → `decision: warn` (if no block)
   - All rules pass or waived → `decision: allow`
   - Insufficient evidence to evaluate → `decision: investigate`
   - In `observe` mode: never emit `block`, emit `warn` instead

5. **Emit output.** Produce a valid output matching the schema.

## Output Contract

```yaml
skill: "policy-eval"
status: success
summary: "2 rules failed. 1 blocking (public storage in staging). 1 waived (dev public assets). Decision: block."
decision: "block"
failed_rules:
  - rule_id: "no-public-storage"
    title: "Disallow public object storage"
    severity: "high"
    effect: "block"
    finding_ref: ".pilot-sec/reports/checkov.json#CKV_AWS_20"
    message: "Public buckets are not allowed in staging"
    remediation:
      - "Set public_access_block = true"
      - "Restrict bucket policy principals"
waivers_applied:
  - waiver_id: "waiver-001"
    rule_id: "no-public-storage"
    scope:
      paths: ["infra/dev/public-assets.tf"]
      environments: ["dev"]
    approved_by: "esteban"
    expires_at: "2026-06-30T00:00:00Z"
    reason: "Temporary public asset hosting during migration"
passed_rules:
  - "no-hardcoded-secrets"
  - "require-tls-1.3"
artifacts_used:
  - ".pilot-sec/reports/checkov.json"
  - "pilot/policy/policies/devsecops/rules/no-public-storage.yaml"
confidence: "high"
```

## Constraints

- Do not discover new findings. Consume only provided artifacts.
- Respect `policy_context.mode`:
  - `observe`: evaluate but never emit `block`
  - `warn`: evaluate but never emit `block`
  - `enforce`: emit `block` when required
- Respect `policy_context.fail_on`: only block on findings at or above this severity.
- Expired waivers do not count. Check `expires_at` against current date.
- If a rule references a fact not present in the evidence, skip that rule and note it in `errors`.
