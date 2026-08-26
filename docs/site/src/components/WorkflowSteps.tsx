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
  Trophy,
  Target,
  ListChecks,
  Scale,
  Search,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const specSteps = [
  { icon: MessageSquare, title: "Discuss", desc: "Clarifies gray areas" },
  { icon: FileText, title: "Plan", desc: "Explores codebase, generates spec" },
  { icon: CheckCircle2, title: "Approve", desc: "You review and approve" },
  { icon: Code2, title: "Implement", desc: "TDD for each task" },
  { icon: RefreshCw, title: "Verify", desc: "Tests pass or loops back" },
];

const buildSteps = [
  { icon: Target, title: "Goal", desc: "Grills a weak end state" },
  { icon: ListChecks, title: "Draft", desc: "Tasks and pass/fail criteria" },
  { icon: Code2, title: "Build", desc: "Works the whole task list" },
  { icon: Scale, title: "Judge", desc: "Rules criteria, pass or fail" },
  { icon: ShieldCheck, title: "Verify", desc: "Tests, E2E, and a code review" },
];

interface WorkflowStep {
  icon: LucideIcon;
  title: string;
  desc: string;
}

/** One command's step sequence: a single row on desktop, a stacked list on mobile. */
const WorkflowDiagram = ({
  command,
  steps,
  loopLabel,
}: {
  command: string;
  steps: WorkflowStep[];
  loopLabel: string;
}) => (
  <div className="rounded-lg p-6 border border-border/50 bg-card">
    <h3 className="text-base font-semibold text-foreground mb-6 text-center">
      <code className="text-primary">{command}</code> Workflow
    </h3>

    {/* Desktop: single row with arrows */}
    <div className="hidden md:flex items-center justify-center gap-3 flex-wrap">
      {steps.map((step, i) => (
        <div key={step.title} className="flex items-center gap-3">
          <div className="flex flex-col items-center">
            <div
              className="w-14 h-14 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center
              hover:bg-primary/20 hover:scale-110 transition-all duration-300"
            >
              <step.icon className="h-6 w-6 text-primary" />
            </div>
            <span className="text-sm text-foreground mt-3 font-medium">
              {step.title}
            </span>
            <span className="text-xs text-muted-foreground text-center max-w-[92px]">
              {step.desc}
            </span>
          </div>
          {i < steps.length - 1 && (
            <span
              className="text-primary text-2xl font-light"
              aria-hidden="true"
            >
              &rarr;
            </span>
          )}
        </div>
      ))}
      <span className="text-muted-foreground text-xs w-full text-center mt-4 flex items-center justify-center gap-1">
        <RefreshCw className="h-3 w-3" /> {loopLabel}
      </span>
    </div>

    {/* Mobile: compact stacked list */}
    <div className="md:hidden space-y-3">
      {steps.map((step, i) => (
        <div key={step.title} className="flex items-center gap-3">
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
          {i < steps.length - 1 && (
            <span
              className="text-primary/40 text-lg flex-shrink-0"
              aria-hidden="true"
            >
              &darr;
            </span>
          )}
          {i === steps.length - 1 && (
            <span className="text-muted-foreground text-xs flex items-center gap-1 flex-shrink-0">
              <RefreshCw className="h-3 w-3" /> {loopLabel}
            </span>
          )}
        </div>
      ))}
    </div>
  </div>
);

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
            Pilot workflows for every stage
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
            Understand unfamiliar code, shape requirements, approve a plan,
            build toward a goal, or trace a defect with evidence at every
            handoff.
          </p>
        </div>

        <div className="mb-10 border-y border-border/60 py-6 sm:py-8 grid gap-6 md:grid-cols-[minmax(0,1.2fr)_minmax(16rem,0.8fr)] md:items-center">
          <div className="flex items-start gap-4">
            <div className="mt-1 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Zap className="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-foreground">
                Cross-agent workflow suite
              </h3>
              <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
                Use <code className="text-foreground">/investigate</code> to
                understand existing code, <code className="text-foreground">/cleanup</code>{" "}
                to audit unused-code candidates, then{" "}
                <code className="text-foreground">/prd</code>,{" "}
                <code className="text-foreground">/spec</code>,{" "}
                <code className="text-foreground">/build</code>, or{" "}
                <code className="text-foreground">/fix</code> to put the right
                product, planning, build, or debugging loop around the work.
              </p>
            </div>
          </div>
          <p className="text-sm leading-relaxed text-muted-foreground md:border-l md:border-border md:pl-6">
            <strong className="text-foreground">Supported agents.</strong>{" "}
            Pilot Shell supports Claude Code and Codex. Available integrations
            follow each agent&apos;s supported interfaces.
          </p>
        </div>

        <div className="mb-6 text-center">
          <h3 className="text-xl font-semibold text-foreground">
            Four core workflows
          </h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Choose the workflow that matches what the work is measured against.
          </p>
        </div>

        {/* Four explicit modes */}
        <div
          ref={modesRef}
          className={`grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12 ${modesInView ? "animate-fade-in-up" : "opacity-0"}`}
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
                <h3 className="text-lg font-semibold text-foreground">
                  Requirements
                  <code className="mt-1 block w-fit text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                    /prd
                  </code>
                </h3>
                <p className="text-sm text-muted-foreground">
                  Brainstorm what to build
                </p>
              </div>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed group-hover:text-foreground/80 transition-colors duration-200">
              Invoke it when the product itself is still unclear. The agent
              pressure-tests directions and writes a PRD you can deliberately
              hand to /spec or /build.
            </p>
            <div className="mt-3 flex items-center gap-1 text-xs text-primary/80 group-hover:text-primary transition-colors">
              <span>Learn more</span>
              <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </a>

          {/* Spec-Driven Mode */}
          <a
            href="/docs/workflows/spec"
            className="group relative rounded-lg p-6 border border-border/50 bg-card hover:border-primary/50 transition-all duration-300 block"
            aria-label="Learn more about /spec"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-11 h-11 bg-primary/20 rounded-xl flex items-center justify-center group-hover:bg-primary/30 group-hover:scale-110 transition-all duration-300">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">
                  Specifications
                  <code className="mt-1 block w-fit text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                    /spec
                  </code>
                </h3>
                <p className="text-sm text-muted-foreground">
                  Plan, build, and verify
                </p>
              </div>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed group-hover:text-foreground/80 transition-colors duration-200">
              Use it when an ordered task list should be written and approved
              before code. It implements with TDD and verifies against that
              approved plan.
            </p>
            <div className="mt-3 flex items-center gap-1 text-xs text-primary/80 group-hover:text-primary transition-colors">
              <span>Learn more</span>
              <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </a>

          {/* Build Loop */}
          <a
            href="/docs/workflows/build"
            className="group relative rounded-lg p-6 border border-border/50 bg-card hover:border-primary/50 transition-all duration-300 block"
            aria-label="Learn more about /build"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-11 h-11 bg-primary/20 rounded-xl flex items-center justify-center group-hover:bg-primary/30 group-hover:scale-110 transition-all duration-300">
                <Trophy className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">
                  Build
                  <code className="mt-1 block w-fit text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                    /build
                  </code>
                </h3>
                <p className="text-sm text-muted-foreground">
                  Name a goal, then walk away
                </p>
              </div>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed group-hover:text-foreground/80 transition-colors duration-200">
              Use it when the end state matters more than a pre-approved task
              list. It sharpens the goal, then builds and judges autonomously
              against explicit pass/fail criteria.
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
                <h3 className="text-lg font-semibold text-foreground">
                  Bugfix
                  <code className="mt-1 block w-fit text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                    /fix
                  </code>
                </h3>
                <p className="text-sm text-muted-foreground">
                  Investigate, test, fix, audit
                </p>
              </div>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed group-hover:text-foreground/80 transition-colors duration-200">
              Invoke the focused TDD bugfix process: reproduce, trace the root
              cause, fix at the source, and verify the behavior end-to-end.
            </p>
            <div className="mt-3 flex items-center gap-1 text-xs text-primary/80 group-hover:text-primary transition-colors">
              <span>Learn more</span>
              <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </a>
        </div>

        {/* Workflow Diagrams — /spec and /build */}
        <div
          ref={diagramRef}
          className={`grid lg:grid-cols-2 gap-6 mb-12 ${diagramInView ? "animate-fade-in-up animation-delay-200" : "opacity-0"}`}
        >
          <WorkflowDiagram
            command="/spec"
            steps={specSteps}
            loopLabel="Loop"
          />
          <WorkflowDiagram
            command="/build"
            steps={buildSteps}
            loopLabel="Failing criteria become the next round"
          />
        </div>

        {/* All Commands */}
        <div
          ref={commandsRef}
          className={`rounded-lg p-6 border border-border/50 bg-card ${commandsInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h3 className="text-lg font-semibold text-foreground mb-5 text-center">
            All Pilot skills
          </h3>
          <div className="grid md:grid-cols-2 gap-x-8">
            <a
              href="/docs/workflows/prd"
              className="group flex min-h-20 flex-col gap-2 border-t border-border/50 py-4 sm:flex-row sm:gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex min-w-44 items-center gap-2">
                <Lightbulb className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/prd</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Brainstorm vague ideas into PRDs — back-and-forth conversation,
                optional deep research, then hand off to /spec or /build.
              </p>
            </a>
            <a
              href="/docs/workflows/spec"
              className="group flex min-h-20 flex-col gap-2 border-t border-border/50 py-4 sm:flex-row sm:gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex min-w-44 items-center gap-2">
                <FileText className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/spec</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Write and approve the task list before implementation, then
                verify the finished work against it.
              </p>
            </a>
            <a
              href="/docs/workflows/build"
              className="group flex min-h-20 flex-col gap-2 border-t border-border/50 py-4 sm:flex-row sm:gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex min-w-44 items-center gap-2">
                <Trophy className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/build</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Goal-and-loop development — name an end state, draft tasks and
                criteria, then build and judge against them autonomously.
              </p>
            </a>
            <a
              href="/docs/workflows/fix"
              className="group flex min-h-20 flex-col gap-2 border-t border-border/50 py-4 sm:flex-row sm:gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex min-w-44 items-center gap-2">
                <Bug className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/fix</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Bugfix workflow — investigate, write a failing test, fix at the
                root cause, and verify the behavior end-to-end.
              </p>
            </a>
            <a
              href="/docs/workflows/investigate"
              className="group flex min-h-20 flex-col gap-2 border-t border-border/50 py-4 sm:flex-row sm:gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex min-w-44 items-center gap-2">
                <Search className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">
                  /investigate
                </code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Trace how existing code works, challenge the conclusion once,
                and answer with file-and-line evidence without changing the
                project.
              </p>
            </a>
            <a
              href="/docs/workflows/setup-rules"
              className="group flex min-h-20 flex-col gap-2 border-t border-border/50 py-4 sm:flex-row sm:gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex min-w-44 items-center gap-2">
                <RefreshCw className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/setup-rules</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Generates project rules from your codebase — explores patterns,
                documents conventions and MCP servers.
              </p>
            </a>
            <a
              href="/docs/workflows/cleanup"
              className="group flex min-h-20 flex-col gap-2 border-t border-border/50 py-4 sm:flex-row sm:gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex min-w-44 items-center gap-2">
                <ListChecks className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/cleanup</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Corroborate analyzer findings, exact references, dynamic entry
                points, and tests into a report-only cleanup inventory.
              </p>
            </a>
            <a
              href="/docs/workflows/create-skill"
              className="group flex min-h-20 flex-col gap-2 border-t border-border/50 py-4 sm:flex-row sm:gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex min-w-44 items-center gap-2">
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
              className="group flex min-h-20 flex-col gap-2 border-t border-border/50 py-4 sm:flex-row sm:gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex min-w-44 items-center gap-2">
                <Gauge className="h-4 w-4 text-primary" />
                <code className="text-sm font-medium text-primary">/benchmark</code>
              </div>
              <p className="text-xs text-muted-foreground group-hover:text-foreground/80">
                Measure whether a rule, skill, or workflow changes agent
                behavior with before-and-after assertions.
              </p>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WorkflowSteps;
