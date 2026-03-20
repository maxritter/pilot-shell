# Skill: iac-analysis

## Purpose

Detect misconfigurations and policy violations in infrastructure-as-code.
Normalize findings from pre-run scanner reports or perform direct rule-based
analysis on Terraform, Kubernetes, Dockerfile, and similar IaC artifacts.

This skill does not apply Terraform or run containers. It reads and analyzes files.

## Input

- `scope`: IaC directories or file globs (e.g. `infra/`, `**/*.tf`, `k8s/`)
- `artifacts`: IaC files, Terraform plan JSON, or pre-run checkov/tfsec JSON reports
- `constraints.frameworks`: optional filter to specific IaC types
- `constraints.changed_only`: if true, focus on resources touched in the current diff
- `context.cloud_provider`: helps scope rule selection (aws, gcp, azure)

## Execution steps

1. Locate IaC files within scope using Glob. Detect frameworks from file extensions and content.
2. If pre-run reports exist in `artifacts`, read and normalize them.
3. For direct analysis (when no pre-run reports), apply rule checks by framework:

   **Terraform:**
   - Public storage: `acl = "public-read"` or missing `public_access_block`
   - Open security groups: `cidr_blocks = ["0.0.0.0/0"]` on sensitive ports
   - Unencrypted storage: missing `server_side_encryption_configuration`
   - No versioning on state buckets
   - IAM wildcard: `"*"` in actions or resources

   **Kubernetes:**
   - `privileged: true` in securityContext
   - `hostNetwork: true` or `hostPID: true`
   - Missing resource limits (cpu/memory)
   - `runAsRoot` without explicit false
   - Sensitive env vars without secretKeyRef

   **Dockerfile:**
   - `USER root` without subsequent USER change
   - `ADD` with URLs (use COPY instead)
   - `--no-check-certificate` in RUN steps
   - Pinned base images: flag `:latest` tags

4. For each finding:
   a. Assign `rule_id` (use provider rule ids where available; prefix `PILOT-IAC-` for custom rules).
   b. Map to normalized `type` from `normalization.yaml`.
   c. Note `is_new_in_diff` if the resource was added or modified in the current change.
   d. Provide `remediation.guidance`.
5. Apply `severity_threshold` filter.

## Output contract

Return a JSON object conforming to `skill.yaml#output_schema`.

```json
{
  "skill": "iac-analysis",
  "status": "success",
  "summary": "4 IaC findings; 2 high-severity public exposure risks in Terraform",
  "findings": [
    {
      "id": "iac-001",
      "rule_id": "CKV_AWS_20",
      "severity": "high",
      "type": "public_bucket",
      "title": "S3 bucket allows public read access",
      "path": "infra/s3.tf",
      "line": 42,
      "resource_kind": "aws_s3_bucket",
      "resource_name": "public_assets",
      "framework": "terraform",
      "remediation": {
        "guidance": [
          "Set acl to private",
          "Add aws_s3_bucket_public_access_block with all options true"
        ]
      },
      "is_new_in_diff": true,
      "confidence": "high"
    }
  ],
  "artifacts_used": ["infra/s3.tf", "infra/sg.tf"],
  "confidence": "high",
  "metadata": {
    "files_scanned": 8,
    "resources_evaluated": 23,
    "frameworks_detected": ["terraform"]
  }
}
```

## Constraints

- Do not run terraform, kubectl, docker, or any infrastructure tooling.
- Only use Glob, Read, Grep, and the bash allowlist: `git diff`, `git show`.
- If pre-run scanner reports are present, prefer normalizing them over re-deriving findings.
- Do not modify any files.
