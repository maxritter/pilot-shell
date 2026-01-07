## Semantic Code Search using Vexor CLI (IMPORTANT)

Semantic file discovery via `vexor`. Use whenever locating where something is implemented/loaded/defined in a medium or large repo, or when the file location is unclear. Prefer this over manual browsing. Find files by intent (what they do), not exact text.

### Command

```bash
vexor "<QUERY>" [--path <ROOT>] [--mode <MODE>] [--ext .py,.md] [--exclude-pattern <PATTERN>] [--top 5] [--format rich|porcelain|porcelain-z]
```

### Common Flags

- `--path/-p`: root directory (default: current dir)
- `--mode/-m`: indexing/search strategy
- `--ext/-e`: limit file extensions (e.g., `.py,.md`)
- `--exclude-pattern`: exclude paths by gitignore-style pattern (repeatable; `.js` → `**/*.js`)
- `--top/-k`: number of results
- `--include-hidden`: include dotfiles
- `--no-respect-gitignore`: include ignored files
- `--no-recursive`: only the top directory
- `--format`: `rich` (default) or `porcelain`/`porcelain-z` for scripts
- `--no-cache`: in-memory only, do not read/write index cache

### Modes (pick the cheapest that works)

- `auto`: routes by file type (default)
- `name`: filename-only (fastest)
- `head`: first lines only (fast)
- `brief`: keyword summary (good for PRDs)
- `code`: code-aware chunking for `.py/.js/.ts` (best default for codebases)
- `outline`: Markdown headings/sections (best for docs)
- `full`: chunk full file contents (slowest, highest recall)

### Troubleshooting

- Need ignored or hidden files: add `--include-hidden` and/or `--no-respect-gitignore`.
- Scriptable output: use `--format porcelain` (TSV) or `--format porcelain-z` (NUL-delimited).
- Get detailed help: `vexor search --help`.
- Config issues: `vexor doctor` or `vexor config --show` diagnoses API, cache, and connectivity (tell the user to set up).

### Examples

```bash
# Find CLI entrypoints / commands
vexor search "typer app commands" --top 5
```

```bash
# Search docs by headings/sections
vexor search "user authentication flow" --path docs --mode outline --ext .md --format porcelain
```

```bash
# Locate config loading/validation logic
vexor search "config loader" --path . --mode code --ext .py
```

```bash
# Exclude tests and JavaScript files
vexor search "config loader" --path . --exclude-pattern tests/** --exclude-pattern .js
```

### Tips

- First time search will index files (may take a minute). Subsequent searches are fast. Use longer timeouts if needed.
- Results return similarity ranking, exact file location, line numbers, and matching snippet preview.
- Combine `--ext` with `--exclude-pattern` to focus on a subset (exclude rules apply on top).
