# Interaction Rethink build plan — beta.25

Build from this branch's skeleton commit. The frozen Interaction Rethink design and build brief dated 6 October 2026 are approved. This is a plan and mounting skeleton, not the completed redesign. All paths below are relative to `qualitylayer/` unless a root path is explicit.

## Invariants and integration seams

- Three places: the live top bar, Now on the left, work on the right. Exactly one amber outlined Your turn card; other surfaces use a small dot that jumps to it.
- Questions are independent batch members. Answer in any order; save each answer immediately, continue independent agent work, publish every visible count in one optimistic update, roll back errors, offer Undo for 5 seconds.
- Reuse `core/task/point-confirmations.ts`. It already stores agreements per normalized text and brings back only the changed point with `Item.changedFrom`. Do not replace it with a section hash. Keep legacy task layouts.
- Real signals determine status. An alive process or a live waiting question prevents a SessionEnd hook from declaring the agent stopped. Working can coexist with open questions. Quiet starts after 2 minutes; guidance after 15 minutes; neither makes a running agent stopped.
- An item is saved, picked up, then acted on: show the state the files prove. Never claim a UI click reached an agent merely because the fetch succeeded.
- `src/ui/interaction/TaskWorkspace.tsx` mounts Now and work. `shell/TaskTopBar.tsx`, `turn/YourTurn.tsx`, `docs/DocumentWorkspace.tsx` and the three `*Work.tsx` surfaces are mounted in TaskView. `shell/ShellExtras.tsx` is mounted in App for the bell and shell overlays. Stubs retain current children.
- Each step enables its own new layout only after its Now component works: `TURN_LAYOUT_READY`, `PLAN_TURN_READY`, `STEPS_TURN_READY`. The shared TaskView then suppresses legacy attention controls for that step. Docs owns suppressing the page's duplicate index/approval; steps owns removing duplicate stop controls in its content. No readiness flag may hide an unimplemented action.
- `turn/projection.ts` is consumed by App and TaskView. Turn implements one optimistic publication there; shell consumes it for Home/nav/title/bell. Keep delivery receipts after an item leaves the card.
- `docs/mode.ts` is consumed by App to collapse the left list for full-size reading. Docs implements that store; shell adds the icon rail. Full-size documents keep the right sidebar and never require browser full screen.
- All new lane APIs are pre-mounted under an authenticated namespace. `server/interaction.ts` composes four adapters asynchronously, allowing each to read its runtime via `api.locate(ctx, task.id)` without editing shared routing. The task interaction read uses the existing detail coalescer. Unknown facts remain null. Capability flags are explicit constants in the owning adapter, not guessed from non-empty arrays.

## Frame → code and data

