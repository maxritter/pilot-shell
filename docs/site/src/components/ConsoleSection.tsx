import { useRef, useState, type KeyboardEvent } from "react";
import { useInView } from "@/hooks/use-in-view";
import ImageModal from "@/components/ImageModal";
import SectionHeader from "@/components/SectionHeader";

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

const SLIDE_W = 1920;
const SLIDE_H = 1396;

const ConsoleSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();
  const [index, setIndex] = useState(0);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const slide = consoleSlides[index];

  const handleTabKeyDown = (
    event: KeyboardEvent<HTMLButtonElement>,
    currentIndex: number,
  ) => {
    let nextIndex: number;

    switch (event.key) {
      case "ArrowRight":
        nextIndex = (currentIndex + 1) % consoleSlides.length;
        break;
      case "ArrowLeft":
        nextIndex =
          (currentIndex - 1 + consoleSlides.length) % consoleSlides.length;
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
    setIndex(nextIndex);
    tabRefs.current[nextIndex]?.focus();
  };

  return (
    <section
      id="console"
      aria-labelledby="console-heading"
      className="py-16 lg:py-24 px-4 sm:px-6 relative"
    >
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={ref}
          className={`${inView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <SectionHeader
            kicker="The human control plane"
            title="Pilot Shell Console"
            titleId="console-heading"
            lead={
              <>
                The local Console at{" "}
                <span className="font-mono text-sm sm:text-[15px]">
                  localhost:41777
                </span>{" "}
                makes the harness visible and steerable — glanced at between
                agent turns, beside the terminal.
              </>
            }
            className="mb-8"
          />

          <div className="max-w-4xl mx-auto">
            <div
              id={`console-panel-${slide.name}`}
              role="tabpanel"
              aria-labelledby={`console-tab-${slide.name}`}
              tabIndex={0}
              className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              <div
                className="rounded-xl overflow-hidden border border-border/50"
                style={{ aspectRatio: `${SLIDE_W} / ${SLIDE_H}` }}
              >
                <ImageModal
                  src={`/console/${slide.name}.webp`}
                  inlineSrc={`/console/${slide.name}_sm.webp`}
                  alt={slide.alt}
                  className="w-full h-auto rounded-xl"
                  width={SLIDE_W}
                  height={SLIDE_H}
                />
              </div>

              <div className="mt-3 text-center">
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">
                    {slide.label}
                  </span>
                  {" — "}
                  {slide.desc}
                </p>
              </div>
            </div>

            <div
              role="tablist"
              aria-label="Console screenshots"
              className="mt-4 flex gap-2 overflow-x-auto pb-2"
            >
              {consoleSlides.map((s, i) => (
                <button
                  key={s.name}
                  ref={(node) => {
                    tabRefs.current[i] = node;
                  }}
                  id={`console-tab-${s.name}`}
                  type="button"
                  role="tab"
                  onClick={() => setIndex(i)}
                  onKeyDown={(event) => handleTabKeyDown(event, i)}
                  aria-label={`Show ${s.label} screenshot`}
                  aria-selected={i === index}
                  aria-controls={`console-panel-${s.name}`}
                  tabIndex={i === index ? 0 : -1}
                  className={`group/thumb relative min-h-11 min-w-[5.75rem] shrink-0 overflow-hidden rounded-lg border-2 transition-[border-color,opacity] duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background sm:min-w-0 sm:flex-1
                    ${
                      i === index
                        ? "border-primary"
                        : "border-transparent opacity-60 hover:opacity-100 hover:border-border"
                    }`}
                >
                  <img
                    src={`/console/thumbs/${s.name}.webp`}
                    alt=""
                    className="w-full h-auto rounded-md"
                    loading="lazy"
                    decoding="async"
                    width={120}
                    height={87}
                  />
                  <div
                    className={`absolute inset-x-0 bottom-0 py-1 text-xs font-medium text-center
                    ${
                      i === index
                        ? "bg-primary/90 text-primary-foreground"
                        : "bg-background/80 text-muted-foreground group-hover/thumb:text-foreground"
                    }`}
                  >
                    {s.label}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ConsoleSection;
