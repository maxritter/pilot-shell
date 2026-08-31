import { useRef, useState, type KeyboardEvent } from "react";
import { useInView } from "@/hooks/use-in-view";
import SectionHeader from "@/components/SectionHeader";

interface Layer {
  num: string;
  name: string;
  desc: string;
  mechs: string[];
  refuses: string;
  gives: string;
}

const layers: Layer[] = [
  {
    num: "01",
    name: "Context Engineering",
    desc: "Relevant source, architecture, project standards, prior decisions, specialized agents, and MCP tools arrive at the stage where they matter — modular, only what's relevant loads.",
    mechs: ["Semble", "CodeGraph", "rules by file type", "RTK", "7 MCP servers"],
    refuses:
      "Reconstructing your codebase from memory. The agent reads the named source instead.",
    gives: "A lean context window — with 60–90% of tool-output tokens compressed away.",
  },
  {
    num: "02",
    name: "Spec-Driven Delivery",
    desc: "Exploration and planning come before code. Behavior changes move through RED → GREEN → REFACTOR, against a plan you reviewed and approved.",
    mechs: ["/prd", "/spec", "/build", "/fix", "TDD"],
    refuses:
      "Code before a plan. /spec implements nothing until the ordered task list is approved.",
    gives:
      "Requirements, plans, and tasks as durable files under docs/ — reviewable, diffable, shareable.",
  },
  {
    num: "03",
    name: "Enforced Quality Gates",
    desc: "Lint, type checks, and tests run as hooks on every edit. Stop guards refuse a completion claim without fresh evidence.",
    mechs: ["lifecycle hooks", "file checker", "stop guards"],
    refuses:
      "Completion claims without evidence. A session cannot end while verification obligations are still open.",
    gives: "Every edit checked at write time — not in a review three days later.",
  },
  {
    num: "04",
    name: "Independent Verification",
    desc: "Independent reviews, full test and build gates, and browser or device verification stand between implementation and handoff.",
    mechs: ["review agents", "E2E", "agent-browser", "Chrome DevTools MCP"],
    refuses:
      "Grading its own work. An independent reviewer judges the diff against the approved plan.",
    gives: "Runtime proof the finished system works, recorded as evidence.",
  },
  {
    num: "05",
    name: "Stateful Delivery & Memory",
    desc: "Requirements, specs, tasks, progress, and verification evidence survive compaction and session boundaries — and travel through the repo to your team.",
    mechs: ["durable docs/", "compaction snapshots", "team memories"],
    refuses:
      "Losing the plan mid-session. Compaction and restarts restore the active plan and its obligations.",
    gives:
      "The same standard across sessions, projects, and teammates — no cloud, you review the diff and commit.",
  },
  {
    num: "06",
    name: "Human Control Plane",
    desc: "The Console connects plan and diff review, annotations, progress, evidence, session recovery, and usage — glanced at between agent turns.",
    mechs: ["Console", "localhost:41777", "annotations"],
    refuses:
      "Running blind. What is active, what is blocked, and what needs you is legible in seconds.",
    gives: "Annotations on specs and diffs flow back into the active workflow.",
  },
];

const AnatomySection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();
  const [index, setIndex] = useState(0);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const active = layers[index];

  const handleTabKeyDown = (
    event: KeyboardEvent<HTMLButtonElement>,
    currentIndex: number,
  ) => {
    let nextIndex: number;
    switch (event.key) {
      case "ArrowRight":
        nextIndex = (currentIndex + 1) % layers.length;
        break;
      case "ArrowLeft":
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
    setIndex(nextIndex);
    tabRefs.current[nextIndex]?.focus();
  };

  return (
    <section
      id="anatomy"
      aria-labelledby="anatomy-heading"
      className="scroll-mt-24 py-16 lg:py-24 px-4 sm:px-6 relative"
    >
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div ref={ref} className={inView ? "animate-fade-in-up" : "opacity-0"}>
          <SectionHeader
            kicker="Anatomy of the harness"
            title="Six layers of quality. Pick one apart."
            titleId="anatomy-heading"
            lead="Each layer enforces something the previous can't. Rules and skills supply context inside these layers — the layers, together, are the product."
            className="mb-8"
          />

          <div
            role="tablist"
            aria-label="Harness layers"
            className="flex flex-wrap justify-start sm:justify-center gap-2 mb-5"
          >
            {layers.map((layer, i) => (
              <button
                key={layer.num}
                ref={(node) => {
                  tabRefs.current[i] = node;
                }}
                id={`anatomy-tab-${layer.num}`}
                type="button"
                role="tab"
                onClick={() => setIndex(i)}
                onKeyDown={(event) => handleTabKeyDown(event, i)}
                aria-selected={i === index}
                aria-controls="anatomy-panel"
                tabIndex={i === index ? 0 : -1}
                className={`flex items-center gap-1.5 rounded-lg border px-3 py-2 text-[12.5px] font-medium transition-all duration-200 cursor-pointer
                  ${
                    i === index
                      ? "border-primary/50 bg-primary/10 text-primary"
                      : "border-border/60 bg-card text-muted-foreground hover:text-foreground"
                  }`}
              >
                <span className="font-mono text-[10px] font-semibold opacity-75">
                  {layer.num}
                </span>
                <span>{layer.name}</span>
              </button>
            ))}
          </div>

          <div className="relative overflow-hidden rounded-lg border border-primary/30 bg-card">
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary to-transparent" />
            <div
              id="anatomy-panel"
              role="tabpanel"
              aria-labelledby={`anatomy-tab-${active.num}`}
              className="grid md:grid-cols-2 gap-6 md:gap-9 p-5 sm:p-8 md:min-h-[230px]"
            >
              <div>
                <div className="font-mono text-xs font-semibold text-primary">
                  LAYER {active.num}
                </div>
                <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground mt-2">
                  {active.name}
                </h3>
                <p className="text-sm leading-relaxed text-muted-foreground mt-3">
                  {active.desc}
                </p>
                <div className="flex flex-wrap gap-1.5 mt-4">
                  {active.mechs.map((mech) => (
                    <span
                      key={mech}
                      className="font-mono text-[11px] font-medium text-primary bg-primary/10 px-2 py-[3px] rounded"
                    >
                      {mech}
                    </span>
                  ))}
                </div>
              </div>
              <div className="border-t md:border-t-0 md:border-l border-border/60 pt-5 md:pt-0 md:pl-9">
                <div className="font-mono text-[10.5px] font-semibold uppercase tracking-[0.1em] text-muted-foreground">
                  What it refuses
                </div>
                <p className="text-sm leading-relaxed text-foreground mt-2.5">
                  {active.refuses}
                </p>
                <div className="font-mono text-[10.5px] font-semibold uppercase tracking-[0.1em] text-muted-foreground mt-5">
                  What you get
                </div>
                <p className="text-sm leading-relaxed text-muted-foreground mt-2.5">
                  {active.gives}
                </p>
              </div>
            </div>
          </div>

          <p className="text-center text-[13px] leading-relaxed text-muted-foreground max-w-2xl mx-auto mt-5">
            One system for Claude Code and Codex — platform adapters preserve
            one engineering standard while the underlying models keep
            improving.
          </p>
        </div>
      </div>
    </section>
  );
};

export default AnatomySection;