| Frame | Owner | Rendering files, existing reuse | Data |
| --- | --- | --- | --- |
| 0a | all; turn owns the common card | `interaction/TaskWorkspace.tsx`, `shell/TaskTopBar.tsx`, `turn/YourTurn.tsx`, `shell/AgentTurn.tsx` | `InteractionSnapshot`, `Item`, live signals, immediate receipts |
| 1a | shell | `Home.tsx`, `shell/ShellExtras.tsx`, `Sidebar.tsx`; reuse Home quick answers | tasks, open turn items, notices, running signals, shipped facts |
| 1b | shell | same Home, `shell/AgentTurn.tsx` | no open items; current work and next ask; no amber empty card |
| 1c | shell | Home and new `shell/HomeFacts.tsx` | `HomeFacts`, task stage buckets, period spending and shipped duration |
| 1d | shell | `Sidebar.tsx`, `kit/CommandBox.tsx`, new `shell/ProjectFilter.tsx` | project/agent counts; one shared project filter scopes nav, Home, bell |
| 2a | turn | `turn/YourTurn.tsx`, new `turn/QuestionBatch.tsx`, `turn/DiscussWork.tsx`, `DiscussPage.tsx`, `FocusQuestion.tsx`, `AnsweredMarkers.ts` | `QuestionBatch`, `QuestionPointLink`, choices/grades/evidence, answered questions, per-point agreement |
| 2b | turn; shell supplies agent turn | same Discuss; `shell/AgentTurn.tsx` | answer receipts, rewriting points, live work, `AgentTurnStep[]`, next ask |
| 3a | docs | `docs/PlanTurn.tsx`, `docs/PlanWork.tsx`, `step-page/PlanningParts.tsx`, `PlanBody.tsx`, `timeline/PlanView.tsx` | Item answers, changedFrom/digest, agreements from turn, designs, engineering decisions, gateId and reviewer result |
| 3b | docs | PlanWork and AgentTurn | partial slices, preserved agreement, helpers and next approval |
| 4a | steps | `steps/StepTurn.tsx`, `steps/StepWork.tsx`, `timeline/ImplementPage.tsx`, `step-page/BuildParts.tsx` | slices/tasks/checkpoints, held addition and affected slice, progress, build comments, prerequisites |
| 4b | steps | same build plus AgentTurn | completed slices, current task/TDD phase, changes/diff, check facts |
| 4c | steps | StepTurn, `ImplementStart.tsx` | implementStart, StartContext, workflow defaults, copied command and actual session attach |
| 5a | steps | StepTurn, `timeline/VerifyPage.tsx`, `step-page/CheckParts.tsx` | `PointProof`, expected/happened/tried, check evidence, capped stop, acceptance second confirmation |
| 5b | steps | StepWork, VerifyPage, AgentTurn | live checklist per point, fixing round, independent checker, quality pass |
| 6a | steps | StepTurn, `timeline/ReviewView.tsx`, `ChangesByTask.tsx`, `FilesChanged.tsx`; docs approval menu | review, PointProof/files/slices/screens, personal confirmation, deviations, gate and ship choice |
| 6b | steps | same Review, AgentTurn | changesRequested sent/picked/done, affected points, kept confirmations |
| 7a | shell | `shell/TaskTopBar.tsx`, `status/StatusPill.tsx`, `live-status.ts`, new `shell/StatusPanel.tsx` | `AgentStatus`, `BackgroundAgent[]`, live signals, open items, existing cost API |
| 7b | shell | same panel | alive process, lastActivity, quiet duration, actual long-running tool; show guidance at 15 min |
| 7c | shell | same panel, resume command | process gone, no alive ask; saved answers, stop time, one CLI continuation command |
| 8a | shell | new `shell/Notifications.tsx`, ShellExtras | `Notification[]`, exact item targets, batch id, open/settled state and project filter |
| 9a | all | canonical `src/interaction/contracts.ts`, four server adapters | the ten data rows: liveness/current words → shell; batch/point link/agreement → turn; helpers/next ask/notifications → shell; designs → docs; proof/change by point → steps. Shell owns burst-event query starvation in hooks.ts. |
| 10a | all | checklist below; no feature may disappear | 76 rows, each with a responsible lane |
| 11a | docs | DocumentWorkspace, new `docs/DocumentHeader.tsx`, `reader/DocReader.tsx`, `reader/DocOutline.tsx`, `sidebar/RightSidebar.tsx`, `kit/CommentsPanel.tsx`, `AskParts.tsx` | document content, document mode, outline, comments/threads, team replies/tallies, agreements/gate; compact Now from turn/docs |
| 11b | docs | RightSidebar, new `docs/FilesTab.tsx`, `sidebar/FileActions.tsx`, `sidebar/ReaderBar.tsx` | task.files/docs, step/audience grouping, selected file, guarded record/doc/open APIs |
| 11c | docs | `design/DesignsTab.tsx`, `design/TaskDesign.tsx`, `design/DesignPreview.tsx` | TaskDesigns and project designs, file/title/author/update/thumb, comment pins |
| 11d | docs | `design/DesignPage.tsx`, `DesignFrame.tsx`, `DesignComments.tsx`, DocumentWorkspace | sandboxed design page, zoom/jump/full screen, theme/viewport controls, pin coordinates and comment receipts |
| 12a | docs owns menus; shell/steps own their surfaces | `docs/TaskMenu.tsx`, DocPathChip, CostPanel, UpgradePopover; shell CommandBox/Settings/Updates/Trouble; steps ImplementStart and approval actions | existing guarded task/share/open/cost APIs; reopen route from steps; current configuration/licence |
| 12b | each lane for its surface; shell coordinates tabs | four lane CSS files; YourTurn first; shell phone navigation | same data/actions at 390px; work, Comments, Files reachable by tabs; preserve focus |

The frozen design's note that TaskView passes no question handler is stale: this branch passes `questionActions` to FocusQuestion. Extend and verify it. The design's section-hash agreement note is also stale: the per-point store exists. Do not reimplement either from that note.

