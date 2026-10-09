import { ArrowRight, Check, ChevronDown, ChevronRight, Copy, Image, Maximize2, MessageSquare, Plus, Send } from "lucide-react";
import type { ReactNode } from "react";
import { CHAPTERS, checkRunning, checksPassed, committedTasks, DESIGN, DISCUSS_BATCH, discussAt, REQUEST, STAGES, TASK, VERIFY_CHECKS } from "@/lib/tour";

/**
 * One close-up of the QualityLayer App per chapter, at reading size. Each is a crop of the App's
 * main column as qualitylayer/design/app draws it: the top bar (the task, its seven steps and the
 * agent chip), the connected seven steps, and then the question or full document. Agent activity
 * opens from its chip. A close-up plays its moments one per second; `step` is the moment.
 */

type Mark = "you" | "work" | "wait" | "done" | "check" | "open";
const Mk = ({ k }: { k: Mark }) => <span aria-hidden="true" className={`cu-mk ${k}`} />;

type Chip = { mark: Mark; name: string; words: string } | null;

/** The top bar: a task with its seven steps and the agent chip, or a page's title. */
function TopBar({ stage, title = TASK, kind = "feature", chip, approval, activity }: { stage: number; title?: string; kind?: string; chip: Chip; approval?: ReactNode; activity?: ReactNode }) {
  return (
    <>
    <div className={`cu-tb${stage >= 0 ? " task" : ""}`}>
      <b className="cu-title">{title}</b>
      {stage < 0 && kind && <span className="cu-kind">{kind}</span>}
      {chip && (
        <details className="cu-status">
          <summary aria-label={`${chip.name} status`} className={`cu-chip ${chip.mark}`}>
            <Mk k={chip.mark} /><b>{chip.name}</b><ChevronDown size={13} aria-hidden="true" />
          </summary>
          <div className="cu-status-panel">
            <p className="cu-k">{chip.name} · {chip.words}</p>
            {activity ?? <p>{chip.words}</p>}
          </div>
        </details>
      )}
    </div>
    {stage >= 0 && <div className="cu-workspace-track">
      <ol className="cu-track" aria-label="Task steps">
        {STAGES.map((label, k) => <li key={label} className={k < stage ? "done" : k === stage ? "cur" : "future"} aria-current={k === stage ? "step" : undefined}>{label}</li>)}
      </ol>
      {approval}
    </div>}
    </>
  );
}

type Gate = { label: string; state?: "cur" | "done"; pips?: [number, number] };

/** A genuine person-needed note; the workflow stays in the connected header. */
function GateTrack({ turn }: { items: Gate[]; turn?: string }) {
  return turn ? <p className="cu-step-note"><Mk k="you" />{turn}</p> : null;
}

function Frame({ top, gate, children, label }: { top: ReactNode; gate?: ReactNode; children: ReactNode; label: string }) {
  return (
    <div className="cu" data-closeup={label}>
      {top}
      {gate}
      <div className="cu-stage">{children}</div>
    </div>
  );
}

/** The one amber card that holds what waits for you. */
function YourTurn({ kind, count, title, text, children, foot }: { kind: string; count?: string; title: ReactNode; text?: ReactNode; children?: ReactNode; foot?: ReactNode }) {
  return (
    <section className="cu-yt">
      <p className="cu-ytag"><Mk k="you" />Your turn<span className="cu-k">· {kind}</span><span className="cu-grow" />{count && <span className="cu-k">{count}</span>}</p>
      <h4 className="cu-yh">{title}</h4>
      {text && <p className="cu-yp">{text}</p>}
      {children && <div className="cu-yb">{children}</div>}
      {foot && <div className="cu-yf">{foot}</div>}
    </section>
  );
}

/** Activity belongs in the status panel, leaving the document in the workspace. */
function AgentActivity({ title, note, sub, children }: { title: string; note?: string; sub?: string; children?: ReactNode }) {
  return (
    <div>
      <h4 className="cu-ah">{title}{note && <span className="cu-k">{note}</span>}</h4>
      {sub && <p className="cu-as">{sub}</p>}
      {children}
    </div>
  );
}

function DeliveryFlow({ pin = false }: { pin?: boolean }) {
  return <div className="cu-dgm">
    {pin && <span className="cu-pin">1</span>}
    <p className="cu-dgmh"><span>What happens to a failed delivery</span><span>{pin ? "1 comment" : "flow"}</span></p>
    <div className="cu-dgr"><span className="cu-dn on">Retry queue<small>keeps each failed delivery once</small></span><span className="cu-dl"><em>try &lt; 3</em></span><span className="cu-dn">Send again<small>a minute apart</small></span></div>
    <div className="cu-dgr"><span className="cu-dn you">Third try failed</span><span className="cu-dl" /><span className="cu-dn">Mail the customer<small>once, then stop</small></span></div>
  </div>;
}

/** Numbered choices with the recommendation marked, and the own-words field always in view. */
function Choices({ items, rec = 0, picked = -1, own = "Or write your own answer…" }: { items: [string, string?][]; rec?: number; picked?: number; own?: string | null }) {
  return (
    <>
      <div className="cu-chs">
        {items.map(([label, note], i) => (
          <span key={label} className={`cu-ch${i === rec ? " rec" : ""}${i === picked ? " picked" : ""}`}>
            <span className="cu-chn">{i + 1}</span>
            <span className="cu-chl">{label}{note && <small>{note}</small>}</span>
            {i === rec && <span className="cu-chr">recommended</span>}
          </span>
        ))}
      </div>
      {own !== null && <div className="cu-own"><span className="cu-field">{own}</span><span className="cu-btn pri">Send <kbd>↵</kbd></span></div>}
    </>
  );
}

const Keys = ({ keys }: { keys: [string, string][] }) => (
  <span className="cu-keys">{keys.map(([k, label]) => <span key={label}><kbd>{k}</kbd>{label}</span>)}</span>
);

