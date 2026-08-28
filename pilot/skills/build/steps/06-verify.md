## Step 6: Verify Before Handing Back

The judge ruled the criteria. This step checks the things criteria mostly do not: that the suite is green, that the artifact actually runs, that the code behind it is sound, and that the docs did not go stale. Then Step 7 hands back.

⛔ **This step is what makes an unsupervised run safe to accept.** Nobody reviews the result before it is called done — no approval gate, no sign-off — so the evidence written here is the entire basis for `VERIFIED`. Every shortcut taken in this step is a claim the user has no way to check. Run it in full, and where you cannot, say so in `## Not Verified` rather than quietly narrowing what "verified" means.

**Skip this step entirely when:**

- `PILOT_BUILD_VERIFICATION_ENABLED` is `"false"` — see 6.0, and note the run **cannot reach `VERIFIED`**.
- You arrived from Step 4.6 (blocked on something outside the session) — the artifact is half-built by design.

You still run it at the round-four ceiling and at 5.5's unachievable exit: the code is finished even though a criterion is not.

### 6.0 Verification switched off means unverified, not verified anyway

When `PILOT_BUILD_VERIFICATION_ENABLED` is `"false"`, the user has turned off the only evidence that would have justified `VERIFIED` on an unsupervised run. So the run ends **honestly unverified** rather than certified on nothing:

1. Write `Verification: disabled (buildWorkflow.verification=false) — no checks, no review, no regression run` into `## Not Verified`.
2. Leave `Status: COMPLETE` and re-register it. `COMPLETE` is exactly true: every task is ticked, the criteria were judged, and verification did not happen.
3. Touch the hand-back sentinel so the session can stop, since nothing will write `VERIFIED`:

   ```bash
   BUILD_SESS="${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-${PILOT_SESSION_ID:-default}}}"
   mkdir -p "$HOME/.pilot/sessions/$BUILD_SESS" && touch "$HOME/.pilot/sessions/$BUILD_SESS/build-handback-pending"
   ```

4. Go to Step 7 and lead the report with it: the criteria passed, and **nothing checked the code behind them**.

⛔ **Do not write `VERIFIED` on this path**, and do not run a lighter improvised subset in its place. The toggle says the user wants the run to stop at the criteria; the honest name for that outcome is not "verified".

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

Append a `## Not Verified` section to the Buildout — the profile you skipped work under, any reviewer that did not run, any check that could not be run and why. "None" is a valid answer when it is true. Step 7 quotes this section verbatim in the report and refuses to write `VERIFIED` without it, so an empty one is a claim — and with no human gate downstream, it is the only place a gap in the evidence gets declared.

### 6.8 Final regression

Re-run the suite, type checker, and build one last time. If fixes landed during this step it catches what they broke; if nothing changed it confirms 6.2 still holds.

### 6.9 Write the verification record

Append a `## Verification Record` section to the Buildout. Step 7 refuses to write `VERIFIED` without it, so this is the durable evidence — not the conversation, which a compaction erases.

```markdown
## Verification Record

- Profile: Full
- Live target: Tier 1, `curl http://localhost:41777/` — identity re-asserted before E2E
- Commands:
  - `uv run pytest -q` — pass (2952 passed)
  - `basedpyright launcher` — pass (0 errors)
  - `ruff check .` — pass
  - `npm run build` — pass
- Reviewers: changes-review 0 must_fix / 0 should_fix · Codex 4 high, all closed
- Docs: README.md, docs/workflows/build.md — or "no doc impact"
- Regression: re-run green after fixes
```

⛔ **Every command is recorded as the command plus `pass` or `fail`, never as prose.** A verification record listing only passing commands is the *only* shape a `VERIFIED` run may have — so a red command is not summarised, softened, or moved into a sentence; it holds the run open until it is fixed or disclosed in `## Not Verified` with the failure still visible as a failure. This is the specific way an unsupervised loop launders a failure into a pass, and the structured pair is what makes the honest path the easy one.

A Minimal-profile run writes the same section with `Commands: n/a (no code)` — the record always exists, it just says less.

### 6.10 The bar `VERIFIED` is measured against

Step 7.4 refuses `VERIFIED` unless every layer below either has real evidence in `## Verification Record` or has a row in `## Not Verified` saying what could not be run and why. There is no third state: a layer you did not think about is a layer you cannot certify.

| Layer | Evidence that counts | Not applicable when |
|---|---|---|
| **Criteria** | Every `- [x]` ticked by a judge pass with evidence pointed at (5.1) | Never — a run with an unticked criterion is not Complete |
| **Suite** | Full test run, exit 0, counts recorded — not the touched files, the suite | Minimal profile (no code) |
| **Types · lint · build** | Each command run, exit 0 | Minimal profile, or the project has no such command (name which) |
| **Runs at all** | The artifact started, primary path exercised with real input, logs read (6.4) | Minimal profile |
| **User-facing paths** | Browser E2E per `browser-automation.md`: snapshot → click → re-snapshot, on a target proven current (6.3) | API or Minimal profile — no UI exists |
| **Code review** | `changes-review` findings collected and closed, `cannot_verify` items settled by you (6.5) | Minimal profile, or the toggle is off — then it is a `## Not Verified` row |
| **Docs** | Files updated, or "no doc impact" recorded (6.6) | Never — the question is always answered |
| **Regression** | Suite, types, and build re-run green after the last fix landed (6.8) | Minimal profile |

⛔ **"The criteria covered that" is not evidence for these layers.** Criteria rule the artifact; these rule the thing behind it. A run whose criteria all passed and whose suite is red is a failing run — fix it, do not reconcile it.

⛔ **A `## Not Verified` row is a disclosure, not a waiver.** Writing one is correct when a check genuinely cannot run here; using one to skip a check that *could* have run is how an autonomous run launders a shortcut into a certificate.

**Done when:** the profile is recorded, everything its row calls for has run, findings are closed, every layer above is either evidenced or disclosed, and `## Not Verified` plus `## Verification Record` are both written — then Step 7.
