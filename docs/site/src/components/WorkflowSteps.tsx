import {
  FileText,
  Code2,
  CheckCircle2,
  RefreshCw,
  Zap,
  MessageSquare,
  Brain,
} from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const specSteps = [
  { icon: MessageSquare, title: "Discuss", desc: "Clarifies gray areas" },
  { icon: FileText, title: "Plan", desc: "Explores codebase, generates spec" },
  { icon: CheckCircle2, title: "Approve", desc: "You review and approve" },
  { icon: Code2, title: "Implement", desc: "TDD for each task" },
  { icon: RefreshCw, title: "Verify", desc: "Tests pass or loops back" },
];

const WorkflowSteps = () => {
  const [headerRef, headerInView] = useInView<HTMLDivElement>();
  const [diagramRef, diagramInView] = useInView<HTMLDivElement>();
  const [modesRef, modesInView] = useInView<HTMLDivElement>();
  const [commandsRef, commandsInView] = useInView<HTMLDivElement>();

  return (
    <section id="workflow" className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        {/* Header */}
        <div
          ref={headerRef}
          className={`text-center mb-12 ${headerInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
            Usage
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
            Two modes to match your workflow
          </p>
        </div>

        {/* Two Modes - Side by Side */}
        <div
          ref={modesRef}
          className={`grid md:grid-cols-2 gap-6 mb-12 ${modesInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          {/* Spec-Driven Mode */}
          <div className="group relative rounded-2xl p-6 border border-primary/50 bg-card/30 backdrop-blur-sm hover:bg-card/50 transition-all duration-300">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-11 h-11 bg-primary/20 rounded-xl flex items-center justify-center">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                  Spec-Driven Mode
                  <code className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                    /spec
                  </code>
                </h3>
                <p className="text-sm text-muted-foreground">
                  For features, bug fixes, and complex changes
                </p>
              </div>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Creates a plan, gets your approval, implements with TDD, verifies
              completion. Best for anything that touches multiple files or needs
              careful planning.
            </p>
          </div>

          {/* Quick Mode */}
          <div className="group relative rounded-2xl p-6 border border-border/50 bg-card/30 backdrop-blur-sm hover:border-primary/30 hover:bg-card/50 transition-all duration-300">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-11 h-11 bg-primary/10 rounded-xl flex items-center justify-center">
                <Zap className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">
                  Quick Mode
                </h3>
                <p className="text-sm text-muted-foreground">
                  For small tasks and quick questions
                </p>
              </div>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Just chat — no plan file, no approval gate. All quality hooks and
              TDD enforcement still apply. Great for small changes, questions,
              and exploration.
            </p>
          </div>
        </div>

        {/* Spec-Driven Workflow Diagram */}
        <div
          ref={diagramRef}
          className={`rounded-2xl p-6 border border-border/50 bg-card/30 backdrop-blur-sm mb-12 ${diagramInView ? "animate-fade-in-up animation-delay-200" : "opacity-0"}`}
        >
          <h3 className="text-base font-semibold text-foreground mb-6 text-center">
            <code className="text-primary">/spec</code> Workflow
          </h3>

          {/* Desktop: single row with arrows (≥768px) */}
          <div className="hidden md:flex items-center justify-center gap-6">
            {specSteps.map((step, i) => (
              <div key={i} className="flex items-center gap-6">
                <div className="flex flex-col items-center">
                  <div
                    className="w-16 h-16 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center
                    hover:bg-primary/20 hover:scale-110 transition-all duration-300"
                  >
                    <step.icon className="h-7 w-7 text-primary" />
                  </div>
                  <span className="text-sm text-foreground mt-3 font-medium">
                    {step.title}
                  </span>
                  <span className="text-xs text-muted-foreground text-center max-w-[100px]">
                    {step.desc}
                  </span>
                </div>
                {i < specSteps.length - 1 && (
                  <span className="text-primary text-2xl font-light">
                    &rarr;
                  </span>
                )}
              </div>
            ))}
            <span className="text-muted-foreground text-sm ml-4 flex items-center gap-1">
              <RefreshCw className="h-4 w-4" /> Loop
            </span>
          </div>

          {/* Mobile: compact numbered list (<768px) */}
          <div className="md:hidden space-y-3">
            {specSteps.map((step, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center flex-shrink-0">
                  <step.icon className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <span className="text-sm text-foreground font-medium">
                    {step.title}
                  </span>
                  <span className="text-xs text-muted-foreground ml-2">
                    {step.desc}
                  </span>
                </div>
                {i < specSteps.length - 1 && (
                  <span className="text-primary/40 text-lg flex-shrink-0">
                    ↓
                  </span>
                )}
                {i === specSteps.length - 1 && (
                  <span className="text-muted-foreground text-xs flex items-center gap-1 flex-shrink-0">
                    <RefreshCw className="h-3 w-3" /> Loop
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* All Commands */}
        <div
          ref={commandsRef}
          className={`rounded-2xl p-6 border border-border/50 bg-card/30 backdrop-blur-sm ${commandsInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h3 className="text-lg font-semibold text-foreground mb-5 text-center">
            All Commands
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="rounded-xl p-4 border border-border/40 bg-background/30">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/spec</code>
              </div>
              <p className="text-xs text-muted-foreground">
                Spec-Driven Development — plan, approve, implement, verify.
                Features and bug fixes. Auto-detects bugfix intent.
              </p>
            </div>
            <div className="rounded-xl p-4 border border-border/40 bg-background/30">
              <div className="flex items-center gap-2 mb-2">
                <RefreshCw className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/sync</code>
              </div>
              <p className="text-xs text-muted-foreground">
                Syncs rules and standards with your codebase — explores
                patterns, discovers conventions, creates new skills.
              </p>
            </div>
            <div className="rounded-xl p-4 border border-border/40 bg-background/30">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/vault</code>
              </div>
              <p className="text-xs text-muted-foreground">
                Team Vault — push, pull, and browse shared rules, skills, and
                commands. Automatic versioning via private Git repo.
              </p>
            </div>
            <div className="rounded-xl p-4 border border-border/40 bg-background/30">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/learn</code>
              </div>
              <p className="text-xs text-muted-foreground">
                Online learning — extracts debugging discoveries, workarounds,
                and tool integrations into reusable skills.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WorkflowSteps;
