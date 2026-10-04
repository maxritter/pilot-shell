import { ArrowUpRight, ChevronDown, ChevronRight } from "lucide-react";
import { Children, type ReactNode } from "react";
import { checksPassed, committedTasks } from "@/lib/tour";

/**
 * The scenes inside the App window, one per chapter, drawn from the App's own screens: the Needs
 * you card with its items, the violet "Checked by agents" line and the work below. Each scene's
 * parts appear one per moment: `ins(n)` and `at(n)` switch at moment n.
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

type ItemProps = { kind: string; what: string; why?: string; buttons?: string[]; done?: boolean; stack?: boolean; under?: boolean; className?: string; children?: ReactNode };

/** One item: its kind, the thing itself, why, and the two answers of its family. */
function Item({ kind, what, why, buttons = [], done = false, stack = false, under = false, className = "", children }: ItemProps) {
  return (
    <div className={`sx-it${done ? " done" : ""}${stack ? " stack" : ""}${under ? " under" : ""} ${className}`}>
      <span aria-hidden="true" className={done ? "sx-ok" : "sx-you"} />
      <div className="sx-itb">
        <p className="sx-ik">{kind}</p>
        <p className="sx-iw">{what}</p>
        {why && <p className="sx-iy">{why}</p>}
        {!stack && children}
      </div>
      {!done && buttons.length > 0 && (
        <div className="sx-iab">
          {buttons.map((label, k) => <span key={label} className={`sx-fake sm${k === 0 ? " first" : ""}`}>{label}</span>)}
        </div>
      )}
      {stack && <div className="sx-itc">{children}</div>}
    </div>
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

const SLICES = [
  { title: "Failed deliveries go to a retry queue", tasks: 2, doing: "writing the failing test: a failed delivery is queued once", first: 1 },
  { title: "Three tries, then mail the customer", tasks: 2, doing: "running delivery.test.ts and mailer.test.ts · 49 s", first: 3 },
  { title: "Retry count in the delivery row", tasks: 1, doing: "running row.test.tsx", first: 5 },
];
/** When a slice starts running and when it is committed (moments of the Implement scene). */
const SLICE_RUN = [1, 3, 1];
const SLICE_DONE = [3, 100, 4];

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

/** `only` renders just chapter `ch`'s scene, for the windows that sit inline beside each chapter. */
export default function TourScenes({ ch, step, tries, onRetry, only = false }: { ch: number; step: number; tries: number; onRetry: () => void; only?: boolean }) {
  const at = (n: number) => step >= n;
  const ins = (n: number) => `sx-in${at(n) ? " on" : ""}`;
  const scene = (k: number) => `sx-sc${ch === k ? " on" : ""}`;
  // Chapters other than their own show a scene finished, so a jump never lands on a half-built window.
  const t = (k: number) => (ch === k ? step : 99);

  const stopped = tries >= 3;
  const vt = t(3);
  const passed = checksPassed(vt);
  const checking = vt < 7;
  const it = t(2);
  const committed = committedTasks(it);

  const scenes = (
    <>
      {/* Discuss 1a: the agent's question, Decided with you, Done means, what the agent read. */}
      <div className={scene(0)} aria-hidden={ch !== 0}>
        <Needs head="How many tries before it stops?" meta={`${t(0) >= 3 ? 3 : 2} answered so far`} settled={t(0) >= 3} className={ins(1)}>
          <p className="sx-nd">Today a failed delivery is lost. The question is when to stop trying.</p>
          <div className={`sx-opts ${ins(2)}`}>
            <span className={`sx-opt rec${t(0) >= 3 ? " pick" : ""}`}><i /><span><b>3 tries · recommended</b><small>Then the customer gets one mail. More tries rarely help.</small></span></span>
            <span className="sx-opt"><i /><span><b>5 tries</b><small>Five failure mails is a lot for one customer.</small></span></span>
            <span className="sx-opt sx-hide"><i /><span><b>Until it succeeds</b></span></span>
          </div>
          <div className={`sx-nf ${ins(2)}`}>
            {t(0) >= 3 ? <span className="sx-tag ok">Answered in Claude Code</span> : <span className="sx-fake sm">Answer in Claude Code</span>}
            <small>The question and your answer stay here as a record.</small>
          </div>
        </Needs>
        <div className="sx-two">
          <div className={`sx-card sx-hide ${ins(4)}`}>
            <p className="sx-ch2">Decided with you <small>2</small></p>
            <div className="sx-dr"><span aria-hidden="true" className="sx-ok" />When to retry<small>A minute apart</small></div>
            <div className="sx-dr"><span aria-hidden="true" className="sx-ok" />Who hears about it<small>One mail</small></div>
          </div>
          <div className={`sx-card sx-hide ${ins(5)}`}>
            <p className="sx-ch2">Done means <small>3</small></p>
            <div className="sx-dr"><Tick />Failed deliveries are retried</div>
            <div className="sx-dr"><Tick />It stops after 3 tries and mails the customer</div>
            <div className="sx-dr"><Tick />Support sees the retry count</div>
          </div>
        </div>
        <Violet head="Read by the agent" facts={["the webhook sender and its tests", "9 files", "3 questions open for research"]} className={ins(6)} />
      </div>

      {/* Plan 1a and 2a: the items in order, then the line of what a second agent found. */}
      <div className={scene(1)} aria-hidden={ch !== 1}>
        {t(1) >= 6 ? (
          <>
            <p className="sx-note"><span aria-hidden="true" className="sx-todo" /><span>In Codex the command is <code>$ql implement retry-webhooks</code>. Another agent: give it the prompt from Copy › For another agent.</span></p>
            <p className="sx-note"><span aria-hidden="true" className="sx-ok" /><span>Approved by you at 13:27 · 5 items settled · the agent’s 3 decisions kept <u>Show</u></span></p>
            <Violet facts={["a second agent found nothing missing", "2 live facts tested, 6 questions answered"]} />
            <div className="sx-sum">
              <b>Failed webhooks are retried, then the customer gets one mail</b>
              <p>The Plan continues here as before: what changes, the mockup, out of scope, the build and the scenarios.</p>
            </div>
          </>
        ) : (
        <>
        <Needs meta="5 open · you can also comment anywhere in the Plan" className={ins(1)}>
          <div className="sx-pair">
            <Item kind="Mockup" what="Failed deliveries" buttons={["Looks right", "Change"]} stack>
              <div className="sx-mk">
                <div className="sx-mkh"><span className="sx-code">deliveries.html · clickable</span></div>
                <div className="sx-mrow"><span className="sx-code">order.paid</span><span>Delivered</span><span /></div>
                <div className="sx-mrow">
                  <span className="sx-code">invoice.sent</span>
                  <span className={stopped ? "sx-red" : "sx-amb"}>{stopped ? "Stopped, mailed" : `Try ${tries} of 3`}</span>
                  <button type="button" onClick={onRetry} disabled={stopped} tabIndex={-1} className="sx-mbtn">Retry</button>
                </div>
              </div>
            </Item>
            <Item kind="Engineering decision" what="Three tries, then one mail" buttons={["Agree", "Change"]} stack className={ins(2)}>
              <p className={`sx-pcs ${ins(3)}`}><span className="sx-cpin">1</span>You: Three tries. Five failure mails is too many.</p>
              <div className="sx-dg">
                <div className="sx-dgr">
                  <span className="sx-node hl"><i className="sx-ic" />Retry queue</span><span className="sx-edge" />
                  <span className="sx-diaw"><span className="sx-dia" /><b>try &lt; <mark>5</mark>?</b>{at(3) && <span className="sx-cpin">1</span>}</span>
                  <span className="sx-edge"><em>yes</em></span>
                  <span className="sx-node ok"><i className="sx-ic" />Send again</span>
                </div>
                <div className="sx-dgd"><span className="sx-down">no</span><span className="sx-node"><i className="sx-ic" />Mail the customer</span></div>
                <span className={`sx-pkt${ch === 1 && at(2) && !at(3) ? " on" : ""}`} />
              </div>
            </Item>
          </div>
          <Item kind="Done means · 3" what="What must hold when it is done, written in Discuss" buttons={["Looks right", "Open"]} className={`sx-row sx-hide ${ins(4)}`} />
          <Item kind="Decided by the agent · 3" what="Change any you disagree with" buttons={["Keep all"]} className={`sx-row sx-hide ${ins(4)}`} />
          <Item kind="Extra review" what="None planned: no sign-in, secret or outside input changes" buttons={["Agree", "Add a review"]} className={`sx-row sx-hide ${ins(5)}`} />
        </Needs>
        <Violet facts={["a second agent found nothing missing", "2 live facts tested, 6 questions answered"]} className={ins(5)} />
        </>
        )}
      </div>

      {/* Implement 1a: what the agent decided on the way, the slices with their tasks, the proof so far. */}
      <div className={scene(2)} aria-hidden={ch !== 2}>
        <Needs head="Decided by the agent while building" meta="the build goes on · ask about any of them now or in Review" className={ins(2)}>
          <Item kind="T2 · outside its files" what="Moved the retry delay into settings.ts, which the sender already imports" buttons={["Fine", "Ask why"]} className="sx-row" />
        </Needs>
        <div className={`sx-bh ${ins(1)}`}><b>The build</b><span>{committed} of 5 tasks · every task test first</span></div>
        <div className={`sx-bld ${ins(1)}`}>
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
        <Fold title="Changes so far" meta="9 files · +214 −31 · grouped by task" live className={`sx-hide ${ins(4)}`} />
        <Violet facts={["2 tasks green, test first", "slice 1’s checks passed", "6 checks recorded"]} className={ins(5)} />
      </div>

      {/* Verify 1a and 1b: every check listed from the start, filling in live; then all passed. */}
      <div className={scene(3)} aria-hidden={ch !== 3}>
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

      {/* Review 1a: what only you can confirm, the result to look at, what the checks found, the Approve menu. */}
      <div className={scene(4)} aria-hidden={ch !== 4}>
        <Needs meta="3 open · 1 settled" className={ins(1)}>
          <Item kind="Only you can confirm" what="One live call to the partner API gave 3 tries" why="Done 2 asks for it, and agents may not call live services while checking." buttons={["I confirm", "Ask the agent to record it"]} />
          <Item kind="Look at the result" what="Failed deliveries as built" buttons={["Looks right", "Change"]} className={ins(2)}>
            <div className="sx-shot">
              <div className="sx-shotl">
                <div className="sx-mrow"><span className="sx-code">order.paid</span><span>Delivered</span></div>
                <div className="sx-mrow"><span className="sx-code">invoice.sent</span><span className="sx-red">Stopped, mailed</span></div>
                <span className="sx-cpin sx-spin">1</span>
              </div>
              <p>The page as built, dark theme, 1280 px. Click anywhere on the screen to pin a change. Matches the Plan’s mockup.</p>
            </div>
          </Item>
          <Item kind="Found while checking" what="The retry mail goes out in English only" buttons={["Accept", "Fix it"]} className={`sx-row ${ins(3)}`} />
          <Item kind="Decided by the agent during the build" what="Moved the retry delay into settings.ts" done className={`sx-row sx-hide ${ins(3)}`}><span className="sx-itn">Accepted by you</span></Item>
        </Needs>
        <Violet facts={["3 of 3 points of Done proven", "3 scenarios", "412 tests", "evidence for each"]} className={ins(4)} />
        <div className={`sx-menu ${ins(5)}`}>
          <div className="sx-mi first"><b>Approve and open a pull request</b><small>Pushes the branch and opens the pull request with the summary and the evidence. Needs gh.</small></div>
          <div className="sx-mi"><b>Approve only</b><small>You push and merge yourself</small></div>
          <div className="sx-mi"><b>Copy the git commands</b><small>gh is not installed here</small></div>
        </div>
      </div>

      {/* Plan 1c and 1d, Slack 1b: the question on a passage, and the Slack messages. */}
      <div className={scene(5)} aria-hidden={ch !== 5}>
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
              <span className={`sx-fake p${ch === 5 && step === 2 ? " press" : ""}`} style={{ alignSelf: "flex-start" }}>Send the question</span>
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
      <div className={scene(6)} aria-hidden={ch !== 6}>
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
            {!at(5) && <div className="sx-row2"><span className={`sx-fake p sm${ch === 6 && step === 4 ? " press" : ""}`}>Send the draft</span><span className="sx-fake sm">Edit</span></div>}
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
      <div className={scene(7)} aria-hidden={ch !== 7}>
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

      {/* Review with teammates: reviewers, a comment on a point of the shared review with its answer, a link for people outside the team. */}
      <div className={scene(8)} aria-hidden={ch !== 8}>
        <div className={`sx-rev ${ins(1)}`}>
          <span className="sx-who2"><span className="sx-av b">D</span>Dana · required · approved</span>
          <span className="sx-who2"><span className="sx-av b">B</span>Ben · optional · {at(4) ? "commented" : "commenting"}</span>
          <span className="sx-lk">Ask someone else</span>
        </div>
        <Needs meta={at(4) ? "1 settled" : "1 open"} settled={at(4)} className={ins(2)}>
          <Item kind="Comment from Ben" what="On Done means, point 3: can support see the count without opening the log?" buttons={["Reply", "Resolve"]} done={at(4)} className="sx-row" />
          <div className="sx-part">
            <p className="sx-ph"><Tick />Done means · 3 <small>Support sees the retry count · evidence: a screenshot</small></p>
            <div className="sx-pb">
              <div className="sx-shotl">
                <div className="sx-mrow"><span className="sx-code">order.paid</span><span>Delivered</span></div>
                <div className="sx-mrow"><span className="sx-code">invoice.sent</span><span className="sx-red">Stopped, mailed</span></div>
              </div>
              <div className={`sx-thread ${ins(2)}`}>
                <div className="sx-tm"><span className="sx-av b">B</span><p><small>Ben · teammate</small>Can support see this without the log?</p></div>
                <div className={`sx-tm ${ins(3)}`}><span className="sx-av b">Y</span><p><small>Your agent</small>Yes, each row shows the try count. Screenshot 2 proves it.</p></div>
              </div>
            </div>
          </div>
        </Needs>
        <div className={`sx-share ${ins(4)}`}><span className="sx-av g"><ArrowUpRight size={14} aria-hidden="true" /></span><div><b>A link for people outside the team</b><small>They read the plan and the review, and comment. Their comments reach you as items that need you.</small></div><span className="sx-fake sm">Copy link</span></div>
      </div>

      {/* Settings 1a and Cost 1a: workers and second opinion, notifications, what each step cost. */}
      <div className={scene(9)} aria-hidden={ch !== 9}>
        <div className="sx-two sx-set2">
          <div className="sx-col">
            <div className={`sx-set ${ins(1)}`}>
              <div className="sx-seth"><b>Subagents</b><small>Agents your agent starts for parts of the work</small></div>
              <div className="sx-setr"><span>Workers<small>Research, building and fixes</small></span><span className="sx-sel">Sonnet 5.5</span><span className="sx-sel">GPT-6.1 Sol</span></div>
              <div className="sx-setr"><span>Checking<small>Decides pass or fail on the finished change; it never wrote the code</small></span><span className="sx-sel">Opus 5.5</span><span className="sx-sel">GPT-6.1 Sol</span></div>
              <p className="sx-setn">Pick No subagents for Workers to have your agent do every step itself.</p>
            </div>
            <div className={`sx-set ${ins(1)}`}>
              <div className="sx-seth"><b>Second opinion</b><small>The other coding agent reviews risky Plans on its own</small></div>
              <div className="sx-setr"><span>Codex reviews Claude Code’s work</span><span className="sx-sel">GPT-6.1 Sol</span></div>
              <div className="sx-setr"><span>Claude Code reviews Codex’s work</span><span className="sx-sel">Sonnet 5.5</span></div>
            </div>
            <div className={`sx-set ${ins(3)}`}>
              <div className="sx-setr"><span>Notifications<small>When something needs you, or a task ships or stops.</small></span><span className="sx-tog on" /></div>
            </div>
          </div>
          <div className={`sx-cost ${ins(2)}`}>
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

      {/* Home 1g and Updates 1a: Claude Code points to the App; a notification; Needs you; where agents run. */}
      <div className={scene(10)} aria-hidden={ch !== 10}>
        <div className="sx-two">
          <div className="sx-term">
            <p className="sx-k">Claude Code</p>
            <p className={`ok ${ins(1)}`}>Every check passed. Review the change in the QualityLayer App.</p>
            <p className={ins(1)}>Nothing more to do here until you approve.</p>
            <div className={`sx-band ${ins(2)}`}><span className="sx-mark" />Retry failed webhooks · waits for your review · 3 items</div>
            <p className="sx-prompt">›</p>
          </div>
          <div className="sx-col">
            <div className={`sx-notif ${ins(3)}`}><span className="sx-mark" /><p><small>QualityLayer · from the menu bar</small>Retry failed webhooks needs your review</p></div>
            <Needs meta="3 open" className={`sx-hide ${ins(4)}`}>
              <Item kind="Only you can confirm" what="One live call to the partner API gave 3 tries" buttons={["I confirm", "Ask the agent to record it"]} under />
              <Item kind="Look at the result" what="Failed deliveries as built" buttons={["Looks right", "Change"]} under />
              <Item kind="Found while checking" what="The retry mail goes out in English only" buttons={["Accept", "Fix it"]} under />
            </Needs>
          </div>
        </div>
        <div className={`sx-row2 sx-hide ${ins(5)}`}><span className="sx-k">Your agents run in</span><span className="sx-tag">the terminal</span><span className="sx-tag">their desktop apps</span><span className="sx-tag">your IDE</span><span className="sx-tag">WSL and servers</span></div>
      </div>
    </>
  );
  return only ? Children.toArray(scenes.props.children)[ch] : scenes;
}
