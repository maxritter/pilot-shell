import { GithubIcon, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Logo from "@/components/Logo";

const HeroSection = () => {
  return (
    <section className="min-h-[70vh] flex flex-col items-center justify-center px-3 xs:px-4 sm:px-6 relative overflow-hidden pt-16 xs:pt-20 pb-4">

      <div className="relative z-10 text-center max-w-4xl mx-auto w-full">
        {/* Logo */}
        <div className="animate-fade-in-up flex justify-center my-2 xs:my-4 sm:my-6">
          <Logo variant="hero" />
        </div>

        {/* Subtitle */}
        <div className="animate-fade-in-up animation-delay-100 mb-6 xs:mb-8 px-1">
          <p className="text-foreground/90 text-xs xs:text-sm sm:text-base md:text-lg lg:text-xl font-medium max-w-[90%] xs:max-w-xl sm:max-w-2xl mx-auto leading-relaxed">
            Make Claude Code production-ready.
          </p>
          <p className="text-muted-foreground text-[11px] xs:text-xs sm:text-sm md:text-base max-w-[90%] xs:max-w-xl sm:max-w-2xl mx-auto mt-1.5 leading-relaxed">
            From requirement to production-grade code — planned, tested, verified.
          </p>
          <p className="text-muted-foreground/70 text-[10px] xs:text-xs sm:text-sm md:text-base max-w-[90%] xs:max-w-xl sm:max-w-2xl mx-auto mt-1.5 leading-relaxed">
            Spec-driven plans. Enforced quality gates. Persistent knowledge.
          </p>
        </div>

        {/* Feature highlights */}
        <div className="flex flex-wrap justify-center gap-3 xs:gap-4 sm:gap-6 mb-6 xs:mb-8 animate-fade-in-up animation-delay-400 px-2">
          <div className="text-center">
            <div className="text-lg xs:text-xl sm:text-2xl font-bold text-primary">
              Spec-Driven
            </div>
            <div className="text-[9px] xs:text-[10px] sm:text-xs text-muted-foreground">
              Plan → Build → Verify
            </div>
          </div>
          <div className="w-px h-8 bg-border/50 hidden xs:block" />
          <div className="text-center">
            <div className="text-lg xs:text-xl sm:text-2xl font-bold text-primary">
              TDD
            </div>
            <div className="text-[9px] xs:text-[10px] sm:text-xs text-muted-foreground">
              Test-First
            </div>
          </div>
          <div className="w-px h-8 bg-border/50 hidden xs:block" />
          <div className="text-center">
            <div className="text-lg xs:text-xl sm:text-2xl font-bold text-primary">
              Memory
            </div>
            <div className="text-[9px] xs:text-[10px] sm:text-xs text-muted-foreground">
              Persistent Context
            </div>
          </div>
          <div className="w-px h-8 bg-border/50 hidden xs:block" />
          <div className="text-center">
            <div className="text-lg xs:text-xl sm:text-2xl font-bold text-primary">
              Overlays
            </div>
            <div className="text-[9px] xs:text-[10px] sm:text-xs text-muted-foreground">
              Modify Defaults
            </div>
          </div>
          <div className="w-px h-8 bg-border/50 hidden xs:block" />
          <div className="text-center">
            <div className="text-lg xs:text-xl sm:text-2xl font-bold text-primary">
              Hooks
            </div>
            <div className="text-[9px] xs:text-[10px] sm:text-xs text-muted-foreground">
              Quality Gates
            </div>
          </div>
        </div>

        {/* Feature badges */}
        <div className="flex flex-wrap justify-center gap-1.5 xs:gap-2 mb-6 xs:mb-8 animate-fade-in-up animation-delay-400 px-2">
          <Badge variant="secondary" className="text-[10px] xs:text-xs">
            Worktree Support
          </Badge>
          <Badge variant="secondary" className="text-[10px] xs:text-xs">
            MCP Servers
          </Badge>
          <Badge variant="secondary" className="text-[10px] xs:text-xs">
            LSP Servers
          </Badge>
          <Badge variant="secondary" className="text-[10px] xs:text-xs">
            Semantic Search
          </Badge>
          <Badge variant="secondary" className="text-[10px] xs:text-xs">
            Pilot Bot
          </Badge>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4 animate-fade-in-up animation-delay-500 px-2">
          <Button
            size="lg"
            asChild
            className="w-full sm:w-auto text-sm xs:text-base"
          >
            <a
              href="https://github.com/maxritter/pilot-shell"
              target="_blank"
              rel="noopener noreferrer"
            >
              <GithubIcon className="mr-1.5 xs:mr-2 h-3.5 w-3.5 xs:h-4 xs:w-4" />
              View on GitHub
            </a>
          </Button>
          <Button
            variant="outline"
            size="lg"
            asChild
            className="w-full sm:w-auto text-sm xs:text-base"
          >
            <a href="/docs/">
              <BookOpen className="mr-1.5 xs:mr-2 h-3.5 w-3.5 xs:h-4 xs:w-4" />
              Read Documentation
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
