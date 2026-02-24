import {
  Clock,
  Zap,
  AlertTriangle,
  CheckCircle2,
  Brain,
  FileCode2,
  ShieldCheck,
} from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const ComparisonSection = () => {
  const [headerRef, headerInView] = useInView<HTMLDivElement>();
  const [cardsRef, cardsInView] = useInView<HTMLDivElement>();

  return (
    <section id="problem" className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        {/* Section Header */}
        <div
          ref={headerRef}
          className={`text-center mb-12 ${headerInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
            The Problem
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-2xl mx-auto">
            Without structure, Claude Code skips tests, loses context, and
            produces inconsistent results.
          </p>
        </div>

        {/* Before & After Terminal Comparison */}
        <div
          ref={cardsRef}
          className={`grid md:grid-cols-2 gap-6 sm:gap-8 stagger-children ${cardsInView ? "in-view" : ""}`}
        >
          {/* Without Pilot Shell */}
          <div className="glass rounded-2xl p-5 sm:p-6 relative border-slate-500/20 hover:border-slate-500/30 transition-colors">
            <div className="absolute top-3 sm:top-4 right-3 sm:right-4 bg-slate-500/20 text-slate-400 px-2 sm:px-3 py-1 rounded-full text-xs font-medium">
              Without Structure
            </div>

            {/* Terminal window */}
            <div className="mt-8 space-y-3">
              {/* Terminal header */}
              <div className="bg-background/80 rounded-t-lg px-4 py-2 flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-slate-500/60" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                  <div className="w-3 h-3 rounded-full bg-blue-500/60" />
                </div>
                <span className="text-xs text-muted-foreground ml-2 font-mono">
                  terminal
                </span>
              </div>

              {/* Terminal content */}
              <div className="bg-background/50 rounded-b-lg p-4 font-mono text-xs sm:text-sm space-y-3">
                <div>
                  <span className="text-blue-400">you:</span>
                  <span className="text-muted-foreground ml-2">
                    Add user authentication
                  </span>
                </div>
                <div>
                  <span className="text-primary">claude:</span>
                  <span className="text-muted-foreground ml-2">
                    What framework? What patterns?
                  </span>
                </div>
                <div className="text-slate-400/80 flex items-center gap-2 text-xs">
                  <AlertTriangle className="h-3 w-3 flex-shrink-0" />
                  <span>No context from previous sessions</span>
                </div>
                <div className="text-slate-400/80 flex items-center gap-2 text-xs">
                  <AlertTriangle className="h-3 w-3 flex-shrink-0" />
                  <span>No codebase knowledge</span>
                </div>
                <div className="border-t border-border/50 pt-3">
                  <span className="text-muted-foreground">
                    ...writes code without tests...
                  </span>
                </div>
                <div className="text-slate-400/80 flex items-center gap-2 text-xs">
                  <AlertTriangle className="h-3 w-3 flex-shrink-0" />
                  <span>No TDD enforcement</span>
                </div>
                <div className="border-t border-border/50 pt-3">
                  <span className="text-muted-foreground">
                    ...commits with issues...
                  </span>
                </div>
                <div className="text-slate-400/80 flex items-center gap-2 text-xs">
                  <AlertTriangle className="h-3 w-3 flex-shrink-0" />
                  <span>No quality checks or formatting</span>
                </div>
              </div>
            </div>

            {/* Result */}
            <div className="mt-4 flex items-center justify-center gap-2 text-slate-400 text-sm">
              <Clock className="h-4 w-4" />
              <span>Inconsistent. Untested. Risky.</span>
            </div>
          </div>

          {/* With Pilot Shell */}
          <div className="glass rounded-2xl p-5 sm:p-6 relative border-primary/20 hover:border-primary/30 transition-colors">
            <div className="absolute top-3 sm:top-4 right-3 sm:right-4 bg-primary/20 text-primary px-2 sm:px-3 py-1 rounded-full text-xs font-medium">
              With Pilot Shell
            </div>

            {/* Terminal window */}
            <div className="mt-8 space-y-3">
              {/* Terminal header */}
              <div className="bg-background/80 rounded-t-lg px-4 py-2 flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-slate-500/60" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                  <div className="w-3 h-3 rounded-full bg-blue-500/60" />
                </div>
                <span className="text-xs text-muted-foreground ml-2 font-mono">
                  pilot
                </span>
              </div>

              {/* Terminal content */}
              <div className="bg-background/50 rounded-b-lg p-4 font-mono text-xs sm:text-sm space-y-2.5">
                {/* /spec command */}
                <div>
                  <span className="text-primary">/spec</span>
                  <span className="text-muted-foreground ml-2">
                    "Add user authentication"
                  </span>
                </div>
                {/* Context injection */}
                <div className="text-primary/80 flex items-center gap-2 text-xs">
                  <Brain className="h-3 w-3 flex-shrink-0" />
                  <span>Persistent memory: Context injected</span>
                </div>
                <div className="text-primary/80 flex items-center gap-2 text-xs">
                  <FileCode2 className="h-3 w-3 flex-shrink-0" />
                  <span>Rules + Standards loaded</span>
                </div>
                <div className="border-t border-border/50 pt-2.5 text-xs">
                  <span className="text-primary">→ Planning:</span>
                  <span className="text-muted-foreground ml-1">
                    Exploring codebase...
                  </span>
                </div>
                <div className="text-primary/80 flex items-center gap-2 text-xs">
                  <CheckCircle2 className="h-3 w-3 flex-shrink-0" />
                  <span>Plan created → Waiting for approval</span>
                </div>
                <div className="border-t border-border/50 pt-2.5 text-xs">
                  <span className="text-primary">→ Implementing:</span>
                  <span className="text-muted-foreground ml-1">
                    TDD enforced
                  </span>
                </div>
                <div className="text-primary/80 flex items-center gap-2 text-xs">
                  <ShieldCheck className="h-3 w-3 flex-shrink-0" />
                  <span>Quality hooks: linted, formatted, typed</span>
                </div>
                <div className="border-t border-border/50 pt-2.5 text-xs">
                  <span className="text-primary">→ Verifying:</span>
                  <span className="text-primary ml-1">All checks passed ✓</span>
                </div>
                <div className="text-primary/80 flex items-center gap-2 text-xs">
                  <Zap className="h-3 w-3 flex-shrink-0" />
                  <span>Complete! Anything else?</span>
                </div>
              </div>
            </div>

            {/* Result */}
            <div className="mt-4 flex items-center justify-center gap-2 text-primary text-sm">
              <Zap className="h-4 w-4" />
              <span>Grab a coffee. Come back to verified code.</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ComparisonSection;
