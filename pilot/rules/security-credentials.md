# Credential Leak Prevention

Pilot scans for credentials at four entry points and blocks the operation when secrets are found. The scanner runs as Claude Code hooks; toggle is ON by default.

## What gets scanned

| Event | What is scanned | What happens on a match |
|-------|-----------------|-------------------------|
| `UserPromptSubmit` | The submitted prompt text | Stderr block message; prompt is **not delivered** to Claude. Exit 2. |
| `PreToolUse(Read)` | Requested file path (name) + file content (binary-safe, BOM-aware) | Read tool denied. The denied path's basename and resolved-symlink target are both checked. |
| `PreToolUse(Bash)` | Command text, `$VAR`/`${VAR}` env values, `cat`/`head`/`tail`/etc. file targets, `git commit` staged diff + staged blobs, chained `git add … && git commit` files | Bash tool denied. |
| `PostToolUse(Bash)` | Combined `stdout + stderr` (first 1 MB) | Tool result is **dropped** — Claude sees the block reason instead of the secret-containing output. |

## What gets detected

24 secret patterns ported from [gitleaks](https://github.com/gitleaks/gitleaks) and [TruffleHog](https://github.com/trufflesecurity/trufflehog), grouped by category:

| Category | Rules |
|----------|-------|
| Cloud | `aws-access-key`, `gcp-api-key`, `private-key` (PEM/SSH) |
| Source control | `github-pat`, `github-fine-grained`, `gitlab-pat` |
| Package registry | `npm-token` |
| Communication | `slack-token`, `slack-webhook`, `discord-webhook`, `telegram-bot-token`, `twilio-sid` |
| Email | `sendgrid-key`, `mailgun-key`, `mailchimp-key` |
| Payment | `stripe-secret-key`, `stripe-restricted-key` |
| AI | `openai-key`, `openai-project-key`, `anthropic-key` |
| Auth | `jwt` |
| Generic | `generic-secret`, `env-assignment`, `connection-string` |

Generic patterns use a Shannon-entropy filter (3.0–3.5 bits per character) to suppress matches like `API_KEY=test12345`.

## `.env` files are name-blocked unconditionally

Any file whose basename is `.env` or starts with `.env.` (e.g. `.env.local`, `.env.production`) is denied at `PreToolUse(Read)` regardless of content. Symlinks are resolved before the name check — `safe.txt → /tmp/.env` is also blocked. This is intentional — agents do not need to read raw secrets to understand the schema; ask the user which keys are missing instead.

## Allow tags (per-call bypass)

Add a tag to your **next user prompt** to bypass the scan for the current turn:

| Tag | Effect |
|-----|--------|
| `[allow-secret]` | Allow secret findings to pass through |
| `[allow-all]` | Bypass all scanner checks (equivalent here, since PII rules are out of scope) |

**One-shot semantics.** The tag is honoured for the *first* tool call after the prompt. Subsequent tool calls in the same agent turn are re-blocked unless you re-tag in a new prompt. Tags in **assistant** messages or in the bash **command string** are NOT honoured (prompt-injection defense).

The block message always shows the exact tag to add and a sample retry phrasing.

## Toggle

Console Settings → Security → Credential Scanner. Default ON.

Disabling skips all scans across all four entry points. The hook subprocess reads `PILOT_CREDENTIAL_SCANNER_ENABLED`, which is exported by the launcher from `~/.pilot/config.json` (`securityScanner.credentialScanner` field). Restart Claude Code after toggling.

## Out of scope (Batch 1)

- **PII detection** (emails, SSN, phones, credit cards, IPs) — sensitive-canary's PII rules and Luhn validator are intentionally NOT ported.
- **`PostToolUse(Grep)`/`(Glob)` output scanning** — Read tool covers underlying file content; deferred follow-up.
- **`Edit`/`Write`/`MultiEdit` pre-flight scanning** — once Claude has the secret in context, blocking the file write doesn't unleak it.
- **`git push` unpushed-range scanning** — commit-time staged-diff scan is the chosen choke point.
- **Subagent / MCP tool outputs** — out of scope; deferred.

## Why it matters

Credential leaks via AI agents have two distinct surfaces. **Context leak**: a secret read into the session ends up in transcripts, summaries, search indexes, and any tool calls the agent makes thereafter — scrubbing them after the fact is unreliable. **Commit leak**: a secret committed to git, even briefly, must be treated as compromised — git history is durable, mirrors are everywhere, and rotation is the only fix.

The scanner closes both surfaces with a single hook entry, fail-closed defaults, and a documented bypass for legitimate cases (e.g., reading your own `.env` to verify content during local dev). False-positive cost is bounded — one tag, one prompt — while the worst-case cost of a real leak is hours of credential rotation, key-rotation cascades, and audit-log review.

## See also

- `development-practices.md` § Git Operations — commit-time scanning interacts with the user-approval rules for `git add` / `git commit`.
- `pilot/hooks/_lib/secret_scanner.py` — the 24-rule definition (port of `sensitive-canary/src/lib/rules.ts`).
- `pilot/hooks/credential_scanner.py` — hook entry point.
