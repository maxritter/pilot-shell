import { Quote } from "lucide-react";

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
    featured: true,
  },
  {
    quote:
      "I have fallen in love with Pilot and just can't stand the idea of having to go back to native Claude.",
    role: "Pilot Shell User",
  },
];

const TestimonialsSection = () => (
  <section className="ps-sec" aria-labelledby="testimonials-heading">
    <div className="ps-ctr">
      <div className="ps-sec-hd ps-rv">
        <h2 className="ps-h2" id="testimonials-heading">
          What Users Say
        </h2>
        <p className="ps-lead">Real feedback from developers using Pilot in production.</p>
      </div>

      <div className="ps-tm ps-stg">
        {testimonials.map((testimonial) => (
          <blockquote
            key={testimonial.quote}
            className={`ps-tcard${testimonial.featured ? " ps-big" : ""}`}
          >
            <Quote
              className={testimonial.featured ? "h-5 w-5 ps-qg" : "h-[18px] w-[18px] ps-qg"}
              aria-hidden="true"
            />
            <p className="ps-tq">"{testimonial.quote}"</p>
            <footer className="ps-trole">{testimonial.role}</footer>
          </blockquote>
        ))}
      </div>
    </div>
  </section>
);

export default TestimonialsSection;
