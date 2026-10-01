import { useState } from "react";
import { useNarrow } from "@/hooks/useNarrow";
import { useDemoTour, type Target } from "./demoTour";

type Kind = "you" | "ag" | "out";
/** A step: its id, name, caption, who acts, and where it opens in the Cockpit (null: nowhere). */
type Node = [id: string, name: string, caption: string, who: Kind, target: Target | null];
type Group = { name: "Plan" | "Build" | "Check" | "Release"; sub: string; flex: number; hue?: string; out?: boolean; nodes: Node[] };

const GROUPS: Group[] = [
  { name: "Plan", sub: "Before any code", flex: 4, hue: "g-violet", nodes: [
    ["frame", "Frame", "Agree what done means", "you", "frame"],
    ["research", "Research", "Find what already exists", "you", "research"],
    ["design", "Design", "Decide with diagrams and mockups", "you", "design"],
    ["outline", "Outline", "Split into small, tested slices", "you", "outline"]] },
  { name: "Build", sub: "Tested as it goes", flex: 4, hue: "g-blue", nodes: [
    ["handoff", "Handoff", "Pick the agent that builds", "you", "build:0"],
    ["build", "Build", "Write the test, then the code", "ag", "build:1"],
    ["checkpoint", "Checkpoint", "Run it end to end", "ag", { view: "task", id: "webhook", doc: "checkpoint" }],
    ["simplify", "Simplify", "Make the whole change simpler", "ag", null]] },
  { name: "Check", sub: "Against your request", flex: 2, hue: "g-teal", nodes: [
    ["verify", "Verify", "An independent check, with evidence", "ag", "verify"],
    ["review", "Review", "You review the finished change", "you", "review"]] },
  { name: "Release", sub: "Your own pipeline", flex: 1, out: true, nodes: [
    ["deploy", "Deploy", "Outside QualityLayer", "out", null]] },
];

type RouteKey = "feature" | "bug" | "quick";
type Route = { label: string; note: string; off: string[]; renamed: Record<string, [string, string]>; benefit: Partial<Record<Group["name"], string>> };

const ROUTES: Record<RouteKey, Route> = {
  feature: { label: "Feature", note: "the full plan. You approve each part before any code is written.", off: [], renamed: {}, benefit: {} },
  bug: { label: "Bug", note: "the bug is reproduced and its cause found before anything is fixed.", off: ["design"],
    renamed: { research: ["Diagnose", "Reproduce it, find the root cause"], outline: ["Outline", "The smallest fix, test-first"] },
    benefit: { Plan: "First a test that shows the bug and its exact cause, then the fix." } },
  quick: { label: "Quick change", note: "a rename, a setting, an obvious fix. Nothing to review up front; if it turns out bigger, the agent switches to a full plan.",
    off: ["frame", "research", "design", "outline", "handoff", "checkpoint", "simplify"],
    renamed: { build: ["Change", "Failing test, then the change"], verify: ["Prove it runs", "Run it, keep evidence"] },
    benefit: { Plan: "Skipped: there is nothing to decide.", Build: "The change still starts with a test." } },
};

const BENEFITS: Partial<Record<Group["name"], string>> = {
  Plan: "Wrong scope and weak designs are caught while they are still cheap to fix.",
  Build: "Every slice starts with a test. After each one the program runs end to end, and it stops for you only if something keeps failing.",
  Check: "The running program is checked against what you asked for, and the evidence is kept for you.",
};

export default function Lifecycle() {
  const [key, setKey] = useState<RouteKey>("feature");
  const tour = useDemoTour();
  // Phones have no Cockpit demo to open, so the steps are plain text there.
  const narrow = useNarrow();
  const route = ROUTES[key];

  return (
    <section id="lifecycle" className="w7-sec" aria-labelledby="lifecycle-h">
      <div className="w7-wrap">
        <div className="w7-head-row">
          <div>
            <h2 id="lifecycle-h" className="w7-h2">How a request becomes a reviewed change</h2>
            <p className="w7-lead w7-lead-tight">
              Features, bugs and small changes each take their own route.{narrow ? "" : " Select a step to see it in the Cockpit."}
            </p>
          </div>
          <div role="group" aria-label="Route" className="w7-seg">
            {(Object.keys(ROUTES) as RouteKey[]).map((k) => (
              <button key={k} type="button" onClick={() => setKey(k)} aria-pressed={k === key} className={`w7-seg-b${k === key ? " on" : ""}`}>{ROUTES[k].label}</button>
            ))}
          </div>
        </div>
        <p className="v8-rnote" aria-live="polite"><b>{route.label}</b> · {route.note}</p>

        <div className="w7-lc">
          {GROUPS.map((g) => {
            const benefit = route.benefit[g.name] ?? BENEFITS[g.name];
            return (
              <div key={g.name} className={`w7-g w7-f${g.flex}${g.hue ? ` ${g.hue}` : ""}`}>
                <p className="w7-gl"><b>{g.name}</b><span>{g.sub}</span></p>
                <div className="w7-br" aria-hidden="true" />
                <ol className={`w7-ns${g.out ? " out" : ""}`} aria-label={`${g.name} stages`}>
                  {g.nodes.map(([id, baseName, baseCaption, who, baseTarget]) => {
                    const skipped = route.off.includes(id);
                    const renamed = route.renamed[id];
                    const name = renamed ? renamed[0] : baseName;
                    const caption = renamed ? renamed[1] : baseCaption;
                    const target: Target | null = id === "research" && key === "bug" ? { view: "task", id: "invoice", doc: "01-diagnosis.md" } : baseTarget;
                    const live = !!target && !skipped && !narrow;
                    const body = (
                      <>
                        <span aria-hidden="true" className={`w7-dot ${who}`} />
                        <span className="w7-tx"><span className="w7-nm">{name}</span><span className="w7-cap">{skipped ? "Skipped" : caption}</span></span>
                      </>
                    );
                    return (
                      <li key={id} className={`w7-n${skipped ? " dim" : ""}${renamed && renamed[0] !== baseName ? " re" : ""}`}>
                        {live ? (
                          <button type="button" className="w7-nb" onClick={() => tour.go(target)} aria-label={`${name}: ${caption}. Open in the Cockpit`}>{body}</button>
                        ) : (
                          <div className="w7-nb">{body}</div>
                        )}
                      </li>
                    );
                  })}
                </ol>
                {benefit ? <p className="w7-bn">{benefit}</p> : null}
              </div>
            );
          })}
        </div>

        <ul className="w7-key" aria-label="Key">
          <li><span aria-hidden="true" className="w7-dot you" />You review</li>
          <li><span aria-hidden="true" className="w7-dot ag" />Agent works</li>
        </ul>
      </div>
    </section>
  );
}