## Data contract and exact routes

The exact TypeScript declarations are committed in **`src/interaction/contracts.ts`**; that file is the contract authority. Do not create parallel wire types. Existing types are reused by import (Question, AnsweredQuestion, Item, ItemAnswer, LiveSignals, Comment, Design, DocEntry, Person). All times are epoch milliseconds; `null` means unknown or unavailable, never zero cost or zero elapsed time. Task ids are `project~slug` and must be URL encoded.

| Contract | Required meaning |
| --- | --- |
| `QuestionBatchInput`, `BatchQuestionInput` | batch id; stable question id, question, choices, recommended index; optional existing context/gate/hold metadata; required `points: number[]` of Done means numbers. An intake can use an empty list until points exist. |
| `QuestionBatch`, `QuestionPointLink`, `BatchAnswer` | full batch with asking agent/session/time, N independently open Question records, point links; answer names both batch and question id, then choice/text/unsure/more. Never answer the first question just because it is first. |
| `PointAgreement` | current point text/hash, agreed text/hash/time and open/agreed/changed; storage remains point-confirmations. Read changedFrom, preserve unchanged agreements across renumbering and retries. |
| `DeliveryReceipt`, `TurnSnapshot` | saved/picked-up/acted, three times and real agent reply; batch/questions/answered/links/items/agreements/receipts. This is the common source for optimistic counts. |
| `AgentState`, `AgentStatus`, `ShellSnapshot` | exactly working/waits-for-you/quiet/stopped/step-done; plain doing words, signals, lastActivity, blocked and open count separately, resume command. Refusal and permission stay separate items/details, not extra states. |
| `BackgroundAgent`, `AgentTurnStep` | stable id/parent, role research/design/building/checking/review/other, subject/state/start/end/doing; done/now/next steps from recorded work, never fabricated progress. |
| `Notification`, `ItemTarget` | stable id, project/time, target task/step/item/view/thread, open/settled/settledAt, batch id; resolve with item, not an independent dismiss counter. One system notification per new batch, not each question or progress tick. |
| `HomeFacts`, `HomePeriod` | timezone; today/week/month from/to boundaries; shipped task ids/times/cost/duration, shipped-only cost, all agent spending, median and fastest duration; task ids by each of the five steps. Week begins Monday, calendar month, local zone. Unattributable cost is null, not a summed guess. |
| `DocumentMode`, `CommentThread`, `TeamReply`, `DocsSnapshot` | fullSize/audience/sidebar/selectedThread; anchored thread with original Comments, replies with app/agent/slack provenance, resolution, explicit delivery timing and optional team tally; document entries and Design index. Full-size mode is local UI state, not a server write. |
| `PointProof`, `StepsSnapshot` | point outcome/state, expected/happened/tried, evidence/files/slices; accepted remains distinct from passed, only-you is not an automated pass. |
| `InteractionSnapshot`, `InteractionCapabilities` | version 1, taskId, four snapshots and explicit supported capabilities. Skeleton exports current singleton question, current answers/items/doc list/signals, with unfinished fields empty/null and capability false. |

`GET /api/tasks/:id/interaction` works now and returns `{ok:true, interaction: InteractionSnapshot}`. No new fields are forced on the existing Api mocks/demo. `ui/api.ts` exports `interactionApi` separately; its `taskRoute<T>` and `shell<T>` support the routes below. All routes use the same cookie/token, Host/Origin and entitlement guards as existing routes. Implement handlers validate JSON, current gate/id/digest, archive/owner state and bounded sizes; stubs return HTTP 501 with `error.code=not_implemented` and lane name. Never leave a stub behind a working-looking control.

