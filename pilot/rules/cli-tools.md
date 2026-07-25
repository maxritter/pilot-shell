## CLI Tools

### Pilot CLI

`~/.pilot/bin/pilot`. **Do NOT call commands not listed here** — `pilot pipe` and `pilot init` do not exist.

| Group | Commands |
|-------|----------|
| Session | `check-context --json`, `register-plan <path> <status>` |
| Review | `review-scope [--slug <slug>] [--json]` — **the** resolver for a code review's `git diff` scope; never derive the range by hand |
| Worktree | `worktree detect\|create\|diff\|sync\|cleanup --json <slug>` (slug = plan filename without date prefix and `.md`; `create` auto-stashes). `worktree status --json` takes **no** slug — it reports the worktree for the *current session*. Use `detect` for a specific plan's branch or base branch. |
| License | `activate <key>`, `deactivate`, `status`, `verify`, `trial --check\|--start` |
| Updates | `update [--yes] [--json]` (alias `upgrade`) — user-initiated; don't run it unasked |
| Other | `greet`, `statusline`, `notify` |

**`review-scope`: scripts and skills must use `--json` and parse it.** A `pilot` older than this subcommand prints a banner and exits 0, so a `|| echo HEAD` fallback never fires and the banner text gets spliced into `git diff`. `--json` returns `mode` (`working-tree` | `worktree`), `base_ref`, `diff_range`, and a `warning` when the scope degraded.

### RTK — token-optimized CLI proxy

The Pilot shell hook auto-rewrites commands (`git status` → `rtk git status`), so normally you do nothing. Direct use: `rtk gain` (savings analytics), `rtk gain --history`, `rtk discover`, `rtk proxy <cmd>` (bypass filtering when debugging).

⚠️ If `rtk gain` errors, a different `rtk` (Rust Type Kit) is on PATH.

### Semble — code search CLI

Same engine as the Semble MCP server; see `mcp-servers.md` for when to reach for it over CodeGraph.

```bash
semble search "authentication flow" ./          # intent
semble search "save_pretrained" ./ --top-k 10   # symbol
semble find-related src/auth.ts 42 ./           # similar code from a location
semble savings                                  # token-saving report
```

Ranking adapts to the query shape (symbol-like queries weight lexical, natural language balances semantic + lexical), boosts definitions over references, and down-ranks test/legacy/example files. Auto-reindexes on file change. Defaults are usually right — snippets are already trimmed to the matched code.

**Not for:** callers/callees/impact (CodeGraph enumerates those; Semble only finds code that *mentions* a callee), AST pattern matching, or extracting the enclosing block at `file:line` (use `Read` with `offset`/`limit`).
