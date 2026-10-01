import { useState } from "react";
import { useNarrow } from "@/hooks/useNarrow";
import { useDemoTour } from "./demoTour";

const STAGES = ["Frame", "Research", "Design", "Outline", "Build", "Verify", "Review"];
const NOTES = [
  "Frame: you and your agent agree on the problem and what done means.",
  "Research: a helper reads the code without seeing your goal, and you correct the findings.",
  "Design: your agent drafts it with diagrams and mockups, the second AI reviews it, and you approve.",
  "Outline: your agent splits the work into slices, and a helper reads the plan like a new builder.",
  "Build: smaller models build the slices in parallel, testers run each one end to end, and one pass simplifies the result.",
  "Verify: an AI that did not write the code checks it against your request, and the second AI reviews the change.",
  "Review: your team reviews the finished change with you, and you approve it.",
];
const DEFAULT_NOTE = "Choose the model for each helper under Subagents in Settings, set the Second opinion there too, or turn either off. Works with Claude Code, Codex and other agents.";

/** A job: first grid column, last column + 1 (stages are columns 2–8), kind, text, and where it sits in its cell. */
type Job = [from: number, to: number, kind: string, text: string, align?: "start" | "center" | "end"];
const LANES: { name: string; sub: string; jobs: Job[] }[] = [
  { name: "You", sub: "You approve every step", jobs: [[2, 6, "you", "Review and approve each part of the plan"], [6, 7, "you", "Hand off"], [8, 9, "you", "Review"]] },
  { name: "Your agent", sub: "Your best model", jobs: [[2, 6, "lead", "Plans with you, one question at a time"], [6, 8, "lead", "Coordinates the build"]] },
  { name: "Helpers", sub: "Start fresh, a cheaper model", jobs: [[3, 4, "sub hl-teal", "Research"], [5, 6, "sub hl-teal", "Plan check"], [6, 7, "sub hl-teal", "Simplify"]] },
  { name: "Slice builders", sub: "Cheaper models, in parallel", jobs: [[6, 7, "sub hl-s1", "Slice 1", "start"], [6, 7, "sub hl-s2", "Slice 2", "center"], [6, 7, "sub hl-s3", "Slice 3", "end"]] },
  { name: "Testers", sub: "Run the program end to end", jobs: [[6, 7, "sub hl-s1", "Test", "start"], [6, 7, "sub hl-s2", "Test", "center"], [6, 7, "sub hl-s3", "Test", "end"], [7, 8, "sub hl-teal", "Final check"]] },
  { name: "Second AI", sub: "From another vendor", jobs: [[4, 5, "peer hl-violet", "Reviews"], [7, 8, "peer hl-violet", "Reviews"]] },
];

const chip = (j: Job) => `v8-ci ${j[2]}${j[1] - j[0] > 1 ? " span" : ""}`;

export default function Crew() {
  const [stage, setStage] = useState(-1);
  const narrow = useNarrow();
  const tour = useDemoTour();

  return (
    <section id="agents" className="w7-sec w7-sunk" aria-labelledby="agents-h">
      <div className="w7-wrap">
        <h2 id="agents-h" className="w7-h2">One agent plans with you. Others build and check.</h2>
        <p className="w7-lead w7-lead-tight">Fresh helpers on cheaper models build and test from the plan. An AI from another vendor reviews.</p>

        {narrow ? (
          // Phones: one line per role in each step; repeated jobs collapse into one chip.
          <ol className="v8-crew-m" aria-label="Who does what at each stage">
            {STAGES.map((name, k) => (
              <li key={name} className="v8-cm">
                <p className="v8-cmh">{name}</p>
                {LANES.flatMap((lane) => {
                  const jobs = lane.jobs.filter((j) => j[0] === k + 2);
                  if (!jobs.length) return [];
                  const same = jobs.length > 1 && jobs.every((j) => j[3] === jobs[0][3]);
                  const chips = same
                    ? [{ cls: `v8-ci ${jobs[0][2]}`, text: jobs[0][3] === "Test" ? "Each slice, end to end" : jobs[0][3] }]
                    : jobs.map((j) => ({ cls: `v8-ci ${j[2]}`, text: j[3] }));
                  return [
                    <p key={lane.name} className="v8-cmr"><b>{lane.name}</b><span className="v8-cmc">{chips.map((c) => <span key={c.text} className={c.cls}><span aria-hidden="true" className="v8-cdot" />{c.text}</span>)}</span></p>,
                  ];
                })}
              </li>
            ))}
          </ol>
        ) : (
          <div className="v8-crew" aria-label="Who does what at each stage">
            <div className="v8-crow v8-chead" role="group" aria-label="Select a step to see who works on it">
              <span className="v8-chint">Select a step</span>
              {STAGES.map((name, k) => (
                <button key={name} type="button" className={`v8-cst${stage === k ? " v8-on" : ""}`} onClick={() => setStage(stage === k ? -1 : k)} aria-pressed={stage === k}>{name}</button>
              ))}
            </div>
            <div className="v8-crow v12-planrow" aria-hidden="true">
              <p className="v8-clane"><b>The plan</b><span>approved by you</span></p>
              <span className="v12-planbar" style={{ gridColumn: "2 / 9" }}>Every agent below works from the approved plan, so none of them needs your chat history</span>
            </div>
            {LANES.map((lane) => (
              <div key={lane.name} className="v8-crow">
                <p className="v8-clane"><b>{lane.name}</b><span>{lane.sub}</span></p>
                {lane.jobs.map((j, i) => {
                  // With a step selected, jobs outside its column fade, so you see who works then.
                  const col = stage + 2;
                  const fade = stage >= 0 && !(j[0] <= col && col < j[1]);
                  return (
                    <span key={i} className={`${chip(j)}${fade ? " v8-fade" : ""}`} style={{ gridColumn: `${j[0]} / ${j[1]}`, justifySelf: j[4] ?? (j[1] - j[0] > 1 ? "stretch" : "center") }}>
                      <span aria-hidden="true" className="v8-cdot" />{j[3]}
                    </span>
                  );
                })}
              </div>
            ))}
          </div>
        )}

        <div className="v8-crew-foot">
          <p aria-live="polite">{stage >= 0 ? NOTES[stage] : DEFAULT_NOTE}</p>
          {narrow ? null : (
            <div className="w7-btns">
              <button type="button" onClick={() => tour.go("build:0")} className="w7-btn-s w7-btn-sm">Try the handoff</button>
              <button type="button" onClick={() => tour.go("settings")} className="w7-btn-s w7-btn-sm">Open Settings</button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
