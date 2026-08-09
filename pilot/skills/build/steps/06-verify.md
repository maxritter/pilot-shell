## Step 6: Verify Before Handing Back

The judge ruled the criteria. This step checks the things criteria mostly do not: that the suite is green, that the artifact actually runs, that the code behind it is sound, and that the docs did not go stale. Then Step 7 hands back.

**Skip this step entirely when:**

- `PILOT_BUILD_VERIFICATION_ENABLED` is `"false"` — but write a `Verification: disabled (buildWorkflow.verification=false)` row into `## Not Verified` first. Step 7 surfaces it at the approval gate, so a run never reaches `VERIFIED` on switched-off evidence without the user seeing that.
- You arrived from Step 4.6 (blocked on something outside the session) — the artifact is half-built by design.

You still run it at the round-four ceiling: the code is finished even though a criterion is not.

### 6.1 Classify, then do only what applies

| Profile | What changed | What runs below |
|---|---|---|
| **Minimal** | **No code at all** — prose, design, research, docs | 6.6 and 6.7 only |
| **API** | Code with a server or CLI, no UI | Everything except the browser half of 6.4 |
| **Full** | Code with a UI or user-facing entry point | Everything |

Record the profile in one line. Getting this right is what keeps a writing build from paying for a code review.

⛔ **Only Minimal skips the code checks.** Anything that produced code — a CLI, a library, a hook, a script — runs 6.2 (automated checks), 6.5 (independent review), and 6.8 (final regression) in full. The profile scales *how the artifact is exercised*, never whether the code behind it is checked; dropping the reviewer for a CLI build is exactly the weaker-than-`/spec` evidence this step exists to remove.

### 6.2 Automated checks

Run the project's own commands, in order, fixing as you go: **full test suite** → **type checker** → **linter** → **build**. All green before continuing; a failure in a file this run touched is always yours. A pre-existing failure in a file the run never touched gets proven unrelated (name the paths) and recorded in `## Not Verified` — do not go fix the codebase.

Then two sweeps over the diff:

- **Least that works** (`development-practices.md`): an abstraction with one implementation, a dependency the stdlib already covers, boilerplate nobody asked for, config for a value that never changes → fix it.
- **Shortcut debt:** `grep -nE '(#|//) ?SHORTCUT:'` over the changed files. Every marker this run added must name a ceiling *and* an upgrade trigger. List unresolved ones in the report.

Changed production files over 800 lines are worth a split; over 1000, flag it.

### 6.3 Prove the running artifact is the current one

Reuse the target Step 5.1a recorded and re-assert identity as 5.1a describes. Review fixes land after the last judge pass, so check it again after 6.5.

### 6.4 Exercise it

Start it, read the logs for errors and stack traces, and run the primary path with real input. Where the artifact processes external data, fetch that data independently and compare — running without errors is not the same as being right.

**Full profile** additionally walks the user-facing paths in a browser (the ladder from 5.1a), covering the criteria's paths plus the standard edges: empty, invalid, stale, error, boundary. **API profile** stops at the command or endpoint — there is no UI to walk.

### 6.5 Independent review of the code

Whenever the artifact is code — API and Full alike — for whichever toggles are on. The two reviewers are gated independently; enabling one does not require the other.

**Resolve the diff scope once** — never by hand:

```bash
SCOPE=$(~/.pilot/bin/pilot review-scope --slug <slug> --json 2>/dev/null \
  | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)))' 2>/dev/null)
echo "${SCOPE:-UNAVAILABLE}"
```

The `json.load` is a guard: a `pilot` predating the subcommand prints a banner and exits 0, so without it `$SCOPE` becomes that banner. Empty → `git diff HEAD` for uncommitted work, or `git diff <base_ref>...HEAD` (three dots, detected base) on a worktree branch.

**`## Changed Files` is the file list** (4.3). In `working-tree` mode `git add` exactly those paths and nothing else, then check `git status --short --untracked-files=all` — anything dirty outside the ledger is the user's, so leave it unstaged and note it. In `worktree` mode do not stage; a plain `git diff HEAD` there reviews an empty diff.

**Run Step 2.4's reviewer-launch protocol again**, gating the two independently as it does, with these inputs:

| | Native reviewer (`PILOT_CHANGES_REVIEW_ENABLED` ≠ `"false"`) | Codex companion (`PILOT_CODEX_CHANGES_REVIEW_ENABLED` = `"true"`) |
|---|---|---|
| Agent / template | the `changes-review` agent, launched exactly the way 2.4 launches `build-review` on this agent | `changes-review-codex.md` |
| Inputs | changed files from `## Changed Files`, plus `base_ref` and `diff_range` from the resolver, verbatim | `{{CHANGED_FILES}}` from the ledger, `{{BASE_REF}}` from the resolver |
| Ask for | correctness, security, cleanups against the goal | same |
| Once-per-run flag | — | `codex-changes-review-ran-<slug>.flag` |

The Codex companion is a Claude-Code-only feature; on Codex, only the native column applies.

Poll up to 150 iterations here rather than 90 — a code diff takes longer than a criteria read. Launch Codex first so the two overlap.

**Apply findings, lineage first.** A finding on a file outside `## Changed Files` is mention-only whatever its severity — report it, never auto-fix it. For the rest: `must_fix` and `should_fix` now, `suggestion` if quick.

⛔ **Settle every `cannot_verify` finding and `uncertain` truth yourself.** A reviewer scoped to a diff cannot check what lives in unchanged code — silence from it is not a pass. Confirm the requirement holds, or find it missing and treat that as `must_fix`.

**Findings do not spend a round.** Close them here, then re-run Step 5.1 for any criterion whose evidence the fix materially changed, and re-check 6.3. The round budget is for criteria, not for review findings.

If a reviewer produced nothing after one relaunch, continue without it and record the gap in `## Not Verified`.

### 6.6 Documentation

Ask once: did this change something a reader of the docs is told? A public API or flag added, renamed, or removed; documented behaviour changed; a new config field, command, or endpoint; a shifted layout. If yes, update the docs in this same run — grep the docs tree for the symbols the diff touched rather than trusting memory, and check any counts or lists you pass. If genuinely doc-irrelevant, record "no doc impact" so the reader knows it was considered.

### 6.7 Write down what you did not verify

Append a `## Not Verified` section to the Buildout — the profile you skipped work under, any reviewer that did not run, any check that could not be run and why. "None" is a valid answer when it is true. Step 7 quotes this section at the approval gate, so an empty one is a claim.

### 6.8 Final regression

Re-run the suite, type checker, and build one last time. If fixes landed during this step it catches what they broke; if nothing changed it confirms 6.2 still holds.

### 6.9 Write the verification record

Append a `## Verification Record` section to the Buildout. Step 7 refuses to write `VERIFIED` without it, so this is the durable evidence — not the conversation, which a compaction erases.

```markdown
## Verification Record

- Profile: Full
- Live target: Tier 1, `curl http://localhost:41777/` — identity re-asserted before E2E
- Checks: suite 2952 passed · types 0 errors · lint clean · build ok
- Reviewers: changes-review 0 must_fix / 0 should_fix · Codex 4 high, all closed
- Docs: README.md, docs/workflows/build.md — or "no doc impact"
- Regression: re-run green after fixes
```

A Minimal-profile run writes the same section with `Checks: n/a (no code)` — the record always exists, it just says less.

**Done when:** the profile is recorded, everything its row calls for has run, findings are closed, and `## Not Verified` plus `## Verification Record` are both written — then Step 7.
