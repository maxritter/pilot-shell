import { useEffect, useRef, useState } from "react";

type Tab = "overview" | "evidence" | "try" | "pr" | "conv";
type Filter = "open" | "all" | "resolved";
type Thread = { on: string; i: string; who: string; when: string; text: string; open: boolean; state: string; tone: "ch" | "an" | "fx" | "rp"; reply?: string; replyWhen?: string };

const SLUG = "queue-migration";
const REVIEWERS: [string, "ok" | "ch"][] = [["B", "ok"], ["A", "ch"], ["C", "ok"]];
/** What the change does, each with its proof; a point can carry a thread or a screenshot. */
const DONE: { t: string; thread?: { i: string; who: string; text: string }; shot?: string }[] = [
  { t: "Every producer enqueues through one adapter." },
  { t: "No job is lost or run twice during the move.", thread: { i: "A", who: "Anna", text: "A capture that times out during the switch: is that covered by a scenario?" } },
  { t: "On-call moves a job type back without a deploy.", shot: "switch panel" },
];
const EVIDENCE: [string, string][] = [["214", "Checks passed"], ["4 / 4", "Scenarios"], ["2 / 2", "Truths"], ["6 / 6", "Done means"]];
const TRY_IT: [string, string?][] = [
  ["Start the queue:", "make dev"],
  ["Open the admin, then Jobs › Switch panel, and move invoice.render to the new client."],
  ["Enqueue an invoice, watch it land on the new client, then move it back."],
];
const THREADS: Thread[] = [
  { on: "Done means · No job is lost or run twice", i: "A", who: "Anna", when: "2 h ago", text: "A capture that times out during the switch: is that covered by a scenario?", open: true, state: "changes requested", tone: "ch" },
  { on: "Decision · one adapter for both clients", i: "B", who: "Ben", when: "3 h ago", text: "Log which client took the job, so support can see it.", open: true, state: "comment", tone: "an" },
  { on: "Picture · switch panel", i: "C", who: "Chen", when: "yesterday", text: "The “move back” button needs a confirm.", open: false, state: "fixed", tone: "fx", reply: "Decided with you: a confirm with the job type’s name. Fixed test first in round 2.", replyWhen: "yesterday" },
];
const TABS: [Tab, string, string][] = [["overview", "Overview", ""], ["evidence", "Evidence", ""], ["try", "Try it", ""], ["pr", "Pull request", "#142"], ["conv", "Conversation", "3"]];
const LOOP: { tone: "you" | "ag" | "vi" | "tl"; title: string; text: string; ends?: boolean }[] = [
  { tone: "you", title: "The team reviews", text: "Comments on any requirement, decision or screenshot; the code goes through the pull request." },
  { tone: "you", title: "Back to your agent", text: "One command hands the open comments, the pull request’s too, to your agent." },
  { tone: "ag", title: "You decide together", text: "Your agent goes through each comment with you before it changes anything." },
  { tone: "vi", title: "Every comment is settled", text: "Each one ends in one of three ways:", ends: true },
  { tone: "tl", title: "Checked again", text: "Fixes are tested, then the whole change is checked again." },
  { tone: "you", title: "Approve and ship", text: "Reviewers look again, and it ships once everyone approves." },
];

