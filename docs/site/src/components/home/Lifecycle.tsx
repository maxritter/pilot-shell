import { useState } from "react";
import { useNarrow } from "@/hooks/useNarrow";
import { OPTIONAL_STEPS, type StepName, stepDef } from "@ql/core/optional-steps.ts";
import { ROUTE_LIST, type RouteName } from "@ql/core/task/route-picture.ts";
import { useDemoTour, type Target } from "./demoTour";
import "./lifecycle.css";

type Kind = "you" | "ag" | "out" | "opt";
/** A step: its id, name, caption, who acts, where it opens in the Cockpit (null: nowhere), and the optional steps that belong to it. */
type Node = [id: string, name: string, caption: string, who: Kind, target: Target | null, optional?: readonly StepName[]];
type Group = { name: "Plan" | "Build" | "Check" | "Release"; sub: string; flex: number; hue?: string; out?: boolean; nodes: Node[] };

const QUALITY = OPTIONAL_STEPS.filter((s) => s.group === "quality").map((s) => s.name);

/** Where a click on an optional step opens in the Cockpit demo; the others have no screen of their own yet. */
const STEP_TARGET: Partial<Record<StepName, Target>> = {
  checkpoints: { view: "task", id: "webhook", doc: "checkpoint" },
};

const GROUPS: Group[] = [
  { name: "Plan", sub: "Before any code", flex: 4, hue: "g-violet", nodes: [
    ["frame", "Frame", "Agree what done means", "you", "frame"],
    ["research", "Research", "Find what already exists", "you", "research"],
    ["design", "Design", "Decide with diagrams and mockups", "you", "design", ["second-opinion"]],
    ["outline", "Outline", "Split into small, tested slices", "you", "outline", ["cold-read"]]] },
  { name: "Build", sub: "Tested as it goes", flex: 3, hue: "g-blue", nodes: [
    ["handoff", "Handoff", "Pick the agent that builds", "you", "build:0"],
    ["build", "Build", "Write the test, then the code", "ag", "build:1", ["checkpoints"]]] },
  { name: "Check", sub: "Against your request", flex: 4, hue: "g-teal", nodes: [
    ["quality", "Quality pass", "Extra checks before the final one", "opt", "verify", QUALITY],
    ["verify", "Verify", "An independent check, with evidence", "ag", "verify"],
    ["review", "Review", "You review the finished change", "you", "review"]] },
  { name: "Release", sub: "Your own pipeline", flex: 1, out: true, nodes: [
    ["deploy", "Deploy", "Outside QualityLayer", "out", null]] },
];

/** What each route shows beyond the registry's own name for it. Every route the product has needs an entry. */
type Route = { label: string; order: number; note: string; off: string[]; renamed: Record<string, [string, string]>; benefit: Partial<Record<Group["name"], string>> };

const QUICK_OFF = ["frame", "research", "design", "outline", "handoff", "quality"];

const ROUTES: Record<RouteName, Route> = {
  "spec feature": { label: "Feature", order: 0, note: "the full plan. You approve each part before any code is written.", off: [], renamed: {}, benefit: {} },
  "spec product": { label: "Product feature", order: 1,
    note: "for product managers. You review a PRD (what to build, and how you will know it worked) and a TDD (how it will be built). They replace the frame and the design.",
    off: [],
    renamed: { frame: ["PRD", "Problem, success measure, mockups"], design: ["TDD", "How it is built, for engineers"] },
    benefit: { Plan: "The product decision is agreed in writing before any design or code." } },
  "spec bugfix": { label: "Bug", order: 2, note: "the bug is reproduced and its cause found before anything is fixed.", off: ["design"],
    renamed: { research: ["Diagnose", "Reproduce it, find the root cause"], outline: ["Outline", "The smallest fix, test-first"] },
    benefit: { Plan: "First a test that shows the bug and its exact cause, then the fix." } },
  "quick change": { label: "Quick change", order: 3, note: "a rename, a setting, an obvious change. Nothing to review up front; if it turns out bigger, the agent switches to a full plan.",
    off: QUICK_OFF,
    renamed: { build: ["Change", "Failing test, then the change"], verify: ["Prove it runs", "Run it, keep evidence"] },
    benefit: { Plan: "Skipped: there is nothing to decide.", Build: "The change still starts with a test." } },
  "quick fix": { label: "Quick fix", order: 4, note: "a small bug with an obvious fix. Nothing to review up front; if it turns out bigger, the agent switches to a full plan.",
    off: QUICK_OFF,
    renamed: { build: ["Fix", "Failing test, then the fix"], verify: ["Prove it runs", "Run it, keep evidence"] },
    benefit: { Plan: "Skipped: there is nothing to decide.", Build: "The fix still starts with a test." } },
};

