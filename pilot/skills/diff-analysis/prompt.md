# diff-analysis

**Category:** analysis
**Contract:** `pilot/skills/_base/contract.yaml`
**Schema:** `pilot/skills/diff-analysis/skill.yaml`

## Purpose

Derive the security-relevant change surface from git diffs and changed files. Identify what changed, classify each changed surface by kind and risk, and surface findings that warrant further investigation by downstream agents or skills.

This skill does not make policy decisions. It produces structured change signal that agents and policy-eval consume.

## Execution Instructions

1. **Collect the diff.** Use `git diff`, `git show`, or read provided artifact files to gather the full change set. Respect `context.base_ref` and `context.head_ref` if provided.

2. **Enumerate changed surfaces.** For each changed file, determine:
   - `path`: relative path from repo root
   - `kind`: classify as one of — `code`, `config`, `infra`, `iac`, `ci`, `manifest`, `secret-surface`, `dependency`, `workflow`
   - `risk_hint`: assign using these heuristics:
     - `critical`: auth, crypto, secrets management, IAM, network exposure config
     - `high`: security controls, input validation, privilege logic, prod infra
     - `medium`: config changes, dependency updates, CI changes
     - `low`: docs, tests, formatting, comments

3. **Scan for findings.** Within the diff, look for:
   - Newly introduced secrets or credential patterns
   - Security control removals or bypasses (e.g., removing auth middleware, disabling TLS)
   - Dangerous function introductions (eval, exec, subprocess with user input)
   - Dependency additions — note name and check for known-suspicious patterns
   - Infrastructure changes that increase exposure (public ACLs, open security groups)
   - CI workflow changes that add new permissions, network access, or external calls

4. **Emit output.** Produce a valid output matching `output_schema` in `skill.yaml`:
   - `changed_surfaces`: one entry per changed file
   - `findings`: one entry per signal worth flagging, with `severity`, `kind`, `path`, `description`, `evidence_ref`
   - `summary`: one paragraph synthesizing the change surface and any notable findings
   - `confidence`: overall confidence in the analysis

## Output Contract

```yaml
skill: "diff-analysis"
status: success | partial | failed
summary: "<paragraph>"
changed_surfaces:
  - path: "src/auth/middleware.ts"
    kind: "code"
    risk_hint: "critical"
    lines_changed: 42
    rationale: "Modifies authentication middleware"
findings:
  - id: "da-001"
    severity: "high"
    kind: "code"
    path: "src/auth/middleware.ts"
    description: "Auth bypass condition introduced on line 88"
    evidence_ref: "git diff HEAD~1..HEAD -- src/auth/middleware.ts#L88"
artifacts_used:
  - "git diff HEAD~1..HEAD"
confidence: "high"
```

## Constraints

- Do not make policy decisions. Emit findings, not verdicts.
- Do not modify any files.
- Redact any actual secret values in `description` or `evidence_ref`.
- If the diff is unavailable, emit `status: failed` with an error.
- Limit findings to signals with `severity >= medium` unless `constraints.severity_filter` overrides.
