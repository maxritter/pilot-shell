import { Quote } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const testimonials = [
  {
    quote:
      "Spec-driven development in Pilot Shell is incredible. I'm so impressed that I have to resist the urge to fix every issue all at once.",
    role: "Pilot Shell User",
  },
  {
    quote:
      "Instead of just letting Claude Code run on its own, you've managed to make it work in a much more organized, consistent, and reliable way within a workflow, which I think is fantastic. What you've built is truly impressive.",
    role: "Pilot Shell User",
  },
  {
    quote:
      "I have fallen in love with Pilot and just can't stand the idea of having to go back to native Claude.",
    role: "Pilot Shell User",
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
          <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
            Real feedback from developers using Pilot in production
          </p>
        </div>

        <div
          className={`grid md:grid-cols-3 gap-6 ${inView ? "animate-fade-in-up animation-delay-200" : "opacity-0"}`}
        >
          {testimonials.map((t, i) => (
            <div
              key={i}
              className="relative rounded-lg p-6 border border-border/50 bg-card hover:border-primary/30 hover:bg-card transition-all duration-300"
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