/** An illustrative Review screen: the team reviews why and how the change was made, with the proof. */
export default function ReviewTeam() {
  const [tab, setTab] = useState<Tab>("overview");
  const [open, setOpen] = useState(1);
  const [agent, setAgent] = useState<"cc" | "cx">("cc");
  const [filter, setFilter] = useState<Filter>("open");
  const [copied, setCopied] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);

  const prompt = `${agent === "cc" ? "/ql" : "$ql"} review ${SLUG}`;
  const copy = () => {
    navigator.clipboard?.writeText(prompt).catch(() => undefined);
    setCopied(true);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setCopied(false), 1800);
  };
  const threads = THREADS.filter((t) => filter === "all" || (filter === "open" ? t.open : !t.open));

  return (
    <div className="r2-root">
      <div className="r2-win" aria-label="Illustrative Review screen">
        <div className="r2-head">
          <div className="r2-title">
            <b>Queue migration</b>
            <span className="r2-meta"><span>In review</span><span className="r2-open">2 open threads</span><span>Checked today · round 2 · by two AIs that did not write it</span></span>
          </div>
          <div className="r2-revs" title="Reviewers">
            <span className="r2-avs">{REVIEWERS.map(([i, tone]) => <span key={i} className={`r2-av r2m-${tone}`}>{i}</span>)}</span>2 of 3 approved
          </div>
          <button type="button" className="r2-ship" disabled tabIndex={-1}>Approve and ship</button>
          <p className="r2-wait">Waits for: 2 open threads, Anna’s approval</p>
        </div>
        <div className="r2-card">
          <div className="r2-ct"><b>Back to your agent</b><span>2 open threads from your reviewers. Start a new session with this command: your agent gets the threads and goes through each one with you before it changes anything.</span></div>
          <div className="r2-prompt">
            <div role="group" aria-label="Agent" className="r2-seg">
              <button type="button" onClick={() => setAgent("cc")} aria-pressed={agent === "cc"} className={`r2-sb${agent === "cc" ? " r2m-on" : ""}`}>Claude Code</button>
              <button type="button" onClick={() => setAgent("cx")} aria-pressed={agent === "cx"} className={`r2-sb${agent === "cx" ? " r2m-on" : ""}`}>Codex</button>
            </div>
            <span className="r2-code">{prompt}</span>
            <button type="button" onClick={copy} className="r2-copy">{copied ? "Copied" : "Copy"}</button>
          </div>
        </div>
        <div role="tablist" aria-label="Review" className="r2-tabs">
          {TABS.map(([id, label, n]) => (
            <button key={id} type="button" role="tab" aria-selected={tab === id} onClick={() => setTab(id)} className={`r2-tab${tab === id ? " r2m-on" : ""}`}>
              {label}{n ? <span className="r2-n">{n}</span> : null}
            </button>
          ))}
        </div>
        <div className="r2-body" role="tabpanel">
          {tab === "overview" ? (
            <div>
              <div className="r2-health"><b>Code health</b><span className="r2-plus">+312</span><span className="r2-minus">−88</span><span>1 new module, with its reason</span><span className="r2-simp">Simplify removed 41 lines</span></div>
              <p className="r2-h">What this change does</p>
              <p className="r2-sub">Everything you asked for, with its proof. Comment on any point.</p>
              <div className="r2-list">
                {DONE.map((m, i) => (
                  <div key={m.t} className="r2-item">
                    <div className="r2-row">
                      <span className="r2-txt">{m.t}</span>
                      <span className="r2-proven">PROVEN</span>
                      <button type="button" onClick={() => setOpen(open === i ? -1 : i)} aria-expanded={open === i} aria-label={m.thread ? "1 comment" : "Comment"} className={`r2-cc${m.thread ? " r2m-has" : ""}`}>
                        <span aria-hidden="true" className="r2-ci" />{m.thread ? "1" : ""}
                      </button>
                    </div>
                    {m.thread && open === i ? (
                      <div className="r2-thread">
                        <div className="r2-msg"><span className="r2-av r2m-ch">{m.thread.i}</span><div><b>{m.thread.who}</b><span className="r2-state r2m-ch">changes requested</span><small>2 h ago</small>{m.thread.text}</div></div>
                      </div>
                    ) : null}
                    {m.shot ? <span className="r2-shot"><i aria-hidden="true" />What a person sees · {m.shot}</span> : null}
                  </div>
                ))}
              </div>
            </div>
          ) : null}
          {tab === "evidence" ? (
            <div>
              <p className="r2-h">How it was verified</p>
              <p className="r2-sub">Checked by an AI that did not write the code, then by a second AI from another vendor.</p>
              <div className="r2-tiles">{EVIDENCE.map(([n, label], i) => <div key={label} className={`r2-tile r2m-t${i + 1}`}><b>{n}</b><span>{label}</span></div>)}</div>
            </div>
          ) : null}
          {tab === "try" ? (
            <div>
              <p className="r2-h">Try the whole change</p>
              <p className="r2-sub">Written by the AI that checked it, for whoever reviews.</p>
              <ol className="r2-steps">{TRY_IT.map(([t, cmd]) => <li key={t}>{t} {cmd ? <span className="r2-mono">{cmd}</span> : null}</li>)}</ol>
            </div>
          ) : null}
          {tab === "pr" ? (
            <div>
              <p className="r2-h">Pull request</p>
              <p className="r2-sub">Opened from Review, with a description drafted from the plan. The code is reviewed there, as always; its open comments come back to your agent with the others.</p>
              <div className="r2-pr">
                <span className="r2-prn">#142</span>
                <span className="r2-prt">Jobs move to the new queue client behind one adapter</span>
                <span className="r2-state r2m-fx">open</span>
                <span className="r2-prc"><span aria-hidden="true">✓</span>12 of 12 checks passed</span>
                <span className="r2-prb">Open on GitHub</span>
              </div>
            </div>
          ) : null}
          {tab === "conv" ? (
            <div>
              <p className="r2-h">Conversation</p>
              <div role="group" aria-label="Filter threads" className="r2-filters">
                {(["open", "all", "resolved"] as Filter[]).map((f) => (
                  <button key={f} type="button" onClick={() => setFilter(f)} aria-pressed={filter === f} className={`r2-f${filter === f ? " r2m-on" : ""}`}>{f[0].toUpperCase() + f.slice(1)}</button>
                ))}
              </div>
              <div className="r2-list">
                {threads.map((t) => (
                  <div key={t.on} className="r2-tc">
                    <div className="r2-on"><span>On</span><span className="r2-anchor">{t.on}</span><span className={`r2-state r2m-${t.tone}`}>{t.state}</span><span className="r2-link">Show</span></div>
                    <div className="r2-msg"><span className="r2-av r2m-ch">{t.i}</span><div><b>{t.who}</b><small>{t.when}</small>{t.text}</div></div>
                    {t.reply ? <div className="r2-msg"><span className="r2-av r2m-ag">CC</span><div><b>Your agent</b><small>{t.replyWhen}</small>{t.reply}</div></div> : null}
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </div>

      <ol className="r2-loop" aria-label="What happens to open threads">
        {LOOP.map((s) => (
          <li key={s.title} className={`r2-step r2m-${s.tone}`}>
            <span aria-hidden="true" className="r2-dot" />
            <span className="r2-sx">
              <b>{s.title}</b>
              <span>{s.text}</span>
              {s.ends ? <span className="r2-ends"><span className="r2-state r2m-fx">fixed</span><span className="r2-state r2m-an">answered</span><span className="r2-state r2m-rp">replanned</span></span> : null}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
