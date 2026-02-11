import { Quote } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const testimonials = [
  {
    quote: "Pilot turned Claude Code from a fast prototype tool into something I trust for production code. The TDD enforcement alone saved me from shipping broken features twice in the first week.",
    role: "Senior Developer",
  },
  {
    quote: "Endless Mode is a game-changer. I used to lose context halfway through complex refactors. Now it just hands off cleanly and picks up exactly where it left off.",
    role: "Full-Stack Engineer",
  },
  {
    quote: "The /spec workflow forces me to think before I code. The plan verification catches gaps I would have missed, and the automated code review is better than most human reviews I've gotten.",
    role: "Tech Lead",
  },
];

const TestimonialsSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={ref}
          className={`text-center mb-12 ${inView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
            What Users Say
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-2xl mx-auto">
            Real feedback from developers using Pilot in production
          </p>
        </div>

        <div className={`grid md:grid-cols-3 gap-6 ${inView ? "animate-fade-in-up animation-delay-200" : "opacity-0"}`}>
          {testimonials.map((t, i) => (
            <div
              key={i}
              className="relative rounded-2xl p-6 border border-border/50 bg-card/30 backdrop-blur-sm hover:border-primary/30 hover:bg-card/50 transition-all duration-300"
            >
              <Quote className="h-8 w-8 text-primary/20 mb-4" />
              <p className="text-muted-foreground text-sm leading-relaxed mb-4">
                "{t.quote}"
              </p>
              <p className="text-xs text-primary font-medium">{t.role}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
