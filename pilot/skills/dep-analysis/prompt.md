# dep-analysis

**Category:** analysis
**Contract:** `pilot/skills/_base/contract.yaml`
**Schema:** `pilot/skills/dep-analysis/skill.yaml`

## Purpose

Analyze project dependencies for known vulnerabilities, license risk, and supply chain signals. Consume pre-existing scan reports when available; fall back to reading lock files directly. Produce normalized findings for agent consumption.

## Execution Instructions

1. **Load inputs.** Check `artifacts` for osv-scanner output, npm audit JSON, or SBOM files. If none, locate lock files in `scope` paths:
   - `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` (Node)
   - `poetry.lock`, `requirements.txt`, `Pipfile.lock` (Python)
   - `go.sum`, `go.mod` (Go)
   - `Cargo.lock` (Rust)

2. **Parse vulnerabilities.** For each vulnerability in the reports or lock files:
   - Extract `package_name`, `package_version`, `ecosystem`
   - Map to `vuln_id` (CVE, GHSA, OSV)
   - Normalize severity using `normalization.yaml` tool_severity_map
   - Note `fixed_in` version if available
   - Mark `is_transitive` if not a direct dependency

3. **Identify supply chain signals.** Look for:
   - Typosquatting patterns (names very similar to popular packages)
   - Packages with no published provenance (no SIGSTORE signature)
   - Recently abandoned packages (last release very old, archived)
   - Recent maintainer transfers

4. **If `context.changed_only` or diff is available:** Identify `newly_added` packages from the diff.

5. **Emit output.** Produce a valid output matching the schema.

## Output Contract

```yaml
skill: "dep-analysis"
status: success
summary: "3 vulnerabilities found: 1 critical (lodash RCE), 2 high. 1 supply chain signal: recent maintainer change in dep-x."
findings:
  - id: "dep-001"
    severity: "critical"
    package_name: "lodash"
    package_version: "4.17.19"
    ecosystem: "npm"
    vuln_id: "CVE-2021-23337"
    description: "Prototype pollution via _.zipObjectDeep; RCE possible in some configurations"
    fixed_in: "4.17.21"
    is_transitive: false
    evidence_ref: ".pilot-sec/reports/osv-results.json#CVE-2021-23337"
supply_chain_signals:
  - package_name: "dep-x"
    signal: "recent-maintainer-change"
    severity: "medium"
newly_added:
  - "some-new-package@1.0.0"
artifacts_used:
  - ".pilot-sec/reports/osv-results.json"
  - "package-lock.json"
confidence: "high"
```

## Constraints

- Do not run package managers or install packages.
- Do not make policy decisions; emit findings only.
- Filter findings to `constraints.severity_filter` threshold when provided.
- If `constraints.include_transitive` is false, omit transitive findings.
- Emit `status: partial` if some lock files were unreadable.
