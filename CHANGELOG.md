# Changelog

Notable changes to QualityLayer and its predecessor, Pilot Shell.

## 12.0.0-beta.16

### New

- While you plan, the agent asks every decision in the chat, including "Is this what you asked for" and "Done means". The App shows only what the open question is about, and an answer you give in the chat settles its item there at once.
- After you approve the Plan, the App opens Implement with one command that starts the build: pick the agent, model, effort and where it starts, then copy it.
- Nothing waits for you while agents build and check. They take the recommended way and note it, and what stays open reaches your final review.
- The agent answers a second opinion's findings itself. You see them as plain lines in one closed row and are asked only what is truly yours to decide.
- New tasks name their files after the step they belong to, from `01-discuss.md` to `05-review.md`, and tasks you already have keep their names.
- Each step page shows the path of its file under the title, with Copy path, Open and Reveal, and the task's other files grouped by step.
- One switch at the end of the step tabs moves between your document and the agent's details, and you can comment on both. Your team now receives the Plan's details and can comment there too.
- When nobody knows an answer, the Plan records it as an unconfirmed assumption, and you can ask the team about it from there.
- The Claude Code progress band and pane use the App's colours, in light and dark terminals, and fit narrow windows.
- A helper that runs far past its time is named, so the agent restarts it instead of waiting for hours.
- `qualitylayer commit slice` checks the exact files it commits, so another session's unfinished work neither blocks a slice nor slips past it.
- Team plans, share links and comments now live in a database in Frankfurt, with an encrypted backup every week to a bucket in the EU.
- `qualitylayer update`, `install.sh` and `install.ps1` check the release's signature as well as its checksums. The installers need `ssh-keygen`, which comes with macOS, Linux and Windows' OpenSSH client.

### Fixed

- Only qualitylayer.dev can grant a paid tier on a machine. An edited local file no longer unlocks Team, and a cancelled licence stops working within 7 days.
- The App no longer says the agent is gone while it is working, and an answer clicked in the App leaves Needs you at once.
- The task page's Approve and Request changes show only while a gate is open.
- An agent can no longer approve its own gate by handing QualityLayer a made-up picker answer: only an answer in the agent's own session record counts.
- The second opinion reads the whole change, also in repositories with encrypted files, split by area when it is large.
- A check whose command could not run now counts as failed and says why, instead of passing.
- A check command the agent corrected during the build now runs, instead of waiting for you to run it.
- Adding tasks to the Plan during Verify takes the build back to Implement by itself, and a check waits for another session's check instead of failing.

### Good to know

- Team plans and share links from the beta were not carried over: the new storage starts empty, so share a plan again to get a new link.

## 12.0.0-beta.15

### New

- Feedback you send from the App now also reaches us by e-mail, so no report waits for someone to open GitHub.

### Fixed

- On Windows with the App installed, `qualitylayer uninstall` now finishes: the small launcher it runs through is moved aside and removed once it closes.

### Good to know

- On beta.14 the App offers this update by itself: choose Restart and update when the sheet appears.

## 12.0.0-beta.14

### New

- Every step has the same layout. A step line says whose turn it is, Needs you holds only what wants a person, and one violet line, Checked by agents, holds what the agents proved.
- Each item has its own two answers. Agree or Change, Looks right or Change, I confirm or Ask the agent to record it, Accept or Fix it.
- Your answers are sent together. The main button reads Approve, or Send 1 change when an answer asks for one.
- The Comments panel lists your drafts, answered threads and your team's comments.
- Discuss shows the agent's question in the App. You still answer it in Claude Code or Codex.
- The Plan puts your decisions first: the mockup, each engineering decision as a diagram you can comment on, and what the agent decided for you. A revised Plan marks what changed since your review.
- Implement shows the slices side by side, with a bar per task, what each agent is doing and the commit of every finished slice.
- Implement lists the agent's own choices as Decided by the agent while building, with Fine and Ask why.
- A new task or file outside the Plan waits for your answer on that slice only. The other slices keep building.
- A checkpoint that fails twice stops the build. You choose Try another fix, Change the Plan or Continue anyway.
- Verify is a live checklist. Every check is listed from the start and fills in as it runs.
- Checking agents record each result with `qualitylayer verdict`, and `qualitylayer attest` keeps what you confirmed in your own words.
- After two tries at checking, the task stops and you choose Check once more, Take it as it is or Stop the task.
- Only you can confirm. A point no agent may settle, such as a call to a live service, is an item in Review and no longer fails a check.
- Review opens on what needs you: screens to look at, Found while checking, and the agent's choices during the build.
- Changes are grouped by the task that made them. Files from other sessions' commits are named and left out of the pull request.
- The Approve menu ships the change: Approve and open a pull request, Approve only, or Copy the git commands. QualityLayer never merges.
- Home covers all your tasks: what needs you, what runs, and what shipped with its cost.
- ⌘K finds tasks, jumps to a setting and filters by need, agent or project. The bell is gone.
- The App opens where you left it: the same task, step and scroll position.
- Slack tells you when someone answers your question. Remind works at most once every 4 hours, and each member has a switch for Slack messages to them.
- The Slack card names the teammates it could not find, and errors say what to do next.
- Outside reviewers comment only. Their comments reach you as an item under Needs you.
- Notifications follow your setting. They cover a Plan or review that waits, a task that stops or ships, a teammate's question, a reminder and an answer.
- Settings has four tabs: Workflow, Licence, Team and About.
- Updates arrive quietly. The App downloads once a day in the background and shows Update ready in the sidebar, with the release notes.
- qualitylayer update prints the same release notes.
- Feedback is one click in the sidebar. It sends your text, screenshots and diagnostics you can read first to a private issue, and qualitylayer feedback does the same.
- Setup is one checklist, with one row for any other coding agent.
- The share page reads like the App. Its tabs are named Discuss, Plan and Build, and the mockup and diagrams are drawn.
- The Cost panel names each agent by its work, with time next to cost.
- A second opinion runs by itself on a risky Plan. Say "no second opinion" to skip it for one task.
- Fable 5.1 is offered wherever a Claude model is chosen.
- Select all fills a group in one click.

### Fixed

- Reopening the App no longer lands on Home.
- Review showed 0 files changed and no gh when the App started from the Dock. The App now reads your login shell's PATH.
- The step tabs and Stay in the browser work in a browser tab.
- Implement no longer shows the start card after the build, and the Verify step bar shows only on Verify.
- Slice text no longer shows raw Markdown.
- An agent can no longer answer your stop for you or pass a point only you can confirm. An answered stop reads Sent, and Implement no longer turns amber for a stop in Verify.
- The share page no longer labels tabs with file names or shows the mockup as a file path.
- The Cost panel lists every agent that worked.
- Live checks an agent runs while planning save their output.
- Your approval stands when a document, mockup or evidence file changes after the review opened.
- Checks that passed are not run again because the Plan or the build log changed.
- Checking agents skip files that Git ignores and files that are generated.
- After a fix, only the failed check and what the fix touched are checked again.
- A computer whose Pilot Shell trial ran out starts a full 7-day trial.

### Good to know

