import { useState } from "react";

type Person = { av: string; name: string; verdict: string; tone: "ok" | "ch" | "cm"; quote: string; outside?: boolean };
const TEAM: Person[] = [
  { av: "B", name: "Ben", verdict: "Approved", tone: "ok", quote: "The adapter is the right seam." },
  { av: "A", name: "Anna", verdict: "Asked for changes", tone: "ch", quote: "Keep the idempotency-key test green when payment capture moves." },
];
const GUEST: Person = { av: "S", name: "Sam · via link", verdict: "Comment", tone: "cm", quote: "Can support see which client a job ran on?", outside: true };
const TASKS = [
  { av: "A", title: "Billing retry schedule", stage: "Design", status: "Waits for Anna’s review", live: false },
  { av: "C", title: "Webhook signing v2", stage: "Outline", status: "Waits for Chen’s review", live: false },
  { av: "B", title: "API rate-limit tiers", stage: "Build 4/9", status: "Building now", live: true },
];

function Switch({ on, label, onToggle }: { on: boolean; label: string; onToggle: () => void }) {
  return <button type="button" onClick={onToggle} role="switch" aria-checked={on} aria-label={label} className={`tm-sw${on ? " on" : ""}`} />;
}

/** Sharing a plan with the team, how their comments reach your agent, and the team's shared tasks. */
export default function PlanTeam({ onOpen }: { onOpen?: () => void }) {
  const [team, setTeam] = useState(true);
  const [link, setLink] = useState(true);
  const waiting = (team ? 2 : 0) + (link ? 1 : 0);
  const people = [...TEAM.map((p) => ({ ...p, on: team })), { ...GUEST, on: link }];
  const docLine = team
    ? link ? "3 comments and 2 reviews, all passed on to your agent" : "2 comments and 2 reviews, passed on to your agent"
    : link ? "1 comment from outside the team" : "Only you see this plan";

  return (
    <div className="tm">
      <div className="tm-main">
        <div className="tm-share" aria-label="Share, as in the Cockpit">
          <div className="tm-sh">Share<span>Queue migration</span></div>
          <div className="tm-row">
            <div className="tm-rt">Acme team<Switch on={team} label="Share with the Acme team" onToggle={() => setTeam(!team)} /></div>
            <p className="tm-rd">Teammates read the plan, comment, approve or ask for changes, and follow the build in their own Cockpit.</p>
          </div>
          <div className="tm-row">
            <div className="tm-rt">People outside the team<Switch on={link} label="Share a link with people outside the team" onToggle={() => setLink(!link)} /></div>
            {link ? <div className="tm-link"><span>qualitylayer.dev/s/q7f2…</span><span className="tm-copy" aria-hidden="true">Copy</span></div> : null}
            <p className="tm-rd">They can read and comment without an account.</p>
          </div>
          <div className="tm-row">
            <div className="tm-rt">Ask a teammate</div>
            <p className="tm-rd">Ask someone on the team about any passage, diagram or table. They get a notification, and if you need their answer, approval waits for it.</p>
          </div>
          <div className="tm-foot"><span>Team plan</span><span className="tm-wait">{waiting ? `${waiting} comment${waiting === 1 ? "" : "s"} waiting` : "Nothing waiting"}</span></div>
        </div>

        <div className="tm-flow" aria-label="How comments reach the plan and your agent">
          <div className="tm-people">
            {people.map((p) => (
              <div key={p.name} className={`tm-p${p.on ? "" : " off"}`}>
                <span className={`tm-av${p.outside ? " out" : ""}`} aria-hidden="true">{p.av}</span>
                <div className="tm-pt">
                  <span className="tm-pn">{p.name}<span className={`tm-v ${p.tone}`}>{p.verdict}</span></span>
                  <p className="tm-q">{p.quote}</p>
                </div>
              </div>
            ))}
          </div>
          <span aria-hidden="true" className="tm-ln" />
          <div className="tm-doc">
            <small>02-design.md</small>
            <b>Jobs move to the new queue client behind one adapter</b>
            <span>{docLine}</span>
          </div>
          <span aria-hidden="true" className="tm-ln" />
          <div className="tm-end">
            <div className="tm-node"><b><span aria-hidden="true" className="tm-i ag" />Your agent</b><span>Answers every comment and changes the plan where it agrees.</span></div>
            <span aria-hidden="true" className="tm-vl" />
            <div className="tm-node you"><b><span aria-hidden="true" className="tm-i you" />You decide</b><span>Their feedback is advice. You approve.</span></div>
          </div>
        </div>
      </div>

      <div className="tm-ws">
        <div className="tm-wh">
          <div><b>Team workspace</b> <span>· every shared plan and its comments, in one place for the team</span></div>
          {onOpen ? <button type="button" onClick={onOpen} className="tm-open">Open it in the Cockpit</button> : null}
        </div>
        {TASKS.map((t) => (
          <div key={t.title} className="tm-wr">
            <span className="tm-av" aria-hidden="true">{t.av}</span>
            <span className="tm-wt">{t.title}</span>
            <span className="tm-ws-st">{t.stage}</span>
            <span className={`tm-ws-s ${t.live ? "live" : "you"}`}>{t.live ? <span aria-hidden="true" className="tm-bar"><i /></span> : null}{t.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
