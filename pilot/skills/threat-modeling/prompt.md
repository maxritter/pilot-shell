# threat-modeling

**Category:** analysis
**Contract:** `pilot/skills/_base/contract.yaml`
**Schema:** `pilot/skills/threat-modeling/skill.yaml`

## Purpose

Identify the security-relevant structure of the system or change under review: what assets exist, where trust boundaries are drawn, what entry points are exposed, and what abuse cases are plausible. This skill feeds agents that must reason about risk without repeating discovery work.

This skill does not emit policy decisions. It produces threat structure that agents and policy-eval consume.

## Execution Instructions

1. **Read the artifacts.** Examine source files, IaC, architecture docs, API specs, or the `context.changed_surfaces` list from a prior diff-analysis run.

2. **Identify assets.** For each meaningful data store, secret, identity, or capability:
   - Assign an `id` (e.g. `asset-001`)
   - Name it clearly
   - Rate `sensitivity` using: `low`, `medium`, `high`, `critical`

3. **Map trust boundaries.** For each interface where trust level changes (user→API, API→DB, service→cloud provider, CI→prod):
   - Identify the `from` and `to` zones
   - Note existing `controls` (auth, TLS, network policy, etc.)

4. **Enumerate entry points.** For each place where external input enters the system:
   - Classify by `kind`: `api`, `ui`, `file`, `network`, `event`, `cli`, `webhook`, `auth`
   - Assign `risk_hint` based on exposure and input handling quality

5. **Derive abuse cases.** For each plausible attacker path:
   - Identify `threat_actor` (e.g. unauthenticated user, malicious dependency, insider)
   - Trace `entry_point` → `asset`
   - Describe `attack_path` in one sentence
   - Assign `severity`
   - Suggest `mitigations`

6. **Emit output.** Produce a valid output matching the schema.

## Output Contract

```yaml
skill: "threat-modeling"
status: success | partial | failed
summary: "<paragraph>"
assets:
  - id: "asset-001"
    name: "User credential store"
    sensitivity: "critical"
    description: "Bcrypt-hashed passwords in PostgreSQL users table"
trust_boundaries:
  - id: "tb-001"
    name: "Public internet → API gateway"
    from: "internet"
    to: "api-gateway"
    controls: ["TLS 1.3", "rate limiting", "WAF"]
entry_points:
  - id: "ep-001"
    name: "POST /api/auth/login"
    kind: "api"
    risk_hint: "critical"
    description: "Accepts username/password; issues JWT"
abuse_cases:
  - id: "abuse-001"
    title: "Credential stuffing via login endpoint"
    threat_actor: "unauthenticated external attacker"
    entry_point: "ep-001"
    asset: "asset-001"
    attack_path: "Attacker submits bulk credential pairs to /api/auth/login to enumerate valid accounts"
    severity: "high"
    mitigations:
      - "Implement account lockout after N failures"
      - "Add CAPTCHA on repeated failure"
artifacts_used:
  - "src/auth/routes.ts"
confidence: "medium"
```

## Constraints

- Do not make policy decisions.
- If `context.changed_surfaces` is provided, prioritize threat-modeling the changed surfaces first.
- Scope to `constraints.focus` categories when provided.
- Emit `status: partial` if you can model some but not all entry points due to missing artifacts.
