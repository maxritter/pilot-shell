import { Brain, GitBranch, ShieldCheck, type LucideIcon } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const teamPoints: Array<{ icon: LucideIcon; title: string; desc: string }> = [
  {
    icon: Brain,
    title: "Team memories",
    desc: "decisions, discoveries, and bugfixes persist across sessions and travel through the project repo to the whole team.",
  },
  {
    icon: GitBranch,
    title: "Extension sharing",
    desc: "skills, rules, commands, and agents move between machines and teammates with git push and pull, managed in the Console.",
  },
  {
    icon: ShieldCheck,
    title: "One standard for everyone",
    desc: "the same plans, gates, and verification hold across sessions, projects, and teammates.",
  },
];

/* Fixed terminal palette — a terminal stays dark in both site themes. */
const term = {
  bg: "bg-[hsl(217,42%,5%)]",
  chrome: "bg-[hsl(217,35%,7.5%)]",
  border: "border-[hsl(217,18%,18%)]",
  fg: "text-[hsl(0,0%,98%)]",
  muted: "text-[hsl(217,10%,65%)]",
  faint: "text-[hsl(217,10%,48%)]",
  blue: "text-[hsl(209,72%,63%)]",
  green: "text-[hsl(160,60%,55%)]",
};

const GitTerminalMock = () => (
  <div className={`${term.bg} border ${term.border} rounded-xl overflow-hidden`} aria-hidden="true">
    <div className={`flex items-center px-3.5 py-2.5 border-b ${term.border} ${term.chrome}`}>
      <div className="flex items-center gap-[7px]">
        <span className="w-[11px] h-[11px] rounded-full bg-[hsl(0,60%,55%)]" />
        <span className="w-[11px] h-[11px] rounded-full bg-[hsl(40,80%,55%)]" />
        <span className="w-[11px] h-[11px] rounded-full bg-[hsl(140,50%,45%)]" />
      </div>
      <span className={`flex-1 text-center font-mono text-[11px] font-medium ${term.muted}`}>
        zsh — api-service
      </span>
    </div>
    <div className={`flex flex-col gap-2.5 p-4 sm:p-5 font-mono text-[11px] sm:text-[12.5px] leading-relaxed ${term.muted}`}>
      <div>
        <span className={`font-semibold ${term.blue}`}>$</span>{" "}
        <span className={term.fg}>git diff --stat</span>
      </div>
      <div className="pl-4">
        docs/memories/payment-provider.md <span className={term.green}>+12</span>
      </div>
      <div className="pl-4">
        docs/memories/rate-limit-design.md <span className={term.green}>+18</span>
      </div>
      <div className="pl-4">
        docs/specs/rate-limiting/plan.md <span className={term.green}>+64</span>
      </div>
      <div className={`pl-4 ${term.faint}`}>3 files changed, 94 insertions(+)</div>
      <div className="mt-1">
        <span className={`font-semibold ${term.blue}`}>$</span>{" "}
        <span className={term.fg}>git commit -m "memories + approved spec"</span>
      </div>
      <div className={`pl-4 ${term.faint}`}>
        teammates load this context at their next session start
      </div>
    </div>
  </div>
);

const TeamSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="team"
      aria-labelledby="team-heading"
      className="scroll-mt-24 py-16 lg:py-24 px-4 sm:px-6 relative"
    >
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={ref}
          className={`grid lg:grid-cols-2 gap-9 lg:gap-14 items-center ${
            inView ? "animate-fade-in-up" : "opacity-0"
          }`}
        >
          <div>
            <div className="font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-primary mb-3">
              Built for teams
            </div>
            <h2
              id="team-heading"
              className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground"
            >
              Share the why, not just the code.
            </h2>
            <p className="text-[15px] leading-relaxed text-muted-foreground mt-3.5">
              Pilot stores a project's captured decisions and discoveries in
              the repo itself, so git carries them to every contributor.
              Teammates' context loads at session start on Claude Code and
              Codex — no cloud, no clock, you review the diff and commit.
            </p>
            <div className="flex flex-col gap-4 mt-6">
              {teamPoints.map((point) => (
                <div key={point.title} className="flex gap-3 items-start">
                  <point.icon
                    className="h-[17px] w-[17px] text-primary flex-none mt-0.5"
                    aria-hidden="true"
                  />
                  <p className="text-[13.5px] leading-relaxed text-muted-foreground">
                    <span className="text-foreground font-medium">
                      {point.title}
                    </span>{" "}
                    — {point.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
          <GitTerminalMock />
        </div>
      </div>
    </section>
  );
};

export default TeamSection;
