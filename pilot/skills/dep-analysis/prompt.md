# Skill: dep-analysis

## Purpose

Identify vulnerable, malicious, or policy-violating dependencies from lockfiles,
manifests, and pre-run scanner reports. Focus on changes introduced in the current
diff when `changed_only` is true.

This skill does not run package managers or network calls. It reads existing
lockfiles and reports.

## Input

- `artifacts`: lockfiles (package-lock.json, poetry.lock, go.sum, Cargo.lock),
  manifest files, or pre-run osv/snyk JSON report paths
- `constraints.severity_threshold`: filter findings below this severity
- `constraints.include_transitive`: whether to report transitive vulnerabilities
- `constraints.changed_only`: if true, only report on deps that changed in the diff

## Execution steps

1. Locate manifest and lockfiles within scope using Glob.
2. If pre-run reports exist in `artifacts`, read and normalize them to `finding/v1`.
3. If only raw manifests/lockfiles are present:
   a. Read each lockfile and extract package names + resolved versions.
   b. Cross-reference against any advisory data in artifacts (osv JSON, snyk JSON).
   c. If `changed_only`, run `git diff <ref>` on the lockfile and extract only added/changed lines.
4. For each vulnerable package:
   a. Identify vuln_id (CVE, GHSA, OSV).
   b. Determine severity from advisory data.
   c. Note whether it is a transitive dependency and trace `introduced_by`.
   d. Note `is_new_in_diff` if the package was added or upgraded in the current change.
5. Apply `severity_threshold` filter.
6. Set aggregate `status`: success if complete, partial if some lockfiles were unreadable.

## Ecosystem detection

| Ecosystem | Manifest | Lockfile |
|-----------|----------|----------|
| npm | package.json | package-lock.json, yarn.lock, pnpm-lock.yaml |
| pypi | pyproject.toml, requirements.txt | poetry.lock, uv.lock |
| go | go.mod | go.sum |
| cargo | Cargo.toml | Cargo.lock |
| maven | pom.xml | - |

## Output contract

Return a JSON object conforming to `skill.yaml#output_schema`.

```json
{
  "skill": "dep-analysis",
  "status": "success",
  "summary": "3 vulnerable packages; 1 new critical introduced in this PR",
  "findings": [
    {
      "id": "dep-001",
      "package_name": "lodash",
      "installed_version": "4.17.15",
      "fixed_version": "4.17.21",
      "severity": "high",
      "vuln_id": "CVE-2021-23337",
      "title": "Prototype Pollution in lodash",
      "is_transitive": false,
      "is_new_in_diff": true,
      "ecosystem": "npm",
      "remediation": "Upgrade lodash to >= 4.17.21"
    }
  ],
  "artifacts_used": ["package-lock.json"],
  "confidence": "high",
  "metadata": {
    "packages_evaluated": 142,
    "new_deps_in_diff": 3
  }
}
```

## Constraints

- Do not run npm, pip, go, or any package manager commands.
- Do not make network calls; use only artifacts provided.
- If no advisory data is available to cross-reference, return `status: partial`
  with a note that findings may be incomplete.
- Only use Glob, Read, Grep, and the bash allowlist: `git diff`, `git show`.
