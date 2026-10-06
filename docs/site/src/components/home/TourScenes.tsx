import { ArrowDown, ArrowUp, ArrowUpRight, ChevronDown, ChevronRight, Copy, Frame, GitBranch, Infinity as Loop, Lock, MessageSquare, PanelRight, Search, SlidersHorizontal, SquarePlus, X } from "lucide-react";
import { Children, type ReactNode } from "react";
import { checksPassed, committedTasks, DESIGN, REQUEST } from "@/lib/tour";

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

/** The card that holds the items waiting for you. */
function Needs({ head = "Needs you", meta, settled = false, className = "", children }: { head?: string; meta?: string; settled?: boolean; className?: string; children: ReactNode }) {
  return (
    <section className={`sx-nc${settled ? " settled" : ""} ${className}`}>
      <div className="sx-nch"><span aria-hidden="true" className={settled ? "sx-ok" : "sx-you"} /><b>{head}</b>{meta && <span>{meta}</span>}</div>
      {children}
    </section>
  );
}

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

/** The question card above the page: the question, how many may follow, who waits, then the choices. */
function QCard({ title, count, waits, className = "", children }: { title: string; count: string; waits: string; className?: string; children: ReactNode }) {
  return (
    <section className={`sx-qc ${className}`}>
      <div className="sx-qh"><span aria-hidden="true" className="sx-you" /><b>{title}</b><em className="sx-hide">{count}</em><small><i />{waits}</small></div>
      {children}
    </section>
  );
}

/** One choice of the card: its number key, the words, and the recommended mark with Enter. */
function Choice({ n, label, rec = false, pick = false, className = "" }: { n: number; label: string; rec?: boolean; pick?: boolean; className?: string }) {
  return (
    <span className={`sx-qo${rec ? " rec" : ""}${pick ? " pick" : ""} ${className}`}>
      <kbd>{n}</kbd><b>{label}</b>{rec && <><em>Recommended</em><small className="sx-hide">↵ Enter</small></>}
    </span>
  );
}