| Route | Request/result | Owner/status at skeleton |
| --- | --- | --- |
| `POST /api/tasks/:id/interaction/turn/batch` | `QuestionBatchInput` → `{batch: QuestionBatch}` | turn; 501 |
| `POST .../turn/answer` | `BatchAnswer` → `{answer: AnsweredQuestion, receipt: DeliveryReceipt}` | turn; 501 |
| `POST .../turn/undo` | `{batch,id,answerAt}` → `{batch: QuestionBatch}`; compare answerAt to avoid undoing a newer correction | turn; 501 |
| `POST .../turn/item` | `ItemAnswerRequest` → `{item: Item,receipt: DeliveryReceipt}`; null answer reopens a single point, seen protects stale wording | turn; 501; Plan/Review reuse |
| `GET .../turn/receipts` | `{receipts: DeliveryReceipt[]}` | turn; 501 |
| `GET /api/interaction/turn/home/:project` | `{turn: TurnSnapshot}` | turn; 501; intake batches before a task exists |
| `POST /api/interaction/turn/home/:project/batch` and `/answer` | same input and result as task batch/answer | turn; 501 |
| `GET /api/interaction/shell/notifications?project=&agent=` | `{notifications: Notification[]}` | shell; 501 |
| `GET /api/interaction/shell/home?project=&agent=&timezone=` | `{facts: HomeFacts}` | shell; 501; cache cost reads off the render critical path |
| `GET /api/tasks/:id/interaction/shell/status` | `{shell: ShellSnapshot}` | shell; 501 |
| `GET .../docs/threads` | `{threads: CommentThread[]}` | docs; 501 |
| `POST .../docs/thread` | `{doc,quote,item?,remark,thread?}` → `{thread: CommentThread}` | docs; 501; local write, use existing comments storage |
| `POST .../docs/resolve` | `{thread}` → `{thread: CommentThread}` | docs; 501 |
| `GET .../steps/proof` | `{proof: PointProof[]}` | steps; 501 |
| `POST .../steps/reopen` | `{note,gateId}` → new Review gate/receipt; only after approved Review, preserves history | steps; 501; risky, report if no safe existing path |

Keep the working existing routes: `GET /api/tasks/:id/doc/:name`, `/record?path=`, `/artifact/:name`, `/evidence/:name`, `/cost`, `/changes`, `/changes/file?path=`; `POST /open` with `{path,how}` through its allowlist; `PUT /comments` with `{doc,comments}`; `POST /comments/build`, `/review`, `/asks`; `/question/answer`, `/question/cancel`, `/question/change` for legacy singleton compatibility; `POST /gate` with decision/gateId/without/ship; `/accept`, `/needs/:task/set`, `/start`; share/link/archive/delete. Existing `/items/answer` accepts only stop items in this branch: do not use it for per-point Agree and assume it landed. Turn's new item route must extend core behavior safely.

Designs already work through `GET /api/tasks/:id/designs` and `/api/projects/:id/designs`, the scoped file/thumb/open routes, and POST scoped comments/resolve. Docs reuses these, their sandbox/bridge and their update index; no production or Slack writes in verification.

### CLI and agent delivery

Turn extends the existing **question command** rather than adding a top-level dispatcher: `qualitylayer question ask --batch '<QuestionBatchInput JSON>'` and `qualitylayer question ask --batch-file <path>` both enqueue atomically and return immediately with ids and current receipts. Support `--home` for intake. Preserve existing singleton ask/wait callers. Reject duplicate ids, malformed/oversize choices, stale gate ids and ambiguous answer identities without partial writes.

Use a lock and atomic storage in the task runtime, never the real HOME. Add `question-batches.json`; migrate/read legacy `question.json` without dropping an open question. `core/task/question.ts` owns the current single-question projection and answer-history compatibility. A batch is not an `ask` heartbeat claiming to block while its agent is working. Track actual blocking separately.

`qualitylayer question poll [--batch <id>]` returns undelivered answers/corrections/more requests plus receipts without blocking. `qualitylayer next` uses the same `takeMeanwhile` delivery path. Each answer must be handed once and be durable across server/agent restart; delivery does not wait for the last answer. The agent reads at every independent-work boundary, folds answers into its work, and resolves the associated records with a real reply. More is per question and must not remove the other open questions. Undo or Change produces a correction even after initial delivery; never erase an already acted-on answer silently.

Turn changes **all relevant** phase/skill wording: intake, Discuss feature/bugfix, Plan including chat_review and second opinion, answer/team-ask, capped, house style and the embedded skill. Required instruction: “Ask all independent questions you can ask now in one batch, with a recommendation and the Done means point each settles. Keep working on what does not depend on an open answer. Read new answers before each dependent step. Ask a follow-up batch only when the answers expose another decision. Never answer for the person.” Chat ends with exactly “👉 Your answer is needed in the QualityLayer App.” Never print a localhost address in chat. A final approval is still gated on unsettled items; batching may not auto-approve it.