- This is a beta from the `dev` branch.
- Settings has fewer choices: no Links setting, no checkpoint switch, no token budget. Old settings files keep loading.
- Moving from Pilot Shell asks nothing. Its tools and memories stay.
- Licence keys come from Polar.sh only. A key from an earlier provider no longer activates.
- The App never starts, pauses or stops an agent. With no agent attached, your answers wait.
- Updates install only when you choose Restart and update. Agents keep working through it.
- Feedback and usage events never include code, plan or document text, task titles, repository or branch names, or file paths.

## 12.0.0 betas before beta.14

### One flow: Discuss → Plan → Implement → Verify → Review

- Every task, a feature or a bug fix, takes the same five steps. The agent discusses the task with you until it understands what you want and what done means (a bug is reproduced first), then writes one Plan: the decisions, a mockup for a UI task, the slices and the checks that prove them.
- One planning decision: you approve the Plan. Implement then starts in a fresh session with one prompt, `/ql implement <task>` in Claude Code or `$ql implement <task>` in Codex, with the recommended model beside it. The second decision is the final review of the change.
- The flow scales by itself: helpers research the code when there is much to trace, build slices side by side when the Plan has several, and run a checkpoint after each slice the Plan marks risky. A task can ask for more or less with `qualitylayer task override` (`+security`, `-checkpoint`, `+second-opinion` and others).
- QualityLayer runs the checks the Plan names and records each result (`qualitylayer check slice <n> | task T<n> | all`); a failed check goes to a fix helper.
- Verify: a polish helper, and a security review when the change crosses a trust boundary, go over the finished change side by side; then one judge, which did not write the code, rules on it with the recorded checks as evidence.
- No separate lane for small changes and no roles: a small change takes the same five steps, with fewer helpers. The per-step switches, the automatic approval of early gates and the role question are gone.
- Settings › Workflow: the helper and judge model for each agent, the second opinion (off unless you turn it on), a checkpoint after every slice, and a soft token budget per task.
- A Cost view in the App shows what a task used per step and per helper, read from the agents' transcripts on your computer. Figures are estimates at list price; a model without a confirmed price shows its tokens only. Passing the budget is said once, and the work goes on.
- Task folders of the earlier flow (`00-frame.md`, `README.md`, `02-design.md`, `03-outline.md`, `04-build.md`) are no longer read: only tasks with `00-discuss.md` appear and finish.
- On a Mac the installer puts the App in `/Applications` when you may write there (an administrator can, without a password), else in `~/Applications`, and removes a copy an earlier install left in `~/Applications`.
- The App's icon has its own light, dark and tinted looks on macOS 26 and later, so the mark stays readable when the Mac shows its icons dark or tinted.

### Also in QualityLayer 12

- Replace the earlier tool bundle with one compiled binary and agent skills.
- Add an independent review by the other agent (Claude Code ↔ Codex) and built-in communication between agent sessions.
- Record every surprise as a note on its task, and amend the approved Plan mid-build with `qualitylayer plan amend` without reopening a gate; the final review lists every amendment and the Plan's diff.
- Give each task the contract it names (`qualitylayer card`), and show the Plan's contracts mapped to their tasks.
- Show Implement, Verify and Review in the App as one timeline with a live strip, verdict cards per round, and a pull-request-style diff review with line comments.
- Add Team features: share a task with your team for their feedback, and send a time-limited link to reviewers outside the team, both from one Share control; their comments reach your agent as advice. Settings shows the team's seats, members and shared links. Solo licences see the controls locked with an upgrade link, and the team service enforces the same gate.
- Keep the workflow's phase texts inside the binary: an agent receives only its task's current step.
- Work on the branch and worktree you have checked out: QualityLayer no longer creates a `ql/<task>` branch, and never switches or merges branches or creates worktrees.
- Use the shared monochrome, blue/amber design for the website, the App and the documentation, with saved light/dark mode and preferences.
- Update the website, its interactive App demo, the documentation and the README.

## Earlier Pilot Shell notes (previously unreleased)

### Bug fixes

- Restore Claude Code's Manual model-switch handoff: approved `/spec` plans now stop before implementation, wait for `/model`, and continue only after exact `resume`. Plan Approval disabled and orchestration-lane runs remain autonomous, while Codex keeps its continuous active-model flow.
- Repair inline Claude Code tool and thinking details after native auto-updates replace Pilot's patched binary. Session startup now reapplies a locally cached, checksum-verified patch kit for the next session, with `pilot repair-display` as an explicit fallback.
- Preserve Impeccable's intentional Claude Code and Codex variants during repository asset synchronization instead of treating their provider-native commands and interaction contracts as a merge conflict.

## [11.0.1] - 2026-09-08

### Bug fixes

- Stop automatic memory from spending millions of background tokens on routine tool traffic. Normalize Pilot's `rtk` command forms, filter read-only retrieval and orchestration events across Claude Code and Codex, coalesce live arrivals, use larger batches, bound captured payloads, and cap provider inference concurrency fairly across sessions.
- Make capture accounting truthful. Persist every provider request—including skips and failures—with provider, model, input, cached-input, output, batch, duration, and outcome fields; attribute a batch's discovery tokens only once; expose queued, processing, failed, rejected, oldest-pending, and 24-hour usage diagnostics.
- Prevent shared-memory retention from resurrecting archived records. Preserve imported identities independently of retained observations, apply retention before import, self-repair partially applied database migrations, and retain pre-v11 observations and generated-wrapper payloads exactly.
- Eliminate Chroma storms. Index imported and newly captured observations in serialized document batches, keep memory bounded while batching, and delete only the vector documents an observation actually created instead of generating hundreds of speculative IDs per row.
- Repair parallel-session correctness. Update provisional sessions when asynchronous initialization arrives, preserve established metadata, quarantine deterministic poison events after finite retries, increase the bounded burst allowance, and keep oversized evidence as useful head/tail excerpts instead of silently dropping it.
- Remove duplicate Pilot commands from mixed Codex hook entries while preserving third-party hooks, preventing duplicate summaries and session finalization after upgrades.
- Keep Open Knowledge Format support for explicit, editable knowledge through `get_knowledge` and `save_knowledge`, while removing OKF synchronization from routine capture/status/import work. One-time legacy-wrapper recovery remains automatic and idempotent.
- Show each memory's local creation date and time in both the overview card and detail view, instead of collapsing a busy day to the date alone.
- Restore native task tracking in current agents. Claude Code receives its supported task/todo environment flags, while Codex 0.152.0 and newer receive `tools.update_plan.enabled = true` only when the user has not explicitly opted out; older Codex versions remain untouched.
- Put `~/.pilot/bin` on login/non-interactive shell paths as well as interactive shells, so Claude Code tool calls can find `rtk` and other Pilot binaries in devcontainers and IDE-launched sessions.

### Verification

- Added regression coverage for queue pressure, RTK/tool filtering, batching, concurrency, token telemetry, retries, session-init races, shared-memory retention, Chroma write/delete bounds, Codex hook merging, OKF separation, and migration repair.
- Added an installed-artifact acceptance that runs real Claude Code and Codex sessions concurrently, migrates pre-v11 data, exercises OKF create/read/update through MCP, verifies relevant recall and bounded files, and restarts to prove zero duplicate import or Chroma work.

