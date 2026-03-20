# iac-analysis

**Category:** analysis
**Contract:** `pilot/skills/_base/contract.yaml`
**Schema:** `pilot/skills/iac-analysis/skill.yaml`

## Purpose

Analyze infrastructure-as-code files (Terraform, Kubernetes, CloudFormation, etc.) for security misconfigurations. Consume existing scanner reports when available; fall back to reading IaC files directly and applying pattern analysis.

## Execution Instructions

1. **Load inputs.** Check `artifacts` for checkov, tfsec, or kube-score JSON reports. If none, use `Glob` to find IaC files in `scope`:
   - `*.tf`, `*.tfvars` (Terraform)
   - `*.yaml`, `*.yml` in k8s paths (Kubernetes)
   - `*-template.json`, `*.cfn.yaml` (CloudFormation)

2. **Parse scan reports.** For each finding:
   - Extract `rule_id`, `resource_kind`, `resource_name`, `path`, `line`
   - Map severity using `normalization.yaml`
   - Classify `misconfiguration_type`
   - Extract or derive `remediation` steps

3. **If reading IaC directly**, look for:
   - Public ACLs or bucket policies (`public-exposure`)
   - Missing encryption at rest or in transit (`missing-encryption`)
   - Overly permissive IAM (`excessive-permissions`, e.g. `*:*`)
   - Open security groups (0.0.0.0/0 ingress on sensitive ports)
   - Missing logging or audit trails (`missing-logging`)
   - Insecure defaults (HTTP instead of HTTPS, no TLS)
   - Privileged containers or `runAsRoot` in Kubernetes

4. **Identify exposure risks.** For public-facing resources, note the exposure type and severity.

5. **Emit output.** Produce a valid output matching the schema.

## Output Contract

```yaml
skill: "iac-analysis"
status: success
summary: "4 findings: 1 critical (public S3 bucket), 2 high (overpermissive IAM, missing encryption), 1 medium."
findings:
  - id: "iac-001"
    severity: "critical"
    rule_id: "CKV_AWS_20"
    resource_kind: "aws_s3_bucket"
    resource_name: "public_assets"
    path: "infra/s3.tf"
    line: 12
    description: "S3 bucket allows public read access via ACL"
    misconfiguration_type: "public-exposure"
    remediation:
      - "Remove acl = \"public-read\""
      - "Add aws_s3_bucket_public_access_block resource"
      - "Restrict bucket policy to specific principals"
    evidence_ref: ".pilot-sec/reports/checkov.json#CKV_AWS_20"
exposure_risks:
  - resource: "aws_s3_bucket.public_assets"
    exposure_type: "public-read"
    severity: "critical"
artifacts_used:
  - ".pilot-sec/reports/checkov.json"
confidence: "high"
```

## Constraints

- Do not run IaC tools or plan/apply infrastructure.
- Do not make policy decisions; emit findings only.
- Filter to `constraints.severity_filter` when provided.
- Focus on `constraints.frameworks` when specified.
- If `constraints.changed_only` is true and diff context is available, prioritize changed IaC files.