Agreements use the existing point-confirmation store and normalized words, with immediate delivery records; retain each prior agreement instead of overwriting all drafts. Free planning comments still explicitly say “goes with your approval”; the gate delivers them via `comments take`/`gate wait`. Build/design comments go immediately and `comments take`, `design comments`, or `next` mark pickup; `comments resolve --answer` proves action. Team ask replies use existing asks-feed/nextForAsk and preserve via/from provenance. Docs and turn must use that existing delivery core, not introduce an unrelated message queue. If a thread's member tally requires unavailable backend data, show only known replies and report the missing backend contract.

## Exclusive ownership

Only build-plan edits shared files. After this commit, no lane edits `TaskView.tsx`, `App.tsx`, `model.ts`, `ui/api.ts`, `server/api.ts`, `server/serve.ts`, `interaction/contracts.ts`, `server/interaction.ts`, `server/interaction-route.ts`, `ui/interaction/**`, `kit/kit.css`, `globals.css`, `brand/palette.css`, package/lock/config files, or PRODUCT.md/DESIGN.md. Ask for a shared change in your report with the exact missing seam. No RuleSync changes.

| Lane | Files it may edit/create |
| --- | --- |
| turn | `ui/turn/**`, `ui/FocusQuestion.tsx`, `ui/DiscussPage.tsx`, `ui/AnsweredMarkers.ts`, `ui/CurrentQuestion.tsx`, `ui/HomeQuestion.tsx`, `ui/question-preview.ts`, `ui/question-card.css`, `ui/useAnswers.ts`, `ui/kit/NeedsYou.tsx`, `ui/kit/ItemRow.tsx`; `server/interaction-turn.ts`; `core/task/question*.ts`, `core/task/intake.ts`, `core/task/point-confirmations.ts`, `core/next.ts`, `core/gate/comments.ts`; `cli/commands/question.ts`; `workflow/phases/**`, `workflow/skill/**`, `workflow/house-style.md` if present. New question/batch/delivery files go under `core/task/`, prefixed `question-` or `interaction-turn-`. |
| shell | `ui/shell/**`, `ui/Home.tsx`, `ui/Sidebar.tsx`, `ui/StepTabs.tsx`, `ui/home.css`, `ui/live-status.ts`, `ui/live-notify.ts`, `ui/NotificationBanner.tsx`, `ui/hooks.ts`, `ui/Resizer.tsx`, `ui/kit/CommandBox.tsx`, `ui/kit/WhoMark.tsx`, `ui/status/StatusPill.tsx`, `ui/status/status.css`, `ui/Trouble.tsx`; `server/interaction-shell.ts`; `core/live/**`, `core/helpers.ts`. New Home/notification modules go under `core/interaction-shell/`. Existing Settings, Updates, licence, first-run and feedback files are shell-owned only if they need a change; preserve those flows. |
| docs | `ui/docs/**`, `ui/sidebar/**`, `ui/reader/**`, `ui/design/**`, `ui/AskParts.tsx`, `ui/DocPathChip.tsx`, `ui/CostPanel.tsx`, `ui/UpgradePopover.tsx`, `ui/PlanBody.tsx`, `ui/timeline/PlanView.tsx`, `ui/kit/CommentsPanel.tsx`; `ui/step-page/StepPage.tsx`, `PlanningParts.tsx`, `Answers.tsx`, `DesignSlot.tsx`, `DocMarkdown.tsx`, `document.ts`, `segments.ts`, `RecordDrawer.tsx`, `step-page.css`; `server/interaction-docs.ts`, `server/designs.ts`, `server/design-bridge.ts`, `server/open-file.ts`, `core/design/**`. New thread helpers go under `core/interaction-docs/`; import gate/comments without editing it. |
| steps | `ui/steps/**`, `ui/timeline/**` EXCEPT `PlanView.tsx`, `ui/ImplementStart.tsx`, `ui/ChangesView.tsx`, `ui/StepActions.tsx`, `ui/build-view.css`, `ui/timeline.css`, `ui/review-view.css`, `ui/review-page.css`, `ui/kit/CheckLine.tsx`, `ui/kit/StepLine.tsx`, `ui/kit/steps.css`, `ui/status/NeedCard.tsx`; `ui/step-page/BuildParts.tsx`, `CheckParts.tsx`, `state.ts`, `live.ts`; `server/interaction-steps.ts`; `core/checklist.ts`, `core/review/**`, `core/gate/amend.ts`, `core/gate/hold.ts`, `core/need/**`, `core/implement/**`, `cli/commands/review.ts`, `cli/commands/need.ts`. New proof/reopen helpers go under `core/interaction-steps/`. |