## [11.0.0] - 2026-09-07

Pilot Shell 11 updates the engineering harness for current Claude Code and Codex, adds automatic memory across both agents, and retires Pilot Bot. This is a major release: review the changes below before upgrading.

### Breaking changes and migration

- **Pilot Bot is retired.** The `pilot bot` command, background bot runtime, channel tasks, scheduler integration, and five bot skills have been removed. Existing private bot data and `JOBS.yaml` files are preserved, but Pilot no longer runs those jobs. Move any jobs you still need to another scheduler before upgrading.
- **Memory retrieval is on demand.** Pilot no longer injects a history digest at every session start or refreshes generated `CLAUDE.md` memory sections. Native agent context remains available; agents query Pilot when they need additional project history. Custom integrations that depended on automatic digest injection should use the memory MCP search and retrieval tools.
- **Manual model switching is the default.** New or unset configurations keep model choice with the user. Existing explicit Automated and Off settings retain their meaning, including migration from the older boolean setting.

### Automatic memory across Claude Code and Codex

- Capture useful decisions, discoveries, and fixes in the background with either provider. Automatic selection uses available low-cost models and can fall back when authentication, quota, or temporary provider failures prevent capture.
- Preserve pending evidence through retries, cancellation, worker restarts, and invalid responses. Observations and queue acknowledgements commit together, with bounded queues and explicit capture status.
- Accept valid multi-observation responses containing separate XML fences and skip markers, fixing batches that previously remained deferred. Malformed or incomplete responses still leave their evidence pending.
- Search local history and shared knowledge together without requiring a model call or a working vector service. Lexical matches, semantic matches, filters, and pagination share one result path.
- Hide proven local/shared duplicates in lists and search while keeping both historical IDs directly readable.
- Keep automatic shared findings in `.pilot/memories/<author>/<YYYY-MM-DD>.jsonl`. Recover unchanged generated Markdown copies into those daily archives before removing the copies; preserve edited knowledge and conflicting records.
- Support explicitly maintained Markdown knowledge with source references, revision conflict protection, validation, and local indexing. Backups include personal knowledge, checkout mappings, and pending capture evidence alongside history.
- Keep Team sharing as a single project switch. Shared files travel through the Git work users authorize; local memory remains usable when sharing or provider access is unavailable.
- Filter routine memory-tool feedback out of automatic capture, and show local and shared findings with their sources in the Console.

### Workflows, rules, and reviews

- Review and update the rules, skills, and reviewer instructions for GPT-6 Astra, Claude Opus 5, and Claude Fable 5.1. Instructions follow the actual runtime's tools, permissions, and model capabilities.
- Execute clear requests directly, preserve native Plan and Goal choices, and use structured questions and review results where the runtime supports them.
- Connect explicit Pilot planning to Claude's native plan approval lifecycle. Capture the accepted draft after approval, preserve native permission boundaries, and handle the current Claude response format.
- Carry lane identity and durable review handles through phase handoffs and resumed work. Revalidate changed plans and preserve independent review results across calls.
- Use existing behavioral coverage and proportionate verification; remove arbitrary context limits, repetitive instructions, and unsupported tool assumptions.

### Hooks and tool output

- Keep diagnostic and routing advice private and nonblocking, with repeated reminders limited per session.
- Prefer Claude's native file-reading tools for inspection and returned background task handles for output collection.
- Preserve Claude's permission decision when RTK rewrites a command. Codex uses its own supported rewrite contract.
- Bound checker subprocesses, run Go diagnostics at package scope, recognize existing integration coverage, and preserve intentional Unicode in source and content.
- Show the reported reasoning effort beside the model in the statusline; omit unknown values.

### Installation and upgrades

- Preserve user-owned Codex rules and configuration while refreshing managed assets. Remove retired managed bot assets without deleting unrelated local skills.
- Apply a checksum-verified display patch to supported native Claude Code installations for detailed tool calls, subagent prompts, and thinking summaries. Patch a copy first, retain the original, and leave unsupported binaries unchanged. Patched macOS binaries are ad-hoc signed; the documented restorer can restore an unchanged Pilot-patched binary.
- Reset verbose display once after successful patching, while preserving later user changes and Claude's own updater.
- Keep local `.pilot/` state and private working documents out of the public Pilot Shell repository.

Run `pilot update` to upgrade, then start a fresh Claude Code or Codex session to load the refreshed hooks and instructions. Claude Code and Codex themselves continue to update through their own installers.

## [9.17.0] - 2026-08-06

### Features

- License-key authenticated subscription portal, configurable worktrees

## [9.16.1] - 2026-08-06

### Bug Fixes

- Set site titles from measured search volume, clear Trivy HIGH findings

## [9.16.0] - 2026-08-03

### Bug Fixes

- Make team-remote push work when the Claude config dir is absent

### Features

- Support custom CLAUDE_CONFIG_DIR and automate team memory sharing

## [9.15.0] - 2026-08-01

### Bug Fixes

- Pin Trivy to a release that still exists

### Features

- Share project memories with your team through the repo

## [9.14.0] - 2026-07-25

### Features

- Adapt Pilot Shell to Opus 5 and consolidate skills, rules, and hooks

## [9.13.2] - 2026-07-22

### Bug Fixes

- Poll teammate feedback for shared requirements and worktree plans

## [9.13.1] - 2026-07-21

### Bug Fixes

- Resolve code review diff scope through a single resolver

## [9.13.0] - 2026-07-16

### Features

- Three-way Model Switching mode (Automated default) replacing slot-pin machinery

## [9.12.1] - 2026-07-14

### Bug Fixes

- Model Switching bug in Pilot Launcher for specific session ID cases
- Update Spec Mode Guard to work with Fable Model Switch

## [9.12.0] - 2026-07-14

### Features

- Window-scoped Fable/Opus model switching for /spec

## [9.11.0] - 2026-07-13

### Features

- Overhaul /spec, /prd, /fix skills and rules; harden worktree sync

## [9.10.2] - 2026-07-10

### Bug Fixes

- Run model switching at 1M with a fixed Opus/Sonnet pair

## [9.10.1] - 2026-07-08

### Bug Fixes

- Restore bypassPermissions after plan-mode exit

## [9.10.0] - 2026-07-07

### Bug Fixes

- List taskkill in knip ignoreBinaries

### Features

- Add /ask-codex skill for headless Codex orchestration

## [9.9.1] - 2026-07-06

### Bug Fixes

- Verify /spec planning-leg model and raise Codex AGENTS.md size cap

## [9.9.0] - 2026-07-03

### Bug Fixes

- Check the full unreleased commit range for the release trigger

### Features

- Per-workflow changes-review modes, uv config isolation, AFK-timeout guard

## [9.8.1] - 2026-07-02

### Bug Fixes

- Deny premature ExitPlanMode before spec approval and harden Codex MCP config healing

## [9.8.0] - 2026-07-01

### Features

