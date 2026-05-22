import { useState } from "react";
import { useInView } from "@/hooks/use-in-view";
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
    alt: "Console Dashboard — stats, recent specifications, sessions, requirements, memories",
    desc: "Global command center with 8 clickable stat cards and 4 recent cards (Specifications, Requirements, Sessions, Memories) with quick navigation. Active specs as pills in the top bar, notification bell in top right.",
  },
  {
    label: "Sessions",
    name: "sessions",
    alt: "Sessions view — browse, search, and resume past sessions",
    desc: "Browse and search past sessions. Copy the Claude Code session ID and use /resume to jump back into any session instantly.",
  },
  {
    label: "Memories",
    name: "memories",
    alt: "Memories view — captured decisions and patterns with semantic search",
    desc: "Decisions, discoveries, and patterns captured automatically. Each memory links to its session — click to navigate. Semantic search across all memories.",
  },
  {
    label: "Extensions",
    name: "extensions",
    alt: "Extensions view — local, plugin, and remote extensions with team sharing",
    desc: "Browse, edit, and share extensions across global, project, plugin, and remote scopes. Team sharing via git with push, pull, and diff.",
  },
  {
    label: "Requirements",
    name: "requirements",
    alt: "Requirements view — PRD brainstorming, research tiers, and requirement tracking",
    desc: "Brainstorm vague ideas into Product Requirements Documents through back-and-forth conversation. Tiered deep research, requirement tracking, and team sharing.",
  },
  {
    label: "Specifications",
    name: "specifications",
    alt: "Specification view — plan annotation, task progress, and phase tracking",
    desc: "All spec plans with task progress, phase tracking, and iteration history. Annotate mode lets you mark up plans visually — select any text and write a note.",
  },
  {
    label: "Changes",
    name: "changes",
    alt: "Changes view — git diff, staged files, code review annotations",
    desc: "Git changes, staged files, and diff viewer with branch and worktree context. Review mode adds inline annotations on diff lines.",
  },
  {
    label: "Usage",
    name: "usage",
    alt: "Usage view — daily costs, cost-by-model breakdown, and usage trends",
    desc: "Daily token costs, cost-by-model breakdown, and usage trends over time.",
  },
  {
    label: "Settings",
    name: "settings",
    alt: "Settings view — spec workflow and console port",
    desc: "Spec workflow toggles (branch isolation, ask questions, plan approval, Model Switching) and reviewer configuration. Active model is set via `/model` — no model dropdowns here.",
  },
  {
    label: "Help",
    name: "help",
    alt: "Help view — embedded documentation and quick-start guides",
    desc: "Embedded documentation from pilot-shell.com — full technical reference without leaving the Console.",
  },
];

const SLIDE_W = 1920;
const SLIDE_H = 1396;

const ConsoleSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();
  const [index, setIndex] = useState(0);
  const slide = consoleSlides[index];

  return (
    <section id="console" className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={ref}
          className={`${inView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
              Pilot Shell Console
            </h2>
            <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
              Real-time notifications, session management, usage analytics, and
              semantic search.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            {/* Main image */}
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

            {/* Active view description */}
            <div className="mt-3 text-center">
              <p className="text-sm text-muted-foreground transition-all duration-200">
                <span className="font-medium text-foreground">
                  {slide.label}
                </span>
                {" — "}
                {slide.desc}
              </p>
            </div>

            {/* Thumbnail strip — 10 tabs */}
            <div className="grid grid-cols-10 gap-1.5 sm:gap-2 mt-3">
              {consoleSlides.map((s, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setIndex(i)}
                  aria-label={`Show ${s.label} screenshot`}
                  aria-pressed={i === index}
                  className={`group/thumb relative rounded-lg overflow-hidden border-2 transition-all duration-200
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
                    className={`absolute inset-x-0 bottom-0 py-0.5 text-[8px] sm:text-[10px] font-medium text-center
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
