import { useState, type CSSProperties } from "react";

type Corner = "tl" | "tr" | "bl" | "br";
type Tone = "cc" | "cx" | "mix";
const NODES: Record<Corner, [mark: string, agent: string, repo: string, tone: Tone]> = {
  tl: ["CC", "Claude Code", "acme/payments", "cc"],
  tr: ["CC", "Claude Code", "acme/api", "cc"],
  bl: ["CX", "Codex", "acme/payments", "cx"],
  br: ["CX", "Codex", "acme/web", "cx"],
};
type Scenario = { label: string; edge: "top" | "bot" | "lft" | "rgt"; nodes: Corner[]; tone: Tone; tag: [string, string, string]; caption: string; msgs: [Corner, Corner, string][] };
const SCENARIOS: Scenario[] = [
  { label: "Ask for a review", edge: "lft", nodes: ["tl", "bl"], tone: "mix", tag: ["45px", "50%", "ask"],
    caption: "Claude Code asks the Codex session next to it for a review and waits for the answer. Different vendor, different blind spots.",
    msgs: [["tl", "bl", "Review the retry logic in jobs/adapter.ts before I commit."], ["bl", "tl", "One issue: a capture that times out can run twice. Line 88."], ["tl", "bl", "Fixed, test first. Thanks."]] },
  { label: "Hand over a task", edge: "top", nodes: ["tl", "tr"], tone: "cc", tag: ["50%", "32px", "hand over"],
    caption: "One Claude Code session hands work to another in a different repository and waits for the result.",
    msgs: [["tl", "tr", "Add the export endpoint checkout needs. Tell me when its tests pass."], ["tr", "tl", "Done: GET /exports with 12 tests passing. The contract is in api/exports.md."]] },
  { label: "Talk a problem through", edge: "bot", nodes: ["bl", "br"], tone: "cx", tag: ["50%", "calc(100% - 32px)", "talk"],
    caption: "Two Codex sessions talk a problem through, then each goes back to its own work.",
    msgs: [["br", "bl", "How should the switch panel show a job type that is still moving?"], ["bl", "br", "A pending state with the number of jobs left on the old client."], ["br", "bl", "Good. I will add it to the mockup."]] },
];
const EDGES: [Scenario["edge"], "h" | "v"][] = [["top", "h"], ["bot", "h"], ["lft", "v"], ["rgt", "v"]];

const color = (tone: Tone) => (tone === "cc" ? "var(--pe-cc)" : tone === "cx" ? "var(--pe-cx)" : "var(--ql-accent)");
const label = (id: Corner) => `${NODES[id][1]} · ${NODES[id][2].split("/")[1]}`;
const line = (c: string) => ({ "--pe-line": c }) as CSSProperties;

/** Four agent sessions on one computer, and three ways they talk to each other. */
export default function Peers() {
  const [index, setIndex] = useState(0);
  const sc = SCENARIOS[index];
  const tone = color(sc.tone);

  return (
    <div className="pe-root">
      <div className="pe-map" role="img" aria-label={`Four agent sessions on one machine, two Claude Code and two Codex, linked in every direction; ${sc.label.toLowerCase()}`}>
        <div className="pe-in">
          {EDGES.map(([edge, dir]) => (
            <div key={edge} className={`pe-e pe-${dir} pe-${edge}${sc.edge === edge ? " pe-act" : ""}`} style={line(tone)}><span aria-hidden="true" className="pe-dot" /></div>
          ))}
          {(Object.keys(NODES) as Corner[]).map((id) => {
            const [mark, agent, repo, t] = NODES[id];
            return (
              <div key={id} className={`pe-node pe-${id} pe-${t}n${sc.nodes.includes(id) ? " pe-act" : ""}`}>
                <span aria-hidden="true" className="pe-mark">{mark}</span>
                <span className="pe-nt"><b>{agent}</b><span>{repo}</span></span>
              </div>
            );
          })}
          <span className="pe-tag" style={{ left: sc.tag[0], top: sc.tag[1], ...line(tone) }}>{sc.tag[2]}</span>
        </div>
      </div>

      <div className="pe-side">
        <div role="group" aria-label="Scenario" className="pe-tabs">
          {SCENARIOS.map((s, i) => (
            <button key={s.label} type="button" onClick={() => setIndex(i)} aria-pressed={i === index} className={`pe-tab${i === index ? " pe-on" : ""}`} style={{ "--pe-tc": color(s.tone) } as CSSProperties}>
              <span aria-hidden="true" className="pe-sw" />{s.label}
            </button>
          ))}
        </div>
        <p className="pe-cap" aria-live="polite">{sc.caption}</p>
        <div className="pe-thread">
          {sc.msgs.map(([from, to, text], i) => (
            <div key={text} className={`pe-msg ${i % 2 === 0 ? "pe-me" : "pe-you"}`} style={{ "--pe-from": color(NODES[from][3]) } as CSSProperties}>
              <span className="pe-who">{label(from)}<em>{` → ${label(to)}`}</em></span>
              <span>{text}</span>
            </div>
          ))}
        </div>
        <ul className="pe-facts" aria-label="How it works">
          <li className="pe-fact">Only on your computer</li>
          <li className="pe-fact">Any pair of agents, either direction</li>
          <li className="pe-fact">A built-in limit stops endless back-and-forth</li>
        </ul>
      </div>
    </div>
  );
}