- Sonnet 5 support, always-1M model aliases, remove Context Window selection

## [9.7.3] - 2026-06-30

### Bug Fixes

- Exclude terminal-status specs from active-specs top bar

## [9.7.2] - 2026-06-26

### Bug Fixes

- Improvements for Codex Spec Mode

## [9.7.1] - 2026-06-26

### Bug Fixes

- Heal duplicate keys and tables in Codex config.toml env-block merge

## [9.7.0] - 2026-06-23

### Features

- Integrate impeccable design detector and design-quality rules

## [9.6.0] - 2026-06-17

### Bug Fixes

- Unify context window to single opusplan control and harden .NET hooks
- **tdd:** Fix C# logic-free heuristic for generic methods and event accessors
- Harden .NET file checker (code-review findings 1,2,3,6,7)
- Address .NET support code-review findings

### Documentation

- Sync marketing site language support with .NET/C# addition
- Correct dotnet format mischaracterization in hook docs
- **rules:** Add C# naming convention to testing RED step

### Features

- Add .NET/C# support to file-quality & TDD hooks 
- Optimize .NET dev support (rule scoping, TDD detector, single-file checker)

### Styling

- Apply ruff format to .NET test files

## [9.5.1] - 2026-06-16

### Bug Fixes

- Add configurable code-review effort setting

## [9.5.0] - 2026-06-12

### Bug Fixes

- Remove process-global fs mocks from console tests, add pre-commit mock-hygiene and knip gates

### Features

- Replace changes-review subagent with built-in /code-review skill on Claude Code

## [9.4.0] - 2026-06-09

### Features

- Support for Mythos Class series with Fable 5 and Bugfixes

## [9.3.3] - 2026-06-09

### Bug Fixes

- Fixing CICD failure
- Charset edit-scoping, reviewer subagent 1M fix, installer/console cleanups

## [9.3.2] - 2026-06-05

### Bug Fixes

- Bugfixes for Spec, Hooks and Statusline

## [9.3.1] - 2026-06-03

### Bug Fixes

- Make 200k/1M models selectable for Opusplan and other bugfixes

## [9.3.0] - 2026-06-03

### Features

- Automate model switching via opusplan and make Pilot admin-only

## [9.2.4] - 2026-06-02

### Bug Fixes

- Improve Usage Savings Calculation
- Remove unused code for Console, Launcher and Installer

## [9.2.3] - 2026-06-02

### Bug Fixes

- Fix flaky getChildProcesses non-Windows enumeration tests
- Add CC to Dev Container and fix Codex Reviewer Agents

## [9.2.2] - 2026-06-02

### Bug Fixes

- Add missing Worker Console Update
- Changes to Codegraph for Codex

## [9.2.1] - 2026-06-01

### Bug Fixes

- Check for Pilot Shell updates every 30 min and on session start

## [9.2.0] - 2026-06-01

### Bug Fixes

- Scope Trivy SARIF gate to CRITICAL,HIGH severities

### Features

- Codex CLI parity, automated /fix reviews, and console security & cross-session hardening

### Miscellaneous

- Updated Website

## [9.1.3] - 2026-05-28

### Bug Fixes

- Add Opus 4.8 support across statusline, usage pricing, and benchmark

## [9.1.2] - 2026-05-28

### Bug Fixes

- Suppress stale update notification once user has upgraded past cached pilot_latest

## [9.1.1] - 2026-05-28

### Bug Fixes

- Populate statusline update-check cache via detached refresh subprocess

## [9.1.0] - 2026-05-28

### Features

- Enable Codex CLI as a first-class agent alongside Claude Code 

## [9.0.6] - 2026-05-26

### Bug Fixes

- Resolve activation endpoint and improve error handling 

## [9.0.5] - 2026-05-22

### Bug Fixes

- Kill ~/.claude/pilot/ — hooks → ~/.claude/hooks/, scripts+ui → ~/.pilot/

## [9.0.4] - 2026-05-22

### Bug Fixes

- Save settings not working

## [9.0.3] - 2026-05-22

### Bug Fixes

- Suppress installer confirm prompt during `pilot update`

## [9.0.2] - 2026-05-22

### Bug Fixes

- Cut console observation noise — skip exploration tools, read-only Bash, raise SDK recording bar
- Use `stty sane` to fully restore terminal before banner prompt

## [9.0.1] - 2026-05-22

### Bug Fixes

- Restore terminal before Enter prompt after pilot update; suppress statusline cost/branch on Max plan

## [9.0.0] - 2026-05-22

### Features

- Model switching for /spec, collapse model selection to /model

## [8.10.5] - 2026-05-21

### Bug Fixes

- License grace periods, scanner fail-open, ctx-mode timeouts, /s CSP

## [8.10.4] - 2026-05-18

### Bug Fixes

- Drop unsupported vercel.json comment + harden logger file fallback
- Harden shared-feedback flow end-to-end against malicious input
- Whitelist feedback fields and cap planPath length (defense-in-depth)

### Styling

- Align pilot-shell.com task card with Console layout

## [8.10.3] - 2026-05-18

### Bug Fixes

- Resolve share-id duplication across spec view/review tabs

## [8.10.2] - 2026-05-18

### Bug Fixes

- Multi-user spec review approve/deny, live SSE updates, section parity, durability hardening
- Stacked layout for share UI in annotation panel, copy via ctrl+c fix

## [8.10.1] - 2026-05-15

### Bug Fixes

- Persistent share-id with singleton lock, unified UI across view/review on Specs and Requirements, manual fetch-feedback button

## [8.10.0] - 2026-05-15

### Features

- Multi-user spec feedback polling with persistent share links

## [8.9.0] - 2026-05-13

### Bug Fixes

- Add missing UI file

### Features

- Spec workflow overhaul, share spec/prd URL shortener, claude auto-update  

## [8.8.0] - 2026-05-12

### Bug Fixes

- Drop pilot/plugin.json from semantic-release prepareCmd

### Features

- Agents dashboard support + Semble code search + LSP marketplace 

## [8.7.1] - 2026-05-08

### Bug Fixes

- Download installer/upstreams.yaml in install.sh bootstrap

## [8.7.0] - 2026-05-07

### Bug Fixes

- Don't run subscription-aware migrations in unit tests
- Use default-foreground ANSI so splash and spinner stay readable in light-mode terminals

### Features

- Supply-chain monitoring + credential scanning + console settings

## [8.6.2] - 2026-05-06

### Bug Fixes

- Always check for updates on launch and tighten install hint
- Re-check for updates after 30 minutes when no update is cached

## [8.6.1] - 2026-05-06

### Bug Fixes

- Show changelog in launcher splash when update is available

## [8.6.0] - 2026-05-06

### Features

- Per-phase 1M context selection for /spec workflow
- Configurable Console port, pilot update CLI, test parsimony, narrow-terminal UI

### Miscellaneous

- New logos, navy theme, hero polish
- Optimize mobile hero — bigger slogan, smaller buttons, cleaner rhythm
- Add Blog button next to Documentation in hero + README nav
- Unify slogan to 'How real engineers run Claude Code' + bump deps
- Launch blog with 63 migrated posts, design polish, brand CTAs
- Add Ahrefs Web Analytics tracking script to marketing site and docs
- SEO crawl fixes — sitemap canonicals + doc meta descriptions
- Optimize website images and accessibility per PageSpeed audit