const TABS = ROUTE_LIST.map((r) => r.name).sort((a, b) => ROUTES[a].order - ROUTES[b].order);

const BENEFITS: Partial<Record<Group["name"], string>> = {
  Plan: "Wrong scope and weak designs are caught while they are still cheap to fix.",
  Build: "Every slice starts with a test. Optional checkpoints run the program end to end after marked slices, and the build stops for you only if something keeps failing.",
  Check: "Optional extra checks come first. Then the running program is checked against what you asked for, and the evidence is kept for you.",
};

export default function Lifecycle() {
  const [key, setKey] = useState<RouteName>("spec feature");
  const tour = useDemoTour();
  // Phones have no Cockpit demo to open, so the steps are plain text there.
  const narrow = useNarrow();
  const route = ROUTES[key];
  const { lane, type } = ROUTE_LIST.find((r) => r.name === key)!;

  return (
    <section id="lifecycle" className="w7-sec" aria-labelledby="lifecycle-h">
      <div className="w7-wrap">
        <div className="w7-head-row">
          <div>
            <h2 id="lifecycle-h" className="w7-h2">How a request becomes a reviewed change</h2>
            <p className="w7-lead w7-lead-tight">
              Features, product features, bugs and small changes each take their own route.{narrow ? "" : " Select a step to see it in the Cockpit."}
            </p>
          </div>
          <div role="group" aria-label="Route" className="w7-seg">
            {TABS.map((k) => (
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
                  {g.nodes.map(([id, baseName, baseCaption, who, baseTarget, optional = []]) => {
                    const skipped = route.off.includes(id);
                    const renamed = route.renamed[id];
                    const name = renamed ? renamed[0] : baseName;
                    const caption = renamed ? renamed[1] : baseCaption;
                    const target: Target | null = id === "research" && key === "spec bugfix" ? { view: "task", id: "invoice", doc: "01-diagnosis.md" } : baseTarget;
                    const live = !!target && !skipped && !narrow;
                    // A step the route never runs (a bugfix has nothing to simplify) is left out.
                    const steps = skipped ? [] : optional.filter((n) => stepDef(n).appliesTo({ lane, type, ui: true }));
                    const body = (
                      <>
                        <span aria-hidden="true" className={`w7-dot ${who}`} />
                        <span className="w7-tx"><span className="w7-nm">{name}</span><span className="w7-cap">{skipped ? "Skipped" : caption}</span></span>
                      </>
                    );
                    return (
                      <li key={id} className={`w7-n${skipped ? " dim" : ""}${renamed && renamed[0] !== baseName ? " re" : ""}${id === "quality" ? " lc-wide" : ""}`}>
                        {live ? (
                          <button type="button" className="w7-nb" onClick={() => tour.go(target)} aria-label={`${name}: ${caption}. Open in the Cockpit`}>{body}</button>
                        ) : (
                          <div className="w7-nb">{body}</div>
                        )}
                        {steps.length > 0 ? (
                          <ul className="lc-opts" aria-label={`Optional steps in ${name}`}>
                            {steps.map((n) => {
                              const stepTarget = STEP_TARGET[n];
                              return (
                                <li key={n}>
                                  {stepTarget && !narrow ? (
                                    <button type="button" className="lc-opt" title={stepDef(n).caption} onClick={() => tour.go(stepTarget)}>{stepDef(n).label}</button>
                                  ) : (
                                    <span className="lc-opt" title={stepDef(n).caption}>{stepDef(n).label}</span>
                                  )}
                                </li>
                              );
                            })}
                          </ul>
                        ) : null}
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
          <li><span aria-hidden="true" className="w7-dot opt" />Optional: switch it off in Settings, when a task starts, or at the handoff</li>
        </ul>
      </div>
    </section>
  );
}
