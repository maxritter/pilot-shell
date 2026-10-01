import type { Faq } from "@/lib/content";

export default function Questions({ faqs, id = "faq", sunk }: { faqs: Faq[]; id?: string; sunk?: boolean }) {
  return (
    <section id={id} className={`w7-sec${sunk ? " w7-sunk" : ""}`} aria-labelledby={`${id}-h`}>
      <div className="w7-wrap w7-faq">
        <h2 className="w7-h2" id={`${id}-h`}>Questions</h2>
        <div className="w7-faql">
          {faqs.map((faq) => (
            <details key={faq.question}>
              <summary>{faq.question}<span aria-hidden="true">+</span></summary>
              <p>{faq.answer}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