## [8.5.3] - 2026-05-04

### Bug Fixes

- Prevent 1M context error when extendedContext disabled, optimize site, improve skills

## [8.5.2] - 2026-04-30

### Bug Fixes

- Tighten /fix and refine spec/prd/create-skill/setup-rules skills

## [8.5.1] - 2026-04-29

### Bug Fixes

- Optimize Context Usage for Rules, Memory and MCPs

## [8.5.0] - 2026-04-29

### Features

- Bugfix workflow redesign with new /fix command 

### Miscellaneous

- Change to Vercel Config
- Updated Website SEO
- Updated Readme

## [8.4.1] - 2026-04-27

### Bug Fixes

- Native usage analytics, ccusage scrub, hook + rules + site updates

## [8.4.0] - 2026-04-24

### Features

- Add /benchmark skill and evaluation framework

## [8.3.0] - 2026-04-23

### Features

- Cross-platform statusline usage, in-process skill build, console task cards

## [8.2.4] - 2026-04-21

### Bug Fixes

- Prevent vector-db disk exhaustion + model routing UI + project-scoped annotations
- **hooks:** Make SessionEnd fully non-blocking so harness cancellation can't leak workers

## [8.2.3] - 2026-04-17

### Bug Fixes

- Drop skill banner, normalize step heading levels across workflow skills

### Miscellaneous

- Reframe customization docs and rework site hero/pillars

## [8.2.2] - 2026-04-17

### Bug Fixes

- Updated inconsistent steps in spec workflow

## [8.2.1] - 2026-04-17

### Bug Fixes

- Removed static effort for skills/commands to adjust based on global
- Customization overrides, skill decomposition polish, generated artifacts untracked

## [8.2.0] - 2026-04-16

### Features

- Customization packs, Opus 4.7 support, and Codex bugfixes

## [8.1.0] - 2026-04-15

### Features

- Add session details with JSONL stats, cost calculation, and enhanced UI

## [8.0.10] - 2026-04-14

### Bug Fixes

- Codegraph native SQLite repair, /spec new-branch option, session prompt display

## [8.0.9] - 2026-04-13

### Bug Fixes

- Deduplicate plugin extensions across marketplaces and add progressive dashboard loading

## [8.0.8] - 2026-04-13

### Bug Fixes

- Add Chrome DevTools MCP plugin, update browser automation to 4-tier, fix auto-mode flag and docs

### Miscellaneous

- Updated Demo Gif
- Updated Readme

## [8.0.7] - 2026-04-10

### Bug Fixes

- Restore dom globals after terminal-preview-xss test to prevent portal ssr leak
- Stop incomplete child_process mocks poisoning CI test runs
- Add tool output compression + sandboxed content cards to Usage view
- Hook venv sync, console annotation writes, codegraph native sqlite

## [8.0.6] - 2026-04-09

### Bug Fixes

- Walk up directory tree for git repo detection in CodeGraph guard

## [8.0.5] - 2026-04-09

### Bug Fixes

- Skip CodeGraph indexing in non-git directories

### Miscellaneous

- Updated Readme
- Improved Readme

## [8.0.4] - 2026-04-09

### Bug Fixes

- Improved PRD and Spec Sharing / Annotation UI on pilot-shell.com
- Improved Dependency Installation Speed for Installer and Updater

## [8.0.3] - 2026-04-09

### Bug Fixes

- Improved Code Reviewer Stability, Codegraph Usage and Context Mode

### Miscellaneous

- Updated specifications images

## [8.0.2] - 2026-04-09

### Bug Fixes

- Console dashboard overhaul — 2x2 recent cards, usage model breakdown, session filtering, spec tab consistency

## [8.0.1] - 2026-04-08

### Bug Fixes

- Use correct CronCreate parameter name (cron, not schedule) in bot skills

## [8.0.0] - 2026-04-08

### Bug Fixes

- Pin Bun to 1.3.11 (1.2.15 lacks compression APIs, latest is unstable)

### Features

- Add Pilot Bot — persistent automation agent with scheduled tasks, background jobs, and optional Telegram
- Complete Console overhaul — v8.0.0 

## [7.11.4] - 2026-04-07

### Bug Fixes

- Console UI overhaul — dashboard sessions card, sidebar worker status, motion system, skeleton loaders

## [7.11.3] - 2026-04-06

### Bug Fixes

- Replace isomorphic-dompurify with dompurify to fix CI ESM incompatibility
- Whitelist web-search-agent in tool_redirect hook for /prd deep research

### Miscellaneous

- Add Homebrew to Linux Dev Container Setup

## [7.11.2] - 2026-04-02

### Bug Fixes

- Pass chromium argument to playwright-cli install-browser and increase timeout
- Symlink RTK to ~/.pilot/bin/ for PATH availability on Linux

## [7.11.1] - 2026-04-02

### Bug Fixes

- Add playwright-cli as 3-tier browser tool, optimize viewer bundle, improve installer UX

## [7.11.0] - 2026-04-01

### Features

- Rename /shape to /prd, add tiered research, fix Console PRD view, restructure docs

## [7.10.2] - 2026-04-01

### Bug Fixes

- Filter Pilot skills from extensions listing and fix CI test failures
- Migrate commands to skills format

## [7.10.1] - 2026-03-31

### Bug Fixes

- Shorten share URLs ~25% by streamlining encoding pipeline

### Miscellaneous

- Optimize website image performance
- Fix self-referencing SHARE_BASE_URL constant on /shared page

## [7.10.0] - 2026-03-31

### Bug Fixes

- Security audit hardening across console, launcher, and installer
- Improve Codex CLI invocation and reviewer agent prompting 

### Features

- Codex adversarial reviewers, spec sharing, and Console improvements 

## [7.9.0] - 2026-03-30

### Features

- Add E2E encrypted spec sharing with collaborative annotation feedback

## [7.8.5] - 2026-03-30

### Bug Fixes

- Added sudo prompt for npm if needed

## [7.8.4] - 2026-03-30

### Bug Fixes

- Use AskUserQuestion at code review gate so stop guard allows exit

## [7.8.3] - 2026-03-30

### Bug Fixes

- Prefer Claude Code Chrome over agent-browser for browser automation

## [7.8.2] - 2026-03-30

### Bug Fixes

- Agent-browser ARM64 Linux support, dynamic devcontainer naming
- Ensure codegraph is in PATH via ~/.pilot/bin symlink

## [7.8.1] - 2026-03-28

### Bug Fixes

- Replace mock.module with spyOn for logger in timeline-formatting tests
- Enhanced CI debug for logger test — check test file content and single-file run
- Add debug step to release.yml (runs on main, not dev)
- Add debug step to diagnose CI logger.formatTool failure
- Pin Bun version to 1.3.9 in CI workflows
- Skip quality hooks when project has no linter config
- Replace codebase-memory-mcp with CodeGraph across project
- Add Claude CLI flag passthrough and relax /spec permission mode enforcement

