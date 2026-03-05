import { useInView } from "@/hooks/use-in-view";
import ImageModal from "@/components/ImageModal";
import { Button } from "@/components/ui/button";
import { Users, GitBranch, Package, RefreshCw, Calendar, Mail } from "lucide-react";

const features = [
  {
    icon: Package,
    title: "Shared Assets",
    desc: "Push and install rules, skills, commands, and agents across your team from a single Git repository.",
  },
  {
    icon: GitBranch,
    title: "Project-Scoped",
    desc: "Assets are scoped to repositories — each project gets exactly the assets it needs, automatically.",
  },
  {
    icon: RefreshCw,
    title: "Version Tracking",
    desc: "Every asset is versioned. See what's installed locally vs. what's latest in the repository at a glance.",
  },
  {
    icon: Users,
    title: "Team Consistency",
    desc: "New team members run one command to get every rule, skill, and workflow the team has standardized on.",
  },
];

const TeamsDashboardSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="teams"
      className="py-16 lg:py-24 px-4 sm:px-6 relative"
    >
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={ref}
          className={`${inView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
              Teams Asset Sharing
            </h2>
            <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
              Share AI assets across your team. Rules, skills, commands, and
              agents — managed from a central Git repository and synced to every
              project.
            </p>
          </div>

          {/* Screenshot */}
          <div className="max-w-4xl mx-auto mb-10">
            <div className="rounded-xl overflow-hidden border border-border/50 shadow-2xl shadow-primary/10">
              <ImageModal
                src="/console/teams.png"
                alt="Teams Dashboard — shared asset management with project-scoped versioning"
                className="w-full rounded-xl"
              />
            </div>
          </div>

          {/* Feature cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto mb-12">
            {features.map((f) => (
              <div
                key={f.title}
                className="rounded-lg border border-border/50 bg-card/50 p-4"
              >
                <f.icon className="h-5 w-5 text-primary mb-2" />
                <h3 className="font-semibold text-foreground text-sm mb-1">
                  {f.title}
                </h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {f.desc}
                </p>
              </div>
            ))}
          </div>

          {/* Team rollout CTA */}
          <div id="rollout" className="text-center max-w-3xl mx-auto">
            <h3 className="text-xl sm:text-2xl font-bold text-foreground mb-3">
              Rolling Out for Your Team?
            </h3>
            <p className="text-muted-foreground text-sm sm:text-base mb-6">
              Let's figure out if Pilot Shell is the right fit for your team and
              get everyone set up.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Button size="lg" asChild>
                <a
                  href="https://calendly.com/rittermax/pilot-shell"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  Book a Call
                </a>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <a href="mailto:mail@maxritter.net">
                  <Mail className="mr-2 h-4 w-4" />
                  Send a Message
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TeamsDashboardSection;