/** The card's foot: Tell me more, the way out when you are not sure, and what the answer settles. */
function QFoot({ fact, settles, className = "" }: { fact?: string; settles: string; className?: string }) {
  return (
    <div className={`sx-qf ${className}`}>
      <span className="sx-qmore"><Search size={12} aria-hidden="true" />Tell me more<kbd>M</kbd></span>
      {fact ? <span className="sx-qfact"><i aria-hidden="true" className="sx-dm" />{fact}</span> : <u className="sx-hide">Not sure, use your recommendation</u>}
      <span className="sx-qset sx-hide">{settles}</span>
    </div>
  );
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
          <span className={tab === "designs" ? "on" : ""}>Designs{tab === "designs" && <i className="sx-ndot" />}</span>
        </span>
        <span className="sx-dicon"><PanelRight size={13} /></span>
      </div>
      {tab === "designs" ? (
        <>
          <p className="sx-lock"><Lock size={12} aria-hidden="true" /><span><b>Only on this computer.</b> Never shared.</span></p>
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
  const answered = t(0) >= 4;
  const pt = t(1);
  const rv = t(5);
  const cm = t(7);
  const tg = t(11);

  const scenes = (
    <>
      {/* Discuss: the question card above the page, then the page: what you decided, as QualityLayer keeps it. */}
      <div className={scene(0)} aria-hidden={ch !== 0}>
        {answered && (
          <div className="sx-rcpt">
            <Tick /><b>Answered</b><span>3 tries, then one mail</span><small className="sx-hide">Claude Code took it at 10:14</small><u>Change</u>
          </div>
        )}
        {answered ? (
          <QCard title="Who hears about it when it stops?" count="question 4 · last questions" waits="Claude Code waits" className="sx-arrive">
            <div className="sx-qos">
              <Choice n={1} label="The customer, in one mail" rec />
              <Choice n={2} label="Support, in a Slack channel" />
              <span className="sx-qown sx-hide"><span>Your own answer</span><kbd>T</kbd><span className="sx-fake sm">Answer</span></span>
            </div>
            <QFoot settles="Settles Decided with you · row 4" />
          </QCard>
        ) : (
          <QCard title="How many tries before it stops?" count="question 3 · about 2 to come" waits="Claude Code waits" className={ins(1)}>
            <p className="sx-qd">Today a failed delivery is lost. The question is when to stop trying and tell the customer.</p>
            <div className={`sx-qos ${ins(2)}`}>
              <Choice n={1} label="3 tries, then one mail" rec pick={t(0) >= 3} />
              <Choice n={2} label="5 tries, then one mail" />
              <span className="sx-qown sx-hide"><span>Your own answer</span><kbd>T</kbd><span className="sx-fake sm">Answer</span></span>
            </div>
            <QFoot settles="Settles Decided with you · row 3" className={ins(2)} />
          </QCard>
        )}
        <div className={`sx-psec ${ins(answered ? 0 : 4)}`}>
          <p className="sx-ph2">Decided with you <small>{answered ? 3 : 2}</small></p>
          <div className="sx-dtab">
            <div className="sx-dtr hd"><span>#</span><span>Question</span><span>Your answer</span></div>
            <div className={`sx-dtr${answered ? "" : " wait"}`}><span>3</span><span>How many tries before it stops?</span><span>{answered ? "3 tries, then one mail" : "Waiting for you"}</span></div>
            <div className="sx-dtr"><span>2</span><span>When does it try again?</span><span>A minute apart</span></div>
            <div className="sx-dtr sx-hide"><span>1</span><span>Which deliveries count as failed?</span><span>Any answer but 2xx</span></div>
          </div>
        </div>
      </div>

      {/* Plan: each decision in the same card, then "Approve the Plan?" above the page that records your calls. */}
      <div className={scene(1)} aria-hidden={ch !== 1}>
        {pt >= 4 ? (
          <section className="sx-appq sx-arrive">
            <div className="sx-aqh"><span aria-hidden="true" className="sx-you" /><b>Approve the Plan?</b><small>2 of 3 answered</small></div>
            <div className="sx-aqr"><span aria-hidden="true" className="sx-ok" />Decision 1 · a retry queue<em>Agree</em></div>
            <div className="sx-aqr"><span aria-hidden="true" className="sx-ok" />Decision 2 · three tries, then one mail<em>Agree</em></div>
            <div className="sx-aqr"><span aria-hidden="true" className="sx-you" />The design · {DESIGN.name}<em className="sx-amb">open<ArrowUp size={11} /></em></div>
            <div className="sx-aqf"><span className="sx-hide">Approving takes the open ones as they are.</span><span className={`sx-fake p${ch === 1 && step === 5 ? " press" : ""}`}>Approve<kbd>⌘↵</kbd></span></div>
          </section>
        ) : (
          <QCard title="Three tries, then one mail. Agree?" count="decision 2 of 3, then Approve the Plan?" waits="Claude Code waits" className={ins(1)}>
            <p className="sx-qd">A failed delivery waits in a retry queue and is sent again a minute apart. After the third try the customer gets one mail.</p>
            <Decision live={ch === 1 && at(2) && !at(3)} />
            <div className={`sx-qos ${ins(2)}`}>
              <Choice n={1} label="Agree" rec pick={pt >= 3} />
              <Choice n={2} label="Change…" className="sx-hide" />
            </div>
            <QFoot fact="Codex read the Plan" settles="In the Plan · Engineering decisions" className={ins(2)} />
          </QCard>
        )}
        <p className="sx-ptitle">Failed webhooks are retried, then the customer gets one mail</p>
        {pt >= 4 && (
          <div className="sx-psec">
            <p className="sx-ph2">Engineering decisions <small>2</small></p>
            <p className="sx-dq"><span>2</span>Three tries, then one mail</p>
            <Decision />
            <div className="sx-call"><span aria-hidden="true" className="sx-ok" /><small>Your call</small><em><Tick />Agree</em><u>Undo</u></div>
          </div>
        )}
      </div>

      {/* Implement Start: your Build defaults drawn as the build, one effort for both, one command. */}
      <div className={scene(2)} aria-hidden={ch !== 2}>
        <div className="sx-sban"><span aria-hidden="true" className="sx-you" /><b>Start the build</b><span className="sx-hide">Run the command below. This page shows the build once it starts.</span></div>
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
      </div>

      {/* Implement: the build on its own, slice by slice, test first; what the agent decided on the way. */}
      <div className={scene(3)} aria-hidden={ch !== 3}>
        <div className="sx-bhd"><span aria-hidden="true" className="sx-ag" /><b>Slice {committed >= 2 ? 2 : 1} of 3 · task {committed + 1} of 5</b><small className="sx-hide">about {committed >= 2 ? 9 : 20} min left</small><em className="sx-hide">Claude Code · 2 agents</em></div>
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
        <p className={`sx-note ${ins(2)}`}><span aria-hidden="true" className="sx-todo" /><span>Nothing waits for you. Anything only you can do goes to the final review.</span></p>
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
            <div className="sx-wh"><b>Waiting for you in Review</b><small>3</small></div>
            <div className="sx-wl">
              <div className="sx-wr"><span aria-hidden="true" className="sx-you" /><span><b>Only you can confirm: one live call to the partner API gave 3 tries</b><small>Done 2 asked for a live call. The agent made it while planning but did not keep the output.</small></span><em>no agent may call it</em></div>
              <div className="sx-wr"><span aria-hidden="true" className="sx-you" /><span><b>Look at the result: Failed deliveries as built</b></span><em>screenshot</em></div>
              <div className="sx-wr"><span aria-hidden="true" className="sx-you" /><span><b>The retry mail goes out in English only</b></span><em>note from the check</em></div>
            </div>
            <Fold title="Scenarios" meta="3 of 3 · each with its output kept" violet />
            <Fold title="Done means" meta="3 of 3 · each with its evidence" violet />
            <Fold title="Project checks" meta="4 of 4 · tests, types, lint, build" violet className="sx-hide" />
          </>
        )}
      </div>

      {/* Review: what is settled with you, the proof, then "Approve the change?" and the ways to ship. */}
      <div className={scene(5)} aria-hidden={ch !== 5}>
        <div className="sx-psec">
          <p className="sx-ph2">Settled with you <small>{Math.min(3, rv)} of 3</small></p>
          <div className="sx-stab">
            <div className={`sx-str${rv >= 1 ? " done" : ""}`}><span aria-hidden="true" className={rv >= 1 ? "sx-ok" : "sx-you"} /><span><small>Only you can confirm</small>One live call to the partner API gave 3 tries</span>{rv >= 1 ? <em><Tick />I confirm</em> : <span className="sx-iab"><span className="sx-fake sm first">I confirm</span><span className="sx-fake sm sx-hide">Ask the agent to record it</span></span>}</div>
            <div className={`sx-str${rv >= 2 ? " done" : ""}`}><span aria-hidden="true" className={rv >= 2 ? "sx-ok" : "sx-you"} /><span><small>Look at the result</small>{DESIGN.name} as built</span><span className="sx-mini sx-hide"><DesignPage className="mini" next /></span>{rv >= 2 ? <em><Tick />Looks right</em> : <span className="sx-iab"><span className="sx-fake sm first">Looks right</span><span className="sx-fake sm sx-hide">Change</span></span>}</div>
            <div className={`sx-str${rv >= 3 ? " done" : ""}`}><span aria-hidden="true" className={rv >= 3 ? "sx-ok" : "sx-you"} /><span><small>Found while checking</small>The retry mail goes out in English only</span>{rv >= 3 ? <em><Tick />Accept</em> : <span className="sx-iab"><span className="sx-fake sm first">Accept</span><span className="sx-fake sm sx-hide">Fix it</span></span>}</div>
          </div>
        </div>
        <Violet facts={["3 of 3 points of Done means passed", "3 scenarios", "412 tests"]} className={ins(3)} />
        <div className={`sx-apw ${ins(4)}`}>
          <section className="sx-appq">
            <div className="sx-aqh"><span aria-hidden="true" className="sx-you" /><b>Approve the change?</b><small className="sx-hide">branch retry-webhooks</small></div>
            <div className="sx-aqf"><span className="sx-hide">Approving ships it the way you pick. QualityLayer never merges.</span><span className={`sx-fake p split${rv >= 5 ? " glow" : ""}`}>Approve and open a pull request</span></div>
          </section>
          <div className={`sx-menu drop ${ins(5)}`}>
            <div className="sx-mi first"><b>Approve and open a pull request</b><small>05-review.md becomes its description, with the proof</small></div>
            <div className="sx-mi"><b>Approve only</b><small>You push and open it yourself</small></div>
            <div className="sx-mi"><b>Copy the git commands</b><small>Push the branch and open the pull request by hand</small></div>
          </div>
        </div>
      </div>

      {/* Designs, in the Plan: the preview of the design the Plan names, and its question. */}
      <div className={scene(6)} aria-hidden={ch !== 6}>
        <p className="sx-ptitle">Failed webhooks are retried, then the customer gets one mail</p>
        <div className={`sx-psec ${ins(2)}`}>
          <p className="sx-ph2">Interface</p>
          <div className="sx-prev">
            <div className="sx-prevc"><span className="sx-prevt">Preview</span><DesignPage className="prev" /></div>
            <div className="sx-prevf"><Frame size={13} aria-hidden="true" /><b>{DESIGN.name}</b><small className="sx-hide">Updated just now</small><span className="sx-fake sm">Open full size</span></div>
          </div>
          <div className={`sx-look ${ins(4)}`}><span aria-hidden="true" className="sx-you" /><small>Look</small><span>Is this how failed deliveries should look?</span><span className="sx-iab"><span className="sx-fake sm first">Looks right</span><span className="sx-fake sm">Change</span></span></div>
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
            <div className={`sx-pop ${ins(1)}`}>
              <b>Ask about this passage</b>
              <div className="sx-who"><span className={`sx-whoi ${at(1) ? "on" : ""}`}><span className="sx-av b">D</span>Dana</span><span className="sx-whoi"><span className="sx-av b">B</span>Ben</span><span className="sx-whoi"><span className="sx-av b">C</span>Chen</span></div>
              <span className="sx-field">Is one minute right for the partner API?</span>
              <span className={`sx-fake p${ch === 8 && step === 2 ? " press" : ""}`} style={{ alignSelf: "flex-start" }}>Send the question</span>
            </div>
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
        <Needs head="Questions for you" meta={`${at(5) ? 1 : 2} open · your answer goes to the asker and their agent`} className={ins(1)}>
          <div className={`sx-q2${at(5) ? " done" : ""}`}>
            <span aria-hidden="true" className={at(5) ? "sx-ok" : "sx-you"} />
            <span className="sx-av b">MR</span>
            <div className="sx-itb">
              <p className="sx-ik">Max Ritter asked you about a passage in the Plan · Retry failed webhooks · needed before approval · 25 min ago</p>
              <p className="sx-iw">“Is one minute right for the partner API?”</p>
            </div>
            {at(5) ? <span className="sx-itn">Answered by you</span> : <div className="sx-iab"><span className="sx-fake sm first">Looks right</span><span className="sx-fake sm">Suggest a change</span></div>}
          </div>
          <div className={`sx-psg ${ins(2)}`}><b>The passage:</b> “A failed delivery is sent again one minute apart, three times, then the customer gets one mail.”</div>
          <div className={`sx-lks ${ins(2)}`}>
            <span>Reply</span><span className={at(3) ? "on" : ""}>Draft with my agent</span><span>Hand to someone else</span><u>Open the Plan at this passage</u>
          </div>
          <div className={`sx-draft${at(5) ? " sent" : ""} ${ins(4)}`}>
            <p className="sx-dh"><span className="sx-ag" />{at(5) ? "Sent to Max · marked “via Claude Code”" : "Draft by your Claude Code · not sent yet"}</p>
            <p>Back off instead: 1, 5, then 15 minutes. The partner API limits retries.</p>
            {!at(5) && <div className="sx-row2"><span className={`sx-fake p sm${ch === 9 && step === 4 ? " press" : ""}`}>Send the draft</span><span className="sx-fake sm">Edit</span></div>}
          </div>
          <div className={`sx-q2 sx-sec ${ins(1)}`}>
            <span aria-hidden="true" className="sx-you" />
            <span className="sx-av b">AB</span>
            <div className="sx-itb">
              <p className="sx-ik">Anna Becker asked you about one diagram · Billing export · Plan · 2 h ago</p>
              <p className="sx-iw">“Is the retry queue a single point of failure?”</p>
            </div>
            <div className="sx-iab"><span className="sx-fake sm first">Looks right</span><span className="sx-fake sm">Suggest a change</span></div>
          </div>
        </Needs>
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
              <div className="sx-hg amb"><span aria-hidden="true" className="sx-you" /><b>Needs you · 1</b></div>
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