### Miscellaneous

- Improved Website Content
- Updated Pricing Section and Readme

## [7.8.0] - 2026-03-27

### Features

- Plan annotations, code review mode, E2E test scenarios in spec workflow 

## [7.7.6] - 2026-03-25

### Bug Fixes

- Replace broken auto-mode probe with retry-on-failure

## [7.7.5] - 2026-03-25

### Bug Fixes

- Safe fallback for --enable-auto-mode on older Claude Code versions

## [7.7.4] - 2026-03-25

### Bug Fixes

- Enable auto mode for team/enterprise/api users

## [7.7.3] - 2026-03-25

### Bug Fixes

- Improve light mode readability and console UI fixes

## [7.7.2] - 2026-03-22

### Bug Fixes

- Add compatibility with Telegram Plugin

### Miscellaneous

- Updated Readme and Website

## [7.7.1] - 2026-03-20

### Bug Fixes

- Add APM format support for team remote extensions, fix category counts, edit modal height, remote content loading, and team gate

### Miscellaneous

- Updated Website and Readme

## [7.7.0] - 2026-03-19

### Features

- Redesign extensions page with color-coded categories, project deletion, and console improvements 

## [7.6.5] - 2026-03-18

### Bug Fixes

- Shorten full model IDs in statusline display
- Use env vars for extended context instead of model name suffix

## [7.6.4] - 2026-03-18

### Bug Fixes

- Optimize rules by converting reference-heavy content to on-demand skills

## [7.6.3] - 2026-03-18

### Bug Fixes

- Add 1M extended context toggle, config migration, and update skillshare extras docs

## [7.6.2] - 2026-03-18

### Bug Fixes

- Improve create-skill with eval testing, description optimization, and writing guidance

## [7.6.1] - 2026-03-18

### Bug Fixes

- Add Remote Control documentation and installer improvements

### Miscellaneous

- Updated Demo Gif with Latest Changes

## [7.6.0] - 2026-03-16

### Features

- Rename /learn to /create-skill and /sync to /setup-rules

## [7.5.11] - 2026-03-16

### Bug Fixes

- Statusline restyle, session reactivation, memory cleanup, context cache preservation

## [7.5.10] - 2026-03-15

### Bug Fixes

- Block plan mode and Explore agent, consolidate hook tests, add /clear instruction

### Miscellaneous

- Updated Demo gifs

## [7.5.9] - 2026-03-15

### Bug Fixes

- Integrate codebase-memory-mcp and sync all documentation

## [7.5.8] - 2026-03-15

### Bug Fixes

- Add RTK CLI installation and standardize dependency UI

## [7.5.7] - 2026-03-14

### Bug Fixes

- Add trivy security scan to pre-commit hook and fix undici CVEs
- Auto-detect context window size from Claude Code statusline

## [7.5.6] - 2026-03-13

### Bug Fixes

- Use IS_SANDBOX=1 instead of permission patching for root support

## [7.5.5] - 2026-03-13

### Bug Fixes

- Support running as root in containers and remove remote fetch/browse UI
- Enable git worktrees and reviewer subagents by default

## [7.5.4] - 2026-03-12

### Bug Fixes

- Clean up memory observer session files from claude -r resume list

## [7.5.3] - 2026-03-12

### Bug Fixes

- Warn instead of block Agent sub-agent calls, allow /spec reviewers silently

## [7.5.2] - 2026-03-12

### Bug Fixes

- Prevent Vercel auto-deploy from overwriting git-crypt CI/CD deployments

## [7.5.1] - 2026-03-12

### Bug Fixes

- Share page detection, sync/collect buttons, skillshare via brew, README cleanup

## [7.5.0] - 2026-03-12

### Features

- Replace Teams with Skillshare-based Share system, streamline spec workflow and hooks 

## [7.4.7] - 2026-03-10

### Bug Fixes

- Improvements for learn and sync commands

## [7.4.6] - 2026-03-10

### Bug Fixes

- Add spec workflow toggles, console settings UI, dark theme, and site redesign

## [7.4.5] - 2026-03-09

### Bug Fixes

- Added settings toggle for subagents and improve their token usage

## [7.4.4] - 2026-03-09

### Bug Fixes

- Optimized runtime of Plan and Spec Reviewer subagents

## [7.4.3] - 2026-03-09

### Bug Fixes

- Enhance Changes tab with git operations, AI commit messages, and model routing

## [7.4.2] - 2026-03-09

### Bug Fixes

- Quality Improvements to Agents, Rules and Spec-Commands

## [7.4.1] - 2026-03-09

### Bug Fixes

- Improve /sync with quality audit phase, consistent structure, and optional dependencies
- Auto-Install Native Claude Code if not already installed on system

## [7.4.0] - 2026-03-08

### Features

- Add Changes view with git diff viewer to Console

## [7.3.2] - 2026-03-08

### Bug Fixes

- Improved /sync Command

## [7.3.1] - 2026-03-08

### Bug Fixes

- Usage summary dashboard showing wrong costs and add token counts

## [7.3.0] - 2026-03-08

### Features

- Replace Vexor with Probe for code search 

## [7.2.2] - 2026-03-06

### Bug Fixes

- Re-Enabled auto-updater for Claude Code in Settings

## [7.2.1] - 2026-03-06

### Bug Fixes

- Redesign bugfix /spec flow with root cause investigation and make reviewers mandatory

### Miscellaneous

- Improve install section after-install guidance
- Streamline landing page sections and remove Under the Hood

## [7.2.0] - 2026-03-05

### Features

- New Teams asset sharing dashboard for skills, rules, commands and agents 

## [7.1.5] - 2026-03-05

### Bug Fixes

- Make hooks read-only, stop blocking plan mode, silence hook errors, optimize git statusline

## [7.1.4] - 2026-03-05

### Bug Fixes

- Clean stale session state on /clear and prevent reviewer skip at high context

## [7.1.3] - 2026-03-02

### Bug Fixes

- Add hash redirect so console dashboard loads without explicit /#/ fragment

## [7.1.2] - 2026-03-02

### Bug Fixes

- Strengthen spec stop guard to prevent premature stops during /spec

## [7.1.1] - 2026-03-02

### Bug Fixes

- Prevent worker from stopping when another session is still active
- Optimize commands and rules for 52% token reduction without quality loss

## [7.1.0] - 2026-03-01

### Features

- Merge 5 spec sub-agents into 2 unified agents for optimized token usage

### Miscellaneous

- Add team rollout section with contact links to README

## [7.0.6] - 2026-02-26

### Bug Fixes

- Update vault workflow for sx 0.11.1+ and improve site/installer/console

## [7.0.5] - 2026-02-26

### Bug Fixes

- Remove aggressive comment stripping from quality hooks and preserve user permission settings
- Mock all subprocess-calling functions in unit tests

## [7.0.4] - 2026-02-25

### Bug Fixes

- Right-size bugfix spec workflow and improve site/installer/console

### Miscellaneous

- Add positioning statement to hero section

## [7.0.3] - 2026-02-25

### Bug Fixes