Everything unlisted is read-only. Do not widen an ownership glob yourself. Each lane owns the CSS files listed for it, its phone-width parts and new tests named `interaction-<lane>-*.test.ts[x]` in tests/ui, server, cli, core and e2e. Existing test files are reserved until explicitly listed below; import the shared fixtures/helpers without editing them. Skeleton `tests/server/interaction-skeleton.test.ts` is frozen: regression tests prove its current false capabilities/stubs until turn replaces the assertions as part of its feature completion (turn exclusively owns subsequent edits to this one test).

Existing test ownership: turn — question-ask (core/cli), question-routes (server), focus-question/current-question/optimistic-question (ui), answer-in-app/focus-question-width (e2e); shell — live-status/live-notify (ui), live-status-layout/cockpit-speed/cockpit-large-task (e2e); docs — designs/step-pages/doc-reader/right-sidebar/ask-parts files wherever present, except core question tests; steps — implement-page/verify-page/review-view/step-state/files-changed (ui), verify-live/holds/build (e2e). Existing broad `app.test.tsx`, `views.test.tsx`, `routes.test.ts`, `phase-wording.test.ts` and helper files stay frozen; add focused lane tests rather than changing shared expectations independently. Turn owns updates to the skeleton test's false-capability/501 expectations when its feature becomes available.

Important seams: turn owns question and comment delivery, docs imports those APIs; docs owns the Plan's render primitives, turn owns reusable question/agreement controls; steps owns Review reopen, docs merely calls that route in its menu; shell owns liveness/helper role collection, steps consumes it. `core/next.ts` belongs only to turn: other lanes request a next-payload addition in their report. `core/helpers.ts` belongs only to shell: steps requests an extra proof signal rather than changing it. This avoids the highest-risk backend collisions.

## Table 10a — every row has a responsible lane

The row numbers follow the frozen table. A responsible lane may import another lane's published component/API but may not edit its files. “Keep” includes checking that the move did not remove the feature. The four proposed drops are approved, not open questions.

