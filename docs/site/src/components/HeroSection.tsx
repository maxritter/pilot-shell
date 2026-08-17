import { GithubIcon, BookOpen, Newspaper } from "lucide-react";
import { Button } from "@/components/ui/button";
import Logo from "@/components/Logo";

const HeroSection = () => {
  return (
    <section className="min-h-[70vh] flex flex-col items-center justify-center px-4 sm:px-6 relative overflow-hidden pt-14 xs:pt-16 sm:pt-20 pb-6">
      <div className="relative z-10 text-center max-w-4xl mx-auto w-full">
        {/* Logo */}
        <div className="animate-fade-in-up flex justify-center mb-4 xs:mb-5 sm:mb-6">
          <Logo variant="hero" />
        </div>

        {/* Slogan + descriptions */}
        <div className="animate-fade-in-up animation-delay-100 mb-6 xs:mb-7 sm:mb-9">
          <h1 className="text-foreground text-xl xs:text-2xl sm:text-3xl md:text-4xl font-semibold tracking-tight leading-tight max-w-4xl mx-auto sm:whitespace-nowrap">
            How real engineers run Claude Code and Codex
          </h1>
          <p className="text-muted-foreground text-sm xs:text-base sm:text-lg md:text-xl mt-3 xs:mt-4 max-w-2xl mx-auto leading-relaxed">
            From requirement to production-grade code: planned, tested,
            verified.
          </p>
          <p className="text-muted-foreground text-xs xs:text-sm sm:text-base mt-2 max-w-2xl mx-auto">
            Spec-driven plans. Enforced quality gates. Persistent knowledge.
          </p>
        </div>

        {/* CTA Buttons — stack on tiny screens, row from xs (475px+) */}
        <div className="flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center justify-center gap-2 sm:gap-3 animate-fade-in-up animation-delay-500 max-w-md sm:max-w-none mx-auto">
          <Button
            asChild
            className="h-11 px-5 text-sm sm:text-base sm:px-6 w-full sm:w-auto"
          >
            <a
              href="https://github.com/maxritter/pilot-shell"
              target="_blank"
              rel="noopener noreferrer"
            >
              <GithubIcon className="mr-2 h-4 w-4" />
              View on GitHub
            </a>
          </Button>
          <Button
            variant="outline"
            asChild
            className="h-11 px-5 text-sm sm:text-base sm:px-6 w-full sm:w-auto"
          >
            <a href="/blog">
              <Newspaper className="mr-2 h-4 w-4" />
              Blog
            </a>
          </Button>
          <Button
            variant="outline"
            asChild
            className="h-11 px-5 text-sm sm:text-base sm:px-6 w-full sm:w-auto"
          >
            <a href="/docs">
              <BookOpen className="mr-2 h-4 w-4" />
              Documentation
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