/** A sent answer, with its undo. */
const Sent = ({ children }: { children: ReactNode }) => (
  <p className="cu-sent"><Check size={14} aria-hidden="true" /><span>{children}</span><span className="cu-k">Undo · 5 s</span></p>
);

/** The violet line: what the agents checked, opening on demand. */
const Checked = ({ facts, head = "Checked by agents" }: { facts: string[]; head?: string }) => (
  <p className="cu-cl"><b>{head}</b>{facts.map((f) => <span key={f}>{f}</span>)}<ChevronDown size={14} aria-hidden="true" /></p>
);

/**
 * The page the agent drew for this task: the person's own product, drawn in its theme. Full size,
 * its Retry button works: three tries and the delivery stops and mails the customer.
 */
export function DesignPage({ tries = 2, onRetry, next = false, pin = false, brief = false }: { tries?: number; onRetry?: () => void; next?: boolean; pin?: boolean; brief?: boolean }) {
  const stopped = tries >= 3;
  const rows: [string, string, string][] = [
    ["order.paid", "/hooks/orders", "Delivered"],
    ["invoice.sent", "/hooks/billing", stopped ? "Stopped, mailed" : `Try ${tries} of 3`],
    ["refund.issued", "/hooks/billing", "Stopped, mailed"],
  ];
  return (
    <div className={`cu-dp${brief ? " brief" : ""}`}>
      <div className="cu-dph"><b>Deliveries</b><span className="cu-dpt"><span>All</span><span className="on">Failed · 2</span></span></div>
      {rows.map(([event, url, state]) => (
        <div key={event} className="cu-dpr">
          <code>{event}</code>
          <code className="dim">{url}</code>
          <span className={state.startsWith("Try") ? "amb" : state.startsWith("Stopped") ? "red" : ""}>
            {state}
            {event === "invoice.sent" && next && !stopped && <small> · next try 14:05</small>}
            {event === "invoice.sent" && pin && <span className="cu-pin">1</span>}
          </span>
          <span>
            {event === "invoice.sent" &&
              (onRetry ? <button type="button" onClick={onRetry} disabled={stopped} tabIndex={-1} className="cu-dpb">Retry</button> : <span className="cu-dpb">Retry</span>)}
          </span>
        </div>
      ))}
      {!brief && <p className="cu-dpf">Three tries, a minute apart. Then the customer gets one mail and the delivery stops.</p>}
    </div>
  );
}

/** A design inside the card it belongs to. */
const DesignIn = ({ children }: { children: ReactNode }) => (
  <div className="cu-dz">
    <p className="cu-dzh"><Image size={13} aria-hidden="true" /><b>failed-deliveries</b><span className="cu-k">· the design for this question</span><span className="cu-grow" /><span className="cu-btn sm"><Maximize2 size={12} aria-hidden="true" />Full size</span></p>
    <div className="cu-dzf">{children}</div>
  </div>
);

const QUESTIONS: { title: string; text: string; settles: string; choices: [string, string?][] }[] = [
  { title: "How many tries before it stops?", text: "Today a failed delivery is lost. After how many tries should it stop and tell someone?", settles: "Done means 2", choices: [["3 tries, then one mail"], ["5 tries, then one mail", "five failure mails is a lot"], ["Until it succeeds"]] },
  { title: "Who hears about it when it stops?", text: "The customer owns the endpoint, so they can fix it. Support sees every failed delivery anyway.", settles: "Done means 2", choices: [["The customer, in one mail"], ["Support, in a Slack channel"], ["Both"]] },
  { title: "When does it try again?", text: "The partner API answers within seconds when it is up.", settles: "Done means 1", choices: [["A minute apart"], ["Back off: 1, 5, then 15 minutes"], ["Five minutes apart"]] },
  { title: "Which endpoints does this cover?", text: "Customers registered their endpoints over several years. Some deliver to a service that no longer exists.", settles: "Done means 1", choices: [["Every endpoint"], ["Only endpoints added from now on"], ["Only the billing endpoints"]] },
];

/** The build's slices as the Outline cut them: slice 1 first, then slices 2 and 3 side by side. `run` and `done` are moments of the Implement close-up. */
const SLICES = [
  { title: "Failed deliveries go to a retry queue", doing: "", par: "", tasks: ["T1", "T2"], run: 0, done: 0 },
  { title: "Three tries, then mail the customer", doing: "T3: the test fails first, then it stops after the third try", par: "built side by side with slice 3", tasks: ["T3", "T4"], run: 0, done: 3 },
  { title: "Retry count in the delivery row", doing: "T5: the test fails first, then each row shows the count", par: "built side by side with slice 2", tasks: ["T5"], run: 0, done: 1 },
];

/** Each point of Done means, the proof beside it, and the moment of the Verify close-up it passes. */
const POINTS: [string, string, number][] = [
  ["Failed deliveries are retried", "delivery.test.ts · a failed delivery is queued once and sent again", 0],
  ["It stops after 3 tries and mails the customer once", "mailer.test.ts · 3 tries, then one mail", 3],
  ["Support sees the retry count", "row.test.tsx · screenshot 2 shows the count in each row", 5],
];

/** Where each Done means point was built: the slice whose scenario proves it. */
const BUILT_IN = [1, 2, 3];

/** A few lines of the diff of one file, as the walkthrough opens it; the comment is on line 14. */
const DIFF: [string, number, string][] = [
  ["ctx", 12, "export function nextTry(delivery: Delivery) {"],
  ["add", 13, "  if (delivery.tries >= settings.maxTries) return stop(delivery)"],
  ["add", 14, "  return retryAt(delivery, settings.retryDelay)"],
  ["ctx", 15, "}"],
];

/**
 * The change top to bottom, as the Review step draws it under the approval card: why, what you
 * asked for, the slices with their files and diffs, what was left alone, how it was checked and where
 * it ships. The pull request's description reads in the same order.
 */
