import { Check, X } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const forYou = [
  "You have an existing codebase — especially a complex one",
  "You take code quality seriously",
  "You want tested, verified code — not vibes",
  "You trust structured workflows over ad-hoc prompting",
  "You've lost context mid-task and hated it",
  "You want your AI to follow your standards, not guess",
];

const notForYou = [
  "You want a simple prompt wrapper",
  "You expect magic without process",
  "You skip tests and ship anyway",
  "You prefer zero structure, maximum freedom",
  "You don't want to learn /spec or rules",
];

const QualifierSection = () => {
  const [headerRef, headerInView] = useInView<HTMLDivElement>();
  const [cardsRef, cardsInView] = useInView<HTMLDivElement>();

  return (
    <section className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-4xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={headerRef}
          className={`text-center mb-12 ${headerInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
            This Is Not for Everyone
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-2xl mx-auto">
            And that's on purpose. Pilot is opinionated — it enforces quality whether you like it or not.
          </p>
        </div>

        <div
          ref={cardsRef}
          className={`grid md:grid-cols-2 gap-6 ${cardsInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          {/* For you */}
          <div className="rounded-2xl p-6 border border-primary/30 bg-card/30 backdrop-blur-sm">
            <h3 className="text-lg font-semibold text-foreground mb-5 flex items-center gap-2">
              <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                <Check className="h-4 w-4 text-primary" />
              </div>
              This is for you if...
            </h3>
            <ul className="space-y-3">
              {forYou.map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm text-muted-foreground">
                  <Check className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Not for you */}
          <div className="rounded-2xl p-6 border border-border/50 bg-card/30 backdrop-blur-sm">
            <h3 className="text-lg font-semibold text-foreground mb-5 flex items-center gap-2">
              <div className="w-8 h-8 bg-slate-500/10 rounded-lg flex items-center justify-center">
                <X className="h-4 w-4 text-slate-400" />
              </div>
              This is NOT for you if...
            </h3>
            <ul className="space-y-3">
              {notForYou.map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm text-slate-400">
                  <X className="h-4 w-4 text-slate-500 flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <p className="text-center text-sm text-muted-foreground mt-8 max-w-xl mx-auto">
          If the left column resonates and the right one doesn't, you're in the right place.
        </p>
      </div>
    </section>
  );
};

export default QualifierSection;
