# Skill: secret-hygiene

## Purpose

Detect, classify, and assess the exposure of secrets in code, config, and git
history. Produce structured findings and actionable revocation guidance.

This skill does not run external scanners. It performs direct file and pattern
analysis within its tool allowlist.

## Input

- `scope`: file globs or directories to search
- `artifacts`: specific files or git refs to analyze
- `constraints.check_history`: if true, also search git log for secrets introduced then removed
- `constraints.redact_values`: if true (default), mask secret values in output

## Execution steps

1. Search scope for credential-shaped patterns using Grep and Glob:
   - High-entropy strings in config files
   - Known credential prefixes: `ghp_`, `AKIA`, `sk-`, `xoxb-`, `Bearer `, `-----BEGIN`, etc.
   - Connection strings: `postgres://`, `mysql://`, `mongodb+srv://`
   - Explicit key/password assignments in .env, .yaml, .json, .toml files
2. For each candidate:
   a. Confirm it is not a placeholder (e.g. `<YOUR_KEY>`, `example`, `changeme`, `xxx`).
   b. Classify by `kind`.
   c. Assign `severity` based on kind and context (critical: private keys, cloud credentials; high: API tokens, passwords).
   d. Redact the value: preserve first 4 and last 4 characters, mask remainder with `x`.
3. If `check_history` is true: run `git log -p --all -S <pattern>` for high-confidence patterns to find historical exposure.
4. For each confirmed finding, assess exposure:
   - `likely_live`: true if the credential appears in a live config path (not test fixtures, not clearly revoked).
   - `blast_radius`: estimate scope of compromise.
   - `revoke_guidance`: ordered, provider-specific steps (GitHub → Settings > Developer Settings > Tokens; AWS → IAM > Access Keys).
5. Deduplicate findings across files and history.

## Output contract

Return a JSON object conforming to `skill.yaml#output_schema`.

```json
{
  "skill": "secret-hygiene",
  "status": "success",
  "summary": "2 secrets detected; 1 likely live GitHub token in .env; 1 historical AWS key revoked",
  "findings": [
    {
      "id": "secret-001",
      "kind": "api_key",
      "severity": "critical",
      "path": ".env",
      "line": 4,
      "redacted_value": "ghp_xxxx...xxxx",
      "confidence": "high",
      "in_history": false
    }
  ],
  "exposure_assessment": {
    "likely_live": true,
    "locations": [".env", "docker-compose.yml"],
    "revoke_guidance": [
      "Go to GitHub Settings > Developer Settings > Personal Access Tokens",
      "Revoke the token matching the detected prefix",
      "Rotate all services using this token",
      "Audit access logs for the token since first commit date"
    ],
    "blast_radius": "high"
  },
  "artifacts_used": [".env", "docker-compose.yml"],
  "confidence": "high"
}
```

## Constraints

- NEVER output unredacted secret values. Always mask the center.
- Do not access external services to validate whether a secret is live.
- If `redact_values` is false (unusual), still do not log or surface raw values in summary text.
- Only use the bash allowlist: `git log`, `git show`, `git diff`, `git grep`.
- Do not modify any files.