- Add bugfix verify phase, Linux Homebrew fallback, and site/console improvements

### Miscellaneous

- Restructure docs page TOC into grouped categories and trim verbose sections
- Trim site sections, reorder layout, and add compatibility FAQ
- Streamline README structure and reduce visual clutter

## [7.0.2] - 2026-02-24

### Bug Fixes

- Vexor test mocking, site responsiveness, and README consolidation
- Add vexor runtime check to installer and update dependencies

### Miscellaneous

- Update logo images and fix footer tagline wrapping

## [7.0.1] - 2026-02-24

### Bug Fixes

- Update version to 7.0.0 in console and plugin packages

## [7.0.0] - 2026-02-24

### Features

- Rename Claude Pilot to Pilot Shell

## [6.11.0] - 2026-02-24

### Features

- Add bugfix spec workflow and viewer enhancements 

## [6.10.3] - 2026-02-23

### Bug Fixes

- Enhance rules, agents, and workflow prompts for better review handling and debugging

## [6.10.1] - 2026-02-22

### Bug Fixes

- Minimize external data to license key and fingerprint only
- Simplify Vercel rewrite rule to fix SPA routing 404s

### Miscellaneous

- Improve mobile responsiveness for hero buttons, pricing cards, and workflow diagram
- Add Vercel ignored build step to skip redundant deployments
- Replace hero Get Started button with View on GitHub and Read Documentation

## [6.10.0] - 2026-02-22

### Features

- Add goal verification sub-agent, documentation pages, and installer fixes

## [6.9.4] - 2026-02-21

### Bug Fixes

- Trigger release for AlmaLinux git prerequisite fix
- Install git via system package manager before Homebrew on RHEL-based distros
- Add uninstall script for clean Pilot removal

### Miscellaneous

- Updated Demo Video Link
- Updated Readme
- Added Demo to Readme and Website

## [6.9.3] - 2026-02-20

### Bug Fixes

- Detect native Windows in install.sh and guide users to WSL2 or Dev Container

## [6.9.2] - 2026-02-20

### Bug Fixes

- Improve vault command with correct client IDs and disable non-Claude clients
- Migrate from deprecated mcp-cli to ToolSearch for MCP tool access

## [6.9.1] - 2026-02-20

### Bug Fixes

- Make vexor model pre-download best-effort during installation
- Use sys.executable instead of uv in spec_validators tests
- Consolidate test infrastructure, harden parallel spec workflows 

## [6.9.0] - 2026-02-19

### Bug Fixes

- Grant prepare-release job write permission for semantic-release dry-run
- Remove Dependabot configuration
- Resolve Trivy security scan findings and add pre-commit hook
- Improved MCP-CLI system as CC default

### Features

- Implement spec/release-security-hardening

## [6.8.3] - 2026-02-19

### Bug Fixes

- Create ~/.pilot/bin directory before writing mcp-cli script
- Remove mcp-cli dependency, refactor console infrastructure, and add real-time notifications
- Real-time notification system with SSE and auto-notify on plan transitions

## [6.8.2] - 2026-02-18

### Bug Fixes

- Global extended context toggle, compact settings UI, and hook improvements 

## [6.8.1] - 2026-02-18

### Bug Fixes

- Go/gopls auto-install, npx zod peer dep fix, and update prompt TTY handling

## [6.8.0] - 2026-02-18

### Features

- Model selection settings, Apple Silicon Vexor acceleration, and worktree sync fixes 

## [6.7.7] - 2026-02-17

### Bug Fixes

- Improve network connectivity for corporate proxy and firewall environments

## [6.7.6] - 2026-02-17

### Bug Fixes

- Improve ChromaDB reliability and harden worktree lifecycle

### Miscellaneous

- Update bug report section in README

## [6.7.5] - 2026-02-17

### Bug Fixes

- Harden worktree lifecycle against data loss and improve project config

## [6.7.4] - 2026-02-17

### Bug Fixes

- Use --autostash on rebase during worktree sync
- Prevent stash data loss during worktree sync

## [6.7.3] - 2026-02-17

### Bug Fixes

- Improve worktree isolation and multi-session reliability

### Miscellaneous

- Updated Installer Instructions for Local Mode

## [6.7.2] - 2026-02-17

### Bug Fixes

- Add retry logic to installer network operations

### Miscellaneous

- Updated Demo Gif

## [6.7.1] - 2026-02-17

### Bug Fixes

- Move settings to global ~/.claude/settings.json with SSL and platform fixes

## [6.7.0] - 2026-02-16

### Features

- Effective context display, non-destructive installer, and npm sudo handling

## [6.6.0] - 2026-02-16

### Features

- Compaction-based context preservation, branding overhaul, and bugfixes 

## [6.5.9] - 2026-02-15

### Bug Fixes

- Prevent installer hang on Homebrew installation and improve UX

### Miscellaneous

- Re-stage worktree files with correct filters

## [6.5.8] - 2026-02-15

### Bug Fixes

- Remove unreliable session ID cross-check in context monitor
- Use runtime container detection in installer, improve UX and polling

## [6.5.7] - 2026-02-14

### Bug Fixes

- Use uv tool install for vexor to work on macOS and dev containers

## [6.5.6] - 2026-02-14

### Bug Fixes

- Clarify existing project support, streamline installer UX

## [6.5.5] - 2026-02-14

### Bug Fixes

- Consolidate Search into Memories, add Vault view, remove custom modes, improve hooks

## [6.5.4] - 2026-02-14

### Bug Fixes

- Stop deleting native Claude Code binary, fix spec UI staleness, improve TDD enforcer

## [6.5.3] - 2026-02-13

### Bug Fixes

- Add pre-commit hook for console build artifacts and rebuild bundles

## [6.5.2] - 2026-02-13

### Bug Fixes

- Add .cursor/ to .gitignore and update vault docs
- Improve vault workflow and usage tab performance

## [6.5.1] - 2026-02-13

### Bug Fixes

- Clean up orphaned pending messages to prevent unbounded queue growth

## [6.5.0] - 2026-02-13

### Features

- Add Usage tab with cost/token tracking

## [6.4.5] - 2026-02-12

### Bug Fixes

- Allow background Bash tasks for long-running processes like dev servers
- Install Playwright system dependencies after browser download
- Optimize subagent models and reduce token waste in review agents
- Run plan verification agents in parallel with run_in_background
- Fix npx MCP server pre-caching leaving incomplete installations

### Miscellaneous

- Update website and README messaging and FAQ transparency

## [6.4.4] - 2026-02-12

### Bug Fixes

- Fix npx package cache detection for versioned packages like open-websearch@latest
- Pre-cache npx MCP servers during install and reorder post-install steps

## [6.4.3] - 2026-02-12

### Bug Fixes

- Improve installer reliability, console UX, and vault auth flow

## [6.4.2] - 2026-02-12

### Bug Fixes

- Add cryptography dependency to pilot wrapper for trial activation

## [6.4.1] - 2026-02-12

### Bug Fixes

- Improve License Activation during Trial

### Miscellaneous

