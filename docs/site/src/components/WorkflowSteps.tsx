import {
  FileText,
  Code2,
  CheckCircle2,
  RefreshCw,
  Zap,
  MessageSquare,
  Brain,
  Lightbulb,
  Gauge,
  Bug,
  ArrowRight,
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
            Three modes for every stage of development
          </p>
        </div>

        {/* Three Modes */}
        <div
          ref={modesRef}
          className={`grid md:grid-cols-3 gap-6 mb-12 ${modesInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          {/* Requirements Mode */}
          <a
            href="/docs/workflows/prd"
            className="group relative rounded-lg p-6 border border-border/50 bg-card hover:border-primary/50 transition-all duration-300 block"
            aria-label="Learn more about /prd"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-11 h-11 bg-primary/10 rounded-xl flex items-center justify-center group-hover:bg-primary/20 group-hover:scale-110 transition-all duration-300">
                <Lightbulb className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                  Requirements
                  <code className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                    /prd
                  </code>
                </h3>
                <p className="text-sm text-muted-foreground">
                  Brainstorm what to build
                </p>
              </div>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed group-hover:text-foreground/80 transition-colors duration-200">
              Back-and-forth brainstorming for vague ideas. Claude pitches directions, pressure-tests them, and converges on a PRD that hands off cleanly to /spec.
            </p>
            <div className="mt-3 flex items-center gap-1 text-xs text-primary/80 group-hover:text-primary transition-colors">
              <span>Learn more</span>
              <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </a>

          {/* Spec-Driven Mode */}
          <a
            href="/docs/workflows/spec"
            className="group relative rounded-lg p-6 border border-primary/50 bg-card hover:border-primary transition-all duration-300 block"
            aria-label="Learn more about /spec"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-11 h-11 bg-primary/20 rounded-xl flex items-center justify-center group-hover:bg-primary/30 group-hover:scale-110 transition-all duration-300">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                  Specifications
                  <code className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                    /spec
                  </code>
                </h3>
                <p className="text-sm text-muted-foreground">
                  Plan, build, and verify
                </p>
              </div>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed group-hover:text-foreground/80 transition-colors duration-200">
              Creates a plan, gets your approval, implements each task with TDD, verifies completion. Best for features and anything multi-file that needs careful planning.
            </p>
            <div className="mt-3 flex items-center gap-1 text-xs text-primary/80 group-hover:text-primary transition-colors">
              <span>Learn more</span>
              <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </a>

          {/* Fix Flow */}
          <a
            href="/docs/workflows/fix"
            className="group relative rounded-lg p-6 border border-border/50 bg-card hover:border-primary/50 transition-all duration-300 block"
            aria-label="Learn more about /fix"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-11 h-11 bg-primary/10 rounded-xl flex items-center justify-center group-hover:bg-primary/20 group-hover:scale-110 transition-all duration-300">
                <Bug className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                  Bugfix
                  <code className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                    /fix
                  </code>
                </h3>
                <p className="text-sm text-muted-foreground">
                  Investigate, test, fix, audit
                </p>
              </div>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed group-hover:text-foreground/80 transition-colors duration-200">
              TDD bugfix workflow — traces the root cause, writes a failing test, fixes at the source, verifies end-to-end. Bails out to /spec when complexity warrants a plan.
            </p>
            <div className="mt-3 flex items-center gap-1 text-xs text-primary/80 group-hover:text-primary transition-colors">
              <span>Learn more</span>
              <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </a>
        </div>

        {/* Spec-Driven Workflow Diagram */}
        <div
          ref={diagramRef}
          className={`rounded-lg p-6 border border-border/50 bg-card mb-12 ${diagramInView ? "animate-fade-in-up animation-delay-200" : "opacity-0"}`}
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
          className={`rounded-lg p-6 border border-border/50 bg-card ${commandsInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h3 className="text-lg font-semibold text-foreground mb-5 text-center">
            All Commands
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <a
              href="/docs/workflows/prd"
              className="rounded-xl p-4 border border-border/40 bg-background/30 hover:border-primary/40 hover:bg-background/50 transition-all duration-200 group"
            >
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/prd</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Brainstorm vague ideas into PRDs — back-and-forth conversation,
                optional deep research, then hand off to /spec.
              </p>
            </a>
            <a
              href="/docs/workflows/spec"
              className="rounded-xl p-4 border border-border/40 bg-background/30 hover:border-primary/40 hover:bg-background/50 transition-all duration-200 group"
            >
              <div className="flex items-center gap-2 mb-2">
                <FileText className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/spec</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Spec-Driven Development — plan, approve, implement, verify.
                For features, refactoring, and architectural changes.
              </p>
            </a>
            <a
              href="/docs/workflows/fix"
              className="rounded-xl p-4 border border-border/40 bg-background/30 hover:border-primary/40 hover:bg-background/50 transition-all duration-200 group"
            >
              <div className="flex items-center gap-2 mb-2">
                <Bug className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/fix</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Bugfix workflow — investigate, write a failing test, fix at the
                root cause, audit end-to-end. Bails out for complex bugs.
              </p>
            </a>
            <a
              href="/docs/workflows/setup-rules"
              className="rounded-xl p-4 border border-border/40 bg-background/30 hover:border-primary/40 hover:bg-background/50 transition-all duration-200 group"
            >
              <div className="flex items-center gap-2 mb-2">
                <RefreshCw className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/setup-rules</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Generates project rules from your codebase — explores patterns,
                documents conventions and MCP servers.
              </p>
            </a>
            <a
              href="/docs/workflows/create-skill"
              className="rounded-xl p-4 border border-border/40 bg-background/30 hover:border-primary/40 hover:bg-background/50 transition-all duration-200 group"
            >
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/create-skill</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Build reusable skills from any topic — explores the codebase
                and creates well-structured skills interactively.
              </p>
            </a>
            <a
              href="/docs/workflows/benchmark"
              className="rounded-xl p-4 border border-border/40 bg-background/30 hover:border-primary/40 hover:bg-background/50 transition-all duration-200 group"
            >
              <div className="flex items-center gap-2 mb-2">
                <Gauge className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/benchmark</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Measure rule and skill impact — runs with/without
                comparisons, grades outputs, proposes concrete edits.
              </p>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WorkflowSteps;
