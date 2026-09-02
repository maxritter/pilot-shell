import { useRef, useState, type KeyboardEvent } from "react";
import { Check } from "lucide-react";
import ImageModal from "@/components/ImageModal";

interface ConsoleSlide {
  label: string;
  name: string;
  alt: string;
  desc: string;
}

const consoleSlides: ConsoleSlide[] = [
  {
    label: "Dashboard",
    name: "dashboard",
    alt: "Console Dashboard - stats, recent specifications, sessions, requirements, memories",
    desc: "See active work, recent sessions, requirements, specifications, and memories at a glance.",
  },
  {
    label: "Sessions",
    name: "sessions",
    alt: "Sessions view — browse, search, and resume past sessions",
    desc: "Browse and search Claude Code and Codex sessions. Resume actions appear only where the agent supports them.",
  },
  {
    label: "Memories",
    name: "memories",
    alt: "Memories view — captured decisions and patterns with semantic search",
    desc: "Search captured decisions, discoveries, and patterns, then follow each memory back to its source session.",
  },
  {
    label: "Extensions",
    name: "extensions",
    alt: "Extensions view — local, plugin, and remote extensions with team sharing",
    desc: "Browse and manage extensions across global, project, plugin, and remote scopes.",
  },
  {
    label: "Requirements",
    name: "requirements",
    alt: "Requirements view — PRD brainstorming, research tiers, and requirement tracking",
    desc: "Shape unclear product ideas into requirements and track the evidence behind them.",
  },
  {
    label: "Specifications",
    name: "specifications",
    alt: "Specification view — plan annotation, task progress, and phase tracking",
    desc: "Review specifications, task progress, phase history, and plan annotations.",
  },
  {
    label: "Changes",
    name: "changes",
    alt: "Changes view — git diff, staged files, code review annotations",
    desc: "Inspect changes with branch and worktree context, including inline review annotations.",
  },
  {
    label: "Usage",
    name: "usage",
    alt: "Usage view — daily costs, cost-by-model breakdown, and usage trends",
    desc: "Review token usage and trends using the data each agent makes available.",
  },
  {
    label: "Settings",
    name: "settings",
    alt: "Settings view — spec and build workflows, and the console port",
    desc: "Configure Pilot's workflows, automation, and Console.",
  },
  {
    label: "Documentation",
    name: "documentation",
    alt: "Documentation view — embedded documentation and quick-start guides",
    desc: "Read the technical reference without leaving the local Console.",
  },
];

const SLIDE_W = 2742;
const SLIDE_H = 1994;

/* The shot spans the full 1280px container, so a 1400px source is soft on a
 * HiDPI screen. Offer both variants and let the browser pick by density. */
const SLIDE_SIZES =
  "(max-width: 768px) calc(100vw - 80px), (max-width: 1328px) calc(100vw - 96px), 1184px";

const ConsoleSection = () => {
  const [index, setIndex] = useState(0);
  const [tick, setTick] = useState(0);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const slide = consoleSlides[index];

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
        nextIndex = (currentIndex + 1) % consoleSlides.length;
        break;
      case "ArrowLeft":
      case "ArrowUp":
        nextIndex = (currentIndex - 1 + consoleSlides.length) % consoleSlides.length;
        break;
      case "Home":
        nextIndex = 0;
        break;
      case "End":
        nextIndex = consoleSlides.length - 1;
        break;
      default:
        return;
    }
    event.preventDefault();
    select(nextIndex);
    tabRefs.current[nextIndex]?.focus();
  };

  return (
    <section className="ps-sec" id="console" aria-labelledby="console-heading">
      <div className="ps-ctr">
        <div className="ps-sec-hd ps-rv">
          <p className="ps-eyebrow">The human control plane</p>
          <h2 className="ps-h2" id="console-heading">
            Pilot Shell Console
          </h2>
          <p className="ps-lead">
            The local Console at <span className="ps-mono">localhost:41777</span>{" "}
            makes the harness visible and steerable — glanced at between agent
            turns, beside the terminal.
          </p>
        </div>

        <div className="ps-con ps-rv ps-rv-z">
          <div
            className={`ps-shot ${tick % 2 ? "ps-fb" : "ps-fa"}`}
            id="console-panel"
            role="tabpanel"
            aria-labelledby={`console-tab-${slide.name}`}
            tabIndex={0}
          >
            <ImageModal
              src={`/console/${slide.name}.webp`}
              inlineSrc={`/console/${slide.name}_sm.webp`}
              inlineSrcSet={`/console/${slide.name}_sm.webp 1400w, /console/${slide.name}.webp ${SLIDE_W}w`}
              sizes={SLIDE_SIZES}
              alt={slide.alt}
              className="ps-shot-img"
              width={SLIDE_W}
              height={SLIDE_H}
            />
            <p className="ps-cap">
              <span className="ps-strong">{slide.label}</span>
              {" — "}
              {slide.desc}
            </p>
          </div>

          <div className="ps-thumbs" role="tablist" aria-label="Console screenshots">
            {consoleSlides.map((s, i) => (
              <button
                key={s.name}
                ref={(node) => {
                  tabRefs.current[i] = node;
                }}
                id={`console-tab-${s.name}`}
                type="button"
                role="tab"
                className="ps-thumb"
                aria-label={`Show ${s.label} screenshot`}
                aria-selected={i === index}
                aria-controls="console-panel"
                tabIndex={i === index ? 0 : -1}
                onClick={() => select(i)}
                onKeyDown={(event) => handleTabKeyDown(event, i)}
              >
                <img
                  className="ps-thumb-img"
                  src={`/console/thumbs/${s.name}.webp`}
                  alt=""
                  loading="lazy"
                  decoding="async"
                  width={120}
                  height={87}
                />
                <span className="ps-thumb-t">
                  {s.label}
                  <Check className="h-3.5 w-3.5 ps-chk" aria-hidden="true" />
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default ConsoleSection;