- Restore STANDARDS in agent roster, remove from hero, add sessions command to docs
- Remove STANDARDS from hero section, consolidate footer links, restore lightweight website deploy

## [6.4.0] - 2026-02-12

### Bug Fixes

- Consolidate website deployment into release pipelines and fix changelog duplication
- Prevent changelog duplication from squash merge commits

### Features

- Parallel multi-agent verification, standards migration, blog & dashboard

### Miscellaneous

- Updated Readme header

## [6.3.3] - 2026-02-11

### Bug Fixes

- Auto-start trial when no license found instead of prompting for key

### Miscellaneous

- Updated changelog for 6.3.2

## [6.3.2] - 2026-02-11

### Bug Fixes

- Various improvements to quality in spec workflow, rules and hooks
- Fix for trial endpoint so users can reactivate if license file gots corrupted
- Correct seat display for solo/team licenses and enrich activation output
- Replace seats with activations, refactor hooks and spec workflow
- Prevent incremental review from overwriting initial PR analysis

### Miscellaneous

- Add model routing docs and Pilot CLI reference to README and website

## [6.3.1] - 2026-02-11

### Bug Fixes

- Fixing Stale Context Monitor on session restart and statusline
- Update spec implementation agent to produce better quality
- Replace raw Python worktree calls with pilot CLI commands in spec instructions

### Miscellaneous

- Fix team checkout seat selection and update changelog

## [6.3.0] - 2026-02-11

### Bug Fixes

- Updated models for commands and agents
- Add MCP server smoke-testing step to sync command
- Resolve console test failures from parallel execution and mock contamination
- Show server-side license dates and seat count in banner
- Promote parallel execution as primary implement strategy and add license display
- Resolve trial activation failures caused by www subdomain redirects
- Sandbox support improvements and UX polish
- Move worktree question to beginning of spec flow
- Add staleness check to context-pct.json cache
- Move licensing to Polar.sh
- Simplify dashboard layout and add delta-aware PR reviews
- Make worktree isolation optional and fix worker startup crash
- Remove working-directory from deploy step to prevent doubled path
- Remove dead code and simplify auth module
- Migrate service integrations and enrich system metadata
- Simplify Vercel deploy to single step (fixes spawn sh ENOENT)
- Add npm install to deploy workflow and handle init timeout rejection
- Migrate to playwright-cli, backport console stability fixes, and harden CI/CD

### Features

- Add parallel execution, goal verification, and workflow improvements
- Add git worktree isolation for /spec workflow

## [6.2.2] - 2026-02-08

### Bug Fixes

- Resolve signal handler deadlock and improve session cleanup

### Miscellaneous

- Small changes to Website and Readme

## [6.2.1] - 2026-02-07

### Bug Fixes

- Move project selector to sidebar and add clear scope indicators across all views
- Restore emojis and add missing launcher features to docs

### Documentation

- Transform website and README with comprehensive system documentation

### Miscellaneous

- Add /vault and /learn to install section, remove remaining count, add custom LSP note
- Remove hardcoded counts and improve quality-focused messaging
- Add /vault to installer post-install and statusline tips, remove language servers stat
- Update branding to new slogan across entire codebase
- Restructure README and website to eliminate duplicate content
- Convert favicon from JPG to PNG for browser compatibility
- Reorder README sections
- Simplify license section in README
- Add license and changelog links to README and website footer
- Update license support contact and remove version line

## [6.2.0] - 2026-02-06

### Bug Fixes

- Resolve continuation path bug, clean up console UI, and add Vexor search backend
- Remove remote mode, extract worker daemon, add offline grace period, and refine hooks/UI
- Address PR #45 review findings and refine console UI
- Clean stale npm temp dirs before Claude Code install and block Explore agent
- Split spec command into phases, add design skill, and optimize skill descriptions
- Remove dead code, unused imports, and legacy integrations

### Features

- Add multi-session parallel support with isolated session state

### Miscellaneous

- Update site tagline
- Update site meta tags

## [6.1.1] - 2026-02-05

### Bug Fixes

- Add console branding and update settings defaults

### Miscellaneous

- Add pricing to website

## [6.1.0] - 2026-02-05

### Bug Fixes

- Rebuild console assets with latest changes
- Address code review findings
- Stale session cleanup, context hook, install docs, and CI pipeline
- Continue reworking towards Pilot Shell Console

### Features

- Pilot Console improvements and enhanced development workflow
- Rebrand memory system to Pilot Console

### Miscellaneous

- Fix changelog generation to prepend-only, restore clean v6 changelog

## [6.0.13] - 2026-02-04

### Bug Fixes

- Prevent blocking on worker restart and shutdown

## [6.0.12] - 2026-02-04

### Bug Fixes

- Show combined changelog for all versions during update
- Remove aggressive process cleanup on startup

## [6.0.11] - 2026-02-04

### Bug Fixes

- Improve hook performance and memory viewer facts display

### Documentation

- Updated Demo Gif

## [6.0.10] - 2026-02-04

### Bug Fixes

- Remove Settings tab from UI, update messaging, improve installer description

## [6.0.9] - 2026-02-03

### Bug Fixes

- Release pipeline now updates files for manual triggers
- Parallel downloads, box alignment, TypeScript errors, remove analytics

## [6.0.8] - 2026-02-03

### Bug Fixes

- Add memory system source from other repo
- Added grep-mcp server

## [6.0.7] - 2026-02-03

### Bug Fixes

- Move worker lifecycle to hooks, simplify launcher cleanup

## [6.0.6] - 2026-02-02

### Bug Fixes

- Improved Plan and Spec Verifier Flow

## [6.0.5] - 2026-02-02

### Bug Fixes

- Add demo gif to README
- Make sx vault setup mandatory when sx installed but not configured

## [6.0.4] - 2026-02-02

### Bug Fixes

- Reduce GitHub API calls and simplify installer cleanup

## [6.0.3] - 2026-02-02

### Bug Fixes

- Shorten banner tagline to fit within box width
- Remove claude alias and update branding to Production-Grade Development

## [6.0.2] - 2026-02-02

### Bug Fixes

- Preserve user's .claude/skills folder and clean up empty rules/custom

## [6.0.1] - 2026-02-02

### Bug Fixes

- Remove duplicate sync step in release workflow
- Resolve release pipeline failure and remove codepro fallbacks
- Emphasize running installer in project folder and remove git setup step
- Add backwards compatibility for --restart-ccp argument

### Documentation

- Simplify install command for easier copying

## [6.0.0] - 2026-02-02

### BREAKING CHANGES

- Major workflow changes for Pilot Shell v6.0
- Project renamed from Claude CodePro to Pilot Shell

### Features

- Add multi-pass plan verification and installer auto-version
- Renamed Project to Pilot Shell

### Bug Fixes

- Update documentation to use claude command instead of pilot alias
- Improve installer location and sync workflow
- Make SEO descriptions consistent with new messaging
- Update favicon to local file and fix remaining old messaging in index.html
- Address PR review findings for installer robustness
- Unquote multi-argument variables in install.sh
- Add multi-pass verification with spec-verifier agent
- Add sx tool and update rules paths
- Improve worker cleanup and installer reliability
