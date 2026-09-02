import { useRef, useState, type KeyboardEvent } from "react";
import {
  Brain,
  Check,
  Eye,
  FileText,
  Layers,
  Monitor,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";

interface Layer {
  icon: LucideIcon;
  name: string;
  short: string;
  desc: string;
  mechs: string[];
  refuses: string;
  gives: string;
}

const layers: Layer[] = [
  {
    icon: Layers,
    name: "Context Engineering",
    short: "Only what is relevant loads, at the stage where it matters.",
    desc: "Relevant source, architecture, project standards, prior decisions, specialized agents, and MCP tools arrive at the stage where they matter — modular, only what's relevant loads.",
    mechs: ["Semble", "CodeGraph", "rules by file type", "RTK", "7 MCP servers"],
    refuses:
      "Reconstructing your codebase from memory. The agent reads the named source instead.",
    gives: "A lean context window — with 60–90% of tool-output tokens compressed away.",
  },
  {
    icon: FileText,
    name: "Spec-Driven Delivery",
    short: "Exploration and planning come before code, against a plan you approved.",
    desc: "Exploration and planning come before code. Behavior changes move through RED → GREEN → REFACTOR, against a plan you reviewed and approved.",
    mechs: ["/prd", "/spec", "/build", "/fix", "TDD"],
    refuses:
      "Code before a plan. /spec implements nothing until the ordered task list is approved.",
    gives:
      "Requirements, plans, and tasks as durable files under docs/ — reviewable, diffable, shareable.",
  },
  {
    icon: ShieldCheck,
    name: "Enforced Quality Gates",
    short: "Lint, type checks, and tests run as hooks on every edit.",
    desc: "Lint, type checks, and tests run as hooks on every edit. Stop guards refuse a completion claim without fresh evidence.",
    mechs: ["lifecycle hooks", "file checker", "stop guards"],
    refuses:
      "Completion claims without evidence. A session cannot end while verification obligations are still open.",
    gives: "Every edit checked at write time — not in a review three days later.",
  },
  {
    icon: Eye,
    name: "Independent Verification",
    short: "Reviews, full gates, and browser proof stand between code and handoff.",
    desc: "Independent reviews, full test and build gates, and browser or device verification stand between implementation and handoff.",
    mechs: ["review agents", "E2E", "agent-browser", "Chrome DevTools MCP"],
    refuses:
      "Grading its own work. An independent reviewer judges the diff against the approved plan.",
    gives: "Runtime proof the finished system works, recorded as evidence.",
  },
  {
    icon: Brain,
    name: "Stateful Delivery & Memory",
    short: "Plans, progress, and evidence survive compaction and travel with the repo.",
    desc: "Requirements, specs, tasks, progress, and verification evidence survive compaction and session boundaries — and travel through the repo to your team.",
    mechs: ["durable docs/", "compaction snapshots", "team memories"],
    refuses:
      "Losing the plan mid-session. Compaction and restarts restore the active plan and its obligations.",
    gives:
      "The same standard across sessions, projects, and teammates — no cloud, you review the diff and commit.",
  },
  {
    icon: Monitor,
    name: "Human Control Plane",
    short: "The Console makes plan, diff, evidence, and usage legible in seconds.",
    desc: "The Console connects plan and diff review, annotations, progress, evidence, session recovery, and usage — glanced at between agent turns.",
    mechs: ["Console", "localhost:41777", "annotations"],
    refuses:
      "Running blind. What is active, what is blocked, and what needs you is legible in seconds.",
    gives: "Annotations on specs and diffs flow back into the active workflow.",
  },
];

const AnatomySection = () => {
  const [index, setIndex] = useState(0);
  const [tick, setTick] = useState(0);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const active = layers[index];

  const select = (next: number) => {
    if (next === index) return;
    setIndex(next);
    setTick((value) => value + 1);
  };

  const handleTabKeyDown = (
    event: KeyboardEvent<HTMLButtonElement>,
    currentIndex: number,
  ) => {
    let nextIndex: number;
    switch (event.key) {
      case "ArrowRight":
      case "ArrowDown":
        nextIndex = (currentIndex + 1) % layers.length;
        break;
      case "ArrowLeft":
      case "ArrowUp":
        nextIndex = (currentIndex - 1 + layers.length) % layers.length;
        break;
      case "Home":
        nextIndex = 0;
        break;
      case "End":
        nextIndex = layers.length - 1;
        break;
      default:
        return;
    }
    event.preventDefault();
    select(nextIndex);
    tabRefs.current[nextIndex]?.focus();
  };

  return (
    <section className="ps-sec" id="anatomy" aria-labelledby="anatomy-heading">
      <div className="ps-ctr">
        <div className="ps-sec-hd ps-left ps-rv">
          <p className="ps-eyebrow">Anatomy of the harness</p>
          <h2 className="ps-h2" id="anatomy-heading">
            Six layers of quality. Pick one apart.
          </h2>
          <p className="ps-lead">
            Each layer enforces something the previous can't. Rules and skills
            supply context inside these layers — the layers, together, are the
            product.
          </p>
        </div>

        <div className="ps-tabs ps-stg" role="tablist" aria-label="Harness layers">
          {layers.map((layer, i) => (
            <button
              key={layer.name}
              ref={(node) => {
                tabRefs.current[i] = node;
              }}
              id={`anatomy-tab-${i}`}
              type="button"
              role="tab"
              className="ps-tab"
              aria-selected={i === index}
              aria-controls="anatomy-panel"
              tabIndex={i === index ? 0 : -1}
              onClick={() => select(i)}
              onKeyDown={(event) => handleTabKeyDown(event, i)}
            >
              <span className="ps-tab-top">
                <span className="ps-tile">
                  <layer.icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <span className="ps-h3">{layer.name}</span>
                <Check className="h-[18px] w-[18px] ps-chk" aria-hidden="true" />
              </span>
              <span className="ps-tab-desc">{layer.short}</span>
            </button>
          ))}
        </div>

        <div
          className={`ps-pnl ${tick % 2 ? "ps-fb" : "ps-fa"}`}
          id="anatomy-panel"
          role="tabpanel"
          aria-labelledby={`anatomy-tab-${index}`}
        >
          <div>
            <p className="ps-lbl">Layer</p>
            <h3 className="ps-h3" style={{ marginTop: 8 }}>
              {active.name}
            </h3>
            <p className="ps-body" style={{ marginTop: 16 }}>
              {active.desc}
            </p>
            <div className="ps-chips">
              {active.mechs.map((mech) => (
                <span key={mech} className="ps-chip">
                  {mech}
                </span>
              ))}
            </div>
          </div>
          <div>
            <p className="ps-lbl">What it refuses</p>
            <p className="ps-body ps-strong" style={{ marginTop: 12 }}>
              {active.refuses}
            </p>
            <p className="ps-lbl" style={{ marginTop: 24 }}>
              What you get
            </p>
            <p className="ps-body" style={{ marginTop: 12 }}>
              {active.gives}
            </p>
          </div>
        </div>

        <p className="ps-sup ps-closing">
          One system for Claude Code and Codex — platform adapters preserve one
          engineering standard while the underlying models keep improving.
        </p>
      </div>
    </section>
  );
};

export default AnatomySection;
