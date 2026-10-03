/** The ten scenes inside the App window. Each scene's parts appear one per moment: `in(n)` and `on(n)` switch at moment n. */

const LANES = [
  ["Retry queue", "helper · Sonnet 5.5"],
  ["Three tries, then mail", "helper · risky"],
  ["Retry count in the row", "helper · Sonnet 5.5"],
];
/** Slices 1 and 3 side by side, slice 2 after them; segment j of a lane fills at its start + j. */
const LANE_START = [1, 3, 1];

const RECORDS: [string, string, string, string][] = [
  ["✗", "slice 1 · test written first, fails", "1", "sx-recr no"],
  ["✗", "slice 3 · test written first, fails", "1", "sx-recr no"],
  ["✓", "check slice 1 · 4 commands from the plan", "0", "sx-recr ok"],
  ["✓", "check slice 3 · 3 commands from the plan", "0", "sx-recr ok"],
  ["✓", "check slice 2 · 5 commands from the plan", "0", "sx-recr ok"],
];

const COST: [string, number][] = [["Discuss", 310], ["Plan", 420], ["Implement", 860], ["Verify", 280], ["Review", 40]];

export default function TourScenes({ ch, step, tries, onRetry }: { ch: number; step: number; tries: number; onRetry: () => void }) {
  const at = (n: number) => step >= n;
  const ins = (n: number) => `sx-in${at(n) ? " on" : ""}`;
  const on = (n: number) => (at(n) ? "on" : "");
  const scene = (k: number) => `sx-sc${ch === k ? " on" : ""}`;
  // Chapters other than their own show a scene finished, so a jump never lands on a half-built window.
  const t = (k: number) => (ch === k ? step : 99);

  const stopped = tries >= 3;
  const shown = ch === 2 ? Math.min(RECORDS.length, Math.max(0, step - 1)) : RECORDS.length;
  const records = RECORDS.slice(0, shown).slice(-4);
  const ringN = ch === 3 ? Math.max(0, Math.min(3, step - 3)) : 3;

  return (
    <>
      <div className={scene(0)} aria-hidden={ch !== 0}>
        <div className="sx-two">
          <div className="sx-term">
            <p className="sx-k">Claude Code</p>
            <p className={`me ${ins(1)}`}>/ql Retry failed webhooks, and stop after a few tries.</p>
            <p className={ins(1)}>Read the webhook sender and its tests.</p>
            <div className={`sx-ask ${ins(2)}`}>
              <p className="sx-askq">How many tries before it stops?</p>
              <span className={`sx-opt rec${at(3) ? " pick" : ""}`}><i />3 tries<em>Recommended</em></span>
              <span className="sx-opt"><i />5 tries</span>
              <span className="sx-opt"><i />Until it succeeds</span>
              <p className="sx-k" style={{ marginTop: 2 }}>Question 3 of 5 · one at a time</p>
            </div>
          </div>
          <div className="sx-cardw sx-hide">
            <p className="sx-k">Plan · being written</p>
            <p className="sx-lbl">Problem</p>
            <p className="sx-gt">A webhook that fails once is lost, and nobody hears about it.</p>
            <p className="sx-lbl">Done means</p>
            <span className={`sx-done ${on(4)}`}><i>✓</i>Failed deliveries are retried</span>
            <span className={`sx-done ${on(5)}`}><i>✓</i>It stops after 3 tries and mails the customer</span>
            <span className={`sx-done ${on(6)}`}><i>✓</i>Support sees the retry count</span>
            <div className={`sx-scal ${ins(7)}`}>Plan gate · 3 slices, 2 side by side · checkpoint after slice 2 · security review</div>
          </div>
        </div>
      </div>

      <div className={scene(1)} aria-hidden={ch !== 1}>
        <span className={`sx-cold ${ins(1)}`}><span className="sx-ok" />Read by a fresh agent first · 2 gaps fixed</span>
        <div className="sx-dgm">
          <div className="sx-grid">
            <span className={`sx-node ${ins(1)}`}><i className="sx-ic" />Webhook fails</span><span className="sx-edge" />
            <span className={`sx-node hl ${ins(1)}`}><i className="sx-ic" />Retry queue</span><span className="sx-edge" />
            <span className="sx-diaw"><span className="sx-dia" /><b>try &lt; <mark>5</mark>?</b>{at(3) && <span className="sx-cpin">1</span>}</span>
            <span className="sx-edge"><em>yes</em></span>
            <span className={`sx-node ok ${ins(1)}`}><i className="sx-ic" />Send again</span>
            <span className="sx-down">no</span>
            <span className="sx-stopw"><span className="sx-node stop"><i className="sx-ic" />Mail the customer</span></span>
            <div className={`sx-pc sx-cmt ${ins(3)}`}><span className="sx-av">Y</span><p><small>You · on “try &lt; 5”</small>Three tries. Five failure mails is too many.</p></div>
          </div>
          <span className={`sx-pkt${ch === 1 && at(2) ? " on" : ""}`} />
        </div>
        <div className={`sx-two sx-hide ${ins(4)}`}>
          <div className="sx-mk">
            <div className="sx-mkh"><b>Deliveries · mockup</b><span className="sx-chip ag">Clickable</span></div>
            <div className="sx-mrow"><span className="sx-code">order.paid</span><span className="sx-meter okm"><i className="on" /><i /><i /></span><span>Delivered</span><span /></div>
            <div className="sx-mrow">
              <span className="sx-code">invoice.sent</span>
              <span className={`sx-meter ${stopped ? "red" : "amb"}`}><i className="on" /><i className={tries >= 2 ? "on" : ""} /><i className={tries >= 3 ? "on" : ""} /></span>
              <span className={stopped ? "sx-red" : "sx-amb"}>{stopped ? "Stopped, mailed" : `Try ${tries} of 3`}</span>
              <button type="button" onClick={onRetry} disabled={stopped} tabIndex={-1} className="sx-mbtn">Retry</button>
            </div>
            <div className="sx-mrow"><span className="sx-code">refund.created</span><span className="sx-meter red"><i className="on" /><i className="on" /><i className="on" /></span><span className="sx-red">Stopped, mailed</span><span /></div>
          </div>
          <div className="sx-sl">
            <div className="sx-slr"><b>1</b><span>Failed deliveries go to a retry queue</span></div>
            <div className="sx-slr"><b>2</b><span>Three tries, then mail the customer</span><span className="sx-risk">Risky</span></div>
            <div className="sx-slr"><b>3</b><span>Retry count in the delivery row</span></div>
          </div>
        </div>
      </div>

      <div className={scene(2)} aria-hidden={ch !== 2}>
        <div className="sx-gantt">
          <div className="sx-gaxis"><span>Slice</span><span>Failing test</span><span>Code</span><span>Test passes</span><span>Runs for real</span></div>
          {LANES.map(([name, who], k) => {
            const fill = (j: number) => (t(2) >= LANE_START[k] + j ? " on" : "");
            // The risky slice ends at a checkpoint: your turn to try it, so its last phase is amber.
            const risky = k === 1;
            return (
              <div className="sx-glane" key={name}>
                <span className="sx-ln"><b>{name}</b><small>{who}</small></span>
                <div className="sx-gtrack">
                  <span className={`sx-seg r${fill(0)}`}>✗ fails</span><span className={`sx-seg b${fill(1)}`}>code</span><span className={`sx-seg g${fill(2)}`}>✓ passes</span><span className={`sx-seg k${risky ? " you" : ""}${fill(3)}`}>{risky ? "try it" : "runs"}</span>
                </div>
              </div>
            );
          })}
        </div>
        <div className="sx-rec">
          <div className="sx-rech"><span>Recorded by QualityLayer</span><span>exit code</span></div>
          {records.map(([mark, text, code, cls]) => <div className={cls} key={text}><b>{mark}</b><span>{text}</span><span>{code}</span></div>)}
        </div>
      </div>

      <div className={scene(3)} aria-hidden={ch !== 3}>
        <div className="sx-vlanes">
          <div className={`sx-vl ${on(1)}`}><b><span className="sx-ok" />Polish</b><small>Leftover code, missing edge-case tests, docs the change made wrong</small></div>
          <div className={`sx-vl ${on(1)}`}><b><span className="sx-ok" />Security</b><small>Beside polish, because the change touches outside input</small></div>
          <div className={`sx-vl ${on(2)}`}><b><span className={at(7) || ch !== 3 ? "sx-ok" : "sx-ag"} />Judge</b><small>An AI that did not write the code, on Opus 5.5</small></div>
        </div>
        <div className="sx-chk">
          <div className="sx-ring" style={{ background: `conic-gradient(var(--ql-accent) ${Math.round((ringN / 3) * 360)}deg, var(--ql-surface-3) 0)` }}>
            <div className="sx-ringin"><b>{ringN}/3</b><small>points of<br />Done hold</small></div>
          </div>
          <div className="sx-evs">
            <div className={`sx-ev ${on(4)}`}><div className="sx-evv">delivery log<br />try 1 · 502<br />try 2 · 502<br />try 3 · stopped</div><p>Retries, then stops</p><span className="sx-stamp">✓ Holds</span></div>
            <div className={`sx-ev ${on(5)}`}><div className="sx-evv">recorded test run<div className="sx-dots">{Array.from({ length: 14 }, (_, i) => <i key={i} />)}</div>14 passed · exit 0</div><p>Mails the customer once</p><span className="sx-stamp">✓ Holds</span></div>
            <div className={`sx-ev ${on(6)}`}><div className="sx-evv">screenshot<div className="sx-shotrow"><span>invoice.sent</span><span className="sx-red">3 of 3</span></div><div className="sx-shotrow"><span>order.paid</span><span>1 of 3</span></div></div><p>Support sees the count</p><span className="sx-stamp">✓ Holds</span></div>
          </div>
        </div>
        <div className={`sx-row2 ${ins(3)}`}><span className="sx-k">Recorded once at the checked revision</span><span className="sx-tag ok">tests</span><span className="sx-tag ok">lint</span><span className="sx-tag ok">types</span><span className="sx-tag ok">build</span></div>
      </div>

      <div className={scene(4)} aria-hidden={ch !== 4}>
        <div className={`sx-proof ${ins(1)}`}><span className="sx-chip ok">✓ 3 of 3 points hold</span><span className="sx-chip ok">14 tests, recorded</span><span className="sx-chip ok">2 screenshots</span></div>
        <div className="sx-two">
          <div className="sx-diff">
            <div className="sx-dfh"><span className="sx-code">delivery-row.tsx</span><span className="sx-add">+12</span><span className="sx-del">−2</span></div>
            <div className="sx-dl0"><i>40</i>{"  <Row id={row.id}>"}</div>
            <div className="sx-dl0"><i>41</i>{"    <Cell>{row.status}</Cell>"}</div>
            <div className="sx-dl0 del"><i>42</i>{"-   <Cell>{row.event}</Cell>"}</div>
            <div className="sx-dl0 add"><i>42</i>{"+   <Cell mono>{row.event}</Cell>"}</div>
            <div className="sx-dl0 add"><i>43</i>{"+   <Tries count={row.tries} />"}</div>
            <div className={`sx-thread ${ins(2)}`}>
              <div className="sx-tm"><span className="sx-av b">D</span><p><small>Dana · teammate</small>Can support see this without the log?</p></div>
              <div className={`sx-tm ${ins(3)}`}><span className="sx-av">Y</span><p><small>You</small>Yes, the meter shows it. See screenshot 2.</p></div>
            </div>
            <div className="sx-dl0"><i>44</i>{"  </Row>"}</div>
          </div>
          <div className={`sx-pr sx-hide ${ins(1)}`}>
            <p className="sx-k">Pull request, written for you</p>
            <h4>Retry failed webhooks</h4>
            <ul><li>Failed deliveries retry three times, a minute apart</li><li>Then the customer gets one mail</li><li>Support sees the count in each row</li></ul>
            <p className="sx-k">Evidence and the plan are linked</p>
          </div>
        </div>
        <div className={`sx-row2 ${ins(3)}`}><span className="sx-k">Team review</span><span className="sx-tag ok">Dana approved</span><span className="sx-tag">Ben commented</span><span className="sx-tag">Chen invited</span></div>
      </div>

      <div className={scene(5)} aria-hidden={ch !== 5}>
        <div className="sx-two">
          <div className="sx-col">
            <div className="sx-pdoc sx-hide">
              <p className="sx-k">Plan · Decisions made for you</p>
              <p className="sx-para">A failed delivery is sent again <mark>one minute apart</mark>, three times, then the customer gets one mail.</p>
            </div>
            <div className={`sx-pop ${ins(1)}`}>
              <b>Ask about this passage</b>
              <div className="sx-who"><span className={`sx-whoi ${on(1)}`}><span className="sx-av b">D</span>Dana</span><span className="sx-whoi"><span className="sx-av b">B</span>Ben</span><span className="sx-whoi"><span className="sx-av b">C</span>Chen</span></div>
              <span className="sx-field">Is one minute right for the partner API?</span>
              <span className={`sx-fake p${ch === 5 && step === 2 ? " press" : ""}`} style={{ alignSelf: "flex-start" }}>Send the question</span>
            </div>
            <div className="sx-row2 sx-hide"><span className="sx-k">Ask about</span><span className="sx-tag">a passage</span><span className="sx-tag">a diagram</span><span className="sx-tag">a section</span><span className="sx-tag">the whole plan</span><span className="sx-tag">a build step</span><span className="sx-tag">a comment thread</span></div>
          </div>
          <div className="sx-col">
            <div className={`sx-slack sx-hide ${ins(3)}`}><span className="sx-av g">#</span><p><small>Slack · QualityLayer</small>Max asked you about <b>Retry failed webhooks</b>. <u>Open in QualityLayer</u></p></div>
            <div className={`sx-ans ${ins(4)}`}><span className="sx-av b">D</span><p><small>Dana · suggests a change<span className="sx-via">via Claude Code</span></small>Back off instead: 1, 5, then 15 minutes. The partner API limits retries.</p></div>
            <div className={`sx-cmt sx-hide ${ins(5)}`}><span className="sx-av">Y</span><p><small>Your agent</small>I’ve updated the plan with Dana’s back-off. Approve it when you’re ready.</p></div>
          </div>
        </div>
      </div>

      <div className={scene(6)} aria-hidden={ch !== 6}>
        <div className="sx-two">
          <div className="sx-cardw sx-hide">
            <p className="sx-k">Max asked you · Retry failed webhooks</p>
            <div className="sx-q">Is one minute right for the partner API?</div>
            <div className="sx-qbtns"><span>Looks right</span><span>Suggest a change</span><span>Reply</span><span>Hand on</span></div>
            <p className="sx-lbl">Work on it with your agent</p>
            <div className="sx-seg3"><span className="on">Claude Code</span><span>Codex</span><span>Grok Bot</span></div>
            <div className="sx-cmdl"><span>/ql answer 7f3a</span><u>Copied ✓</u></div>
            <p className="sx-lbl">Or the agent leaves a draft here</p>
            <div className="sx-row2"><span className="sx-fake p">Send</span><span className="sx-fake">Edit</span><span className="sx-fake">Discard</span></div>
          </div>
          <div className="sx-term">
            <p className="sx-k">Dana’s Claude Code</p>
            <p className={`me ${ins(1)}`}>/ql answer 7f3a</p>
            <p className={ins(1)}>Read the ask, the plan and partner-client.ts.</p>
            <p className={`q ${ins(2)}`}>? How strict is the partner’s rate limit?</p>
            <p className={`sel ${ins(2)}`}>› 10 calls a minute (Recommended)</p>
            <p className={`ok ${ins(3)}`}>Draft (suggests a change): back off 1, 5, then 15 minutes.</p>
            <p className={`q ${ins(4)}`}>? Send this as your answer to Max?</p>
            <p className={`sel ${ins(4)}`}>› Send it</p>
            <p className={`ok ${ins(5)}`}>✓ Sent to Max · marked “via Claude Code”</p>
          </div>
        </div>
      </div>

      <div className={scene(7)} aria-hidden={ch !== 7}>
        <div className={`sx-tbl ${ins(1)}`}>
          <div className="sx-tblh">Asked of you</div>
          <div className="sx-askr"><span className="sx-av b">A</span><span>Anna asks about the <b>Billing export</b> plan</span><span className="sx-chip you">Plan</span></div>
          <div className="sx-askr sx-hide"><span className="sx-av b">C</span><span>Chen asks about a build step in <b>SSO group sync</b></span><span className="sx-chip you">Implement</span></div>
        </div>
        <div className={`sx-tbl ${ins(2)}`}>
          <div className="sx-tblh">Shared tasks</div>
          <div className="sx-tr"><span className="sx-av b">A</span><span>Billing export</span><span className="sx-sp cur">Plan</span><span className="sx-mut">waits for Ben and you</span></div>
          <div className="sx-tr"><span className="sx-av b">C</span><span>SSO group sync</span><span className="sx-sp cur ag">Implement</span><span className="sx-mut">slice 2 of 4</span></div>
          <div className="sx-tr sx-hide"><span className="sx-av b">B</span><span>Invoice PDFs</span><span className="sx-sp cur ag">Verify</span><span className="sx-mut">being checked</span></div>
          <div className="sx-tr sx-hide"><span className="sx-av">Y</span><span>Retry failed webhooks</span><span className="sx-sp done">Review</span><span className="sx-mut">Dana commented</span></div>
        </div>
        <div className={`sx-share ${ins(3)}`}><span className="sx-av g">↗</span><div><b>A link for people outside the team</b><small>They read the plan and comment. Their comments reach your agent.</small></div><span className="sx-fake">Copy link</span></div>
      </div>

      <div className={scene(8)} aria-hidden={ch !== 8}>
        <div className="sx-two">
          <div className={`sx-set ${ins(1)}`}>
            <div className="sx-setr"><span>Helper model<small>Builds, polishes, fixes</small></span><span className="sx-sel">Sonnet 5.5</span></div>
            <div className="sx-setr"><span>Judge model<small>Checks the finished change</small></span><span className="sx-sel">Opus 5.5</span></div>
            <div className="sx-setr"><span>Second opinion<small>Another vendor reviews the plan and the change</small></span><span className="sx-tog" /></div>
            <div className="sx-setr sx-hide"><span>Always run checkpoints<small>Off: only after risky slices</small></span><span className="sx-tog" /></div>
            <div className="sx-setr sx-hide"><span>Token budget per task</span><span className="sx-sel">3M tokens</span></div>
          </div>
          <div className={`sx-cost ${ins(2)}`}>
            <p className="sx-k">This task · tokens per step</p>
            {COST.map(([label, v]) => (
              <div className="sx-cb" key={label}>
                <span>{label}</span>
                <span className="sx-cbt"><i className={ch !== 8 || at(2) ? "on" : ""} style={{ width: `${Math.round((v / 860) * 100)}%` }} /></span>
                <span>{v}K</span>
              </div>
            ))}
            <div className="sx-budget"><span>Estimated at list prices</span><span><b>1.9M</b> of 3M</span></div>
          </div>
        </div>
        <div className={`sx-helpers sx-hide ${ins(3)}`}>
          <p className="sx-k">Implement and Verify · tokens per helper</p>
          <div><span>Slice helpers, 3 side by side · Sonnet 5.5</span><span>640K</span></div>
          <div><span>Polish · Sonnet 5.5</span><span>110K</span></div>
          <div><span>Judge · Opus 5.5</span><span>170K</span></div>
        </div>
      </div>

      <div className={scene(9)} aria-hidden={ch !== 9}>
        <div className="sx-two">
          <div className="sx-term">
            <p className="sx-k">Claude Code</p>
            <p className={`ok ${ins(1)}`}>The plan is ready. Review it in QualityLayer.</p>
            <p className={ins(1)}>Planning stops here. After you approve, start a fresh session and type /ql implement.</p>
            <div className={`sx-band ${ins(2)}`}><span className="sx-mark" />Retry failed webhooks · the plan waits for you · 1 answer in</div>
            <p className="sx-prompt">›</p>
          </div>
          <div className="sx-col">
            <div className={`sx-notif ${ins(3)}`}><span className="sx-mark" /><p><small>QualityLayer · from the menu bar</small>The plan for Retry failed webhooks waits for you.</p></div>
            <div className={`sx-term sx-hide ${ins(4)}`}><p className="sx-k">Codex · another task</p><p>Implementing Invoice PDFs · slice 2 of 4</p><p className="ok">✓ check slice 2 · exit 0 · recorded</p></div>
            <div className={`sx-peer sx-hide ${ins(5)}`}><span className="sx-pch">Claude Code</span><span className="sx-parr" /><span className="sx-pch">Codex</span></div>
            <p className={`sx-k sx-hide ${ins(5)}`} style={{ textAlign: "center" }}>Sessions ask each other for a review</p>
          </div>
        </div>
        <div className={`sx-row2 sx-hide ${ins(5)}`}><span className="sx-k">Your agents run in</span><span className="sx-tag">the terminal</span><span className="sx-tag">their desktop apps</span><span className="sx-tag">your IDE</span><span className="sx-tag">WSL and servers</span></div>
      </div>
    </>
  );
}
