import { Bell, Link2, Users } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";
import SectionHeader from "@/components/SectionHeader";
import IconTile from "@/components/IconTile";

const reviewerFeatures = [
  {
    icon: Link2,
    title: "One link, many reviewers",
    desc: (
      <>
        Click{" "}
        <span className="font-mono text-xs text-foreground/80">
          Share with Teammates
        </span>{" "}
        once and forward the link to as many people as you like — no Pilot
        install required on their side.
      </>
    ),
  },
  {
    icon: Users,
    title: "Feedback grouped by author",
    desc: (
      <>
        Teammate annotations stream back into your Console in 60 seconds —
        stored next to the spec, so the agent reads them at the next review
        checkpoint.
      </>
    ),
  },
  {
    icon: Bell,
    title: "Zero handoff overhead",
    desc: (
      <>
        Reviewers click{" "}
        <span className="font-mono text-xs text-foreground/80">Submit</span> —
        no copy-URL-back step. Each submit lands as a single notification in
        your Console.
      </>
    ),
  },
];

const SpecReviewMock = () => (
  <div className="bg-card border border-border/70 rounded-xl overflow-hidden shadow-[0_24px_60px_hsl(217,40%,2%,0.2)] dark:shadow-[0_24px_60px_hsl(217,40%,2%,0.45)]">
    <div className="flex items-center gap-2.5 px-3.5 py-2.5 border-b border-border/50 bg-muted/50 dark:bg-[hsl(217,35%,7.5%)]">
      <div className="flex items-center gap-[7px]" aria-hidden="true">
        <span className="w-[11px] h-[11px] rounded-full bg-[hsl(0,60%,55%)]" />
        <span className="w-[11px] h-[11px] rounded-full bg-[hsl(40,80%,55%)]" />
        <span className="w-[11px] h-[11px] rounded-full bg-[hsl(140,50%,45%)]" />
      </div>
      <span className="flex-1 text-center font-mono text-[11px] text-muted-foreground bg-background/60 rounded-md px-3 py-1">
        pilot-shell.com/s/rate-limiting
      </span>
    </div>
    <div className="p-5">
      <div className="font-mono text-[10.5px] font-semibold uppercase tracking-[0.1em] text-muted-foreground mb-3">
        Specification — rate limiting
      </div>
      <div className="flex flex-col gap-2 text-[12.5px] leading-relaxed text-muted-foreground">
        <div>1. Add a token-bucket limiter to the gateway middleware</div>
        <div className="bg-primary/10 border-l-2 border-primary px-2.5 py-1.5 rounded-r text-foreground/90">
          2. Return 429 with a Retry-After header once the bucket is empty
        </div>
        <div>3. Persist per-key counters in Redis with a sliding window</div>
      </div>
      <div className="flex gap-2.5 mt-4 px-3.5 py-3 bg-background/50 border border-border/60 rounded-lg">
        <span
          className="flex-none w-[26px] h-[26px] rounded-full bg-primary/15 text-primary flex items-center justify-center text-[10px] font-semibold"
          aria-hidden="true"
        >
          BK
        </span>
        <div className="min-w-0">
          <div className="text-[11px] text-muted-foreground">
            <span className="font-semibold text-foreground">Bob K.</span> · 2m
            ago · on line 2
          </div>
          <div className="text-[12.5px] text-foreground/85 leading-relaxed mt-0.5">
            What happens when the client retries during a window rollover?
            Worth an explicit test.
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2 mt-3.5 text-[11.5px] text-muted-foreground">
        <Bell className="h-[13px] w-[13px] text-primary" aria-hidden="true" />3
        annotations on rate-limiting — grouped by author in your Console
      </div>
    </div>
  </div>
);

const SpecCollabSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="shift-left"
      aria-labelledby="shift-left-heading"
      className="scroll-mt-24 py-16 lg:py-24 px-4 sm:px-6 relative"
    >
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div ref={ref} className={inView ? "animate-fade-in-up" : "opacity-0"}>
          <SectionHeader
            kicker="Shift Left"
            title="Catch flaws in the spec, not the PR."
            titleId="shift-left-heading"
            lead={
              <>
                Review and annotate requirements with your team{" "}
                <span className="text-foreground font-medium">
                  before a single line of code is written
                </span>
                . Wrong approach, missed edge case, unclear scope, weak
                architecture — spot it while it costs a sentence to change, not
                a refactor.
              </>
            }
            className="mb-10"
          />

          <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-9 lg:gap-14 items-center">
            <SpecReviewMock />
            <div className="flex flex-col gap-6">
              {reviewerFeatures.map((feature) => (
                <div key={feature.title} className="flex gap-4 items-start">
                  <IconTile icon={feature.icon} />
                  <div>
                    <div className="text-[15px] font-semibold text-foreground mb-1">
                      {feature.title}
                    </div>
                    <p className="text-[13px] leading-relaxed text-muted-foreground">
                      {feature.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SpecCollabSection;
