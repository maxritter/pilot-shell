# Security Hardening Note — Default Execution & MCP Trust Boundaries

## What changed and why

### `pilot/settings.json`

| Setting | Before | After | Reason |
|---|---|---|---|
| `permissions.defaultMode` | `"bypassPermissions"` | `"default"` | `bypassPermissions` silently grants every tool call without prompting. `default` restores per-operation review, limiting blast radius for any mistaken or malicious agent action. |
| `skipDangerousModePermissionPrompt` | `true` | `false` | This flag suppressed the warning shown when entering elevated-trust modes. Re-enabling it ensures the operator is informed before trust is escalated. |
| `enableAllProjectMcpServers` | `true` | `false` | Automatically loading every `.mcp.json` server in a project means any checked-in config file becomes an implicit execution surface. Disabling requires explicit opt-in per session. |

### `pilot/.mcp.json`

All three `npx`-invoked MCP servers now carry explicit version pins so that
`npx -y <package>` cannot silently pull a newer (potentially compromised)
release at runtime:

| Server | Before | After |
|---|---|---|
| `context7` | `@upstash/context7-mcp` | `@upstash/context7-mcp@2.1.4` |
| `web-search` | `open-websearch` | `open-websearch@1.2.7` |
| `web-fetch` | `fetcher-mcp` | `fetcher-mcp@0.3.9` |

The two remaining servers (`codebase-memory-mcp` via a local binary and
`grep-mcp` via HTTP) have no npm version to pin; their trust boundaries are
discussed below.

---

## Residual trust risks (still present after this patch)

1. **`DISABLE_INSTALLATION_CHECKS=true`** (`pilot/settings.json` `env` block)  
   Skips integrity checks during installation. Left in place to preserve
   container/CI compatibility, but increases supply-chain risk on developer
   machines. Operators who do not need this should remove it locally.

2. **`grep-mcp` HTTP server** (`pilot/.mcp.json`)  
   Points to `https://mcp.grep.app`, an external HTTP endpoint. No version
   pin is possible for HTTP transports. All tool calls to this server leave
   the local machine. Treat it as an untrusted network dependency.

3. **`codebase-memory-mcp` local binary** (`pilot/.mcp.json`)  
   Executes `~/.local/bin/codebase-memory-mcp` directly. Integrity depends on
   whatever was written to that path at install time; there is no checksum
   verification here.

4. **`install.sh` upstream origin** (`install.sh`, line 5)  
   `REPO="maxritter/pilot-shell"` still pulls release artifacts from the
   upstream repository. This fork's installer currently has no independent
   release channel, so users are trusting the upstream supply chain.

5. **`npx -y` flag on pinned packages**  
   Even with version pins, `npx -y` auto-installs without interactive
   confirmation. A compromised npm registry entry at the pinned version would
   still execute. Prefer `npm exec` with a local cache or a lockfile once
   this project has a dedicated npm workspace.
