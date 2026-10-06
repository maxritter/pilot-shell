import { ArrowDown, ArrowUpRight, ChevronDown, ChevronRight, Copy, Expand, FileText, Frame, GitBranch, Infinity as Loop, Lock, MessageSquare, PanelRight, Search, SlidersHorizontal, SquarePlus, X } from "lucide-react";
import { Children, type ReactNode } from "react";
import { checksPassed, committedTasks, DESIGN, questionsLeft, REQUEST } from "@/lib/tour";

/**
 * The scenes inside the App window, one per chapter, drawn from the App's own screens: the
 * question card, the step's page with its marked sections, Implement Start, the build, the
 * checklist, the Approve card, designs full size, the Team space, Settings and "+ New". Each
 * scene's parts appear one per moment: `ins(n)` and `at(n)` switch at moment n.
 */

const Tick = () => (
  <svg className="sx-tick" viewBox="0 0 12 12" aria-hidden="true">
    <path d="M2.5 6.2 5 8.7l4.5-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

/** The violet line: what the agents proved, in at most five facts. */
function Violet({ head = "Checked by agents", facts, className = "" }: { head?: string; facts: string[]; className?: string }) {
  return (
    <div className={`sx-vio ${className}`}>
      <i aria-hidden="true" className="sx-dm" /><b>{head}</b>
      {facts.map((f) => <span key={f}>{f}</span>)}
      <ChevronDown size={14} aria-hidden="true" />
    </div>
  );
}

/** A closed part of a step: one line, opened on demand. */
function Fold({ title, meta, className = "", violet = false, live = false }: { title: string; meta: string; className?: string; violet?: boolean; live?: boolean }) {
  return (
    <div className={`sx-fl ${className}`}>
      <i aria-hidden="true" className={violet ? "sx-dm" : live ? "sx-ag" : "sx-ok"} /><b>{title}</b><span>{meta}</span><ChevronRight size={14} aria-hidden="true" />
    </div>
  );
}

/** One place for the person's actions, with the rest of the batch in the same card. */
function Turn({ title, meta, children, className = "" }: { title: string; meta?: string; children: ReactNode; className?: string }) {
  return (
    <section className={`sx-turn ${className}`}>
      <div className="sx-turn-label"><i className="sx-you" />Your turn</div>
      <div className="sx-turn-head"><b>{title}</b>{meta && <small>{meta}</small>}</div>
      {children}
    </section>
  );
}

function AgentTurn({ title, doing, next }: { title: string; doing: string; next: string }) {
  return <section className="sx-agent-turn"><p><i className="sx-ag" /><b>Claude Code’s turn</b></p><strong>{title}</strong><span>{doing}</span><div><small>Next for you</small><span>{next}</span></div></section>;
}

function DocHead({ name, file }: { name: string; file: string }) {
  return <div className="sx-dochead"><b>{name}</b><span><FileText size={11} />{file}</span><PanelRight size={13} /><Expand size={13} /></div>;
}

/** One choice of the card: its number key, the words, and the recommended mark with Enter. */
function Choice({ n, label, rec = false, pick = false, className = "" }: { n: number; label: string; rec?: boolean; pick?: boolean; className?: string }) {
  return (
    <span className={`sx-qo${rec ? " rec" : ""}${pick ? " pick" : ""} ${className}`}>
      <kbd>{n}</kbd><b>{label}</b>{rec && <><em>Recommended</em><small className="sx-hide">↵ Enter</small></>}
    </span>
  );
}

const QUESTIONS = [
  { n: 3, title: "How many tries before it stops?", answer: "3 tries, then one mail", other: "5 tries, then one mail" },
  { n: 4, title: "Who hears about it when it stops?", answer: "The customer, in one mail", other: "Support, in a Slack channel" },
  { n: 5, title: "When does it try again?", answer: "A minute apart", other: "Five minutes apart" },
];

/** The second question is answered first, then the first: order is the person's choice. */
function DiscussBatch({ step }: { step: number }) {
  const left = questionsLeft(step);
  const answered = (n: number) => n === 4 ? step >= 3 : n === 3 ? step >= 4 : step >= 5;
  const open = step < 3 ? 4 : step < 4 ? 3 : 5;
  const active = QUESTIONS.find((q) => q.n === open)!;
  return <div className="sx-nowdoc">
    <div className="sx-turn-column">
      {left ? <Turn title={`${left} ${left === 1 ? "question" : "questions"} from Claude Code`} meta={`${3 - left} of 3 answered`}>
        <p className="sx-turn-intro">Answer in any order. Claude Code keeps reading the code.</p>
        <div className="sx-batch-open sx-arrive" key={open}>
          <small>Question {open} · settles Done means {open === 5 ? 1 : 2}</small>
          <h4>{active.title}</h4>
          <div className="sx-qos"><Choice n={1} label={active.answer} rec pick={step === 2} /><Choice n={2} label={active.other} />
            <span className="sx-qown"><span>Your own answer</span><kbd>Tab</kbd></span>
          </div>
          <div className="sx-qf"><span className="sx-qmore"><Search size={12} />Tell me more</span><u>Not sure</u></div>
        </div>
        {QUESTIONS.filter((q) => !answered(q.n) && q.n !== open).map((q) => <div className="sx-batch-row" key={q.n}><small>{q.n}</small><span>{q.title}</span><ChevronRight size={12} /></div>)}
        <p className="sx-turn-foot">Each answer reaches your agent at once.</p>
      </Turn> : <AgentTurn title="Turning your answers into Done means" doing="All 3 answered. Reading the delivery code, then writing the agreed result." next="Agree to Done means, point by point." />}
      {step >= 3 && step < 5 && <div className="sx-undo"><Tick /><span>Answer sent</span><u>Undo · 5 s</u></div>}
      {left > 0 && <p className="sx-meanwhile"><i className="sx-ag" />Meanwhile, reading notify.ts</p>}
    </div>
    <div className="sx-document">
      <DocHead name="Discuss" file="01-discuss.md" />
      <p className="sx-ph2">Problem</p><p className="sx-docpara">A failed webhook is lost. Retry it, then tell the customer if it still fails.</p>
      <p className="sx-ph2">Done means <small>3 points</small></p>
      <div className="sx-point-list"><div><small>1</small><span>Failed deliveries are retried.</span></div><div><small>2</small><span>It stops after 3 tries and mails once.</span></div><div><small>3</small><span>Support sees the retry count.</span></div></div>
      <p className="sx-ph2">Decided with you <small>{5 - left}</small></p>
      <div className="sx-decided">
        {QUESTIONS.filter((q) => answered(q.n)).reverse().map((q) => <div key={q.n}><small>{q.title}</small><b>{q.answer}</b><u>Change</u></div>)}
        {left > 0 ? <><div><small>Which deliveries count as failed?</small><b>Any answer but 2xx</b><u>Change</u></div><div><small>Where should support see them?</small><b>The deliveries page</b><u>Change</u></div></> : <div className="sx-earlier-decisions"><small>2 earlier answers</small><ChevronDown size={12} /></div>}
      </div>
    </div>
  </div>;
}

function PlanScene({ step }: { step: number }) {
  const full = step >= 4;
  const allAgreed = step >= 3;
  return <div className={full ? "sx-plan-reader sx-arrive" : "sx-nowdoc"}>
    <div className={full ? "sx-plan-outline" : "sx-turn-column"}>
      <Turn title={allAgreed ? "Everything is settled" : `Agree to ${step >= 2 ? 1 : 2} points`} meta={allAgreed ? "3 points agreed" : "Done means"}>
        {allAgreed ? <><p className="sx-turn-intro">Read the Plan and its comments, then approve.</p><div className="sx-turn-actions"><span className="sx-fake p">Approve Plan</span></div></> : <>
          <div className="sx-batch-open">
            <small>Done means 2 · changed since you agreed</small><h4>Is the new wording still what you mean?</h4>
            <div className="sx-wasnow"><small>Was</small><s>It stops after 3 tries.</s><small>Now</small><span>It stops after 3 tries and <mark>mails the customer once.</mark></span></div>
            <p className="sx-docpara">Your other agreed point stays agreed.</p>
            <div className="sx-turn-actions"><span className={`sx-fake p sm${step === 3 ? " press" : ""}`}>Agree</span><span className="sx-fake sm">Change</span></div>
          </div>
          {step < 2 && <div className="sx-batch-row"><small>3</small><span>Support sees the retry count.</span><span className={`sx-fake sm${step === 1 ? " press" : ""}`}>Agree</span></div>}
        </>}
      </Turn>
      {full && <nav className="sx-outline"><b>On this page</b><span>Done means</span><span>Engineering decisions</span><span className="on">Slices · 3</span><span>Risks</span><span>Not doing</span></nav>}
    </div>
    <div className={`sx-document${full ? " sx-full-document" : ""}`}>
      <DocHead name={full ? "Exit full size" : "Plan · Read in full"} file="02-plan.md" />
      <h4 className="sx-plan-title">Plan: Retry failed webhooks</h4><p className="sx-docby">Written by Claude Code · read by Codex</p>
      {!full ? <>
        <p className="sx-ph2">Done means <small>{allAgreed ? "3 agreed" : step >= 2 ? "2 agreed · 1 changed" : "1 agreed · 1 changed"}</small></p>
        <div className="sx-point-list"><div><small>1</small><span>Failed deliveries are retried.</span><em>Agreed</em></div><div><small>2</small><span>It stops after 3 tries and mails once.</span><em>{allAgreed ? "Agreed" : "Changed"}</em></div><div><small>3</small><span>Support sees the retry count.</span><em>{step >= 2 ? "Agreed" : "Agree next"}</em></div></div>
        <p className="sx-ph2">Engineering decisions</p><p className="sx-docpara">Retry the delivery from a queue. After the third try, mail the customer once.</p><Decision />
        <Violet head="Codex read the Plan" facts={["5 tasks · test first"]} />
      </> : <>
        <p className="sx-ph2">Slices</p><h4>Slice 1 · Queue failed deliveries</h4><p className="sx-docpara">Keep each failed delivery once, ready to try again.</p>
        <h4>Slice 2 · Three tries, then one mail</h4><p className="sx-docpara sx-line-quote"><span className="sx-cpin">1</span><mark>Count every attempt, including the first delivery. Stop after the third and mail the customer once.</mark></p>
        <ol className="sx-plan-tasks"><li>Test the retry limit first</li><li>Send one mail when it stops</li></ol>
        <h4>Slice 3 · Show the retry count</h4><p className="sx-docpara">Support sees the count in each delivery row.</p>
        <div className="sx-phone-comment"><MessageSquare size={12} /><b>You, on slice 2</b><span>Count the first delivery too.</span></div>
      </>}
    </div>
    {full && <aside className="sx-line-comment"><div className="sx-reader-tabs"><b>Comments 1</b><span>Files</span><span>Designs</span></div><small>On slice 2</small><blockquote>“Count every attempt, including the first delivery.”</blockquote><p><b>You</b><small>just now</small></p><p>Count the first delivery too.</p><p className="sx-comment-reply"><b>Claude Code</b><span>The limit includes it. I’ll test that explicitly.</span></p><div className="sx-comment-links"><u>Reply</u><u>Resolve</u></div></aside>}
  </div>;
}

/**
 * The page an agent drew for this task: a mock of the product's failed deliveries, drawn the way
 * the person's own product might look. `next` adds the change the comment asked for. Full size, its
 * Retry button works: three tries and the delivery stops and mails the customer.
 */
function DesignPage({ next = false, pin = false, tries = 2, onRetry, className = "" }: { next?: boolean; pin?: boolean; tries?: number; onRetry?: () => void; className?: string }) {
  const stopped = tries >= 3;
  const rows: [string, string, string, string?][] = [
    ["order.paid", "/hooks/orders", "Delivered"],
    ["invoice.sent", "/hooks/billing", stopped ? "Stopped, mailed" : `Try ${tries} of 3`, stopped ? undefined : "next try 14:05"],
    ["refund.issued", "/hooks/billing", "Stopped, mailed"],
    ["customer.updated", "/hooks/crm", "Delivered"],
  ];
  return (
    <div className={`sx-dp ${className}`}>
      <div className="sx-dph"><b>Deliveries</b><span className="sx-dptabs"><span>All</span><span className="on">Failed · 2</span></span></div>
      <div className="sx-dpt">
        <div className="sx-dpr hd"><span>Event</span><span>Endpoint</span><span>Status</span><span /></div>
        {rows.map(([event, url, state, extra]) => (
          <div key={event} className={`sx-dpr${extra && next ? " new" : ""}`}>
            <span className="sx-code">{event}</span>
            <span className="sx-code dim">{url}</span>
            <span className={state.startsWith("Try") ? "sx-amb" : state.startsWith("Stopped") ? "sx-red" : ""}>
              {state}{extra && next && <small> · {extra}</small>}
              {event === "invoice.sent" && pin && <span className="sx-cpin sx-dpin">1</span>}
            </span>
            <span>
              {event === "invoice.sent" &&
                (onRetry ? (
                  <button type="button" onClick={onRetry} disabled={stopped} tabIndex={-1} className="sx-dpbtn">Retry</button>
                ) : (
                  <span className="sx-dpbtn">Retry</span>
                ))}
            </span>
          </div>
        ))}
      </div>
      <div className="sx-dpf">
        <div><b>How retries work</b><span>Three tries, a minute apart. Then the customer gets one mail and the delivery stops.</span></div>
        <div><b>Mail to the customer</b><span>“We could not deliver invoice.sent to /hooks/billing. Check the endpoint, then retry it here.”</span></div>
      </div>
    </div>
  );
}

const SLICES = [
  { title: "Failed deliveries go to a retry queue", tasks: 2, doing: "writing the failing test: a failed delivery is queued once", first: 1 },
  { title: "Three tries, then mail the customer", tasks: 2, doing: "running delivery.test.ts and mailer.test.ts · 49 s", first: 3 },
  { title: "Retry count in the delivery row", tasks: 1, doing: "running row.test.tsx", first: 5 },
];
/** When a slice starts running and when it is committed (moments of the Implement scene). */
const SLICE_RUN = [1, 3, 1];
const SLICE_DONE = [3, 100, 4];

/** The Plan's second engineering decision as a diagram: the retry queue, the three tries, the one mail. */
function Decision({ live = false }: { live?: boolean }) {
  return (
    <div className="sx-dg">
      <div className="sx-dgr">
        <span className="sx-node hl"><i className="sx-ic" />Retry queue</span><span className="sx-edge" />
        <span className="sx-diaw"><span className="sx-dia" /><b>try &lt; 3?</b></span>
        <span className="sx-edge"><em>yes</em></span>
        <span className="sx-node ok"><i className="sx-ic" />Send again</span>
      </div>
      <div className="sx-dgd"><span className="sx-down">no</span><span className="sx-node"><i className="sx-ic" />Mail the customer</span></div>
      <span className={`sx-pkt${live ? " on" : ""}`} />
    </div>
  );
}

/** The checks of the Verify scene: its section, label, and the moment it passes. Each runs for the moment before. */
const CHECKS: { group: string; note?: string; items: [string, number, string?][] }[] = [
  { group: "Project checks", note: "4 of 4, recorded at 5a4a12d", items: [["Test suite · 412 pass", 2], ["Types", 2], ["Lint", 2], ["Build", 2]] },
  { group: "Scenarios", note: "run end to end", items: [["1 · A failed delivery is retried", 2], ["2 · Stops after 3 tries, mails once", 3, "part 2"], ["3 · Support sees the retry count", 4, "part 3"]] },
  { group: "Done means", note: "each point against the diff and the running program", items: [["1 · Failed deliveries are retried", 3], ["2 · It stops after 3 tries", 4], ["3 · Support sees the count", 5]] },
  { group: "Code review", items: [["Every changed file against its task", 6]] },
];
const TOTAL_CHECKS = 12;

const COST: [string, string, string, string][] = [
  ["Discuss", "12 min", "$2.10", "var(--ql-text-dim)"],
  ["Plan", "18 min", "$3.85", "var(--ql-amber)"],
  ["Implement", "26 min", "$9.40", "var(--ql-accent)"],
  ["Verify", "21 min", "$5.60", "var(--ql-check)"],
];

/** A setting's row in a defaults card: what it is, why, and its picker. */
const Def = ({ label, why, value }: { label: string; why: string; value: string }) => (
  <div className="sx-defr"><b>{label}</b><small className="sx-hide">{why}</small><span className="sx-sel">{value}<em className="sx-hide">recommended</em></span></div>
);

/** The agent tabs at the top of a defaults card; the default one is marked. */
const AgentTabs = () => (
  <div className="sx-atabs"><span className="on">Claude Code<em>Default</em></span><span>Codex</span><span className="sx-hide">Another agent</span><small className="sx-hide"><Tick />Recommended setup</small></div>
);

/** The right sidebar of a task chapter: Comments or Designs, the interactive parts of a task. */
export function RightSide({ ch, step, tab }: { ch: number; step: number; tab: "comments" | "designs" }) {
  const at = (n: number) => step >= n;
  const ins = (n: number) => `sx-in${at(n) ? " on" : ""}`;
  return (
    <aside className="sx-rs">
      <div className="sx-rsh">
        <span className="sx-rseg">
          <span className={tab === "comments" ? "on" : ""}>Comments{tab === "comments" && !at(4) && <b>1</b>}</span>
          <span>Files</span>
          <span className={tab === "designs" ? "on" : ""}>Designs{tab === "designs" && <i className="sx-ndot" />}</span>
        </span>
        <span className="sx-dicon"><PanelRight size={13} /></span>
      </div>
      {tab === "designs" ? (
        <>
          <p className="sx-lock"><Lock size={12} aria-hidden="true" /><span><b>Interactive page stays here.</b> Share links include a still.</span></p>
          <p className="sx-rsg"><span>This task</span><b>1</b></p>
          <div className={`sx-drow on ${ins(1)}`}>
            <span className="sx-thumb"><DesignPage className="mini" /></span>
            <span className="sx-drt">
              <b>{DESIGN.name}{at(1) && <i className="sx-ndot" />}</b>
              <small>{DESIGN.purpose}</small>
              <em>Updated just now</em>
              <span className="sx-plan">Shown in the Plan</span>
            </span>
          </div>
          <p className="sx-rsg"><span>In this project</span><b>2</b></p>
          <div className="sx-drow">
            <span className="sx-thumb blank"><Frame size={14} /></span>
            <span className="sx-drt"><b>Settings page</b><small>Every setting on one page</small><em>Updated yesterday <MessageSquare size={11} /> 1</em></span>
          </div>
          <div className="sx-drow">
            <span className="sx-thumb blank"><Frame size={14} /></span>
            <span className="sx-drt"><b>Onboarding</b><small>The first start, step by step</small><em>Updated 3 days ago</em></span>
          </div>
          <p className="sx-rsf">Ask your agent to draw one: “mock up the settings page”.</p>
        </>
      ) : (
        <>
          <p className="sx-rsg"><span>Open on Review</span><b>{at(4) ? 0 : 1}</b></p>
          <div className={`sx-cm ${ins(1)}${at(4) ? " done" : ""}`}>
            <p className="sx-cmh"><span className="sx-av b">BC</span><b>Ben Chen</b><small>11:02</small></p>
            <p className="sx-cmref"><span className="sx-cpin">1</span>Done means · point 3<ArrowDown size={11} /></p>
            <p className="sx-cmt">Can support see the count without opening the log?</p>
            <p className={`sx-cmr ${ins(3)}`}><i className="sx-ag" /><span><b>Claude Code</b> Yes, each row shows the try count. Screenshot 2 proves it.</span></p>
            <p className="sx-cml">{at(4) ? <span>Resolved by you</span> : <><u>Reply</u><u>Resolve</u></>}</p>
          </div>
          <p className="sx-rsg"><span>Resolved</span><b>{at(4) ? 3 : 2}</b><ChevronDown size={12} /></p>
          <div className="sx-rsc"><span>Comment on the review. Select words in the page to quote them.</span><span className="sx-fake sm">Add comment</span></div>
        </>
      )}
    </aside>
  );
}

/** `only` renders just chapter `ch`'s scene, for the windows that sit inline beside each chapter. */
export default function TourScenes({ ch, step, tries, onRetry, only = false }: { ch: number; step: number; tries: number; onRetry: () => void; only?: boolean }) {
  const at = (n: number) => step >= n;
  const ins = (n: number) => `sx-in${at(n) ? " on" : ""}`;
  const scene = (k: number) => `sx-sc${ch === k ? " on" : ""}`;
  // Chapters other than their own show a scene finished, so a jump never lands on a half-built window.
  const t = (k: number) => (ch === k ? step : 99);

  const vt = t(4);
  const passed = checksPassed(vt);
  const checking = vt < 7;
  const it = t(3);
  const committed = committedTasks(it);
  const pt = t(1);
  const rv = t(5);
  const cm = t(7);
  const tg = t(11);

  const scenes = (
    <>
      {/* Discuss: the batch shrinks as answers arrive; the document records each decision. */}
      <div className={scene(0)} aria-hidden={ch !== 0}><DiscussBatch step={t(0)} /></div>

      {/* Plan: agree point by point, then read the document full size with a line comment. */}
      <div className={scene(1)} aria-hidden={ch !== 1}><PlanScene step={pt} /></div>

      {/* Implement Start: your Build defaults drawn as the build, one effort for both, one command. */}
      <div className={scene(2)} aria-hidden={ch !== 2}>
        <Turn title="Start the build" meta="Run the command below">
        <section className="sx-ist">
          <div className="sx-isth"><b>Build with</b><span className="sx-seg3"><span className="on">Claude Code</span><span>Codex</span><span className="sx-hide">Another agent</span></span><small className="sx-hide"><Tick />Recommended setup</small></div>
          <div className={`sx-nodes ${ins(1)}`}>
            <div className="sx-bnode"><p>Orchestrator</p><span className="sx-sel">Opus 5.5</span><small>Coordinates · writes no code</small></div>
            <span className="sx-bedge"><em>3 slices</em></span>
            <div className="sx-bnode"><p>Workers</p><span className="sx-sel">Sonnet 5.5</span><small>Write the code, a slice each</small></div>
          </div>
          <div className={`sx-eff ${ins(1)}`}><span>Effort for both</span><span className="sx-seg3"><span>Medium</span><span className="on">High</span><span>Extra high</span></span></div>
          <div className="sx-isto sx-hide"><span><Loop size={12} />Goal</span><span><SquarePlus size={12} />This session</span><span className="sx-adj"><SlidersHorizontal size={12} />Adjust<ChevronDown size={11} /></span></div>
          <div className={`sx-istc ${ins(2)}`}>
            <p className="sx-hide">In the session that planned it, type these first, one at a time</p>
            <div className="sx-lines sx-hide"><code>/clear<Copy size={10} /></code><code>/model opus<Copy size={10} /></code><code>/effort high<Copy size={10} /></code></div>
            <div className="sx-cmdb"><code>/goal /ql implement retry-webhooks</code><span className={`sx-fake p sm${ch === 2 && step === 3 ? " press" : ""}`}><Copy size={11} />{t(2) >= 3 ? "Copied" : "Copy"}</span></div>
          </div>
        </section>
        </Turn>
      </div>

      {/* Implement: the build on its own, slice by slice, test first; what the agent decided on the way. */}
      <div className={scene(3)} aria-hidden={ch !== 3}>
        <AgentTurn title={`Slice ${committed >= 2 ? 2 : 1} of 3 · task ${committed + 1} of 5`} doing="Nothing waits for you. The agents are building and running the tests." next="Review the finished change with its proof." />
        <div className={`sx-bld ${ins(0)}`}>
          {SLICES.map((s, k) => {
            const state = it >= SLICE_DONE[k] ? "done" : it >= SLICE_RUN[k] ? "run" : "wait";
            return (
              <div className={`sx-sr ${state}`} key={s.title}>
                <span className="sx-sn">{k + 1}</span>
                <span className="sx-st"><b>{s.title}</b>{state === "run" && <small>{s.doing}</small>}</span>
                <span className="sx-segs">{Array.from({ length: s.tasks }, (_, j) => <i key={j} className={state === "done" ? "done" : state === "run" && j === 0 ? "run" : ""} />)}</span>
                <span className="sx-sl2">{state === "done" ? (k === 0 ? "committed 08d634b" : "committed") : state === "run" ? `T${s.first}` : "after 1"}</span>
              </div>
            );
          })}
        </div>
        <div className={`sx-psec ${ins(4)}`}>
          <p className="sx-ph2">Decided while building <small>1</small></p>
          <div className="sx-dwb"><span className="sx-code dim">slice 1</span><span>Moved the retry delay into settings.ts, which the sender already imports.</span><u>Ask why</u></div>
        </div>
        <Fold title="Changes so far" meta="9 files · +214 −31 · grouped by task" live className={`sx-hide ${ins(5)}`} />
        <Violet facts={["2 tasks green, test first", "slice 1’s checks passed", "6 checks recorded"]} className={ins(5)} />
      </div>

      {/* Verify: every check listed from the start, filling in live; then all passed. */}
      <div className={scene(4)} aria-hidden={ch !== 4}>
        {checking ? (
          <>
            <AgentTurn title="Checking the change" doing={`${passed} of 12 checks passed. Agents that did not write the code check the result.`} next="Confirm what only you can check, in Review." />
            <div className="sx-vh">
              <b>{passed} of {TOTAL_CHECKS} checks passed</b>
              <span className="sx-bar2"><i className="v" style={{ width: `${(passed / TOTAL_CHECKS) * 100}%` }} /><i className="b" style={{ width: vt < 6 ? "8%" : "0%" }} /></span>
              <span className="sx-vm">polish 2 min · project checks 3 min · checking 4 min so far</span>
            </div>
            <div className="sx-chk">
              <div className="sx-cg">
                <p className="sx-cl">Before checking</p>
                <div className="sx-cr">
                  <span className="sx-ck"><span aria-hidden="true" className={vt >= 1 ? "sx-ok" : "sx-todo"} />Polish · 2 simplifications</span>
                  <span className="sx-ck mut"><span aria-hidden="true" className="sx-todo" />Security review · not needed</span>
                </div>
              </div>
              {CHECKS.map((g) => (
                <div className="sx-cg" key={g.group}>
                  <p className="sx-cl">{g.group}{g.note && <small> · {g.note}</small>}</p>
                  <div className="sx-cr">
                    {g.items.map(([label, when, part]) => {
                      const state = vt >= when ? "ok" : vt >= when - 1 ? "run" : "wait";
                      return (
                        <span className="sx-ck" key={label}>
                          <span aria-hidden="true" className={state === "ok" ? "sx-dm" : state === "run" ? "sx-ag" : "sx-todo"} />{label}{state === "run" && part && <em>{part}</em>}
                        </span>
                      );
                    })}
                  </div>
                </div>
              ))}
              <div className={`sx-now ${ins(2)}`}><b>Now</b>part 2 · scenario 2: fails a webhook three times · part 3 · Done 3: opens the delivery row</div>
            </div>
          </>
        ) : (
          <>
            <Violet facts={["12 of 12 passed", "412 tests", "3 agents that did not write the code"]} />
            <Turn title="Waiting for you in Review" meta="3 to answer">
            <div className="sx-wl">
              <div className="sx-wr"><span aria-hidden="true" className="sx-you" /><span><b>Only you can confirm: one live call to the partner API gave 3 tries</b><small>Done 2 asked for a live call. The agent made it while planning but did not keep the output.</small></span><em>no agent may call it</em></div>
              <div className="sx-wr"><span aria-hidden="true" className="sx-you" /><span><b>Look at the result: Failed deliveries as built</b></span><em>screenshot</em></div>
              <div className="sx-wr"><span aria-hidden="true" className="sx-you" /><span><b>The retry mail goes out in English only</b></span><em>note from the check</em></div>
            </div>
            </Turn>
            <Fold title="Scenarios" meta="3 of 3 · each with its output kept" violet />
            <Fold title="Done means" meta="3 of 3 · each with its evidence" violet />
            <Fold title="Project checks" meta="4 of 4 · tests, types, lint, build" violet className="sx-hide" />
          </>
        )}
      </div>

      {/* Review: what is settled with you, the proof, then "Approve the change?" and the ways to ship. */}
      <div className={scene(5)} aria-hidden={ch !== 5}>
        <Turn title={rv >= 3 ? "Approve the change?" : `Settle ${Math.max(0, 3 - rv)} things, then approve`} meta={`${Math.min(3, rv)} of 3 settled`}>
        <div className="sx-psec">
          <p className="sx-ph2">Settled with you <small>{Math.min(3, rv)} of 3</small></p>
          <div className="sx-stab">
            <div className={`sx-str${rv >= 1 ? " done" : ""}`}><span aria-hidden="true" className={rv >= 1 ? "sx-ok" : "sx-you"} /><span><small>Only you can confirm</small>One live call to the partner API gave 3 tries</span>{rv >= 1 ? <em><Tick />I confirm</em> : <span className="sx-iab"><span className="sx-fake sm first">I confirm</span><span className="sx-fake sm sx-hide">Ask the agent to record it</span></span>}</div>
            <div className={`sx-str${rv >= 2 ? " done" : ""}`}><span aria-hidden="true" className={rv >= 2 ? "sx-ok" : "sx-you"} /><span><small>Look at the result</small>{DESIGN.name} as built</span><span className="sx-mini sx-hide"><DesignPage className="mini" next /></span>{rv >= 2 ? <em><Tick />Looks right</em> : <span className="sx-iab"><span className="sx-fake sm first">Looks right</span><span className="sx-fake sm sx-hide">Change</span></span>}</div>
            <div className={`sx-str${rv >= 3 ? " done" : ""}`}><span aria-hidden="true" className={rv >= 3 ? "sx-ok" : "sx-you"} /><span><small>Found while checking</small>The retry mail goes out in English only</span>{rv >= 3 ? <em><Tick />Accept</em> : <span className="sx-iab"><span className="sx-fake sm first">Accept</span><span className="sx-fake sm sx-hide">Fix it</span></span>}</div>
          </div>
        </div>
        <div className={`sx-apw ${ins(4)}`}>
          <section className="sx-approval">
            <div className="sx-aqf"><span className="sx-hide">Approving ships it the way you pick. QualityLayer never merges.</span><span className={`sx-fake p split${rv >= 5 ? " glow" : ""}`}>Approve and open a pull request</span></div>
          </section>
          <div className={`sx-menu drop ${ins(5)}`}>
            <div className="sx-mi first"><b>Approve and open a pull request</b><small>05-review.md becomes its description, with the proof</small></div>
            <div className="sx-mi"><b>Approve only</b><small>You push and open it yourself</small></div>
            <div className="sx-mi"><b>Copy the git commands</b><small>Push the branch and open the pull request by hand</small></div>
          </div>
        </div>
        </Turn>
        <Violet facts={["3 of 3 points of Done means passed", "3 scenarios", "412 tests"]} className={ins(3)} />
      </div>

      {/* Designs, in the Plan: the preview of the design the Plan names, and its question. */}
      <div className={scene(6)} aria-hidden={ch !== 6}>
        <Turn title="Look at the design" meta="1 to answer"><div className={`sx-turn-actions ${ins(4)}`}><span>Is this how failed deliveries should look?</span><span className="sx-fake sm first">Looks right</span><span className="sx-fake sm">Change</span></div></Turn>
        <p className="sx-ptitle">Failed webhooks are retried, then the customer gets one mail</p>
        <div className={`sx-psec ${ins(2)}`}>
          <p className="sx-ph2">Interface</p>
          <div className="sx-prev">
            <div className="sx-prevc"><span className="sx-prevt">Preview</span><DesignPage className="prev" /></div>
            <div className="sx-prevf"><Frame size={13} aria-hidden="true" /><b>{DESIGN.name}</b><small className="sx-hide">Updated just now</small><span className="sx-fake sm">Open full size</span></div>
          </div>
        </div>
        <div className={`sx-toast ${ins(3)}`}><i className="sx-ndot" /><span><b>{DESIGN.name}</b> was updated</span><span className="sx-fake sm">Open</span><X size={12} aria-hidden="true" /></div>
      </div>

      {/* A design open full size: comment on a spot, and the agent changes the same page. */}
      <div className={`${scene(7)} sx-full`} aria-hidden={ch !== 7}>
        <div className="sx-canvas">
          <div className={`sx-cmode ${cm >= 1 && cm < 3 ? "sx-in on" : "sx-in"}`}><b>Comment</b><span>Click a spot on the design</span><kbd>Esc</kbd><span className="sx-hide">leaves</span></div>
          <DesignPage className="full" next={cm >= 4} pin={cm >= 2} tries={tries} onRetry={onRetry} />
          <div className={`sx-composer ${cm >= 2 && cm < 3 ? "sx-in on" : "sx-in"}`}>
            <p><b>You</b> on {DESIGN.name} · this spot</p>
            <span className="sx-field">Say when it tries next.</span>
            <div className="sx-row2"><small className="sx-hide">⌘↵ adds it</small><span className={`sx-fake sm p${ch === 7 && step === 2 ? " press" : ""}`}>Comment</span></div>
          </div>
          <div className={`sx-cbub ${cm >= 3 ? "sx-in on" : "sx-in"}`}>
            <p><span className="sx-cpin">1</span><b>You</b><span>Say when it tries next.</span></p>
            <p className={`sx-cmr ${ins(4)}`}><i className="sx-ag" /><span><b>Claude Code</b> Each failed row now says when it tries next.</span></p>
          </div>
          <div className={`sx-toast ${ins(4)}`}><i className="sx-ndot" /><span><b>{DESIGN.name}</b> was updated</span><span className="sx-fake sm">Open</span></div>
        </div>
      </div>

      {/* Plan 1c and 1d, Slack 1b: the question on a passage, and the Slack messages. */}
      <div className={scene(8)} aria-hidden={ch !== 8}>
        <div className={`sx-rev sx-hide ${ins(2)}`}>
          <span className="sx-who2"><span className="sx-av b">D</span>Dana · required · {at(5) ? "answered" : "reading"}</span>
          <span className="sx-who2"><span className="sx-av b">B</span>Ben · optional · approved</span>
          <span className="sx-lk">Ask someone else</span>
        </div>
        <div className="sx-two">
          <div className="sx-col">
            <div className="sx-pdoc sx-hide">
              <p className="sx-k">Plan · Decisions made for you</p>
              <p className="sx-para">A failed delivery is sent again <mark>one minute apart</mark>, three times, then the customer gets one mail.</p>
            </div>
            <Turn title="Ask about this passage" className={ins(1)}>
            <div className="sx-pop">
              <div className="sx-who"><span className={`sx-whoi ${at(1) ? "on" : ""}`}><span className="sx-av b">D</span>Dana</span><span className="sx-whoi"><span className="sx-av b">B</span>Ben</span><span className="sx-whoi"><span className="sx-av b">C</span>Chen</span></div>
              <span className="sx-field">Is one minute right for the partner API?</span>
              <span className={`sx-fake p${ch === 8 && step === 2 ? " press" : ""}`} style={{ alignSelf: "flex-start" }}>Send the question</span>
            </div>
            </Turn>
          </div>
          <div className="sx-col">
            <div className={`sx-slk ${ins(3)}`}>
              <span className="sx-slkm"><span className="sx-mark" /></span>
              <div>
                <p><b>QualityLayer</b> <small>APP · 10:42</small></p>
                <p>Max asked you on <b>Retry failed webhooks</b> · Plan · <i>needed before approval</i></p>
                <p className="sx-slq">Is one minute right for the partner API?</p>
                <u>Open the question in the QualityLayer App</u>
                <small>Or answer with your own agent: <code>/ql answer a7k2</code></small>
              </div>
            </div>
            <div className={`sx-slk sx-hide ${ins(4)}`}>
              <span className="sx-slkm"><span className="sx-mark" /></span>
              <div>
                <p><b>QualityLayer</b> <small>APP · 11:07</small></p>
                <p>Dana answered your question on <b>Retry failed webhooks</b> · suggests a change</p>
                <p className="sx-slq">Back off instead: 1, 5, then 15 minutes. The partner API limits retries.</p>
                <u>Open the answer in the QualityLayer App</u>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Team 1a, in Dana's App: Questions for you, her agent's draft, Send the draft. */}
      <div className={scene(9)} aria-hidden={ch !== 9}>
        <Turn title="Questions for you" meta={`${at(5) ? 1 : 2} open`} className={ins(1)}>
          {!at(5) && <>
          <div className="sx-q2">
            <span aria-hidden="true" className="sx-you" />
            <span className="sx-av b">MR</span>
            <div className="sx-itb">
              <p className="sx-ik">Max Ritter asked you about a passage in the Plan · Retry failed webhooks · needed before approval · 25 min ago</p>
              <p className="sx-iw">“Is one minute right for the partner API?”</p>
            </div>
            <div className="sx-iab"><span className="sx-fake sm first">Looks right</span><span className="sx-fake sm">Suggest a change</span></div>
          </div>
          <div className={`sx-psg ${ins(2)}`}><b>The passage:</b> “A failed delivery is sent again one minute apart, three times, then the customer gets one mail.”</div>
          <div className={`sx-lks ${ins(2)}`}>
            <span>Reply</span><span className={at(3) ? "on" : ""}>Draft with my agent</span><span>Hand to someone else</span><u>Open the Plan at this passage</u>
          </div>
          <div className={`sx-draft ${ins(4)}`}>
            <p className="sx-dh"><span className="sx-ag" />Draft by your Claude Code · not sent yet</p>
            <p>Back off instead: 1, 5, then 15 minutes. The partner API limits retries.</p>
            <div className="sx-row2"><span className={`sx-fake p sm${ch === 9 && step === 4 ? " press" : ""}`}>Send the draft</span><span className="sx-fake sm">Edit</span></div>
          </div>
          </>}
          <div className={`sx-q2 sx-sec ${ins(1)}`}>
            <span aria-hidden="true" className="sx-you" />
            <span className="sx-av b">AB</span>
            <div className="sx-itb">
              <p className="sx-ik">Anna Becker asked you about one diagram · Billing export · Plan · 2 h ago</p>
              <p className="sx-iw">“Is the retry queue a single point of failure?”</p>
            </div>
            <div className="sx-iab"><span className="sx-fake sm first">Looks right</span><span className="sx-fake sm">Suggest a change</span></div>
          </div>
        </Turn>
        {at(5) && <div className="sx-rcpt sx-arrive"><Tick /><b>Answered by you</b><span>Sent to Max via Claude Code</span></div>}
      </div>

      {/* Team 1a, lower half: your questions to others, what everyone is building, activity. */}
      <div className={scene(10)} aria-hidden={ch !== 10}>
        <div className={`sx-sh ${ins(1)}`}><b>Your questions to others</b><small>2</small></div>
        <div className={`sx-tbl ${ins(1)}`}>
          <div className="sx-qr"><span className="sx-av b">DW</span><span><b>Dana</b> · a passage in Retry failed webhooks · “Is one minute right for the partner API?”</span><em>answered · suggests a change</em></div>
          <div className="sx-qr"><span className="sx-av b">BC</span><span><b>Ben</b> · the diagram in Billing export · “Is a retry queue enough?”</span><em>waiting · reminded 2 h ago</em><span className="sx-fake sm">Hand to…</span></div>
        </div>
        <div className={`sx-sh ${ins(2)}`}><b>Working now</b><small>3</small></div>
        <div className={`sx-tbl ${ins(2)}`}>
          <div className="sx-wk"><span className="sx-av b">AB</span><b>Billing export</b><span className="sx-pbar"><i className="d" /><i className="d" /><i className="b" /><i /><i /></span><span>Implement 4/9 · slice 2 of 3</span><em>Codex</em></div>
          <div className="sx-wk"><span className="sx-av b">BC</span><b>Invoice PDFs</b><span className="sx-pbar"><i className="d" /><i className="d" /><i className="d" /><i className="b" /><i /></span><span>Verify · checking 18 of 24</span><em>Claude Code</em></div>
          <div className="sx-wk"><span className="sx-av b">CT</span><b>SSO group sync</b><span className="sx-pbar"><i className="d" /><i className="a" /><i /><i /><i /></span><span>Plan · waits for you and Ben</span><em>Claude Code</em></div>
        </div>
        <Fold title="Team activity" meta="today · 2 Plans approved · 1 shipped · 5 answers" className={ins(3)} />
      </div>

      {/* Review with teammates: reviewers, a point of the review with its proof, the comment in the sidebar, a link to the shared copy. */}
      <div className={scene(11)} aria-hidden={ch !== 11}>
        <Turn title={tg >= 4 ? "Ready to approve" : "A comment from Ben"} meta={tg >= 4 ? "Everything is settled" : "1 to answer"}><div className="sx-turn-actions"><span>{tg >= 4 ? "Read the proof, then approve the change." : "Can support see the count without opening the log?"}</span><span className="sx-fake sm p">{tg >= 4 ? "Approve" : "Reply"}</span></div></Turn>
        <div className={`sx-rev ${ins(1)}`}>
          <span className="sx-who2"><span className="sx-av b">D</span>Dana · required · approved</span>
          <span className="sx-who2"><span className="sx-av b">B</span>Ben · optional · {tg >= 4 ? "commented" : "commenting"}</span>
          <span className="sx-lk sx-hide">Ask someone else</span>
        </div>
        <div className={`sx-pcard ${ins(2)}`}>
          <p className="sx-ph"><Tick />Done means · 3 <span className="sx-cpin">1</span><small className="sx-hide">Support sees the retry count · evidence: a screenshot</small></p>
          <div className="sx-pb">
            <div className="sx-shotl">
              <div className="sx-mrow"><span className="sx-code">order.paid</span><span>Delivered</span></div>
              <div className="sx-mrow"><span className="sx-code">invoice.sent</span><span className="sx-red">Stopped, mailed</span></div>
            </div>
            <div className={`sx-thread sx-only-nw ${ins(2)}`}>
              <div className="sx-tm"><span className="sx-av b">B</span><p><small>Ben · teammate</small>Can support see this without the log?</p></div>
              <div className={`sx-tm ${ins(3)}`}><span className="sx-av b">Y</span><p><small>Your agent</small>Yes, each row shows the try count. Screenshot 2 proves it.</p></div>
            </div>
            <p className="sx-pbn sx-wide-only">Screenshot 2 · each failed row shows its try count, as Done means 3 asks.</p>
          </div>
        </div>
        <div className={`sx-share ${ins(4)}`}><span className="sx-av g"><ArrowUpRight size={14} aria-hidden="true" /></span><div><b>A link for people outside the team</b><small>Open the link to read the latest shared copy. Reload to see later changes. Designs stay on your computer.</small></div><span className="sx-fake sm">Copy link</span></div>
      </div>

      {/* Settings › Workflow: Planning and Build defaults per agent, the independent review; what each step cost. */}
      <div className={scene(12)} aria-hidden={ch !== 12}>
        <div className="sx-two sx-set2">
          <div className="sx-col">
            <div className={`sx-set ${ins(1)}`}>
              <div className="sx-seth"><b>Planning defaults</b><small>New task opens with these. Discuss and Plan run on them.</small></div>
              <AgentTabs />
              <Def label="Model" why="The most capable you can afford" value="Opus 5.5" />
              <Def label="Effort" why="At least High" value="High" />
              <Def label="Start in" why="Where the session opens" value="New session" />
            </div>
            <div className={`sx-set ${ins(2)}`}>
              <div className="sx-seth"><b>Build defaults</b><small>Implement Start opens with these. Change anything there for one build.</small></div>
              <AgentTabs />
              <Def label="Orchestrator" why="Plans every slice and reads every report" value="Opus 5.5" />
              <Def label="Workers" why="They write the code, a slice each" value="Sonnet 5.5" />
              <Def label="Effort for both" why="The orchestrator and every worker" value="High" />
            </div>
          </div>
          <div className="sx-col">
            <div className={`sx-set ${ins(2)}`}>
              <div className="sx-seth"><b>Independent review</b><small>An agent that never wrote the code decides whether it passes</small></div>
              <div className="sx-setr"><span>In Claude Code</span><span className="sx-sel">Opus 5.5</span></div>
              <div className="sx-setr"><span>In Codex</span><span className="sx-sel">GPT-6.1 Sol</span></div>
            </div>
            <div className={`sx-cost ${ins(3)}`}>
              <p className="sx-cv"><b>$20.95</b> so far · 1 h 17 min<small>estimated at list price</small></p>
              <span className="sx-cbar">{COST.map(([label, , cost, color]) => <i key={label} style={{ background: color, flexGrow: Number(cost.slice(1)) }} />)}</span>
              <div className="sx-ctab">
                <div className="sx-cth"><span>Step</span><span>time</span><span>cost</span></div>
                {COST.map(([label, time, cost, color]) => (
                  <div className="sx-ctr" key={label}><span><i style={{ background: color }} />{label}</span><span>{time}</span><span>{cost}</span></div>
                ))}
                <div className="sx-ctr tot"><span>Total</span><span>1 h 17 min</span><span>$20.95</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Home with "+ New" open: say what you want, pick the setup, copy one command; a notification when it needs you. */}
      <div className={scene(13)} aria-hidden={ch !== 13}>
        <div className="sx-two sx-homeg">
          <section className={`sx-newc ${ins(1)}`}>
            <div className="sx-newh"><b>New task</b><X size={13} aria-hidden="true" /></div>
            <p className="sx-hide">Tasks start in your coding agent. Say what you want, copy the command and run it there.</p>
            <div className="sx-atabs"><span className="on">Claude Code</span><span>Codex</span><span>Another agent</span></div>
            <p className="sx-nlab">What do you want to build or fix?</p>
            <span className="sx-field sx-nreq">{REQUEST}</span>
            <div className={`sx-nopts ${ins(2)}`}>
              <span><small>Model</small><span className="sx-sel">Opus 5.5</span></span>
              <span><small>Effort</small><span className="sx-sel">High</span></span>
              <span className="sx-hide"><small>Start in</small><span className="sx-seg3"><span>This session</span><span className="on">New session</span><span><GitBranch size={11} />New worktree</span></span></span>
            </div>
            <div className={`sx-cmdb ${ins(2)}`}><code>claude --model opus --effort high "/ql {REQUEST}"</code><span className={`sx-fake p sm${ch === 13 && step === 3 ? " press" : ""}`}><Copy size={11} />{t(13) >= 3 ? "Copied" : "Copy"}</span></div>
          </section>
          <div className="sx-col">
            <div className={`sx-notif ${ins(4)}`}><span className="sx-mark" /><p><small>QualityLayer · from the menu bar</small>Retry failed webhooks needs your review</p></div>
            <div className={`sx-home sx-hide ${ins(4)}`}>
              <div className="sx-hg amb"><span aria-hidden="true" className="sx-you" /><b>Your turn · 1</b></div>
              <div className="sx-hr"><span aria-hidden="true" className="sx-you" />Retry failed webhooks<small>Review · 3 to answer</small></div>
              <div className="sx-hg"><b>Running · 1</b></div>
              <div className="sx-hr"><span aria-hidden="true" className="sx-ag" />Invoice PDFs<small>Codex · building slice 2</small></div>
            </div>
            <div className={`sx-row2 ${ins(5)}`}><span className="sx-k">Your agents run in</span><span className="sx-tag">the terminal</span><span className="sx-tag">their desktop apps</span><span className="sx-tag">your IDE</span><span className="sx-tag">WSL and servers</span></div>
          </div>
        </div>
      </div>
    </>
  );
  return only ? Children.toArray(scenes.props.children)[ch] : scenes;
}