function Walkthrough() {
  return (
    <section className="cu-card cu-wt" aria-label="The change, top to bottom">
      <p className="cu-cardh"><b>The change, top to bottom</b><span className="cu-k">3 slices · 5 tasks · 8 files</span><span className="cu-grow" /><span className="cu-k cu-wt-same">same order as the pull request</span></p>
      <div className="cu-wr">
        <span className="cu-wk">Why</span>
        <p>A failed webhook delivery is lost today. After this change it is tried three times, and the customer gets one mail if it still fails.</p>
      </div>
      <div className="cu-wr">
        <span className="cu-wk">What you asked for<small>3 points</small></span>
        <div className="cu-wpts">
          {POINTS.map(([title], k) => (
            <p key={title}><span className="cu-num">{k + 1}</span><span>{title}<small>built in slice {BUILT_IN[k]} · proved by scenario {k + 1}</small></span><span className="cu-k">passed</span></p>
          ))}
        </div>
      </div>
      <div className="cu-wr">
        <span className="cu-wk">Built, slice by slice<small>comment on any line</small></span>
        <div className="cu-wsl">
          {SLICES.map((slice, k) => (
            <div key={slice.title} className={`cu-ws${k === 1 ? " open" : ""}`}>
              <p className="cu-wsh">{k === 1 ? <ChevronDown size={13} aria-hidden="true" /> : <ChevronRight size={13} aria-hidden="true" />}<span className="cu-num">{k + 1}</span><span className="cu-wst">{slice.title}</span><span className="cu-k">{slice.tasks.length} {slice.tasks.length === 1 ? "task" : "tasks"} · {k === 2 ? 2 : 3} files{k === 1 ? " · 1 decision" : ""}</span></p>
              {k === 1 && (
                <div className="cu-wsb">
                  <p className="cu-wd"><Mk k="done" /><span>Decided while building · Moved the retry delay into settings.ts</span><span className="cu-lnk">Ask why</span></p>
                  <p className="cu-wf"><span className="cu-k">T3</span><code>src/delivery/retry.ts</code><span className="cu-k">+38 −4</span></p>
                  <div className="cu-wdf" role="group" aria-label="Diff of src/delivery/retry.ts">
                    {DIFF.map(([kind, n, line]) => (
                      <div key={n}>
                        <p className={`cu-wl ${kind}`}><span>{n}</span><code>{line}</code></p>
                        {n === 14 && <p className="cu-wth"><i className="cu-av">D</i><span><b>Dana</b> <span className="cu-k">from the team</span><br />Does the count start again after a delivery succeeds?</span></p>}
                      </div>
                    ))}
                  </div>
                  <p className="cu-wf"><span className="cu-k">T3</span><code>tests/delivery/retry.test.ts</code><span className="cu-k">new · +54</span></p>
                  <p className="cu-wf"><span className="cu-k">T4</span><code>src/mail/stop-notice.ts</code><span className="cu-k">new · +22</span></p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      <div className="cu-wr">
        <span className="cu-wk">Deliberately not changed</span>
        <p>Deliveries to endpoints that no longer exist stay as they are. The mail for other events keeps its wording.</p>
      </div>
      <div className="cu-wr">
        <span className="cu-wk">How it was checked</span>
        <p className="cu-wchk"><Mk k="check" />12 of 12 checks passed<span className="cu-k">· 3 steps to try it yourself · 1 thing only you can confirm</span></p>
      </div>
      <div className="cu-wr">
        <span className="cu-wk">Ship</span>
        <p>Lands on <code>ql/retry-webhooks</code> · pull request to <code>main</code> · no security findings</p>
      </div>
    </section>
  );
}

/** After the approval: the pull request's checks and reviews, until it is merged. */
function PullRequest() {
  const rows: [Mark, string, string][] = [
    ["work", "CI · macOS", "running · 4 min"],
    ["check", "CI · Linux", "passed · 6 min"],
    ["check", "Shellcheck and actionlint", "passed · 12 s"],
    ["wait", "Anna and Ben were asked", "no review yet"],
  ];
  return (
    <section className="cu-card" aria-label="Pull request">
      <p className="cu-cardh"><b>Pull request #412</b><span className="cu-k">ql/retry-webhooks → main · checks and reviews</span></p>
      {rows.map(([mark, what, state]) => (
        <p key={what} className="cu-pr"><Mk k={mark} /><span>{what}</span><span className="cu-k">{state}</span></p>
      ))}
    </section>
  );
}

const COST: [string, string, string, string][] = [
  ["Discuss", "7 min", "$1.30", "var(--ql-text-dim)"],
  ["Research", "5 min", "$0.80", "var(--ql-text-muted)"],
  ["Plan", "12 min", "$2.60", "var(--ql-amber)"],
  ["Outline", "6 min", "$1.25", "var(--ql-amber-ink)"],
  ["Implement", "26 min", "$9.40", "var(--ql-accent)"],
  ["Verify", "21 min", "$5.60", "var(--ql-check)"],
];

const waits = (words: string): Chip => ({ mark: "wait", name: "Claude Code", words });
const works = (words: string): Chip => ({ mark: "work", name: "Claude Code", words });

/** The close-up of chapter `id` at moment `step`. `tries` drives the design's working Retry button. */
export default function CloseUp({ id, step: asked, tries = 2, onRetry }: { id: string; step: number; tries?: number; onRetry?: () => void }) {
  // A close-up has no moment past its last.
  const step = Math.min(asked, CHAPTERS.find((c) => c.id === id)?.steps ?? asked);
  const at = (n: number) => step >= n;
  const show = (n: number) => `cu-in${at(n) ? " on" : ""}`;

  switch (id) {
    case "discuss": {
      // One batch of four, answered in any order: the strip shows all of them, one is in focus.
      const { answered, focus, picked, sent } = discussAt(step);
      const q = QUESTIONS[focus];
      const left = DISCUSS_BATCH - answered.length;
      return (
        <Frame label="Discuss"
          top={<TopBar stage={0} chip={works("reading notify.ts")} activity={<AgentActivity title="Reading the code while you answer" note="2 min" sub="Each answer reaches Claude Code at once. It writes Done means from them." />} />}
          gate={<GateTrack items={[]} turn={`Your turn · ${left} ${left === 1 ? "question" : "questions"}`} />}>
          {sent !== null && <Sent>Sent to Claude Code · {QUESTIONS[sent].choices[0][0]}</Sent>}
          <YourTurn kind={`a batch of ${DISCUSS_BATCH} from Claude Code`} title={q.title} text={<>{q.text} <span className="cu-k">Settles {q.settles}.</span></>}
            foot={<Keys keys={[["1", "pick"], ["↵", "send"], ["M", "tell me more"], ["R", "use the recommendation"]]} />}>
            <div className="cu-bq">
              <b>Scope and what Done means</b>
              <span className="cu-strip" role="group" aria-label="Questions in this batch">
                {QUESTIONS.map((x, k) => (
                  <span key={x.title} className={`${answered.includes(k) ? "done" : ""}${k === focus ? " on" : ""}`} aria-current={k === focus ? "true" : undefined}>
                    {answered.includes(k) && <Check size={12} aria-hidden="true" />}{k + 1}
                  </span>
                ))}
              </span>
              <span className="cu-bqr">question {focus + 1} of {DISCUSS_BATCH}</span>
            </div>
            <Choices items={q.choices} picked={picked ? 0 : -1} />
          </YourTurn>
        </Frame>
      );
    }

    case "plan": {
      // The complete Plan with its approval in the header from the first moment; a comment lands on its diagram, then Approve is ready.
      const commented = at(1);
      return (
        <Frame label="Plan"
          top={<TopBar stage={2} chip={waits("waits for your review")} approval={<div className="cu-approval"><span className="cu-k">Ready to approve</span><span className="cu-btn sm">Give feedback</span><span className={`cu-btn pri sm${at(2) ? " glow" : ""}`}>Approve Plan</span></div>} />}>
          <article className="cu-document compact" aria-label="Plan document">
            <h4>Retry failed webhook deliveries</h4>
            <p>Queue failed deliveries, retry three times, then mail the customer once.</p>
            <h5>Done means</h5>
            <ol>{POINTS.map(([title]) => <li key={title}>{title}</li>)}</ol>
            <p className="row"><b>Decisions</b> Support retries failed deliveries only, after checking the endpoint.</p>
            <DeliveryFlow pin={commented} />
            <p className="row"><b>Contracts</b> Three interfaces the build is held to, each folded to one headline</p>
            <p className="row"><b>Reviewed by</b> A reviewer read this Plan first; the findings are folded in</p>
          </article>
        </Frame>
      );
    }

    case "research": {
      const asked = at(3);
      const QUESTIONS_READ: [string, number][] = [
        ["How does a failed delivery leave the sender today?", 1],
        ["Where could a retry count live?", 2],
        ["What sends mail to the customer today?", 3],
      ];
      return (
        <Frame label="Research"
          top={<TopBar stage={1} chip={asked ? waits("waits for your choice") : works("3 agents reading the code")} activity={<AgentActivity title="Reading the code, without your request" note={`${3 + step} min`} sub="Each agent takes one area and answers questions about how it works today. None of them sees what you asked for."><p className="cu-prog">{Math.min(3, step)} of 3 questions answered</p></AgentActivity>} />}
          gate={<GateTrack items={[]} turn={asked ? "Your turn · 1 choice" : undefined} />}>
          {asked ? (
            <>
              <Checked head="The questions" facts={["3 answered", "by agents that never see your request"]} />
              <YourTurn kind="A choice the code leaves open" count="1 of 1" title="Who sends the one mail when a delivery stops?"
                text={<>The mailer already sends one mail for each event. <span className="cu-k">From Research · what sends mail today.</span></>}
                foot={<Keys keys={[["1 2", "pick"], ["↵", "send"], ["R", "recommended"]]} />}>
                <Choices items={[["Reuse the order mail", "one mail path to keep current"], ["A separate stop mail", "its own wording, a second path to keep current"]]} picked={at(4) ? 0 : -1} />
              </YourTurn>
            </>
          ) : (
            <section className="cu-card">
              <p className="cu-cardh"><b>The questions</b><span className="cu-k">answered by agents that never see your request</span></p>
              {QUESTIONS_READ.map(([title, when], k) => {
                const state = step >= when ? "check" : "work";
                return (
                  <div key={title} className="cu-vr">
                    <Mk k={state} />
                    <span className="cu-num">{k + 1}</span>
                    <span className="cu-slt">{title}<small>{state === "check" ? "answered" : "reading the code"}</small></span>
                    <span className={`cu-k ${state}`}>{state === "check" ? "answered" : ""}</span>
                  </div>
                );
              })}
            </section>
          )}
        </Frame>
      );
    }

    case "outline": {
      const waves: [string, string][] = [["Wave 1", "Slice 1 · failed deliveries go to a retry queue"], ["Wave 2", "Slices 2 and 3, side by side"]];
      return (
        <Frame label="Outline"
          top={<TopBar stage={3} chip={at(3) ? waits("the Outline is done") : works("writing the Outline")} activity={<AgentActivity title="Cutting the Plan into slices" note={`${2 + step} min`} sub="You read the Plan meanwhile. Nothing to approve here; the build can start the moment you approve the Plan." />} />}>
          <article className="cu-document" aria-label="Outline document">
            <h4>The build, slice by slice</h4>
            <p>3 slices and 5 tasks, in 2 waves.</p>
            <h5>How the build runs</h5><ol>{waves.map(([wave, what]) => <li key={wave}>{wave} · {what}</li>)}</ol>
            <h5>Slices</h5><ol>{SLICES.map((slice) => <li key={slice.title}>{slice.title} · {slice.tasks.length} {slice.tasks.length === 1 ? "task" : "tasks"}</li>)}</ol>
            <h5>How each point is proved</h5><ol>{POINTS.map(([title], k) => <li key={title}>{title} · scenario {k + 1}</li>)}</ol>
            {at(2) && (<><h5>Checked by a second reader</h5><p>2 gaps found and fixed. Every Done means point has a scenario.</p></>)}
          </article>
        </Frame>
      );
    }

    case "start":
      return (
        <Frame label="Start"
          top={<TopBar stage={4} chip={waits("Plan approved")} />}
          gate={<GateTrack items={[{ label: "Start", state: "cur" }, { label: "Slices · 3" }, { label: "Checked as it builds" }, { label: "Agents check every point" }]} turn="Your turn · start the build" />}>
          <YourTurn kind="Implement" title="Start the build" text="Paste one command in a fresh session. From then on the build runs on its own until the final review.">
            <span className="cu-seg"><span className="on">Claude Code</span><span>Codex</span><span>Another agent</span></span>
            <p className="cu-defs"><span><span className="cu-k">Plans each slice</span> Opus 5.5</span><span><span className="cu-k">Builds</span> Sonnet 5.5</span><span><span className="cu-k">Effort</span> High</span><span className="cu-lnk">Change</span></p>
            <div className="cu-cmd"><code>/ql implement retry-webhooks</code><span className={`cu-btn pri sm${step === 1 ? " press" : ""}`}>{at(2) ? <Check size={12} aria-hidden="true" /> : <Copy size={12} aria-hidden="true" />}{at(2) ? "Copied" : "Copy"}</span></div>
          </YourTurn>
        </Frame>
      );

    case "implement": {
      const done = committedTasks(step);
      const slicesDone = SLICES.filter((s) => step >= s.done).length;
      const building = slicesDone < SLICES.length;
      return (
        <Frame label="Implement"
          top={<TopBar stage={4} chip={works(building ? "building slices 2 and 3 side by side" : "recording the proof")} activity={<AgentActivity title={building ? "Building slices 2 and 3 side by side" : "The build is finished"} note={`${10 + step * 3} min`} sub="Every task starts with a failing test. Slices that don’t overlap build side by side."><p className="cu-prog">{done} of 5 tasks committed · every test run recorded</p></AgentActivity>} />}
          gate={<GateTrack items={[{ label: "Started 14:02", state: "done" }, { label: `Slices · ${slicesDone} of 3`, state: "cur", pips: [slicesDone, 3] }, { label: "Checked as it builds" }, { label: "Agents check every point" }]} />}>
          <section className="cu-card">
            <p className="cu-cardh"><b>Slices</b><span className="cu-k">{slicesDone} of 3 done · {done} of 5 tasks committed</span></p>
            {SLICES.map((s, k) => {
              const state = step >= s.done ? "done" : step >= s.run ? "run" : "next";
              const note = state === "run" ? s.doing : s.par;
              return (
                <div key={s.title} className={`cu-slr ${state}`}>
                  <Mk k={state === "done" ? "done" : state === "run" ? "work" : "open"} />
                  <span className="cu-num">{k + 1}</span>
                  <span className="cu-slt">{s.title}{note && <small>{note}</small>}</span>
                  <span className="cu-k">{state === "done" ? "committed" : state === "run" ? "building" : "after 1"}</span>
                </div>
              );
            })}
          </section>
          <p className={`cu-row ${show(4)}`}><Mk k="done" /><span className="cu-k">Decided while building</span><span>Moved the retry delay into settings.ts</span><span className="cu-grow" /><span className="cu-btn sm">Ask why</span></p>
          <div className={show(5)}><Checked facts={["5 tasks green, test first", "11 test runs recorded"]} /></div>
        </Frame>
      );
    }

    case "verify": {
      const passed = checksPassed(step);
      const done = at(7);
      const pointsPassed = POINTS.filter(([, , when]) => step >= when).length;
      return (
        <Frame label="Verify"
          top={<TopBar stage={5} chip={done ? waits("waits for your review") : works(`running ${checkRunning(step)}`)} activity={<AgentActivity title="Agents that did not write the code are checking" note={`${passed} of 12`}><p className="cu-prog">412 tests passed · types, lint and build passed</p></AgentActivity>} />}
          gate={<GateTrack items={[{ label: "Polish", state: "done" }, { label: "Project checks · 4", state: at(2) ? "done" : "cur" }, { label: `Done means · ${pointsPassed} of 3`, state: at(2) && !done ? "cur" : at(6) ? "done" : undefined, pips: [pointsPassed, 3] }, { label: "Code review", state: at(6) ? "done" : undefined }]} turn={done ? "Your turn · 2 in Review" : undefined} />}>
          <Checked head="Six checks, in order" facts={VERIFY_CHECKS} />
          {done && <Checked facts={["12 of 12 passed", "412 tests", "evidence for each point"]} />}
          <section className="cu-card">
            <p className="cu-cardh"><b>Done means</b><span className="cu-k">each point against the running program</span></p>
            {POINTS.map(([title, evidence, when], k) => {
              const state = step >= when ? "check" : step >= when - 1 ? "work" : "open";
              return (
                <div key={title} className="cu-vr">
                  <Mk k={state} />
                  <span className="cu-num">{k + 1}</span>
                  <span className="cu-slt">{title}<small>{state === "check" ? evidence : state === "work" ? "checking now" : "waiting"}</small></span>
                  <span className={`cu-k ${state}`}>{state === "check" ? "passed" : state === "work" ? "checking" : ""}</span>
                </div>
              );
            })}
          </section>
          {done && <p className="cu-nextyou"><span className="cu-k">Next for you</span><span>Review · one live call only you can confirm, and one choice the agent made</span></p>}
        </Frame>
      );
    }

    case "review": {
      // The approval card, then the change top to bottom; once approved, the pull request stays on the page until it is merged.
      const left = Math.max(0, 2 - step);
      const approved = at(5);
      if (approved)
        return (
          <Frame label="Review"
            top={<TopBar stage={6} chip={{ mark: "done", name: "Claude Code", words: "pull request #412 is open" }} />}>
            <section className="cu-card cu-calm">
              <p className="cu-cardh"><b>Approved · pull request #412 opened</b><span className="cu-k">on ql/retry-webhooks</span></p>
              <p className="cu-calmp">Checks run on GitHub now. The task stays open until the pull request is merged, and you are told when a review or a failing check needs you.</p>
            </section>
            <PullRequest />
            <p className="cu-fold"><b>The change, top to bottom</b><span className="cu-k">as you approved it · 8 files</span><ChevronRight size={14} aria-hidden="true" /></p>
          </Frame>
        );
      return (
        <Frame label="Review"
          top={<TopBar stage={6} chip={waits("waits for your review")} />}
          gate={<GateTrack items={[{ label: "What you get · 3 points", state: "done" }, { label: "Only you can confirm · 1", state: at(1) ? "done" : "cur" }, { label: "Decided while building · 1", state: at(2) ? "done" : at(1) ? "cur" : undefined }, { label: "Approve", state: at(2) ? "cur" : undefined }]} turn={left ? `Your turn · ${left} ${left === 1 ? "thing" : "things"}` : "Your turn · approve"} />}>
          <YourTurn kind="then approve" count={`${2 - left} of 2`} title={left ? `${left} ${left === 1 ? "thing" : "things"}, then approve` : "Approve the change?"} text="Agents checked everything they can; 3 of 3 points passed. Approve opens the pull request unless you pick otherwise."
            foot={<><Keys keys={[["Y", "confirm"], ["↵", "approve"]]} /><span className="cu-grow" /><span className={`cu-split${at(3) ? " glow" : ""}`}><span className="cu-btn pri">Approve</span><span className="cu-btn pri"><ChevronDown size={13} aria-hidden="true" /></span></span></>}>
            {at(1) ? <Sent>Confirmed · one live call to the partner API gave 3 tries</Sent> : (
              <div className="cu-item">
                <p className="cu-k">Only you can confirm · Done means 2</p>
                <b>One live call to the partner API gave 3 tries</b>
                <p className="cu-itp">Agents may not call live services while checking.</p>
                <p className="cu-acts"><span className="cu-btn pri sm">I confirm</span><span className="cu-btn sm">Ask the agent to record it</span></p>
              </div>
            )}
            {at(2) ? <Sent>Fine · the retry delay lives in settings.ts</Sent> : (
              <div className="cu-item">
                <p className="cu-k">Decided by Claude Code while building · 1 flagged for you</p>
                <b>Moved the retry delay into settings.ts, which the sender already imports</b>
                <p className="cu-acts"><span className="cu-btn pri sm">Fine</span><span className="cu-btn sm">Ask why</span></p>
              </div>
            )}
          </YourTurn>
          <div className={`cu-menu ${show(4)}`}>
            <p className="first"><b>Approve and open a pull request</b><small>Its description follows this page, with the proof</small></p>
            <p><b>Approve only</b><small>You push and open it yourself</small></p>
            <p><b>Copy the git commands</b><small>Push the branch and open the pull request by hand</small></p>
          </div>
          <Walkthrough />
        </Frame>
      );
    }

    case "draw": {
      // The request and the drawn page, inside the Plan's question, from the first moment.
      return (
        <Frame label="Designs"
          top={<TopBar stage={2} chip={waits("waits for you")} activity={<AgentActivity title="Drew the page you asked for" note="1 min" sub="It drew one clickable page in your product’s look, and the Plan asks you about it." />} />}
          gate={<GateTrack items={[]} turn={at(2) ? undefined : "Your turn · 1 design"} />}>
          <YourTurn kind="Design · shown in the Plan" title="Is this how failed deliveries should look?" text={`You asked: “Mock up the ${DESIGN.name.toLowerCase()} page.”`}
            foot={<Keys keys={[["1", "looks right"], ["2", "change it"], ["F", "full size"]]} />}>
            <DesignIn><DesignPage brief /></DesignIn>
            <Choices items={[["Looks right"], ["Change it…", "say what to change, or point at a spot full size"]]} picked={at(1) ? 0 : -1} own={null} />
          </YourTurn>
        </Frame>
      );
    }

    case "comment":
      return (
        <Frame label="Comment"
          top={<TopBar stage={2} chip={at(2) && !at(3) ? works("changing the design") : waits("waits for you")} />}
          gate={<div className="cu-gt"><span className="cu-g done"><Image size={13} aria-hidden="true" />failed-deliveries · full size</span><span className="cu-grow" /><span className={`cu-btn sm${!at(2) ? " on" : ""}`}><MessageSquare size={12} aria-hidden="true" />Comment <kbd>C</kbd></span></div>}>
          {!at(2) && <p className="cu-mode"><b>Comment</b><span>Click a spot on the design</span><kbd>Esc</kbd></p>}
          <div className="cu-dzf big"><DesignPage tries={tries} onRetry={onRetry} pin={at(1)} next={at(3)} /></div>
          {at(1) && !at(2) && <div className="cu-compose"><p className="cu-k">You · on invoice.sent</p><span className="cu-field">Say when it tries next.</span><span className={`cu-btn pri sm${step === 1 ? " press" : ""}`}>Comment</span></div>}
          {at(2) && (
            <section className="cu-th">
              <div className="cu-msg"><span className="cu-pin">1</span><p><b>You</b> Say when it tries next.</p></div>
              <div className={`cu-msg ${show(3)}`}><Mk k="done" /><p><b>Claude Code</b> Each failed row now says when it tries next.</p></div>
            </section>
          )}
        </Frame>
      );

    case "ask":
      return (
        <Frame label="Ask"
          top={<TopBar stage={2} chip={waits("waits for you")} />}
          gate={<GateTrack items={[{ label: "Done means · 3", state: "done" }, { label: "Decisions · 2 of 2", state: "done" }, { label: "Team · Dana", state: "cur", pips: [at(4) ? 1 : 0, 1] }, { label: "Approve" }]} turn={at(2) && !at(4) ? undefined : "Your turn · approve"} />}>
          <section className="cu-doc">
            <p className="cu-k">03-plan.md · Decided by the agent</p>
            <p>A failed delivery is sent again <mark>one minute apart</mark>, three times, then the customer gets one mail.</p>
          </section>
          {!at(2) && (
            <section className="cu-pop">
              <b>Ask the team about this passage</b>
              <span className="cu-people"><span className="on"><i>D</i>Dana</span><span><i>B</i>Ben</span><span><i>C</i>Chen</span></span>
              <span className="cu-field">Is one minute right for the partner API?</span>
              <p className="cu-acts"><span className="cu-k">Needed before approval</span><span className="cu-sw on" /><span className="cu-grow" /><span className={`cu-btn pri sm${step === 1 ? " press" : ""}`}><Send size={12} aria-hidden="true" />Ask Dana</span></p>
            </section>
          )}
          {at(2) && (
            <section className="cu-th">
              <p className="cu-thq">You asked <b>Dana</b> · needed before approval · Slack message sent</p>
              <div className="cu-msg"><i className="cu-av">M</i><p><b>You</b> Is one minute right for the partner API?</p></div>
              {at(3) && <div className="cu-msg"><i className="cu-av">D</i><p><b>Dana</b> <span className="cu-via">via Claude Code</span> <span className="cu-k">suggests a change</span><br />Back off instead: 1, 5, then 15 minutes. The partner API limits retries.</p></div>}
              {at(4) && <p className="cu-thf"><Mk k="done" />Claude Code updated the passage · approve when you are ready</p>}
            </section>
          )}
        </Frame>
      );

    case "answer": {
      // The question with its passage in view from the first moment; your agent's draft waits, not sent, for your yes.
      return (
        <Frame label="Questions for you"
          top={<TopBar stage={-1} title="Team" kind="Ritter Labs · Dana’s App" chip={null} />}
          gate={<GateTrack items={[]} turn="Your turn · 2 questions" />}>
          <YourTurn kind="Question from Max Ritter · 25 min ago" count="1 of 2" title="“Is one minute right for the partner API?”" text={<>Retry failed webhooks · Plan · <b>needed before approval</b></>}
            foot={<Keys keys={[["1", "looks right"], ["2", "suggest a change"], ["R", "reply"]]} />}>
            <p className="cu-quote">A failed delivery is sent again <mark>one minute apart</mark>, three times, then the customer gets one mail.</p>
            <Choices items={[["Looks right"], ["Suggest a change"], ["Reply"]]} rec={-1} picked={at(1) ? 1 : -1} own="Or hand it to someone else…" />
            <div className={`cu-draft ${show(2)}`}>
              <p className="cu-k"><Mk k="work" />Draft by your Claude Code · not sent yet</p>
              <p>Back off instead: 1, 5, then 15 minutes. The partner API limits retries.</p>
              <p className="cu-acts"><span className="cu-btn pri sm">Send the draft</span><span className="cu-btn sm">Edit</span></p>
            </div>
          </YourTurn>
        </Frame>
      );
    }

    case "space":
      return (
        <Frame label="Team space"
          top={<TopBar stage={-1} title="Team" kind="Ritter Labs · 4 members" chip={null} />}
          gate={<GateTrack items={[{ label: "Questions for you · 0", state: "done" }, { label: "Your questions to others · 2", state: "cur" }, { label: "Working now · 3" }]} />}>
          <section className="cu-card">
            <p className="cu-cardh"><b>Your questions to others</b><span className="cu-k">2</span></p>
            <p className="cu-tr"><i className="cu-av">D</i><span><b>Dana</b> · a passage in Retry failed webhooks</span><span className="cu-k">answered · suggests a change</span></p>
            <p className="cu-tr"><i className="cu-av amb">B</i><span><b>Ben</b> · the diagram in Billing export</span><span className="cu-k you">waiting a day · {at(2) ? "reminded just now" : "reminded 2 h ago"}</span><span className="cu-acts"><span className={`cu-btn sm${step === 1 ? " press" : ""}`}>Remind</span><span className="cu-btn sm">Hand to…</span></span></p>
          </section>
          <section className="cu-card">
            <p className="cu-cardh"><b>Working now</b><span className="cu-k">3</span></p>
            {([["A", "Billing export", "Implement · slice 2 of 3", "Codex", "work"], ["B", "Invoice PDFs", "Verify · checking 18 of 24", "Claude Code", "work"], ["C", "SSO group sync", "Plan · waits for Chen", "Claude Code", "you"]] as const).map(([av, task, where, agent, mark]) => (
              <p key={task} className="cu-tr"><i className="cu-av">{av}</i><span><b>{task}</b></span><span className="cu-tw"><Mk k={mark} />{where}</span><span className="cu-k">{agent}</span></p>
            ))}
          </section>
          <p className="cu-fold"><b>Team activity</b><span className="cu-k">today · 2 Plans approved · 1 shipped · 5 answers</span><ChevronRight size={14} aria-hidden="true" /></p>
        </Frame>
      );

    case "together": {
      const ready = at(2);
      return (
        <Frame label="Review together"
          top={<TopBar stage={6} chip={waits("waits for your review")} />}
          gate={<GateTrack items={[{ label: "What you get · 3 points", state: "done" }, { label: "Teammates · 2", state: ready ? "done" : "cur", pips: [ready ? 2 : 1, 2] }, { label: "Approve", state: ready ? "cur" : undefined }]} turn={ready ? "Your turn · approve" : "Your turn · 1 comment"} />}>
          <YourTurn kind={ready ? "then the pull request" : "Comment from Ben · Done means 3"} title={ready ? "Ready to approve" : "Can support see the count without opening the log?"}
            foot={ready ? <><span className="cu-votes"><span><b>Dana</b> approved</span><span><b>Ben</b> commented</span></span><span className="cu-grow" /><span className="cu-split glow"><span className="cu-btn pri">Approve</span><span className="cu-btn pri"><ChevronDown size={13} aria-hidden="true" /></span></span></> : <Keys keys={[["R", "reply"], ["E", "resolve"]]} />}>
            <div className="cu-proof">
              <p className="cu-k"><Mk k="check" />Done means 3 · Support sees the retry count · screenshot 2</p>
              <DesignPage tries={3} />
            </div>
            <section className="cu-th">
              <div className="cu-msg"><i className="cu-av">B</i><p><b>Ben</b> <span className="cu-k">teammate</span><br />Can support see this without the log?</p></div>
              <div className={`cu-msg ${show(1)}`}><Mk k="done" /><p><b>Claude Code</b><br />Yes, each row shows the try count. Screenshot 2 proves it.</p></div>
            </section>
          </YourTurn>
        </Frame>
      );
    }

    case "settings":
      return (
        <Frame label="Settings"
          top={<TopBar stage={-1} title="Settings" kind="every project on this computer" chip={null} />}
          gate={<div className="cu-gt"><span className="cu-seg"><span className="on">Workflow</span><span>Licence</span><span>Team</span><span>About</span></span></div>}>
          <div className="cu-two">
            <div className="cu-col">
              <section className="cu-card">
                <p className="cu-cardh"><b>Planning defaults</b><span className="cu-k">Discuss, Research, Plan, Outline</span></p>
                <p className="cu-set"><span>Agent</span><span className="cu-seg"><span className="on">Claude Code</span><span>Codex</span></span></p>
                <p className="cu-set"><span>Model</span><span className="cu-sel">Opus 5.5</span></p>
                <p className="cu-set"><span>Effort</span><span className="cu-sel">High</span></p>
                <p className="cu-set"><span>Starts in</span><span className="cu-sel">This session</span></p>
              </section>
              <section className="cu-card">
                <p className="cu-cardh"><b>Build defaults</b><span className="cu-k">Implement</span></p>
                <p className="cu-set"><span>Agent</span><span className="cu-seg"><span className={at(1) ? "" : "on"}>Claude Code</span><span className={at(1) ? "on" : ""}>Codex</span></span></p>
                <p className="cu-set"><span>Plans each slice</span><span className="cu-sel">Opus 5.5</span></p>
                <p className="cu-set"><span>Builds</span><span className="cu-sel">{at(1) ? "GPT-6.1 Sol" : "Sonnet 5.5"}</span></p>
                <p className="cu-set"><span>Checks it<small>never wrote the code</small></span><span className="cu-sel">{at(1) ? "Opus 5.5" : "GPT-6.1 Sol"}</span></p>
              </section>
            </div>
            <section className="cu-card cu-cost">
              <p className="cu-cardh"><b>Retry failed webhooks</b><span className="cu-k">estimated at list price</span></p>
              <p className="cu-amt"><b>$20.95</b><span className="cu-k">1 h 17 min</span></p>
              <span className="cu-cbar">{COST.map(([label, , cost, color]) => <i key={label} style={{ background: color, flexGrow: Number(cost.slice(1)) }} />)}</span>
              {COST.map(([label, time, cost, color]) => (
                <p key={label} className="cu-ctr"><span><i style={{ background: color }} />{label}</span><span>{time}</span><span>{cost}</span></p>
              ))}
            </section>
          </div>
        </Frame>
      );

    case "agents":
      return (
        <Frame label="New task"
          top={<TopBar stage={-1} title="Home" kind="your tasks on this computer" chip={null} />}
          gate={<div className="cu-gt"><span className="cu-g done">Your turn · 1</span><span className="cu-g done">Running · 1</span><span className="cu-g done">Shipped · 4</span><span className="cu-grow" /><span className="cu-btn sm on"><Plus size={13} aria-hidden="true" />New task</span></div>}>
          <section className="cu-card cu-new">
            <p className="cu-cardh"><b>New task</b><span className="cu-k">starts in your coding agent</span></p>
            <div className="cu-newb">
              <span className="cu-seg"><span className="on">Claude Code</span><span>Codex</span><span>Another agent</span></span>
              <span className="cu-field">{REQUEST}</span>
              <p className="cu-defs"><span><span className="cu-k">Model</span> Opus 5.5</span><span><span className="cu-k">Effort</span> High</span><span><span className="cu-k">Starts in</span> a new session</span><span className="cu-lnk">Change</span></p>
              <div className="cu-cmd"><code>claude --model opus --effort high "/ql {REQUEST}"</code><span className={`cu-btn pri sm${step === 1 ? " press" : ""}`}>{at(2) ? <Check size={12} aria-hidden="true" /> : <Copy size={12} aria-hidden="true" />}{at(2) ? "Copied" : "Copy"}</span></div>
            </div>
          </section>
          <p className="cu-runs"><span className="cu-k">The App runs on</span><span>macOS</span><span>Windows</span><span>Linux</span><span className="cu-k">and opens in your browser on a server or in WSL</span></p>
          <p className={`cu-notif ${show(3)}`}><span aria-hidden="true" className="sx-mark" /><span><small>QualityLayer · from the menu bar</small>Retry failed webhooks needs your review</span><ArrowRight size={14} aria-hidden="true" /></p>
        </Frame>
      );

    default:
      return null;
  }
}