| # | Feature | Responsible lane |
| --- | --- | --- |
| 1 | Logo goes Home | shell |
| 2 | Project filter | shell |
| 3 | Filter note and Clear | shell |
| 4 | Groups: Needs you, Running, Shipped, Archived → Your turn wording | shell |
| 5 | Personal / Team switch, Team space → Team row | shell |
| 6 | Account menu, licence line | shell |
| 7 | Settings, Docs, Theme, Feedback | shell |
| 8 | Resizable columns | shell |
| 9 | Hide the task list → rail | shell |
| 10 | Links into the App, exact Slack thread | docs |
| 11 | What needs you, answered in place on Home | shell; turn projection/actions |
| 12 | Answers to your questions, notices | shell |
| 13 | Questions from teammates on Home | shell |
| 14 | Running with live lines, How to resume | shell |
| 15 | Shipped, cost, All shipped and archived | shell |
| 16 | Tasks in each step, spending by period | shell |
| 17 | Step tabs with marks → top track | shell |
| 18 | Step-tab badges — DROP | shell |
| 19 | Step line, main button, Cmd+Enter → Now | turn; docs/steps own their step actions |
| 20 | File chip, branch chip, type tag | docs |
| 21 | Checks chip → Implement violet line | steps |
| 22 | Cost, Share, Archive, Delete → task menu | docs |
| 23 | Decided elsewhere, decision errors | turn |
| 24 | Plan diff → Was/Now and path menu | docs |
| 25 | Agent question, choices, evidence, why → batch | turn |
| 26 | Answered-question markers → neutral Q tags | turn |
| 27 | Q answered line and Back to question — DROP | turn |
| 28 | In / not in this task, Decided with you | turn |
| 29 | Handed back as too small | turn |
| 30 | Plan items, answers, Undo, Add review | docs; reusable turn actions |
| 31 | Done-means points, per-point comment | docs; turn owns agreement persistence |
| 32 | Reviewer findings, second opinion | docs |
| 33 | Out of scope, assumptions with Ask, slices, how we'll know | docs |
| 34 | Contract map, prerequisites | docs; steps consumes check facts |
| 35 | Keyboard up/down/Enter, settled fold replacement | turn |
| 36 | Implement start and defaults | steps |
| 37 | Slices, tasks, checkpoints | steps |
| 38 | Changed while building, changes so far, diff drawer | steps |
| 39 | Build comments, Send to the build, mentions | steps |
| 40 | Add to Plan, stop after failed checkpoint | steps |
| 41 | Live checklist, evidence, stop card → per point | steps |
| 42 | Before checking, whole change, Stop checking and review | steps |
| 43 | What changed, by task, Try it yourself → by point | steps |
| 44 | Diff line comments, complete diff | steps |
| 45 | Approve menu, Send N changes, approve without waiting | steps |
| 46 | Your notes after sending changes | steps |
| 47 | Amend after approving | steps; docs menu entry |
| 48 | Shipped: PR, what you decided, cost | steps; shell Home consumes facts |
| 49 | Full document for each step | docs |
| 50 | Block/line comments, quotes, highlights | docs |
| 51 | Threads, reply, resolve, passage changed, agent answers | docs |
| 52 | Comments that go to agent | docs; turn delivery core |
| 53 | Ask team, agent/Slack answers | docs |
| 54 | Team answer tally | docs |
| 55 | Remind, Hand to, Ask review, reviewers | docs |
| 56 | Share popover, create/renew/revoke outside links | docs |
| 57 | Teammate task, teammate Review tabs | shell; preserve read-only view |
| 58 | Right sidebar Comments / Files / Designs | docs |
| 59 | Files by step/audience/records | docs |
| 60 | Copy path, Open, Reveal | docs |
| 61 | Outline, folding, jump links, Copy menu | docs |
| 62 | Mermaid zoom/source/full screen/pins | docs |
| 63 | Sandboxed mockups, Show me, screenshot pins, designs | docs |
| 64 | Agent marks, quiet, resume | shell |
| 65 | Cost popover | docs; shell panel links to it |
| 66 | Cmd+K tasks/mentions/settings/filters | shell |
| 67 | Settings Workflow/Licence/Team/About | shell; preserve, no new Teams integration |
| 68 | Feedback, Report this | shell |
| 69 | Update line/sheet/toast | shell |
| 70 | Trial ended, locked Share, setup, first run, handover, moved | shell |
| 71 | Notifications | shell |
| 72 | Turn on notifications banner | shell |
| 73 | Server down, older link | shell |
| 74 | Archive, restore, delete | docs |
| 75 | Narrow and phone widths | shell coordinates tabs; every lane owns its content |
| 76 | Unused Grok App route — DROP | build-plan removed shared server route; turn verifies no UI depends on it. CLI Grok is outside this drop. |

## Tests and actual-agent delivery checks

All CLI/App/server/test processes use a fresh temp HOME and QUALITYLAYER_HOME. Browser uses mock keychain/basic password store. Real-agent runs get a fresh CODEX_HOME with only copied auth.json and the four allowed config values; no real hooks/plugins/MCP, no keychain. No real Slack, backend writes, Polar, or deploys. Build/test may not replace dist while a release gate uses it.

