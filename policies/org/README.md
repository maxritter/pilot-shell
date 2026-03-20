# Org-level policy overlays

Place organisation-specific policy YAML files here.

Files are loaded alphabetically after `policies/default/rules.yaml`.
Each file follows the same schema as `rules.yaml`.

Example use cases:
- Add company-specific blocked commands
- Require gate approval for production deployments
- Add warn rules for proprietary tooling

Example file: `policies/org/acme-corp.yaml`

```yaml
rules:
  - name: require-approval-prod-deploy
    description: Production deploys require ACME_PROD_APPROVED=1
    action: require
    command_pattern: "\\b(kubectl|helm)\\b.*--namespace\\s+production\\b"
    gate_env_var: ACME_PROD_APPROVED
    gate_description: >
      Set ACME_PROD_APPROVED=1 after completing the change-management ticket.
```
