# Step 4 — Execute

Run the runner **in the background** so the user gets live status updates while it runs. Foreground bash blocks for the full duration (often 5-30 minutes) and shows nothing until the end — that's a bad UX, don't do it.

## Launch in the background

Use the `Bash` tool with `run_in_background=true`. Capture the returned task ID; you will need it to read output and check completion.

```
Bash(
  command="PYTHONPATH=~/.claude/skills/benchmark uv run python -m scripts.runner \
    --config benchmarks/<target-name>/evals.json \
    --skip-permissions",
  description="Run benchmark in background",
  run_in_background=true,
)
```

That's it for arguments — defaults handle the rest. The runner reads the target skill's `model:` frontmatter and uses that for both executor and grader. Rules targets and skills without a `model:` field fall back to `claude-sonnet-4-6`.

**Why `uv run`:** every Python invocation in this project uses `uv run` — no system `python` or `python3`. It ensures the right interpreter and dependency set.

**Why `--skip-permissions`:** all benchmark runs need this flag because `claude -p` is spawned non-interactively (no terminal to answer permission prompts). It passes `--dangerously-skip-permissions` to every executor and grader subprocess. Only use in a trusted environment — the grader reads arbitrary file paths passed by evals.json.

## Surface the plan header to the user immediately

As soon as the runner starts, it prints a plan header (config path, target, output dir, evals × configs × runs, models). Read it with `BashOutput` and relay it verbatim to the user so they see the scope and ETA up front:

```
BashOutput(bash_id="<task_id>")
```

Then send a brief intro to the user, e.g.:

> Benchmark started in the background. **Plan:** 6 evals × 2 configs × 1 run = 12 runs, executor=claude-opus-4-7. Estimated ~30-45 min on opus. I'll surface progress as runs complete and the final summary when it finishes.

## Status updates while it runs

The runner emits two kinds of stdout that Claude should look for:

| Pattern | When | What to do |
|---------|------|-----------|
| `[N/M] ✓ eval-X config run-N  78.3s, 12.4k tok  · ... ETA Xm` | Per completed run | Once you've seen >2 of these, you have an ETA — relay the latest ETA to the user when they ask or every ~5 min. |
| `· [snapshot Xs elapsed] N done · M in-flight · K queued · F failed` | Every 30s while in-flight | Use these as quick "still alive" pings. |
| `✗ eval-X config run-N  failed: <reason>` | On run failure | Surface immediately to the user — failures often mean config issues (timeout, claude-cli-not-found, grader-no-output). |

**You will be notified automatically when the background task completes** — do NOT sleep, poll, or proactively check on its progress. Continue with other work or respond to the user's questions in the meantime. When the user asks "how's it going?", call `BashOutput(bash_id=...)` to fetch the latest lines and summarize them.

## When the runner completes

The runner's tail of output includes a summary block:

```
────────────────────────────────────────────────────────────────────────
Benchmark complete in 33m14s  (12 ok, 0 failed, 0 skipped)
────────────────────────────────────────────────────────────────────────
  With Skill                   ok 6/6  avg 110.5s, 568k tok total
  Without Skill                ok 6/6  avg 78.2s, 138k tok total
────────────────────────────────────────────────────────────────────────
Wrote benchmarks/<target>/runs/<ts>/benchmark.json
```

Read the final BashOutput and:
1. Quote the summary block to the user
2. Compute and surface the headline `delta.pass_rate` from `benchmark.json` (signed string like `+0.50`)
3. Note any per-eval outliers if `stddev > 0.3`

## Flags (override the defaults when you have a reason)

| Flag | Default | When to override |
|------|---------|------------------|
| `--runs N` | `1` | `2-3` only when measuring variance — N runs are now parallelized across workers, so wall time grows sub-linearly. |
| `--model <id>` | skill frontmatter → `claude-sonnet-4-6` | Cross-model comparison. Accepts `opus`/`sonnet`/`haiku` aliases or explicit `claude-...` IDs. |
| `--grader-model <id>` | same as `--model` | Run the grader at a different tier (rare — pairing them avoids "smart writer judged by dumb grader" artifacts). |
| `--configs with,without` | both | Smoke test one side. |
| `--workers N` | `4` | Drop to `2` when running opus to be kinder to rate limits. For small eval sets bump to `min(total_runs, 8)` so every run lands in the first wave (3 evals × 2 configs × 1 run = 6 → `--workers 6` cuts wall time roughly in half). The runner submits one pool task per (eval, config, run_idx) so workers stay saturated. |
| `--no-isolate-global` | off | Disable auto-hiding of `~/.claude/rules/<basename>.md` and `~/.claude/skills/<name>/` during the run. Default behavior is to move globally-installed copies of the target aside (with crash-proof recovery manifest) so the `without` config is truly without the target. Use `--no-isolate-global` only when you want to measure the target **in addition to** global guidance. |
| `--restore-hidden` | off | Exit after recovering any `.pilot-bench-hidden-*` files left by a crashed prior run (normally swept automatically on every startup). |
| `--timeout <sec>` | `600` | Bump for slow models or large prompts. |
| `--grader-timeout <sec>` | `300` | Bump if `grader-no-output` failures appear. |
| `--output <dir>` | `benchmarks/<target>/runs/<ts>/` | Override when you want a specific output path. |

## Failure handling

When you see `failed.json` referenced (or a `✗ failed:` line):

- `reason: timeout` — bump `--timeout` or reduce `--runs`.
- `reason: no-result-event` — stream-json stream was malformed. Inspect `outputs/transcript.jsonl` for the raw stream.
- `reason: claude-cli-not-found` — the `claude` CLI isn't on PATH. Install Claude Code first.
- `reason: grader-no-output` / `grader-invalid-json` — the grader subagent failed. Retry or bump `--grader-model` a tier.

A few failed runs do not abort the rest of the benchmark — each writes its own `failed.json` and the runner continues. Surface failures to the user but only stop everything if more than half are failing.

## Commit the snapshot

Once the benchmark is stable (you've got a result you trust), commit `benchmarks/<target>/runs/<timestamp>/benchmark.json` as a baseline snapshot. Future runs can compare against it.

## Exit

Go to Step 5 (present findings & iterate).
