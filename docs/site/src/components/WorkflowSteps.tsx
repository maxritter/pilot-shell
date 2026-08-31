import {
  ArrowRight,
  Bug,
  Code2,
  FileText,
  Lightbulb,
  ListChecks,
  MessageSquare,
  MonitorCheck,
  ShieldCheck,
  Trophy,
  type LucideIcon,
} from "lucide-react";
import { useInView } from "@/hooks/use-in-view";
import SectionHeader from "@/components/SectionHeader";
import IconTile from "@/components/IconTile";

interface Workflow {
  icon: LucideIcon;
  title: string;
  kicker: string;
  summary: string;
  href: string;
}

const workflows: Workflow[] = [
  {
    icon: Lightbulb,
    title: "Requirements",
    kicker: "/prd — brainstorm what to build",
    summary:
      "Invoke it when the product itself is still unclear. The agent pressure-tests directions and writes a PRD you can deliberately hand to /spec or /build.",
    href: "/docs/workflows/prd",
  },
  {
    icon: FileText,
    title: "Specifications",
    kicker: "/spec — plan, build, and verify",
    summary:
      "Use it when an ordered task list should be written and approved before code. It implements with TDD and verifies against that approved plan.",
    href: "/docs/workflows/spec",
  },
  {
    icon: Trophy,
    title: "Build",
    kicker: "/build — name a goal, walk away",
    summary:
      "Use it when the end state matters more than a pre-approved task list. It sharpens the goal, then builds and judges autonomously against explicit pass/fail criteria.",
    href: "/docs/workflows/build",
  },
  {
    icon: Bug,
    title: "Bugfix",
    kicker: "/fix — investigate, test, fix, audit",
    summary:
      "The focused TDD bugfix process: reproduce, trace the root cause, fix at the source, and verify the behavior end-to-end.",
    href: "/docs/workflows/fix",
  },
];

const flowSteps: Array<{ icon: LucideIcon; label: string }> = [
  { icon: MessageSquare, label: "Requirement" },
  { icon: ListChecks, label: "Plan / criteria" },
  { icon: Code2, label: "TDD implementation" },
  { icon: ShieldCheck, label: "Quality gates" },
  { icon: MonitorCheck, label: "Review & verification loop" },
];

const onDemandCommands = [
  {
    command: "/setup-rules",
    desc: "Generates modular project rules and MCP docs from the real codebase.",
    href: "/docs/workflows/setup-rules",
  },
  {
    command: "/create-skill",
    desc: "Captures a repeatable procedure as a tested, reusable skill.",
    href: "/docs/workflows/create-skill",
  },
  {
    command: "/benchmark",
    desc: "Measures whether a rule or skill actually changes agent behavior, with before/after evals.",
    href: "/docs/workflows/benchmark",
  },
  {
    command: "/investigate",
    desc: "Traces one codebase question with cited evidence, without changing the project.",
    href: "/docs/workflows/investigate",
  },
  {
    command: "/cleanup",
    desc: "Corroborates dead-code candidates into a report-only cleanup inventory with file-and-line evidence.",
    href: "/docs/workflows/cleanup",
  },
];

const FeatureCard = ({ icon, title, kicker, summary, href }: Workflow) => (
  <a
    href={href}
    className="group relative block rounded-lg border border-border/50 bg-card p-5 transition-all duration-300 hover:border-primary/50"
  >
    <div className="pointer-events-none absolute inset-0 rounded-lg bg-gradient-to-br from-primary/5 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
    <div className="flex items-center gap-3 mb-3">
      <IconTile
        icon={icon}
        className="transition-transform duration-300 group-hover:scale-110 group-hover:bg-primary/20"
      />
      <div>
        <h3 className="text-base font-semibold text-foreground">{title}</h3>
        <p className="font-mono text-[11px] text-muted-foreground">{kicker}</p>
      </div>
    </div>
    <p className="text-xs leading-relaxed text-muted-foreground transition-colors duration-200 group-hover:text-foreground/80">
      {summary}
    </p>
    <div className="mt-3 flex items-center gap-1 text-xs text-primary group-hover:underline">
      <span>Learn more</span>
      <ArrowRight className="h-3 w-3 transition-transform duration-200 group-hover:translate-x-0.5" />
    </div>
  </a>
);

const WorkflowSteps = () => {
  const [ref, inView] = useInView<HTMLDivElement>();
  const [onDemandRef, onDemandInView] = useInView<HTMLDivElement>();

  return (
    <section
      id="workflows"
      aria-labelledby="workflows-heading"
      className="scroll-mt-24 py-16 lg:py-24 px-4 sm:px-6 relative"
    >
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div ref={ref} className={inView ? "animate-fade-in-up" : "opacity-0"}>
          <SectionHeader
            kicker="Coordinated parts"
            title="Workflows put the harness around the work."
            titleId="workflows-heading"
            lead="Direct requests, native Plan/Goal tools, and Pilot workflows are peers. Use a Pilot workflow when its durable product, planning, or verification contract fits the work."
            className="mb-10"
          />

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {workflows.map((workflow) => (
              <FeatureCard key={workflow.href} {...workflow} />
            ))}
          </div>

          <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
            {flowSteps.map((step, i) => (
              <div key={step.label} className="flex items-center gap-3">
                {i > 0 && (
                  <ArrowRight
                    className="hidden sm:block h-3.5 w-3.5 text-muted-foreground/50"
                    aria-hidden="true"
                  />
                )}
                <span className="inline-flex items-center gap-1.5 rounded-full border border-border/50 bg-card px-3 py-1.5 text-sm text-muted-foreground">
                  <step.icon className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                  {step.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div
          ref={onDemandRef}
          className={`mt-14 grid lg:grid-cols-[0.85fr_1.15fr] gap-8 lg:gap-14 items-center ${
            onDemandInView ? "animate-fade-in-up" : "opacity-0"
          }`}
        >
          <div>
            <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
              Rules, skills, and memory
            </h3>
            <p className="text-sm leading-relaxed text-muted-foreground mt-3">
              They are coordinated parts of the harness — they supply context;
              they are not the product by themselves. Pilot generates, tests,
              and measures them with dedicated workflows.
            </p>
          </div>
          <div className="rounded-lg border border-border/50 bg-card px-5 sm:px-6 py-1.5">
            {onDemandCommands.map((entry, i) => (
              <div
                key={entry.command}
                className={`grid sm:grid-cols-[132px_1fr] gap-1 sm:gap-4 items-baseline py-3.5 ${
                  i < onDemandCommands.length - 1 ? "border-b border-border/40" : ""
                }`}
              >
                <a
                  href={entry.href}
                  className="font-mono text-[12.5px] font-medium text-primary hover:underline"
                >
                  {entry.command}
                </a>
                <span className="text-[13px] leading-relaxed text-muted-foreground">
                  {entry.desc}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default WorkflowSteps;
