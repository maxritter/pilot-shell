# Security Hardening Notes

This document records the rationale, scope, and known residual risks for the
security hardening patch applied to this fork
(`canstralian/pilot-shell-devsecops`).

---

## What Changed

### `pilot/settings.json`

- **`defaultMode`**: `"bypassPermissions"` → `"default"`
  `bypassPermissions` silently approves every tool call without user
  confirmation. `"default"` restores the normal approval prompt, limiting
  blast radius from any unexpected or malicious tool invocation.

- **`enableAllProjectMcpServers`**: `true` → `false`
  Auto-trusting every MCP server declared in a project is a supply-chain
  risk. `false` requires explicit per-server opt-in.

### `pilot/.mcp.json`

Pinned all `npx`-based MCP servers to explicit versions to eliminate
floating/latest resolution that can pull unreviewed package updates:

| Server | Before | After |
|---|---|---|
| `context7` | `@upstash/context7-mcp` | `@upstash/context7-mcp@2.1.4` |
| `web-search` | `open-websearch` | `open-websearch@1.2.7` |
| `web-fetch` | `fetcher-mcp` | `fetcher-mcp@0.3.9` |

### `install.sh`

`REPO` remains `"maxritter/pilot-shell"` — unchanged intentionally. A
warning comment was added immediately above it: this fork has published zero
release artifacts. Rebranding `REPO` to this fork's path would cause every
install attempt to 404 on binary and installer downloads. The comment makes
the upstream dependency explicit rather than silent.

---

## Assumptions

- `pilot/settings.json` is parsed as JSONC by Claude Code, so `//` comments
  are valid there. `pilot/.mcp.json` is parsed by Python's `json.loads()`
  (see `installer/steps/dependencies.py`), so no comments were added there.
- Pinned npm versions (`2.1.4`, `1.2.7`, `0.3.9`) were the latest stable
  releases at the time of this patch and should be reviewed on a regular
  cadence.
- `skipDangerousModePermissionPrompt: true` was left unchanged as it was
  out of scope for this patch but is called out below.

---

## Remaining Security / Identity Risks

- **`skipDangerousModePermissionPrompt: true` remains enabled.** Even with
  `defaultMode` set to `default`, this still weakens the friction layer
  around escalation into more permissive execution modes.

- **Pinned MCP package versions reduce supply-chain drift, but they do not
  establish artifact trust by themselves.** There is still no signature
  verification, hash pinning, or provenance validation for npm-resolved
  tooling.

- **`enableAllProjectMcpServers: false` narrows ambient capability, but any
  explicitly enabled MCP server still inherits the trust model of its
  package, config, and exposed tools.** The fork still needs a clearer
  allowlist and review posture for MCP usage.

- **If `install.sh` still points to upstream artifacts, the fork's install
  path remains identity-ambiguous.** Users may believe they are installing
  fork-owned behavior while actually receiving upstream binaries or release
  assets.

- **If the installer only documents upstream dependency rather than
  replacing it, the fork still lacks an independent release chain.** That is
  a supply-chain and product-boundary gap, even if it is now transparent.

- **Upstream branding, URLs, and repo references may still exist elsewhere
  in docs, scripts, or metadata.** That can create confusion about support,
  ownership, release provenance, and expected behavior.

- **The current hardening changes improve defaults, but they do not yet add
  enforcement for security checks** such as secret scanning, dependency
  audit, policy validation, or release gating.

- **Extension trust remains a live surface.** Rules, commands, skills,
  agents, and MCP configurations can still alter behavior materially, and
  the fork does not yet appear to have a fully documented trust and review
  model for shared extensions.

- **Privacy and security claims may still exceed what is currently
  demonstrated by code or documentation.** Until data flows, trust
  boundaries, and network behavior are explicitly documented, those claims
  should be treated as provisional.

---

## One-Line Summary for Commit Notes

> Default privilege and MCP exposure were reduced, but major trust surfaces
> remain: dangerous-mode prompt suppression, unsigned external tooling,
> ambiguous installer provenance, inherited upstream identity, and the
> absence of enforced security verification gates.
