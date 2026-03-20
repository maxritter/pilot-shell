# Skill: diff-analysis

## Purpose

Extract security-relevant change signals from a git diff. Produce a structured
surface map so downstream agents can prioritize scanner scope and threat modeling.

This skill does not make policy decisions. It only classifies what changed.

## Input

- `objective`: what the caller wants to understand (e.g. "identify high-risk surfaces in this PR")
- `scope`: file globs or git refs to bound the analysis
- `artifacts`: commit refs, branch names, or diff files to analyze
- `context.branch`, `context.base_ref`, `context.head_ref`: optional git context

## Execution steps

1. Run `git diff <base_ref>..<head_ref> --name-status` or read provided diff files.
2. Classify each changed file by `kind`:
   - `code`: source files (.py, .ts, .go, .js, .rb, etc.)
   - `config`: application config (.env, .yaml, .json, .toml, .ini)
   - `infra`: Terraform, CloudFormation, Helm, Kubernetes manifests
   - `ci`: GitHub Actions, GitLab CI, Dockerfile, .github/
   - `manifest`: package.json, pyproject.toml, go.mod, Cargo.toml, requirements.txt
   - `secret-surface`: files likely to contain or reference secrets
3. Assign `risk_hint` per file:
   - `critical`: credentials, private keys, production infra changes, CI pipeline mutations
   - `high`: manifest changes (dep additions), auth code, IAM/RBAC, network config
   - `medium`: application config, test infra, API clients
   - `low`: docs, comments, formatting, test fixtures
4. Emit `findings` for specific patterns within the diff:
   - New files added in sensitive locations (`.github/`, `infra/`, root `.env`)
   - Removal of security controls (e.g. deleted secret scanner config)
   - Credential-shaped strings introduced (defer detail to secret-hygiene skill)
5. Return `changed_surfaces` sorted by `risk_hint` descending.

## Output contract

Return a JSON object conforming to `skill.yaml#output_schema`.

```json
{
  "skill": "diff-analysis",
  "status": "success",
  "summary": "14 files changed; 3 high-risk surfaces identified (CI pipeline, infra, manifest)",
  "changed_surfaces": [
    {
      "path": ".github/workflows/deploy.yml",
      "kind": "ci",
      "risk_hint": "critical",
      "lines_added": 22,
      "lines_removed": 4
    }
  ],
  "findings": [],
  "artifacts_used": ["git diff origin/main..HEAD"],
  "confidence": "high"
}
```

## Constraints

- Do not read file contents beyond what is needed to classify kind and risk_hint.
- Do not run scanners. Surface classification only.
- If the diff is unavailable, return `status: partial` and explain in `metadata.error`.
- Use only the bash allowlist: `git diff`, `git status`, `git show`, `git log`.
