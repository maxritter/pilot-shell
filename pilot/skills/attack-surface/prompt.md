# attack-surface

**Category:** analysis
**Contract:** `pilot/skills/_base/contract.yaml`
**Schema:** `pilot/skills/attack-surface/skill.yaml`

## Purpose

Map the external and internal attack surface exposed by the system or by a specific change. Enumerate API endpoints, permissions, and network exposure. This feeds threat modeling and policy evaluation — it does not make decisions.

## Execution Instructions

1. **Load inputs.** Read API specs (OpenAPI, GraphQL schema), source routes, IaC files, and `context.changed_surfaces` from diff-analysis if available.

2. **Enumerate endpoints.** For each route or API endpoint:
   - Record `path`, `method`
   - Determine `auth_required` (look for auth middleware, guards, decorators)
   - Determine `accepts_input` (request body, query params, file uploads)
   - Assign `risk_hint`:
     - `critical`: unauthenticated write, file upload, exec, admin action
     - `high`: authenticated write to sensitive resource, bulk operations
     - `medium`: authenticated read, filtered queries
     - `low`: static content, health checks

3. **Map permissions.** For IAM roles, service accounts, and RBAC rules:
   - Identify `principal`, `resource`, `action`
   - Assess `scope_risk` (wildcard `*` → critical, broad resource → high, scoped → low/medium)

4. **Assess network exposure.** For each resource with network configuration:
   - Determine if `public`, `internal`, or `private`
   - List open `ports`
   - Assign `risk_hint`

5. **Emit findings.** Flag specific concerns:
   - Unauthenticated endpoints that accept input
   - Overly broad permissions (wildcard principals or actions)
   - Publicly exposed management ports (22, 3389, 5432, etc.)
   - New endpoints added in the current change

6. **Emit output.** Produce a valid output matching the schema.

## Output Contract

```yaml
skill: "attack-surface"
status: success
summary: "12 endpoints mapped; 2 unauthenticated write endpoints (high risk). 1 public management port (critical)."
endpoints:
  - id: "ep-001"
    path: "/api/v1/upload"
    method: "POST"
    auth_required: false
    risk_hint: "critical"
    accepts_input: true
    description: "Unauthenticated file upload endpoint"
permissions:
  - id: "perm-001"
    principal: "ci-runner"
    resource: "*"
    action: "s3:*"
    scope_risk: "critical"
    description: "CI runner has full S3 access; should be scoped to deployment bucket"
network_exposure:
  - resource: "ec2/bastion"
    exposure: "public"
    ports: [22, 3389]
    risk_hint: "high"
findings:
  - id: "as-001"
    severity: "critical"
    description: "POST /api/v1/upload accepts file uploads without authentication"
    path: "src/routes/upload.ts"
artifacts_used:
  - "src/routes/upload.ts"
  - "infra/iam.tf"
confidence: "medium"
```

## Constraints

- Do not make policy decisions; map and flag only.
- If `constraints.changed_only` is true, focus on endpoints and permissions introduced or modified in the current diff.
- If `constraints.include_internal` is false, omit internal-only endpoints.
- Do not attempt live probing or network scanning.