| Lane | Test-first behavior, then real browser/CLI proof |
| --- | --- |
| turn | Two or more simultaneous questions; reverse-order answers; agent can run an independent command with questions open; unknown/stale id refused; concurrent answers do not overwrite; restart keeps remaining questions/answers; per-question More/Not sure/Change; Undo within 5 s and rollback on error; unchanged agreement survives one-point rewording/renumbering; API rejects stale wording; shared optimistic update changes card/nav/Home/bell/title together. Browser clicks → real `question poll` or `next` receives each answer before the rest are answered → agent updates the exact Done means point → real reply is shown. Run tests/core/question-ask, cli/question-ask, server/question-routes, ui/focus-question/current-question/optimistic-question, e2e/answer-in-app/focus-question-width and new interaction-turn flow tests. |
| shell | Five states with alive PID and misleading SessionEnd; waiting vs still-working batch; restart ownership; quiet at 2 min and guidance at 15; role/subject/start/end helpers; dead process resume; one notification per batch, settlement follows item across surfaces; exact-item jump; project+agent filters; local calendar boundaries/DST; missing costs stay unknown; no N+1 cost reads on first render; Cmd+K and keyboard/resizing; event bursts cannot continually cancel the newest task request. Real CLI activity/question heartbeat, kill/restart only the fixture agent/server, inspect panel and nav; full speed/large-task tests green. |
| docs | Plan Was/Now for only the changed point, unchanged points stay agreed; design preview/full size; F/Exit with focus return; full-size outline and rail; file grouping/back/read-only records; path/open allowlist; one focused thread, reply/resolution/changed passage/provenance/team tally using local team fixtures; no leak of agent/ or designs to public snapshots; theme/viewport/zoom/pins. Browser comment → real `comments take` or `gate wait` after temp approval → agent `comments resolve --answer` → visible reply; design pin → `design comments` → agent updates same file → App update notice. Agreement click uses turn item API and its real receipts. |
| steps | Add/Skip unplanned file holds only the affected slice (see risk below); actual attach after Copy, every default picker/Reset; live TDD board/checkpoints/diff/comments; proof grouped by Done means; accepted fail distinct from pass and confirmation twice; independent checks; preserved personal confirmation; send changes with picked/done; affected-point rechecks; all approval choices with no merge/branch switch; safe reopen after approval. Browser build comment → real `comments take`; review note → gate wait/next → real agent fix → resolve receipt. Use temp git remote or fixture for PR action, never production. |

Each lane captures its frames against the frozen reference at desktop and 390px, light and dark, checks console errors/overflow/focus, and checks every action looks clickable only if it works. Captures stay in its uncommitted report folder. Run typecheck, lint and relevant files before each conventional commit; run the full suite after integration. Existing release-branch failures are not permission for new ones. Keep baseline failing test names/logs in reports; get verify/green's exact known list before declaring the final release green.

## Risks and tonight's cuts

1. **Current core conflicts with the new unplanned-file ask.** The existing skill says all build changes are agent-made and nothing waits; 4a requires a person to Add/Skip an unplanned file. Steps owns holds/amend behavior, turn owns the phase wording. Limit the change to the specified file hold, isolate the slice, test continued work; do not restore broad autonomous-build pauses. Raise any wider behavior decision to the reviewer.
2. **Immediate Agree differs from current draft delivery.** `useAnswers` and many item handlers save drafts until approval. Turn must add a real per-item delivery path and preserve existing comments; docs cannot just hide the item optimistically and call it delivered.
3. **Undo after pickup is a correction.** A poll can win the race before five seconds. Append a correction with identity/version and show pickup honestly. Do not cancel dependent work magically or erase the audit trail.
4. **Thread/tally data may be incomplete.** Existing local Comments and Ask rows contain different reply/provenance forms. Docs normalizes them without a production/backend change. Null tally is honest. Never ship a static sample count.
5. **Status and Home costs can slow the App.** Reuse live read/cache and off-path cost aggregation. Avoid querying every task's full diff or transcript to render nav/notifications. Preserve speed budgets and large-task tests.
6. **Readiness can strand a control.** Each lane keeps fallback children until its full step works, and enables only its step. Docs must remove duplicated document approval when that step moves into Now. Integration must test both old and pages task layouts.
7. **Reopen Review touches lifecycle and approval history.** Reuse a safe amend/review path and advance(), never assign stage from a route. If it requires new lifecycle semantics, report the issue; do not improvise a reopen.
8. **Source/security and merge collisions.** Everything in qualitylayer stays encrypted, including new files. Stage only owned paths. No pushes/rebases/deploys. Shared edits go to the integrator. Do not merge another lane into this planning branch; implementing lanes follow the brief's authorized integration protocol within their own branches.

If time runs short, cut historical helper expansion, fancy motion, Home spending breakdown detail, and extra design viewport presets first. Keep honest missing-data states. Defer risky Review reopen if no safe core path exists and report it as an explicit design miss. Never cut delivery correctness, batched questions, per-point preservation, five-state liveness, one Your turn card, usable phone navigation, existing feature access, or required checks. Capability false/501 is acceptable only in this skeleton, never as release completion.

Reviewer questions: confirm verify/green's exact 13-failure inventory; confirm the file-hold scope in risk 1 is the intended exception to autonomous building; decide whether risky Review reopen should be deferred if its existing core path cannot preserve approval history. These do not block the bounded lane work above.
