import { Github } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useInView } from "@/hooks/use-in-view";

const DemoSection = () => {
  const [headerRef, headerInView] = useInView<HTMLDivElement>();

  return (
    <section id="demo" className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={headerRef}
          className={`text-center ${headerInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
            See It In Action
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto mb-8">
            A full-stack project — created from scratch, then extended with 3
            features in parallel. Every line of code planned, tested, and
            verified entirely by AI. Zero manual code edits.
          </p>
          <Button variant="outline" size="lg" asChild>
            <a
              href="https://github.com/maxritter/pilot-shell-demo"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="mr-2 h-5 w-5" />
              Watch the demo and browse the code
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
};

export default DemoSection;
