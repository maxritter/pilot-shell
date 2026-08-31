import { GithubIcon, BookOpen, Newspaper, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import CodeBlock from "@/components/CodeBlock";
import IconTile from "@/components/IconTile";

const INSTALL_COMMAND =
  "curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash";

/* Fixed terminal palette — a terminal stays dark in both site themes. */
const term = {
  bg: "bg-[hsl(217,42%,5%)]",
  chrome: "bg-[hsl(217,35%,7.5%)]",
  border: "border-[hsl(217,18%,18%)]",
  fg: "text-[hsl(0,0%,98%)]",
  muted: "text-[hsl(217,10%,65%)]",
  faint: "text-[hsl(217,10%,45%)]",
  blue: "text-[hsl(209,72%,63%)]",
  green: "text-[hsl(160,60%,55%)]",
  red: "text-[hsl(0,84%,70%)]",
  amber: "text-[hsl(38,92%,60%)]",
};

const TerminalMock = () => (
  <div
    className={`${term.bg} border ${term.border} rounded-xl overflow-hidden shadow-[0_32px_80px_hsl(217,40%,2%,0.6)]`}
    aria-hidden="true"
  >
    <div className={`flex items-center px-3.5 py-2.5 border-b ${term.border} ${term.chrome}`}>
      <div className="flex items-center gap-[7px]">
        <span className="w-[11px] h-[11px] rounded-full bg-[hsl(0,60%,55%)]" />
        <span className="w-[11px] h-[11px] rounded-full bg-[hsl(40,80%,55%)]" />
        <span className="w-[11px] h-[11px] rounded-full bg-[hsl(140,50%,45%)]" />
      </div>
      <span className={`flex-1 text-center font-mono text-[11px] font-medium ${term.muted}`}>
        claude — api-service
      </span>
      <span className={`font-mono text-[10px] font-medium ${term.faint}`}>80×24</span>
    </div>
    <div className={`flex flex-col gap-2.5 px-4 sm:px-5 pt-5 pb-4 font-mono text-[11px] sm:text-[12.5px] leading-relaxed ${term.muted}`}>
      <div className="flex gap-2.5">
        <span className={`flex-none w-3.5 font-semibold ${term.blue}`}>&gt;</span>
        <span className={`font-medium ${term.fg}`}>/spec add rate limiting to the public API</span>
      </div>
      <div className="flex gap-2.5">
        <span className={`flex-none w-3.5 ${term.faint}`}>⋯</span>
        <span>
          exploring codebase{" "}
          <span className={term.faint}>— Semble ×6 · CodeGraph ×2 · 3 memories recalled</span>
        </span>
      </div>
      <div className="flex gap-2.5">
        <span className={`flex-none w-3.5 ${term.green}`}>✓</span>
        <span className="text-[hsl(0,0%,98%,0.85)]">
          plan written — 4 tasks <span className={term.faint}>· approved by you</span>
        </span>
      </div>
      <div className="flex gap-2.5">
        <span className={`flex-none w-3.5 ${term.red}`}>✗</span>
        <span>
          <span className={term.red}>RED</span> test_rate_limit_returns_429{" "}
          <span className={term.faint}>· fails, as expected</span>
        </span>
      </div>
      <div className="flex gap-2.5">
        <span className={`flex-none w-3.5 ${term.green}`}>✓</span>
        <span>
          <span className={term.green}>GREEN</span>{" "}
          <span className={term.faint}>· ruff · basedpyright · 218 tests passed</span>
        </span>
      </div>
      <div className="flex gap-2.5">
        <span className={`flex-none w-3.5 ${term.amber}`}>■</span>
        <span className={term.amber}>
          stop guard{" "}
          <span className={term.muted}>— completion blocked, E2E evidence missing</span>
        </span>
      </div>
      <div className="flex gap-2.5">
        <span className={`flex-none w-3.5 ${term.green}`}>✓</span>
        <span className="text-[hsl(0,0%,98%,0.85)]">
          verified in browser — evidence saved to Console
        </span>
      </div>
      <div className="flex gap-2.5 items-center">
        <span className={`flex-none w-3.5 font-semibold ${term.blue}`}>&gt;</span>
        <span className="inline-block w-2 h-[15px] rounded-[1px] bg-[hsl(209,72%,63%)]" />
      </div>
    </div>
    <div className={`flex items-center justify-between px-4 py-2 border-t ${term.border} ${term.chrome} font-mono text-[10.5px] font-medium ${term.muted}`}>
      <span>
        <span className={term.blue}>Pilot Shell</span> · opusplan · ctx 34% · git:main
      </span>
    </div>
  </div>
);

const HeroSection = () => {
  return (
    <section className="px-4 sm:px-6 pt-28 sm:pt-32 pb-16 lg:pb-20">
      <div className="max-w-6xl mx-auto grid lg:grid-cols-[0.92fr_1.08fr] gap-10 lg:gap-14 items-center">
        <div className="animate-fade-in-up min-w-0 max-w-2xl mx-auto lg:mx-0 w-full">
          <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-primary mb-4">
            How real engineers run Claude Code and Codex
          </p>
          <h1 className="text-3xl sm:text-4xl lg:text-[44px] font-bold tracking-tight leading-[1.12] text-foreground">
            From requirement to production-grade code —{" "}
            <span className="text-primary">planned, tested, verified.</span>
          </h1>
          <p className="text-muted-foreground text-[15px] sm:text-base leading-relaxed mt-5 max-w-lg">
            Pilot Shell is a professional context and harness engineering
            system for Claude Code and Codex. It coordinates the complete
            engineering process around the model — with quality enforced on
            every layer.
          </p>
          <div className="flex flex-wrap gap-2.5 sm:gap-3 mt-7">
            <Button asChild size="lg" className="flex-1 sm:flex-none min-w-[140px]">
              <a
                href="https://github.com/maxritter/pilot-shell"
                target="_blank"
                rel="noopener noreferrer"
              >
                <GithubIcon className="mr-2 h-4 w-4" />
                View on GitHub
              </a>
            </Button>
            <Button asChild size="lg" variant="outline" className="flex-1 sm:flex-none min-w-[110px]">
              <a href="/docs">
                <BookOpen className="mr-2 h-4 w-4" />
                Docs
              </a>
            </Button>
            <Button asChild size="lg" variant="outline" className="flex-1 sm:flex-none min-w-[110px]">
              <a href="/blog">
                <Newspaper className="mr-2 h-4 w-4" />
                Blog
              </a>
            </Button>
          </div>
          <div className="mt-6 max-w-xl">
            <CodeBlock command={INSTALL_COMMAND} label="install command" />
            <p className="text-xs text-muted-foreground mt-2.5">
              macOS · Linux · Windows (WSL2) — installs in under 2 minutes.
              Works with any existing project.
            </p>
          </div>
        </div>

        <div className="animate-fade-in-up animation-delay-200 relative min-w-0 lg:pb-8 max-w-2xl mx-auto lg:mx-0 w-full">
          <TerminalMock />
          <div className="static lg:absolute lg:-right-2 lg:bottom-0 mt-3 lg:mt-0 w-full lg:w-auto flex gap-3 items-center bg-card border border-primary/35 rounded-[10px] py-3 pl-3.5 pr-4 shadow-[0_18px_44px_hsl(217,40%,2%,0.55)]">
            <IconTile icon={Bell} sizeClass="w-9 h-9" iconClass="h-[18px] w-[18px]" />
            <div>
              <div className="text-[12.5px] font-semibold text-foreground">
                Verification complete
              </div>
              <div className="font-mono text-[11px] text-muted-foreground mt-0.5">
                evidence saved — Console · localhost:41777
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
